"""
Système Juridique Intelligent Marocain
Application Streamlit — Interface Ministère de la Justice
Lancement : streamlit run app/streamlit_app.py
"""

import os
import time
import json
import pickle
import base64
import tempfile
import warnings
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="المستشار القانوني الذكي | وزارة العدل",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  Chemins absolus
# ─────────────────────────────────────────────────────────────
ROOT     = Path(r"C:\Users\azuz\Downloads\legal_ai_morocco_VF\legal_ai_morocco_VF")
VEC_DIR  = ROOT / "vector_db"
PROC_DIR = ROOT / "processed_data"
DATA_DIR = ROOT / "data"
APP_DIR  = ROOT / "app"


# ─────────────────────────────────────────────────────────────
#  Logo loader
# ─────────────────────────────────────────────────────────────
def load_logo_b64():
    for fname, mime in [
        ("justice.svg", "image/svg+xml"),
        ("justice.png", "image/png"),
        ("adl.svg",     "image/svg+xml"),
    ]:
        p = APP_DIR / fname
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8"), mime
    return "", ""

LOGO_B64, LOGO_MIME = load_logo_b64()

def logo_img_tag(height="68px") -> str:
    if LOGO_B64:
        return (f'<img src="data:{LOGO_MIME};base64,{LOGO_B64}" '
                f'alt="وزارة العدل" style="height:{height};width:auto;display:block">')
    return """<svg viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg" style="height:68px;width:68px">
  <circle cx="36" cy="36" r="34" fill="none" stroke="#c8992a" stroke-width="1.5"/>
  <path d="M24 48L24 30L28 30L28 26L32 26L32 22L36 18L40 22L40 26L44 26L44 30L48 30L48 48Z"
        fill="none" stroke="#c8992a" stroke-width="1.3" stroke-linejoin="round"/>
  <rect x="30" y="36" width="12" height="12" fill="none" stroke="#c8992a" stroke-width="1"/>
  <circle cx="36" cy="28" r="2" fill="#c8992a"/>
</svg>"""


# ─────────────────────────────────────────────────────────────
#  CSS Global Streamlit
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap');

#MainMenu, footer                { visibility: hidden; }
[data-testid="stToolbar"]        { display: none !important; }
[data-testid="stHeader"]         { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
.stDeployButton                  { display: none !important; }

.block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}

/* TABS */
[data-testid="stTabs"] { display:flex; flex-direction:column; align-items:center; }
[data-testid="stTabsNavContainer"] {
    width:100%; display:flex; justify-content:center;
    border-bottom:1px solid #e0e0e0 !important;
    background:#fff !important; padding:0 20px !important;
}
[data-testid="stTabs"] > div:first-child { justify-content:center !important; width:100%; }
button[data-baseweb="tab"] {
    font-family:'Cairo',sans-serif !important; font-size:15px !important;
    font-weight:600 !important; padding:14px 28px !important;
    color:#1a3a5c !important; border-bottom:3px solid transparent !important; margin:0 4px !important;
}
button[data-baseweb="tab"]:hover {
    color:#c8992a !important; border-bottom-color:#c8992a !important;
    background:rgba(200,153,42,0.06) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color:#c8992a !important; border-bottom:3px solid #c8992a !important;
    background:transparent !important;
}

/* Cartes */
.mj-result-box {
    background:#fff; border-radius:8px; padding:24px;
    border:0.5px solid #e0e0e0; border-top:3px solid #1a3a5c;
    direction:rtl; margin-bottom:16px; font-family:'Cairo',sans-serif;
}
.mj-article-card {
    background:#f8f9fa; border-radius:8px; padding:14px 16px;
    margin:8px 0; border-right:4px solid #c8992a; direction:rtl;
}
.mj-article-title { font-weight:700; color:#1a3a5c; margin-bottom:6px; font-family:'Cairo',sans-serif; font-size:13.5px; }
.mj-article-text  { font-size:12.5px; color:#444; line-height:1.6; font-family:'Cairo',sans-serif; }
.mj-article-score { float:left; font-size:11px; color:#999; }
.mj-disclaimer {
    background:#fff8e1; border-right:4px solid #c8992a; padding:12px 16px;
    border-radius:4px; font-size:12px; color:#5d4037;
    font-family:'Cairo',sans-serif; direction:rtl; margin-top:8px;
}
.mj-stat-card {
    background:#fff; border-radius:8px; padding:18px; text-align:center;
    border:0.5px solid #e0e0e0; border-top:3px solid #1a3a5c;
    direction:rtl; margin-bottom:8px;
}
.mj-stat-card .num { font-size:28px; font-weight:700; color:#1a3a5c; font-family:'Cairo',sans-serif; }
.mj-stat-card .ar  { font-size:13px; font-weight:600; color:#333; font-family:'Cairo',sans-serif; }
.mj-stat-card .fr  { font-size:10px; color:#aaa; font-family:'Cairo',sans-serif; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  HEADER HTML — rendu via components.html (iframe, pas de sanitiseur)
# ─────────────────────────────────────────────────────────────
HEADER_HTML = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&family=Noto+Naskh+Arabic:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Cairo',sans-serif;background:#f5f7fa;direction:rtl}}
.topbar{{background:#1a3a5c;padding:6px 36px;display:flex;justify-content:space-between;align-items:center}}
.topbar a{{color:#9db0bf;text-decoration:none;font-size:12.5px;margin-left:28px; padding:10px 20px}}
.topbar a:hover{{color:#c8992a}}
.lang-btn{{background:#c8992a;color:#fff;border:none;padding:3px 14px;font-size:11px;border-radius:3px;font-family:'Cairo',sans-serif;cursor:pointer}}
.mj-header{{background:#1a3a5c;padding:13px 36px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #c8992a}}
.logo-section{{display:flex;align-items:center;gap:14px}}
.logo-texts{{display:flex;flex-direction:column;gap:1px}}
.logo-ar-sm{{color:#fff;font-size:13px;font-weight:600}}
.logo-ar-lg{{color:#c8992a;font-size:19px;font-weight:700;line-height:1.2}}
.logo-fr{{color:rgba(255,255,255,0.45);font-size:10px;letter-spacing:.05em}}
.header-right{{display:flex;flex-direction:column;align-items:flex-end;gap:8px}}
.platform-links{{display:flex;gap:8px}}
.platform-btn{{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.2);color:#fff;padding:4px 16px;border-radius:3px;font-size:12px;font-family:'Cairo',sans-serif;cursor:pointer}}
.esvc-btn{{background:#c8992a;color:#fff;padding:8px 22px;border-radius:4px;font-size:13px;font-weight:600;font-family:'Cairo',sans-serif;cursor:pointer;border:none}}
.mj-nav{{background:#fff;border-bottom:1px solid #ddd;padding:0 36px;display:flex;overflow-x:auto;box-shadow:0 2px 6px rgba(0,0,0,0.05)}}
.nav-item{{padding:15px 17px;font-size:13px;color:#1a3a5c;font-weight:600;cursor:pointer;white-space:nowrap;border-bottom:3px solid transparent;transition:all .2s}}
.nav-item:hover,.nav-item.active{{border-bottom-color:#c8992a;color:#c8992a}}
.svc-strip{{background:#fff;border-bottom:1px solid #ebebeb;padding:0 36px;overflow-x:auto;display:flex;justify-content:center}}
.svc-inner{{display:flex;justify-content:space-between;width:100%}}
.svc-item{{display:inline-flex;flex-direction:column;align-items:center;gap:6px;padding:13px 28px;min-width:100px;border-left:1px solid #eee;cursor:pointer;text-decoration:none;color:#1a3a5c;transition:background .15s}}
.svc-item:hover{{background:#f8f9fb}}
.svc-icon{{width:34px;height:34px;background:#eef3f9;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px}}
.svc-label{{font-size:10px;font-weight:600;text-align:center;color:#1a3a5c;white-space:normal;max-width:80px;line-height:1.3}}
.svc-ai{{background:#fff8ec!important;border-right:3px solid #c8992a!important}}
.svc-ai .svc-icon{{background:#fff3cd;color:#c8992a}}
.svc-ai .svc-label{{color:#c8992a;font-weight:700}}
.mj-hero{{background:#1a3a5c;overflow:hidden}}
.hero-inner{{display:flex;min-height:400px}}
.hero-left{{width:190px;flex-shrink:0;background:rgba(200,153,42,0.06);border-left:1px solid rgba(200,153,42,0.15);display:flex;flex-direction:column;justify-content:center;align-items:center;gap:14px;padding:20px 12px}}
.hero-left-year{{font-size:20px;font-weight:700;color:rgba(200,153,42,0.75);text-align:center}}
.hero-left-lbl{{font-size:10px;color:rgba(200,153,42,0.5);text-align:center;line-height:1.6}}
.hero-center{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:52px 36px;text-align:center}}
.hero-badge{{display:inline-block;background:rgba(200,153,42,0.15);border:1px solid rgba(200,153,42,0.4);color:#c8992a;font-size:11px;font-weight:600;padding:5px 18px;border-radius:20px;margin-bottom:22px}}
.hero-title{{font-family:'Noto Naskh Arabic','Cairo',serif;font-size:50px;font-weight:700;color:#fff;line-height:1.35;margin-bottom:8px}}
.hero-title .hl{{color:#4a90d9;display:block}}
.hero-divider{{width:54px;height:3px;background:#c8992a;margin:0 auto 16px;border-radius:2px}}
.hero-subtitle{{font-size:12px;color:rgba(255,255,255,0.45);margin-bottom:32px;letter-spacing:.08em}}
.cta-row{{display:flex;gap:11px;justify-content:center;flex-wrap:wrap}}
.btn-gold{{background:#c8992a;color:#fff;border:none;padding:10px 24px;font-size:13px;font-weight:600;border-radius:4px;cursor:pointer;font-family:'Cairo',sans-serif}}
.btn-outline{{background:transparent;color:#fff;border:1px solid rgba(255,255,255,0.4);padding:10px 24px;font-size:13px;border-radius:4px;cursor:pointer;font-family:'Cairo',sans-serif}}
.btn-ai{{background:rgba(74,144,217,0.15);border:1px solid rgba(74,144,217,0.5);color:#a8d0f5;padding:10px 24px;font-size:13px;border-radius:4px;cursor:pointer;font-family:'Cairo',sans-serif}}
.hero-right{{width:190px;flex-shrink:0;background:rgba(10,30,50,0.35);border-right:1px solid rgba(255,255,255,0.07);display:flex;flex-direction:column;justify-content:center}}
.hero-stat{{padding:18px;border-bottom:1px solid rgba(255,255,255,0.06)}}
.hero-stat:last-child{{border-bottom:none}}
.hero-stat-num{{font-size:22px;font-weight:700;color:#c8992a;font-family:'Cairo',sans-serif}}
.hero-stat-lbl{{font-size:10.5px;color:rgba(255,255,255,0.45);font-family:'Cairo',sans-serif;line-height:1.4;margin-top:2px}}
.stats-row{{background:#15304d;padding:26px 36px}}
.stats-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;max-width:1100px;margin:0 auto;text-align:center}}
.stat-item{{padding:10px;border-left:1px solid rgba(255,255,255,0.08)}}
.stat-item:last-child{{border-left:none}}
.stat-num{{font-size:30px;font-weight:700;color:#c8992a;font-family:'Cairo',sans-serif}}
.stat-lbl{{font-size:11.5px;color:rgba(255,255,255,0.55);font-family:'Cairo',sans-serif;margin-top:2px}}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <a href="#">إتصال</a><a href="#">روابط مفيدة</a>
    <a href="#">وظائف</a><a href="#">إعلانات قضائية</a><a href="#">مستجدات</a>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <a href="#" style="margin:0">Français</a>
    <button class="lang-btn">العربية</button>
  </div>
</div>

<div class="mj-header">
  <div class="logo-section">
    {logo_img_tag("68px")}
    <div class="logo-texts">
      <div class="logo-ar-sm">المملكة المغربية</div>
      <div class="logo-ar-lg">وزارة العدل</div>
      <div class="logo-fr">MINISTÈRE DE LA JUSTICE</div>
    </div>
  </div>
  <div class="header-right">
    <div class="platform-links">
      <button class="platform-btn">محاكم</button>
      <button class="platform-btn">عدالة</button>
    </div>
    <button class="esvc-btn">الخدمات الإلكترونية</button>
  </div>
</div>

<div class="mj-nav">
  <div class="nav-item active">الرئيسية</div>
  <div class="nav-item">الوزارة ▾</div>
  <div class="nav-item">المنظومة القضائية ▾</div>
  <div class="nav-item">التشريع ▾</div>
  <div class="nav-item">التعاون الدولي ▾</div>
  <div class="nav-item">الإصلاح القضائي ▾</div>
  <div class="nav-item">المواطن والقضاء ▾</div>
  <div class="nav-item">المستشار الذكي ▾</div>
</div>

<div class="svc-strip">
  <div class="svc-inner">
    <a class="svc-item" href="#"><div class="svc-icon">📋</div><div class="svc-label">تتبع ملفات القضايا</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">📅</div><div class="svc-label">جدول الجلسات</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">📄</div><div class="svc-label">طلب السجل العدلي</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">🏢</div><div class="svc-label">السجل التجاري</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">💬</div><div class="svc-label">خدمة الشكايات</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">⚖️</div><div class="svc-label">منصة المحامي</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">🚗</div><div class="svc-label">غرامات السير</div></a>
    <a class="svc-item" href="#"><div class="svc-icon">📆</div><div class="svc-label">حجز المواعيد</div></a>
    <a class="svc-item svc-ai" href="#"><div class="svc-icon">🤖</div><div class="svc-label">المستشار الذكي</div></a>
  </div>
</div>

<div class="mj-hero">
  <div class="hero-inner">
    <div class="hero-left">
      <svg viewBox="0 0 70 100" width="58" height="83" style="opacity:0.22">
        <rect x="5" y="30" width="60" height="65" fill="none" stroke="#c8992a" stroke-width="1.5" rx="2"/>
        <rect x="15" y="14" width="40" height="20" fill="none" stroke="#c8992a" stroke-width="1.5" rx="1"/>
        <rect x="28" y="4" width="14" height="12" fill="none" stroke="#c8992a" stroke-width="1.5"/>
        <circle cx="35" cy="64" r="10" fill="none" stroke="#c8992a" stroke-width="1.5"/>
        <line x1="35" y1="56" x2="35" y2="72" stroke="#c8992a" stroke-width="1"/>
        <line x1="27" y1="64" x2="43" y2="64" stroke="#c8992a" stroke-width="1"/>
      </svg>
      <div>
        <div class="hero-left-year">1956</div>
        <div class="hero-left-lbl">تأسيس الوزارة</div>
      </div>
    </div>
    <div class="hero-center">
      <div class="hero-badge">المملكة المغربية · وزارة العدل · النظام القانوني الذكي</div>
      <div class="hero-title">
        القضاء في خدمة
        <span class="hl">المواطن</span>
      </div>
      <div class="hero-divider"></div>
      <div class="hero-subtitle">JUSTICE AU SERVICE DU CITOYEN — SYSTÈME JURIDIQUE INTELLIGENT</div>
      <div class="cta-row">
        <button class="btn-gold">الخدمات الإلكترونية</button>
        <button class="btn-outline">تعرف على الوزارة</button>
        <button class="btn-ai">⚖️ المستشار القانوني الذكي</button>
      </div>
    </div>
    <div class="hero-right">
      <div class="hero-stat"><div class="hero-stat-num">4.2M+</div><div class="hero-stat-lbl">قضية معالجة سنوياً</div></div>
      <div class="hero-stat"><div class="hero-stat-num">82</div><div class="hero-stat-lbl">محكمة وطنياً</div></div>
      <div class="hero-stat"><div class="hero-stat-num">+50</div><div class="hero-stat-lbl">نصاً تشريعياً مُدرجاً</div></div>
      <div class="hero-stat"><div class="hero-stat-num" style="color:#a8d0f5">جديد</div><div class="hero-stat-lbl">المستشار الذكي متاح الآن</div></div>
    </div>
  </div>
</div>

<div class="stats-row">
  <div class="stats-grid">
    <div class="stat-item"><div class="stat-num">4.2M+</div><div class="stat-lbl">قضية معالجة سنوياً</div></div>
    <div class="stat-item"><div class="stat-num">82</div><div class="stat-lbl">محكمة على الصعيد الوطني</div></div>
    <div class="stat-item"><div class="stat-num">+50</div><div class="stat-lbl">نصاً قانونياً مُدرجاً</div></div>
    <div class="stat-item"><div class="stat-num">14</div><div class="stat-lbl">خدمة إلكترونية للمواطن</div></div>
  </div>
</div>

</body></html>"""


# ─────────────────────────────────────────────────────────────
#  FOOTER — rendu via components.html (iframe isolé)
#  ⚠️  Le footer DOIT être dans un iframe séparé car st.markdown
#      échappe les balises grid/flex complexes sur certaines versions.
#      On génère un HTML complet autonome.
# ─────────────────────────────────────────────────────────────
FOOTER_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Cairo',sans-serif;background:#0f1e2d;direction:rtl}
.footer{padding:36px 40px 20px;background:#0f1e2d}
.grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;max-width:1100px;margin:0 auto 28px}
.brand{font-size:15px;font-weight:700;color:#fff;margin-bottom:10px}
.desc{font-size:12px;color:rgba(255,255,255,0.4);line-height:1.9}
.addr{margin-top:12px;font-size:11px;color:rgba(255,255,255,0.2)}
.col-title{font-size:13px;font-weight:700;color:#c8992a;margin-bottom:12px;
           border-bottom:1px solid rgba(200,153,42,0.2);padding-bottom:8px}
.links{font-size:12px;color:rgba(255,255,255,0.45);line-height:2.3}
.bar{border-top:1px solid rgba(255,255,255,0.08);padding-top:16px;text-align:center;
     font-size:11px;color:rgba(255,255,255,0.25);max-width:1100px;margin:0 auto}
.sub{color:rgba(255,255,255,0.12)}
</style>
</head>
<body>
<div class="footer">
  <div class="grid">
    <div>
      <div class="brand">وزارة العدل — المملكة المغربية</div>
      <div class="desc">تعمل وزارة العدل على تعزيز منظومة العدالة وصون الحقوق وضمان سيادة القانون في خدمة المواطن المغربي. النظام القانوني الذكي إضافة رقمية لتيسير الوصول إلى المعلومة القانونية.</div>
      <div class="addr">Avenue Al Majd, Hay Riad · Rabat 10100</div>
    </div>
    <div>
      <div class="col-title">روابط سريعة</div>
      <div class="links">الصفحة الرئيسية<br>الوزارة<br>التشريع<br>الإصلاح القضائي<br>إتصال</div>
    </div>
    <div>
      <div class="col-title">الخدمات</div>
      <div class="links">السجل العدلي<br>تتبع القضايا<br>جدول الجلسات<br>المستشار الذكي</div>
    </div>
    <div>
      <div class="col-title">المنصات الشريكة</div>
      <div class="links">منصة محاكم<br>بوابة عدالة<br>منصة المحامي<br>الإيداع الإلكتروني</div>
    </div>
  </div>
  <div class="bar">
    © 2025 وزارة العدل — المملكة المغربية · جميع الحقوق محفوظة · Ministère de la Justice — Royaume du Maroc<br>
    <span class="sub">النظام القانوني الذكي · Claude AI + FAISS · للأغراض الإعلامية فقط</span>
  </div>
</div>
</body></html>"""


# ─────────────────────────────────────────────────────────────
#  Data loaders
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_components():
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        index_path = VEC_DIR / "faiss_index.bin"
        meta_path  = VEC_DIR / "metadata.pkl"
        if not index_path.exists() or not meta_path.exists():
            return None, None, None, f"Base vectorielle non trouvée dans : {VEC_DIR}"
        index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return index, metadata, model, None
    except ImportError as e:
        return None, None, None, f"Dépendance manquante : {e}"
    except Exception as e:
        return None, None, None, str(e)


@st.cache_data(show_spinner=False)
def load_dataframe():
    for p in [PROC_DIR / "processed_laws.csv", DATA_DIR / "raw_laws.csv"]:
        if p.exists():
            return pd.read_csv(p)
    return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────────────────────
CATEGORY_LABELS = {
    "civil":     "⚖️ Civil",
    "penal":     "🚨 Pénal",
    "social":    "👷 Social",
    "familial":  "👨‍👩‍👧 Familial",
    "education": "🎓 Éducation",
}
CATEGORY_COLORS = {
    "civil":     "#1565C0",
    "penal":     "#B71C1C",
    "social":    "#1B5E20",
    "familial":  "#6A1B9A",
    "education": "#E65100",
}


# ─────────────────────────────────────────────────────────────
#  Fonctions utilitaires
# ─────────────────────────────────────────────────────────────
def semantic_search(query, index, metadata, model, top_k=5, category_filter=None):
    q_emb = model.encode([query], normalize_embeddings=True).astype(np.float32)
    dists, idxs = index.search(q_emb, top_k * 3)
    results, seen = [], set()
    for dist, idx in zip(dists[0], idxs[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        meta = metadata[idx].copy()
        if category_filter and meta.get("category") != category_filter:
            continue
        key = str(meta.get("article_text", ""))[:80]
        if key in seen:
            continue
        seen.add(key)
        meta["score"] = float(dist)
        results.append(meta)
        if len(results) >= top_k:
            break
    return results


def call_claude_api(question, context, lang, api_key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        sys_fr = """Vous êtes un assistant juridique expert en droit marocain, intégré au système officiel du Ministère de la Justice.
Basez-vous EXCLUSIVEMENT sur les articles fournis. Répondez en français.
## 📋 Analyse de la situation
## ⚖️ Lois applicables
## 🛡️ Droits et obligations
## 📝 Procédure recommandée
## 📚 Références légales"""
        sys_ar = """أنت مساعد قانوني خبير في القانون المغربي، مدمج في المنظومة الرسمية لوزارة العدل.
استند حصراً إلى المواد المقدمة. أجب بالعربية.
## 📋 تحليل الوضع
## ⚖️ القوانين المنطبقة
## 🛡️ الحقوق والالتزامات
## 📝 الإجراء الموصى به
## 📚 المراجع القانونية"""
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=sys_ar if lang == "ar" else sys_fr,
            messages=[{"role": "user", "content": f"السؤال:\n{question}\n\nالمواد القانونية:\n{context}"}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"⚠️ Erreur API : {e}"


def format_article_card(art):
    cat   = art.get("category", "?")
    color = CATEGORY_COLORS.get(cat, "#1a3a5c")
    score = art.get("score", 0)
    text  = art.get("article_text", "")
    return f"""
<div class="mj-article-card">
  <span class="mj-article-score">الصلة: {score:.2f}</span>
  <div class="mj-article-title">
    <span style="color:{color}">●</span>
    {art.get('title', 'قانون')} — م.{art.get('article_number', '?')}
    <span style="background:{color};color:#fff;font-size:10px;padding:2px 8px;
                 border-radius:10px;margin-right:6px">{CATEGORY_LABELS.get(cat, cat)}</span>
  </div>
  <div class="mj-article-text">{text[:400]}{'...' if len(text) > 400 else ''}</div>
</div>"""


def extract_text_from_upload(uploaded_file):
    name    = uploaded_file.name.lower()
    content = uploaded_file.read()
    if name.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            import fitz
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            doc  = fitz.open(tmp_path)
            text = "\n".join(p.get_text() for p in doc)
            os.unlink(tmp_path)
            return text if len(text.strip()) > 50 else "PDF scanné — installez pytesseract."
        except Exception as e:
            return f"Erreur PDF : {e}"
    if name.endswith(".docx"):
        try:
            from docx import Document
            import io
            return "\n".join(p.text for p in Document(io.BytesIO(content)).paragraphs if p.text.strip())
        except Exception as e:
            return f"Erreur DOCX : {e}"
    return "Format non supporté."


# ─────────────────────────────────────────────────────────────
#  Chargement données
# ─────────────────────────────────────────────────────────────
index, metadata, embed_model, load_error = load_components()
df_laws = load_dataframe()


# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f'<div style="text-align:center;padding:10px 0 14px">'
            f'<img src="data:{LOGO_MIME};base64,{LOGO_B64}" style="height:60px;width:auto"/>'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;font-size:36px;padding:10px 0 14px">⚖️</div>',
                    unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding-bottom:14px;border-bottom:1px solid rgba(200,153,42,0.3);
                margin-bottom:14px;direction:rtl">
      <div style="font-size:15px;font-weight:700;color:#1a3a5c;font-family:'Cairo',sans-serif">وزارة العدل</div>
      <div style="font-size:12px;color:#c8992a;font-family:'Cairo',sans-serif">النظام القانوني الذكي</div>
      <div style="font-size:10px;color:#888;font-family:'Cairo',sans-serif">Système Juridique Intelligent Marocain</div>
    </div>""", unsafe_allow_html=True)

    api_key = st.text_input(
        "🔑 Clé API Anthropic", type="password", placeholder="sk-ant-...",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Obtenez votre clé sur console.anthropic.com",
    )
    st.markdown("---")
    lang = st.selectbox("🌐 Langue de réponse", options=["fr", "ar"],
                        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇲🇦 العربية")
    cat_raw = st.selectbox("📂 Domaine juridique",
                            options=["Tous", "civil", "penal", "social", "familial", "education"],
                            format_func=lambda x: CATEGORY_LABELS.get(x, x.capitalize()))
    category_filter = None if cat_raw == "Tous" else cat_raw
    top_k = st.slider(" Articles à récupérer", 3, 10, 5)
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Cairo',sans-serif;font-size:12px;color:#555;direction:rtl">
      <b style="color:#1a3a5c">المصادر القانونية :</b><br><br>
      • مدونة الالتزامات والعقود<br>
      • مدونة الشغل (قانون 65-99)<br>
      • مدونة الأسرة<br>
      • قانون 103-13 (العنف ضد المرأة)<br>
      • القانون الجنائي<br>
      • قانون الجنسية المغربية<br>
      • قانون التعليم 51-17<br>
      • التحكيم والوساطة<br>
      • وغيرها من النصوص التشريعية...
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<div class="mj-disclaimer">⚠️ هذه الأداة للأغراض الإعلامية فقط. '
        'لأي نزاع قانوني، استشر محامياً مقيداً بهيئة المحامين المغربية.</div>',
        unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  HEADER  (iframe)
# ─────────────────────────────────────────────────────────────
components.html(HEADER_HTML, height=625, scrolling=False)


# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tabs = st.tabs([
    " الرئيسية",
    " المستشار الذكي",
    " تحليل وثيقة",
    " استكشاف القوانين",
    " سجل الاستشارات",
])


# ═══════════════════════════════════════════════════════════════
#  TAB 0 — ACCUEIL
# ═══════════════════════════════════════════════════════════════
with tabs[0]:

    # Bannière IA
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a3a5c,#1e4a6e);border-radius:8px;
                padding:24px 28px;direction:rtl;display:flex;align-items:center;gap:20px;
                margin:20px 0 16px;border:1px solid rgba(200,153,42,0.3)">
      <div style="width:58px;height:58px;background:rgba(200,153,42,0.15);border-radius:50%;
                  display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0">🤖</div>
      <div>
        <div style="display:inline-block;background:#c8992a;color:#fff;font-size:10px;font-weight:700;
                    padding:2px 12px;border-radius:12px;font-family:'Cairo',sans-serif;margin-bottom:6px">
          جديد ✦ مستجد
        </div>
        <div style="font-size:19px;font-weight:700;color:#fff;font-family:'Cairo',sans-serif">
          المستشار القانوني الذكي المغربي
        </div>
        <div style="font-size:12.5px;color:rgba(255,255,255,0.55);font-family:'Cairo',sans-serif;line-height:1.6">
          نظام ذكاء اصطناعي مبني على النصوص التشريعية المغربية الرسمية —
          استشارات فورية باللغتين العربية والفرنسية بتقنية RAG + Claude AI
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Statistiques
    if not df_laws.empty:
        c1, c2, c3, c4 = st.columns(4)
        total  = len(df_laws)
        n_laws = df_laws["law_number"].nunique() if "law_number" in df_laws.columns else "—"
        n_cats = df_laws["category"].nunique()   if "category"   in df_laws.columns else "—"
        n_lang = df_laws["language"].nunique()   if "language"   in df_laws.columns else "—"
        for col, (num, ar, fr) in zip([c1, c2, c3, c4], [
            (total,  "مادة قانونية مُفهرسة", "Articles indexés"),
            (n_laws, "نص تشريعي",            "Textes de loi"),
            (n_cats, "مجال قانوني",           "Domaines"),
            (n_lang, "لغة مدعومة",           "Langues"),
        ]):
            col.markdown(
                f'<div class="mj-stat-card">'
                f'<div class="num">{num}</div>'
                f'<div class="ar">{ar}</div>'
                f'<div class="fr">{fr}</div></div>',
                unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Domaines
    st.markdown("####  المجالات القانونية المُغطاة")
    dc = st.columns(5)
    domains = [
        ("⚖️", "المدني",     "العقود، الملكية، الالتزامات، البيع، الإيجار، التحكيم"),
        ("🚨", "الجنائي",    "الجرائم، المخالفات، الإجراءات الجنائية، العنف"),
        ("👷", "الاجتماعي", "قانون الشغل، الفصل، الإجازات، الراتب، الضمان"),
        ("👨‍👩‍👧", "الأسري",   "الزواج، الطلاق، الحضانة، الكفالة، الجنسية، الإرث"),
        ("🎓", "التعليم",    "المنظومة التعليمية، الامتحانات، الغش، المؤسسات"),
    ]
    for col, (icon, title, desc) in zip(dc, domains):
        col.markdown(f"""
        <div style="background:#fff;border-radius:8px;padding:18px 12px;text-align:center;
                    border:0.5px solid #e0e0e0;cursor:pointer;direction:rtl;min-height:160px">
          <div style="font-size:26px;margin-bottom:8px">{icon}</div>
          <div style="font-size:13px;font-weight:700;color:#1a3a5c;font-family:'Cairo',sans-serif;margin-bottom:4px">{title}</div>
          <div style="font-size:10.5px;color:#888;font-family:'Cairo',sans-serif;line-height:1.4">{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ── FOOTER via components.html (HTML complet autonome dans iframe) ──
    components.html(FOOTER_HTML, height=300, scrolling=False)


# ═══════════════════════════════════════════════════════════════
#  TAB 1 — ASSISTANT JURIDIQUE
# ═══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 💬 صِف وضعك القانوني أو اطرح سؤالك")

    ex_cols = st.columns(3)
    examples = [
        "يريد صاحب العمل فصلي دون سبب مشروع، ما هي حقوقي؟",
        "تعرضت للعنف من طرف زوجي، ما هي الإجراءات القانونية؟",
        "أريد الطعن في عقد بيع عقاري، كيف أتصرف؟",
    ]
    for col, ex in zip(ex_cols, examples):
        if col.button(f" {ex[:42]}...", key=f"ex_{ex[:8]}", use_container_width=True):
            st.session_state["question_input"] = ex

    question = st.text_area(
        "سؤالك / وضعك القانوني :",
        value=st.session_state.get("question_input", ""),
        height=130,
        placeholder="صِف مشكلتك القانونية بالتفصيل... / Décrivez votre problème juridique en détail...",
        key="question_area",
    )
    b1, b2 = st.columns([4, 1])
    analyze = b1.button(" تحليل وضعي القانوني", type="primary", use_container_width=True)
    b2.button("🗑️ مسح",
              on_click=lambda: st.session_state.update({"question_input": "", "last_result": None}),
              use_container_width=True)

    if analyze and question.strip():
        if not api_key:
            st.error("⚠️ يرجى إدخال مفتاح API في الشريط الجانبي.")
        elif load_error or index is None:
            st.warning("⚠️ قاعدة البيانات غير متاحة. شغّل الـ notebooks أولاً.")
        else:
            with st.spinner("⚙️ جارٍ التحليل القانوني..."):
                t0       = time.time()
                articles = semantic_search(question, index, metadata, embed_model,
                                           top_k=top_k, category_filter=category_filter)
                ctx      = "\n\n".join([
                    f"[{i+1}] {a.get('title','?')} — م.{a.get('article_number','?')}\n{a.get('article_text','')}"
                    for i, a in enumerate(articles)
                ])
                response = call_claude_api(question, ctx, lang, api_key)
                result   = {
                    "question":  question,
                    "response":  response,
                    "articles":  articles,
                    "lang":      lang,
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "elapsed":   round(time.time() - t0, 1),
                }
                st.session_state["last_result"] = result
                st.session_state.setdefault("history", []).insert(0, result)
            st.rerun()

    result = st.session_state.get("last_result")
    if result:
        st.markdown(f"<small style='color:#888'>⏱ {result.get('elapsed','?')} ثانية</small>",
                    unsafe_allow_html=True)
        r1, r2 = st.columns([3, 2])
        with r1:
            st.markdown("###  التحليل القانوني")
            st.markdown(
                f'<div class="mj-result-box">{result["response"].replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True)
        with r2:
            st.markdown(f"###  المواد المُستردة ({len(result['articles'])})")
            for art in result["articles"]:
                st.markdown(format_article_card(art), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  TAB 2 — ANALYSER UN DOCUMENT
# ═══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("###  تحليل وثيقة قانونية")
    cu, cq = st.columns([2, 3])
    with cu:
        uploaded = st.file_uploader("اختر ملفاً", type=["pdf","docx","txt","png","jpg","jpeg"])
        if uploaded:
            st.success(f"✅ {uploaded.name}")
            with st.spinner("استخراج النص..."):
                doc_text = extract_text_from_upload(uploaded)
            st.info(f"📝 {len(doc_text)} حرف مُستخرَج")
            with st.expander("معاينة النص"):
                st.text(doc_text[:800] + ("..." if len(doc_text) > 800 else ""))
            st.session_state["doc_text"] = doc_text
    with cq:
        doc_q = st.text_area("سؤالك حول الوثيقة :", height=100,
                              placeholder="ما هي حقوقي وفق هذه الوثيقة؟ / هل توجد بنود غير قانونية؟")
        if st.button(" تحليل الوثيقة", type="primary",
                     disabled=not (st.session_state.get("doc_text") and doc_q)):
            if not api_key:
                st.error("⚠️ مفتاح API مطلوب.")
            else:
                with st.spinner("جارٍ التحليل..."):
                    combined = f"{doc_q}\n\nمحتوى الوثيقة:\n{st.session_state.get('doc_text','')[:3000]}"
                    arts, ctx = [], ""
                    if index and metadata and embed_model:
                        arts = semantic_search(combined, index, metadata, embed_model, top_k=4)
                        ctx  = "\n\n".join([
                            f"[{i+1}] {a.get('title','?')}\n{a.get('article_text','')}"
                            for i, a in enumerate(arts)
                        ])
                    response = call_claude_api(combined, ctx, lang, api_key)
                    st.markdown("### 📋 نتيجة التحليل")
                    st.markdown(
                        f'<div class="mj-result-box">{response.replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True)
                    for art in arts:
                        st.markdown(format_article_card(art), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  TAB 3 — EXPLORER LES LOIS
# ═══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("###  استكشاف القاعدة القانونية المغربية")
    if df_laws.empty:
        st.info("قاعدة البيانات غير محملة. شغّل الـ notebook الأول.")
    else:
        f1, f2, f3 = st.columns(3)
        cats    = (["الكل"] + sorted(df_laws["category"].dropna().unique().tolist())
                   if "category" in df_laws.columns else ["الكل"])
        sel_cat = f1.selectbox("المجال", cats,
                                format_func=lambda x: CATEGORY_LABELS.get(x, x.capitalize()))
        srch    = f2.text_input(" بحث في النصوص", placeholder="كلمة مفتاح...")
        n_show  = f3.slider("عدد المواد", 5, 50, 10)

        filt = df_laws.copy()
        if sel_cat != "الكل" and "category" in filt.columns:
            filt = filt[filt["category"] == sel_cat]
        if srch and "article_text" in filt.columns:
            filt = filt[filt["article_text"].str.contains(srch, case=False, na=False)]

        st.markdown(f"**{len(filt)} مادة** وجدت")
        dcols = [c for c in ["title","article_number","category","language","article_text"]
                 if c in filt.columns]
        if dcols:
            st.dataframe(filt[dcols].head(n_show), use_container_width=True, hide_index=True)

        if "category" in df_laws.columns and len(df_laws) > 0:
            import matplotlib
            import matplotlib.pyplot as plt
            matplotlib.rcParams['font.family'] = 'DejaVu Sans'

            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            fig.patch.set_facecolor('#f5f7fa')

            cc     = df_laws["category"].value_counts()
            colors = [CATEGORY_COLORS.get(c, "#1a3a5c") for c in cc.index]
            bars   = axes[0].barh(cc.index, cc.values, color=colors, height=0.6)
            axes[0].set_title("Articles par domaine juridique", fontweight="bold", fontsize=13, pad=12)
            axes[0].set_facecolor('#f5f7fa')
            axes[0].spines[['top', 'right']].set_visible(False)
            axes[0].tick_params(labelsize=10)
            for bar, val in zip(bars, cc.values):
                axes[0].text(bar.get_width() + 0.1,
                             bar.get_y() + bar.get_height() / 2,
                             str(val), va='center', fontsize=10, color='#333')

            if "language" in df_laws.columns:
                lc = df_laws["language"].value_counts()
                wedge_colors = ["#1a3a5c","#c8992a","#2e7d32","#b71c1c"][:len(lc)]
                wedges, texts, autotexts = axes[1].pie(
                    lc.values, labels=lc.index, autopct="%1.0f%%",
                    colors=wedge_colors, startangle=90,
                    wedgeprops=dict(edgecolor='white', linewidth=2),
                )
                for t in autotexts:
                    t.set_fontsize(11)
                    t.set_color('white')
                    t.set_fontweight('bold')
                axes[1].set_title("Répartition par langue", fontweight="bold", fontsize=13, pad=12)

            plt.tight_layout(pad=2)
            st.pyplot(fig)


# ═══════════════════════════════════════════════════════════════
#  TAB 4 — HISTORIQUE
# ═══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("###  سجل الاستشارات القانونية")
    history = st.session_state.get("history", [])
    if not history:
        st.info("لا توجد استشارات بعد. استخدم تبويب 'المستشار الذكي'.")
    else:
        st.markdown(f"**{len(history)} استشارة**")
        st.download_button(
            "📥 تصدير (JSON)",
            data=json.dumps(
                [{"timestamp": r["timestamp"], "question": r["question"], "response": r["response"]}
                 for r in history],
                ensure_ascii=False, indent=2),
            file_name=f"استشارات_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )
        for i, entry in enumerate(history):
            with st.expander(
                f"[{entry['timestamp']}] {entry['question'][:70]}...",
                expanded=(i == 0)
            ):
                a, b = st.columns([3, 2])
                with a:
                    st.markdown("** التحليل القانوني :**")
                    st.markdown(entry["response"])
                with b:
                    arts = entry.get("articles", [])
                    if arts:
                        st.markdown(f"** المواد ({len(arts)}) :**")
                        for art in arts:
                            c = CATEGORY_COLORS.get(art.get("category", "?"), "#1a3a5c")
                            st.markdown(
                                f'<span style="background:{c};color:#fff;font-size:10px;'
                                f'padding:2px 10px;border-radius:10px;margin:2px;display:inline-block">'
                                f'{art.get("title","?")[:28]} — م.{art.get("article_number","?")}</span>',
                                unsafe_allow_html=True)