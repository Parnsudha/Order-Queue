import streamlit as st
import pandas as pd
import os
from streamlit_folium import st_folium
import folium
from datetime import datetime, time, date

import json
import streamlit as st
from google.oauth2.service_account import Credentials

# 🔐 Load credentials from Streamlit Cloud Secrets
credentials_dict = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(credentials_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)

import gspread

# Authorize gspread with credentials
gc = gspread.authorize(credentials)

# Open your Google Sheet (replace with your sheet ID or name)
# If using sheet name:
spreadsheet = gc.open("ParnSudha Orders")  # Must match exactly

# Use the first worksheet (or change to specific one)
sheet = spreadsheet.worksheet("Orders")


#CSV_FILE = "orders.csv"
#st.write("📁 Writing to:", os.path.abspath(CSV_FILE))

# Ensure CSV file exists

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
    map_data = st_folium(m, width=360, height=300)
    submitted = st.form_submit_button("Submit Order")


# --- Save the Order ---
if submitted:
    if name and qty:
        lat = map_data["last_clicked"]["lat"] if map_data.get("last_clicked") else ""
        lon = map_data["last_clicked"]["lng"] if map_data.get("last_clicked") else ""

        new_order = pd.DataFrame([[
            name, qty, str(delivery_date), str(delivery_time),
            lat, lon, "No", "No", address
        ]], columns=[
            "Customer Name", "Quantity", "Delivery Date", "Delivery Time",
            "Latitude", "Longitude", "Delivered", "Zoho", "Memo"
        ])


        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        df = pd.concat([df, new_order], ignore_index=True)
        values = [df.columns.values.tolist()] + df.astype(str).values.tolist()
        sheet.update(values)

	# 🔁 Reset form inputs manually

        st.success("✅ Thank you! Your order has been placed.")
        st.write("📄 Your submitted order:", new_order)    
    else:
        st.error("❌ Please fill in your name and quantity.")

