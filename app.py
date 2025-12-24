import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Sistem Nilai ICT", layout="wide")

# ===== SESSION =====
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.role = ""

# ===== PROTEKSI =====
if not st.session_state.login:
    st.warning("🔒 Silakan login terlebih dahulu")
    st.page_link("pages/auth.py", label="👉 Login ke Sistem")
    st.stop()


# ===== DATABASE =====
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["MYSQL_HOST"],
        user=st.secrets["MYSQL_USER"],
        password=st.secrets["MYSQL_PASSWORD"],
        database=st.secrets["MYSQL_DB"],
        port=st.secrets["MYSQL_PORT"],
    )


def load_nilai():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM nilai_siswa", conn)
    conn.close()
    return df


st.title("📚 Sistem Nilai ICT")
st.write(f"👤 {st.session_state.username} ({st.session_state.role})")

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("pages/auth.py")

df = load_nilai()
st.dataframe(df, use_container_width=True)
