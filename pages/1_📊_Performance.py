"""Performance — chuqur metrikalar, drawdown, streak, taqsimot."""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

import theme as T
from analytics import kpis

T.page_setup("Performance", "📊")
T.need_data()

tr = T.get_trades()
k = kpis(tr)

st.title("📊 Performance tahlili")
st.caption(f"{k['trades']} savdo · {tr['open_time'].min():%d-%b %Y} → {tr['close_time'].max():%d-%b %Y}")

# KPI'lar
T.kpi_row([
    T.kpi_card("Net foyda", T.money(k["net"]), grad="green" if k["net"] >= 0 else "red", icon="💰",
               sub_color=T.color_of(k["net"])),
    T.kpi_card("Profit factor", "∞" if k["profit_factor"] == float("inf") else f"{k['profit_factor']:.2f}",
               grad="purple", icon="⚖️"),
    T.kpi_card("Expectancy", T.money(k["expectancy"]), "savdoga", "teal", "📈", T.color_of(k["expectancy"])),
    T.kpi_card("Max drawdown", T.money(k["max_drawdown"]), grad="red", icon="📉", sub_color=T.RED),
])
st.write("")
T.kpi_row([
    T.kpi_card("O'rtacha davomiylik", f"{k['avg_duration_min']:.0f} daq", grad="blue", icon="⏱️"),
    T.kpi_card("Umumiy hajm", f"{k['total_volume']:,.1f} lot", grad="gold", icon="📦"),
    T.kpi_card("Komissiya", T.money(k["total_commission"]), grad="blue", icon="🧾"),
    T.kpi_card("Swap", T.money(k["total_swap"]), grad="purple", icon="🔄", sub_color=T.color_of(k["total_swap"])),
])

st.write("")
c1, c2 = st.columns(2)

with c1:
    T.section("Equity + Drawdown", "📈")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tr["close_time"], y=tr["equity"], name="Equity",
                             line=dict(color=T.BLUE, width=2), fill="tozeroy",
                             fillcolor="rgba(79,140,255,0.10)"))
    fig.add_trace(go.Scatter(x=tr["close_time"], y=tr["peak"], name="Peak",
                             line=dict(color=T.GREEN, width=1, dash="dot")))
    fig.update_layout(height=340)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    T.section("Drawdown (underwater)", "🌊")
    fig = go.Figure(go.Scatter(x=tr["close_time"], y=tr["drawdown"], fill="tozeroy",
                               line=dict(color=T.RED, width=1.2),
                               fillcolor="rgba(246,70,93,0.18)"))
    fig.update_layout(height=340, yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    T.section("Natijalar taqsimoti", "📊")
    fig = px.histogram(tr, x="net", nbins=45, color="result",
                       color_discrete_map={"Win": T.GREEN, "Loss": T.RED, "BE": T.MUTED})
    fig.update_layout(height=330, xaxis_title="Net foyda, $", yaxis_title="soni", legend_title=None,
                      bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    T.section("Savdo davomiyligi vs natija", "⏱️")
    fig = px.scatter(tr, x="duration_min", y="net", color="result", size="volume",
                     color_discrete_map={"Win": T.GREEN, "Loss": T.RED, "BE": T.MUTED},
                     hover_data=["symbol"])
    fig.update_layout(height=330, xaxis_title="davomiylik (daq)", yaxis_title="net $", legend_title=None)
    st.plotly_chart(fig, use_container_width=True)

# Streak vizual
T.section("Ketma-ket natijalar (streak)", "🔥")
colors = [T.GREEN if v > 0 else (T.RED if v < 0 else T.MUTED) for v in tr["net"]]
fig = go.Figure(go.Bar(x=list(range(1, len(tr) + 1)), y=tr["net"], marker_color=colors,
                       hovertemplate="#%{x}<br>%{y:$,.0f}<extra></extra>"))
fig.update_layout(height=260, xaxis_title="savdo tartibi", yaxis_title="net $")
st.plotly_chart(fig, use_container_width=True)
