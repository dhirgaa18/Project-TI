import streamlit as st
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

# =========================
# BACKUP DATABASE
# =========================
elif menu == "Backup Database":

    st.title("💾 Backup Database")

    if st.button("Backup Sekarang"):

        if not os.path.exists("backup"):
            os.makedirs("backup")

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        shutil.copy(
            "usaha.db",
            f"backup/{backup_name}"
        )

        st.success("Backup berhasil dibuat")
