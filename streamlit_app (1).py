# Starter Project Streamlit — Sistem Manajemen Usaha

## Overview

Aplikasi ini dibuat untuk membantu pemilik usaha mengelola:

* Penjualan
* Stok produk
* Pengeluaran
* Supplier
* Dashboard laporan
* Login user
* Export Excel/PDF
* Backup database

Teknologi yang digunakan:

* Python
* Streamlit
* SQLite
* Pandas
* Plotly
* SQLAlchemy

---

# Struktur Project

```plaintext
usaha_app/
│
├── app.py
├── database.py
├── requirements.txt
├── usaha.db
│
├── pages/
│   ├── dashboard.py
│   ├── penjualan.py
│   ├── produk.py
│   ├── pengeluaran.py
│   ├── supplier.py
│   ├── laporan.py
│   └── settings.py
│
├── assets/
│   └── logo.png
│
├── exports/
│
└── backup/
```

---

# Install Library

```bash
pip install streamlit pandas plotly sqlalchemy openpyxl
```

---

# requirements.txt

```txt
streamlit
pandas
plotly
sqlalchemy
openpyxl
```

---

# database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///usaha.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

---

# app.py

```python
import streamlit as st

st.set_page_config(
    page_title="Manajemen Usaha",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sistem Manajemen Usaha")

st.markdown("""
Selamat datang di aplikasi manajemen usaha.
Gunakan menu di sidebar untuk mengelola bisnis.
""")
```

---

# Login System Sederhana

## Tambahkan di app.py

```python
USER = "admin"
PASS = "12345"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == USER and password == PASS:
            st.session_state.login = True
            st.success("Login berhasil")
            st.rerun()

        else:
            st.error("Username atau password salah")

    st.stop()
```

---

# Dashboard

## pages/dashboard.py

```python
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

conn = sqlite3.connect("usaha.db")

st.title("📈 Dashboard")

penjualan = pd.read_sql(
    "SELECT * FROM penjualan",
    conn
)

pengeluaran = pd.read_sql(
    "SELECT * FROM pengeluaran",
    conn
)

produk = pd.read_sql(
    "SELECT * FROM produk",
    conn
)

penjualan_total = penjualan["total"].sum()
pengeluaran_total = pengeluaran["nominal"].sum()
profit = penjualan_total - pengeluaran_total

col1, col2, col3 = st.columns(3)

col1.metric("Penjualan", f"Rp {penjualan_total:,}")
col2.metric("Pengeluaran", f"Rp {pengeluaran_total:,}")
col3.metric("Profit", f"Rp {profit:,}")

st.divider()

st.subheader("Grafik Penjualan")

if not penjualan.empty:

    chart = penjualan.groupby("tanggal")["total"].sum().reset_index()

    fig = px.line(
        chart,
        x="tanggal",
        y="total"
    )

    st.plotly_chart(fig, use_container_width=True)
```

---

# Produk & Stok

## pages/produk.py

```python
import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

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

conn.commit()

st.title("📦 Produk & Stok")

with st.form("produk"):

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

    submit = st.form_submit_button("Tambah")

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

        st.success("Produk berhasil ditambahkan")

produk_df = pd.read_sql(
    "SELECT * FROM produk",
    conn
)

st.dataframe(
    produk_df,
    use_container_width=True
)
```

---

# Penjualan

## pages/penjualan.py

```python
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS penjualan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    produk TEXT,
    jumlah INTEGER,
    total INTEGER
)
""")

conn.commit()

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
        min_value=1
    )

    selected = produk_df[
        produk_df["nama"] == produk
    ].iloc[0]

    total = selected["harga_jual"] * jumlah

    st.info(f"Total = Rp {total:,}")

    if st.button("Simpan Penjualan"):

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

        stok_baru = selected["stok"] - jumlah

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

        st.success("Penjualan berhasil")
```

---

# Pengeluaran

## pages/pengeluaran.py

```python
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect("usaha.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pengeluaran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    nama TEXT,
    nominal INTEGER
)
""")

conn.commit()

st.title("💸 Pengeluaran")

with st.form("pengeluaran"):

    nama = st.text_input("Nama Pengeluaran")

    nominal = st.number_input(
        "Nominal",
        min_value=0
    )

    submit = st.form_submit_button("Simpan")

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

        st.success("Pengeluaran berhasil disimpan")

pengeluaran_df = pd.read_sql(
    "SELECT * FROM pengeluaran",
    conn
)

st.dataframe(
    pengeluaran_df,
    use_container_width=True
)
```

---

# Export Excel

## Tambahkan di laporan.py

```python
import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect("usaha.db")

penjualan = pd.read_sql(
    "SELECT * FROM penjualan",
    conn
)

st.title("📄 Export Laporan")

excel = "laporan_penjualan.xlsx"

penjualan.to_excel(
    excel,
    index=False
)

with open(excel, "rb") as file:

    st.download_button(
        label="Download Excel",
        data=file,
        file_name=excel
    )
```

---

# Backup Database

```python
import shutil
from datetime import datetime

backup_name = f"backup_{datetime.now().strftime('%Y%m%d')}.db"

shutil.copy(
    "usaha.db",
    f"backup/{backup_name}"
)
```

---

# Dark Mode Tips

Gunakan file:

```plaintext
.streamlit/config.toml
```

Isi:

```toml
[theme]
base="dark"
primaryColor="#4CAF50"
backgroundColor="#0E1117"
secondaryBackgroundColor="#262730"
textColor="#FAFAFA"
```

---

# Cara Menjalankan

```bash
streamlit run app.py
```

---

# Fitur Upgrade Selanjutnya

## Level Menengah

* Upload foto produk
* Search produk
* Filter tanggal
* Supplier management
* QR code produk
* Laporan PDF
* Multi-user login

---

## Level Profesional

* Hosting online
* PostgreSQL
* Cloud backup
* Scan barcode
* AI prediksi penjualan
* Sistem hutang/piutang
* Integrasi WhatsApp
* Notifikasi stok menipis

---

# UI/UX yang Disarankan

Gunakan:

* Sidebar kiri
* Font besar
* Card statistik
* Grafik sederhana
* Warna soft

Hindari:

* terlalu banyak animasi
* terlalu banyak warna
* menu kecil
* layout penuh tulisan

---

# Saran Pengembangan

## Tahap 1

Fokus:

* produk
* penjualan
* pengeluaran
* laporan

---

## Tahap 2

Tambahkan:

* login
* export excel
* backup
* grafik

---

## Tahap 3

Upgrade:

* cloud hosting
* multi-user
* database PostgreSQL
* mobile responsive

---

# Kesimpulan

Arsitektur terbaik untuk jangka panjang:

```plaintext
Streamlit
    ↓
Python
    ↓
SQLite
    ↓
Export Excel/PDF
```

Lalu nanti bisa diupgrade menjadi:

```plaintext
Streamlit
    ↓
FastAPI / Backend API
    ↓
PostgreSQL
    ↓
Cloud Server
```

Tanpa perlu membuat ulang seluruh aplikasi.
