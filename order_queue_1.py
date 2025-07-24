import streamlit as st
import streamlit as st

PASSWORD = "Parn"

#def login():
#    pwd = st.sidebar.text_input("Enter password", type="password")
#    if pwd == PASSWORD:
#        return True
#    elif pwd != "":
#        st.error("Incorrect password")
#    return False
#
#if not login():
#    st.stop()  # Stop the app here if not logged in
import pandas as pd
import os

CSV_FILE = "orders.csv"

# Initialize CSV if not exists
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Customer Name", "Quantity", "Delivery Date", "Delivery Time", "Delivered", "Zoho", "Memo", "Latitude", "Longitude"])
    df_init.to_csv(CSV_FILE, index=False)

# Load orders
df = pd.read_csv(CSV_FILE)
# Ensure all expected columns are present
required_columns = ["Customer Name", "Quantity", "Delivery Date", "Delivery Time", "Delivered", "Paid", "Memo"]
for col in required_columns:
    if col not in df.columns:
        df[col] = ""
if "Memo" not in df.columns:
    df["Memo"] = ""

st.title("📦 ParnSudha Order Queue")

# --- Add New Order ---
st.subheader("Add New Order")
with st.form("order_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input("Customer Name")
    with col2:
        qty = st.number_input("Qty", min_value=20, step=5)

    col3, col4 = st.columns(2)
    with col3:
        delivery_date = st.date_input("Delivery Date", min_value=date.today()-1)
    with col4:
        delivery_time = st.time_input("Delivery Time", value=time(16, 0))

    memo = st.text_input("Memo / Comment (optional)")

    submitted = st.form_submit_button("Add Order")

#    name = st.text_input("Customer Name")
#    qty = st.number_input("Quantity", min_value=1)
#    delivery_date = st.date_input("Delivery Date")
#    delivery_time = st.time_input("Delivery Time")
#    submitted = st.form_submit_button("Add Order")

    if submitted:
        new_order = pd.DataFrame([[name, qty, delivery_date, delivery_time, "No", "No", memo]],
                                 columns=["Customer Name", "Quantity", "Delivery Date", "Delivery Time", "Delivered", "Paid", "Memo"])
        df = pd.concat([df, new_order], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Order Added")
        st.rerun()

# --- Status and Delete update functions ---
def update_status(index, column):
    current = df.at[index, column]
    df.at[index, column] = "No" if current == "Yes" else "Yes"
    df.to_csv(CSV_FILE, index=False)
    st.rerun()

def delete_order(index):
    global df
    df = df.drop(index).reset_index(drop=True)
    df.to_csv(CSV_FILE, index=False)
    st.rerun()

# --- Filter Orders ---
st.subheader("Filter Orders By:")

filter_option = st.selectbox("", [
    "Pending to Deliver",
    "All Orders",
    "Delivered but Zoho Pending",
    "Completed Orders"
], index=0)  # default = "Pending to Deliver"

# Filter logic
if filter_option == "All Orders":
    filtered_df = df
elif filter_option == "Pending to Deliver":
    filtered_df = df[df['Delivered'] != "Yes"]
elif filter_option == "Delivered but Zoho Pending":
    filtered_df = df[(df['Delivered'] == "Yes") & (df['Zoho'] != "Yes")]
elif filter_option == "Completed Orders":
    filtered_df = df[(df['Delivered'] == "Yes") & (df['Zoho'] == "Yes")]
else:
    filtered_df = df

# --- Show Orders ---
st.subheader(f"{filter_option}")

if not filtered_df.empty:
    for i, row in filtered_df.iterrows():
        order_line = (
            f"**{row['Customer Name']}** - Qty: {row['Quantity']} | Date: {row['Delivery Date']} {row['Delivery Time']} "
            f"| Delivered: {row['Delivered']} | Zoho: {row['Zoho']}"
        )
        if 'Memo' in row and pd.notna(row['Memo']) and row['Memo'].strip() != "":
            order_line += f" | 📝 {row['Memo']}"

        st.write(order_line)

        col1, col2, col3 = st.columns(3)
        with col1:
            label = "Mark Delivered ✅" if row['Delivered'] != "Yes" else "Undo Delivered ❌"
            if st.button(label, key=f"deliv_{i}"):
                update_status(i, "Delivered")

        with col2:
            label = "Mark Zoho 💰" if row['Zoho'] != "Yes" else "Undo Zoho ❌"
            if st.button(label, key=f"Zoho_{i}"):
                update_status(i, "Zoho")

        with col3:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                delete_order(i)

        st.divider()
else:
    st.info("No orders found for this filter.")
# Convert to CSV and add to sidebar
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Orders Backup",
    data=csv,
    file_name="orders_backup.csv",
    mime="text/csv"
)
