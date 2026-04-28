import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

@st.cache_data
def load_data():
    main_df = pd.read_csv(Path(__file__).parent / "main_data.csv")
    rfm_df = pd.read_csv(Path(__file__).parent / "rfm_data.csv")
    main_df["order_purchase_timestamp"] = pd.to_datetime(main_df["order_purchase_timestamp"])
    main_df["order_month"] = main_df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return main_df, rfm_df

main_df, rfm_df = load_data()

st.title("🛒 E-Commerce Public Dataset Dashboard")
st.caption("Dashboard analisis revenue, tren penjualan, dan segmentasi pelanggan berbasis RFM.")

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"{main_df['revenue'].sum():,.2f}")
col2.metric("Jumlah Order", f"{main_df['order_id'].nunique():,}")
col3.metric("Jumlah Customer", f"{main_df['customer_id'].nunique():,}")

st.subheader("Top 10 Kategori Produk Berdasarkan Revenue")
category_revenue = (
    main_df.groupby("product_category_name_english")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(12, 5))
category_revenue.plot(kind="bar", ax=ax)
ax.set_title("Top 10 Kategori Produk dengan Revenue Tertinggi")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Total Revenue")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

st.subheader("Tren Revenue Bulanan")
monthly_revenue = main_df.groupby("order_month")["revenue"].sum().reset_index()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_revenue["order_month"], monthly_revenue["revenue"], marker="o")
ax.set_title("Tren Revenue Bulanan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Revenue")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

st.subheader("Distribusi Segmentasi Pelanggan")
segment_counts = rfm_df["customer_segment"].value_counts().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
segment_counts.plot(kind="bar", ax=ax)
ax.set_title("Distribusi Segmentasi Pelanggan")
ax.set_xlabel("Segment")
ax.set_ylabel("Jumlah Customer")
ax.tick_params(axis="x", rotation=45)

for i, value in enumerate(segment_counts):
    ax.text(i, value, str(value), ha="center", va="bottom")

st.pyplot(fig)

st.subheader("Insight")
st.write("""
- Kategori dengan revenue tertinggi adalah **health_beauty**, diikuti oleh **watches_gifts** dan **bed_bath_table**.
- Revenue mengalami peningkatan signifikan sepanjang tahun 2017 hingga awal 2018.
- Mayoritas pelanggan berada pada segment **Regular Customers**.
- Segmentasi RFM membantu perusahaan menentukan strategi promosi yang lebih tepat.
""")

with st.expander("Lihat Data Utama"):
    st.dataframe(main_df)

with st.expander("Lihat Data RFM"):
    st.dataframe(rfm_df)