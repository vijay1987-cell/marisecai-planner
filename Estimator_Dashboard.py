import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="MarisecAI | Infrastructure Configurator", layout="wide")

# --- 2. E2E NETWORKS STYLE CSS ---
st.markdown("""
    <style>
    /* Professional White/Light Gray Theme */
    .stApp { background-color: #f8f9fa; color: #212529; }
    
    /* Clean Sidebar-style Sectioning */
    .config-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Typography */
    h1, h2, h3 { color: #0056b3 !important; font-family: 'Inter', sans-serif; }
    .label-text { font-weight: 600; color: #495057; margin-bottom: 8px; }
    
    /* E2E Style Blue Button */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 4px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 2rem;
        width: 100%;
    }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    
    /* Price Highlight Box */
    .price-box {
        background-color: #e7f3ff;
        border: 1px solid #b3d7ff;
        border-radius: 6px;
        padding: 15px;
        text-align: center;
    }
    .price-value { font-size: 2rem; font-weight: 700; color: #0056b3; }
    
    /* Remove white space at top */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INFRASTRUCTURE DATA ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks", "link": "https://www.e2enetworks.com/gpus/nvidia-b200"},
    "NVIDIA H200 (SXM)": {"tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks", "link": "https://www.e2enetworks.com/gpu-cloud"},
    "NVIDIA A100 (80GB)": {"tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock", "link": "https://www.e2enetworks.com/gpus/nvidia-a100-80gb"}
}

# --- 4. HEADER ---
st.image("https://www.e2enetworks.com/e2e-logo.svg", width=150) # Placeholder for logo
st.title("Project Infrastructure Configurator")
st.markdown("Configure your AI workload requirements to determine the optimal cluster size and procurement strategy.")

# --- 5. CONFIGURATOR LAYOUT ---
col_main, col_summary = st.columns([2, 1])

with col_main:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### 1. Workload Parameters")
    
    c1, c2 = st.columns(2)
    with c1:
        data_val = st.number_input("Dataset Volume", min_value=1.0, value=10.0)
        d_unit = st.selectbox("Volume Unit", ["TB", "GB"])
        data_gb = data_val * 1024 if d_unit == "TB" else data_val
    with c2:
        time_val = st.number_input("Processing Timeline", min_value=1.0, value=72.0)
        t_unit = st.selectbox("Timeline Unit", ["Hours", "Days", "Weeks"])
        h_map = {"Hours": 1, "Days": 24, "Weeks": 168}
        total_hrs = time_val * h_map[t_unit]

    st.markdown("---")
    st.markdown("### 2. Compute Selection")
    c3, c4 = st.columns(2)
    with c3:
        hw_sel = st.selectbox("GPU Accelerator Model", list(HW_DB.keys()))
        arch = st.selectbox("Architecture Optimization", ["VTS MoE (0.85x)", "Standard (1.0x)", "Dense (0.6x)"])
    with c4:
        prec = st.radio("Precision Level", ["FP16", "INT8", "FP8"], horizontal=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CALCULATION LOGIC ---
info = HW_DB[hw_sel]
p_map = {"FP16": 1.0, "INT8": 1.3, "FP8": 1.6}
a_map = {"VTS MoE (0.85x)": 0.85, "Standard (1.0x)": 1.0, "Dense (0.6x)": 0.6}
eff_tp = info["tp"] * p_map[prec] * a_map[arch]
n_nodes = math.ceil(data_gb / (eff_tp * total_hrs))

cost_rent = n_nodes * info["rent"] * total_hrs
cost_acq = n_nodes * info["acq"]

# --- 7. SUMMARY SIDEBAR ---
with col_summary:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### Configuration Summary")
    
    st.markdown(f"**Nodes Required:** {n_nodes}x {hw_sel}")
    st.markdown(f"**Total Hours:** {total_hrs:.0f} hrs")
    
    st.markdown("---")
    st.markdown('<div class="price-box">', unsafe_allow_html=True)
    st.markdown("Estimated Hourly Price")
    st.markdown(f'<div class="price-value">₹{n_nodes * info["rent"]}/hr</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"**Total OpEx:** ₹{cost_rent:,.0f}")
    st.markdown(f"**Total CapEx:** ₹{cost_acq:,.0f}")
    st.markdown(f"**Lead Time:** {info['lead']}")
    
    st.write("")
    st.markdown(f"[View Pricing Detail on E2E Networks]({info['link']})")
    st.button("Request Custom Quote")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. RFQ SECTION ---
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown("### Generate Deployment Plan")
mode = st.radio("Selection Strategy:", ["Cloud Rental (OpEx)", "Direct Purchase (CapEx)"], horizontal=True)

if mode == "Cloud Rental (OpEx)":
    rfq_text = f"E2E Networks Cloud Quote Request\n\nResource: {n_nodes}x {hw_sel}\nTimeline: {total_hrs} Hours\nCompliance: MeitY empanelled cloud required."
else:
    rfq_text = f"Hardware Procurement RFQ\n\nAsset: {n_nodes}x {hw_sel}\nTarget Delivery: Bangalore HQ\nLead Time: Relative to {info['lead']} estimate."

st.text_area("Final RFQ Draft", rfq_text, height=120)
st.download_button("Download RFQ PDF", rfq_text, file_name="E2E_Style_RFQ.txt")
st.markdown('</div>', unsafe_allow_html=True)
