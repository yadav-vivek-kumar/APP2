import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit command)
# ---------------------------------------------------------
st.set_page_config(page_title="Flat Rate Finder", page_icon="📦", layout="centered")

# ---------------------------------------------------------
# DEFAULT RATE TABLE
# Edit this dictionary to use your own regions and prices.
# Keys = region name, Values = flat rate.
# (Change CURRENCY_SYMBOL below if you're not using USD.)
# ---------------------------------------------------------
DEFAULT_RATES = {
    "North America": 10.00,
    "South America": 18.00,
    "Europe": 15.00,
    "Africa": 22.00,
    "Asia": 20.00,
    "Middle East": 19.00,
    "Oceania": 25.00,
}
CURRENCY_SYMBOL = "$"


def default_df():
    return pd.DataFrame(list(DEFAULT_RATES.items()), columns=["Region", "Rate"])


if "rates_df" not in st.session_state:
    st.session_state.rates_df = default_df()

# ---------------------------------------------------------
# SIDEBAR — optionally replace the rate table with your own CSV
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Rate table")
    st.caption("Upload a CSV with 'Region' and 'Rate' columns to use your own data.")

    uploaded_file = st.file_uploader("Upload rates (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            custom_df = pd.read_csv(uploaded_file)
            custom_df.columns = [c.strip().title() for c in custom_df.columns]
            if {"Region", "Rate"}.issubset(custom_df.columns):
                custom_df["Rate"] = pd.to_numeric(custom_df["Rate"], errors="coerce")
                custom_df = custom_df.dropna(subset=["Region", "Rate"])
                custom_df = custom_df.drop_duplicates(subset="Region", keep="last")
                st.session_state.rates_df = custom_df[["Region", "Rate"]].reset_index(drop=True)
                st.success(f"Loaded {len(custom_df)} regions.")
            else:
                st.error("CSV must contain 'Region' and 'Rate' columns.")
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")

    if st.button("Reset to default rates"):
        st.session_state.rates_df = default_df()
        st.rerun()

    st.divider()
    template_csv = pd.DataFrame({"Region": ["My Region"], "Rate": [0.00]}).to_csv(index=False)
    st.download_button("Download CSV template", template_csv, "rate_template.csv", "text/csv")

rates_df = st.session_state.rates_df

# ---------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------
st.title("📦 Flat Rate Finder")
st.caption("Select a region to see its flat rate.")

if rates_df.empty:
    st.warning("No regions loaded. Upload a CSV or reset to defaults from the sidebar.")
else:
    region_list = sorted(rates_df["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", region_list)

    rate_value = rates_df.loc[rates_df["Region"] == selected_region, "Rate"].iloc[0]
    st.metric(label=f"Flat rate — {selected_region}", value=f"{CURRENCY_SYMBOL}{rate_value:,.2f}")

    with st.expander("📊 View all regions and rates"):
        st.dataframe(
            rates_df.sort_values("Region").reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
        st.bar_chart(rates_df.set_index("Region")["Rate"])

st.divider()
st.caption("Built with Streamlit. Edit DEFAULT_RATES in app.py, or upload a CSV, to use your own regions.")
