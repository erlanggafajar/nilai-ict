import streamlit as st
import pandas as pd
import os
import hashlib

# ================== KONFIGURASI ==================
DATA_FILE = "data_nilai_siswa.csv"
USER_FILE = "users.csv"

st.set_page_config(page_title="Sistem Nilai ICT", layout="wide")


# ================== UTIL AUTH ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        df = pd.DataFrame(columns=["username", "password", "role"])
        df.to_csv(USER_FILE, index=False)
        return df


def save_user(username, password, role):
    users = load_users()
    if username in users["username"].values:
        return False
    users.loc[len(users)] = {
        "username": username,
        "password": hash_password(password),
        "role": role,
    }
    users.to_csv(USER_FILE, index=False)
    return True


# ================== DATA SISWA ==================
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(
            columns=[
                "Nama Siswa",
                "P1",
                "P2",
                "P3",
                "P4",
                "P5",
                "P6",
                "P7",
                "Nilai Akhir",
            ]
        )
        df.to_csv(DATA_FILE, index=False)
        return df


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ================== SESSION ==================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.role = ""

# ================== SIDEBAR AUTH ==================
st.sidebar.title("🔐 Autentikasi")
menu = st.sidebar.selectbox("Menu", ["Login", "Daftar"])

users = load_users()

# ---------- LOGIN ----------
if menu == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        hashed = hash_password(password)
        user = users[(users["username"] == username) & (users["password"] == hashed)]

        if not user.empty:
            st.session_state.login = True
            st.session_state.username = username
            st.session_state.role = user.iloc[0]["role"]
            st.sidebar.success("Login berhasil")
            st.rerun()
        else:
            st.sidebar.error("Username atau password salah")

# ---------- REGISTER ----------
elif menu == "Daftar":
    new_user = st.sidebar.text_input("Username Baru")
    new_pass = st.sidebar.text_input("Password Baru", type="password")
    role = st.sidebar.selectbox("Role", ["viewer", "admin"])

    if st.sidebar.button("Daftar"):
        if new_user and new_pass:
            if save_user(new_user, new_pass, role):
                st.sidebar.success("Akun berhasil dibuat")
            else:
                st.sidebar.error("Username sudah terdaftar")
        else:
            st.sidebar.warning("Lengkapi data")

# ---------- LOGOUT ----------
if st.session_state.login:
    st.sidebar.divider()
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.write(f"🔑 Role: {st.session_state.role}")
    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

# ================== HALAMAN UTAMA ==================
st.title("📚 Sistem Nilai ICT")
st.subheader("SMPIT Nurul Qolbi Bekasi")

df = load_data()

# ================== ROLE BASED VIEW ==================
if not st.session_state.login:
    st.warning("🔒 Silakan login untuk mengakses data")

elif st.session_state.role == "admin":
    st.success("🛠️ Mode Admin (CRUD Aktif)")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Nama Siswa": st.column_config.TextColumn("Nama Lengkap"),
            "Nilai Akhir": st.column_config.NumberColumn("Nilai Akhir", format="%d"),
        },
    )

    if st.button("💾 Simpan Perubahan"):
        save_data(edited_df)
        st.success("Data berhasil disimpan")

    # ===== HAPUS SISWA =====
    with st.expander("🗑️ Hapus Siswa"):
        if not edited_df.empty:
            siswa = st.selectbox("Pilih Siswa", edited_df["Nama Siswa"].tolist())
            if st.button("Hapus"):
                new_df = edited_df[edited_df["Nama Siswa"] != siswa]
                save_data(new_df)
                st.warning(f"{siswa} dihapus")
                st.rerun()

elif st.session_state.role == "viewer":
    st.info("👀 Mode Viewer (Hanya Lihat)")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ================== STATISTIK ==================
if st.session_state.login and not df.empty:
    st.divider()
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Siswa", len(df))
    col2.metric("Rata-rata Nilai", f"{df['Nilai Akhir'].mean():.2f}")
    col3.metric("Nilai Tertinggi", df["Nilai Akhir"].max())
