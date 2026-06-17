"""Bozor — EURUSD candlestick va narx tahlili."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import theme as T

T.page_setup("Bozor", "📈")

r = T.get_rates()

st.title("📈 Bozor — EURUSD (D1)")

if r.empty:
    st.info("rates_EURUSD.csv topilmadi. `python main.py` ni ishga tushiring.")
    st.stop()

last = r.iloc[-1]
prev = r.iloc[-2]
chg = last["close"] - prev["close"]
chg_pct = 100 * chg / prev["close"]

st.caption(f"{len(r)} kunlik shamlar · {r['time'].min():%d-%b-%Y} → {r['time'].max():%d-%b-%Y}")

T.kpi_row([
    T.kpi_card("Oxirgi narx", f"{last['close']:.5f}", f"{chg:+.5f} ({chg_pct:+.2f}%)",
               "green" if chg >= 0 else "red", "💱", T.color_of(chg)),
    T.kpi_card("Kun maksimumi", f"{last['high']:.5f}", grad="gold", icon="⬆️"),
    T.kpi_card("Kun minimumi", f"{last['low']:.5f}", grad="purple", icon="⬇️"),
    T.kpi_card("Davr diapazoni", f"{r['high'].max():.4f} – {r['low'].min():.4f}", grad="blue", icon="📏"),
])

st.write("")
T.section("Candlestick + Volume", "🕯️")

# moving averages
r = r.copy()
r["ma20"] = r["close"].rolling(20).mean()
r["ma50"] = r["close"].rolling(50).mean()

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                    row_heights=[0.75, 0.25])
fig.add_trace(go.Candlestick(
    x=r["time"], open=r["open"], high=r["high"], low=r["low"], close=r["close"],
    increasing_line_color=T.GREEN, decreasing_line_color=T.RED, name="EURUSD"), row=1, col=1)
fig.add_trace(go.Scatter(x=r["time"], y=r["ma20"], line=dict(color=T.GOLD, width=1.3), name="MA20"), row=1, col=1)
fig.add_trace(go.Scatter(x=r["time"], y=r["ma50"], line=dict(color=T.PURPLE, width=1.3), name="MA50"), row=1, col=1)
fig.add_trace(go.Bar(x=r["time"], y=r["tick_volume"], marker_color=T.BLUE, name="Volume", opacity=.5), row=2, col=1)
fig.update_layout(height=560, xaxis_rangeslider_visible=False, legend=dict(orientation="h", y=1.05))
st.plotly_chart(fig, use_container_width=True)

T.section("Kunlik o'zgarish (%)", "📉")
r["ret"] = r["close"].pct_change() * 100
fig = go.Figure(go.Bar(x=r["time"], y=r["ret"],
                       marker_color=[T.GREEN if v >= 0 else T.RED for v in r["ret"].fillna(0)]))
fig.update_layout(height=260, yaxis_title="%")
st.plotly_chart(fig, use_container_width=True)
