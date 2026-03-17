import streamlit as st
import pandas as pd
import math

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="MarisecAI Master Planner", layout="wide")

st.markdown("""
    <style>
    /* Deep Sea Glassmorphism Background */
    .stApp {
        background: radial-gradient(circle at top right, #001233, #000000);
        color: white;
    }

    /* Glass Card styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px) saturate(180%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }

    /* Metric & Text Styling */
    .metric-val { font-size: 2.2rem; font-weight: 800; color: #00d4ff; margin: 10px 0; }
    .roi-positive { color: #00ffcc; font-weight: bold; }
    .lead-note { color: #ffcc00; font-size: 0.85rem; }
    
    /* Vessel Preview Boxes */
    .vessel-box { 
        border-left: 3px solid #00ffcc; background: rgba(0, 255, 204, 0.05);
        padding: 15px; border-radius: 5px; margin-bottom: 10px; font-size: 0.9rem;
    }

    /* Clean UI Overrides */
    .stButton>button { width: 100%; background: #00d4ff; color: #001233; font-weight: bold; border: none; height: 3rem; }
    .stDownloadButton>button { background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASES ---
HW_INFO = {
    "NVIDIA B200 (SXM)": {
        "tp": 210, "acq": 5200000, "rent": 430, "lead": "32-40 Weeks", 
        "acq_url": "https://www.nvidia.com/en-in/data-center/dgx-b200/",
        "rent_url": "https://www.e2enetworks.com/gpus/nvidia-b200",
        "vendor": "E2E Networks (MeitY)"
    },
    "NVIDIA H200 (SXM)": {
        "tp": 125, "acq": 3800000, "rent": 300, "lead": "12-16 Weeks",
        "acq_url": "https://www.nvidia.com/en-in/data-center/h200/",
        "rent_url": "https://www.e2enetworks.com/gpu-cloud",
        "vendor": "E2E Networks / Oracle"
    },
    "NVIDIA A100 (80GB)": {
        "tp": 60, "acq": 1800000, "rent": 180, "lead": "Ready Stock (Local)",
        "acq_url": "https://www.indiamart.com/proddetail/nvidia-a100-tensor-core-gpu-card-80gb-2855180993955.html",
        "rent_url": "https://www.cantech.in/gpu-servers/rent-a100-gpu",
        "vendor": "Cantech / IndiaMART Sellers"
    }
}
ARCH_MAP = {"VTS (Maritime Signal MoE)": 0.85, "Standard (YOLO)": 1.0, "Simple": 1.5, "Dense": 0.6}
JETSON_NANO_TP = 0.5 

# --- 3. SELECTION SECTION ---
st.title("🚢 MarisecAI Master Infrastructure Strategy")

with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    with c1:
        data_val = st.number_input("Data Volume", min_value=1.0, value=10.0)
        d_unit = st.radio("Unit", ["TB", "GB"], horizontal=True)
        data_gb = data_val * 1024 if d_unit == "TB" else data_val
    with c2:
        time_val = st.number_input("Target Delivery", min_value=1.0, value=72.0)
        t_unit = st.radio("Period", ["Hrs", "Days", "Months"], horizontal=True)
        h_map = {"Hrs": 1, "Days": 24, "Months": 720}
        total_hrs = time_val * h_map[t_unit]
    with c3:
        arch = st.selectbox("Architecture Type", list(ARCH_MAP.keys()))
        prec = st.selectbox("Precision (Quantization)", ["4-bit", "8-bit", "16-bit"], index=1)
        hw_sel = st.selectbox("Target Hardware", list(HW_INFO.keys()))
    
    st.write("")
    if st.button("🔥 GENERATE UNIFIED STRATEGY & ROI"):
        st.session_state.active = True
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CALCULATION & ROI ---
if 'active' in st.session_state:
    info = HW_INFO[hw_sel]
    q_map = {"4-bit": 1.6, "8-bit": 1.3, "16-bit": 1.0}
    eff_tp = info["tp"] * q_map[prec] * ARCH_MAP[arch]
    n_gpus = math.ceil(data_gb / (eff_tp * total_hrs))
    
    cost_rent = n_gpus * info["rent"] * total_hrs
    cost_acq = n_gpus * info["acq"]
    
    nano_days = (data_gb / JETSON_NANO_TP) / 24
    cluster_days = total_hrs / 24
    v_boost = nano_days / cluster_days

    st.markdown("### 📈 Strategic ROI & Time-Velocity Advantage")
    roi1, roi2, roi3 = st.columns(3)
    with roi1:
        st.markdown(f'<div class="glass-card"><p>Jetson Nano Baseline</p><div class="metric-val">{nano_days:.1f} Days</div></div>', unsafe_allow_html=True)
    with roi2:
        st.markdown(f'<div class="glass-card"><p>{hw_sel} Cluster</p><div class="metric-val" style="color:#00ffcc">{cluster_days:.1f} Days</div><p class="roi-positive">🚀 {v_boost:.0f}x Speed Increase</p></div>', unsafe_allow_html=True)
    with roi3:
        st.markdown(f'<div class="glass-card"><p>Purchase (CapEx)</p><div class="metric-val">₹{cost_acq:,.0f}</div><p class="lead-note">⏱️ Lead: {info["lead"]}</p></div>', unsafe_allow_html=True)

    # --- 5. THE PREVIEW BUTTON ---
    st.divider()
    if st.button("👁️ SHOW VESSEL DASHBOARD PREVIEW"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🛰️ Live MoE Inference Stream (Vessel Analysis)")
        pv1, pv2, pv3 = st.columns(3)
        pv1.markdown(f'<div class="vessel-box"><b>Active Vessel:</b> MARI-EXE-01<br><b>Position:</b> Arabian Sea (Mumbai Coast)<br><b>Risk Index:</b> 0.12 (Low)</div>', unsafe_allow_html=True)
        pv2.markdown(f'<div class="vessel-box"><b>Compute Engine:</b> {hw_sel}<br><b>Throughput:</b> {eff_tp:.2f} GB/hr<br><b>Precision:</b> {prec}</div>', unsafe_allow_html=True)
        pv3.markdown(f'<div class="vessel-box"><b>MoE Routing:</b> Active<br><b>Nodes Online:</b> {n_gpus}<br><b>Status:</b> Optimizing...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 6. EXECUTION & RFQ ---
    st.markdown("### 📜 Procurement Strategy")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    mode = st.radio("RFQ Selection:", ["Buy Hardware (CapEx)", "Rent Hardware (OpEx)"], horizontal=True)
    
    if mode == "Buy Hardware (CapEx)":
        rfq_txt = f"Subject: RFQ - {n_gpus}x {hw_sel}\n\nNote: Please confirm lead time relative to estimated {info['lead']}. OEM 3-Year Warranty mandatory."
    else:
        rfq_txt = f"Subject: RFQ - Cloud Instance ({hw_sel})\n\nRequirement: MeitY empanelled provider ({info['vendor']}). Sovereign data residency required."
        
    st.text_area("Live RFQ Preview", rfq_txt, height=120)
    st.download_button("📥 Download RFQ Text", rfq_txt, "MarisecAI_RFQ.txt")
    st.markdown(f'<p><a href="{info["rent_url"]}" target="_blank" style="color:#00d4ff; text-decoration:none;">🔗 Visit {info["vendor"]} for Live Pricing</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
