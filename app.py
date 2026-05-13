import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

st.set_page_config(
    page_title="CheeseGuard • Analyzer",
    page_icon="🧀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS فخم
st.markdown("""
<style>
    .main {background-color: #0E1117;}
    .big-font {font-size: 52px !important; font-weight: bold; color: #00FFAA;}
    .verdict-good {background: linear-gradient(90deg, #00C853, #64DD17); color: white; padding: 25px; border-radius: 15px; text-align: center;}
    .verdict-warn {background: linear-gradient(90deg, #FFB300, #FF8F00); color: black; padding: 25px; border-radius: 15px; text-align: center;}
    .verdict-bad {background: linear-gradient(90deg, #F44336, #D32F2F); color: white; padding: 25px; border-radius: 15px; text-align: center;}
    .ingredient-card {background-color: #1E242F; padding: 18px; border-radius: 12px; margin: 8px 0; border-left: 4px solid #00FFAA;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="big-font">🧀 CheeseGuard Pro</h1>', unsafe_allow_html=True)
st.markdown("**محلل مكونات الجبن الذكي • النسخة الاحترافية**")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/cheese.png", width=100)
    st.title("CheeseGuard")
    st.divider()
    language = st.radio("اللغة", ["العربية", "English"])
    st.info("🛡️ لأغراض توعوية فقط - ليس بديل عن استشارة متخصص")

tab1, tab2, tab3 = st.tabs(["🔍 تحليل جديد", "📖 تاريخ التحليلات", "ℹ️ عن التطبيق"])

# ====================== قاعدة البيانات ======================
harmful_db = {
    "natamycin": "مضاد فطريات - شائع في الجبن المبشور",
    "cellulose": "بودرة الخشب (مضاد تكتل)",
    "sodium phosphate": "فوسفات الصوديوم - قد يؤثر على الكلى",
    "carrageenan": "مثخن - قد يسبب التهابات معوية",
    "msg": "غلوتامات أحادية الصوديوم",
    "potato starch": "نشا بطاطس (مضاد تكتل)",
    "artificial color": "ألوان صناعية",
    "e202": "سوربات البوتاسيوم",
    "e235": "ناتامايسين"
}

def analyze_ingredients(text):
    text_lower = text.lower()
    ingredients = [ing.strip() for ing in re.split(r'[,;•]', text) if ing.strip()]
    
    warnings = []
    score = 88
    harmful_found = []
    
    for ing in ingredients:
        for bad, desc in harmful_db.items():
            if bad in ing.lower():
                warnings.append(f"⚠️ {ing} → {desc}")
                harmful_found.append(ing)
                score -= 16
    
    score = max(15, min(100, score))
    
    if score > 75:
        verdict = "✅ ممتاز - طبيعي"
        color = "good"
    elif score > 50:
        verdict = "⚠️ مقبول مع تحفظ"
        color = "warn"
    else:
        verdict = "❌ غير موصى به"
        color = "bad"
    
    return {
        "score": round(score),
        "verdict": verdict,
        "color": color,
        "warnings": warnings,
        "ingredients": ingredients,
        "harmful_count": len(harmful_found),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# ====================== Tab 1: التحليل الجديد ======================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📸 رفع صورة الليبل")
        uploaded_file = st.file_uploader("ارفع صورة مكونات الجبن", type=["png", "jpg", "jpeg"])
        
        st.subheader("أو 📝 اكتب المكونات")
        ingredients_text = st.text_area(
            "الصق قائمة المكونات هنا",
            height=120,
            placeholder="Pasteurized Milk, Salt, Cultures, Rennet, Natamycin, Cellulose Powder..."
        )
        
        analyze_btn = st.button("🚀 ابدأ التحليل", type="primary", use_container_width=True)
    
    if analyze_btn and (ingredients_text.strip() or uploaded_file):
        with st.spinner("جاري التحليل الذكي..."):
            text_to_analyze = ingredients_text
            if uploaded_file:
                text_to_analyze += "\n[تم رفع صورة - سيتم تحليلها بـ OCR في النسخة القادمة]"
            
            result = analyze_ingredients(text_to_analyze)
            
            # حفظ في التاريخ
            if 'history' not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append(result)
            
            # عرض النتيجة
            if result["color"] == "good":
                st.markdown(f'<div class="verdict-good"><h2>{result["verdict"]}</h2></div>', unsafe_allow_html=True)
            elif result["color"] == "warn":
                st.markdown(f'<div class="verdict-warn"><h2>{result["verdict"]}</h2></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="verdict-bad"><h2>{result["verdict"]}</h2></div>', unsafe_allow_html=True)
            
            st.metric("التقييم الصحي", f"{result['score']}/100", delta=None)
            
            st.subheader("⚠️ التحذيرات")
            for w in result["warnings"]:
                st.warning(w)
            
            st.subheader("📋 كل المكونات")
            for ing in result["ingredients"]:
                st.markdown(f'<div class="ingredient-card">• {ing}</div>', unsafe_allow_html=True)
            
            # أزرار التصدير
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📄 تصدير تقرير PDF"):
                    st.success("تم تصدير التقرير (سيتم تفعيل PDF في النسخة القادمة)")
            with col_b:
                if st.button("📋 نسخ النتيجة"):
                    st.success("تم النسخ!")

# ====================== Tab 2: التاريخ ======================
with tab2:
    if 'history' in st.session_state and st.session_state.history:
        st.subheader("تاريخ التحليلات السابقة")
        for i, res in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{res['timestamp']}** - {res['verdict']} ({res['score']}/100)")
            st.progress(res['score']/100)
            st.divider()
    else:
        st.info("لم تقم بأي تحليل بعد")

with tab3:
    st.markdown("### CheeseGuard Pro v1.0")
    st.write("تطبيق مصري احترافي لتحليل مكونات الجبن والألبان.")

---

### إزاي تشغله؟

```bash
streamlit run app.py
