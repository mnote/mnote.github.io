#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""都业华 11/10 午评核验：标的快照 + 15 分钟 K + 板块匹配"""
import json
import os
import time
import urllib.request

import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
UA = {"User-Agent": "Mozilla/5.0"}
OUT = "/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace/dyh_1130_check.json"


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


def snapshot(code):
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid(code)}"
              "&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f116,f168,f169,f170")
    if not d or not d.get("data"):
        return None
    x = d["data"]
    return {"name": x.get("f58"), "code": x.get("f57"), "price": x.get("f43") / 100,
            "high": x.get("f44") / 100, "low": x.get("f45") / 100, "open": x.get("f46") / 100,
            "prev": x.get("f60") / 100, "amount_yi": round((x.get("f48") or 0) / 1e8, 2),
            "pct": x.get("f170") / 100, "mktcap_yi": round((x.get("f116") or 0) / 1e8, 1)}


def kline(code, klt=15, lmt=80):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid(code)}"
              f"&klt={klt}&fqt=1&lmt={lmt}&end=20500101"
              "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61")
    if not d or not d.get("data"):
        return []
    out = []
    for kk in d["data"]["klines"]:
        p = kk.split(",")
        out.append({"dt": p[0], "o": float(p[1]), "c": float(p[2]), "h": float(p[3]),
                    "l": float(p[4]), "vol": float(p[5]), "amt": float(p[6]),
                    "pct": float(p[8]), "chg": float(p[9])})
    return out


def board(code):
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid=90.{code}"
              "&fields=f43,f44,f45,f46,f48,f57,f58,f60,f170")
    if not d or not d.get("data"):
        return None
    x = d["data"]
    return {"name": x.get("f58"), "price": x.get("f43") / 100, "open": x.get("f46") / 100,
            "high": x.get("f44") / 100, "low": x.get("f45") / 100, "prev": x.get("f60") / 100,
            "pct": x.get("f170") / 100, "amount_yi": round((x.get("f48") or 0) / 1e8, 1)}


if __name__ == "__main__":
    out = {}

    # --- 1) 找宇树科技 ---
    try:
        sb = pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,industry,list_date")
        hit = sb[sb["name"].str.contains("宇树|Unitree", na=False)]
        out["unitree"] = hit.to_dict("records")
        if hit.empty:
            for st in ("P", "D"):
                sb2 = pro.stock_basic(exchange="", list_status=st, fields="ts_code,symbol,name,industry,list_date")
                h2 = sb2[sb2["name"].str.contains("宇树", na=False)]
                if not h2.empty:
                    out.setdefault("unitree_other", {})[st] = h2.to_dict("records")
    except Exception as e:
        print("sb fail", e)

    # --- 2) 板块代码匹配 ---
    boards = {}
    for bs, tag in [("m:90+t:3", "concept"), ("m:90+t:2", "industry")]:
        for pn in range(1, 12):
            d = fetch(f"https://push2.eastmoney.com/api/qt/clist/get?fs={bs}&pn={pn}&pz=100"
                      "&po=1&np=1&fltt=2&invt=2&fid=f3&fields=f2,f3,f6,f12,f14,f62,f104,f105")
            if not d or not d.get("data") or not d["data"].get("diff"):
                break
            diff = d["data"]["diff"]
            if isinstance(diff, dict):
                diff = list(diff.values())
            for it in diff:
                boards[it["f12"]] = {"name": it["f14"], "pct": it.get("f3"),
                                     "amount_yi": round((it.get("f6") or 0) / 1e8, 1),
                                     "up": it.get("f104"), "down": it.get("f105"),
                                     "main_net_yi": round((it.get("f62") or 0) / 1e8, 2)}
            if len(diff) < 100:
                break
            time.sleep(0.2)
    keys = ["人形机器人", "机器人", "AI视频", "光伏设备", "光伏", "算力", "AI应用", "传媒", "短剧", "游戏"]
    out["board_hits"] = {c: v for c, v in boards.items() if any(k in v["name"] for k in keys)}
    out["board_snapshot"] = {name: board(c) for c, name in
                             [("BK1761", "AI视频"), ("BK1031", "光伏设备"), ("BK1157", "人形机器人"),
                              ("BK1134", "算力概念"), ("BK0486", "传媒"), ("BK1151", "短剧互动游戏")]}

    # --- 3) 个股 ---
    stocks = ["603259", "600150", "603893", "600887", "301308", "603986", "688787", "300133", "000807"]
    st = {}
    for c in stocks:
        s = snapshot(c)
        k15 = kline(c, 15, 40)
        kd = kline(c, 101, 30)
        st[c] = {"snap": s, "k15": k15[-16:], "daily": kd[-12:]}
        time.sleep(0.25)
    out["stocks"] = st

    with open(OUT, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out.get("unitree", {}), ensure_ascii=False))
    print("板块命中：")
    for c, v in sorted(out["board_hits"].items(), key=lambda x: -(x[1]["pct"] or 0)):
        print(f"  {v['name']:14s} {c} {v['pct']:+6.2f}% 额{v['amount_yi']:>7.0f}亿 涨{v['up']}/跌{v['down']} 主力{v['main_net_yi']:+.2f}亿")
    print("\n个股快照：")
    for c, v in st.items():
        s = v["snap"]
        if s:
            print(f"  {s['name']:8s} {c} 现{s['price']:>9.2f} 涨{s['pct']:+6.2f}% 开{s['open']:>9.2f} 高{s['high']:>9.2f} 低{s['low']:>9.2f} 昨{s['prev']:>9.2f} 额{s['amount_yi']:>6.1f}亿")
