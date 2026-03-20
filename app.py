import streamlit as st

# 1. Konfiguration
st.set_page_config(page_title="Diastolisk Dysfunktion", layout="centered")

# 2. CSS för total döljning av branding och optimerad mobilvy
st.markdown("""
    <style>
        /* Döljer header, footer och menyer helt */
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        
        /* Tar bort Streamlit-logotyper och statusikoner */
        .stAppDeployButton {display: none !important;}
        div[data-testid="stStatusWidget"] {display: none !important;}
        div[data-testid="stToolbar"] {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}

        /* Renodlad titel utan emoji för Pixel 10 */
        .main-title {
            font-size: 24px !important;
            font-weight: bold;
            margin-top: -65px; 
            padding-bottom: 15px;
            color: #1E1E1E;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    </style>
    <div class="main-title">Diastolisk Dysfunktion</div>
""", unsafe_allow_html=True)

# --- 3. EACVI DIASTOLISK GRADERING ---
st.subheader("EACVI gradering")
with st.container():
    c1, c2 = st.columns(2)
    ef = c1.number_input("LVEF (%)", 10, 85, 55)
    lavi = c2.number_input("LAVI (ml/m²)", 10, 80, 28)
    
    col1, col2, col3 = st.columns(3)
    e_vel = col1.number_input("E (m/s)", 0.20, 2.00, 0.80)
    e_prime = col2.number_input("e' avg (cm/s)", 2, 25, 9)
    tr_vmax = col3.number_input("TR Vmax (m/s)", 1.50, 4.50, 2.40)
    
    e_ep = (e_vel * 100) / e_prime if e_prime > 0 else 0

    def analyze_diastology():
        if ef >= 50:
            pts = sum([e_ep > 14, e_prime < 9, tr_vmax > 2.8, lavi > 34])
            if pts <= 1: return "Normal diastolisk funktion", "success"
            if pts == 2: return "Indeterminerad", "warning"
            return "Diastolisk dysfunktion", "error"
        else:
            if (e_vel / 0.8) <= 0.5: return "Grad I DD (Normalt LAP)", "info"
            pts = sum([e_ep > 14, tr_vmax > 2.8, lavi > 34])
            return ("Grad II DD (Högt LAP)" if pts >= 2 else "Grad I DD"), "error"

    res, status = analyze_diastology()
    if status == "success": st.success(f"**EACVI:** {res}")
    elif status == "warning": st.warning(f"**EACVI:** {res}")
    else: st.error(f"**EACVI:** {res}")
    st.caption(f"Beräknad E/e': {e_ep:.1f}")

st.divider()

# --- 4. KLINISKA PARAMETRAR ---
with st.expander("👤 Kliniska Parametrar & BMI", expanded=True):
    col_k1, col_k2 = st.columns(2)
    age = col_k1.number_input("Ålder", 18, 100, 65)
    
    h_cm = st.number_input("Längd (cm)", 100, 220, 175)
    w_kg = st.number_input("Vikt (kg)", 30, 250, 80)
    bmi = w_kg / ((h_cm/100)**2)
    st.caption(f"Beräknat BMI: {bmi:.1f} kg/m²")
    
    ck1, ck2 = st.columns(2)
    afib = ck1.checkbox("Afib")
    htn = ck2.checkbox("HTN (≥2 läk)")

st.divider()

# --- 5. SCORES ---
tab1, tab2 = st.tabs(["HFA-PEFF", "H2FPEF"])

with tab1:
    st.subheader("HFA-PEFF (Step 2)")
    major, minor = [], []
    if e_ep >= 15: major.append("E/e' ≥ 15 (2p)")
    elif 9 <= e_ep <= 14: minor.append("E/e' 9-14 (1p)")
    if tr_vmax > 2.8: major.append("TR Vmax > 2.8 (2p)")
    
    lavi_limit = 40 if afib else 34
    if lavi > lavi_limit: major.append(f"LAVI > {lavi_limit} (2p)")
    elif lavi >= 29: minor.append("LAVI 29-34 (1p)")

    for m in major: st.write(f"✅ {m}")
    for n in minor: st.write(f"🔸 {n}")
    
    bnp_stat = st.selectbox("NT-proBNP", ["Normal", "Minor (1p)", "Major (2p)"])
    h_total = (len(major) * 2) + len(minor)
    if bnp_stat == "Minor (1p)": h_total += 1
    elif bnp_stat == "Major (2p)": h_total += 2

    if h_total >= 5: st.error(f"Score: {h_total} p - HFpEF Bekräftad")
    elif h_total >= 2: st.warning(f"Score: {h_total} p - Intermediär")
    else: st.success(f"Score: {h_total} p - HFpEF Osannolikt")

with tab2:
    st.subheader("H2FPEF Score")
    h2_pts = 0
    if bmi > 30: h2_pts += 2
    if htn: h2_pts += 1
    if afib: h2_pts += 3
    if tr_vmax > 2.8: h2_pts += 1
    if age > 60: h2_pts += 1
    if e_ep > 9: h2_pts += 1
    
    p_map = {0:4, 1:12, 2:29, 3:54, 4:77, 5:90, 6:96, 7:98, 8:99}
    prob = p_map.get(h2_pts, 99)
    
    if h2_pts >= 6: st.error(f"Score: {h2_pts} - {prob}% Sannolikhet")
    elif h2_pts >= 2: st.warning(f"Score: {h2_pts} - {prob}% Sannolikhet")
    else: st.success(f"Score: {h2_pts} - {prob}% Sannolikhet")
    st.progress(min(h2_pts / 9, 1.0))

st.divider()

# --- 6. RESET ---
if st.button("🔄"):
    st.rerun()
