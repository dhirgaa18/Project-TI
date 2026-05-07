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

    st.title("🌿 Dashboard UMKM Pro")

    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)
    bahan = pd.read_sql("SELECT * FROM bahan_baku", conn)

    omzet = penjualan["total"].sum() if not penjualan.empty else 0

    col1, col2 = st.columns(2)

    col1.metric("💰 Omzet", f"Rp {omzet:,}")
    col2.metric("🧪 Total Bahan", len(bahan))

    st.subheader("⚠️ Stok Kritis")

    st.dataframe(bahan[bahan["stok"] <= 5], use_container_width=True)

# ==============================
# BAHAN BAKU
# ==============================
elif menu == "🧪 Bahan Baku":

    st.title("🧪 Bahan Baku")

    bahan_df = pd.read_sql("SELECT * FROM bahan_baku", conn)

    edited = st.data_editor(
        bahan_df,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 Simpan Bahan"):
        cursor.execute("DELETE FROM bahan_baku")
        conn.commit()

        for _, r in edited.iterrows():
            cursor.execute("""
                INSERT INTO bahan_baku (nama, stok, satuan)
                VALUES (?, ?, ?)
            """, (r["nama"], r["stok"], r["satuan"]))

        conn.commit()
        st.success("Bahan update")

# ==============================
# PRODUKSI
# ==============================
elif menu == "🏭 Produksi":

    st.title("🏭 Produksi")

    bahan = pd.read_sql("SELECT * FROM bahan_baku", conn)

    produk = st.text_input("Nama Produk")
    jumlah = st.number_input("Jumlah Produksi", min_value=1)

    bahan_pakai = st.selectbox("Pilih Bahan", bahan["nama"] if not bahan.empty else ["-"])
    pakai_qty = st.number_input("Jumlah Bahan Dipakai", min_value=1)

    if st.button("Produksi"):

        # simpan produksi
        cursor.execute("""
            INSERT INTO produksi (tanggal, nama_produk, jumlah)
            VALUES (?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d"), produk, jumlah))

        # kurangi bahan
        cursor.execute("""
            UPDATE bahan_baku
            SET stok = stok - ?
            WHERE nama = ?
        """, (pakai_qty, bahan_pakai))

        conn.commit()
        st.success("Produksi berhasil + bahan berkurang")

# ==============================
# PRODUK JADI
# ==============================
elif menu == "📦 Produk Jadi":

    st.title("📦 Produk Jadi (Hasil Produksi)")

    produksi = pd.read_sql("""
        SELECT nama_produk,
               SUM(jumlah) as total
        FROM produksi
        GROUP BY nama_produk
    """, conn)

    st.dataframe(produksi, use_container_width=True)

# ==============================
# PENJUALAN
# ==============================
elif menu == "🛒 Penjualan":

    st.title("🛒 Penjualan")

    produk = pd.read_sql("SELECT * FROM produk", conn)

    if not produk.empty:

        p = st.selectbox("Produk", produk["nama"])
        j = st.number_input("Jumlah", 1)

        data = produk[produk["nama"] == p].iloc[0]
        total = data["harga_jual"] * j

        st.info(f"Total Rp {total:,}")

        if st.button("Jual"):

            if data["stok"] < j:
                st.error("Stok kurang")
            else:

                cursor.execute("""
                    INSERT INTO penjualan VALUES (NULL,?,?,?,?)
                """, (datetime.now().strftime("%Y-%m-%d"), p, j, total))

                cursor.execute("""
                    UPDATE produk
                    SET stok = stok - ?
                    WHERE nama = ?
                """, (j, p))

                conn.commit()

                st.success("Penjualan berhasil")

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
