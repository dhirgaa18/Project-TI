import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="BananaCrunch UMKM",
    page_icon="🍌",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>

.stApp{
    background: linear-gradient(
    135deg,
    #f6f1e9,
    #ede0d4,
    #d6ccc2
    );
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#5C4033;
}

/* Judul */
h1,h2,h3{
    color:#5C4033;
    font-family:Trebuchet MS;
}

/* Button */
.stButton>button{
    background:#F4D35E;
    color:#5C4033;
    border:none;
    border-radius:12px;
    padding:10px 20px;
    font-weight:bold;
}

.stButton>button:hover{
    background:#6B8E23;
    color:white;
}

/* Metric */
[data-testid="metric-container"]{
    background:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect(
    "banana_crunch.db",
    check_same_thread=False
)

c = conn.cursor()

# =====================================================
# TABLES
# =====================================================
c.execute("""
CREATE TABLE IF NOT EXISTS bahan(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    stok REAL,
    satuan TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS produk(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    jenis TEXT,
    rasa TEXT,
    stok INTEGER,
    harga INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS produksi(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    jenis TEXT,
    rasa TEXT,
    jumlah REAL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS penjualan(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    produk TEXT,
    qty INTEGER,
    total INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS pengeluaran(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    nama TEXT,
    nominal INTEGER
)
""")

conn.commit()

# =====================================================
# SEED DATA
# =====================================================
cek = pd.read_sql(
    "SELECT COUNT(*) as jumlah FROM bahan",
    conn
)

if cek["jumlah"][0] == 0:

    data_awal = [
        ("Pisang Raja", 50, "kg"),
        ("Pisang Kepok", 50, "kg"),
        ("Minyak Goreng", 20, "liter"),
        ("Gula", 10, "kg"),
        ("Garam", 10, "kg"),
        ("Gas LPG", 10, "tabung")
    ]

    c.executemany("""
    INSERT INTO bahan(nama, stok, satuan)
    VALUES(?,?,?)
    """, data_awal)

    conn.commit()

# =====================================================
# LOGIN
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Login Admin")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username == "admin" and password == "12345":

            st.session_state.login = True
            st.rerun()

        else:
            st.error("Username / Password salah")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("🍌 BananaCrunch")

menu = st.sidebar.radio(
    "📋 Menu",
    [
        "🏠 Dashboard",
        "🧪 Bahan Baku",
        "🏭 Produksi",
        "📦 Produk Jadi",
        "🛒 Penjualan",
        "💸 Pengeluaran",
        "📊 Laporan",
        "👤 Profil UMKM"
    ]
)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "🏠 Dashboard":

    st.title("🍌 BananaCrunch Dashboard")

    bahan = pd.read_sql(
        "SELECT * FROM bahan",
        conn
    )

    produk = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    penjualan = pd.read_sql(
        "SELECT * FROM penjualan",
        conn
    )

    pengeluaran = pd.read_sql(
        "SELECT * FROM pengeluaran",
        conn
    )

    # OMZET
    if not penjualan.empty:

        penjualan["total"] = pd.to_numeric(
            penjualan["total"],
            errors="coerce"
        ).fillna(0)

        omzet = penjualan["total"].sum()

    else:
        omzet = 0

    # PENGELUARAN
    if not pengeluaran.empty:

        pengeluaran["nominal"] = pd.to_numeric(
            pengeluaran["nominal"],
            errors="coerce"
        ).fillna(0)

        total_pengeluaran = pengeluaran["nominal"].sum()

    else:
        total_pengeluaran = 0

    laba = omzet - total_pengeluaran

    # METRIC
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Omzet",
        f"Rp {omzet:,.0f}"
    )

    col2.metric(
        "📦 Produk",
        len(produk)
    )

    col3.metric(
        "🧪 Bahan",
        len(bahan)
    )

    col4.metric(
        "💵 Laba",
        f"Rp {laba:,.0f}"
    )

    st.divider()

    # GRAFIK
    st.subheader("📈 Grafik Penjualan")

    if not penjualan.empty:

        chart = penjualan.groupby(
            "tanggal"
        )["total"].sum()

        st.line_chart(chart)

    # STOK MINIM
    stok_minim = bahan[
        bahan["stok"] < 5
    ]

    if not stok_minim.empty:

        st.warning(
            "⚠ Ada bahan baku hampir habis!"
        )

        st.dataframe(
            stok_minim,
            use_container_width=True
        )

# =====================================================
# BAHAN BAKU
# =====================================================
elif menu == "🧪 Bahan Baku":

    st.title("🧪 Data Bahan Baku")

    nama = st.text_input(
        "Nama Bahan"
    )

    stok = st.number_input(
        "Jumlah Stok",
        min_value=0.0
    )

    satuan = st.selectbox(
        "Satuan",
        ["kg", "liter", "pcs", "tabung"]
    )

    if st.button("Tambah Bahan"):

        c.execute("""
        INSERT INTO bahan(
            nama,
            stok,
            satuan
        )
        VALUES(?,?,?)
        """, (
            nama,
            stok,
            satuan
        ))

        conn.commit()

        st.success(
            "✅ Bahan berhasil ditambahkan"
        )

    st.divider()

    data = pd.read_sql(
        "SELECT * FROM bahan",
        conn
    )

    st.dataframe(
        data,
        use_container_width=True
    )

# =====================================================
# PRODUKSI
# =====================================================
elif menu == "🏭 Produksi":

    st.title("🏭 Produksi Keripik Pisang")

    bahan = pd.read_sql(
        "SELECT * FROM bahan",
        conn
    )

    jenis = st.selectbox(
        "Jenis Pisang",
        ["Pisang Raja", "Pisang Kepok"]
    )

    rasa = st.selectbox(
        "Rasa",
        ["Manis", "Asin"]
    )

    jumlah = st.number_input(
        "Jumlah Pisang (kg)",
        min_value=1.0
    )

    if st.button("Produksi Sekarang"):

        kebutuhan = [
            (jenis, jumlah),
            ("Minyak Goreng", jumlah * 0.2)
        ]

        if rasa == "Manis":

            kebutuhan.append(
                ("Gula", jumlah * 0.05)
            )

        else:

            kebutuhan.append(
                ("Garam", jumlah * 0.03)
            )

        cukup = True

        for nama_bahan, kebutuhan_bahan in kebutuhan:

            row = bahan[
                bahan["nama"] == nama_bahan
            ]

            if row.empty:

                st.error(
                    f"{nama_bahan} tidak tersedia"
                )

                cukup = False
                break

            if row.iloc[0]["stok"] < kebutuhan_bahan:

                st.error(
                    f"Stok {nama_bahan} kurang"
                )

                cukup = False
                break

        # PRODUKSI BERHASIL
        if cukup:

            # KURANGI STOK BAHAN
            for nama_bahan, kebutuhan_bahan in kebutuhan:

                c.execute("""
                UPDATE bahan
                SET stok = stok - ?
                WHERE nama = ?
                """, (
                    kebutuhan_bahan,
                    nama_bahan
                ))

            # SIMPAN PRODUKSI
            c.execute("""
            INSERT INTO produksi(
                tanggal,
                jenis,
                rasa,
                jumlah
            )
            VALUES(?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                jenis,
                rasa,
                jumlah
            ))

            # NAMA PRODUK
            nama_produk = (
                f"Keripik {jenis} {rasa}"
            )

            # HASIL PRODUK
            hasil_produk = int(
                jumlah * 10
            )

            # CEK PRODUK
            cek_produk = pd.read_sql(
                f"""
                SELECT * FROM produk
                WHERE nama = '{nama_produk}'
                """,
                conn
            )

            if cek_produk.empty:

                harga = 15000

                if jenis == "Pisang Kepok":
                    harga = 12000

                c.execute("""
                INSERT INTO produk(
                    nama,
                    jenis,
                    rasa,
                    stok,
                    harga
                )
                VALUES(?,?,?,?,?)
                """, (
                    nama_produk,
                    jenis,
                    rasa,
                    hasil_produk,
                    harga
                ))

            else:

                c.execute("""
                UPDATE produk
                SET stok = stok + ?
                WHERE nama = ?
                """, (
                    hasil_produk,
                    nama_produk
                ))

            conn.commit()

            st.success(
                "✅ Produksi berhasil!"
            )

# =====================================================
# PRODUK JADI
# =====================================================
elif menu == "📦 Produk Jadi":

    st.title("📦 Produk Jadi")

    produk = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    st.dataframe(
        produk,
        use_container_width=True
    )

# =====================================================
# PENJUALAN
# =====================================================
elif menu == "🛒 Penjualan":

    st.title("🛒 Penjualan")

    produk = pd.read_sql(
        "SELECT * FROM produk",
        conn
    )

    if produk.empty:

        st.warning(
            "Belum ada produk"
        )

    else:

        pilih = st.selectbox(
            "Pilih Produk",
            produk["nama"]
        )

        qty = st.number_input(
            "Jumlah",
            min_value=1
        )

        row = produk[
            produk["nama"] == pilih
        ].iloc[0]

        total = qty * row["harga"]

        st.info(
            f"💰 Total : Rp {total:,.0f}"
        )

        if st.button("Jual Produk"):

            if qty > row["stok"]:

                st.error(
                    "Stok tidak cukup"
                )

            else:

                # INSERT PENJUALAN
                c.execute("""
                INSERT INTO penjualan(
                    tanggal,
                    produk,
                    qty,
                    total
                )
                VALUES(?,?,?,?)
                """, (
                    datetime.now().strftime("%Y-%m-%d"),
                    pilih,
                    qty,
                    total
                ))

                # UPDATE STOK
                c.execute("""
                UPDATE produk
                SET stok = stok - ?
                WHERE nama = ?
                """, (
                    qty,
                    pilih
                ))

                conn.commit()

                st.success(
                    "✅ Penjualan berhasil"
                )

# =====================================================
# PENGELUARAN
# =====================================================
elif menu == "💸 Pengeluaran":

    st.title("💸 Pengeluaran")

    nama = st.text_input(
        "Nama Pengeluaran"
    )

    nominal = st.number_input(
        "Nominal",
        min_value=0
    )

    if st.button("Simpan Pengeluaran"):

        c.execute("""
        INSERT INTO pengeluaran(
            tanggal,
            nama,
            nominal
        )
        VALUES(?,?,?)
        """, (
            datetime.now().strftime("%Y-%m-%d"),
            nama,
            nominal
        ))

        conn.commit()

        st.success(
            "✅ Pengeluaran disimpan"
        )

    data = pd.read_sql(
        "SELECT * FROM pengeluaran",
        conn
    )

    st.dataframe(
        data,
        use_container_width=True
    )

# =====================================================
# LAPORAN
# =====================================================
elif menu == "📊 Laporan":

    st.title("📊 Laporan Keuangan")

    penjualan = pd.read_sql(
        "SELECT * FROM penjualan",
        conn
    )

    pengeluaran = pd.read_sql(
        "SELECT * FROM pengeluaran",
        conn
    )

    # OMZET
    if not penjualan.empty:

        penjualan["total"] = pd.to_numeric(
            penjualan["total"],
            errors="coerce"
        ).fillna(0)

        omzet = penjualan["total"].sum()

    else:
        omzet = 0

    # PENGELUARAN
    if not pengeluaran.empty:

        pengeluaran["nominal"] = pd.to_numeric(
            pengeluaran["nominal"],
            errors="coerce"
        ).fillna(0)

        keluar = pengeluaran["nominal"].sum()

    else:
        keluar = 0

    laba = omzet - keluar

    st.metric(
        "💰 Omzet",
        f"Rp {omzet:,.0f}"
    )

    st.metric(
        "💸 Pengeluaran",
        f"Rp {keluar:,.0f}"
    )

    st.metric(
        "💵 Laba Bersih",
        f"Rp {laba:,.0f}"
    )

# =====================================================
# PROFIL UMKM
# =====================================================
elif menu == "👤 Profil UMKM":

    st.title("👤 Profil UMKM")

    st.markdown("""
    ## 🍌 BananaCrunch

    UMKM keripik pisang lokal berbasis digital.

    ### Produk:
    - Keripik Pisang Raja
    - Keripik Pisang Kepok
    - Rasa Manis
    - Rasa Asin

    ### Keunggulan:
    ✅ Higienis  
    ✅ Renyah  
    ✅ Bahan berkualitas  
    ✅ Sistem produksi digital  

    ---
    Dibuat menggunakan Streamlit ❤️
    """)
