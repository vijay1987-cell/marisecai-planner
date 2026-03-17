import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG & E2E THEME ---
st.set_page_config(page_title="MarisecAI | Training Strategy", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; color: #333; }
    hr, .stDivider { display: none !important; }
    .config-card { background: #ffffff; border: 1px solid #dfe3e8; border-radius: 4px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #005bb7 !important; font-family: 'Segoe UI', sans-serif; }
    .price-text { font-size: 2.2rem; font-weight: 700; color: #0066cc; }
    .reco-badge { background-color: #e7f3ff; color: #005bb7; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; }
    div.stButton > button:first-child { background-color: #0066cc; color: white; border-radius: 4px; font-weight: 600; height: 3.5rem; width: 100%; border: none; }
    .stDownloadButton>button { background: transparent; border: 1px solid #0066cc; color: #0066cc; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks", "url_acq": "https://www.nvidia.com/en-in/data-center/dgx-b200/", "url_rent": "https://www.e2enetworks.com/gpus/nvidia-b200"},
    "NVIDIA H200 (SXM)": {"tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks", "url_acq": "https://www.nvidia.com/en-in/data-center/h200/", "url_rent": "https://www.e2enetworks.com/gpu-cloud"},
    "NVIDIA A100 (80GB)": {"tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock", "url_acq": "https://www.indiamart.com/proddetail/nvidia-a100-tensor-core-gpu-card-80gb-2855180993955.html", "url_rent": "https://www.cantech.in/gpu-servers/rent-a100-gpu"}
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
        
        # Expert Mode: Only shows if a specific GPU is selected
        if hw_sel != "🔍 Auto-Select (Recommend for me)":
            llm_type = st.selectbox("Language Model Type", list(LLM_MAP.keys()))
            quant = st.radio("Quantization Type", list(Q_MAP.keys()), horizontal=True)
        else:
            llm_type = "Standard CNN/ViT"
            quant = "FP16 (Full)"

    st.write("")
    run_calc = st.button("View Training Strategy")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CALCULATION LOGIC ---
def get_recommendation(target_gb, target_hrs):
    for model, specs in reversed(list(HW_DB.items())):
        needed = math.ceil(target_gb / (specs['tp'] * target_hrs))
        if needed <= 8: return model
    return "NVIDIA B200 (SXM)"

if hw_sel == "🔍 Auto-Select (Recommend for me)":
    final_hw = get_recommendation(data_gb, total_hrs)
    status_label = "RECOMMENDED HARDWARE"
    is_auto = True
else:
    final_hw = hw_sel
    status_label = f"COST COMPARISON: {final_hw}"
    is_auto = False

info = HW_DB[final_hw]
eff_tp = info["tp"] * Q_MAP[quant] * LLM_MAP[llm_type]
n_nodes = math.ceil(data_gb / (eff_tp * total_hrs))
cost_rent = n_nodes * info["rent"] * total_hrs
cost_acq = n_nodes * info["acq"]

# --- 5. RESULTS & VALUE PROPOSITION ---
st.markdown(f"### {status_label}")

v1, v2 = st.columns(2)
with v1:
    st.markdown(f"""
    <div class="config-card">
        <p class="label-sub">Option A: Renting (OpEx)</p>
        <div class="price-text">₹{cost_rent:,.0f}</div>
        <p>Monthly Flexible billing via Cloud. Data Residency: India.</p>
        <a href="{info['url_rent']}" target="_blank" style="color:#0066cc; text-decoration:none; font-weight:600;">🔗 Check Rental Availability</a>
    </div>
    """, unsafe_allow_html=True)
    
    with st.popover("📂 View Calculation Logic"):
        st.latex(r"N_{nodes} = \lceil \frac{Data_{GB}}{Throughput_{eff} \times Time} \rceil")
        st.info(f"Throughput: {eff_tp:.2f} GB/hr | Required: {n_nodes} Nodes")
        st.success(f"Cost: {n_nodes} nodes × ₹{info['rent']} × {total_hrs} hrs = ₹{cost_rent:,.0f}")

with v2:
    st.markdown(f"""
    <div class="config-card">
        <p class="label-sub">Option B: Acquisition (CapEx)</p>
        <div class="price-text">₹{cost_acq:,.0f}</div>
        <p><b>Status:</b> {info['lead']} Delivery</p>
        <a href="{info['url_acq']}" target="_blank" style="color:#0066cc; text-decoration:none; font-weight:600;">🔗 Check Purchase Lead Time</a>
    </div>
    """, unsafe_allow_html=True)

# --- 6. PROCUREMENT ---
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown("### Final Deployment RFQ")
rfq_mode = st.radio("Selected Strategy:", ["Rental Request", "Acquisition Request"], horizontal=True)

if rfq_mode == "Rental Request":
    rfq = f"Subject: RFQ - Cloud Instance ({final_hw})\nNodes: {n_nodes}\nDuration: {total_hrs} hrs\nSovereign Terms: Indian DC Data Residency required."
else:
    rfq = f"Subject: Purchase RFQ - {n_nodes}x {final_hw}\nLead Time: Relative to {info['lead']} estimate.\nDelivery: Bangalore HQ."

st.text_area("Preview", rfq, height=100)
st.download_button("Export Procurement Plan", rfq, file_name="MarisecAI_RFQ.txt")
st.markdown('</div>', unsafe_allow_html=True)
