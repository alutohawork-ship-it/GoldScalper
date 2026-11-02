"""CLI agent XAUUSD: analyze | watch | chat | open | close.

Agent ini hanya memberi analisa dan saran. Tidak ada eksekusi order otomatis.
"""
import argparse
import json
import time
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

import agent  # noqa: E402
import market_data as md  # noqa: E402

CHAT_SYSTEM = (
    "Kamu asisten analisa trading XAUUSD untuk scalper. Jawab dalam Bahasa Indonesia, "
    "singkat dan jelas. Dasarkan jawaban pada data pasar JSON yang diberikan di setiap pesan; "
    "jika data tidak cukup, katakan dengan jujur. Jangan menjanjikan profit, dan ingatkan "
    "manajemen risiko bila relevan. Kamu tidak mengeksekusi order."
)


def stamp():
    return datetime.now().strftime("%H:%M:%S")


def print_signal(sig, price):
    line = "=" * 60
    print(line)
    print(f"{stamp()}  XAUUSD {price:.2f}  |  {sig.get('action')}  "
          f"bias {sig.get('bias')}  conf {sig.get('confidence')}")
    if sig.get("action") != "NO_TRADE":
        print(f"Entry {sig['entry']}  SL {sig['stop_loss']}  TP1 {sig['take_profit_1']}  "
              f"TP2 {sig.get('take_profit_2')}  RR {sig.get('rr_tp1')}")
    print(f"Setup     : {sig.get('setup_summary')}")
    print(f"Invalidasi: {sig.get('invalidation')}")
    if sig.get("validation_note"):
