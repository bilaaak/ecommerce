import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="dark")

# Helper function
def create_monthly_revenue_df(df):
    monthly_revenue_df = df.resample(rule="M", on="order_purchase_timestamp").agg({
        "payment_value": "sum",
        "order_id": "nunique"
    })

    monthly_revenue_df = monthly_revenue_df.reset_index()
    monthly_revenue_df.rename(columns={
        "order_purchase_timestamp": "month",
        "payment_value": "revenue",
        "order_id": "order_count"
    }, inplace=True)

    return monthly_revenue_df


def create_category_revenue_df(df):
    category_revenue_df = (
        df.drop_duplicates(subset=["order_id", "order_item_id", "product_id"])
        .groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    category_revenue_df.rename(columns={
        "price": "revenue"
    }, inplace=True)

    return category_revenue_df

# Load data
all_df = pd.read_csv("all_data.csv")

# Convert datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

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
st.header("E-Commerce Public Dataset Dashboard :shopping_trolley:")

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


# Monthly revenue
st.subheader("Tren Revenue Bulanan")

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    monthly_revenue_df["month"],
    monthly_revenue_df["revenue"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)

ax.set_title("Tren Revenue Bulanan pada Transaksi E-Commerce", fontsize=20)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Revenue")
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y")

st.pyplot(fig)


# Category revenue
st.subheader("Top 10 Kategori Produk Berdasarkan Revenue")

fig, ax = plt.subplots(figsize=(16, 8))

colors = ["#90CAF9"] + ["#D3D3D3"] * 9

sns.barplot(
    x="revenue",
    y="product_category_name_english",
    data=category_revenue_df.head(10),
    palette=colors,
    ax=ax
)

ax.set_title("Top 10 Kategori Produk dengan Revenue Tertinggi", fontsize=20)
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Kategori Produk")

st.pyplot(fig)

st.caption("Copyright © Dicoding 2025")