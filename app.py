import streamlit as st

# Konfiguration för mobil optimering
st.set_page_config(page_title="Diastolic Dysfunction CDS", layout="centered")

st.title("🫀 Diastolic Dysfunction CDS")

# --- 1. EACVI DIASTOLISK GRADERING ---
st.subheader("EACVI Diastolisk Gradering")
with st.container():
    c1, c2 = st.columns(2)
    ef = c1.number_input("LVEF (%)", 10, 85, 55)
    lavi = c2.number_input("LAVI (ml/m²)", 10, 80, 28)
    
    col1, col2, col3 = st.columns(3)
    e_vel = col1.number_input("E (m/s)", 0.2, 2.0, 0.80)
    e_prime = col2.number_input("e' avg (cm/s)", 2, 25, 9)
    tr_vmax = col3.number_input("TR Vmax (m/s)", 1.5, 4.5, 2.40)
    
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

# --- 2. KLINISKA PARAMETRAR (Med BMI-kalkylator) ---
with st.expander("👤 Kliniska Parametrar", expanded=True):
    col_k1, col_k2 = st.columns(2)
    age = col_k1.number_input("Ålder", 18, 100, 65)
    
    # BMI Beräkning
    height = st.number_input("Längd (cm)", 100, 220, 175)
    weight = st.number_input("Vikt (kg)", 30, 250, 80)
    bmi = weight / ((height/100)**2)
    st.caption(f"Beräknat BMI: {bmi:.1f} kg/m²")
    
    col_k3, col_k4 = st.columns(2)
    afib = col_k3.checkbox("Afib")
    htn = col_k4.checkbox("HTN (≥2 läk)")

st.divider()

# --- 3. SCORES (Flikar) ---
tab1, tab2 = st.tabs(["HFA-PEFF", "H2FPEF"])

with tab1:
    st.subheader("HFA-PEFF Score (Step 2)")
    major_criteria, minor_criteria = [], []
    
    if e_ep >= 15: major_criteria.append("E/e' ≥ 15 (2p)")
    elif 9 <= e_ep <= 14: minor_criteria.append("E/e' 9-14 (1p)")
    if tr_vmax > 2.8: major_criteria.append("TR Vmax > 2.8 (2p)")
    
    lavi_limit_major = 40 if afib else 34
    if lavi > lavi_limit_major: major_criteria.append(f"LAVI > {lavi_limit_major} (2p)")
    elif lavi >= 29: minor_criteria.append("LAVI 29-34 (1p)")

    for m in major_criteria: st.write(f"✅ {m}")
    for n in minor_criteria: st.write(f"🔸 {n}")

    bnp = st.selectbox("NT-proBNP Status", ["Normal", "Minor (1p)", "Major (2p)"])
    hfa_total = (len(major_criteria) * 2) + len(minor_criteria)
    if bnp == "Minor (1p)": hfa_total += 1
    elif bnp == "Major (2p)": hfa_total += 2

    if hfa_total >= 5: st.error(f"Score: {hfa_total} p - HFpEF Bekräftad")
    elif hfa_total >= 2: st.warning(f"Score: {hfa_total} p - Intermediär")
    else: st.success(f"Score: {hfa_total} p - HFpEF Osannolikt")

with tab2:
    st.subheader("H2FPEF Score")
    h2_pts = 0
    if bmi > 30: h2_pts += 2
    if htn: h2_pts += 1
    if afib: h2_pts += 3
    if tr_vmax > 2.8: h2_pts += 1
    if age > 60: h2_pts += 1
    if e_ep > 9: h2_pts += 1
    
    prob_map = {0: 4, 1: 12, 2: 29, 3: 54, 4: 77, 5: 90, 6: 96, 7: 98, 8: 99}
    prob = prob_map.get(h2_pts, 99)
    
    if h2_pts >= 6: st.error(f"Score: {h2_pts} - {prob}%")
    elif h2_pts >= 2: st.warning(f"Score: {h2_pts} - {prob}%")
    else: st.success(f"Score: {h2_pts} - {prob}%")
    st.progress(min(h2_pts / 9, 1.0))

st.divider()

# --- RESET (Endast Ikon) ---
if st.button("🔄"):
    st.rerun()
