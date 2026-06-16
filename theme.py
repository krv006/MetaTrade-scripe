"""
Dizayn yadrosi: ranglar, CSS, ma'lumot yuklash, KPI komponentlari, Plotly shabloni.
Barcha sahifalar shu moduldan foydalanadi.
"""
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

from analytics import build_trades, kpis  # noqa: F401 (sahifalar import qiladi)

EXPORT = Path("mt5_export")

# ============ RANG PALITRASI (premium fintech dark) ============
BG       = "#0a0e1a"
SURFACE  = "#121826"
SURFACE2 = "#1a2236"
BORDER   = "#232c43"
TEXT     = "#e8edf7"
MUTED    = "#8a94ad"
GREEN    = "#0ecb81"
RED      = "#f6465d"
BLUE     = "#4f8cff"
GOLD     = "#f0b90b"
PURPLE   = "#a78bfa"
TEAL     = "#2dd4bf"

GRAD = {
    "blue":   "linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%)",
    "green":  "linear-gradient(135deg,#065f46 0%,#0ecb81 100%)",
    "red":    "linear-gradient(135deg,#7f1d1d 0%,#f6465d 100%)",
    "gold":   "linear-gradient(135deg,#78350f 0%,#f0b90b 100%)",
    "purple": "linear-gradient(135deg,#4c1d95 0%,#a78bfa 100%)",
    "teal":   "linear-gradient(135deg,#134e4a 0%,#2dd4bf 100%)",
}


# ============ FORMATLASH ============
def money(v, dec=0):
    if v is None or pd.isna(v):
        return "—"
    a = abs(v); sign = "-" if v < 0 else ""
    if a >= 1_000_000:
        return f"{sign}${a/1_000_000:.2f}M"
    if a >= 1_000:
        return f"{sign}${a/1_000:.1f}K"
    return f"{sign}${a:,.{dec}f}"


def pct(v, dec=1):
    return "—" if v is None or pd.isna(v) else f"{v:.{dec}f}%"


def color_of(v):
    return GREEN if v > 0 else (RED if v < 0 else MUTED)


# ============ MA'LUMOT YUKLASH ============
@st.cache_data(show_spinner=False)
def get_trades():
    return build_trades()


@st.cache_data(show_spinner=False)
def get_account():
    f = EXPORT / "account_info.csv"
    if not f.exists():
        return {}
    return pd.read_csv(f).iloc[0].to_dict()


@st.cache_data(show_spinner=False)
def get_positions():
    f = EXPORT / "positions.csv"
    if not f.exists() or f.stat().st_size == 0:
        return pd.DataFrame()
    p = pd.read_csv(f, parse_dates=["time"])
    if p.empty:
        return p
    p["dir"] = p["type"].map({0: "BUY", 1: "SELL"})
    return p


@st.cache_data(show_spinner=False)
def get_rates():
    f = EXPORT / "rates_EURUSD.csv"
    if not f.exists():
        return pd.DataFrame()
    return pd.read_csv(f, parse_dates=["time"])


@st.cache_data(show_spinner=False)
def get_symbols():
    f = EXPORT / "symbols.csv"
    if not f.exists():
        return pd.DataFrame()
    return pd.read_csv(f)


def data_ready():
    f = EXPORT / "deals_history.csv"
    return f.exists() and f.stat().st_size > 0


# ============ GLOBAL CSS ============
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
    .stApp {{ background:
        radial-gradient(1200px 600px at 100% -10%, rgba(79,140,255,0.08), transparent 60%),
        radial-gradient(1000px 500px at -10% 0%, rgba(167,139,250,0.06), transparent 55%),
        {BG}; }}

    /* sarlavhalar */
    h1,h2,h3 {{ letter-spacing:-0.02em; }}
    .block-container {{ padding-top:2.2rem; padding-bottom:3rem; max-width:1400px; }}

    /* sidebar */
    section[data-testid="stSidebar"] {{ background:{SURFACE}; border-right:1px solid {BORDER}; }}
    section[data-testid="stSidebar"] * {{ color:{TEXT}; }}

    /* KPI kartochka */
    .kpi {{
        background:{SURFACE}; border:1px solid {BORDER}; border-radius:18px;
        padding:18px 20px; position:relative; overflow:hidden; height:100%;
        box-shadow:0 4px 24px rgba(0,0,0,0.25); transition:transform .15s ease, border-color .15s ease;
    }}
    .kpi:hover {{ transform:translateY(-3px); border-color:{BLUE}; }}
    .kpi .bar {{ position:absolute; left:0; top:0; bottom:0; width:5px; }}
    .kpi .ic {{ font-size:20px; opacity:.9; }}
    .kpi .lab {{ color:{MUTED}; font-size:12.5px; font-weight:600; text-transform:uppercase; letter-spacing:.06em; margin-top:6px; }}
    .kpi .val {{ font-size:27px; font-weight:800; line-height:1.15; margin-top:2px; color:{TEXT}; white-space:nowrap; }}
    .kpi .sub {{ font-size:12.5px; font-weight:600; margin-top:4px; }}

    /* hero kartochka */
    .hero {{
        border-radius:22px; padding:26px 30px; color:white; position:relative; overflow:hidden;
        box-shadow:0 8px 40px rgba(0,0,0,0.35);
    }}
    .hero .big {{ font-size:46px; font-weight:800; line-height:1; }}
    .hero .cap {{ font-size:13px; font-weight:600; text-transform:uppercase; letter-spacing:.08em; opacity:.85; }}
    .hero .row {{ display:flex; gap:26px; margin-top:16px; flex-wrap:wrap; }}
    .hero .row div b {{ font-size:18px; font-weight:800; display:block; }}
    .hero .row div span {{ font-size:11.5px; opacity:.8; text-transform:uppercase; letter-spacing:.05em; }}

    /* bo'lim sarlavhasi */
    .sec {{ display:flex; align-items:center; gap:10px; margin:8px 0 14px; }}
    .sec .t {{ font-size:18px; font-weight:700; color:{TEXT}; }}
    .sec .l {{ flex:1; height:1px; background:linear-gradient(90deg,{BORDER},transparent); }}

    /* badge */
    .badge {{ display:inline-block; padding:3px 10px; border-radius:999px; font-size:11.5px; font-weight:700; }}

    /* jadval */
    [data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:14px; }}

    /* metric default tozalash */
    [data-testid="stMetricValue"] {{ font-weight:800; }}
    #MainMenu, footer {{ visibility:hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ============ KOMPONENTLAR ============
def kpi_card(label, value, sub="", grad="blue", icon="•", sub_color=None):
    sub_color = sub_color or MUTED
    sub_html = f'<div class="sub" style="color:{sub_color}">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi">
      <div class="bar" style="background:{GRAD.get(grad, GRAD['blue'])}"></div>
      <div class="ic">{icon}</div>
      <div class="lab">{label}</div>
      <div class="val">{value}</div>
      {sub_html}
    </div>"""


def kpi_row(cards):
    """cards: kpi_card() HTML stringlar ro'yxati -> bir qatorda chiqaradi."""
    cols = st.columns(len(cards))
    for col, html in zip(cols, cards):
        col.markdown(html, unsafe_allow_html=True)


def section(title, icon=""):
    st.markdown(f'<div class="sec"><span class="t">{icon} {title}</span><span class="l"></span></div>',
                unsafe_allow_html=True)


def page_setup(title, icon="📈"):
    st.set_page_config(page_title=f"{title} · Scripe Trade", page_icon=icon, layout="wide")
    inject_css()


def need_data():
    if not data_ready():
        st.error("Ma'lumot topilmadi. Avval terminalda `python main.py` ni ishga tushiring.")
        st.stop()


# ============ PLOTLY DARK SHABLON ============
def _register_template():
    pio.templates["scripe"] = go.layout.Template(
        layout=dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, family="Inter, sans-serif", size=12),
            colorway=[BLUE, GREEN, GOLD, PURPLE, TEAL, RED],
            xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
            yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER),
            margin=dict(l=10, r=10, t=30, b=10),
            hoverlabel=dict(bgcolor=SURFACE2, bordercolor=BORDER, font_size=12),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
    )
    pio.templates.default = "plotly_dark+scripe"


_register_template()
