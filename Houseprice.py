import streamlit as st
import pandas as pd
import plotly.express as px

# --- REGIONAL APP INITIALIZATION ---
st.set_page_config(
    page_title="Regional Flat Price Index",
    page_icon="🗺️",
    layout="wide"
)

# --- PROPERTY DATA BASELINE ---
@st.cache_data
def get_regional_market_data():
    data = [
        {"Region": "South Mumbai", "Locality": "Malabar Hill / Colaba", "Min_Rate": 85000, "Max_Rate": 135000, "Avg_Rate": 110000},
        {"Region": "South Mumbai", "Locality": "Worli / Prabhadevi", "Min_Rate": 46500, "Max_Rate": 110000, "Avg_Rate": 75000},
        {"Region": "Western Suburbs", "Locality": "Bandra West / Juhu", "Min_Rate": 45000, "Max_Rate": 75000, "Avg_Rate": 62000},
        {"Region": "Western Suburbs", "Locality": "Andheri West", "Min_Rate": 30000, "Max_Rate": 45000, "Avg_Rate": 37500},
        {"Region": "Western Suburbs", "Locality": "Goregaon / Malad West", "Min_Rate": 22000, "Max_Rate": 34000, "Avg_Rate": 26500},
        {"Region": "Central Suburbs", "Locality": "Powai / Chandivali", "Min_Rate": 28000, "Max_Rate": 42000, "Avg_Rate": 35000},
        {"Region": "Thane Belt", "Locality": "Thane West (Prime)", "Min_Rate": 16000, "Max_Rate": 25000, "Avg_Rate": 19500},
        {"Region": "Navi Mumbai Hub", "Locality": "Vashi / Nerul", "Min_Rate": 19000, "Max_Rate": 30000, "Avg_Rate": 23500}
    ]
    return pd.DataFrame(data)

df = get_regional_market_data()

st.title("🗺️ Regional Real Estate Index & Flat Price Engine")
st.markdown("Locate flat value variants across geographic macro-regions instantly.")
st.write("---")

# --- INTERACTIVE DROPDOWN SELECTIONS ---
col_controls, col_display = st.columns([1, 2])

with col_controls:
    st.header("📍 Select Target Parameters")
    selected_region = st.selectbox("1. Macro Region Zone:", options=sorted(df["Region"].unique()))
    
    filtered_localities = df[df["Region"] == selected_region]["Locality"].tolist()
    selected_locality = st.selectbox("2. Micro-Market Locality:", options=filtered_localities)
    
    st.write("---")
    flat_config = st.selectbox("Flat Sizing Variant:", ["1 BHK", "2 BHK", "3 BHK"])
    config_sizes = {"1 BHK": 450, "2 BHK": 750, "3 BHK": 1100}
    carpet_area = st.number_input("Carpet Area (Sq. Feet):", min_value=250, value=config_sizes[flat_config])

# --- CALCULATION LOGIC CORRIDOR ---
target_row = df[(df["Region"] == selected_region) & (df["Locality"] == selected_locality)].iloc[0]
total_valuation = target_row["Avg_Rate"] * carpet_area

with col_display:
    st.header("📊 Flat Price Evaluation")
    
    # Hero metric layout
    if total_valuation >= 10000000:
        st.metric(label=f"Estimated Value ({selected_locality})", value=f"₹{total_valuation / 10000000:.2f} Crores")
    else:
        st.metric(label=f"Estimated Value ({selected_locality})", value=f"₹{total_valuation / 100000:.2f} Lakhs")
        
    st.write("---")
    # Quick data insights plot
    fig = px.bar(
        df[df["Region"] == selected_region], 
        x="Locality", 
        y="Avg_Rate", 
        title=f"Rate Metrics Matrix across {selected_region}",
        labels={"Avg_Rate": "Rate/Sq.Ft (₹)"}
    )
    st.plotly_chart(fig, use_container_width=True)
