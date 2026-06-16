# 📈 Scripe Trade

MetaTrader 5 (Exness) hisobidagi savdo ma'lumotini eksport qilib, **TradeZella uslubidagi** interaktiv, ko'p sahifali dashboard'da tahlil qiladi.

## Ishga tushirish

```powershell
# 1) MT5 dan ma'lumotni eksport qilish (mt5_export/*.csv)
.venv\Scripts\python.exe main.py

# 2) Interaktiv dashboard (http://localhost:8501)
.venv\Scripts\python.exe -m streamlit run dashboard.py
```

`.env` faylida MT5 login/parol/server/yo'l saqlanadi (git'ga tushmaydi).

## Tuzilma

| Fayl | Vazifasi |
|------|----------|
| `main.py` | MT5 → CSV eksport |
| `analytics.py` | Tahlil yadrosi: round-trip savdo, KPI, breakdown |
| `theme.py` | Dizayn yadrosi: ranglar, CSS, komponentlar, Plotly shablon |
| `dashboard.py` | Bosh sahifa — umumiy ko'rinish |
| `pages/` | 7 sahifa: Performance, Instrumentlar, Vaqt, Pozitsiyalar, Savdolar, Bozor, Hisob |
| `analyze.py` | Statik PNG grafiklar (`analysis/`) |

## Sahifalar

- 🏠 **Umumiy ko'rinish** — hero KPI, equity, kunlik PnL
- 📊 **Performance** — drawdown, streak, taqsimot, scatter
- 🏆 **Instrumentlar** — har symbol uchun alohida KPI
- 🕐 **Vaqt tahlili** — kun×soat heatmap
- 💼 **Ochiq pozitsiyalar** — jonli floating PnL
- 📋 **Savdolar jurnali** — filtr + CSV eksport
- 📈 **Bozor** — EURUSD candlestick + MA + volume
- ⚙️ **Hisob** — balans, margin, leverage
