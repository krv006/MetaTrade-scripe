"""
Savdo tahlili + vizualizatsiya.
mt5_export/deals_history.cs qav ni o'qib, userndya savdo qilayotganini
tahlil qiladi va analysis/ papkaga grafiklar saqlaydi.

Avval main.py ni ishga tushiring (ma'lumotni eksport qilish uchun).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # GUI'siz, faqat fayl saqlash
import matplotlib.pyplot as plt
from pathlib import Path

IN_FILE  = Path("mt5_export/deals_history.csv")
OUT_DIR  = Path("analysis"); OUT_DIR.mkdir(exist_ok=True)

# MT5 deal turlari
DEAL_TYPE  = {0: "BUY", 1: "SELL", 2: "BALANCE"}


def load():
    d = pd.read_csv(IN_FILE, parse_dates=["time"])
    # faqat real savdolar (balance/credit operatsiyalarini chiqaramiz)
    trades = d[d["type"].isin([0, 1])].copy()
    # yopilgan savdolar = realized profit shu yerda
    closed = trades[trades["entry"] == 1].copy()
    # to'liq natija = profit + swap + commission
    closed["net"] = closed["profit"] + closed["swap"] + closed["commission"]
    closed["dir"] = closed["type"].map(DEAL_TYPE)
    closed["hour"] = closed["time"].dt.hour
    closed["weekday"] = closed["time"].dt.day_name()
    closed = closed.sort_values("time").reset_index(drop=True)
    closed["equity"] = closed["net"].cumsum()
    return d, closed


def summary(d, c):
    wins = c[c["net"] > 0]
    loss = c[c["net"] < 0]
    gross_win = wins["net"].sum()
    gross_loss = abs(loss["net"].sum())
    print("=" * 50)
    print("           SAVDO TAHLILI (HISOBOT)")
    print("=" * 50)
    print(f"Davr:               {c['time'].min()}  ->  {c['time'].max()}")
    print(f"Yopilgan savdolar:  {len(c)}")
    print(f"Net foyda:          {c['net'].sum():,.2f} USD")
    print(f"Win rate:           {100 * len(wins) / len(c):.1f}%  ({len(wins)} yutuq / {len(loss)} zarar)")
    print(f"O'rtacha yutuq:     {wins['net'].mean():,.2f}")
    print(f"O'rtacha zarar:     {loss['net'].mean():,.2f}")
    pf = gross_win / gross_loss if gross_loss else float("inf")
    print(f"Profit factor:      {pf:.2f}   (>1.5 yaxshi)")
    print(f"Eng katta yutuq:    {c['net'].max():,.2f}")
    print(f"Eng katta zarar:    {c['net'].min():,.2f}")
    # max drawdown (eng katta tushish)
    eq = c["equity"]
    dd = (eq - eq.cummax()).min()
    print(f"Max drawdown:       {dd:,.2f}")
    print("-" * 50)
    print("Symbol bo'yicha:")
    by = c.groupby("symbol")["net"].agg(["sum", "count", "mean"]).round(2)
    print(by.to_string())
    print("=" * 50)


def charts(c):
    plt.style.use("seaborn-v0_8-darkgrid")

    # 1) Equity curve (kapital o'sishi)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(c["time"], c["equity"], color="#2563eb", lw=2)
    ax.fill_between(c["time"], c["equity"], alpha=0.15, color="#2563eb")
    ax.set_title("Kapital o'sishi (Equity Curve)")
    ax.set_xlabel("Vaqt"); ax.set_ylabel("Jami net foyda, USD")
    fig.autofmt_xdate(); fig.tight_layout()
    fig.savefig(OUT_DIR / "1_equity_curve.png", dpi=120); plt.close(fig)

    # 2) Symbol bo'yicha net foyda
    by = c.groupby("symbol")["net"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in by.values]
    ax.barh(by.index, by.values, color=colors)
    ax.set_title("Symbol bo'yicha net foyda")
    ax.set_xlabel("USD")
    fig.tight_layout(); fig.savefig(OUT_DIR / "2_profit_by_symbol.png", dpi=120); plt.close(fig)

    # 3) Yutuq/zarar taqsimoti
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(c[c.net > 0]["net"], bins=30, color="#16a34a", alpha=0.7, label="Yutuq")
    ax.hist(c[c.net < 0]["net"], bins=30, color="#dc2626", alpha=0.7, label="Zarar")
    ax.axvline(0, color="black", lw=1)
    ax.set_title("Savdo natijalari taqsimoti")
    ax.set_xlabel("Net foyda, USD"); ax.set_ylabel("Savdolar soni"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT_DIR / "3_pnl_distribution.png", dpi=120); plt.close(fig)

    # 4) Soat bo'yicha net foyda (qaysi vaqtda yaxshi savdo qiladi)
    by_h = c.groupby("hour")["net"].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in by_h.values]
    ax.bar(by_h.index, by_h.values, color=colors)
    ax.set_title("Soat bo'yicha net foyda")
    ax.set_xlabel("Soat (server vaqti)"); ax.set_ylabel("USD")
    fig.tight_layout(); fig.savefig(OUT_DIR / "4_profit_by_hour.png", dpi=120); plt.close(fig)

    # 5) BUY vs SELL
    by_d = c.groupby("dir")["net"].agg(["sum", "count"])
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in by_d["sum"].values]
    ax.bar(by_d.index, by_d["sum"], color=colors)
    for i, (s, n) in enumerate(zip(by_d["sum"], by_d["count"])):
        ax.text(i, s, f"{n} ta", ha="center", va="bottom")
    ax.set_title("BUY va SELL bo'yicha net foyda")
    ax.set_ylabel("USD")
    fig.tight_layout(); fig.savefig(OUT_DIR / "5_buy_vs_sell.png", dpi=120); plt.close(fig)

    print(f"\n5 ta grafik saqlandi -> {OUT_DIR}/")


def main():
    if not IN_FILE.exists():
        raise SystemExit("mt5_export/deals_history.csv topilmadi. Avval: python main.py")
    d, c = load()
    summary(d, c)
    charts(c)


if __name__ == "__main__":
    main()
