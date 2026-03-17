import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG & E2E THEME ---
st.set_page_config(page_title="MarisecAI | NVIDIA GPU Consultant", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; color: #333; }
    hr, .stDivider { display: none !important; }
    .config-card { background: #ffffff; border: 1px solid #dfe3e8; border-radius: 4px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #005bb7 !important; font-family: 'Segoe UI', sans-serif; }
    .price-text { font-size: 2rem; font-weight: 700; color: #0066cc; }
    .reco-badge { background-color: #e7f3ff; color: #005bb7; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; margin-left: 10px; }
    div.stButton > button:first-child { background-color: #0066cc; color: white; border-radius: 4px; font-weight: 600; height: 3.5rem; width: 100%; border: none; }
    .label-sub { color: #666; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. EXPANDED NVIDIA ACTIVE SUPPORT DATABASE ---
# Sorted roughly from lowest performance to highest
HW_DB = {
    "NVIDIA L4 (24GB)": {"tp": 15, "acq": 250000, "rent": 45, "lead": "Ready Stock", "url_acq": "https://www.nvidia.com/en-us/data-center/l4/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-l4"},
    "NVIDIA A40 (48GB)": {"tp": 30, "acq": 900000, "rent": 85, "lead": "Ready Stock", "url_acq": "https://www.nvidia.com/en-in/design-visualization/rtx-a40/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-a40"},
    "NVIDIA L40S (48GB)": {"tp": 45, "acq": 1200000, "rent": 110, "lead": "2-4 Weeks", "url_acq": "https://www.nvidia.com/en-us/data-center/l40s/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-l40s"},
    "NVIDIA A100 (80GB)": {"tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock", "url_acq": "https://www.nvidia.com/en-in/data-center/a100/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-a100-80gb"},
    "NVIDIA H100 (80GB)": {"tp": 80, "acq": 3200000, "rent": 240, "lead": "8-12 Weeks", "url_acq": "https://www.nvidia.com/en-in/data-center/h100/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-h100-80gb"},
    "NVIDIA H200 (SXM)": {"tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks", "url_acq": "https://www.nvidia.com/en-in/data-center/h200/", "url_rent": "https://www.e2enetworks.com/gpu-cloud"},
    "NVIDIA B200 (SXM)": {"tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks", "url_acq": "https://www.nvidia.com/en-in/data-center/dgx-b200/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-b200"}
}

LLM_MAP = {"MoE (Mixture of Experts)": 0.85, "Dense Transformer": 0.70, "Standard CNN/ViT": 1.0, "Lightweight (YOLO/Distil)": 1.5}
Q_MAP = {"FP16 (Full)": 1.0, "INT8 (Quantized)": 1.3, "FP8 (Optimized)": 1.6}

# --- 3. INPUT SECTION ---
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
        total_hrs = time_val * {"Hours": 1, "Days": 24, "Weeks": 168}[st.selectbox("Timeline", ["Hours", "Days", "Weeks"])]
        
    with c3:
        hw_sel = st.selectbox("GPU Accelerator Model", ["🔍 Auto-Select (Recommend for me)"] + list(HW_DB.keys()))
        
        # Selection Logic
        if hw_sel != "🔍 Auto-Select (Recommend for me)":
            llm_type = st.selectbox("Language Model Type", list(LLM_MAP.keys()))
            quant = st.radio("Quantization Type", list(Q_MAP.keys()), horizontal=True)
        else:
            llm_type = "Standard CNN/ViT"
            quant = "FP16 (Full)"

    st.write("")
    if st.button("View Training Strategy"):
        st.session_state.run = True
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. MULTI-HARDWARE RESULTS ---
if 'run' in st.session_state:
    if hw_sel == "🔍 Auto-Select (Recommend for me)":
        # Strategy: Show all models that can do it with <= 32 nodes
        display_list = []
        for model, specs in HW_DB.items():
            eff_tp_check = specs["tp"] * Q_MAP[quant] * LLM_MAP[llm_type]
            needed = math.ceil(data_gb / (eff_tp_check * total_hrs))
            if needed <= 32: display_list.append(model)
        status_header = "Recommended Hardware Options"
    else:
        display_list = [hw_sel]
        status_header = f"Strategy Comparison: {hw_sel}"

    st.markdown(f"### {status_header}")
    
    if not display_list:
        st.error("No hardware meets this timeframe within realistic node counts. Please increase processing window.")
    
    for model in display_list:
        info = HW_DB[model]
        eff_tp = info["tp"] * Q_MAP[quant] * LLM_MAP[llm_type]
        n_nodes = math.ceil(data_gb / (eff_tp * total_hrs))
        cost_rent = n_nodes * info["rent"] * total_hrs
        cost_acq = n_nodes * info["acq"]

        st.markdown(f'<div style="background:rgba(0,102,204,0.05); padding:10px; border-radius:4px; margin-bottom:10px;"><b>Model: {model}</b></div>', unsafe_allow_html=True)
        v1, v2 = st.columns(2)
        
        with v1:
            st.markdown(f"""
            <div class="config-card">
                <p class="label-sub">Option A: Renting (OpEx)</p>
                <div class="price-text">₹{cost_rent:,.0f}</div>
                <p>Requirement: <b>{n_nodes} Nodes</b></p>
                <a href="{info['url_rent']}" target="_blank" style="color:#0066cc; text-decoration:none; font-weight:600;">🔗 Sourcing & Rental Info</a>
            </div>
            """, unsafe_allow_html=True)
            
            with st.popover(f"📂 Calculation Logic ({model})"):
                st.latex(r"N_{nodes} = \lceil \frac{Data_{GB}}{Throughput_{eff} \times Time_{hrs}} \rceil")
                st.write(f"Effective Throughput: **{eff_tp:.2f} GB/hr**")
                st.success(f"Final Cost: {n_nodes} nodes × ₹{info['rent']} × {total_hrs} hrs = ₹{cost_rent:,.0f}")

        with v2:
            st.markdown(f"""
            <div class="config-card">
                <p class="label-sub">Option B: Acquisition (CapEx)</p>
                <div class="price-text">₹{cost_acq:,.0f}</div>
                <p>Est. Lead Time: <b>{info['lead']}</b></p>
                <a href="{info['url_acq']}" target="_blank" style="color:#0066cc; text-decoration:none; font-weight:600;">🔗 Direct Purchase Leads</a>
            </div>
            """, unsafe_allow_html=True)
