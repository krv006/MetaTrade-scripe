import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()

ok = mt5.initialize(
    path=os.getenv("MT5_PATH"),
    login=int(os.getenv("MT5_LOGIN")),
    password=os.getenv("MT5_PASSWORD"),
    server=os.getenv("MT5_SERVER"),
)
print(ok, mt5.last_error())
mt5.shutdown()
