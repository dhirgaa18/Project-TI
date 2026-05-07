# =========================
# FILE: app.py
# Jalankan:
# streamlit run app.py
# =========================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Manajemen Usaha",
    page_icon="📊",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# MEMBUAT TABEL
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS produk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    harga_beli INTEGER,
    harga_jual INTEGER,
    stok INTEGER,
    kategori TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS penjualan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    produk TEXT,
    jumlah INTEGER,
    total INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    nama TEXT,
    nominal INTEGER
)
""")

conn.commit()

# =========================
# SIDEBAR MENU
# =========================
menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Input Penjualan",
        "Produk & Stok",
        "Pengeluaran",
        "Laporan"
    ]
)

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("📊 Dashboard Usaha")

    # Total penjualan
    total_penjualan = cursor.execute("""
    SELECT IFNULL(SUM(total),0) FROM penjualan
    """).fetchone()[0]

    # Total pengeluaran
    total_pengeluaran = cursor.execute("""
    SELECT IFNULL(SUM(nominal),0) FROM pengeluaran
    """).fetchone()[0]

    # Profit
    profit = total_penjualan - total_pengeluaran

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Penjualan", f"Rp {total_penjualan:,}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,}")
    col3.metric("Profit", f"Rp {profit:,}")

    st.divider()

    st.subheader("Produk Hampir Habis")

    stok_df = pd.read_sql_query("""
    SELECT nama, stok
    FROM produk
    WHERE stok <= 5
    """, conn)

    st.dataframe(stok_df, use_container_width=True)

# =========================
# INPUT PENJUALAN
# =========================
elif menu == "Input Penjualan":

    st.title("🛒 Input Penjualan")

    produk_df = pd.read_sql_query(
        "SELECT * FROM produk",
        conn
    )

    if produk_df.empty:
        st.warning("Belum ada produk.")
    else:

        produk_pilih = st.selectbox(
            "Pilih Produk",
            produk_df["nama"]
        )

        jumlah = st.number_input(
            "Jumlah",
            min_value=1,
            step=1
        )

        produk_data = produk_df[
            produk_df["nama"] == produk_pilih
        ].iloc[0]

        total = produk_data["harga_jual"] * jumlah

        st.info(f"Total: Rp {total:,}")

        if st.button("Simpan Penjualan"):

            # simpan penjualan
            cursor.execute("""
            INSERT INTO penjualan
            (tanggal, produk, jumlah, total)
            VALUES (?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                produk_pilih,
                jumlah,
                total
            ))

            # update stok
            stok_baru = produk_data["stok"] - jumlah

            cursor.execute("""
            UPDATE produk
            SET stok = ?
            WHERE nama = ?
            """, (
                stok_baru,
                produk_pilih
            ))

            conn.commit()

            st.success("Penjualan berhasil disimpan!")

# =========================
# PRODUK & STOK
# =========================
elif menu == "Produk & Stok":

    st.title("📦 Produk & Stok")

    with st.form("form_produk"):

        nama = st.text_input("Nama Produk")

        harga_beli = st.number_input(
            "Harga Beli",
            min_value=0
        )

        harga_jual = st.number_input(
            "Harga Jual",
            min_value=0
        )

        stok = st.number_input(
            "Stok",
            min_value=0
        )

        kategori = st.text_input("Kategori")

        submit = st.form_submit_button("Tambah Produk")

        if submit:

            cursor.execute("""
            INSERT INTO produk
            (nama, harga_beli, harga_jual, stok, kategori)
            VALUES (?, ?, ?, ?, ?)
            """, (
                nama,
                harga_beli,
                harga_jual,
                stok,
                kategori
            ))

            conn.commit()

            st.success("Produk berhasil ditambahkan!")

    st.divider()

    st.subheader("Daftar Produk")

    produk_df = pd.read_sql_query(
        "SELECT * FROM produk",
        conn
    )

    st.dataframe(
        produk_df,
        use_container_width=True
    )

# =========================
# PENGELUARAN
# =========================
elif menu == "Pengeluaran":

    st.title("💸 Pengeluaran")

    with st.form("form_pengeluaran"):

        nama = st.text_input("Nama Pengeluaran")

        nominal = st.number_input(
            "Nominal",
            min_value=0
        )

        submit = st.form_submit_button("Simpan")

        if submit:

            cursor.execute("""
            INSERT INTO pengeluaran
            (tanggal, nama, nominal)
            VALUES (?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                nama,
                nominal
            ))

            conn.commit()

            st.success("Pengeluaran berhasil ditambahkan!")

    st.divider()

    pengeluaran_df = pd.read_sql_query(
        "SELECT * FROM pengeluaran",
        conn
    )

    st.dataframe(
        pengeluaran_df,
        use_container_width=True
    )

# =========================
# LAPORAN
# =========================
elif menu == "Laporan":

    st.title("📈 Laporan Penjualan")

    laporan_df = pd.read_sql_query("""
    SELECT tanggal, SUM(total) as total_harian
    FROM penjualan
    GROUP BY tanggal
    """, conn)

    st.dataframe(
        laporan_df,
        use_container_width=True
    )

    st.line_chart(
        laporan_df.set_index("tanggal")
    )
