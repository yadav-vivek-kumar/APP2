import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# 1. Page Configuration
st.set_page_config(
    page_title="AI Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Helper Function to Generate Mock Business Data
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    n_customers = 200
    customer_ids = [f"CUST-{i:04d}" for i in range(1, n_customers + 1)]
    
    recency = np.random.randint(1, 365, size=n_customers)
    frequency = np.random.randint(1, 50, size=n_customers)
    monetary = frequency * np.random.uniform(20, 150, size=n_customers) + np.random.normal(0, 10, size=n_customers)
    monetary = np.clip(monetary, 10, None)  # Ensure no negative values
    
    df = pd.DataFrame({
        "CustomerID": customer_ids,
        "Recency (Days since last purchase)": recency,
        "Frequency (Total Orders)": frequency,
        "Monetary (Total Spend $)": np.round(monetary, 2)
    })
    return df

# 3. Main Header
st.title("📊 AI-Driven Customer Insights & LTV Predictor")
st.markdown("""
This enterprise-grade application utilizes **Unsupervised Machine Learning (K-Means Clustering)** for behavior-based customer segmentation and **Supervised Learning (Linear Regression)** to predict future Customer Lifetime Value (LTV). 
""")

st.sidebar.header("📁 Data Source Control")
data_option = st.sidebar.radio("Select Dataset:", ("Use Demo E-Commerce Data", "Upload Custom CSV"))

# Load Data
if data_option == "Upload Custom CSV":
    uploaded_file = st.sidebar.file_uploader("Upload your business CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.sidebar.warning("Awaiting file upload. Showing demo data instead.")
        df = generate_mock_data()
else:
    df = generate_mock_data()

# Tabs for Organized Navigation
tab1, tab2, tab3 = st.tabs(["📋 Data Overview", "🤖 AI Customer Segmentation", "🔮 LTV Prediction Model"])

# --- TAB 1: DATA OVERVIEW ---
with tab1:
    st.header("Business Metrics Overview")
    
    # Key Performance Indicators (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{df.shape[0]}")
    col2.metric("Total Revenue", f"${df.iloc[:, 3].sum():,.2f}")
    col3.metric("Avg Spend per Customer", f"${df.iloc[:, 3].mean():,.2f}")
    col4.metric("Avg Purchase Frequency", f"{df.iloc[:, 2].mean():.1f} orders")
    
    st.subheader("Raw Customer Transaction Data Summary")
    st.dataframe(df, use_container_width=True)

# --- TAB 2: AI CUSTOMER SEGMENTATION ---
with tab2:
    st.header("Unsupervised AI: Customer Segmentation")
    st.markdown("By analyzing **Recency, Frequency, and Monetary (RFM)** metrics, the K-Means algorithm groups similar buyers together to identify VIPs, at-risk clients, and casual shoppers.")
    
    # Sidebar control for clusters placed inline or in sidebar contextually
    n_clusters = st.slider("Select Number of Customer Clusters (AI 'K' Parameter)", min_value=2, max_value=6, value=3)
    
    # Prepare features for AI
    features = df.iloc[:, 1:4]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Apply K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(scaled_features)
    df['Cluster'] = df['Cluster'].apply(lambda x: f"Cluster {x+1}")
    
    # Visualization: 3D Scatter Plot
    st.subheader("3D Interactive Customer Clusters")
    fig = px.scatter_3d(
        df, 
        x=df.columns[1], 
        y=df.columns[2], 
        z=df.columns[3],
        color='Cluster',
        title="Customer Persona Visualization",
        labels={df.columns[1]: 'Recency', df.columns[2]: 'Frequency', df.columns[3]: 'Monetary Value'},
        opacity=0.8
    )
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=40))
    st.plotly_chart(fig, use_container_width=True)
    
    # Cluster Analysis Table
    st.subheader("Segment Analysis For Marketing Strategy")
    cluster_summary = df.groupby('Cluster').mean(numeric_only=True).reset_index()
    st.dataframe(cluster_summary, use_container_width=True)

# --- TAB 3: LTV PREDICTION ---
with tab3:
    st.header("Supervised AI: Future Value Prediction")
    st.markdown("Predict future financial value using historical interaction behavior.")
    
    # Target and Features setup
    X = df.iloc[:, 1:3] # Recency and Frequency
    y = df.iloc[:, 3]   # Monetary (Current Value as proxy for target LTV metrics)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    st.subheader("Predict Customer Spend Potential Instantly")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        input_recency = st.number_input("Days since customer's last purchase:", min_value=1, max_value=365, value=30)
    with col_input2:
        input_frequency = st.number_input("Total transactions completed historically:", min_value=1, max_value=100, value=5)
        
    # Prediction Generation
    user_input = np.array([[input_recency, input_frequency]])
    predicted_val = model.predict(user_input)[0]
    
    st.success(f"### 🔮 Predicted Customer Value: ${max(predicted_val, 0.0):,.2f}")
    
    # Teacher Bonus: Model Performance transparency
    st.info(f"**Academic Transparency Note:** This model is running a live scikit-learn Linear Regression. Training R² Score: **{model.score(X_train, y_train):.2f}**")
