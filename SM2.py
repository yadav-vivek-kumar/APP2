import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.optimize as sco
import requests
import random

# App Interface Setup
st.set_page_config(
    page_title="AI Portfolio Optimizer",
    page_icon="🤖",
    layout="wide"
)

# Dark Executive Dashboard Styling
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 12px;
    }
    .stProgress > div > div > div > div {
        background-color: #10b981;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Driven Portfolio Allocation Terminal")
st.markdown("🔒 **Business Use-Case:** Algorithmic Risk-Mitigation and Capital Optimization Engine for Retail Wealth Managers.")

# Anti-Throttling User Agents
AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
]

@st.cache_data(ttl=300)
def fetch_portfolio_history(tickers):
    session = requests.Session()
    session.headers.update({'User-Agent': random.choice(AGENTS)})
    
    # We fetch 1 Year of historical data to run the optimization models cleanly
    df = pd.DataFrame()
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol, session=session)
            hist = stock.history(period="1y", interval="1d")
            if not hist.empty:
                df[symbol] = hist['Close']
        except Exception:
            pass
    return df

# --- SIDEBAR: ASSET COMPOSITION ---
st.sidebar.header("💼 Target Asset Basket")
st.sidebar.markdown("Define the core assets available for your investment pool:")

default_basket = ["AAPL", "NVDA", "MSFT", "RELIANCE.NS", "TSLA"]
user_basket_input = st.sidebar.text_input(
    "Asset Tickers (Comma-separated)", 
    value=", ".join(default_basket)
)

# Parse inputs securely
portfolio_tickers = [t.strip().upper() for t in user_basket_input.split(",") if t.strip()]

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Optimization Target")
optimization_strategy = st.sidebar.radio(
    "Select AI Allocation Mode",
    options=["Maximize Sharpe Ratio (High Efficiency)", "Minimum Volatility (Low Risk)"]
)

# --- EXECUTION LOGIC ---
if len(portfolio_tickers) < 2:
    st.warning("⚠️ Please provide at least 2 valid ticker symbols to perform optimization analysis.")
else:
    with st.spinner("Streaming price metrics and compiling covariance matrices..."):
        price_matrix = fetch_portfolio_history(portfolio_tickers)
        
    if price_dataframe_empty := price_matrix.empty or (price_matrix.shape[1] < 2):
        st.error("❌ App processing failed. Server connection timed out or symbols could not be resolved.")
    else:
        # Calculate performance statistics mathematically
        log_returns = np.log(price_matrix / price_matrix.shift(1)).dropna()
        num_assets = len(price_matrix.columns)
        
        # Expected annual returns & covariance matrix
        annual_returns = log_returns.mean() * 252
        covariance_matrix = log_returns.cov() * 252

        # --- MATHEMATICAL PORTFOLIO ENGINE (SCIPY DRIVEN) ---
        def get_portfolio_stats(weights):
            weights = np.array(weights)
            p_ret = np.sum(annual_returns * weights)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            sharpe = p_ret / p_vol if p_vol != 0 else 0
            return np.array([p_ret, p_vol, sharpe])

        # Scipy Optimization Functions
        def min_func_sharpe(weights): return -get_portfolio_stats(weights)[2]
        def min_func_variance(weights): return get_portfolio_stats(weights)[1]

        # Allocation boundaries: sum of weights equals 100% (1.0), weights must be between 0 and 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for asset in range(num_assets))
        initial_guess = num_assets * [1. / num_assets,]

        if "Sharpe" in optimization_strategy:
            opt_results = sco.minimize(min_func_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        else:
            opt_results = sco.minimize(min_func_variance, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

        optimal_weights = opt_results['x']
        metrics = get_portfolio_stats(optimal_weights)

        # --- VIEW RENDERING (PREMIUM UX) ---
        st.subheader("💡 Algorithmic Allocation Breakdown")
        st.markdown("The system has computed the most mathematically efficient way to spread capital across your assets:")
        
        # Display Core Optimization Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Expected Annual Return", f"{metrics[0]*100:.2f}%")
        col2.metric("Portfolio Volatility (Risk)", f"{metrics[1]*100:.2f}%")
        col3.metric("Sharpe Performance Ratio", f"{metrics[2]:.2f}")

        st.markdown("---")
        
        # Split layout for interactive charts
        chart_col, data_col = st.columns([3, 2])
        
        with data_col:
            st.subheader("📋 Recommended Capital Weightings")
            for idx, ticker in enumerate(price_matrix.columns):
                percentage = optimal_weights[idx] * 100
                st.markdown(f"**{ticker}**")
                st.progress(int(percentage))
                st.caption(f"Allocate **{percentage:.2f}%** of capital to this asset.")

        with chart_col:
            # Render Clean Allocation Pie/Donut Chart using Plotly
            fig = go.Figure(data=[go.Pie(
                labels=list(price_matrix.columns),
                values=optimal_weights * 100,
                hole=.4,
                marker=dict(colors=st.colors.radial),
                hoverinfo='label+percent'
            )])
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=380,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # Core Asset Baseline Comparison Plotting
        st.markdown("---")
        st.subheader("📈 Normalized 1-Year Baseline Reference Matrix")
        
        normalized_chart = go.Figure()
        for ticker in price_matrix.columns:
            series = price_matrix[ticker].dropna()
            normalized_vals = ((series / series.iloc[0]) - 1) * 100
            normalized_chart.add_trace(go.Scatter(
                x=series.index, y=normalized_vals, mode='lines', name=ticker, line=dict(width=2)
            ))
        normalized_chart.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10), height=350, hovermode="x unified"
        )
        st.plotly_chart(normalized_chart, use_container_width=True)
