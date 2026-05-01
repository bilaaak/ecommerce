import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


st.set_page_config(
    page_title="E-Commerce Public Dataset Dashboard",
    page_icon="🛒",
    layout="wide"
)

sns.set(style="darkgrid")


# =========================
# Load Data
# =========================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "all_data.csv")

    df = pd.read_csv(file_path)

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )

    df = df.dropna(subset=["order_purchase_timestamp"])
    df = df.sort_values("order_purchase_timestamp").reset_index(drop=True)

    # Jika kolom revenue belum ada, gunakan price sebagai revenue produk
    if "revenue" not in df.columns:
        df["revenue"] = df["price"]

    return df


# =========================
# Helper Function
# =========================
def create_monthly_revenue_df(df):
    df = df.copy()

    # Menghindari duplikasi item jika ada data ganda
    item_df = df.drop_duplicates(
        subset=["order_id", "order_item_id", "product_id"]
    ).copy()

    item_df["month"] = (
        item_df["order_purchase_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_revenue_df = (
        item_df
        .groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            order_count=("order_id", "nunique")
        )
        .sort_values("month")
    )

    return monthly_revenue_df


def create_category_revenue_df(df):
    df = df.copy()

    # Menghindari duplikasi item
    item_df = df.drop_duplicates(
        subset=["order_id", "order_item_id", "product_id"]
    ).copy()

    category_revenue_df = (
        item_df
        .dropna(subset=["product_category_name_english"])
        .groupby("product_category_name_english", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            item_count=("product_id", "count")
        )
        .sort_values("revenue", ascending=False)
    )

    return category_revenue_df


# =========================
# Main Data
# =========================
all_df = load_data()


# =========================
# Sidebar Filter
# =========================
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.header("Filter Data")

    date_range = st.date_input(
        label="Rentang Waktu",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

if len(date_range) != 2:
    st.warning("Silakan pilih tanggal awal dan tanggal akhir.")
    st.stop()

start_date, end_date = date_range

start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= start_datetime) &
    (all_df["order_purchase_timestamp"] < end_datetime)
].copy()


# =========================
# Prepare Data
# =========================
monthly_revenue_df = create_monthly_revenue_df(main_df)
category_revenue_df = create_category_revenue_df(main_df)


# =========================
# Dashboard Title
# =========================
st.title("E-Commerce Public Dataset Dashboard 🛒")

st.write(
    """
    Dashboard ini menampilkan hasil analisis transaksi e-commerce Olist berdasarkan
    dua pertanyaan bisnis utama, yaitu kategori produk dengan total revenue tertinggi
    dan tren revenue bulanan.
    """
)


# =========================
# Ringkasan Data
# =========================
st.subheader("Ringkasan Data")

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df["order_id"].nunique()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df.drop_duplicates(
        subset=["order_id", "order_item_id", "product_id"]
    )["revenue"].sum()
    st.metric("Total Revenue Produk", value=f"R$ {total_revenue:,.2f}")

with col3:
    total_products = main_df["product_id"].nunique()
    st.metric("Total Products", value=f"{total_products:,}")


# =========================
# Pertanyaan 1
# =========================
st.subheader("Pertanyaan 1: Kategori Produk dengan Revenue Tertinggi")

top10_category = category_revenue_df.head(10)

if top10_category.empty:
    st.info("Tidak ada data kategori produk pada rentang tanggal yang dipilih.")
else:
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ["#90CAF9"] + ["#D3D3D3"] * (len(top10_category) - 1)

    sns.barplot(
        x="revenue",
        y="product_category_name_english",
        data=top10_category,
        palette=colors,
        ax=ax
    )

    ax.set_title("Top 10 Kategori Produk dengan Revenue Tertinggi")
    ax.set_xlabel("Total Revenue Produk")
    ax.set_ylabel("Kategori Produk")

    st.pyplot(fig)

    top5_categories = category_revenue_df.head(5)["product_category_name_english"].tolist()
    top5_text = ", ".join([f"**{category}**" for category in top5_categories])

    st.write(
        f"""
        **Insight:** Kategori produk dengan total revenue tertinggi adalah {top5_text}.
        Revenue kategori dihitung menggunakan kolom `revenue` yang berasal dari harga
        item produk, sehingga analisis ini sesuai untuk melihat kontribusi pendapatan
        pada level kategori produk.
        """
    )


# =========================
# Pertanyaan 2
# =========================
st.subheader("Pertanyaan 2: Tren Revenue Bulanan")

if monthly_revenue_df.empty:
    st.info("Tidak ada data revenue bulanan pada rentang tanggal yang dipilih.")
else:
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        monthly_revenue_df["month"],
        monthly_revenue_df["revenue"],
        marker="o",
        linewidth=2
    )

    ax.set_title("Tren Revenue Bulanan pada Transaksi E-Commerce")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Revenue Produk")
    ax.tick_params(axis="x", rotation=45)

    st.pyplot(fig)

    peak_row = monthly_revenue_df.loc[monthly_revenue_df["revenue"].idxmax()]
    peak_month = peak_row["month"].strftime("%Y-%m")
    peak_revenue = peak_row["revenue"]

    st.write(
        f"""
        **Insight:** Revenue bulanan menunjukkan perubahan pendapatan produk dari waktu
        ke waktu. Revenue mencapai nilai tertinggi pada **{peak_month}** dengan total
        revenue sekitar **R$ {peak_revenue:,.2f}**. Revenue pada bulan tertentu dapat
        terlihat sangat rendah apabila jumlah order pada periode tersebut sedikit atau
        cakupan datanya tidak lengkap, sehingga tidak dapat langsung disimpulkan sebagai
        penurunan performa bisnis.
        """
    )


st.caption("Copyright © Dicoding 2025")