import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="UMKM Keripik Pisang",
    page_icon="🌿",
    layout="wide"
)

# ======================
# CSS EARTHY
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f6f1e9,#ede0d4,#d6ccc2);
}

[data-testid="stSidebar"] {
    background: #5c4033;
    color: white;
}

h1, h2, h3 {
    color: #5c4033;
}
</style>
""", unsafe_allow_html=True)

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("keripik.db", check_same_thread=False)
c = conn.cursor()

# bahan pisang
c.execute("""
CREATE TABLE IF NOT EXISTS bahan (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    stok INTEGER
)
""")

# produk jadi
c.execute("""
CREATE TABLE IF NOT EXISTS produk (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    rasa TEXT,
    stok INTEGER,
    harga INTEGER
)
""")

# produksi
c.execute("""
CREATE TABLE IF NOT EXISTS produksi (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    bahan TEXT,
    jumlah INTEGER,
    hasil INTEGER
)
""")

# penjualan
c.execute("""
CREATE TABLE IF NOT EXISTS penjualan (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    produk TEXT,
    jumlah INTEGER,
    total INTEGER
)
""")

# pengeluaran
c.execute("""
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY,
    tanggal TEXT,
    nama TEXT,
    nominal INTEGER
)
""")

conn.commit()

# ======================
# LOGIN SIMPLE
# ======================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "12345":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Salah login")

    st.stop()

# ======================
# MENU
# ======================
menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Bahan Baku",
        "Produksi",
        "Produk Jadi",
        "Penjualan",
        "Pengeluaran"
    ]
)

# ======================
# DASHBOARD
# ======================
if menu == "Dashboard":
    st.title("🌿 Dashboard Keripik Pisang")

    produk = pd.read_sql("SELECT * FROM produk", conn)
    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)
    bahan = pd.read_sql("SELECT * FROM bahan", conn)

    omzet = penjualan["total"].sum() if not penjualan.empty else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Omzet", f"Rp {omzet:,}")
    col2.metric("📦 Produk", len(produk))
    col3.metric("🧪 Bahan", len(bahan))

# ======================
# BAHAN BAKU
# ======================
elif menu == "Bahan Baku":
    st.title("🧪 Bahan Baku (Pisang)")

    nama = st.selectbox("Jenis Pisang", ["Pisang Raja", "Pisang Kepok"])
    stok = st.number_input("Stok (kg)", min_value=0)

    if st.button("Tambah"):
        c.execute("INSERT INTO bahan VALUES (NULL,?,?)", (nama, stok))
        conn.commit()
        st.success("Bahan masuk")

    st.dataframe(pd.read_sql("SELECT * FROM bahan", conn))

# ======================
# PRODUKSI
# ======================
elif menu == "Produksi":
    st.title("🏭 Produksi Keripik")

    bahan = pd.read_sql("SELECT * FROM bahan", conn)

    if bahan.empty:
        st.warning("Isi bahan dulu")
    else:
        pilih = st.selectbox("Pilih Bahan", bahan["nama"])
        jumlah = st.number_input("Kg dipakai", min_value=1)

        hasil = jumlah * 2  # 1kg jadi 2kg keripik

        if st.button("Produksi"):
            c.execute("""
                INSERT INTO produksi VALUES (NULL,?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                pilih,
                jumlah,
                hasil
            ))

            conn.commit()
            st.success(f"Hasil keripik: {hasil} kg")

# ======================
# PRODUK JADI
# ======================
elif menu == "Produk Jadi":
    st.title("📦 Produk Keripik")

    nama = st.text_input("Nama Produk")
    rasa = st.selectbox("Rasa", ["Manis", "Asin"])
    stok = st.number_input("Stok", min_value=0)
    harga = st.number_input("Harga", min_value=0)

    if st.button("Simpan Produk"):
        c.execute("""
            INSERT INTO produk VALUES (NULL,?,?,?,?)
        """, (nama, rasa, stok, harga))

        conn.commit()
        st.success("Produk jadi ditambah")

    st.dataframe(pd.read_sql("SELECT * FROM produk", conn))

# ======================
# PENJUALAN
# ======================
elif menu == "Penjualan":
    st.title("🛒 Penjualan")

    produk = pd.read_sql("SELECT * FROM produk", conn)

    if produk.empty:
        st.warning("Belum ada produk jadi")
    else:
        pilih = st.selectbox("Produk", produk["nama"])
        qty = st.number_input("Jumlah", min_value=1)

        row = produk[produk["nama"] == pilih].iloc[0]
        total = qty * row["harga"]

        st.info(f"Total: Rp {total:,}")

        if st.button("Jual"):
            if qty > row["stok"]:
                st.error("Stok kurang")
            else:
                c.execute("""
                    INSERT INTO penjualan VALUES (NULL,?,?,?,?)
                """, (
                    datetime.now().strftime("%Y-%m-%d"),
                    pilih,
                    qty,
                    total
                ))

                c.execute("""
                    UPDATE produk SET stok = stok - ?
                    WHERE nama = ?
                """, (qty, pilih))

                conn.commit()
                st.success("Terjual")

# ======================
# PENGELUARAN
# ======================
elif menu == "Pengeluaran":
    st.title("💸 Pengeluaran")

    nama = st.text_input("Nama")
    nominal = st.number_input("Nominal")

    if st.button("Simpan"):
        c.execute("INSERT INTO pengeluaran VALUES (NULL,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d"), nama, nominal))
        conn.commit()
        st.success("Tersimpan")

    st.dataframe(pd.read_sql("SELECT * FROM pengeluaran", conn))
