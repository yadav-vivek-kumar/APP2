import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# App Configuration
st.set_page_config(
    page_title="LogiRoute Fleet Optimizer",
    page_icon="🚚",
    layout="wide"
)

# Dark Fleet Management UI Adjustments
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 16px;
        border-radius: 10px;
    }
    div[data-testid="stSidebar"] { background-color: #0b0f19; }
    </style>
""", unsafe_allow_html=True)

st.title("🚚 LogiRoute Last-Mile Fleet Dispatcher")
st.markdown("🔒 **Business Problem:** Minimizing fuel overheads and route overlaps by algorithmically clustering delivery destinations for local fleets.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("📦 Fleet Parameters")

available_drivers = st.sidebar.slider(
    "Number of Active Drivers (Fleets)",
    min_value=2,
    max_value=6,
    value=3
)

total_packages = st.sidebar.slider(
    "Total Outstanding Packages Today",
    min_value=10,
    max_value=100,
    value=40,
    step=5
)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Central Hub Coordinates")
hub_lat = st.sidebar.number_input("Warehouse Latitude", value=19.0760)  # Defaults near Mumbai region
hub_lon = st.sidebar.number_input("Warehouse Longitude", value=72.8777)

# --- SIMULATE REAL RANDOM LOCATION POINTS ---
@st.cache_data(ttl=600)
def generate_delivery_points(num_points, h_lat, h_lon):
    np.random.seed(42) # Keeps layout consistent across slider changes
    # Generate random delivery drop-offs within a 15km radius of the warehouse hub
    lats = h_lat + np.random.uniform(-0.1, 0.1, num_points)
    lons = h_lon + np.random.uniform(-0.1, 0.1, num_points)
    
    # Randomly assign package weights (kg) and urgency priorities
    weights = np.random.uniform(0.5, 15.0, num_points)
    priorities = np.random.choice(["Standard", "Express", "Same-Day Priority"], num_points, p=[0.5, 0.3, 0.2])
    
    return pd.DataFrame({
        "Latitude": lats,
        "Longitude": lons,
        "Payload_Weight_KG": weights,
        "Priority": priorities
    })

df_deliveries = generate_delivery_points(total_packages, hub_lat, hub_lon)

# --- ALGORITHMIC CLUSTERING ENGINE (K-MEANS) ---
# Coordinates vector matrix extraction
X = df_deliveries[["Latitude", "Longitude"]]

# Run KMeans clustering to assign packages to the closest geometric driver group
kmeans = KMeans(n_clusters=available_drivers, random_state=42, n_init=10)
df_deliveries["Driver_ID"] = kmeans.fit_predict(X) + 1 # Dynamic ID assignment (Driver 1, Driver 2...)

# Calculate operational metrics
total_weight = df_deliveries["Payload_Weight_KG"].sum()
avg_packages_per_driver = total_packages / available_drivers

# --- UI VIEW DISPLAY ---
st.subheader("📊 Dispatch Operations Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Fleet Size Assigned", f"{available_drivers} Active Drivers")
with col2:
    st.metric("Active Deliveries Routed", f"{total_packages} Drop-offs")
with col3:
    st.metric("Total Cargo manifest Weight", f"{total_weight:.1f} KG")
with col4:
    st.metric("Avg Load Per Driver", f"{avg_packages_per_driver:.1f} Parcels")

st.markdown("---")

# Split Dashboard Workspace Layout
map_col, manifest_col = st.columns([3, 2])

with map_col:
    st.subheader("🗺️ Algorithmic Fleet Allocation Map")
    st.caption("Each unique colored node group represents a highly optimized, distinct zone assigned to a separate delivery driver.")
    
    fig = go.Figure()
    
    # 1. Plot the Central Depot / Warehouse Hub
    fig.add_trace(go.Scatter(
        x=[hub_lon], y=[hub_lat],
        mode='markers',
        name='🏢 Central Logistics Hub',
        marker=dict(size=16, color='#ef4444', symbol='square'),
        hovertemplate="<b>Central Distribution Center</b><extra></extra>"
    ))
    
    # 2. Plot clustered package allocations iteratively per assigned driver
    colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899', '#14b8a6']
    
    for driver in range(1, available_drivers + 1):
        driver_df = df_deliveries[df_deliveries["Driver_ID"] == driver]
        color_assigned = colors[(driver - 1) % len(colors)]
        
        # Plot drop points
        fig.add_trace(go.Scatter(
            x=driver_df["Longitude"], y=driver_df["Latitude"],
            mode='markers+text',
            name=f"🚛 Driver Group {driver} Zone",
            marker=dict(size=9, color=color_assigned, symbol='circle'),
            hovertemplate="<b>Driver:</b> " + str(driver) + "<br><b>Weight:</b> %{text} KG<extra></extra>",
            text=driver_df["Payload_Weight_KG"].round(1).astype(str)
        ))
        
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
        xaxis=dict(title="Longitude Coordinate Points", showgrid=True, gridcolor='#232a3b'),
        yaxis=dict(title="Latitude Coordinate Points", showgrid=True, gridcolor='#232a3b'),
        hovermode="closest"
    )
    st.plotly_chart(fig, use_container_width=True)

with manifest_col:
    st.subheader("📋 Digital Freight Manifest Sheets")
    
    selected_driver_view = st.selectbox(
        "Filter Checklist by Route Assignment:",
        options=[f"Driver {i}" for i in range(1, available_drivers + 1)]
    )
    
    # Extract numerical index identifier
    driver_num = int(selected_driver_view.split(" ")[1])
    filtered_manifest = df_deliveries[df_deliveries["Driver_ID"] == driver_num]
    
    # Format and present clean layout lists
    presentation_df = filtered_manifest[["Payload_Weight_KG", "Priority", "Latitude", "Longitude"]].copy()
    presentation_df["Payload_Weight_KG"] = presentation_df["Payload_Weight_KG"].round(2).astype(str) + " kg"
    
    st.markdown(f"**Total parcels assigned to this route:** {len(presentation_df)}")
    st.dataframe(presentation_df, hide_index=True, use_container_width=True)
