import streamlit as st

# Optimering för mobil/inbäddning
st.set_page_config(page_title="EACVI Diastolic Tool", layout="centered")

st.markdown("### 🫀 EACVI Diastolisk Gradering")

# --- DATA-INPUT ---
with st.container():
    c1, c2 = st.columns(2)
    ef = c1.number_input("LVEF (%)", 10, 85, 55, help="Från EchoNet på USB")
    lavi = c2.number_input("LAVI (ml/m²)", 10, 80, 28, help="Från CoTr på USB")

st.divider()

# Doppler-värden (Manuella)
col1, col2, col3 = st.columns(3)
e_vel = col1.number_input("E (m/s)", 0.2, 2.0, 0.8)
a_vel = col2.number_input("A (m/s)", 0.2, 2.0, 0.7)
e_prime = col3.number_input("e' avg (cm/s)", 2, 25, 9)
tr_vmax = st.slider("TR Vmax (m/s)", 1.5, 4.5, 2.4)

# --- ALGORITM ---
e_ep = (e_vel * 100) / e_prime if e_prime > 0 else 0
e_a = e_vel / a_vel if a_vel > 0 else 0

def analyze():
    if ef >= 50: # Normal EF Pathway
        pts = sum([e_ep > 14, e_prime < 9, tr_vmax > 2.8, lavi > 34])
        if pts <= 1: return "Normal", "success"
        if pts == 2: return "Indeterminerad", "warning"
        return "Diastolisk Dysfunktion", "error"
    else: # Nedsatt EF Pathway
        if e_a <= 0.8 and e_vel <= 0.5: return "Grad I (Normalt LAP)", "info"
        if e_a >= 2.0: return "Grad III (Högt LAP)", "error"
        pts = sum([e_ep > 14, tr_vmax > 2.8, lavi > 34])
        if pts >= 2: return "Grad II (Högt LAP)", "error"
        return "Grad I (Normalt LAP)", "info"

res, status = analyze()

# --- DISPLAY ---
st.divider()
if status == "success": st.success(f"**Slutsats:** {res}")
elif status == "warning": st.warning(f"**Slutsats:** {res}")
elif status == "error": st.error(f"**Slutsats:** {res}")
else: st.info(f"**Slutsats:** {res}")

st.caption(f"Beräknad E/e': {e_ep:.1f} | E/A: {e_a:.2f}")
