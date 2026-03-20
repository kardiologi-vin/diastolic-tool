import streamlit as st

# Konfiguration för mobil optimering
st.set_page_config(page_title="Diastolic Dysfunction CDS", layout="centered")

st.title("🫀 Diastolic Dysfunction CDS")

# --- GEMENSAMMA INPUTS ---
with st.sidebar:
    st.header("Kliniska Parametrar")
    age = st.number_input("Ålder", 18, 100, 65)
    bmi = st.number_input("BMI (kg/m²)", 15, 60, 27)
    afib = st.checkbox("Förmaksflimmer (Afib)")
    htn = st.checkbox("Hypertoni (≥2 läkemedel)")

# Flikar för diagnostiska ramverk
tab1, tab2, tab3 = st.tabs(["EACVI 2016", "HFA-PEFF", "H2FPEF"])

# --- TAB 1: EACVI 2016 ---
with tab1:
    st.subheader("EACVI Diastolisk Gradering")
    c1, c2 = st.columns(2)
    ef = c1.number_input("LVEF (%)", 10, 85, 55)
    lavi = c2.number_input("LAVI (ml/m²)", 10, 80, 28)
    
    col1, col2, col3 = st.columns(3)
    e_vel = col1.number_input("E (m/s)", 0.2, 2.0, 0.8)
    e_prime = col2.number_input("e' avg (cm/s)", 2, 25, 9)
    tr_vmax = col3.number_input("TR Vmax (m/s)", 1.5, 4.5, 2.4)
    
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
    if status == "success": st.success(f"**Slutsats:** {res}")
    elif status == "warning": st.warning(f"**Slutsats:** {res}")
    else: st.error(f"**Slutsats:** {res}")
    st.caption(f"E/e': {e_ep:.1f}")

# --- TAB 2: HFA-PEFF ---
with tab2:
    st.subheader("HFA-PEFF Score (Step 2)")
    
    hfa_points = 0
    major_criteria = []
    minor_criteria = []
    
    # Automatisk logik baserad på Tab 1
    if e_ep >= 15: major_criteria.append("E/e' ≥ 15 (2p)")
    elif 9 <= e_ep <= 14: minor_criteria.append("E/e' 9-14 (1p)")
    
    if tr_vmax > 2.8: major_criteria.append("TR Vmax > 2.8 (2p)")
    
    lavi_limit_major = 40 if afib else 34
    lavi_limit_minor = 29 # Förenklat gränsvärde
    
    if lavi > lavi_limit_major: major_criteria.append(f"LAVI > {lavi_limit_major} (2p)")
    elif lavi >= lavi_limit_minor: minor_criteria.append(f"LAVI {lavi_limit_minor}-{lavi_limit_major} (1p)")

    for c in major_criteria: st.write(f"✅ {c}")
    for c in minor_criteria: st.write(f"🔸 {c}")

    bnp = st.selectbox("NT-proBNP", ["Normal", "Minor (1p)", "Major (2p)"])
    
    hfa_total = (len(major_criteria) * 2) + len(minor_criteria)
    if bnp == "Minor (1p)": hfa_total += 1
    elif bnp == "Major (2p)": hfa_total += 2

    st.metric("Total HFA-PEFF", f"{hfa_total} p")
    if hfa_total >= 5: st.error("HFpEF Bekräftad")
    elif hfa_total >= 2: st.warning("Intermediär (Kräver Stress-Eko/Invasiv)")
    else: st.success("HFpEF Osannolikt")

# --- TAB 3: H2FPEF ---
with tab3:
    st.subheader("H2FPEF Score")
    
    h2_pts = 0
    if bmi > 30: h2_pts += 2
    if htn: h2_pts += 1
    if afib: h2_pts += 3
    if tr_vmax > 2.8: h2_pts += 1
    if age > 60: h2_pts += 1
    if e_ep > 9: h2_pts += 1
    
    prob_map = {0: 4, 1: 12, 2: 29, 3: 54, 4: 77, 5: 90, 6: 96, 7: 98, 8: 99, 9: 99}
    prob = prob_map.get(h2_pts, 99)
    
    st.metric("H2FPEF Score", h2_pts, f"{prob}% Sannolikhet")
    st.progress(h2_pts / 9)
