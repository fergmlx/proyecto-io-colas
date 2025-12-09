"""
Interactive Streamlit Dashboard for Queue Theory Analysis
Run with: streamlit run app/dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append('..')

from src.data_processor import DataProcessor
from src.distribution_fitter import DistributionFitter
from src.queue_models import MMcQueue, QueueSimulator
from src.optimizer import CostOptimizer

# Page configuration
st.set_page_config(
    page_title="Queue Theory Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('<h1 style="text-align: center; color: #1f77b4;">🚀 Queue Theory Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Interactive M/M/c Queue Modeling and Optimization**")
st.markdown("---")

# Sidebar
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("### System Parameters")

lambda_rate = st.sidebar.number_input("Arrival Rate (λ) - requests/hour", min_value=1.0, max_value=500.0, value=120.0, step=1.0)
mu_rate = st.sidebar.number_input("Service Rate (μ) - requests/hour per server", min_value=1.0, max_value=200.0, value=30.0, step=1.0)

st.sidebar.markdown("### Cost Parameters")
cost_server = st.sidebar.number_input("Server Cost ($/hour)", min_value=1.0, max_value=1000.0, value=50.0, step=5.0)
cost_waiting = st.sidebar.number_input("Waiting Cost ($/customer)", min_value=1.0, max_value=500.0, value=20.0, step=5.0)
c_max = st.sidebar.slider("Maximum Servers to Evaluate", min_value=5, max_value=30, value=15, step=1)

c_min = int(np.ceil(lambda_rate / mu_rate)) + 1

tab1, tab2, tab3, tab4 = st.tabs(["📊 System Overview", "🔧 Queue Analysis", "💰 Cost Optimization", "📈 Sensitivity Analysis"])

with tab1:
    st.header("System Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Arrival Rate (λ)", value=f"{lambda_rate:.1f}", delta="req/hour")
    with col2:
        st.metric(label="Service Rate (μ)", value=f"{mu_rate:.1f}", delta="req/hour/server")
    with col3:
        traffic_intensity = lambda_rate / mu_rate
        st.metric(label="Traffic Intensity (λ/μ)", value=f"{traffic_intensity:.2f}", delta="customers")
    with col4:
        st.metric(label="Min Servers Needed", value=f"{c_min}", delta="for stability")

with tab2:
    st.header("M/M/c Queue Analysis")
    c_selected = st.slider("Number of Servers (c)", min_value=c_min, max_value=c_max, value=c_min + 2, step=1)
    try:
        queue = MMcQueue(lambda_rate, mu_rate, c_selected)
        metrics = queue.calculate_metrics()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Utilization (ρ)", f"{metrics['utilization_percent']:.1f}%", delta="server load")
        with col2:
            st.metric("Avg Queue Length (Lq)", f"{metrics['Lq']:.2f}", delta="customers")
        with col3:
            st.metric("Avg Wait Time (Wq)", f"{metrics['Wq']*60:.1f} min", delta="in queue")
        with col4:
            st.metric("Prob. of Waiting", f"{metrics['Pw_erlang_c']*100:.1f}%", delta="Erlang-C")
        with col5:
            st.metric("Avg System Time (W)", f"{metrics['W']*60:.1f} min", delta="total time")
    except ValueError as e:
        st.error(f"❌ Invalid configuration: {e}")

with tab3:
    st.header("Cost Optimization")
    if st.button("🔍 Find Optimal Configuration", type="primary"):
        with st.spinner("Running optimization..."):
            optimizer = CostOptimizer(lambda_rate, mu_rate, cost_server, cost_waiting)
            result = optimizer.optimize(c_min=c_min, c_max=c_max)
            if result['success']:
                st.success("✅ Optimization Complete!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Optimal Servers (c*)", f"{result['optimal_c']}", delta="servers")
                with col2:
                    st.metric("Total Cost", f"${result['total_cost']:.2f}", delta="per hour")
                with col3:
                    st.metric("Avg Wait Time", f"{result['metrics']['Wq']*60:.1f} min", delta="in queue")

with tab4:
    st.header("Sensitivity Analysis")
    st.markdown("Analyze how system performance changes with different parameters.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p>📚 Queue Theory Dashboard | Built with Streamlit</p></div>", unsafe_allow_html=True)
