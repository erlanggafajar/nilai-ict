import streamlit as st
import pandas as pd
from db import get_connection
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os


def export_pdf(df):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp_file.name, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("<b>Rekap Nilai Siswa ICT</b>", styles["Title"])
    elements.append(title)

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


st.set_page_config(
    page_title="Rekap Nilai ICT", layout="wide", initial_sidebar_state="collapsed"
)

# ================= SESSION GUARD =================
if not st.session_state.get("login"):
    st.switch_page("pages/auth.py")
    st.stop()

role = st.session_state.get("role")


# ================= DB FUNCTIONS =================
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
        """
        insert into nilai_siswa
        (nama_siswa, p1, p2, p3, p4, p5, p6, p7, nilai_akhir)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
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
        """
        update nilai_siswa set
        p1=%s, p2=%s, p3=%s, p4=%s, p5=%s, p6=%s, p7=%s,
        nilai_akhir=%s
        where id=%s
        """,
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


# ================= UI =================
st.title("📊 Rekap Nilai Siswa ICT")
st.write(f"👤 {st.session_state.username} ({role})")

# ---------- CREATE ----------
if role == "admin":
    st.subheader("➕ Input Nilai Siswa")

    with st.form("form_input", clear_on_submit=True):
        nama = st.text_input("Nama Siswa")

        cols = st.columns(7)
        p = [
            cols[0].number_input("P1", 0, 100, 75),
            cols[1].number_input("P2", 0, 100, 75),
            cols[2].number_input("P3", 0, 100, 75),
            cols[3].number_input("P4", 0, 100, 75),
            cols[4].number_input("P5", 0, 100, 75),
            cols[5].number_input("P6", 0, 100, 75),
            cols[6].number_input("P7", 0, 100, 75),
        ]

        submit = st.form_submit_button("Simpan Nilai")

        if submit:
            if not nama:
                st.warning("Nama siswa wajib diisi")
            else:
                insert_data(nama, p)
                st.success("Nilai berhasil disimpan")
                st.rerun()

st.divider()

# ---------- READ ----------
df = load_data()
st.subheader("📄 Data Nilai")
st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("📤 Ekspor Data")

if not df.empty:
    if st.button("⬇️ Download PDF"):
        pdf_path = export_pdf(df)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Unduh Rekap Nilai (PDF)",
                data=f,
                file_name="rekap_nilai_ict.pdf",
                mime="application/pdf",
            )

        os.remove(pdf_path)
else:
    st.info("Belum ada data untuk diekspor")


def prepare_pdf_df(df):
    df_pdf = df.copy()

    # hapus kolom id
    if "id" in df_pdf.columns:
        df_pdf = df_pdf.drop(columns=["id"])

    # tambah kolom nomor di depan
    df_pdf.insert(0, "No", range(1, len(df_pdf) + 1))

    return df_pdf


# ---------- UPDATE & DELETE ----------
if role == "admin" and not df.empty:
    st.subheader("✏️ Edit / Hapus Nilai")

    selected_id = st.selectbox("Pilih ID Siswa", df["id"])

    row = df[df["id"] == selected_id].iloc[0]

    st.write(f"👨‍🎓 **{row['nama_siswa']}**")

    cols = st.columns(7)
    p_edit = [
        cols[0].number_input("P1", 0, 100, int(row["p1"])),
        cols[1].number_input("P2", 0, 100, int(row["p2"])),
        cols[2].number_input("P3", 0, 100, int(row["p3"])),
        cols[3].number_input("P4", 0, 100, int(row["p4"])),
        cols[4].number_input("P5", 0, 100, int(row["p5"])),
        cols[5].number_input("P6", 0, 100, int(row["p6"])),
        cols[6].number_input("P7", 0, 100, int(row["p7"])),
    ]

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update"):
            update_data(selected_id, p_edit)
            st.success("Nilai diperbarui")
            st.rerun()

    with col2:
        if st.button("Hapus"):
            delete_data(selected_id)
            st.warning("Data dihapus")
            st.rerun()

# ---------- LOGOUT ----------
st.divider()
if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("pages/auth.py")
