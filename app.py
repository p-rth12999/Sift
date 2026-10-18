import streamlit as st
import time
from database import init_db, insert_order, fetch_all_orders, delete_order
from parser import parse_hinglish_dm

st.set_page_config(page_title="Sift | Local AI Order Parser", page_icon="⚡", layout="wide")
init_db()

# Header
st.title("⚡ Sift: Zero-Cloud Insta-Store DM Order Parser")
st.caption("100% Offline Open-Weight AI (`llama3.2:3b`) • Zero API Cost • Full Customer Data Privacy")

# Sidebar Configuration & Sample Test Loader
with st.sidebar:
    st.header("⚙️ Engine Settings")
    model_choice = st.selectbox("Local Open-Weight Model", ["gemma2:2b", "llama3.2:3b"], index=0)
    st.success("🟢 Local Ollama Engine Active")
    st.markdown("---")
    st.subheader("🧪 Load Hinglish Test Samples")
    if st.button("Load 3 Messy Hinglish DMs"):
        st.session_state["sample_input"] = (
            "Bhai 2 oversized black acid-wash tees bhej do L size mein. "
            "Name: Rohan Deshmukh, Ph: 9823011223. Address: Flat 402, Sai Residency, Kothrud, Pune 411038. "
            "GPay kar diya hai 1398 rs.\n"
            "---\n"
            "Hey di! Need 1 Aesthetic Crochet Tote Bag (Beige). COD rakhna please. "
            "Sneha Patil, 8805544332, Hostel 4, Viman Nagar, Pune. Price 650 na?\n"
            "---\n"
            "Bro 3 cargo pants olive green XL size confirm kar do. "
            "Aditya Kulkarni (9123456780). Deliver to: Shop 12, FC Road, Pune. Payment pending hai abhi."
        )

# Main Layout: Left (Input) | Right (Metrics & Database)
col1, col2 = st.columns([1, 1.4])

with col1:
    st.subheader("📥 Paste Instagram / WhatsApp DMs")
    st.write("Tip: Paste multiple DMs separated by `---` to batch-process orders at once.")
    
    default_text = st.session_state.get("sample_input", "")
    dm_input = st.text_area("Messy Customer Messages:", value=default_text, height=240, placeholder="Paste Hinglish DM here...")

    if st.button("🚀 Parse & Save Orders Locally", type="primary", use_container_width=True):
        if not dm_input.strip():
            st.warning("Please paste at least one DM message first.")
        else:
            raw_dms = [msg.strip() for msg in dm_input.split("---") if msg.strip()]
            progress = st.progress(0)
            status_text = st.empty()
            start_time = time.time()

            for idx, dm in enumerate(raw_dms):
                status_text.info(f"⚡ Parsing DM {idx + 1} of {len(raw_dms)} offline via {model_choice}...")
                extracted = parse_hinglish_dm(dm, model_name=model_choice)
                insert_order(extracted, dm)
                progress.progress((idx + 1) / len(raw_dms))

            elapsed = round(time.time() - start_time, 2)
            status_text.success(f"✅ Extracted {len(raw_dms)} order(s) in {elapsed}s! Cost: ₹0.00")

with col2:
    st.subheader("📊 Live Order Book & Dispatch Sheet")
    orders_df = fetch_all_orders()

    if not orders_df.empty:
        # Top KPI Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Orders", len(orders_df))
        m2.metric("Total Revenue", f"₹{orders_df['total_amount'].sum():,.0f}")
        paid_count = len(orders_df[orders_df["payment_status"].str.lower() == "paid"])
        m3.metric("Paid Orders", f"{paid_count} / {len(orders_df)}")

        # Display Clean Table
        display_cols = [
            "id", "customer_name", "phone_number", "item_name", 
            "quantity", "size", "total_amount", "payment_status", "delivery_address", "created_at"
        ]
        st.dataframe(orders_df[display_cols], use_container_width=True, hide_index=True)

        # Export & Delete Controls
        c_dl, c_del = st.columns([2, 1])
        with c_dl:
            csv_data = orders_df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Excel/CSV Dispatch Sheet",
                data=csv_data,
                file_name="sift_dispatch_orders.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_del:
            del_id = st.number_input("Order ID to delete", min_value=1, step=1, label_visibility="collapsed")
            if st.button("🗑️ Delete Order ID", use_container_width=True):
                delete_order(int(del_id))
                st.rerun()
    else:
        st.info("No orders logged yet. Click **'Load 3 Messy Hinglish DMs'** in the left sidebar and hit Parse!")
