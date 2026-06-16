"""
Tahlil yadrosi (core).
MT5 deals_history.csv ni o'qib, round-trip savdolarni yig'adi va
barcha metrikalarni hisoblaydi. dashboard.py va analyze.py shu moduldan foydalanadi.
"""
from pathlib import Path
import pandas as pd

DEALS_FILE = Path("mt5_export/deals_history.csv")


def build_trades(deals_path: Path = DEALS_FILE) -> pd.DataFrame:
    """deals_history dan round-trip savdolar jadvalini quradi (1 qator = 1 savdo)."""
    d = pd.read_csv(deals_path, parse_dates=["time"])
    t = d[d["type"].isin([0, 1])].copy()  # 0=BUY, 1=SELL (balance emas)

    rows = []
    for pid, x in t.groupby("position_id"):
        ins = x[x["entry"] == 0]   # kirish dealari
        outs = x[x["entry"] == 1]  # chiqish dealari
        if ins.empty or outs.empty:
            continue
        vol = ins["volume"].sum()
        open_px = (ins["price"] * ins["volume"]).sum() / vol if vol else 0
        out_vol = outs["volume"].sum()
        close_px = (outs["price"] * outs["volume"]).sum() / out_vol if out_vol else 0
        rows.append({
            "position_id": pid,
            "symbol": x["symbol"].iloc[0],
            "dir": "BUY" if ins["type"].iloc[0] == 0 else "SELL",
            "open_time": ins["time"].min(),
            "close_time": outs["time"].max(),
            "volume": vol,
            "open_price": round(open_px, 5),
            "close_price": round(close_px, 5),
            "profit": x["profit"].sum(),
            "commission": x["commission"].sum(),
            "swap": x["swap"].sum(),
            "net": x["profit"].sum() + x["swap"].sum() + x["commission"].sum(),
        })

    tr = pd.DataFrame(rows).sort_values("close_time").reset_index(drop=True)
    if tr.empty:
        return tr
    tr["duration_min"] = (tr["close_time"] - tr["open_time"]).dt.total_seconds() / 60
    tr["result"] = tr["net"].apply(lambda v: "Win" if v > 0 else ("Loss" if v < 0 else "BE"))
    tr["hour"] = tr["close_time"].dt.hour
    tr["weekday"] = tr["close_time"].dt.day_name()
    tr["date"] = tr["close_time"].dt.date
    tr["equity"] = tr["net"].cumsum()
    tr["peak"] = tr["equity"].cummax()
    tr["drawdown"] = tr["equity"] - tr["peak"]
    return tr


def kpis(tr: pd.DataFrame) -> dict:
    """Asosiy KPI'lar (TradeZella uslubidagi)."""
    if tr.empty:
        return {}
    wins = tr[tr["net"] > 0]
    loss = tr[tr["net"] < 0]
    gross_win = wins["net"].sum()
    gross_loss = abs(loss["net"].sum())

    # ketma-ket streak
    streak = max_win_streak = max_loss_streak = 0
    last = None
    for r in tr["result"]:
        if r == last:
            streak += 1
        else:
            streak = 1
            last = r
        if r == "Win":
            max_win_streak = max(max_win_streak, streak)
        elif r == "Loss":
            max_loss_streak = max(max_loss_streak, streak)

    return {
        "trades": len(tr),
        "net": tr["net"].sum(),
        "win_rate": 100 * len(wins) / len(tr),
        "wins": len(wins),
        "losses": len(loss),
        "avg_win": wins["net"].mean() if len(wins) else 0,
        "avg_loss": loss["net"].mean() if len(loss) else 0,
        "profit_factor": gross_win / gross_loss if gross_loss else float("inf"),
        "expectancy": tr["net"].mean(),
        "best": tr["net"].max(),
        "worst": tr["net"].min(),
        "max_drawdown": tr["drawdown"].min(),
        "avg_duration_min": tr["duration_min"].mean(),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "total_volume": tr["volume"].sum(),
        "total_commission": tr["commission"].sum(),
        "total_swap": tr["swap"].sum(),
    }


def symbol_breakdown(tr: pd.DataFrame) -> pd.DataFrame:
    """Har bir symbol uchun alohida metrikalar jadvali."""
    if tr.empty:
        return pd.DataFrame()
    rows = []
    for sym, x in tr.groupby("symbol"):
        wins = x[x["net"] > 0]
        loss = x[x["net"] < 0]
        gl = abs(loss["net"].sum())
        rows.append({
            "symbol": sym,
            "trades": len(x),
            "net": x["net"].sum(),
            "win_rate": 100 * len(wins) / len(x),
            "profit_factor": (wins["net"].sum() / gl) if gl else float("inf"),
            "avg_win": wins["net"].mean() if len(wins) else 0,
            "avg_loss": loss["net"].mean() if len(loss) else 0,
            "best": x["net"].max(),
            "worst": x["net"].min(),
            "volume": x["volume"].sum(),
            "avg_duration_min": x["duration_min"].mean(),
        })
    return pd.DataFrame(rows).sort_values("net", ascending=False).reset_index(drop=True)


def hour_weekday_pivot(tr: pd.DataFrame) -> pd.DataFrame:
    """Soat x hafta-kuni net foyda matritsasi (heatmap uchun)."""
    if tr.empty:
        return pd.DataFrame()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    p = tr.pivot_table(index="weekday", columns="hour", values="net", aggfunc="sum", fill_value=0)
    return p.reindex([d for d in order if d in p.index])


def daily_pnl(tr: pd.DataFrame) -> pd.DataFrame:
    """Kunlik net foyda."""
    if tr.empty:
        return pd.DataFrame()
    g = tr.groupby("date").agg(net=("net", "sum"), trades=("net", "size")).reset_index()
    g["cum"] = g["net"].cumsum()
    return g


if __name__ == "__main__":
    tr = build_trades()
    print(f"Savdolar: {len(tr)}")
    for k, v in kpis(tr).items():
        print(f"  {k:18}: {v:,.2f}" if isinstance(v, float) else f"  {k:18}: {v}")
