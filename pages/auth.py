import streamlit as st
import hashlib
import mysql.connector

st.set_page_config(page_title="Auth - Sistem Nilai ICT")


# ================== DATABASE ==================
def get_connection():
    try:
        # Debug: Show which credentials are being used
        st.sidebar.write("Database Connection Info:")
        st.sidebar.json({
            "host": st.secrets["MYSQL_HOST"],
            "port": st.secrets["MYSQL_PORT"],
            "user": st.secrets["MYSQL_USER"],
            "database": st.secrets["MYSQL_DB"]
        }, expanded=False)
        
        conn = mysql.connector.connect(
            host=st.secrets["MYSQL_HOST"],
            user=st.secrets["MYSQL_USER"],
            password=st.secrets["MYSQL_PASSWORD"],
            database=st.secrets["MYSQL_DB"],
            port=int(st.secrets["MYSQL_PORT"]),
        )
        return conn
    except KeyError as e:
        st.error(f"❌ Konfigurasi database tidak lengkap: {str(e)}")
        st.stop()
    except mysql.connector.Error as err:
        st.error(f"❌ Gagal terhubung ke database: {err}")
        st.error(f"Menggunakan user: {st.secrets.get('MYSQL_USER', 'tidak ada')}")
        st.error(f"Host: {st.secrets.get('MYSQL_HOST', 'tidak ada')}")
        st.error(f"Database: {st.secrets.get('MYSQL_DB', 'tidak ada')}")
        st.stop()


# ================== SECURITY ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================== AUTH FUNCTIONS ==================
def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT username, role FROM users WHERE username=%s AND password=%s",
        (username, hash_password(password)),
    )
    user = cur.fetchone()
    conn.close()
    return user


def register_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    # cek username sudah ada
    cur.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        conn.close()
        return False, "Username sudah terdaftar"

    # role otomatis viewer
    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, 'viewer')",
        (username, hash_password(password)),
    )
    conn.commit()
    conn.close()
    return True, "Akun berhasil dibuat (role: viewer)"


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
