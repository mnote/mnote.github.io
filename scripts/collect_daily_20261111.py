"""11/11 日线数据 + 6 月顶部回撤核验（Tushare Pro）。

用法： ~/czsc/.venv/bin/python scripts/collect_daily_20261111.py
"""
import json
import os
import time
from pathlib import Path

import pandas as pd
import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN",
                        "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261110"

INDEXES = ["000001.SH", "399001.SZ", "399006.SZ", "000300.SH", "000688.SH"]
STOCKS = ["300308.SZ", "300502.SZ", "300394.SZ", "603986.SH", "301308.SZ",
          "688836.SH", "603893.SH", "688585.SH", "002708.SZ", "301536.SZ",
          "688332.SZ", "688256.SZ", "300475.SZ", "688525.SH", "001309.SZ"]


def retry(fn, n=4, **kw):
    for i in range(n):
        try:
            df = fn(**kw)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            if i == n - 1:
                print(f"    [ERR] {kw} {e}")
            time.sleep(1.2)
    return pd.DataFrame()


def fetch(ts_code, days=130):
    if ts_code.endswith((".SH", ".SZ")) and ts_code[:6] in ("000001", "399001", "399006", "000300", "000688"):
        df = retry(pro.index_daily, ts_code=ts_code, start_date=START, end_date=END)
        adj = None
    else:
        df = retry(pro.daily, ts_code=ts_code, start_date=START, end_date=END)
        adj = retry(pro.adj_factor, ts_code=ts_code, start_date=START, end_date=END)
    if df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    if adj is not None and not adj.empty:
        adj = adj.copy()
        adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
        adj = adj.sort_values("trade_date")
        df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
        df["adj_factor"] = df["adj_factor"].ffill().bfill()
        latest = df["adj_factor"].iloc[-1]
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] * df["adj_factor"] / latest
    df = df.tail(days).reset_index(drop=True)
    df = df.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                            "low": "Low", "close": "Close", "vol": "Volume"})
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Volume"] = df["Volume"].astype(float)
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]]


def drawdown_check(ts_code, name, top_start="2026-06-18", top_end="2026-06-30"):
    """6 月顶部 -> 年内最低点的最大回撤，核验「跌 60%~70%」。"""
    df = fetch(ts_code, days=200)
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"])
    seg = df[(df["Date"] >= top_start) & (df["Date"] <= top_end)]
    if seg.empty:
        return None
    pk = seg["High"].max()
    pk_date = seg.loc[seg["High"].idxmax(), "Date"].strftime("%Y-%m-%d")
    after = df[df["Date"] > seg["Date"].max()]
    if after.empty:
        return None
    tr = after["Low"].min()
    tr_date = after.loc[after["Low"].idxmin(), "Date"].strftime("%Y-%m-%d")
    # 从顶部收盘到最低收盘
    pc = seg.loc[seg["High"].idxmax(), "Close"]
    tc = after.loc[after["Low"].idxmin(), "Close"]
    return {
        "code": ts_code, "name": name,
        "peak": round(float(pk), 2), "peak_date": pk_date,
        "peak_close": round(float(pc), 2),
        "trough": round(float(tr), 2), "trough_date": tr_date,
        "trough_close": round(float(tc), 2),
        "dd_high_low": round((tr / pk - 1) * 100, 1),
        "dd_close_close": round((tc / pc - 1) * 100, 1),
        "last_close": round(float(df["Close"].iloc[-1]), 2),
        "rebound_from_low": round((df["Close"].iloc[-1] / tc - 1) * 100, 1),
    }


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = {}
    for c in INDEXES + STOCKS:
        df = fetch(c)
        if df.empty:
            print(f"  [skip] {c}")
            continue
        data[c] = df.to_dict("records")
        print(f"  [ok] {c}  {len(df)} 行  末收 {df['Close'].iloc[-1]:.2f}  "
              f"({df['Date'].iloc[-1]})")
        time.sleep(0.25)

    p = out_dir / "_daily_20261111.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"[out] {p}  ({len(data)} 个标的)")

    print("\n=== 6 月顶部 -> 最低点回撤核验 ===")
    names = {"300308.SZ": "中际旭创", "300502.SZ": "新易盛", "300394.SZ": "天孚通信",
             "603986.SH": "兆易创新", "301308.SZ": "江波龙", "688525.SH": "佰维存储",
             "300475.SZ": "香农芯创", "001309.SZ": "德明利", "688256.SH": "寒武纪"}
    dd = []
    for c, n in names.items():
        r = drawdown_check(c, n)
        if r:
            dd.append(r)
            print(f"  {n:6s} 顶 {r['peak']:.2f}({r['peak_date']}) → 底 {r['trough']:.2f}"
                  f"({r['trough_date']})  高低 {r['dd_high_low']:+.1f}%  "
                  f"收盘对收盘 {r['dd_close_close']:+.1f}%  "
                  f"最新 {r['last_close']:.2f} 自底部 {r['rebound_from_low']:+.1f}%")
    (out_dir / "_drawdown_20261111.json").write_text(
        json.dumps(dd, ensure_ascii=False, indent=2), encoding="utf-8")
