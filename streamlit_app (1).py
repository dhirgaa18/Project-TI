import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
import shutil

# ====================================
# KONFIGURASI HALAMAN
# ====================================
st.set_page_config(
    page_title="Manajemen Usaha",
    page_icon="📊",
    layout="wide"
)

# ====================================
# CUSTOM CSS - EARTHY THEME
# ====================================
st.markdown("""
<style>

/* Background utama */
.stApp {
    background: linear-gradient(
        135deg,
        #f6f1e9,
        #ede0d4,
        #d6ccc2
    );
}

/* Container utama */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #5c4033,
        #7f5539
    );
    border-right: 2px solid #b08968;
}

[data-testid="stSidebar"] * {
    color: #fffaf3;
}

/* Judul */
h1, h2, h3 {
    color: #5c4033;
    font-weight: 700;
}

/* Metric Card */
[data-testid="metric-container"] {
    background: rgba(255, 250, 243, 0.75);
    border: 1px solid rgba(176, 137, 104, 0.3);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 20px rgba(92, 64, 51, 0.08);
}

/* Form */
form {
    background: rgba(255, 250, 243, 0.78);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 6px 18px rgba(92, 64, 51, 0.08);
}

/* Button */
.stButton > button {
    background: linear-gradient(
        90deg,
        #6b705c,
        #a5a58d
    );
    color: white;
    border-radius: 12px;
    border: none;
    padding: 12px 24px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(
        90deg,
        #5c4033,
        #7f5539
    );
    color: white;
}

/* Input */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
    border: 1px solid #b7b7a4 !important;
    background-color: #fffaf3 !important;
    color: #5c4033 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(92, 64, 51, 0.05);
}

/* Alert */
.stAlert {
    border-radius: 12px;
}

/* Login box */
.login-box {
    background: rgba(255,250,243,0.75);
    padding: 30px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 24px rgba(92,64,51,0.1);
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: #b7b7a4;
}

</style>
""", unsafe_allow_html=True)


# ====================================
# DATABASE
# ====================================
conn = sqlite3.connect(
    "usaha.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ====================================
# MEMBUAT TABEL
# ====================================
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

# ====================================
# TABEL BAHAN BAKU
# ====================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS bahan_baku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    stok INTEGER,
    satuan TEXT
)
""")

# ====================================
# TABEL PRODUKSI
# ====================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS produksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    nama_produk TEXT,
    jumlah INTEGER
)
""")

conn.commit()


# ====================================
# LOGIN
# ====================================
USERNAME = "admin"
PASSWORD = "12345"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username == USERNAME and password == PASSWORD:

            st.session_state.login = True
            st.success("Login berhasil")
            st.rerun()

        else:
            st.error("Username atau Password salah")

    st.stop()

```python id="menu-produksi"
# ====================================
# SIDEBAR
# ====================================
st.sidebar.title("🌿 Manajemen Usaha")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "📈 Dashboard",
        "🧪 Bahan Baku",
        "🏭 Produksi",
        "📦 Produk Jadi",
        "🛒 Penjualan",
        "💸 Pengeluaran",
        "📄 Laporan",
        "💾 Backup Database"
    ]
)

# ====================================
# DASHBOARD
# ====================================
if menu == "Dashboard":

    st.title("📈 Dashboard Usaha")

    penjualan_df = pd.read_sql(
        "SELECT * FROM penjualan",
        conn
    )

    pengeluaran_df = pd.read_sql(
        "SELECT * FROM pengeluaran",
        conn
    )

    produk_df = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    total_penjualan = (
        penjualan_df["total"].sum()
        if not penjualan_df.empty
        else 0
    )

    total_pengeluaran = (
        pengeluaran_df["nominal"].sum()
        if not pengeluaran_df.empty
        else 0
    )

    profit = total_penjualan - total_pengeluaran

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Penjualan",
        f"Rp {total_penjualan:,}"
    )

    col2.metric(
        "Pengeluaran",
        f"Rp {total_pengeluaran:,}"
    )

    col3.metric(
        "Profit",
        f"Rp {profit:,}"
    )

    st.divider()

    st.subheader("📦 Produk Hampir Habis")

    stok_tipis = (
        produk_df[produk_df["stok"] <= 5]
        if not produk_df.empty
        else pd.DataFrame()
    )

    st.dataframe(
        stok_tipis,
        use_container_width=True
    )
```python id="fitur-produksi"
# ====================================
# BAHAN BAKU
# ====================================
elif menu == "🧪 Bahan Baku":

    st.title("🧪 Data Bahan Baku")

    with st.form("form_bahan"):

        nama = st.text_input("Nama Bahan")

        stok = st.number_input(
            "Stok",
            min_value=0
        )

        satuan = st.selectbox(
            "Satuan",
            ["Kg", "Gram", "Liter", "Pcs"]
        )

        submit = st.form_submit_button(
            "Tambah Bahan"
        )

        if submit:

            cursor.execute(
                """
                INSERT INTO bahan_baku
                (nama, stok, satuan)
                VALUES (?, ?, ?)
                """,
                (
                    nama,
                    stok,
                    satuan
                )
            )

            conn.commit()

            st.success(
                "Bahan berhasil ditambahkan"
            )

    bahan_df = pd.read_sql(
        "SELECT * FROM bahan_baku",
        conn
    )

    st.dataframe(
        bahan_df,
        use_container_width=True
    )

# ====================================
# PRODUKSI
# ====================================
elif menu == "🏭 Produksi":

    st.title("🏭 Produksi Hari Ini")

    with st.form("form_produksi"):

        nama_produk = st.text_input(
            "Nama Produk"
        )

        jumlah = st.number_input(
            "Jumlah Produksi",
            min_value=1
        )

        submit = st.form_submit_button(
            "Simpan Produksi"
        )

        if submit:

            cursor.execute(
                """
                INSERT INTO produksi
                (tanggal, nama_produk, jumlah)
                VALUES (?, ?, ?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d"),
                    nama_produk,
                    jumlah
                )
            )

            conn.commit()

            st.success(
                "Data produksi berhasil disimpan"
            )

    produksi_df = pd.read_sql(
        "SELECT * FROM produksi",
        conn
    )

    st.dataframe(
        produksi_df,
        use_container_width=True
    )

# ====================================
# PRODUK JADI
# ====================================
elif menu == "📦 Produk Jadi":

    st.title("📦 Produk Jadi")

    produk_df = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    st.dataframe(
        produk_df,
        use_container_width=True
    )

# ====================================
# PRODUK
# ====================================
elif menu == "Produk":

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

        submit = st.form_submit_button(
            "Tambah Produk"
        )

        if submit:

            cursor.execute(
                """
                INSERT INTO produk
                (nama, harga_beli, harga_jual, stok, kategori)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    nama,
                    harga_beli,
                    harga_jual,
                    stok,
                    kategori
                )
            )

            conn.commit()

            st.success(
                "Produk berhasil ditambahkan"
            )

    produk_df = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    st.dataframe(
        produk_df,
        use_container_width=True
    )

# ====================================
# PENJUALAN
# ====================================
elif menu == "Penjualan":

    st.title("🛒 Input Penjualan")

    produk_df = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    if produk_df.empty:

        st.warning("Belum ada produk")

    else:

        produk = st.selectbox(
            "Pilih Produk",
            produk_df["nama"]
        )

        jumlah = st.number_input(
            "Jumlah",
            min_value=1,
            step=1
        )

        selected = produk_df[
            produk_df["nama"] == produk
        ].iloc[0]

        total = (
            selected["harga_jual"] * jumlah
        )

        st.info(
            f"Total Harga = Rp {total:,}"
        )

        if st.button(
            "Simpan Penjualan"
        ):

            stok_baru = (
                selected["stok"] - jumlah
            )

            if stok_baru < 0:

                st.error(
                    "Stok tidak cukup"
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO penjualan
                    (tanggal, produk, jumlah, total)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        datetime.now().strftime("%Y-%m-%d"),
                        produk,
                        jumlah,
                        total
                    )
                )

                cursor.execute(
                    """
                    UPDATE produk
                    SET stok = ?
                    WHERE nama = ?
                    """,
                    (
                        stok_baru,
                        produk
                    )
                )

                conn.commit()

                st.success(
                    "Penjualan berhasil disimpan"
                )

# ====================================
# PENGELUARAN
# ====================================
elif menu == "Pengeluaran":

    st.title("💸 Pengeluaran")

    with st.form("form_pengeluaran"):

        nama = st.text_input(
            "Nama Pengeluaran"
        )

        nominal = st.number_input(
            "Nominal",
            min_value=0
        )

        submit = st.form_submit_button(
            "Simpan"
        )

        if submit:

            cursor.execute(
                """
                INSERT INTO pengeluaran
                (tanggal, nama, nominal)
                VALUES (?, ?, ?)
                """,
                (
                    datetime.now().strftime("%Y-%m-%d"),
                    nama,
                    nominal
                )
            )

            conn.commit()

            st.success(
                "Pengeluaran berhasil ditambahkan"
            )

    pengeluaran_df = pd.read_sql(
        "SELECT * FROM pengeluaran",
        conn
    )

    st.dataframe(
        pengeluaran_df,
        use_container_width=True
    )

# ====================================
# LAPORAN
# ====================================
elif menu == "Laporan":

    st.title("📈 Laporan Penjualan")

    laporan_df = pd.read_sql(
        """
        SELECT tanggal,
               SUM(total) as total_harian
        FROM penjualan
        GROUP BY tanggal
        """,
        conn
    )

    st.dataframe(
        laporan_df,
        use_container_width=True
    )

    if not laporan_df.empty:

        fig = px.line(
            laporan_df,
            x="tanggal",
            y="total_harian",
            title="Grafik Penjualan"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    export_file = "laporan_penjualan.xlsx"

    laporan_df.to_excel(
        export_file,
        index=False
    )

    with open(export_file, "rb") as file:

        st.download_button(
            label="⬇ Download Excel",
            data=file,
            file_name=export_file
        )

# ====================================
# BACKUP DATABASE
# ====================================
elif menu == "Backup Database":

    st.title("💾 Backup Database")

    if st.button("Backup Sekarang"):

        if not os.path.exists("backup"):
            os.makedirs("backup")

        backup_name = (
            f"backup_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )

        shutil.copy(
            "usaha.db",
            f"backup/{backup_name}"
        )

        st.success("Backup berhasil dibuat")

