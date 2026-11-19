"""11/19 午评 · 补齐原文点名的 3 只标的（奥普特/柯力传感/中文在线）
这 3 只在 11/18 收评已被老师剔除，但本次原文仍点名，需补数据以便对照。
"""
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
D8 = "20261119"
THS_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
SINA_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

EXTRA = {"奥普特": "688686", "柯力传感": "603662", "中文在线": "300364"}


def ths_kline(code, tries=4):
    url = f"https://d.10jqka.com.cn/v6/line/{code}/01/last.js"
    for i in range(tries):
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers=THS_UA), timeout=25).read().decode()
            j = json.loads(re.search(r"\((.*)\)", raw, re.S).group(1))
            rows = []
            for line in j["data"].split(";"):
                f = line.split(",")
                if len(f) < 7:
                    continue
                try:
                    rows.append({"d": f[0], "o": float(f[1]), "h": float(f[2]), "l": float(f[3]),
                                 "c": float(f[4]), "v": float(f[5]), "amt": float(f[6])})
                except ValueError:
                    continue
            return j.get("name", ""), rows
        except Exception as e:
            print("  retry", code, str(e)[:60])
            time.sleep(1.0 + i)
    return "", []


def sina(sym):
    url = f"https://hq.sinajs.cn/list={sym}"
    for t in range(4):
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers=SINA_UA), timeout=20).read()
            m = re.search(r'var hq_str_\w+="([^"]*)"', raw.decode("gbk", "ignore"))
            if not m:
                time.sleep(0.8 + t)
                continue
            f = m.group(1).split(",")
            if len(f) < 32 or not f[0]:
                time.sleep(0.8 + t)
                continue
            return {"name": f[0], "open": float(f[1]), "prev": float(f[2]),
                    "price": float(f[3]), "high": float(f[4]), "low": float(f[5]),
                    "vol": float(f[8]), "amount": float(f[9]), "date": f[30], "time": f[31]}
        except Exception:
            time.sleep(0.8 + t)
    return {}


data = json.loads((RPT / "data_20261119.json").read_text(encoding="utf-8"))

for name, code in EXTRA.items():
    sym = ("sh" if code[0] == "6" else "sz") + code
    n, rows = ths_kline("hs_" + code)
    s = sina(sym)
    print(f"  {name} {code} bars={len(rows)} snap={s.get('price')} {s.get('time')}")
    if not rows or not s:
        continue
    if rows[-1]["d"] == D8:
        rows[-1].update({"o": s["open"], "h": s["high"], "l": s["low"],
                         "c": s["price"], "v": s["vol"], "amt": s["amount"]})
    else:
        rows.append({"d": D8, "o": s["open"], "h": s["high"], "l": s["low"],
                     "c": s["price"], "v": s["vol"], "amt": s["amount"]})
    data["series"][name] = rows
    prev = rows[-2]["c"]
    w60, w20, w5 = rows[-60:], rows[-20:], rows[-5:]
    data["stocks"][name] = {
        "code": code, "em_name": n,
        "date": rows[-1]["d"], "open": rows[-1]["o"], "high": rows[-1]["h"],
        "low": rows[-1]["l"], "close": rows[-1]["c"], "prev_close": prev,
        "pct": round((rows[-1]["c"] / prev - 1) * 100, 2),
        "vol": rows[-1]["v"], "amt": rows[-1]["amt"],
        "hi60": max(r["h"] for r in w60), "lo60": min(r["l"] for r in w60),
        "vol_ma5": round(sum(r["v"] for r in w5) / 5, 0),
        "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0),
        "snap": {"open": s["open"], "high": s["high"], "low": s["low"],
                 "close": s["price"], "prev_close": s["prev"],
                 "pct": round((s["price"] / s["prev"] - 1) * 100, 2),
                 "vol": s["vol"], "amt": s["amount"], "time": s["time"]},
    }
    data.setdefault("snapshot_raw", {})[sym] = s

(RPT / "data_20261119.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved 11/19 data, stocks =", len(data["stocks"]))
