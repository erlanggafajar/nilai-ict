import streamlit as st
import hashlib
import mysql.connector

st.set_page_config(page_title="Login - Sistem Nilai ICT")


def get_connection():
    return mysql.connector.connect(
        host=st.secrets["MYSQL_HOST"],
        user=st.secrets["MYSQL_USER"],
        password=st.secrets["MYSQL_PASSWORD"],
        database=st.secrets["MYSQL_DB"],
        port=st.secrets["MYSQL_PORT"],
    )


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, hash_password(password)),
    )
    user = cur.fetchone()
    conn.close()
    return user


st.title("🔐 Login Sistem Nilai ICT")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = login_user(username, password)
    if user:
        st.session_state.login = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.success("Login berhasil")
        st.switch_page("app.py")
    else:
        st.error("Username atau password salah")
