import streamlit as st
import pandas as pd
import psycopg2

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


# ===== DATABASE (POSTGRESQL - SUPABASE POOLER) =====
def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
    )


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
