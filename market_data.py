"""Ambil candle dari Yahoo Finance (yfinance) dan hitung indikator serta struktur harga."""
import pandas as pd
import yfinance as yf


def fetch(symbol, interval, period):
    df = yf.download(symbol, interval=interval, period=period,
                     auto_adjust=False, progress=False)
    if df.empty:
        raise RuntimeError(f"Data kosong: {symbol} {interval} {period}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_convert("UTC")
    return df


def to_3m(df_1m):
    """M3 dibentuk dari data 1 menit, karena Yahoo tidak menyediakan interval 3 menit."""
    return (df_1m.resample("3min")
            .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
            .dropna())


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    pc = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def rsi(s, n=14):
    d = s.diff()
