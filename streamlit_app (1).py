import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
import shutil

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="Manajemen Usaha",
    page_icon="🌿",
    layout="wide"
)

# ==============================
# EARTHY THEME
# ==============================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#f6f1e9,#ede0d4,#d6ccc2);
}

.block-container {
    padding: 2rem;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#5c4033,#7f5539);
}
[data-testid="stSidebar"] * {
    color: white;
}

/* cards */
[data-testid="metric-container"] {
    background: rgba(255,250,243,0.8);
    padding: 15px;
    border-radius: 15px;
}

/* button */
.stButton > button {
    background: #6b705c;
    color: white;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS produk (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    harga_beli INTEGER,
    harga_jual INTEGER,
    stok INTEGER,
    kategori TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS penjualan (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    produk TEXT,
    jumlah INTEGER,
    total INTEGER
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    nama TEXT,
    nominal INTEGER
)""")

conn.commit()

# ==============================
# LOGIN SIMPLE
# ==============================
USERNAME = "admin"
PASSWORD = "12345"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Salah")

    st.stop()

# ==============================
# SIDEBAR (ONLY ONCE!)
# ==============================
menu = st.sidebar.radio(
    "🌿 Menu",
    ["Dashboard", "Produk", "Penjualan", "Pengeluaran", "Laporan", "Backup"]
)

# ==============================
# DASHBOARD
# ==============================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)
    pengeluaran = pd.read_sql("SELECT * FROM pengeluaran", conn)

    total_jual = penjualan["total"].sum() if not penjualan.empty else 0
    total_keluar = pengeluaran["nominal"].sum() if not pengeluaran.empty else 0
    profit = total_jual - total_keluar

    col1, col2, col3 = st.columns(3)

    col1.metric("Penjualan", f"Rp {total_jual:,}")
    col2.metric("Pengeluaran", f"Rp {total_keluar:,}")
    col3.metric("Profit", f"Rp {profit:,}")

    st.divider()

# ==============================
# PRODUK
# ==============================
elif menu == "Produk":

    st.title("📦 Produk")

    with st.form("produk"):
        nama = st.text_input("Nama")
        hb = st.number_input("Harga Beli")
        hj = st.number_input("Harga Jual")
        stok = st.number_input("Stok")
        kategori = st.text_input("Kategori")

        if st.form_submit_button("Tambah"):
            cursor.execute(
                "INSERT INTO produk VALUES (NULL,?,?,?,?,?)",
                (nama, hb, hj, stok, kategori)
            )
            conn.commit()
            st.success("OK")

    df = pd.read_sql("SELECT * FROM produk", conn)
    st.dataframe(df, use_container_width=True)

# ==============================
# PENJUALAN
# ==============================
elif menu == "Penjualan":

    st.title("🛒 Penjualan")

    produk = pd.read_sql("SELECT * FROM produk", conn)

    if produk.empty:
        st.warning("Kosong")
    else:
        p = st.selectbox("Produk", produk["nama"])
        j = st.number_input("Jumlah", 1)

        data = produk[produk["nama"] == p].iloc[0]
        total = data["harga_jual"] * j

        st.info(f"Total {total}")

        if st.button("Simpan"):
            cursor.execute(
                "INSERT INTO penjualan VALUES (NULL,?,?,?,?)",
                (datetime.now().strftime("%Y-%m-%d"), p, j, total)
            )
            conn.commit()
            st.success("OK")

# ==============================
# PENGELUARAN
# ==============================
elif menu == "Pengeluaran":

    st.title("💸 Pengeluaran")

    with st.form("keluar"):
        nama = st.text_input("Nama")
        n = st.number_input("Nominal")

        if st.form_submit_button("Simpan"):
            cursor.execute(
                "INSERT INTO pengeluaran VALUES (NULL,?,?,?)",
                (datetime.now().strftime("%Y-%m-%d"), nama, n)
            )
            conn.commit()
            st.success("OK")

    df = pd.read_sql("SELECT * FROM pengeluaran", conn)
    st.dataframe(df, use_container_width=True)

# ==============================
# LAPORAN
# ==============================
elif menu == "Laporan":

    st.title("📄 Laporan")

    df = pd.read_sql("""
        SELECT tanggal, SUM(total) as total
        FROM penjualan
        GROUP BY tanggal
    """, conn)

    st.dataframe(df)

    if not df.empty:
        fig = px.line(df, x="tanggal", y="total")
        st.plotly_chart(fig)

# ==============================
# BACKUP
# ==============================
elif menu == "Backup":

    st.title("💾 Backup")

    if st.button("Backup"):
        if not os.path.exists("backup"):
            os.makedirs("backup")

        name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy("usaha.db", f"backup/{name}")

        st.success("Backup done")
