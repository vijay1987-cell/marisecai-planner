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
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px; margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    /* Native Streamlit components for Math use standard colors, so we style the labels */
    .stMarkdown h3, .stMarkdown h4 { color: #00d4ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASES ---
HW_DB = {
    "NVIDIA B200 (SXM)": {"tp_gb_hr": 210, "acq": 5200000, "rent": 450, "vram": 192, "tdp": 1.0},
    "NVIDIA H200 (SXM)": {"tp_gb_hr": 125, "acq": 3800000, "rent": 320, "vram": 141, "tdp": 0.7},
    "NVIDIA A100 (80GB)": {"tp_gb_hr": 60, "acq": 1800000, "rent": 195, "vram": 80, "tdp": 0.4}
}

ARCH_COMPLEXITY = {
    "Simple (CNN/Linear)": 1.5,
    "Standard (ViT/YOLO)": 1.0,
    "VTS (Maritime Signal MoE)": 0.85,
    "Dense (Transformer/LLM)": 0.6,
    "Extreme (MoE/400B+)": 0.35
}

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("🚢 Global Configuration")
    data_size_tb = st.number_input("Dataset Size (TB)", min_value=0.1, value=1.0)
    data_gb = data_size_tb * 1024
    
    time_mode = st.radio("Time Constraint", ["Set a Deadline (Hrs)", "No Deadline (Use 8-GPU Node)"])
    if time_mode == "Set a Deadline (Hrs)":
        target_hrs = st.number_input("Target Hours", min_value=1, value=48)
    else:
        target_hrs = 0
    
    st.divider()
    arch_type = st.selectbox("Architecture Type", list(ARCH_COMPLEXITY.keys()))
    precision = st.selectbox("Precision (Quantization)", ["4-bit", "8-bit", "16-bit"])
    selected_hw = st.selectbox("Target Hardware", list(HW_DB.keys()))

# --- CALCULATION ENGINE ---
hw = HW_DB[selected_hw]
q_mult = {"4-bit": 1.6, "8-bit": 1.3, "16-bit": 1.0}
comp_mult = ARCH_COMPLEXITY[arch_type]
eff_tp_per_gpu = hw["tp_gb_hr"] * q_mult[precision] * comp_mult

if target_hrs > 0:
    gpus_needed = math.ceil(data_gb / (eff_tp_per_gpu * target_hrs))
    final_time = target_hrs
else:
    gpus_needed = 8 
    final_time = data_gb / (eff_tp_per_gpu * gpus_needed)

rent_total = gpus_needed * hw["rent"] * final_time
acq_total = gpus_needed * hw["acq"]

# --- MAIN UI ---
st.title("🚢 MarisecAI Master Infrastructure Planner")

tab1, tab2 = st.tabs(["📊 Estimator & Comparison", "📜 RFQ Generator"])

with tab1:
    st.subheader(f"Financial Comparison: {data_size_tb}TB via {selected_hw}")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""<div class="glass-card">
        <h3>Option A: Renting (OpEx)</h3>
        <h2 style='color:#00d4ff'>₹{rent_total:,.0f}</h2>
        <p><b>Cluster Size:</b> {gpus_needed}x GPUs</p>
        <p><b>Completion Time:</b> {final_time:.1f} Hours</p>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""<div class="glass-card">
        <h3>Option B: Acquisition (CapEx)</h3>
        <h2 style='color:#00ffcc'>₹{acq_total:,.0f}</h2>
        <p><b>Break-even:</b> {acq_total/rent_total if rent_total > 0 else 0:.1f} Cycles</p>
        <p><b>Hardware Asset:</b> {gpus_needed}x {selected_hw} Units</p>
        </div>""", unsafe_allow_html=True)

    st.divider()
    
    # --- LOGIC WIDGET (Using Native Markdown for LaTeX Reliability) ---
    with st.expander("🔍 VIEW HARDWARE & FINANCIAL CALCULATION LOGIC", expanded=True):
        st.write("### 1. Throughput & Scaling Logic")
        st.latex(r"V_{eff} = V_{base} \times Q_{mult} \times A_{complex}")
        st.write(f"**Current calculation:** {hw['tp_gb_hr']} × {q_mult[precision]} × {comp_mult} = **{eff_tp_per_gpu:.2f} GB/hr**")
        
        st.latex(r"N_{gpus} = \lceil \frac{D_{gb}}{V_{eff} \times T} \rceil")
        st.write(f"**Hardware Scaling:** {data_gb:,.0f} / ({eff_tp_per_gpu:.2f} × {final_time:.1f}) = **{gpus_needed} Units**")

        st.write("---")
        st.write("### 2. Financial Logic (Rental Arrival)")
        st.write("The rental amount is calculated based on the allocated cluster size and operational hours:")
        st.latex(r"Cost_{Rent} = N_{gpus} \times Rate_{hourly} \times T")
        
        # Show exactly how the number in the card was arrived at
        st.write(f"**Step-by-step:** {gpus_needed} GPUs × ₹{hw['rent']} × {final_time:.1f} Hours")
        st.info(f"Final Calculation: **₹{rent_total:,.0f}**")

with tab2:
    st.title("Technical Specification for RFQ")
    # RFQ Logic remains same as previous stable version
    rfq_body = f"""
    PROJECT: MARISECAI TRAINING INFRASTRUCTURE
    1. ACCELERATOR: {gpus_needed}x {selected_hw}
    2. DATA SCOPE: {data_size_tb} TB Dataset
    3. TIMELINE: {final_time:.1f} Hours
    """
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="background:white; color:black; padding:20px; border-radius:10px;"><pre>{rfq_body}</pre></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)