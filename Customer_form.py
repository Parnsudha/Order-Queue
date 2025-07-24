import streamlit as st
import pandas as pd
import os
from streamlit_folium import st_folium
import folium
from datetime import datetime, time, date

CSV_FILE = "orders.csv"

# Ensure CSV file exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=[
        "Customer Name", "Quantity", "Delivery Date", "Delivery Time", "Delivered", "Zoho", "Memo",
        "Latitude", "Longitude"
    ])
    df.to_csv(CSV_FILE, index=False)

st.subheader("📥 Place Your Order")

# --- Order Form ---
with st.form("customer_order_form"):
    name = st.text_input("Customer Name")
    qty = st.number_input("Quantity", min_value=20, step=5)
    delivery_date = st.date_input("Preferred Delivery Date", min_value=date.today())
    delivery_time = st.time_input("Preferred Delivery Time", value=time(16, 0))
    address = st.text_area("Delivery Address (optional)")

    st.markdown("### 📍 Click on the Map for Delivery Location")
    m = folium.Map(location=[26.9124, 75.7873], zoom_start=12)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, width=620, height=270)
    submitted = st.form_submit_button("Submit Order")


# --- Save the Order ---
if submitted:
    if name and qty:
        lat = map_data["last_clicked"]["lat"] if map_data.get("last_clicked") else ""
        lon = map_data["last_clicked"]["lng"] if map_data.get("last_clicked") else ""

        new_order = pd.DataFrame([[
            name, qty, delivery_date, delivery_time,
            lat, lon, "No", "No", address
        ]], columns=[
            "Customer Name", "Quantity", "Delivery Date", "Delivery Time",
            "Latitude", "Longitude", "Delivered", "Zoho", "Memo"
        ])

        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_order], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

	# 🔁 Reset form inputs manually

        st.success("✅ Thank you! Your order has been placed.")
        
    else:
        st.error("❌ Please fill in your name and quantity.")
