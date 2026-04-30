import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


sns.set(style="darkgrid")


# Helper function
def create_monthly_revenue_df(df):
    df = df.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce"
    )
    df = df.dropna(subset=["order_purchase_timestamp"])

    df["month"] = df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()

    monthly_revenue_df = (
        df.groupby("month")
        .agg(
            revenue=("payment_value", "sum"),
            order_count=("order_id", "nunique")
        )
        .reset_index()
        .sort_values("month")
    )

    return monthly_revenue_df


def create_category_revenue_df(df):
    category_revenue_df = (
        df.groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    category_revenue_df.rename(
        columns={
            "payment_value": "revenue"
        },
        inplace=True
    )

    return category_revenue_df


# Load data
BASE_DIR = os.path.dirname(__file__)
all_df = pd.read_csv(os.path.join(BASE_DIR, "all_data.csv"))

# Convert datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(
    all_df["order_purchase_timestamp"],
    errors="coerce"
)

all_df = all_df.dropna(subset=["order_purchase_timestamp"])

# Sort data
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.header("Filter Data")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (all_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

# Prepare dataframe
monthly_revenue_df = create_monthly_revenue_df(main_df)
category_revenue_df = create_category_revenue_df(main_df)

# Dashboard title
st.title("E-Commerce Public Dataset Dashboard 🛒")

st.write(
    """
    Dashboard ini menampilkan hasil analisis transaksi e-commerce Olist berdasarkan
    dua pertanyaan bisnis utama, yaitu tren revenue bulanan dan kategori produk
    dengan total revenue tertinggi.
    """
)

# Metrics
st.subheader("Ringkasan Data")

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df["order_id"].nunique()
    st.metric("Total Orders", value=f"{total_orders:,}")

with col2:
    total_revenue = main_df["payment_value"].sum()
    st.metric("Total Revenue", value=f"R$ {total_revenue:,.2f}")

with col3:
    total_products = main_df["product_id"].nunique()
    st.metric("Total Products", value=f"{total_products:,}")


# Question 1
st.subheader("Pertanyaan 1: Kategori Produk dengan Revenue Tertinggi")

fig, ax = plt.subplots(figsize=(12, 6))

colors = ["#90CAF9"] + ["#D3D3D3"] * 9

sns.barplot(
    x="revenue",
    y="product_category_name_english",
    data=category_revenue_df.head(10),
    palette=colors,
    ax=ax
)

ax.set_title("Top 10 Kategori Produk dengan Revenue Tertinggi")
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Kategori Produk")

st.pyplot(fig)

st.write(
    """
    **Insight:** Kategori produk dengan total revenue tertinggi adalah
    **bed_bath_table**, diikuti oleh **health_beauty**, **computers_accessories**,
    **furniture_decor**, dan **watches_gifts**. Hal ini menunjukkan bahwa kategori
    kebutuhan rumah tangga, kecantikan, aksesori komputer, dekorasi rumah, dan hadiah
    memiliki kontribusi besar terhadap pendapatan e-commerce Olist.
    """
)


# Question 2
st.subheader("Pertanyaan 2: Tren Revenue Bulanan")

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    monthly_revenue_df["month"],
    monthly_revenue_df["revenue"],
    marker="o",
    linewidth=2
)

ax.set_title("Tren Revenue Bulanan pada Transaksi E-Commerce")
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Revenue")
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)

st.write(
    """
    **Insight:** Revenue bulanan cenderung meningkat sejak awal tahun 2017 dan
    mencapai puncaknya pada November 2017. Setelah itu, revenue masih berada pada
    level yang cukup tinggi hingga pertengahan 2018, meskipun mengalami fluktuasi.
    Revenue pada September dan Oktober 2018 terlihat sangat rendah karena cakupan
    data pada periode tersebut tidak lengkap, sehingga tidak dapat langsung dianggap
    sebagai penurunan performa bisnis.
    """
)

st.caption("Copyright © Dicoding 2025")