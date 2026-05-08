import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import calendar

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: #FBF8F3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3B2314 0%, #5C3320 100%);
    border-right: none;
}

[data-testid="stSidebar"] .stRadio label {
    color: #F5E6C8 !important;
    font-size: 14px;
    padding: 6px 0;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F5E6C8 !important;
}

[data-testid="stSidebar"] p {
    color: #C4A882 !important;
}

/* Headings */
h1 { color: #3B2314 !important; font-weight: 700 !important; }
h2 { color: #5C3320 !important; font-weight: 600 !important; }
h3 { color: #5C3320 !important; font-weight: 600 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #EDE0D0;
    box-shadow: 0 2px 8px rgba(59,35,20,0.06);
}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 13px;
    color: #8B6A50;
    font-weight: 500;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px;
    font-weight: 700;
    color: #3B2314;
}

/* Buttons */
.stButton > button {
    background: #E8A020;
    color: #3B2314;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.2px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 6px rgba(232,160,32,0.3);
}

.stButton > button:hover {
    background: #5C7A2A;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(92,122,42,0.35);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #E5D5C5 !important;
    background: white !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #EDE0D0;
}

/* Divider */
hr {
    border-color: #EDE0D0 !important;
}

/* Alert boxes */
.stSuccess {
    border-radius: 10px;
    background: #EEF7E8 !important;
    border-left: 4px solid #5C7A2A !important;
}

.stWarning {
    border-radius: 10px;
    background: #FFF8E8 !important;
    border-left: 4px solid #E8A020 !important;
}

.stError {
    border-radius: 10px;
    background: #FFF0F0 !important;
    border-left: 4px solid #E84040 !important;
}

/* Info box */
.stInfo {
    border-radius: 10px;
    background: #FFF4E0 !important;
    border-left: 4px solid #E8A020 !important;
}

/* Tab styling */
[data-testid="stTab"] {
    font-weight: 600;
    color: #8B6A50;
}

/* Card custom */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid #EDE0D0;
    box-shadow: 0 2px 8px rgba(59,35,20,0.06);
    margin-bottom: 12px;
}

.section-title {
    font-size: 13px;
    font-weight: 600;
    color: #8B6A50;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect("banana_crunch.db", check_same_thread=False)
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
    kategori TEXT DEFAULT 'Lainnya',
    nominal INTEGER
)
""")

conn.commit()

# Migration: tambah kolom kategori kalau belum ada (untuk database lama)
try:
    c.execute("ALTER TABLE pengeluaran ADD COLUMN kategori TEXT DEFAULT 'Lainnya'")
    conn.commit()
except Exception:
    pass  # kolom sudah ada, skip

# =====================================================
# SEED DATA
# =====================================================
cek = pd.read_sql("SELECT COUNT(*) as jumlah FROM bahan", conn)
if cek["jumlah"][0] == 0:
    data_awal = [
        ("Pisang Raja", 50, "kg"),
        ("Pisang Kepok", 50, "kg"),
        ("Minyak Goreng", 20, "liter"),
        ("Gula", 10, "kg"),
        ("Garam", 10, "kg"),
        ("Gas LPG", 10, "tabung")
    ]
    c.executemany("INSERT INTO bahan(nama, stok, satuan) VALUES(?,?,?)", data_awal)
    conn.commit()

# =====================================================
# FIX DATA LAMA: update total=0 di penjualan
# =====================================================
rows_nol = conn.execute("SELECT id, produk, qty FROM penjualan WHERE total = 0 OR total IS NULL").fetchall()
for rid, nama_prod, qty_prod in rows_nol:
    harga_fix = conn.execute("SELECT harga FROM produk WHERE nama = ?", (nama_prod,)).fetchone()
    if harga_fix:
        total_fix = int(qty_prod) * int(harga_fix[0])
        conn.execute("UPDATE penjualan SET total = ? WHERE id = ?", (total_fix, rid))
conn.commit()

# =====================================================
# LOGIN
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom: 32px;'>
            <div style='font-size: 56px;'>🍌</div>
            <h1 style='color:#3B2314; margin:8px 0 4px;'>BananaCrunch</h1>
            <p style='color:#8B6A50; font-size:15px;'>Sistem Manajemen UMKM</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input("👤 Username", placeholder="Masukkan username")
            password = st.text_input("🔒 Password", type="password", placeholder="Masukkan password")
            if st.button("🚀 Masuk ke Dashboard", use_container_width=True):
                if username == "admin" and password == "12345":
                    st.session_state.login = True
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")
        st.markdown("<br><p style='text-align:center; color:#C4A882; font-size:12px;'>© 2024 BananaCrunch UMKM</p>", unsafe_allow_html=True)
    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 24px;'>
        <div style='font-size:40px;'>🍌</div>
        <h2 style='color:#F5E6C8; margin:8px 0 2px; font-size:20px;'>BananaCrunch</h2>
        <p style='color:#C4A882; font-size:12px; margin:0;'>Manajemen UMKM Digital</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    menu = st.radio(
        "Navigasi",
        [
            "🏠 Dashboard",
            "🧪 Bahan Baku",
            "🏭 Produksi",
            "📦 Produk Jadi",
            "🛒 Penjualan",
            "💸 Pengeluaran",
            "📊 Laporan Bulanan",
            "👤 Profil UMKM"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("<p style='color:#C4A882; font-size:11px; text-align:center;'>Login sebagai Admin</p>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.login = False
        st.rerun()

# =====================================================
# HELPERS
# =====================================================
def format_rp(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

def get_bulan_list():
    bulan_names = ["Januari","Februari","Maret","April","Mei","Juni",
                   "Juli","Agustus","September","Oktober","November","Desember"]
    return bulan_names

# =====================================================
# DASHBOARD
# =====================================================
if menu == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.markdown(f"<p style='color:#8B6A50; margin-top:-12px;'>Selamat datang kembali! — {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)

    bahan    = pd.read_sql("SELECT * FROM bahan", conn)
    produk   = pd.read_sql("SELECT * FROM produk", conn)
    penjualan = pd.read_sql("SELECT * FROM penjualan", conn)
    pengeluaran = pd.read_sql("SELECT * FROM pengeluaran", conn)

    # Hitung bulan ini
    bulan_ini = datetime.now().strftime("%Y-%m")

    if not penjualan.empty:
        penjualan["total"] = pd.to_numeric(penjualan["total"], errors="coerce").fillna(0)
        omzet_total = penjualan["total"].sum()
        omzet_bulan = penjualan[penjualan["tanggal"].str.startswith(bulan_ini)]["total"].sum()
    else:
        omzet_total = omzet_bulan = 0

    if not pengeluaran.empty:
        pengeluaran["nominal"] = pd.to_numeric(pengeluaran["nominal"], errors="coerce").fillna(0)
        keluar_total = pengeluaran["nominal"].sum()
        keluar_bulan = pengeluaran[pengeluaran["tanggal"].str.startswith(bulan_ini)]["nominal"].sum()
    else:
        keluar_total = keluar_bulan = 0

    laba_total = omzet_total - keluar_total
    laba_bulan = omzet_bulan - keluar_bulan

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Omzet Bulan Ini", format_rp(omzet_bulan))
    col2.metric("💸 Pengeluaran Bulan Ini", format_rp(keluar_bulan))
    col3.metric("💵 Laba Bulan Ini", format_rp(laba_bulan))
    col4.metric("📦 Total Produk", len(produk))

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 📈 Tren Penjualan Harian")
        if not penjualan.empty:
            chart_data = penjualan.groupby("tanggal")["total"].sum().reset_index()
            chart_data = chart_data.sort_values("tanggal")
            chart_data = chart_data.set_index("tanggal")
            st.line_chart(chart_data, use_container_width=True, height=250, color="#E8A020")
        else:
            st.info("Belum ada data penjualan")

    with col_right:
        st.markdown("### 🧪 Stok Bahan Baku")
        if not bahan.empty:
            for _, row in bahan.iterrows():
                persen = min(row["stok"] / 50 * 100, 100)
                warna = "#5C7A2A" if persen > 40 else ("#E8A020" if persen > 15 else "#E84040")
                st.markdown(f"""
                <div style='margin-bottom:12px;'>
                    <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'>
                        <span style='color:#3B2314; font-weight:500;'>{row['nama']}</span>
                        <span style='color:#8B6A50;'>{row['stok']} {row['satuan']}</span>
                    </div>
                    <div style='background:#F0E8DC; border-radius:999px; height:6px;'>
                        <div style='background:{warna}; width:{persen}%; border-radius:999px; height:6px;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # Stok minim
    stok_minim = bahan[bahan["stok"] < 5]
    if not stok_minim.empty:
        st.warning(f"⚠️ **{len(stok_minim)} bahan** hampir habis! Segera lakukan restok.")
        st.dataframe(stok_minim[["nama", "stok", "satuan"]], use_container_width=True, hide_index=True)

    # Penjualan per produk
    if not penjualan.empty:
        st.markdown("### 🏆 Penjualan per Produk")
        per_produk = penjualan.groupby("produk")["total"].sum().reset_index()
        per_produk.columns = ["Produk", "Total Penjualan"]
        per_produk["Total Penjualan"] = per_produk["Total Penjualan"].apply(format_rp)
        per_produk = per_produk.sort_values("Total Penjualan", ascending=False)
        st.dataframe(per_produk, use_container_width=True, hide_index=True)

# =====================================================
# BAHAN BAKU
# =====================================================
elif menu == "🧪 Bahan Baku":
    st.markdown("## 🧪 Bahan Baku")

    tab1, tab2 = st.tabs(["📋 Data Stok", "➕ Tambah / Update"])

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            nama_bahan = st.text_input("Nama Bahan", placeholder="cth: Pisang Ambon")
            stok_bahan = st.number_input("Jumlah Stok", min_value=0.0, step=0.5)
        with col2:
            satuan = st.selectbox("Satuan", ["kg", "liter", "pcs", "tabung", "gram", "ml"])
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("💾 Simpan Bahan", use_container_width=True):
                if nama_bahan.strip():
                    # Cek apakah bahan sudah ada
                    existing = pd.read_sql(f"SELECT * FROM bahan WHERE LOWER(nama) = LOWER('{nama_bahan}')", conn)
                    if not existing.empty:
                        c.execute("UPDATE bahan SET stok = stok + ? WHERE LOWER(nama) = LOWER(?)", (stok_bahan, nama_bahan))
                        conn.commit()
                        st.success(f"✅ Stok {nama_bahan} diperbarui!")
                    else:
                        c.execute("INSERT INTO bahan(nama, stok, satuan) VALUES(?,?,?)", (nama_bahan, stok_bahan, satuan))
                        conn.commit()
                        st.success(f"✅ Bahan '{nama_bahan}' berhasil ditambahkan!")
                else:
                    st.error("Nama bahan tidak boleh kosong!")

    with tab1:
        data = pd.read_sql("SELECT id, nama as 'Nama Bahan', stok as 'Stok', satuan as 'Satuan' FROM bahan", conn)
        st.dataframe(data, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🗑️ Hapus Bahan")
        col1, col2 = st.columns([2, 1])
        with col1:
            all_bahan = pd.read_sql("SELECT * FROM bahan", conn)
            if not all_bahan.empty:
                pilih_hapus = st.selectbox("Pilih bahan untuk dihapus", all_bahan["nama"])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if not all_bahan.empty and st.button("🗑️ Hapus", use_container_width=True):
                c.execute("DELETE FROM bahan WHERE nama = ?", (pilih_hapus,))
                conn.commit()
                st.success(f"Bahan '{pilih_hapus}' dihapus!")
                st.rerun()

# =====================================================
# PRODUKSI
# =====================================================
elif menu == "🏭 Produksi":
    st.markdown("## 🏭 Produksi Keripik Pisang")

    tab1, tab2 = st.tabs(["🏭 Proses Produksi", "📜 Riwayat Produksi"])

    with tab1:
        bahan = pd.read_sql("SELECT * FROM bahan", conn)

        col1, col2 = st.columns(2)
        with col1:
            jenis = st.selectbox("Jenis Pisang", ["Pisang Raja", "Pisang Kepok"])
            rasa  = st.selectbox("Rasa", ["Manis", "Asin"])
        with col2:
            jumlah = st.number_input("Jumlah Pisang (kg)", min_value=1.0, step=0.5)

        # Preview kebutuhan
        kebutuhan_list = [
            (jenis, jumlah, "kg"),
            ("Minyak Goreng", round(jumlah * 0.2, 2), "liter"),
        ]
        if rasa == "Manis":
            kebutuhan_list.append(("Gula", round(jumlah * 0.05, 2), "kg"))
        else:
            kebutuhan_list.append(("Garam", round(jumlah * 0.03, 2), "kg"))

        st.markdown("#### 🧮 Estimasi Kebutuhan Bahan")
        for nb, jml, sat in kebutuhan_list:
            row = bahan[bahan["nama"] == nb]
            tersedia = row.iloc[0]["stok"] if not row.empty else 0
            ok = tersedia >= jml
            icon = "✅" if ok else "❌"
            st.markdown(f"- {icon} **{nb}**: butuh **{jml} {sat}** | stok: {tersedia} {sat}")

        st.markdown(f"#### 🎯 Hasil Produksi: ~**{int(jumlah * 10)} bungkus**")

        if st.button("🚀 Mulai Produksi", use_container_width=False):
            kebutuhan = [(jenis, jumlah), ("Minyak Goreng", jumlah * 0.2)]
            kebutuhan.append(("Gula" if rasa == "Manis" else "Garam",
                              jumlah * 0.05 if rasa == "Manis" else jumlah * 0.03))

            cukup = True
            for nama_b, kebutuhan_b in kebutuhan:
                row = bahan[bahan["nama"] == nama_b]
                if row.empty or row.iloc[0]["stok"] < kebutuhan_b:
                    st.error(f"❌ Stok {nama_b} tidak mencukupi!")
                    cukup = False
                    break

            if cukup:
                for nama_b, kebutuhan_b in kebutuhan:
                    c.execute("UPDATE bahan SET stok = stok - ? WHERE nama = ?", (kebutuhan_b, nama_b))

                c.execute("INSERT INTO produksi(tanggal, jenis, rasa, jumlah) VALUES(?,?,?,?)",
                          (datetime.now().strftime("%Y-%m-%d"), str(jenis), str(rasa), float(jumlah)))

                nama_produk = f"Keripik {jenis} {rasa}"
                hasil_produk = int(jumlah * 10)
                harga = 15000 if jenis == "Pisang Raja" else 12000

                cek_produk = pd.read_sql(f"SELECT * FROM produk WHERE nama = '{nama_produk}'", conn)
                if cek_produk.empty:
                    c.execute("INSERT INTO produk(nama, jenis, rasa, stok, harga) VALUES(?,?,?,?,?)",
                              (nama_produk, jenis, rasa, hasil_produk, harga))
                else:
                    c.execute("UPDATE produk SET stok = stok + ? WHERE nama = ?", (hasil_produk, nama_produk))

                conn.commit()
                st.success(f"✅ Produksi berhasil! {hasil_produk} bungkus {nama_produk} siap dijual.")
                st.balloons()

    with tab2:
        riwayat = pd.read_sql("""
            SELECT tanggal as 'Tanggal', jenis as 'Jenis', rasa as 'Rasa',
                   jumlah as 'Pisang (kg)', CAST(jumlah*10 AS INT) as 'Hasil (bungkus)'
            FROM produksi ORDER BY id DESC
        """, conn)
        if riwayat.empty:
            st.info("Belum ada riwayat produksi")
        else:
            st.dataframe(riwayat, use_container_width=True, hide_index=True)

# =====================================================
# PRODUK JADI
# =====================================================
elif menu == "📦 Produk Jadi":
    st.markdown("## 📦 Produk Jadi")

    produk = pd.read_sql("SELECT * FROM produk", conn)

    if produk.empty:
        st.info("Belum ada produk. Lakukan produksi terlebih dahulu.")
    else:
        # Cards per produk
        cols = st.columns(len(produk) if len(produk) <= 3 else 3)
        for i, (_, row) in enumerate(produk.iterrows()):
            with cols[i % 3]:
                stok_warna = "#5C7A2A" if row["stok"] > 20 else ("#E8A020" if row["stok"] > 5 else "#E84040")
                st.markdown(f"""
                <div style='background:white; border-radius:16px; padding:20px;
                            border:1px solid #EDE0D0; margin-bottom:12px;
                            box-shadow:0 2px 8px rgba(59,35,20,0.06);'>
                    <div style='font-size:24px; margin-bottom:8px;'>🍌</div>
                    <p style='font-weight:700; font-size:16px; color:#3B2314; margin:0 0 4px;'>{row['nama']}</p>
                    <p style='color:#8B6A50; font-size:13px; margin:0 0 12px;'>
                        {row['jenis']} • Rasa {row['rasa']}
                    </p>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <p style='font-size:12px; color:#8B6A50; margin:0;'>Stok</p>
                            <p style='font-size:20px; font-weight:700; color:{stok_warna}; margin:0;'>{row['stok']}</p>
                            <p style='font-size:11px; color:#8B6A50; margin:0;'>bungkus</p>
                        </div>
                        <div style='text-align:right;'>
                            <p style='font-size:12px; color:#8B6A50; margin:0;'>Harga</p>
                            <p style='font-size:16px; font-weight:700; color:#E8A020; margin:0;'>Rp {row['harga']:,}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📋 Tabel Produk")

        tabel = produk[["nama", "jenis", "rasa", "stok", "harga"]].copy()
        tabel.columns = ["Nama Produk", "Jenis", "Rasa", "Stok (bungkus)", "Harga (Rp)"]
        tabel["Harga (Rp)"] = pd.to_numeric(tabel["Harga (Rp)"], errors="coerce").fillna(0).apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(tabel, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### ✏️ Update Harga Produk")
        col1, col2, col3 = st.columns(3)
        with col1:
            produk_pilih = st.selectbox("Produk", produk["nama"])
        with col2:
            harga_baru = st.number_input("Harga Baru (Rp)", min_value=1000, step=500)
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Update Harga"):
                c.execute("UPDATE produk SET harga = ? WHERE nama = ?", (harga_baru, produk_pilih))
                conn.commit()
                st.success(f"✅ Harga {produk_pilih} diperbarui!")
                st.rerun()

# =====================================================
# PENJUALAN
# =====================================================
elif menu == "🛒 Penjualan":
    st.markdown("## 🛒 Penjualan")

    tab1, tab2 = st.tabs(["🛍️ Catat Penjualan", "📋 Riwayat Penjualan"])

    with tab1:
        produk = pd.read_sql("SELECT * FROM produk", conn)

        if produk.empty:
            st.warning("⚠️ Belum ada produk. Lakukan produksi terlebih dahulu.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                pilih = st.selectbox("Pilih Produk", produk["nama"])
                row = produk[produk["nama"] == pilih].iloc[0]
            with col2:
                qty = st.number_input("Jumlah (bungkus)", min_value=1, max_value=int(row["stok"]))

            total = int(qty) * int(row["harga"])

            st.markdown(f"""
            <div style='background:#FFF4E0; border-radius:12px; padding:16px 20px;
                        border:1px solid #F5D08A; margin:16px 0;'>
                <div style='display:flex; justify-content:space-between;'>
                    <div>
                        <p style='color:#8B6A50; font-size:13px; margin:0;'>Produk</p>
                        <p style='color:#3B2314; font-weight:600; margin:0;'>{pilih}</p>
                    </div>
                    <div>
                        <p style='color:#8B6A50; font-size:13px; margin:0;'>Qty</p>
                        <p style='color:#3B2314; font-weight:600; margin:0;'>{qty} bungkus</p>
                    </div>
                    <div style='text-align:right;'>
                        <p style='color:#8B6A50; font-size:13px; margin:0;'>Total</p>
                        <p style='color:#E8A020; font-weight:700; font-size:20px; margin:0;'>{format_rp(total)}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("💳 Proses Penjualan", use_container_width=False):
                if qty > row["stok"]:
                    st.error("❌ Stok tidak mencukupi!")
                else:
                    harga_db = conn.execute(
                        "SELECT harga FROM produk WHERE nama = ?", (str(pilih),)
                    ).fetchone()
                    harga_bersih = int(harga_db[0]) if harga_db else 0
                    total_bersih = int(qty) * harga_bersih
                    c.execute("INSERT INTO penjualan(tanggal, produk, qty, total) VALUES(?,?,?,?)",
                              (datetime.now().strftime("%Y-%m-%d"), str(pilih), int(qty), total_bersih))
                    c.execute("UPDATE produk SET stok = stok - ? WHERE nama = ?", (int(qty), str(pilih)))
                    conn.commit()
                    st.success(f"✅ Penjualan {int(qty)} bungkus {pilih} berhasil! {format_rp(total_bersih)}")
                    st.balloons()

    with tab2:
        penjualan = pd.read_sql("""
            SELECT tanggal as 'Tanggal', produk as 'Produk',
                   qty as 'Qty', total as 'Total (Rp)'
            FROM penjualan ORDER BY id DESC LIMIT 100
        """, conn)

        if penjualan.empty:
            st.info("Belum ada riwayat penjualan")
        else:
            penjualan["Total (Rp)"] = pd.to_numeric(penjualan["Total (Rp)"], errors="coerce").fillna(0)
            penjualan["Total (Rp)"] = penjualan["Total (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(penjualan, use_container_width=True, hide_index=True)

# =====================================================
# PENGELUARAN
# =====================================================
elif menu == "💸 Pengeluaran":
    st.markdown("## 💸 Pengeluaran")

    tab1, tab2 = st.tabs(["➕ Tambah Pengeluaran", "📋 Riwayat"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            nama_keluar = st.text_input("Keterangan", placeholder="cth: Beli minyak goreng")
            nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
        with col2:
            kategori = st.selectbox("Kategori", [
                "Bahan Baku", "Operasional", "Gaji", "Transportasi",
                "Pemasaran", "Peralatan", "Lainnya"
            ])
            tanggal_keluar = st.date_input("Tanggal", value=datetime.now())

        if st.button("💾 Simpan Pengeluaran", use_container_width=False):
            if nama_keluar.strip() and nominal > 0:
                c.execute("INSERT INTO pengeluaran(tanggal, nama, kategori, nominal) VALUES(?,?,?,?)",
                          (tanggal_keluar.strftime("%Y-%m-%d"), str(nama_keluar), str(kategori), int(nominal)))
                conn.commit()
                st.success(f"✅ Pengeluaran {format_rp(nominal)} disimpan!")
            else:
                st.error("Keterangan dan nominal harus diisi!")

    with tab2:
        data_keluar = pd.read_sql("""
            SELECT tanggal as 'Tanggal', nama as 'Keterangan',
                   kategori as 'Kategori', nominal as 'Nominal (Rp)'
            FROM pengeluaran ORDER BY id DESC
        """, conn)

        if data_keluar.empty:
            st.info("Belum ada data pengeluaran")
        else:
            # Summary per kategori
            st.markdown("#### 📊 Ringkasan per Kategori")
            summary = pd.read_sql("""
                SELECT kategori as 'Kategori',
                       COUNT(*) as 'Jumlah Transaksi',
                       SUM(nominal) as 'Total'
                FROM pengeluaran GROUP BY kategori ORDER BY Total DESC
            """, conn)
            summary["Total"] = summary["Total"].apply(format_rp)
            st.dataframe(summary, use_container_width=True, hide_index=True)

            st.divider()
            data_keluar["Nominal (Rp)"] = pd.to_numeric(data_keluar["Nominal (Rp)"], errors="coerce").fillna(0).apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(data_keluar, use_container_width=True, hide_index=True)

# =====================================================
# LAPORAN BULANAN
# =====================================================
elif menu == "📊 Laporan Bulanan":
    st.markdown("## 📊 Laporan Bulanan")

    now = datetime.now()
    bulan_names = get_bulan_list()

    col1, col2 = st.columns(2)
    with col1:
        tahun_pilih = st.selectbox("Tahun", list(range(now.year, now.year - 4, -1)))
    with col2:
        bulan_pilih = st.selectbox("Bulan", range(1, 13),
                                    index=now.month - 1,
                                    format_func=lambda x: bulan_names[x-1])

    prefix = f"{tahun_pilih}-{bulan_pilih:02d}"
    nama_bulan = f"{bulan_names[bulan_pilih-1]} {tahun_pilih}"

    st.markdown(f"### 📅 Laporan {nama_bulan}")
    st.divider()

    penjualan_b = pd.read_sql(
        f"SELECT * FROM penjualan WHERE tanggal LIKE '{prefix}%'", conn)
    pengeluaran_b = pd.read_sql(
        f"SELECT * FROM pengeluaran WHERE tanggal LIKE '{prefix}%'", conn)
    produksi_b = pd.read_sql(
        f"SELECT * FROM produksi WHERE tanggal LIKE '{prefix}%'", conn)

    if not penjualan_b.empty:
        penjualan_b["total"] = pd.to_numeric(penjualan_b["total"], errors="coerce").fillna(0)
        omzet_b = penjualan_b["total"].sum()
        total_terjual = penjualan_b["qty"].sum()
    else:
        omzet_b = total_terjual = 0

    if not pengeluaran_b.empty:
        pengeluaran_b["nominal"] = pd.to_numeric(pengeluaran_b["nominal"], errors="coerce").fillna(0)
        keluar_b = pengeluaran_b["nominal"].sum()
    else:
        keluar_b = 0

    laba_b = omzet_b - keluar_b
    total_produksi_b = produksi_b["jumlah"].sum() if not produksi_b.empty else 0

    # KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Omzet", format_rp(omzet_b))
    c2.metric("💸 Pengeluaran", format_rp(keluar_b))
    c3.metric("💵 Laba Bersih", format_rp(laba_b),
              delta=f"{'Untung' if laba_b >= 0 else 'Rugi'}")
    c4.metric("📦 Terjual", f"{int(total_terjual)} bungkus")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 🛒 Penjualan Harian")
        if not penjualan_b.empty:
            daily = penjualan_b.groupby("tanggal")["total"].sum()
            st.bar_chart(daily, use_container_width=True, height=220, color="#E8A020")
        else:
            st.info("Tidak ada penjualan bulan ini")

    with col_r:
        st.markdown("#### 💸 Pengeluaran per Kategori")
        if not pengeluaran_b.empty and "kategori" in pengeluaran_b.columns:
            per_kat = pengeluaran_b.groupby("kategori")["nominal"].sum().reset_index()
            per_kat.columns = ["Kategori", "Total"]
            per_kat["Total"] = per_kat["Total"].apply(format_rp)
            st.dataframe(per_kat, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada pengeluaran bulan ini")

    st.divider()

    # Detail tabel
    st.markdown("#### 📋 Detail Penjualan")
    if not penjualan_b.empty:
        tampil = penjualan_b[["tanggal", "produk", "qty", "total"]].copy()
        tampil.columns = ["Tanggal", "Produk", "Qty", "Total"]
        tampil["Total"] = tampil["Total"].apply(format_rp)
        st.dataframe(tampil, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data penjualan")

    st.markdown("#### 📋 Detail Pengeluaran")
    if not pengeluaran_b.empty:
        tampil_k = pengeluaran_b[["tanggal", "nama", "kategori", "nominal"]].copy()
        tampil_k.columns = ["Tanggal", "Keterangan", "Kategori", "Nominal"]
        tampil_k["Nominal"] = tampil_k["Nominal"].apply(format_rp)
        st.dataframe(tampil_k, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data pengeluaran")

    # Ringkasan teks
    st.divider()
    st.markdown("#### 📝 Ringkasan Otomatis")
    status = "UNTUNG 📈" if laba_b >= 0 else "RUGI 📉"
    st.markdown(f"""
    <div style='background:white; border-radius:14px; padding:20px 24px;
                border:1px solid #EDE0D0; line-height:1.8;'>
        <p style='color:#3B2314; font-size:15px;'>
        Pada bulan <strong>{nama_bulan}</strong>, BananaCrunch mencatat omzet sebesar
        <strong style='color:#E8A020;'>{format_rp(omzet_b)}</strong> dengan total
        <strong>{int(total_terjual)} bungkus</strong> produk terjual.
        Total pengeluaran tercatat <strong style='color:#E84040;'>{format_rp(keluar_b)}</strong>.
        </p>
        <p style='color:#3B2314; font-size:16px; font-weight:700; margin:0;'>
        Status: {status} — Laba Bersih {format_rp(laba_b)}
        </p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# PROFIL UMKM
# =====================================================
elif menu == "👤 Profil UMKM":
    st.markdown("## 👤 Profil UMKM")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        <div style='background:white; border-radius:20px; padding:32px 24px;
                    border:1px solid #EDE0D0; text-align:center;
                    box-shadow:0 2px 8px rgba(59,35,20,0.06);'>
            <div style='font-size:64px; margin-bottom:12px;'>🍌</div>
            <h2 style='color:#3B2314; margin:0 0 4px;'>BananaCrunch</h2>
            <p style='color:#8B6A50; font-size:14px; margin:0;'>UMKM Keripik Pisang</p>
            <div style='margin:16px 0;'>
                <span style='background:#FFF4E0; color:#E8A020; padding:4px 12px;
                             border-radius:20px; font-size:12px; font-weight:600;'>
                    ✅ Aktif Beroperasi
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:white; border-radius:20px; padding:28px;
                    border:1px solid #EDE0D0; box-shadow:0 2px 8px rgba(59,35,20,0.06);'>
            <h3 style='color:#3B2314; margin:0 0 16px;'>ℹ️ Tentang Usaha</h3>
            <p style='color:#5C3320; line-height:1.7;'>
                BananaCrunch adalah UMKM keripik pisang lokal yang menggunakan sistem manajemen
                berbasis digital untuk meningkatkan efisiensi produksi dan penjualan.
            </p>
            <hr style='border-color:#EDE0D0;'>
            <h3 style='color:#3B2314; margin:12px 0;'>🍌 Produk Kami</h3>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:8px;'>
                <div style='background:#FBF8F3; border-radius:8px; padding:8px 12px; font-size:13px; color:#5C3320;'>🍌 Keripik Pisang Raja Manis</div>
                <div style='background:#FBF8F3; border-radius:8px; padding:8px 12px; font-size:13px; color:#5C3320;'>🍌 Keripik Pisang Raja Asin</div>
                <div style='background:#FBF8F3; border-radius:8px; padding:8px 12px; font-size:13px; color:#5C3320;'>🍌 Keripik Pisang Kepok Manis</div>
                <div style='background:#FBF8F3; border-radius:8px; padding:8px 12px; font-size:13px; color:#5C3320;'>🍌 Keripik Pisang Kepok Asin</div>
            </div>
            <hr style='border-color:#EDE0D0;'>
            <h3 style='color:#3B2314; margin:12px 0;'>⭐ Keunggulan</h3>
            <div style='display:flex; flex-wrap:wrap; gap:8px;'>
                <span style='background:#EEF7E8; color:#3B6A10; padding:4px 12px; border-radius:20px; font-size:13px;'>✅ Higienis</span>
                <span style='background:#EEF7E8; color:#3B6A10; padding:4px 12px; border-radius:20px; font-size:13px;'>✅ Renyah</span>
                <span style='background:#EEF7E8; color:#3B6A10; padding:4px 12px; border-radius:20px; font-size:13px;'>✅ Bahan Berkualitas</span>
                <span style='background:#EEF7E8; color:#3B6A10; padding:4px 12px; border-radius:20px; font-size:13px;'>✅ Sistem Digital</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center; color:#C4A882; font-size:13px;'>
        Dibuat dengan ❤️ menggunakan Streamlit • BananaCrunch © 2026
    </p>
    """, unsafe_allow_html=True)
