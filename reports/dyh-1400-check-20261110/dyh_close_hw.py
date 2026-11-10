#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""11/10 收评核验 v2：作业题 万兴科技 vs 中文在线 + 玄学链 + 周线关键位(248.49/155.5)"""
import json
import os
import time
import urllib.request

import tushare as ts

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace"
pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))


def fetch(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(1.5)


def secid(code):
    return ("1." if code[0] in "56" else "0.") + code


def kline(secid_s, klt=101, lmt=100):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid_s}"
              f"&klt={klt}&fqt=1&lmt={lmt}&end=20500101"
              "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61")
    out = []
    for kk in (d.get("data") or {}).get("klines", []):
        p = kk.split(",")
        out.append({"dt": p[0], "o": float(p[1]), "c": float(p[2]), "h": float(p[3]),
                    "l": float(p[4]), "vol": float(p[5]), "amt": float(p[6]), "pct": float(p[8])})
    return out


def snap(code):
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid(code)}"
              "&fields=f43,f44,f45,f46,f48,f57,f58,f60,f116,f170,f169")
    if not d or not d.get("data"):
        return None
    x = d["data"]
    return {"name": x.get("f58"), "price": x.get("f43") / 100, "high": x.get("f44") / 100,
            "low": x.get("f45") / 100, "open": x.get("f46") / 100, "prev": x.get("f60") / 100,
            "pct": x.get("f170") / 100, "amount_yi": round((x.get("f48") or 0) / 1e8, 2),
            "mktcap_yi": round((x.get("f116") or 0) / 1e8, 1)}


def concepts(code):
    d = fetch(f"https://push2.eastmoney.com/api/qt/slist/get?spt=3&fltt=2&invt=2&fields=f12,f13,f14,f3,f62"
              f"&secid={secid(code)}&pn=1&pz=50&po=1&np=1&fid=f3")
    if not d or not d.get("data"):
        return []
    return [{"name": x["f14"], "code": x["f12"], "pct": x.get("f3"),
             "main_yi": round((x.get("f62") or 0) / 1e8, 2)} for x in (d["data"].get("diff") or [])]


def macd(closes, fast=12, slow=26, sig=9):
    import math
    def ema(vals, n):
        k = 2 / (n + 1)
        e = vals[0]
        out = [e]
        for v in vals[1:]:
            e = v * k + e * (1 - k)
            out.append(e)
        return out
    ef, es = ema(closes, fast), ema(closes, slow)
    dif = [a - b for a, b in zip(ef, es)]
    dea = ema(dif, sig)
    return dif[-1], dea[-1], (dif[-1] - dea[-1]) * 2, dif[-2] - dea[-2]


if __name__ == "__main__":
    out = {}

    # ---- 1) 作业题：万兴科技 vs 中文在线 ----
    hw = {}
    for nm, code in [("万兴科技", "300624"), ("中文在线", "300364")]:
        k = kline(secid(code), 101, 80)
        s = snap(code)
        closes = [r["c"] for r in k]
        dif, dea, bar, bar_prev = macd(closes)
        hi60 = max(r["h"] for r in k[-60:])
        lo60 = min(r["l"] for r in k[-60:])
        last = k[-1]
        hw[nm] = {
            "code": code, "snap": s,
            "close": last["c"], "pct": last["pct"], "high": last["h"], "low": last["l"],
            "high60": hi60, "low60": lo60,
            "dist_high60": round((last["c"] / hi60 - 1) * 100, 2),
            "dist_low60": round((last["c"] / lo60 - 1) * 100, 2),
            "ret5": round((last["c"] / k[-6]["c"] - 1) * 100, 2),
            "ret10": round((last["c"] / k[-11]["c"] - 1) * 100, 2),
            "ret20": round((last["c"] / k[-21]["c"] - 1) * 100, 2),
            "dif": round(dif, 3), "dea": round(dea, 3), "bar": round(bar, 3),
            "golden": dif > dea, "bar_expand": bar > bar_prev,
            "mktcap_yi": s["mktcap_yi"] if s else None,
            "tail": [{"d": r["dt"][:10], "c": r["c"], "h": r["h"], "l": r["l"], "pct": r["pct"],
                      "amt_yi": round(r["amt"] / 1e8, 2)} for r in k[-12:]],
            "concepts": concepts(code)[:18],
        }
        time.sleep(0.3)
    out["homework"] = hw

    # ---- 2) 周线关键位：248.49 / 155.5 ----
    wk = {}
    for nm, code in [("瑞芯微", "1.603893"), ("海天瑞声", "1.688787")]:
        k = kline(code, 102, 120)   # klt=102 = 周线
        ks = kline(code, 101, 500)
        wk[nm] = {
            "week_high": max(r["h"] for r in k),
            "week_high_date": next((r["dt"][:10] for r in k if r["h"] == max(x["h"] for x in k)), None),
            "week_tail": [{"d": r["dt"][:10], "c": r["c"], "h": r["h"], "l": r["l"]} for r in k[-6:]],
            "daily_500_high": max(r["h"] for r in ks),
            "daily_500_high_date": next((r["dt"][:10] for r in ks if r["h"] == max(x["h"] for x in ks)), None),
            "hit_248": [r["dt"][:10] for r in ks if abs(r["h"] - 248.49) < 1.0][:5],
            "hit_1555": [r["dt"][:10] for r in ks if abs(r["h"] - 155.5) < 1.0][:5],
        }
        time.sleep(0.25)
    out["weekly_levels"] = wk

    # ---- 3) 玄学链：名字含"东方"/"羊" 的股票 11/09-11/10 表现 ----
    try:
        sb = pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,industry")
        cand = sb[sb["name"].str.contains("东方", na=False)]
        codes = list(cand["ts_code"])[:60]
        rows = []
        for i in range(0, len(codes), 30):
            chunk = codes[i:i + 30]
            df = pro.daily(ts_code=",".join(chunk), start_date="20261106", end_date="20261110")
            if df is not None and len(df):
                rows.append(df)
        import pandas as pd
        alldf = pd.concat(rows)
        name_map = dict(zip(sb["ts_code"], sb["name"]))
        alldf["name"] = alldf["ts_code"].map(name_map)
        piv = alldf.pivot_table(index="name", columns="trade_date", values="pct_chg")
        piv = piv[[c for c in piv.columns if c >= "20261106"]]
        piv["amount_yi"] = alldf.groupby("name")["amount"].sum() / 1e5
        piv = piv.sort_values(piv.columns[-1], ascending=False)
        out["xuanxue_dongfang"] = piv.round(2).reset_index().to_dict("records")[:25]
    except Exception as e:
        print("xuanxue fail", e)

    with open(f"{BASE}/dyh_close_hw.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for nm, v in hw.items():
        print(f"===== {nm} {v['code']} =====")
        print(f"  收{v['close']:.2f} {v['pct']:+.2f}% 高{v['high']:.2f} 低{v['low']:.2f} 额{v['snap']['amount_yi']:.2f}亿 市值{v['mktcap_yi']:.0f}亿")
        print(f"  60日高{v['high60']:.2f} 低{v['low60']:.2f} | 距高{v['dist_high60']:+.1f}% 距低{v['dist_low60']:+.1f}%")
        print(f"  5日{v['ret5']:+.1f}% 10日{v['ret10']:+.1f}% 20日{v['ret20']:+.1f}% | MACD DIF{v['dif']:.2f} DEA{v['dea']:.2f} 柱{v['bar']:.2f} 金叉{v['golden']}")
        print("  近8日:", " ".join(f"{r['d'][5:]}:{r['pct']:+.1f}%" for r in v["tail"][-8:]))
        print("  概念:", ", ".join(f"{c['name']}{c['pct']:+.1f}%" for c in v["concepts"][:12]))
    print("\n== 周线关键位 ==")
    for nm, v in wk.items():
        print(f"  {nm}: 周线高{v['week_high']:.2f}({v['week_high_date']}) 日线500高{v['daily_500_high']:.2f}({v['daily_500_high_date']}) 命中248.49:{v['hit_248']} 命中155.5:{v['hit_1555']}")
    print("\n== 玄学链·东方字样 ==")
    for r in out.get("xuanxue_dongfang", [])[:15]:
        print("  ", {k: r[k] for k in list(r)[:7]})
