import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG & E2E THEME ---
st.set_page_config(page_title="MarisecAI | Hardware Consultant", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; color: #333; }
    hr, .stDivider { display: none !important; }
    .config-card { background: #ffffff; border: 1px solid #dfe3e8; border-radius: 4px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #005bb7 !important; font-family: 'Segoe UI', sans-serif; }
    .price-text { font-size: 2.2rem; font-weight: 700; color: #0066cc; }
    .reco-badge { background-color: #e7f3ff; color: #005bb7; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; }
    div.stButton > button:first-child { background-color: #0066cc; color: white; border-radius: 4px; font-weight: 600; height: 3.5rem; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE HARDWARE KNOWLEDGE BASE ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks", "tier": "Ultra-High Performance"},
    "NVIDIA H200 (SXM)": {"tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks", "tier": "Enterprise Standard"},
    "NVIDIA A100 (80GB)": {"tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock", "tier": "Value/Inference"}
}

# --- 3. INPUTS ---
st.title("Project Infrastructure Configurator")

with st.container():
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    
    with c1:
        data_val = st.number_input("Dataset Volume", min_value=1.0, value=10.0)
        unit = st.selectbox("Unit", ["TB", "GB"])
        data_gb = data_val * 1024 if unit == "TB" else data_val
        
    with c2:
        time_val = st.number_input("Processing Window", min_value=1.0, value=72.0)
        t_unit = st.selectbox("Timeline", ["Hours", "Days", "Weeks"])
        total_hrs = time_val * {"Hours": 1, "Days": 24, "Weeks": 168}[t_unit]
        
    with c3:
        # Added "" as a blank option for recommendation
        hw_options = ["🔍 Auto-Select (Recommend for me)"] + list(HW_DB.keys())
        hw_sel = st.selectbox("GPU Accelerator Model", hw_options)
        arch = st.selectbox("Optimization Profile", ["VTS MoE (0.85x)", "Standard (1.0x)"])

    st.write("")
    run_calc = st.button("Generate Strategy & Recommend Hardware")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. THE RECOMMENDATION ENGINE ---
def recommend_gpu(target_gb, target_hrs):
    # Rule: Find the cheapest GPU that can finish the job with <= 8 nodes
    best_fit = "NVIDIA A100 (80GB)" # Default
    for model, specs in reversed(list(HW_DB.items())):
        needed = math.ceil(target_gb / (specs['tp'] * target_hrs))
        if needed <= 8:
            best_fit = model
    return best_fit

if hw_sel == "🔍 Auto-Select (Recommend for me)":
    final_hw = recommend_gpu(data_gb, total_hrs)
    is_reco = True
else:
    final_hw = hw_sel
    is_reco = False

# --- 5. CALCULATIONS ---
info = HW_DB[final_hw]
eff_tp = info["tp"] * (0.85 if "VTS" in arch else 1.0)
n_nodes = math.ceil(data_gb / (eff_tp * total_hrs))
cost_rent = n_nodes * info["rent"] * total_hrs
cost_acq = n_nodes * info["acq"]

# --- 6. VALUE PROPOSITION SECTION ---
st.markdown(f"### Strategy for {final_hw} " + ('<span class="reco-badge">RECOMMENDED</span>' if is_reco else ""), unsafe_allow_html=True)

v1, v2 = st.columns(2)
with v1:
    st.markdown(f"""
    <div class="config-card">
        <p class="label-sub">Option A: Cloud Rental (OpEx)</p>
        <div class="price-text">₹{cost_rent:,.0f}</div>
        <p><b>Pay-as-you-go:</b> No upfront cost. Includes power and 24/7 IST support.</p>
        <p style="color:#666; font-size:0.8rem">Break-even vs Buying: {(cost_acq/cost_rent):.1f} similar projects.</p>
    </div>
    """, unsafe_allow_html=True)

with v2:
    st.markdown(f"""
    <div class="config-card">
        <p class="label-sub">Option B: Direct Acquisition (CapEx)</p>
        <div class="price-text">₹{cost_acq:,.0f}</div>
        <p><b>Lead Time:</b> {info['lead']}</p>
        <p><b>TCO:</b> Own the asset for 3-5 years. Best for 24/7 sustained workloads.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 7. PROCUREMENT RFQ ---
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown("### Deployment Plan")
mode = st.radio("Selected Path:", ["Rent Hardware", "Purchase Hardware"], horizontal=True)

if mode == "Rent Hardware":
    rfq = f"Request: {n_nodes}x {final_hw}\nDuration: {total_hrs} hrs\nNote: MeitY empanelled Indian DC required for MarisecAI data."
else:
    rfq = f"Purchase: {n_nodes}x {final_hw}\nDelivery: Bangalore HQ\nNote: Please confirm stock status relative to {info['lead']} lead time."

st.text_area("Final RFQ Draft", rfq, height=100)
st.download_button("Export Deployment Plan", rfq, file_name="MarisecAI_Strategy.txt")
st.markdown('</div>', unsafe_allow_html=True)
