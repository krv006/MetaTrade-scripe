"""Vaqt tahlili — soat/kun heatmap va vaqt bo'yicha foyda."""
import plotly.graph_objects as go
import streamlit as st

import theme as T
from analytics import hour_weekday_pivot

T.page_setup("Vaqt tahlili", "🕐")
T.need_data()

tr = T.get_trades()

st.title("🕐 Vaqt bo'yicha tahlil")
st.caption("Qaysi soat va kunlarda savdo foydaliroq (server vaqti)")

WD = {"Monday": "Dushanba", "Tuesday": "Seshanba", "Wednesday": "Chorshanba",
      "Thursday": "Payshanba", "Friday": "Juma", "Saturday": "Shanba", "Sunday": "Yakshanba"}

# Heatmap: kun x soat
T.section("Heatmap — Kun × Soat (net foyda)", "🔥")
piv = hour_weekday_pivot(tr)
if not piv.empty:
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[f"{h:02d}" for h in piv.columns],
        y=[WD.get(d, d) for d in piv.index],
        colorscale=[[0, T.RED], [0.5, "#1a2236"], [1, T.GREEN]], zmid=0,
        hovertemplate="Soat %{x}<br>%{y}<br><b>%{z:$,.0f}</b><extra></extra>"))
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    T.section("Soat bo'yicha net foyda", "⏰")
    by_h = tr.groupby("hour")["net"].sum().reindex(range(24), fill_value=0)
    fig = go.Figure(go.Bar(x=[f"{h:02d}" for h in by_h.index], y=by_h.values,
                           marker_color=[T.GREEN if v >= 0 else T.RED for v in by_h.values]))
    fig.update_layout(height=320, xaxis_title="soat", yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    T.section("Hafta kuni bo'yicha", "📅")
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_d = tr.groupby("weekday")["net"].sum().reindex(order).dropna()
    fig = go.Figure(go.Bar(x=[WD[d] for d in by_d.index], y=by_d.values,
                           marker_color=[T.GREEN if v >= 0 else T.RED for v in by_d.values]))
    fig.update_layout(height=320, yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

# Savdo aktivligi soat bo'yicha
T.section("Savdo aktivligi (soat bo'yicha savdolar soni)", "📊")
cnt = tr.groupby("hour").size().reindex(range(24), fill_value=0)
fig = go.Figure(go.Bar(x=[f"{h:02d}" for h in cnt.index], y=cnt.values, marker_color=T.BLUE))
fig.update_layout(height=260, xaxis_title="soat", yaxis_title="savdolar soni")
st.plotly_chart(fig, use_container_width=True)
