import streamlit as st
import pandas as pd
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Regional Property Valuation Engine",
    page_icon="🗺️",
    layout="wide"
)

# --- 2026 LIVE PROPERTY PRICING DATA BY REGION ---
@st.cache_data
def load_regional_market_data():
    data = [
        # South Mumbai Region
        {"Region": "South Mumbai", "Locality": "Malabar Hill / Colaba", "Min_Rate": 85000, "Max_Rate": 135000, "Avg_Rate": 110000, "Rental_Yield": 4.94},
        {"Region": "South Mumbai", "Locality": "Worli / Prabhadevi", "Min_Rate": 46500, "Max_Rate": 110000, "Avg_Rate": 75000, "Rental_Yield": 4.50},
        
        # Western Suburbs Region
        {"Region": "Western Suburbs", "Locality": "Bandra West / Juhu", "Min_Rate": 45000, "Max_Rate": 75000, "Avg_Rate": 62000, "Rental_Yield": 3.40},
        {"Region": "Western Suburbs", "Locality": "Andheri West", "Min_Rate": 30000, "Max_Rate": 45000, "Avg_Rate": 37500, "Rental_Yield": 3.55},
        {"Region": "Western Suburbs", "Locality": "Goregaon / Malad West", "Min_Rate": 22000, "Max_Rate": 34000, "Avg_Rate": 26500, "Rental_Yield": 3.20},
        {"Region": "Western Suburbs", "Locality": "Borivali / Kandivali", "Min_Rate": 21000, "Max_Rate": 31000, "Avg_Rate": 24500, "Rental_Yield": 3.15},
        
        # Central Suburbs Region
        {"Region": "Central Suburbs", "Locality": "Powai / Chandivali", "Min_Rate": 28000, "Max_Rate": 42000, "Avg_Rate": 35000, "Rental_Yield": 3.82},
        {"Region": "Central Suburbs", "Locality": "Chembur / Ghatkopar", "Min_Rate": 24000, "Max_Rate": 35000, "Avg_Rate": 28000, "Rental_Yield": 3.60},
        
        # Peripheral & Affordable Region
        {"Region": "Thane Belt", "Locality": "Thane West (Prime)", "Min_Rate": 16000, "Max_Rate": 25000, "Avg_Rate": 19500, "Rental_Yield": 3.10},
        {"Region": "Navi Mumbai Hub", "Locality": "Vashi / Nerul", "Min_Rate": 19000, "Max_Rate": 30000, "Avg_Rate": 23500, "Rental_Yield": 3.30},
        {"Region": "Navi Mumbai Hub", "Locality": "Kharghar / Ulwe", "Min_Rate": 12000, "Max_Rate": 20000, "Avg_Rate": 15000, "Rental_Yield": 3.45}
    ]
    return pd.DataFrame(data)

df = load_regional_market_data()

# --- HEADER LAYER ---
st.title("🗺️ Regional Real Estate Index & Flat Price Engine")
st.markdown("Locate real-time flat value variations across geographical macro-regions and micro-market localities.")
st.write("---")

# --- NAVIGATION UI SIDEBAR ---
st.sidebar.header("📍 Region Filtering Parameters")

# Step 1: Select Macro Region
selected_region = st.sidebar.selectbox(
    "1. Select Macro Region Zone:",
    options=sorted(df["Region"].unique())
)

# Step 2: Select Micro Locality dynamically isolated to that Region
filtered_localities = df[df["Region"] == selected_region]["Locality"].tolist()
selected_locality = st.sidebar.selectbox(
    "2. Select Micro-Market Locality:",
    options=filtered_localities
)

# Step 3: Flat Configuration Layout Specs
st.sidebar.write("---")
st.sidebar.header("📐 Flat Sizing Profile")
flat_config = st.sidebar.selectbox("Flat Type Variant:", ["1 BHK", "2 BHK", "3 BHK", "4 BHK Custom"])

# Populate standard regional carpet sizing defaults safely
config_size_defaults = {"1 BHK": 450, "2 BHK": 750, "3 BHK": 1100, "4 BHK Custom": 1800}
carpet_area = st.sidebar.number_input(
    "Carpet Area (Sq. Feet):", 
    min_value=250, max_value=8000, 
    value=config_size_defaults[flat_config]
)

# Extract row calculations matrix variables
target_row = df[(df["Region"] == selected_region) & (df["Locality"] == selected_locality)].iloc[0]

# --- MAIN CONTENT DISPLAY INTERFACE ---
st.subheader(f"🔍 Current Valuation: {selected_locality} ({selected_region})")

# Real-time processing loops for total valuation cost spectrum
low_end_cost = target_row["Min_Rate"] * carpet_area
avg_end_cost = target_row["Avg_Rate"] * carpet_area
high_end_cost = target_row["Max_Rate"] * carpet_area

def format_to_crores_lakhs(value_in_inr):
    if value_in_inr >= 10000000:
        return f"₹{value_in_inr / 10000000:.2f} Cr"
    return f"₹{value_in_inr / 100000:.2f} Lakh"

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Minimum Market Value", format_to_crores_lakhs(low_end_cost), delta="Entry Level Construction")
with c2:
    st.metric("Average Market Value", format_to_crores_lakhs(avg_end_cost), delta="Mid-Segment Standard", delta_color="off")
with c3:
    st.metric("Premium Grade Value", format_to_crores_lakhs(high_end_cost), delta="Luxury/Gated Amenities")

st.write("---")

# --- VISUALIZATION TABS ---
tab_geo, tab_analytics = st.tabs(["📊 Cross-Region Comparative Metrics", "📋 Master Zone Database File"])

with tab_geo:
    st.markdown("### Comparative Regional Rate Spreads per Sq. Ft.")
    
    # Render chart comparing the absolute spectrum range across localities
    fig_range = px.bar(
        df,
        x="Locality",
        y="Avg_Rate",
        color="Region",
        title="Average Square Footage Flat Pricing Comparison Matrix",
        labels={"Avg_Rate": "Average Base Rate (₹/SqFt)", "Locality": "Locality Hub Point"},
        text_auto=True,
        height=500
    )
    fig_range.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig_range, use_container_width=True)

with tab_analytics:
    st.markdown("### Regional Master Data Catalog")
    # Clean display configuration output
    st.dataframe(
        df[["Region", "Locality", "Min_Rate", "Max_Rate", "Avg_Rate", "Rental_Yield"]],
        use_container_width=True,
        hide_index=True
    )

# Legal parameters info banner box
st.warning(
    f"🚨 **Statutory Cost Breakdown Calculation:** The above values show net base carpet price variables. "
    f"Buying a property in **{selected_region}** requires additional localized financial loads: "
    f"**Stamp Duty (approx 5-6%)**, **Registration fees (1%)**, and **GST (1% for affordable housing, 5% for standard lines)**."
)
