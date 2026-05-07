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
    page_title="Manajemen UMKM Produksi",
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

/* metric */
[data-testid="metric-container"] {
    background: rgba(255,250,243,0.85);
    border-radius: 15px;
    padding: 15px;
}

/* button */
.stButton > button {
    background: #6b705c;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS bahan_baku (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    stok INTEGER,
    satuan TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS produksi (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    nama_produk TEXT,
    jumlah INTEGER
)""")

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
# LOGIN
# ==============================
USER = "admin"
PASS = "12345"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login UMKM")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == USER and p == PASS:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Salah login")

    st.stop()

# ==============================
# MENU (FIXED)
# ==============================
menu = st.sidebar.radio(
    "🌿 Menu",
    [
        "📈 Dashboard",
        "🧪 Bahan Baku",
        "🏭 Produksi",
        "📦 Produk Jadi",
        "🛒 Penjualan",
        "💸 Pengeluaran",
        "📄 Laporan"
    ]
)

# ==============================
# DASHBOARD (FIX PRODUKSI SYSTEM)
# ==============================
if menu == "📈 Dashboard":

    st.title("🌿 Dashboard UMKM Produksi")

    bahan = pd.read_sql("SELECT * FROM bahan_baku", conn)
    produksi = pd.read_sql("SELECT * FROM produksi", conn)
    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)
    pengeluaran = pd.read_sql("SELECT * FROM pengeluaran", conn)

    total_jual = penjualan["total"].sum() if not penjualan.empty else 0
    total_keluar = pengeluaran["nominal"].sum() if not pengeluaran.empty else 0
    profit = total_jual - total_keluar

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Penjualan", f"Rp {total_jual:,}")
    col2.metric("💸 Pengeluaran", f"Rp {total_keluar:,}")
    col3.metric("📈 Profit", f"Rp {profit:,}")

    st.divider()

    st.subheader("🧪 Bahan Baku Menipis")
    st.dataframe(bahan[bahan["stok"] <= 5], use_container_width=True)

    st.subheader("🏭 Produksi Terakhir")
    st.dataframe(produksi.tail(5), use_container_width=True)

# ==============================
# BAHAN BAKU
# ==============================
elif menu == "🧪 Bahan Baku":

    st.title("🧪 Bahan Baku")

    with st.form("bahan"):
        nama = st.text_input("Nama")
        stok = st.number_input("Stok", min_value=0)
        satuan = st.selectbox("Satuan", ["Kg","Gram","Liter","Pcs"])

        if st.form_submit_button("Tambah"):
            cursor.execute(
                "INSERT INTO bahan_baku VALUES (NULL,?,?,?)",
                (nama, stok, satuan)
            )
            conn.commit()
            st.success("OK")

    st.dataframe(pd.read_sql("SELECT * FROM bahan_baku", conn))

# ==============================
# PRODUKSI
# ==============================
elif menu == "🏭 Produksi":

    st.title("🏭 Produksi")

    with st.form("produksi"):
        nama = st.text_input("Nama Produk")
        jumlah = st.number_input("Jumlah", min_value=1)

        if st.form_submit_button("Simpan"):
            cursor.execute(
                "INSERT INTO produksi VALUES (NULL,?,?,?)",
                (datetime.now().strftime("%Y-%m-%d"), nama, jumlah)
            )
            conn.commit()
            st.success("Tersimpan")

    st.dataframe(pd.read_sql("SELECT * FROM produksi", conn))

# ==============================
# PRODUK JADI
# ==============================
elif menu == "📦 Produk Jadi":

    st.title("📦 Produk Jadi")

    st.dataframe(pd.read_sql("SELECT * FROM produk", conn))

# ==============================
# PENJUALAN
# ==============================
elif menu == "🛒 Penjualan":

    st.title("🛒 Penjualan")

    produk_df = pd.read_sql("SELECT * FROM produk", conn)

    if produk_df.empty:
        st.warning("⚠️ Belum ada produk. Tambahkan dulu di menu Produk.")
    else:

        produk = st.selectbox("Pilih Produk", produk_df["nama"])
        jumlah = st.number_input("Jumlah", min_value=1, step=1)

        data = produk_df[produk_df["nama"] == produk].iloc[0]
        total = int(data["harga_jual"]) * int(jumlah)

        st.info(f"💰 Total Harga: Rp {total:,}")

        if st.button("💾 Simpan Penjualan"):

            try:
                cursor.execute("""
                    INSERT INTO penjualan (tanggal, produk, jumlah, total)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().strftime("%Y-%m-%d"),
                    produk,
                    jumlah,
                    total
                ))

                conn.commit()

                st.success("✅ Penjualan berhasil disimpan!")

                # DEBUG: langsung reload data
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    st.subheader("📊 Data Penjualan")

    penjualan_df = pd.read_sql("SELECT * FROM penjualan", conn)
    st.dataframe(penjualan_df, use_container_width=True)

# ==============================
# PENGELUARAN
# ==============================
elif menu == "💸 Pengeluaran":

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

    st.dataframe(pd.read_sql("SELECT * FROM pengeluaran", conn))

# ==============================
# LAPORAN
# ==============================
elif menu == "📄 Laporan":

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
