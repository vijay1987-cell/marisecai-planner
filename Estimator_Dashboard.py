import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="MarisecAI | Cloud Configurator", layout="wide")

# --- 2. CLEAN E2E STYLE CSS ---
st.markdown("""
    <style>
    /* Background and global text */
    .stApp { background-color: #f4f7f9; color: #333; }
    
    /* Remove default Streamlit horizontal lines (The "White Bars") */
    hr { display: none !important; }
    .stDivider { display: none !important; }
    
    /* Main Config Card */
    .config-card {
        background: #ffffff;
        border: 1px solid #dfe3e8;
        border-radius: 4px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Headings */
    h1, h2, h3 { color: #005bb7 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* E2E Specific Button */
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
        border-radius: 4px;
        font-weight: 600;
        border: none;
        height: 3rem;
        width: 100%;
    }
    div.stButton > button:hover { background-color: #004d99; border-color: #004d99; }

    /* Summary Price Box */
    .summary-box {
        background-color: #f0f7ff;
        border-left: 4px solid #0066cc;
        padding: 1.5rem;
        border-radius: 4px;
    }
    .price-text { font-size: 2.2rem; font-weight: 700; color: #0066cc; margin: 0.5rem 0; }
    
    /* Fix top spacing */
    .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks"},
    "NVIDIA H200 (SXM)": {"tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks"},
    "NVIDIA A100 (80GB)": {"tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock"}
}

# --- 4. HEADER ---
st.title("Project Infrastructure Configurator")

# --- 5. MAIN LAYOUT ---
col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### Workload Parameters")
    
    c1, c2 = st.columns(2)
    with c1:
        data_val = st.number_input("Dataset Volume", min_value=1.0, value=10.0)
        unit = st.selectbox("Unit", ["TB", "GB"])
        data_gb = data_val * 1024 if unit == "TB" else data_val
    with c2:
        time_val = st.number_input("Processing Window", min_value=1.0, value=72.0)
        t_unit = st.selectbox("Timeline", ["Hours", "Days", "Weeks"])
        total_hrs = time_val * {"Hours": 1, "Days": 24, "Weeks": 168}[t_unit]

    st.markdown("<br>### Compute Selection", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        hw_sel = st.selectbox("GPU Accelerator Model", list(HW_DB.keys()))
        arch = st.selectbox("Optimization Profile", ["VTS MoE (0.85x)", "Standard (1.0x)", "Dense (0.6x)"])
    with c4:
        prec = st.radio("Compute Precision", ["FP16", "INT8", "FP8"], horizontal=True)
    
    apply_btn = st.button("Calculate Optimal Configuration")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CALCULATIONS ---
info = HW_DB[hw_sel]
p_map = {"FP16": 1.0, "INT8": 1.3, "FP8": 1.6}
a_map = {"VTS MoE (0.85x)": 0.85, "Standard (1.0x)": 1.0, "Dense (0.6x)": 0.6}
eff_tp = info["tp"] * p_map[prec] * a_map[arch]
n_nodes = math.ceil(data_gb / (eff_tp * total_hrs))

cost_rent = n_nodes * info["rent"] * total_hrs
cost_acq = n_nodes * info["acq"]

# --- 7. SIDEBAR SUMMARY ---
with col_side:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### Deployment Summary")
    st.markdown(f"**Resource:** {n_nodes}x {hw_sel}")
    st.markdown(f"**Execution:** {total_hrs:.0f} Total Hours")
    
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.markdown("Estimated Cost")
    st.markdown(f'<div class="price-text">₹{cost_rent:,.0f}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#666; font-size:0.85rem;">Approx. ₹{n_nodes * info["rent"]}/hr</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<br>**CapEx Path:** ₹{cost_acq:,.0f}", unsafe_allow_html=True)
    st.markdown(f"**Lead Time:** {info['lead']}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. RFQ SECTION ---
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown("### Strategic Procurement")
mode = st.radio("Engagement Model:", ["Cloud Rental (OpEx)", "Direct Purchase (CapEx)"], horizontal=True)

if mode == "Cloud Rental (OpEx)":
    rfq_text = f"Request for Cloud Compute: {n_nodes}x {hw_sel}\nEstimated Duration: {total_hrs} Hours\nCompliance Requirement: MeitY empanelled Indian DC."
else:
    rfq_text = f"Purchase RFQ: {n_nodes}x {hw_sel}\nDelivery: Bangalore HQ\nLead Time Note: Relative to {info['lead']} availability."

st.text_area("Review RFQ Template", rfq_text, height=120)
st.download_button("Export as TXT", rfq_text, file_name="MarisecAI_Config.txt")
st.markdown('</div>', unsafe_allow_html=True)
