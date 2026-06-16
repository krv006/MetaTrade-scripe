"""
Scripe Trade — Umumiy ko'rinish (Home).
Ishga tushirish:  streamlit run dashboard.py
"""
import plotly.graph_objects as go
import streamlit as st

import theme as T
from analytics import kpis, daily_pnl

T.page_setup("Umumiy ko'rinish", "🏠")
T.need_data()

tr = T.get_trades()
acc = T.get_account()
k = kpis(tr)

# ---------- HERO ----------
net = k["net"]
grad = T.GRAD["green"] if net >= 0 else T.GRAD["red"]
st.markdown(f"""
<div class="hero" style="background:{grad}">
  <div class="cap">Scripe Trade · {acc.get('name','')} · {acc.get('server','')}</div>
  <div class="big">{T.money(net)}</div>
  <div class="cap" style="margin-top:4px">Jami realizatsiya qilingan net foyda</div>
  <div class="row">
    <div><b>{k['trades']}</b><span>Savdolar</span></div>
    <div><b>{T.pct(k['win_rate'])}</b><span>Win rate</span></div>
    <div><b>{'∞' if k['profit_factor']==float('inf') else f"{k['profit_factor']:.2f}"}</b><span>Profit factor</span></div>
    <div><b>{T.money(k['max_drawdown'])}</b><span>Max drawdown</span></div>
    <div><b>{T.money(acc.get('balance',0))}</b><span>Balans</span></div>
    <div><b>{T.money(acc.get('equity',0))}</b><span>Equity</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------- ASOSIY (OPSHI) KPI'lar ----------
T.section("Asosiy ko'rsatkichlar", "📌")
T.kpi_row([
    T.kpi_card("Net foyda", T.money(k["net"]), f"{k['wins']}W / {k['losses']}L", "green" if net >= 0 else "red", "💰",
               T.color_of(net)),
    T.kpi_card("Win rate", T.pct(k["win_rate"]), f"{k['wins']} yutuq", "blue", "🎯"),
    T.kpi_card("Profit factor", "∞" if k["profit_factor"] == float("inf") else f"{k['profit_factor']:.2f}",
               "yutuq/zarar nisbati", "purple", "⚖️"),
    T.kpi_card("Expectancy", T.money(k["expectancy"]), "har savdoga", "teal", "📈",
               T.color_of(k["expectancy"])),
])
st.write("")
T.kpi_row([
    T.kpi_card("O'rtacha yutuq", T.money(k["avg_win"]), "win savdo", "green", "🟢", T.GREEN),
    T.kpi_card("O'rtacha zarar", T.money(k["avg_loss"]), "loss savdo", "red", "🔴", T.RED),
    T.kpi_card("Eng katta yutuq", T.money(k["best"]), "rekord", "gold", "🏆", T.GREEN),
    T.kpi_card("Max win/loss streak", f"{k['max_win_streak']} / {k['max_loss_streak']}", "ketma-ket", "blue", "🔥"),
])

st.write("")

# ---------- EQUITY + KUNLIK PnL ----------
c1, c2 = st.columns([3, 2])

with c1:
    T.section("Kapital o'sishi (Equity)", "📈")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tr["close_time"], y=tr["equity"], mode="lines",
        line=dict(color=T.BLUE, width=2.5), fill="tozeroy",
        fillcolor="rgba(79,140,255,0.12)", name="Equity",
        hovertemplate="%{x|%d-%b %H:%M}<br><b>%{y:$,.0f}</b><extra></extra>"))
    fig.update_layout(height=360, yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    T.section("Kunlik natija", "📅")
    d = daily_pnl(tr)
    fig = go.Figure(go.Bar(
        x=d["date"].astype(str), y=d["net"],
        marker_color=[T.GREEN if v >= 0 else T.RED for v in d["net"]],
        hovertemplate="%{x}<br><b>%{y:$,.0f}</b><extra></extra>"))
    fig.update_layout(height=360, yaxis_title=None, xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

# ---------- SYMBOL ULUSHI ----------
c3, c4 = st.columns(2)
with c3:
    T.section("Symbol bo'yicha foyda ulushi", "🥧")
    by = tr.groupby("symbol")["net"].sum()
    pos = by[by > 0]
    fig = go.Figure(go.Pie(
        labels=pos.index, values=pos.values, hole=.62,
        marker=dict(colors=[T.GOLD, T.TEAL, T.BLUE, T.PURPLE]),
        textinfo="label+percent"))
    fig.update_layout(height=320, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    T.section("Yutuq / Zarar nisbati", "📊")
    fig = go.Figure(go.Bar(
        x=[k["wins"], k["losses"]], y=["Yutuq", "Zarar"], orientation="h",
        marker_color=[T.GREEN, T.RED], text=[k["wins"], k["losses"]], textposition="outside"))
    fig.update_layout(height=320, xaxis_title="savdolar soni")
    st.plotly_chart(fig, use_container_width=True)

st.caption("◂ Chap menyudan boshqa sahifalarga o'ting: Performance · Instrumentlar · Vaqt tahlili · Ochiq pozitsiyalar · Savdolar · Bozor · Hisob")
