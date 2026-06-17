"""Savdolar jurnali — to'liq jadval, filtrlar, eksport."""
import streamlit as st

import theme as T
from analytics import kpis

T.page_setup("Savdolar jurnali", "📋")
T.need_data()

tr_all = T.get_trades()

st.title("📋 Savdolar jurnali")

# --- Filtrlar ---
st.sidebar.header("Filtrlar")
syms = sorted(tr_all["symbol"].unique())
f_sym = st.sidebar.multiselect("Instrument", syms, default=syms)
f_dir = st.sidebar.multiselect("Yo'nalish", ["BUY", "SELL"], default=["BUY", "SELL"])
f_res = st.sidebar.multiselect("Natija", ["Win", "Loss", "BE"], default=["Win", "Loss", "BE"])
dmin, dmax = tr_all["date"].min(), tr_all["date"].max()
f_date = st.sidebar.date_input("Sana oralig'i", (dmin, dmax), min_value=dmin, max_value=dmax)

tr = tr_all[tr_all["symbol"].isin(f_sym) & tr_all["dir"].isin(f_dir) & tr_all["result"].isin(f_res)]
if isinstance(f_date, tuple) and len(f_date) == 2:
    tr = tr[(tr["date"] >= f_date[0]) & (tr["date"] <= f_date[1])]

if tr.empty:
    st.warning("Filtrga mos savdo yo'q.")
    st.stop()

k = kpis(tr)
st.caption(f"{k['trades']} savdo · net {T.money(k['net'])} · win rate {T.pct(k['win_rate'])}")

# Mini KPI
T.kpi_row([
    T.kpi_card("Savdolar", f"{k['trades']}", grad="blue", icon="🔢"),
    T.kpi_card("Net foyda", T.money(k["net"]), grad="green" if k["net"] >= 0 else "red", icon="💰",
               sub_color=T.color_of(k["net"])),
    T.kpi_card("Win rate", T.pct(k["win_rate"]), grad="purple", icon="🎯"),
    T.kpi_card("Expectancy", T.money(k["expectancy"]), "savdoga", "teal", "📈", T.color_of(k["expectancy"])),
])

st.write("")
T.section("Jadval", "📑")
show = tr[["open_time", "close_time", "symbol", "dir", "volume", "open_price",
           "close_price", "duration_min", "net", "result"]].copy()
show["duration_min"] = show["duration_min"].round(1)
show = show.sort_values("close_time", ascending=False).rename(columns={
    "open_time": "ochilish", "close_time": "yopilish", "dir": "yo'nalish", "volume": "hajm",
    "open_price": "kirish", "close_price": "chiqish", "duration_min": "daq", "net": "net $", "result": "natija"})

st.dataframe(
    show.style
    .map(lambda v: f"color:{T.color_of(v)};font-weight:700", subset=["net $"])
    .format({"net $": "{:,.2f}", "kirish": "{:.5f}", "chiqish": "{:.5f}", "hajm": "{:.2f}"}),
    use_container_width=True, height=520)

st.download_button("⬇️ CSV yuklab olish", show.to_csv(index=False).encode("utf-8"),
                   "scripe_trades.csv", "text/csv")
