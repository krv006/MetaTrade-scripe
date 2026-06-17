"""Hisob — account ma'lumotlari va margin holati."""
import plotly.graph_objects as go
import streamlit as st

import theme as T

T.page_setup("Hisob", "⚙️")

acc = T.get_account()

st.title("⚙️ Hisob ma'lumotlari")

if not acc:
    st.info("account_info.csv topilmadi.")
    st.stop()

st.caption(f"{acc.get('name','')} · {acc.get('company','')} · {acc.get('server','')}")

T.kpi_row([
    T.kpi_card("Balans", T.money(acc.get("balance", 0)), grad="blue", icon="🏦"),
    T.kpi_card("Equity", T.money(acc.get("equity", 0)), grad="green", icon="💎"),
    T.kpi_card("Floating PnL", T.money(acc.get("profit", 0)), grad="green" if acc.get("profit", 0) >= 0 else "red",
               icon="💵", sub_color=T.color_of(acc.get("profit", 0))),
    T.kpi_card("Leverage", f"1:{int(acc.get('leverage', 0))}", grad="gold", icon="⚡"),
])
st.write("")
T.kpi_row([
    T.kpi_card("Margin", T.money(acc.get("margin", 0)), grad="purple", icon="🔒"),
    T.kpi_card("Free margin", T.money(acc.get("margin_free", 0)), grad="teal", icon="🔓"),
    T.kpi_card("Margin level", f"{acc.get('margin_level', 0):,.0f}%", grad="blue", icon="📐"),
    T.kpi_card("Valyuta", f"{acc.get('currency', '')}", grad="gold", icon="💱"),
])

st.write("")
c1, c2 = st.columns([1, 1])

with c1:
    T.section("Margin holati", "🔒")
    margin = acc.get("margin", 0)
    free = acc.get("margin_free", 0)
    fig = go.Figure(go.Pie(labels=["Band margin", "Bo'sh margin"], values=[margin, free], hole=.62,
                           marker=dict(colors=[T.GOLD, T.GREEN])))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    T.section("Balans vs Equity", "⚖️")
    fig = go.Figure(go.Bar(x=["Balans", "Equity"], y=[acc.get("balance", 0), acc.get("equity", 0)],
                           marker_color=[T.BLUE, T.GREEN],
                           text=[T.money(acc.get("balance", 0)), T.money(acc.get("equity", 0))],
                           textposition="outside"))
    fig.update_layout(height=300, yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

T.section("To'liq ma'lumot", "📋")
import pandas as pd
df = pd.DataFrame(list(acc.items()), columns=["Maydon", "Qiymat"])
st.dataframe(df, use_container_width=True, height=420, hide_index=True)
