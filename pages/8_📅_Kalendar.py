"""Kalendar — oylik P&L kalendari (TradeZella uslubida). Kunni bosganda tafsilot."""
import calendar as cal
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import theme as T
from analytics import day_stats

T.page_setup("Kalendar", "📅")
T.need_data()

tr = T.get_trades().copy()
tr["d"] = pd.to_datetime(tr["date"])

# ---------- Kalendar maxsus CSS ----------
st.markdown(f"""
<style>
.st-key-cal [data-testid="column"] {{ padding:3px !important; }}
/* kun tugmasi (savdo bo'lgan kun) */
.st-key-cal button {{
   height:104px !important; width:100% !important; border-radius:12px !important;
   white-space:pre-line !important; text-align:left !important;
   align-items:flex-start !important; justify-content:flex-start !important;
   font-weight:700 !important; line-height:1.3 !important; padding:8px 10px !important;
   transition:transform .12s ease !important;
}}
.st-key-cal button:hover {{ transform:translateY(-2px); }}
/* yutuq kuni = primary */
.st-key-cal [data-testid="stBaseButton-primary"] {{
   background:linear-gradient(135deg,rgba(6,95,70,.45),rgba(14,203,129,.30)) !important;
   border:1px solid {T.GREEN} !important; color:#d6ffe9 !important;
}}
/* zarar kuni = secondary */
.st-key-cal [data-testid="stBaseButton-secondary"] {{
   background:linear-gradient(135deg,rgba(127,29,29,.45),rgba(246,70,93,.25)) !important;
   border:1px solid {T.RED} !important; color:#ffd9df !important;
}}
.calempty {{ height:104px; border:1px solid {T.BORDER}; border-radius:12px;
   background:{T.SURFACE}; color:{T.MUTED}; padding:8px 10px; font-weight:700; opacity:.55; }}
.calblank {{ height:104px; }}
.calhead {{ text-align:center; color:{T.MUTED}; font-weight:700; font-size:12px;
   text-transform:uppercase; letter-spacing:.05em; padding:6px 0; }}
</style>
""", unsafe_allow_html=True)

# ---------- Oy holati ----------
maxd = tr["d"].max()
if "cal_y" not in st.session_state:
    st.session_state.cal_y, st.session_state.cal_m = int(maxd.year), int(maxd.month)


def shift(delta):
    m = st.session_state.cal_m + delta
    y = st.session_state.cal_y + (m - 1) // 12
    st.session_state.cal_y, st.session_state.cal_m = y, (m - 1) % 12 + 1


# ---------- Sarlavha + navigatsiya ----------
nav = st.columns([1, 1, 4, 2, 4])
nav[0].button("◀", on_click=shift, args=(-1,), use_container_width=True)
nav[1].button("▶", on_click=shift, args=(1,), use_container_width=True)
y, m = st.session_state.cal_y, st.session_state.cal_m
nav[2].markdown(f"### {cal.month_name[m]} {y}")
if nav[3].button("Bu oy", use_container_width=True):
    st.session_state.cal_y, st.session_state.cal_m = int(maxd.year), int(maxd.month)
    st.rerun()

# shu oydagi savdolar
mon = tr[(tr["d"].dt.year == y) & (tr["d"].dt.month == m)]
month_net = mon["net"].sum()
nav[4].markdown(f"### <span style='color:{T.color_of(month_net)}'>{T.money(month_net)}</span> "
                f"<span style='font-size:13px;color:{T.MUTED}'>· {len(mon)} savdo</span>",
                unsafe_allow_html=True)

# kunlik agregatsiya
by_day = mon.groupby(mon["d"].dt.day).agg(net=("net", "sum"), n=("net", "size")).to_dict("index")


# ---------- Kun dialogi ----------
@st.dialog("Kun tafsiloti", width="large")
def day_dialog(d_obj):
    day_tr = tr[tr["d"].dt.date == d_obj].sort_values("open_time")
    s = day_stats(day_tr)
    net = s["net"]
    st.markdown(
        f"### {d_obj:%a, %b %d, %Y} &nbsp; "
        f"<span style='color:{T.color_of(net)};font-size:18px'>Net P&L {T.money(net, 2)}</span>",
        unsafe_allow_html=True)

    # mini equity + stats
    cL, cR = st.columns([1, 1])
    with cL:
        eq = day_tr["net"].cumsum()
        fig = go.Figure(go.Scatter(
            x=list(range(1, len(eq) + 1)), y=eq, fill="tozeroy",
            line=dict(color=T.color_of(net), width=2),
            fillcolor=f"rgba({'14,203,129' if net>=0 else '246,70,93'},0.15)"))
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0),
                          xaxis_title="savdo #", yaxis_title="$")
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        a, b = st.columns(2)
        a.metric("Total Trades", s["trades"])
        b.metric("Gross P&L", T.money(s["gross"], 0))
        a.metric("Winners / Losers", f"{s['winners']} / {s['losers']}")
        b.metric("Commissions", T.money(s["commission"], 2))
        a.metric("Win Rate", T.pct(s["win_rate"]))
        b.metric("Profit Factor", "∞" if s["profit_factor"] == float("inf") else f"{s['profit_factor']:.2f}")
        a.metric("Volume", f"{s['volume']:,.2f}")
        b.metric("Swap", T.money(s["swap"], 2))
    st.markdown(
        f"<div style='color:{T.MUTED};font-size:13px;margin-top:4px'>"
        f"Eng katta yutuq: <b style='color:{T.GREEN}'>{T.money(s['best'],0)}</b> &nbsp;·&nbsp; "
        f"Eng katta zarar: <b style='color:{T.RED}'>{T.money(s['worst'],0)}</b></div>",
        unsafe_allow_html=True)

    st.divider()
    # bitimlar jadvali
    tbl = day_tr.copy()
    tbl["Side"] = tbl["dir"].map({"BUY": "LONG", "SELL": "SHORT"})
    tbl["Open time"] = tbl["open_time"].dt.strftime("%H:%M:%S")
    tbl["R-Multiple"] = "—"
    tbl["Strategy"] = "—"
    out = tbl[["Open time", "symbol", "Side", "duration_min", "open_price", "close_price", "net"]].rename(
        columns={"symbol": "Ticker", "duration_min": "Daq", "open_price": "Kirish",
                 "close_price": "Chiqish", "net": "Net P&L"})
    st.dataframe(
        out.style
        .map(lambda v: f"color:{T.color_of(v)};font-weight:700", subset=["Net P&L"])
        .format({"Net P&L": "{:,.2f}", "Kirish": "{:.5f}", "Chiqish": "{:.5f}", "Daq": "{:.1f}"}),
        use_container_width=True, height=360, hide_index=True)


# ---------- Kalendar grid ----------
st.write("")
grid = st.container(key="cal")
with grid:
    # sarlavha qatori (hafta kunlari, Sun-first)
    heads = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hc = st.columns(7)
    for col, h in zip(hc, heads):
        col.markdown(f"<div class='calhead'>{h}</div>", unsafe_allow_html=True)

    weeks = cal.Calendar(firstweekday=6).monthdayscalendar(y, m)  # 6 = Sunday
    for week in weeks:
        cols = st.columns(7)
        for col, day in zip(cols, week):
            if day == 0:
                col.markdown("<div class='calblank'></div>", unsafe_allow_html=True)
                continue
            if day in by_day:
                info = by_day[day]
                label = f"{day}\n{T.money(info['net'])}\n{info['n']} savdo"
                btype = "primary" if info["net"] >= 0 else "secondary"
                if col.button(label, key=f"day_{y}_{m}_{day}", type=btype, use_container_width=True):
                    day_dialog(date(y, m, day))
            else:
                col.markdown(f"<div class='calempty'>{day}</div>", unsafe_allow_html=True)

st.caption("💡 Rangli kunni bosing — o'sha kunning to'liq tafsiloti va bitimlari ochiladi.")
