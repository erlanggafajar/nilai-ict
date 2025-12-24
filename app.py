import streamlit as st
import pandas as pd
from db import get_connection

from auth_guard import require_login

require_login()

st.set_page_config(
    page_title="Login Sistem Nilai ICT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===== SESSION =====
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.role = ""

# ===== PROTEKSI =====
if not st.session_state.get("login"):
    st.switch_page("pages/auth.py")
    st.stop()


def load_nilai():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM nilai_siswa ORDER BY nama_siswa", conn)
    conn.close()
    return df


# ===== UI =====
st.title("📚 Sistem Nilai ICT")
st.write(f"👤 {st.session_state.username} ({st.session_state.role})")

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("pages/auth.py")

df = load_nilai()
st.dataframe(df, use_container_width=True)
