import streamlit as st
import pandas as pd
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="MarisecAI Master Planner", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #020024 0%, #08084b 35%, #001233 100%); color: white; }
    .stApp { background: transparent; }
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    div.stButton > button:first-child {
        background-color: #00d4ff; color: #001233; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASES & LEAD TIMES ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp_gb_hr": 210, "acq": 5200000, "rent": 450, "vram": 192, "lead": "32-40 Weeks (Global Shortage)"},
    "NVIDIA H200 (SXM)": {"tp_gb_hr": 125, "acq": 3800000, "rent": 320, "vram": 141, "lead": "12-16 Weeks (Stable)"},
    "NVIDIA A100 (80GB)": {"tp_gb_hr": 60, "acq": 1800000, "rent": 195, "vram": 80, "lead": "Ready Stock / 2 Weeks"}
}
ARCH_COMPLEXITY = {"VTS (Maritime Signal MoE)": 0.85, "Standard (ViT/YOLO)": 1.0, "Simple (CNN/Linear)": 1.5, "Dense (Transformer/LLM)": 0.6}

# --- 1. SELECTION SECTION ---
st.title("🚢 MarisecAI Master Infrastructure Planner")

with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    with c1:
        data_val = st.number_input("Data Size", min_value=1.0, value=1.0)
        unit = st.radio("Data Unit", ["TB", "GB"], horizontal=True)
        data_gb = data_val * 1024 if unit == "TB" else data_val
    with c2:
        time_val = st.number_input("Time Target", min_value=1.0, value=48.0)
        t_unit = st.radio("Time Unit", ["Hrs", "Days", "Months"], horizontal=True)
        hours_map = {"Hrs": 1, "Days": 24, "Months": 720}
        total_hours = time_val * hours_map[t_unit]
    with c3:
        arch = st.selectbox("Architecture Type", list(ARCH_COMPLEXITY.keys()), index=0)
        prec = st.selectbox("Precision (Quantization)", ["4-bit", "8-bit", "16-bit"], index=1)
        hw_choice = st.selectbox("Target Hardware", list(HW_DB.keys()), index=0)
    
    # Store calculations in session state to persist after RFQ clicks
    if st.button("APPLY SELECTION & GENERATE STRATEGY") or 'data_gb' not in st.session_state:
        hw = HW_DB[hw_choice]
        q_map = {"4-bit": 1.6, "8-bit": 1.3, "16-bit": 1.0}
        eff_tp = hw["tp_gb_hr"] * q_map[prec] * ARCH_COMPLEXITY[arch]
        n_gpus = math.ceil(data_gb / (eff_tp * total_hours))
        
        st.session_state.update({
            'data_gb': data_gb, 'total_hours': total_hours, 'hw_choice': hw_choice,
            'n_gpus': n_gpus, 'cost_rent': n_gpus * hw["rent"] * total_hours,
            'cost_acq': n_gpus * hw["acq"], 'eff_tp': eff_tp, 'hw_data': hw
        })
    st.markdown('</div>', unsafe_allow_html=True)

# --- 2. RESULTS ---
st.markdown("### 📊 Infrastructure Comparison")
res_c1, res_c2 = st.columns(2)

with res_c1:
    st.markdown(f'<div class="glass-card"><h4 style="color:#00d4ff">Option A: Renting</h4><h2>₹{st.session_state.cost_rent:,.0f}</h2><p>Cluster: {st.session_state.n_gpus}x GPUs</p></div>', unsafe_allow_html=True)
    with st.popover("📂 View Renting Logic"):
        st.latex(r"N_{gpus} = \lceil \frac{D_{gb}}{V_{eff} \times T} \rceil")
        st.info(f"Calc: {st.session_state.data_gb:,.0f} / ({st.session_state.eff_tp:.2f} × {st.session_state.total_hours}) = {st.session_state.n_gpus}")

with res_c2:
    st.markdown(f'<div class="glass-card"><h4 style="color:#00ffcc">Option B: Acquisition</h4><h2>₹{st.session_state.cost_acq:,.0f}</h2><p>Lead Time: <b>{st.session_state.hw_data["lead"]}</b></p></div>', unsafe_allow_html=True)
    with st.popover("📂 View Purchase Logic"):
        st.latex(r"Cost_{Acq} = N_{gpus} \times Price_{unit}")
        st.success(f"Calc: {st.session_state.n_gpus} × ₹{st.session_state.hw_data['acq']:,.0f}")

# --- 3. RFQ SECTION (Reliable Implementation) ---
st.divider()
st.markdown("### 📜 Prepare RFQ Document")
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    rfq_mode = st.radio("RFQ Strategy:", ["Buy Hardware (CapEx)", "Rent Hardware (OpEx)"], horizontal=True)
    
    if rfq_mode == "Buy Hardware (CapEx)":
        rfq_text = f"Subject: RFQ - {st.session_state.n_gpus}x {st.session_state.hw_choice}\n\nLead Time Requirement: {st.session_state.hw_data['lead']}\nStandard Terms: OEM 3-Year Platinum Warranty required. Delivery to Bangalore HQ."
    else:
        rfq_text = f"Subject: RFQ - Cloud GPU Cluster\n\nSecurity Terms: MeitY empanelled Indian Data Center required. Data residency strictly within India. No data-usage clause for training."
        
    st.text_area("Draft Preview", rfq_text, height=150)
    st.download_button("📥 Download RFQ Text", data=rfq_text, file_name="MarisecAI_RFQ.txt")
    st.markdown('</div>', unsafe_allow_html=True)
