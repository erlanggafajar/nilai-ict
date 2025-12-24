import streamlit as st


def require_login():
    if not st.session_state.get("login"):
        st.switch_page("pages/auth.py")
        st.stop()


def require_admin():
    require_login()
    if st.session_state.get("role") != "admin":
        st.error("⛔ Akses admin saja")
        st.stop()
