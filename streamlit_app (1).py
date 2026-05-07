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

c.execute("""CREATE TABLE IF NOT EXISTS bahan (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    stok REAL,
    satuan TEXT
)""")

conn.commit()

# ======================
# SEED DATA (FIXED 100%)
# ======================
cek = pd.read_sql("SELECT COUNT(*) as c FROM bahan", conn)

if cek["c"][0] == 0:

    data = [
        ("Pisang Raja", 50, "kg"),
        ("Pisang Kepok", 50, "kg"),
        ("Minyak Goreng", 20, "liter"),
        ("Garam", 10, "kg"),
        ("Gula", 10, "kg"),
        ("Gas LPG", 10, "tabung")
    ]

    c.executemany("""
        INSERT INTO bahan (nama, stok, satuan)
        VALUES (?, ?, ?)
    """, data)

    conn.commit()
# ======================
# LOGIN
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
    ["Dashboard", "Bahan Baku", "Produksi", "Produk Jadi", "Penjualan", "Pengeluaran"]
)

# ======================
# DASHBOARD
# ======================
if menu == "Dashboard":

    st.title("🌿 Dashboard")

    bahan = pd.read_sql("SELECT * FROM bahan", conn)
    produk = pd.read_sql("SELECT * FROM produk", conn)
    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)

    omzet = penjualan["total"].sum() if not penjualan.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Omzet", f"Rp {omzet:,}")
    col2.metric("Produk", len(produk))
    col3.metric("Bahan", len(bahan))

# ======================
# BAHAN
# ======================
elif menu == "Bahan Baku":

    st.title("🧪 Bahan Baku")

    bahan = pd.read_sql("SELECT * FROM bahan", conn)

    st.dataframe(bahan, use_container_width=True)

    st.subheader("Tambah Bahan")

    nama = st.text_input("Nama bahan")
    stok = st.number_input("Stok", min_value=0.0)
    satuan = st.selectbox("Satuan", ["kg", "liter", "tabung"])

    if st.button("Tambah"):

        if nama == "":
            st.error("Nama tidak boleh kosong")
        else:
            c.execute("""
                INSERT INTO bahan (nama, stok, satuan)
                VALUES (?, ?, ?)
            """, (nama, stok, satuan))

            conn.commit()
            st.success("Bahan berhasil ditambah")
            st.rerun()

# ======================
# PRODUKSI (FIX TOTAL)
# ======================
elif menu == "Produksi":

    st.title("🏭 Produksi Keripik")

    bahan = pd.read_sql("SELECT * FROM bahan", conn)

    jenis = st.selectbox("Pisang", ["Pisang Raja", "Pisang Kepok"])
    jumlah = st.number_input("Kg Pisang", min_value=1)

    if st.button("Produksi"):

        kebutuhan = [
            (jenis, jumlah),
            ("Minyak Goreng", jumlah * 0.2),
            ("Garam", jumlah * 0.05),
            ("Gula", jumlah * 0.03),
        ]

        # cek stok
        cukup = True

        for nama, qty in kebutuhan:
            c.execute("SELECT stok FROM bahan WHERE nama=?", (nama,))
            data = c.fetchone()

            if data is None or data[0] < qty:
                cukup = False

        if not cukup:
            st.error("Stok tidak cukup")
        else:
            for nama, qty in kebutuhan:
                c.execute("""
                    UPDATE bahan
                    SET stok = stok - ?
                    WHERE nama = ?
                """, (qty, nama))

            conn.commit()
            st.success("Produksi berhasil 🍌")

# ======================
# PRODUK
# ======================
elif menu == "Produk Jadi":

    st.title("📦 Produk Jadi")

    nama = st.text_input("Nama")
    rasa = st.selectbox("Rasa", ["Manis", "Asin"])
    stok = st.number_input("Stok", min_value=0)
    harga = st.number_input("Harga", min_value=0)

    if st.button("Simpan"):
        c.execute("INSERT INTO produk VALUES (NULL,?,?,?,?)",
                  (nama, rasa, stok, harga))
        conn.commit()
        st.success("OK")

    st.dataframe(pd.read_sql("SELECT * FROM produk", conn))

# ======================
# PENJUALAN (FIX)
# ======================
elif menu == "Penjualan":

    st.title("🛒 Penjualan")

    produk = pd.read_sql("SELECT * FROM produk", conn)

    if produk.empty:
        st.warning("Belum ada produk")
    else:
        pilih = st.selectbox("Produk", produk["nama"])
        qty = st.number_input("Jumlah", min_value=1)

        row = produk[produk["nama"] == pilih].iloc[0]
        total = qty * row["harga"]

        st.info(f"Total Rp {total:,}")

        if st.button("Jual"):

            if qty > row["stok"]:
                st.error("Stok kurang")
            else:
                c.execute("""INSERT INTO penjualan VALUES (NULL,?,?,?,?)""",
                          (datetime.now().strftime("%Y-%m-%d"), pilih, qty, total))

                c.execute("""UPDATE produk SET stok=stok-? WHERE nama=?""",
                          (qty, pilih))

                conn.commit()
                st.success("Berhasil jual")

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
        st.success("OK")

    st.dataframe(pd.read_sql("SELECT * FROM pengeluaran", conn))
