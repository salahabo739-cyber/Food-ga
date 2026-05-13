import streamlit as st
import re
from datetime import datetime

st.set_page_config(
    page_title="CheeseGuard Pro",
    page_icon="🧀",
    layout="wide"
)

# ---------------- UI ----------------
st.markdown("""
<style>
.big {font-size:50px; font-weight:bold; color:#00ffcc;}
.card {padding:15px; border-radius:12px; background:#1e1e1e; margin:10px 0;}
.good {background:linear-gradient(90deg,#00c853,#64dd17); padding:15px; border-radius:12px;}
.warn {background:linear-gradient(90deg,#ffb300,#ff8f00); padding:15px; border-radius:12px;}
.bad {background:linear-gradient(90deg,#f44336,#d32f2f); padding:15px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big">🧀 CheeseGuard Pro</div>', unsafe_allow_html=True)
st.write("تحليل مكونات الجبن بطريقة ذكية")

# ---------------- DB ----------------
harmful_db = {
    "natamycin": "مضاد فطريات",
    "cellulose": "بودرة خشب / مضاد تكتل",
    "sodium phosphate": "قد يؤثر على الكلى",
    "carrageenan": "قد يسبب مشاكل هضمية",
    "msg": "منكهات صناعية",
    "artificial color": "ألوان صناعية",
    "e202": "مادة حافظة",
    "e235": "مادة حافظة"
}

# ---------------- Logic ----------------
def analyze(text):
    ingredients = [i.strip() for i in re.split(r"[;,•]", text) if i.strip()]
    
    score = 100
    warnings = []

    for ing in ingredients:
        for bad, desc in harmful_db.items():
            if bad in ing.lower():
                score -= 15
                warnings.append(f"{ing} → {desc}")

    score = max(10, score)

    if score > 75:
        status = "good"
        verdict = "ممتاز"
    elif score > 50:
        status = "warn"
        verdict = "مقبول"
    else:
        status = "bad"
        verdict = "غير جيد"

    return ingredients, score, warnings, status, verdict


# ---------------- Input ----------------
text = st.text_area("اكتب المكونات هنا")

if st.button("تحليل"):
    if not text.strip():
        st.error("اكتب مكونات الأول")
    else:
        ingredients, score, warnings, status, verdict = analyze(text)

        if status == "good":
            st.markdown(f'<div class="good">النتيجة: {verdict}</div>', unsafe_allow_html=True)
        elif status == "warn":
            st.markdown(f'<div class="warn">النتيجة: {verdict}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bad">النتيجة: {verdict}</div>', unsafe_allow_html=True)

        st.metric("Score", f"{score}/100")

        st.subheader("Warnings")
        for w in warnings:
            st.warning(w)

        st.subheader("Ingredients")
        for i in ingredients:
            st.write("•", i)


# ---------------- History ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if text and st.button("Save"):
    st.session_state.history.append({
        "text": text,
        "time": datetime.now().strftime("%H:%M")
    })

st.subheader("History")
for h in reversed(st.session_state.history):
    st.write(h["time"], ":", h["text"])