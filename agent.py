"""Logika agent: analisa multi-timeframe, validasi sinyal, cek exit, dan logging."""
import csv
import json
import os
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import market_data as md
from llm import LLM

SYMBOL = os.getenv("SYMBOL", "XAUUSD=X")
MIN_RR = float(os.getenv("MIN_RR", "1.5"))
MIN_CONF = float(os.getenv("MIN_CONFIDENCE", "60"))

STATE_FILE = Path("state.json")
POSITION_FILE = Path("position.json")
LOG_FILE = Path("signals_log.csv")

ANALYSIS_SYSTEM = """Kamu adalah analis teknikal XAUUSD (emas) untuk trader scalping. Kamu menerima data candle dan indikator M30, M15, M5, dan M3 dalam format JSON.

Alur kerja (top-down):
1. M30 = bias utama. Tentukan arah dari struktur (HH+HL atau LH+LL), stack EMA 9/21/200, dan candle terakhir.
2. M15 = area. Cari FVG terbuka atau level likuiditas yang searah bias dan dekat harga.
3. M5 = trigger. Perlu liquidity sweep di area itu, lalu CHoCH atau BOS searah bias.
4. M3 = konfirmasi. Candle terakhir menutup searah dan menunjukkan penolakan dari area.

Aturan:
- Jawab HANYA dengan satu objek JSON yang valid. Tanpa teks lain dan tanpa markdown.
- Gunakan HANYA angka yang ada di data. Jangan mengarang harga.
- Konsistensi: jika previous_bias ada, pertahankan arahnya kecuali ada invalidasi yang jelas (misalnya close M30 menembus level invalidasi). Jangan membalik arah karena satu candle kecil.
- Jika M30, M15, M5, dan M3 belum selaras, isi action = "NO_TRADE" dan tetap isi bias sesuai M30.
- BUY hanya jika bias BULLISH. SELL hanya jika bias BEARISH.
- Stop loss ditaruh di balik sweep atau swing terakhir, dengan buffer sekitar 0.2 x ATR14 M5. TP1 di likuiditas atau swing berikutnya, TP2 di likuiditas berikutnya.
- Semua teks dalam Bahasa Indonesia.
- Ini adalah analisa, bukan jaminan profit.

Format JSON:
