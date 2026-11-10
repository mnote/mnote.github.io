#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""十点看盘核验 v2：板块分时（开盘/当前/冲高回落）+ 沪市深市早盘成交额累计"""
import json
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
OUT = "/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace/dyh_1010_trend.json"


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(1.5)


def trends(secid):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={secid}"
              "&ndays=1&iscr=0&iscca=0&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
              "&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
    if not d or not d.get("data"):
        return None, None
    prev = d["data"].get("preClose")
    pts = []
    for line in (d["data"].get("trends") or []):
        p = line.split(",")
        if len(p) < 8:
            continue
        try:
            pts.append({"t": p[0], "open": float(p[1]), "close": float(p[2]), "high": float(p[3]),
                        "low": float(p[4]), "vol": float(p[5]), "amt": float(p[6]),
                        "avg": float(p[7]), "pct": 0.0})
        except Exception:
            pass
    for p in pts:
        p["pct"] = (p["close"] / prev - 1) * 100
    return prev, pts


def summarize(name, secid):
    prev, pts = trends(secid)
    if not pts:
        return None
    op = [p for p in pts if p["t"].endswith("09:30")]
    first = op[0] if op else pts[0]
    hi = max(pts, key=lambda p: p["pct"])
    lo = min(pts, key=lambda p: p["pct"])
    last = pts[-1]
    # 早盘(9:30-10:30)成交额
    early = sum(p["amt"] for p in pts if p["t"][11:13] <= "10" and p["t"][11:16] <= "10:30")
    return {"name": name, "secid": secid, "pre": prev, "n": len(pts),
            "open_pct": round((first["open"] / prev - 1) * 100, 2),
            "now_pct": round(last["pct"], 2),
            "high_pct": round(hi["pct"], 2), "high_t": hi["t"],
            "low_pct": round(lo["pct"], 2), "low_t": lo["t"],
            "pullback_pp": round(hi["pct"] - last["pct"], 2),
            "amt_total_yi": round(last["amt"] / 1e8, 1),
            "amt_to_1030_yi": round(early / 1e8, 1),
            "last_t": last["t"]}


if __name__ == "__main__":
    targets = [
        ("上证指数", "1.000001"), ("深证成指", "0.399001"), ("创业板指", "0.399006"),
        ("算力概念", "90.BK1134"), ("算力租赁", "90.BK0966"), ("CPO概念", "90.BK1128"),
        ("液冷服务器", "90.BK1138"), ("数据中心", "90.BK0922"),
        ("AI应用", "90.BK1629"), ("AIGC概念", "90.BK1111"), ("ChatGPT概念", "90.BK1126"),
        ("短剧互动游戏", "90.BK1151"), ("网络游戏", "90.BK0509"), ("多模态AI", "90.BK1153"),
        ("影视概念", "90.BK0847"), ("文化传媒", "90.BK0486"), ("人工智能", "90.BK0800"),
    ]
    res = []
    for nm, sid in targets:
        s = summarize(nm, sid)
        if s:
            res.append(s)
        time.sleep(0.25)
    with open(OUT, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"{'名称':<12}{'开盘%':>8}{'现%':>8}{'最高%':>8}{'高点时':>10}{'最低%':>8}{'回落pp':>8}{'至今成交(亿)':>14}{'至10:30(亿)':>13}")
    for s in res:
        print(f"{s['name']:<12}{s['open_pct']:>8.2f}{s['now_pct']:>8.2f}{s['high_pct']:>8.2f}{s['high_t'][11:16]:>10}"
              f"{s['low_pct']:>8.2f}{s['pullback_pp']:>8.2f}{s['amt_total_yi']:>14.1f}{s['amt_to_1030_yi']:>13.1f}")
