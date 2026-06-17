"""Ochiq pozitsiyalar — jonli ochiq savdolar va floating PnL."""
import plotly.graph_objects as go
import streamlit as st

import theme as T

T.page_setup("Ochiq pozitsiyalar", "💼")

pos = T.get_positions()
acc = T.get_account()

st.title("💼 Ochiq pozitsiyalar")

if pos.empty:
    st.info("Hozir ochiq pozitsiya yo'q.")
    st.stop()

floating = pos["profit"].sum() + pos["swap"].sum()
st.caption(f"{len(pos)} ta ochiq pozitsiya · floating PnL: {T.money(floating)}")

T.kpi_row([
    T.kpi_card("Ochiq pozitsiyalar", f"{len(pos)}", grad="blue", icon="📂"),
    T.kpi_card("Floating PnL", T.money(floating), grad="green" if floating >= 0 else "red", icon="💵",
               sub_color=T.color_of(floating)),
    T.kpi_card("Umumiy hajm", f"{pos['volume'].sum():,.2f} lot", grad="gold", icon="📦"),
    T.kpi_card("Margin band", T.money(acc.get("margin", 0)), f"free: {T.money(acc.get('margin_free',0))}",
               "purple", "🔒"),
])

st.write("")
c1, c2 = st.columns([3, 2])

with c1:
    T.section("Pozitsiyalar jadvali", "📋")
    show = pos[["symbol", "dir", "volume", "price_open", "price_current", "sl", "tp", "swap", "profit", "time"]].copy()
    show = show.rename(columns={"dir": "yo'nalish", "volume": "hajm", "price_open": "ochilish",
                                "price_current": "joriy", "profit": "PnL", "time": "vaqt"})
    st.dataframe(
        show.style
        .map(lambda v: f"color:{T.color_of(v)};font-weight:700", subset=["PnL"])
        .format({"PnL": "{:,.2f}", "swap": "{:,.2f}"}),
        use_container_width=True, height=360)

with c2:
    T.section("Symbol bo'yicha floating PnL", "📊")
    by = pos.groupby("symbol")["profit"].sum().sort_values()
    fig = go.Figure(go.Bar(x=by.values, y=by.index, orientation="h",
                           marker_color=[T.GREEN if v >= 0 else T.RED for v in by.values],
                           text=[T.money(v) for v in by.values], textposition="outside"))
    fig.update_layout(height=360, xaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

# BUY/SELL taqsimot
T.section("Yo'nalish taqsimoti", "🧭")
c3, c4 = st.columns(2)
with c3:
    cnt = pos["dir"].value_counts()
    fig = go.Figure(go.Pie(labels=cnt.index, values=cnt.values, hole=.6,
                           marker=dict(colors=[T.GREEN, T.RED])))
    fig.update_layout(height=280, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
with c4:
    vol = pos.groupby("dir")["volume"].sum()
    fig = go.Figure(go.Bar(x=vol.index, y=vol.values, marker_color=[T.GREEN, T.RED],
                           text=[f"{v:.2f}" for v in vol.values], textposition="outside"))
    fig.update_layout(height=280, yaxis_title="lot")
    st.plotly_chart(fig, use_container_width=True)
