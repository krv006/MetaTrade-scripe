import os
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# ---- Konfiguratsiya (.env dan o'qiladi) ----
load_dotenv()
LOGIN    = int(os.getenv("MT5_LOGIN"))
PASSWORD = os.getenv("MT5_PASSWORD")
SERVER   = os.getenv("MT5_SERVER")
MT5_PATH = os.getenv("MT5_PATH")  # terminal64.exe yo'li
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", "365"))
OUT_DIR = Path("mt5_export"); OUT_DIR.mkdir(exist_ok=True)


def connect():
    if not mt5.initialize(path=MT5_PATH, login=LOGIN, password=PASSWORD, server=SERVER):
        raise RuntimeError(f"initialize() failed: {mt5.last_error()}")
    print("Connected:", mt5.version())



def to_df(records):
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(list(records), columns=records[0]._asdict().keys())
    for col in [c for c in df.columns if c.startswith("time")]:
        df[col] = pd.to_datetime(df[col], unit="s")
    return df


def save(df, name):
    path = OUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  {name}: {len(df)} rows -> {path}")


def export_all():
    info = mt5.account_info()
    save(pd.DataFrame([info._asdict()]) if info else pd.DataFrame(), "account_info")
    save(to_df(mt5.positions_get()), "positions")
    save(to_df(mt5.orders_get()), "orders_open")

    frm, to = datetime.now() - timedelta(days=HISTORY_DAYS), datetime.now()
    save(to_df(mt5.history_orders_get(frm, to)), "orders_history")
    save(to_df(mt5.history_deals_get(frm, to)), "deals_history")

    symbols = mt5.symbols_get()
    if symbols:
        save(pd.DataFrame([s._asdict() for s in symbols]), "symbols")

    rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_D1, 0, 500)
    if rates is not None and len(rates):
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        save(df, "rates_EURUSD")


def main():
    connect()
    try:
        print("Exporting...")
        export_all()
        print("Done.")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()