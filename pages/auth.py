import streamlit as st
import hashlib
import psycopg2
import bcrypt

st.set_page_config(page_title="Auth - Sistem Nilai ICT")


# ================== DATABASE ==================
def get_connection():
    return psycopg2.connect(
        hostaddr=st.secrets["DB_HOST"],  # ⬅️ PENTING
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
    )


# ================== SECURITY ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================== AUTH FUNCTIONS ==================
def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("select id, password, role from users where username=%s", (username,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row and bcrypt.checkpw(password.encode(), row[1].encode()):
        return {"id": row[0], "role": row[2]}
    return None


def register_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cur.execute(
            "insert into users (username, password, role) values (%s, %s, 'viewer')",
            (username, hashed),
        )
        conn.commit()
        return True, "Registrasi berhasil (role: viewer)"
    except:
        return False, "Username sudah digunakan"
    finally:
        cur.close()
        conn.close()


# ================== UI ==================
st.title("🔐 Sistem Autentikasi")

tab_login, tab_daftar = st.tabs(["Login", "Daftar"])

# ---------- LOGIN ----------
with tab_login:
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

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

# ---------- REGISTER ----------
with tab_daftar:
    new_user = st.text_input("Username Baru", key="reg_user")
    new_pass = st.text_input("Password Baru", type="password", key="reg_pass")

    if st.button("Daftar"):
        if not new_user or not new_pass:
            st.warning("Lengkapi semua field")
        else:
            ok, msg = register_user(new_user, new_pass)
            if ok:
                st.success(msg)
                st.info("Silakan login menggunakan akun tersebut")
            else:
                st.error(msg)
