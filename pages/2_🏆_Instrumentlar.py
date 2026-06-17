"""Instrumentlar — har bir symbol uchun ALOHIDA KPI va grafiklar."""
import plotly.graph_objects as go
import streamlit as st

import theme as T
from analytics import symbol_breakdown

T.page_setup("Instrumentlar", "🏆")
T.need_data()

tr = T.get_trades()
sb = symbol_breakdown(tr)
syms = T.get_symbols()

st.title("🏆 Instrumentlar bo'yicha tahlil")
st.caption("Har bir savdo qilingan instrument uchun alohida ko'rsatkichlar")

# Umumiy taqqoslash grafiklari
c1, c2 = st.columns(2)
with c1:
    T.section("Symbol bo'yicha net foyda", "💰")
    fig = go.Figure(go.Bar(x=sb["net"], y=sb["symbol"], orientation="h",
                           marker_color=[T.GREEN if v >= 0 else T.RED for v in sb["net"]],
                           text=[T.money(v) for v in sb["net"]], textposition="outside"))
    fig.update_layout(height=300, xaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    T.section("Savdolar soni", "🔢")
    fig = go.Figure(go.Bar(x=sb["trades"], y=sb["symbol"], orientation="h",
                           marker_color=T.BLUE, text=sb["trades"], textposition="outside"))
    fig.update_layout(height=300, xaxis_title="soni")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Har bir symbol uchun ALOHIDA blok
desc_map = {}
if not syms.empty and "name" in syms.columns:
    desc_map = dict(zip(syms["name"], syms.get("description", syms["name"])))

for _, r in sb.iterrows():
    sym = r["symbol"]
    pf = "∞" if r["profit_factor"] == float("inf") else f"{r['profit_factor']:.2f}"
    badge_color = T.GREEN if r["net"] >= 0 else T.RED
    st.markdown(
        f'<div class="sec"><span class="t">{sym}</span>'
        f'<span class="badge" style="background:{badge_color}22;color:{badge_color};margin-left:6px">'
        f'{T.money(r["net"])}</span>'
        f'<span style="color:{T.MUTED};font-size:13px;margin-left:10px">{desc_map.get(sym,"")}</span>'
        f'<span class="l"></span></div>', unsafe_allow_html=True)

    T.kpi_row([
        T.kpi_card("Net foyda", T.money(r["net"]), f"{r['trades']} savdo",
                   "green" if r["net"] >= 0 else "red", "💰", T.color_of(r["net"])),
        T.kpi_card("Win rate", T.pct(r["win_rate"]), grad="blue", icon="🎯"),
        T.kpi_card("Profit factor", pf, grad="purple", icon="⚖️"),
        T.kpi_card("O'rtacha davomiylik", f"{r['avg_duration_min']:.0f} daq", grad="teal", icon="⏱️"),
    ])
    st.write("")
    T.kpi_row([
        T.kpi_card("O'rtacha yutuq", T.money(r["avg_win"]), grad="green", icon="🟢", sub_color=T.GREEN),
        T.kpi_card("O'rtacha zarar", T.money(r["avg_loss"]), grad="red", icon="🔴", sub_color=T.RED),
        T.kpi_card("Eng katta yutuq", T.money(r["best"]), grad="gold", icon="🏆", sub_color=T.GREEN),
        T.kpi_card("Hajm", f"{r['volume']:,.1f} lot", grad="blue", icon="📦"),
    ])

    # shu symbol equity
    sub = tr[tr["symbol"] == sym].sort_values("close_time").copy()
    sub["eq"] = sub["net"].cumsum()
    fig = go.Figure(go.Scatter(x=sub["close_time"], y=sub["eq"], fill="tozeroy",
                               line=dict(color=badge_color, width=2),
                               fillcolor=f"rgba({'14,203,129' if r['net']>=0 else '246,70,93'},0.12)"))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.write("")
