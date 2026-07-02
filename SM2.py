import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="E-Commerce B2B Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Lifetime Value & Churn Risk Dashboard")
st.markdown("""
This dashboard helps account managers identify high-value clients at risk of churning. 
It uses a **Random Forest Classifier** trained dynamically on customer behavioral data.
""")

# 2. DATA GENERATION (MOCK BUSINESS DATA)
@st.cache_data
def load_mock_data():
    np.random.seed(42)
    n_customers = 400
    
    customer_ids = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    tenure_months = np.random.randint(1, 48, size=n_customers)
    monthly_charges = np.random.uniform(50, 500, size=n_customers)
    total_support_calls = np.random.randint(0, 10, size=n_customers)
    clv = (monthly_charges * tenure_months) * np.random.uniform(0.8, 1.2, size=n_customers)
    
    # Logic to make churn look realistic
    churn_probability = 1 / (1 + np.exp(-(-2 + 0.5 * total_support_calls - 0.04 * tenure_months)))
    churned = (np.random.rand(n_customers) < churn_probability).astype(int)
    
    df = pd.DataFrame({
        "CustomerID": customer_ids,
        "TenureMonths": tenure_months,
        "MonthlyCharges": np.round(monthly_charges, 2),
        "TotalSupportCalls": total_support_calls,
        "CLV": np.round(clv, 2),
        "Churn": churned
    })
    return df

df = load_mock_data()

# 3. MACHINE LEARNING MODEL TRAINING
@st.cache_resource
def train_model(data):
    X = data[["TenureMonths", "MonthlyCharges", "TotalSupportCalls", "CLV"]]
    y = data["Churn"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    return model

model = train_model(df)

# Add predictions back to the core dataframe
X_all = df[["TenureMonths", "MonthlyCharges", "TotalSupportCalls", "CLV"]]
df["Churn_Risk_Prob"] = model.predict_proba(X_all)[:, 1]

# 4. SIDEBAR CONTROLS
st.sidebar.header("🎯 Dashboard Filters")
clv_threshold = st.sidebar.slider(
    "Minimum Customer Lifetime Value (CLV)", 
    int(df["CLV"].min()), 
    int(df["CLV"].max()), 
    int(df["CLV"].median())
)

risk_threshold = st.sidebar.slider(
    "Churn Risk Probability Threshold", 
    0.0, 1.0, 0.50, step=0.05
)

filtered_df = df[(df["CLV"] >= clv_threshold) & (df["Churn_Risk_Prob"] >= risk_threshold)]

# 5. MAIN KPI METRICS
st.subheader("📈 Business Performance Overview")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(label="Total Portfolio Value", value=f"${df['CLV'].sum():,.2f}")
with kpi2:
    at_risk_count = df[df["Churn_Risk_Prob"] >= 0.5].shape[0]
    st.metric(label="Customers At High Risk (>50%)", value=at_risk_count, delta=f"{at_risk_count/len(df)*100:.1f}% of base", delta_color="inverse")
with kpi3:
    st.metric(label="Average CLV", value=f"${df['CLV'].mean():,.2f}")

st.markdown("---")

# 6. CHARTS & VISUALIZATIONS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Support Calls vs. Churn Risk Proximity")
    fig_scatter = px.scatter(
        df, 
        x="TotalSupportCalls", 
        y="Churn_Risk_Prob", 
        color="Churn",
        size="MonthlyCharges",
        hover_data=["CustomerID"],
        labels={"TotalSupportCalls": "Support Desk Interactions", "Churn_Risk_Prob": "Predicted Churn Probability"},
        color_continuous_scale=px.colors.sequential.Bluered
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Distribution of Customer Value (CLV)")
    fig_hist = px.histogram(
        df, 
        x="CLV", 
        color="Churn", 
        barmode="overlay",
        labels={"CLV": "Lifetime Value ($)"},
        color_discrete_sequence=["#2ca02c", "#d62728"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# 7. ACTIONABLE INSIGHTS TABLE
st.markdown("---")
st.subheader("🚨 Action Items: High-Value Clients to Intervene")

display_cols = ["CustomerID", "TenureMonths", "MonthlyCharges", "TotalSupportCalls", "CLV", "Churn_Risk_Prob"]
action_df = filtered_df[display_cols].sort_values(by="Churn_Risk_Prob", ascending=False)

if not action_df.empty:
    st.dataframe(
        action_df.style.format({
            "MonthlyCharges": "${:.2f}",
            "CLV": "${:.2f}",
            "Churn_Risk_Prob": "{:.1%}"
        }), 
        use_container_width=True
    )
else:
    st.success("No customers match your risk profile criteria. Keep up the good work!")
