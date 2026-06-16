# 📈 Scripe Trade

**MetaTrader 5** (Exness) hisobidagi savdo ma'lumotini eksport qilib, **TradeZella uslubidagi** interaktiv, ko'p sahifali dashboard'da tahlil qiladigan tizim.

> Win rate, profit factor, equity curve, drawdown, instrument tahlili, vaqt heatmap, P&L kalendari va boshqalar — barchasi o'zingizning MT5 hisobingiz uchun, lokal va bepul.

---

## 📦 Talablar

- **Windows** (MetaTrader5 Python kutubxonasi faqat Windows'da ishlaydi)
- **Python 3.10+**
- **MetaTrader 5 terminali** o'rnatilgan bo'lishi kerak (Exness yoki boshqa broker)
- MT5 hisob ma'lumotlari: login, parol, server

---

## 🚀 O'rnatish

### 1. Repozitoriyni oching va virtual muhit yarating

```powershell
cd C:\Users\user\PycharmProjects\Scripe_Trade

# virtual muhit (agar yo'q bo'lsa)
python -m venv .venv
```

### 2. Kutubxonalarni o'rnating

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. `.env` faylini sozlang

Loyiha papkasida `.env` faylini yarating (yoki tahrirlang) va o'z MT5 ma'lumotlaringizni kiriting:

```env
MT5_LOGIN=login
MT5_PASSWORD="parolingiz"
MT5_SERVER=Exness-MT5Trial15
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
HISTORY_DAYS=365
```

| O'zgaruvchi | Tavsif |
|-------------|--------|
| `MT5_LOGIN` | MT5 hisob raqami |
| `MT5_PASSWORD` | MT5 paroli (qo'shtirnoq ichida) |
| `MT5_SERVER` | Broker serveri (masalan `Exness-MT5Trial15`) |
| `MT5_PATH` | `terminal64.exe` ga to'liq yo'l |
| `HISTORY_DAYS` | Necha kunlik tarix yuklanadi (standart 365) |

> ⚠️ `terminal64.exe` yo'lini topish: MT5 terminalni oching → odatda `C:\Program Files\MetaTrader 5\terminal64.exe`. Exness'niki boshqa papkada bo'lishi mumkin.

> 🔒 `.env` fayli `.gitignore` da — parolingiz git'ga tushmaydi.

---

## ▶️ Ishga tushirish

Ikki bosqich:

### 1-bosqich — Ma'lumotni eksport qilish (MT5 → CSV)

```powershell
.venv\Scripts\python.exe main.py
```

Bu `mt5_export/` papkaga 7 ta CSV fayl yaratadi:
`account_info`, `positions`, `orders_open`, `orders_history`, `deals_history`, `symbols`, `rates_EURUSD`.

> MT5 terminali ochiq bo'lishi shart emas — skript o'zi ishga tushiradi.

### 2-bosqich — Dashboard'ni ochish

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard.py
```

Brauzerda avtomatik ochiladi: **http://localhost:8501**

Chap menyudan sahifalar orasida o'ting.

### Qo'shimcha — statik PNG grafiklar (ixtiyoriy)

```powershell
.venv\Scripts\python.exe analyze.py
```

`analysis/` papkaga 5 ta PNG grafik saqlaydi (equity, symbol, taqsimot, soat, buy/sell).

### Ulanishni tekshirish (debug)

```powershell
.venv\Scripts\python.exe test.py
```

`True (1, 'Success')` chiqsa — ulanish ishlayapti.

---

## 🗂 Loyiha tuzilmasi

```
Scripe_Trade/
├── main.py              # MT5 → CSV eksport
├── analytics.py         # Tahlil yadrosi (round-trip savdo, KPI, breakdown)
├── theme.py             # Dizayn yadrosi (ranglar, CSS, komponentlar, Plotly shablon)
├── dashboard.py         # Bosh sahifa — umumiy ko'rinish
├── analyze.py           # Statik matplotlib grafiklar
├── test.py              # MT5 ulanishni tekshirish
├── requirements.txt     # Kutubxonalar
├── .env                 # MT5 maxfiy ma'lumotlar (git'ga tushmaydi)
├── .streamlit/
│   └── config.toml      # Streamlit dark tema
├── pages/               # Dashboard sahifalari
│   ├── 1_📊_Performance.py
│   ├── 2_🏆_Instrumentlar.py
│   ├── 3_🕐_Vaqt_tahlili.py
│   ├── 4_💼_Ochiq_pozitsiyalar.py
│   ├── 5_📋_Savdolar.py
│   ├── 6_📈_Bozor.py
│   ├── 7_⚙️_Hisob.py
│   └── 8_📅_Kalendar.py
├── mt5_export/          # Eksport qilingan CSV'lar (main.py yaratadi)
└── analysis/            # Statik PNG grafiklar (analyze.py yaratadi)
```

---

## 📑 Dashboard sahifalari

| Sahifa | Mazmun |
|--------|--------|
| 🏠 **Umumiy ko'rinish** | Hero KPI, equity curve, kunlik P&L, symbol ulushi |
| 📊 **Performance** | Drawdown, streak, natija taqsimoti, davomiylik vs natija |
| 🏆 **Instrumentlar** | Har bir symbol uchun **alohida KPI** va mini equity |
| 🕐 **Vaqt tahlili** | Kun × soat **heatmap**, soat/kun bo'yicha foyda |
| 💼 **Ochiq pozitsiyalar** | Jonli floating P&L, ochiq savdolar jadvali |
| 📋 **Savdolar jurnali** | To'liq jadval + filtrlar (symbol/yo'nalish/sana) + CSV eksport |
| 📈 **Bozor** | EURUSD candlestick + MA20/MA50 + volume |
| ⚙️ **Hisob** | Balans, equity, margin, leverage |
| 📅 **Kalendar** | Oylik P&L kalendari; kun bosilganda o'sha kun bitimlari + statistika |

---

## 📊 Metrikalar haqida

- **Round-trip savdo** — kirish va chiqish bitimlari `position_id` bo'yicha birlashtiriladi (1 savdo = 1 qator).
- **Net** = `profit + swap + commission`.
- **Win rate** = yutuq savdolar foizi.
- **Profit factor** = jami yutuq / jami zarar (>1.5 yaxshi hisoblanadi).
- **Expectancy** = har bir savdoning o'rtacha natijasi.
- **Max drawdown** = equity'ning eng katta tushishi.

---

## 🔄 Ma'lumotni yangilash

Yangi savdolar qo'shilganda dashboard'ni yangilash uchun:

1. `main.py` ni qayta ishga tushiring (yangi CSV).
2. Dashboard'da yuqori-o'ng burchakdagi menyu → **Rerun** (yoki `R` tugmasi), kerak bo'lsa cache'ni tozalang (**Clear cache**).

---

## 🛠 Muammolarni hal qilish

| Muammo | Yechim |
|--------|--------|
| `initialize() failed ... Authorization failed` | `.env` da login/parol/server to'g'riligini tekshiring |
| `IPC initialize failed ... terminal64.exe` | `MT5_PATH` noto'g'ri — to'g'ri yo'lni ko'rsating |
| `mt5_export/...csv topilmadi` | Avval `python main.py` ni ishga tushiring |
| `No module named ...` | `pip install -r requirements.txt` |
| Port band (8501) | `streamlit run dashboard.py --server.port 8502` |

---

## 🔜 Keyingi rejalar

- 🤖 **AI tahlil** — Claude API bilan savdo patternlari va tavsiyalar ("Zella AI" analogi)
- 📝 **Journaling** — har savdoga eslatma, strategiya teg, skrinshot (SQLite)
- 📐 **R-Multiple / MAE-MFE** — risk-reward va savdo ichidagi maksimal yo'qotish/foyda
- ⏱ **Real-time** — MT5 dan avtomatik yangilanish
