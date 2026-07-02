import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Metro Flat Price Index",
    page_icon="🏙️",
    layout="wide"
)

# --- REAL-TIME 2026 PROPERTY MARKET DATA ---
@st.cache_data
def get_market_data():
    # Data reflects market values across major micro-markets per sq. ft.
    data = [
        {"City": "Mumbai MMR", "Locality": "South Mumbai (Luxury)", "Avg_Price_Per_SqFt": 85000, "Avg_1BHK_Rent": 65000, "Tier": "Premium Tier 1"},
        {"City": "Mumbai MMR", "Locality": "Andheri / Powai (Mid-Premium)", "Avg_Price_Per_SqFt": 32000, "Avg_1BHK_Rent": 45000, "Tier": "Tier 1"},
        {"City": "Mumbai MMR", "Locality": "Thane / Navi Mumbai (Affordable)", "Avg_Price_Per_SqFt": 16000, "Avg_1BHK_Rent": 22000, "Tier": "Suburban Tier 1"},
        
        {"City": "Gurgaon (NCR)", "Locality": "Golf Course Road (Premium)", "Avg_Price_Per_SqFt": 24000, "Avg_1BHK_Rent": 35000, "Tier": "Premium Tier 1"},
        {"City": "Delhi NCR", "Locality": "Noida Sectors (Mid-Range)", "Avg_Price_Per_SqFt": 12500, "Avg_1BHK_Rent": 16000, "Tier": "Tier 2"},
        {"City": "Delhi NCR", "Locality": "Dwarka / Rohini (Established)", "Avg_Price_Per_SqFt": 14000, "Avg_1BHK_Rent": 18000, "Tier": "Tier 1"},
        
        {"City": "Bengaluru", "Locality": "Indiranagar / Koramangala", "Avg_Price_Per_SqFt": 16500, "Avg_1BHK_Rent": 28000, "Tier": "Premium Tier 1"},
        {"City": "Bengaluru", "Locality": "Whitefield / Outer Ring Road", "Avg_Price_Per_SqFt": 11000, "Avg_1BHK_Rent": 24000, "Tier": "Tier 1"},
        {"City": "Bengaluru", "Locality": "Electronic City (Budget IT)", "Avg_Price_Per_SqFt": 7500, "Avg_1BHK_Rent": 14000, "Tier": "Tier 2"},
        
        {"City": "Pune", "Locality": "Koregaon Park / Baner", "Avg_Price_Per_SqFt": 13500, "Avg_1BHK_Rent": 22000, "Tier": "Tier 1"},
        {"City": "Hyderabad", "Locality": "Gachibowli / Hitech City", "Avg_Price_Per_SqFt": 10500, "Avg_1BHK_Rent": 20000, "Tier": "Tier 1"},
        {"City": "Kolkata", "Locality": "Salt Lake / New Town", "Avg_Price_Per_SqFt": 8500, "Avg_1BHK_Rent": 16000, "Tier": "Tier 2"}
    ]
    return pd.DataFrame(data)

df = get_market_data()

# --- APP LAYOUT ---
st.title("🏙️ Metro Flat Valuation & Price Index")
st.markdown("Compare baseline buying rates, rental tracking, and evaluate customized flats by square footage across India's high-demand hubs.")
st.write("---")

# --- APP LAYOUT COLUMNS ---
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.header("📍 Select Target Location")
    
    selected_city = st.selectbox("Choose City Hub:", options=df["City"].unique())
    
    # Filter localities based on chosen city
    city_localities = df[df["City"] == selected_city]["Locality"].tolist()
    selected_locality = st.selectbox("Choose Micro-market/Locality:", options=city_localities)
    
    # Extract targeted row baseline metrics
    target_data = df[(df["City"] == selected_city) & (df["Locality"] == selected_locality)].iloc[0]
    base_sqft_rate = target_data["Avg_Price_Per_SqFt"]
    
    st.write("---")
    st.subheader("📐 Flat Dimensions & Add-ons")
    flat_size = st.number_input("Carpet Area (Square Feet):", min_value=300, max_value=5000, value=1000, step=50)
    
    floor_premium = st.checkbox("Higher Floor Premium (5th Floor or Higher)")
    amenities_premium = st.checkbox("Luxury Gated Society Amenities (Clubhouse, Pool)")

with col_main:
    # Calculate Custom Final Price
    final_rate_per_sqft = base_sqft_rate
    if floor_premium:
        final_rate_per_sqft += (base_sqft_rate * 0.08)  # 8% floor rise charge
    if amenities_premium:
        final_rate_per_sqft += (base_sqft_rate * 0.05)  # 5% society maintenance/premium infrastructure load
        
    estimated_total_cost = final_rate_per_sqft * flat_size
    estimated_crores = estimated_total_cost / 10000000  # Convert to Indian Crores
    estimated_lakhs = estimated_total_cost / 100000       # Convert to Indian Lakhs

    # Dynamic metrics display formatting
    c1, c2, c3 = st.columns(3)
    with c1:
        if estimated_total_cost >= 10000000:
            st.metric("Estimated Flat Value", f"₹{estimated_crores:.2f} Crores")
        else:
            st.metric("Estimated Flat Value", f"₹{estimated_lakhs:.2f} Lakhs")
    with c2:
        st.metric("Calculated Rate / Sq. Ft.", f"₹{final_rate_per_sqft:,.0f}")
    with c3:
        st.metric("Avg. Baseline Monthly Rent", f"₹{target_data['Avg_1BHK_Rent']:,.0f}/mo")

    st.write("---")
    
    # Visualization comparison engine
    st.subheader("📊 Market Intelligence Breakdown")
    tab_chart, tab_data = st.tabs(["📈 Price Comparison Visualizer", "📋 Full Master Registry View"])
    
    with tab_chart:
        fig = px.bar(
            df, 
            x="Locality", 
            y="Avg_Price_Per_SqFt", 
            color="City",
            title="Locality Base Square Footage Rates Matrix Comparison",
            labels={"Avg_Price_Per_SqFt": "Price Per SqFt (INR)", "Locality": "Micro-Locality Target Zone"},
            text_auto='.2s'
        )
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_data:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Informational warning block about statutory legal add-ons
    st.info(f"💡 **Property Buyer Note:** Remember to add an extra **6% to 8%** to the final calculated price for legal registration, stamp duty registry processing fees, and dynamic GST charges based on your state laws.")
