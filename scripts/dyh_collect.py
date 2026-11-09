"""都业华 2026-11-09 收评 · 数据采集
1) 东财 15 分钟 K 线（9 只标的 + 上证/创业板）→ CSV 供 czsc 跑缠论
2) czsc analyze --freq 15分钟 --json → 分型/笔/中枢/背驰
3) 市场宽度：全 A 成交额、涨跌家数、涨停/跌停家数（东财 ZT/DT pool）
4) 板块快照：东财行业板块，找 光伏设备/元件/半导体/机器人 等
5) 羊字辈标的筛选（tushare stock_basic）
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import tushare as ts

OUT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261109")
DATA = OUT / "data"
DATA.mkdir(parents=True, exist_ok=True)

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

STOCKS = {
    "药明康德": ("1.603259", "603259.SH"),
    "中国船舶": ("1.600150", "600150.SH"),
    "瑞芯微":   ("1.603893", "603893.SH"),
    "伊利股份": ("1.600887", "600887.SH"),
    "江波龙":   ("0.301308", "301308.SZ"),
    "兆易创新": ("1.603986", "603986.SH"),
    "海天瑞声": ("1.688787", "688787.SH"),
    "华策影视": ("0.300133", "300133.SZ"),
    "云铝股份": ("0.000807", "000807.SZ"),
}
INDEX = {
    "上证指数": ("1.000001", "000001.SH"),
    "创业板指": ("0.399006", "399006.SZ"),
}


def em_kline_15m(secid, lmt=1000):
    url = ("https://push2his.eastmoney.com/api/qt/stock/kline/get?"
           f"secid={secid}&klt=15&fqt=1&lmt={lmt}&end=20500101"
           "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57")
    for _ in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=20)
            js = r.json()
            if js.get("data") and js["data"].get("klines"):
                return js["data"]["klines"]
        except Exception as e:
            print("retry", secid, e)
        time.sleep(1.5)
    return []


def klines_to_csv(klines, symbol, path):
    rows = []
    for k in klines:
        p = k.split(",")
        rows.append({
            "dt": p[0], "symbol": symbol,
            "open": float(p[1]), "close": float(p[2]),
            "high": float(p[3]), "low": float(p[4]),
            "vol": float(p[5]), "amount": float(p[6]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


def run_czsc(csv_path, freq="15分钟"):
    p = subprocess.run(
        [str(Path.home() / "czsc/.venv/bin/czsc"), "analyze", str(csv_path), "--freq", freq, "--json"],
        capture_output=True, text=True,
    )
    if p.returncode != 0:
        return {"error": p.stderr[-800:]}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"raw": p.stdout[-3000:]}


# ── 1+2 分钟级缠论 ──────────────────────────────────────
result = {}
for name, (secid, code) in {**STOCKS, **INDEX}.items():
    kl = em_kline_15m(secid)
    if not kl:
        print(f"[FAIL kline] {name}")
        continue
    sym = code.replace(".", "_")
    csv = DATA / f"{sym}_15m.csv"
    df = klines_to_csv(kl, sym, csv)
    js = run_czsc(csv)
    result[name] = {
        "code": code,
        "bars": len(df),
        "from": df["dt"].iloc[0],
        "to": df["dt"].iloc[-1],
        "czsc": js,
    }
    print(f"[OK] {name} {code} bars={len(df)} {df['dt'].iloc[0]} → {df['dt'].iloc[-1]}")

(OUT / "czsc_15m.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

# ── 3 市场宽度 ──────────────────────────────────────────
breadth = {}
try:
    d = pro.daily(trade_date="20261109")
    for _ in range(3):
        if d is not None and not d.empty:
            break
        time.sleep(1)
        d = pro.daily(trade_date="20261109")
    d["limit_pct"] = 10.0
    d.loc[d["ts_code"].str.contains(r"(300|301|688|689)\.", regex=True), "limit_pct"] = 20.0
    d["limit_pct"] = d["limit_pct"].where(d["ts_code"].str[2:3] != "8", 30.0)
    up = int((d["pct_chg"] > 0).sum())
    down = int((d["pct_chg"] < 0).sum())
    flat = int((d["pct_chg"] == 0).sum())
    zt = int((d["pct_chg"] >= d["limit_pct"] - 0.5).sum())
    dt_ = int((d["pct_chg"] <= -(d["limit_pct"] - 0.5)).sum())
    amt = float(d["amount"].sum()) / 1e5  # 千元 → 亿元
    breadth = {
        "trade_date": "2026-11-09", "total": int(len(d)),
        "up": up, "down": down, "flat": flat,
        "zt_est": zt, "dt_est": dt_,
        "amount_yi": round(amt, 1),
        "median_pct": round(float(d["pct_chg"].median()), 3),
        "avg_pct": round(float(d["pct_chg"].mean()), 3),
    }
    d.to_csv(DATA / "all_a_20261109.csv", index=False)
except Exception as e:
    breadth = {"error": str(e)}

for kind, url in [
    ("zt", "https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=1&sort=fbt:asc&date=20261109"),
    ("dt", "https://push2ex.eastmoney.com/getTopicDTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=1&sort=fbt:asc&date=20261109"),
]:
    try:
        js = requests.get(url, headers=UA, timeout=20).json()
        breadth[f"{kind}_em"] = js.get("data", {}).get("tc") if js.get("data") else 0
    except Exception as e:
        breadth[f"{kind}_em"] = f"err {e}"

# ── 4 板块快照 ──────────────────────────────────────────
sectors = {}
try:
    url = ("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1&fltt=2&invt=2"
           "&fid=f3&fs=m:90+t:2&fields=f12,f14,f3,f104,f105,f128,f136,f140")
    js = requests.get(url, headers=UA, timeout=25).json()
    diff = js["data"]["diff"]
    KEY = ["光伏", "元件", "半导体", "机器人", "算力", "光模块", "消费电子", "电池", "医药", "船舶"]
    for it in diff:
        nm = it.get("f14", "")
        if any(k in nm for k in KEY):
            sectors[nm] = {"code": it.get("f12"), "pct": it.get("f3"),
                           "up": it.get("f104"), "down": it.get("f105"),
                           "leader": it.get("f128"), "leader_pct": it.get("f136")}
except Exception as e:
    sectors = {"error": str(e)}

# ── 5 羊字辈 ────────────────────────────────────────────
yang = []
try:
    sb = pro.stock_basic(exchange="", list_status="L", fields="ts_code,name,industry")
    hit = sb[sb["name"].str.contains("羊", na=False)]
    yang = hit.to_dict("records")
except Exception as e:
    yang = [{"error": str(e)}]

summary = {"breadth": breadth, "sectors": sectors, "yang": yang}
(OUT / "market_20261109.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(breadth, ensure_ascii=False))
print(json.dumps(sectors, ensure_ascii=False))
print(json.dumps(yang, ensure_ascii=False))
