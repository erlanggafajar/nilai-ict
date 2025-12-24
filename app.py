import streamlit as st
import pandas as pd
from db import get_connection
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os


# ================= PDF HELPERS (Tetap) =================
def prepare_pdf_df(df):
    df_pdf = df.copy()
    if "id" in df_pdf.columns:
        df_pdf = df_pdf.drop(columns=["id"])
    df_pdf.insert(0, "No", range(1, len(df_pdf) + 1))
    return df_pdf


def export_pdf(df):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>Rekap Nilai Siswa ICT</b>", styles["Title"]))
    elements.append(Paragraph(" ", styles["Normal"]))
    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return tmp_file.name


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Sistem Nilai ICT",
    page_icon="📊",
    layout="wide",
)

# ================= SESSION GUARD (Tetap) =================
if not st.session_state.get("login"):
    st.switch_page("pages/auth.py")
    st.stop()

role = st.session_state.get("role")


# ================= DATABASE FUNCTIONS (Tetap) =================
def load_data():
    conn = get_connection()
    df = pd.read_sql("select * from nilai_siswa order by id desc", conn)
    conn.close()
    return df


def hitung_nilai_akhir(p):
    return round(sum(p) / len(p))


def insert_data(nama, p):
    nilai_akhir = hitung_nilai_akhir(p)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "insert into nilai_siswa (nama_siswa, p1, p2, p3, p4, p5, p6, p7, nilai_akhir) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (nama, *p, nilai_akhir),
    )
    conn.commit()
    cur.close()
    conn.close()


def update_data(id_, p):
    nilai_akhir = hitung_nilai_akhir(p)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "update nilai_siswa set p1=%s, p2=%s, p3=%s, p4=%s, p5=%s, p6=%s, p7=%s, nilai_akhir=%s where id=%s",
        (*p, nilai_akhir, id_),
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_data(id_):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("delete from nilai_siswa where id=%s", (id_,))
    conn.commit()
    cur.close()
    conn.close()


# ================= UI LAYOUT UPDATE =================

# --- SIDEBAR (Clean Design) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.title("Menu Utama")
    st.write(f"Masuk Dengan: **{st.session_state.username}**")
    st.caption(f"Hak Akses: {role.upper()}")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/auth.py")

# --- HEADER SECTION ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("📊 Rekap Nilai Siswa ICT")
    st.info("Selamat datang di panel manajemen nilai SMPIT Nurul Qolbi 2025.")

# --- METRIC SUMMARY ---
df = load_data()
if not df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Siswa", len(df))
    m2.metric("Rata-rata Kelas", f"{df['nilai_akhir'].mean():.1f}")
    m3.metric("Nilai Tertinggi", df["nilai_akhir"].max())

# --- MAIN CONTENT TABS ---
# Memisahkan Lihat Data, Input, dan Ekspor agar tidak menumpuk dalam satu halaman panjang
tab1, tab2, tab3 = st.tabs(["📄 Lihat Data", "➕ Input Nilai", "⚙️ Kelola & Ekspor"])

with tab1:
    st.subheader("Daftar Nilai Keseluruhan")
    if not df.empty:
        df_view = df.drop(columns=["id"])
        df_view.insert(0, "No", range(1, len(df_view) + 1))
        # Menggunakan Container Width dan Height agar lebih rapi
        st.dataframe(df_view, use_container_width=True, height=400)
    else:
        st.info("Belum ada data siswa.")

with tab2:
    if role == "admin":
        st.subheader("Tambah Data Siswa Baru")
        with st.container(border=True):
            with st.form("form_input", clear_on_submit=True):
                nama = st.text_input(
                    "Nama Lengkap Siswa", placeholder="Contoh: Ahmad Fauzi"
                )
                st.write("Input Nilai Pertemuan (0-100):")
                cols = st.columns(7)
                p = [cols[i].number_input(f"P{i+1}", 0, 100, 75) for i in range(7)]

                submit = st.form_submit_button(
                    "Simpan Nilai Sekarang", use_container_width=True
                )
                if submit:
                    if not nama:
                        st.warning("Nama siswa tidak boleh kosong!")
                    else:
                        insert_data(nama, p)
                        st.success(f"Berhasil menyimpan data {nama}")
                        st.rerun()
    else:
        st.warning("Hanya akun Admin yang dapat menambah data.")

with tab3:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Ekspor ke PDF")
        if not df.empty:
            if st.button("📑 Generate Report PDF", use_container_width=True):
                df_pdf = prepare_pdf_df(df)
                pdf_path = export_pdf(df_pdf)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF Sekarang",
                        data=f,
                        file_name="rekap_nilai_ict.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                os.remove(pdf_path)
        else:
            st.info("Tidak ada data untuk diekspor.")

    with col_right:
        if role == "admin" and not df.empty:
            st.subheader("Edit atau Hapus Data")
            with st.expander("Buka Panel Edit"):
                selected_id = st.selectbox(
                    "Pilih Siswa berdasarkan ID",
                    df["id"],
                    format_func=lambda x: f"ID: {x} - {df[df['id']==x]['nama_siswa'].values[0]}",
                )
                row = df[df["id"] == selected_id].iloc[0]

                st.write(f"Mengedit Nilai: **{row['nama_siswa']}**")
                cols_edit = st.columns(4)  # Layout grid untuk edit
                p_edit = []
                for i in range(7):
                    val = cols_edit[i % 4].number_input(
                        f"P{i+1}", 0, 100, int(row[f"p{i+1}"]), key=f"edit_{i}"
                    )
                    p_edit.append(val)

                c1, c2 = st.columns(2)
                if c1.button("✅ Update Data", use_container_width=True):
                    update_data(selected_id, p_edit)
                    st.success("Data diperbarui!")
                    st.rerun()

                if c2.button(
                    "🗑️ Hapus Siswa", use_container_width=True, type="secondary"
                ):
                    delete_data(selected_id)
                    st.warning("Data telah dihapus.")
                    st.rerun()
        elif role != "admin":
            st.subheader("Pengaturan")
            st.info("Anda login sebagai User (View Only).")

# --- FOOTER ---
st.divider()
st.caption("© 2025 Tim Jago Komputer Kresna")
