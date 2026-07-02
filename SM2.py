import streamlit as st
import pandas as pd
import plotly.express as px

# --- INITIALIZE PAGE ---
st.set_page_config(
    page_title="Flat Availability Hub",
    page_icon="🏢",
    layout="wide"
)

# --- SIMULATED APARTMENT DATABASE ---
if "flats" not in st.session_state:
    st.session_state.flats = pd.DataFrame([
        {"Flat_No": "101", "Floor": "1st", "BHK": "1 BHK", "Rent_USD": 1200, "Status": "Available", "Tenant": "-"},
        {"Flat_No": "102", "Floor": "1st", "BHK": "2 BHK", "Rent_USD": 1800, "Status": "Occupied", "Tenant": "Sarah Jenkins"},
        {"Flat_No": "201", "Floor": "2nd", "BHK": "2 BHK", "Rent_USD": 1850, "Status": "Available", "Tenant": "-"},
        {"Flat_No": "202", "Floor": "2nd", "BHK": "3 BHK", "Rent_USD": 2500, "Status": "Maintenance", "Tenant": "-"},
        {"Flat_No": "301", "Floor": "3rd", "BHK": "1 BHK", "Rent_USD": 1250, "Status": "Occupied", "Tenant": "Michael Chang"},
        {"Flat_No": "302", "Floor": "3rd", "BHK": "3 BHK", "Rent_USD": 2600, "Status": "Available", "Tenant": "-"},
    ])

# --- APP HEADER ---
st.title("🏢 Flat Availability & Management Tracker")
st.markdown("Track, filter, and manage apartment lease status and maintenance records in real-time.")
st.write("---")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Inventory")
status_filter = st.sidebar.multiselect(
    "Filter by Status:",
    options=st.session_state.flats["Status"].unique(),
    default=st.session_state.flats["Status"].unique()
)
bhk_filter = st.sidebar.multiselect(
    "Filter by Config (BHK):",
    options=st.session_state.flats["BHK"].unique(),
    default=st.session_state.flats["BHK"].unique()
)

# Apply filters
filtered_df = st.session_state.flats[
    (st.session_state.flats["Status"].isin(status_filter)) &
    (st.session_state.flats["BHK"].isin(bhk_filter))
]

# --- METRIC HERO TILES ---
total_flats = len(st.session_state.flats)
avail_flats = len(st.session_state.flats[st.session_state.flats["Status"] == "Available"])
occ_flats = len(st.session_state.flats[st.session_state.flats["Status"] == "Occupied"])
maint_flats = len(st.session_state.flats[st.session_state.flats["Status"] == "Maintenance"])

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Flats", total_flats)
with m2:
    st.metric("Available To Rent", avail_flats, delta=f"{avail_flats} open", delta_color="normal")
with m3:
    st.metric("Occupied", occ_flats)
with m4:
    st.metric("Under Maintenance", maint_flats)

st.write("---")

# --- TABS FOR WORKFLOWS ---
tab_view, tab_manage = st.tabs(["📊 Inventory Dashboard", "⚙️ Update Flat Status"])

with tab_view:
    col_table, col_chart = st.columns([3, 2])
    
    with col_table:
        st.subheader("Current Flat Registry")
        # Visual color mapping formatting for clarity
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
    with col_chart:
        st.subheader("Occupancy Breakdown")
        if not filtered_df.empty:
            fig = px.pie(
                filtered_df, 
                names="Status", 
                title="Status Proportions",
                color="Status",
                color_discrete_map={"Available": "#2ECC71", "Occupied": "#3498DB", "Maintenance": "#E74C3C"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No flats match your filters.")

with tab_manage:
    st.subheader("Change Status / Log New Booking")
    
    col_f, col_s, col_t = st.columns(3)
    
    with col_f:
        selected_flat = st.selectbox("Select Flat Number:", st.session_state.flats["Flat_No"].tolist())
    
    # Extract current values for chosen flat
    current_row = st.session_state.flats[st.session_state.flats["Flat_No"] == selected_flat].iloc[0]
    
    with col_s:
        new_status = st.selectbox(
            "Target Status:", 
            options=["Available", "Occupied", "Maintenance"], 
            index=["Available", "Occupied", "Maintenance"].index(current_row["Status"])
        )
        
    with col_t:
        # Enable or disable tenant entry based on selected status
        if new_status == "Occupied":
            default_tenant = "" if current_row["Tenant"] == "-" else current_row["Tenant"]
            new_tenant = st.text_input("Tenant Full Name:", value=default_tenant)
        else:
            new_tenant = "-"
            st.text_input("Tenant Full Name:", value="-", disabled=True)

    if st.button("Commit Status Change", type="primary"):
        # Locating the row index in the session state
        idx = st.session_state.flats[st.session_state.flats["Flat_No"] == selected_flat].index[0]
        
        # Validations
        if new_status == "Occupied" and (not new_tenant or new_tenant.strip() == "-"):
            st.error("Please enter a valid tenant name for 'Occupied' status updates.")
        else:
            st.session_state.flats.at[idx, "Status"] = new_status
            st.session_state.flats.at[idx, "Tenant"] = new_tenant
            st.success(f"Successfully updated Flat {selected_flat} to {new_status}!")
            st.rerun()
