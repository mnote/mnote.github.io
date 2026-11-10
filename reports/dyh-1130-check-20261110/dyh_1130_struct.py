#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""午评核验 v2：宇树科技走势 + AI视频/瑞芯微 15 分钟中枢结构"""
import json
import os
import subprocess
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace"


def fetch(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(1.5)


def kline(secid, klt=15, lmt=200):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}"
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


def write_csv(rows, path):
    with open(path, "w") as f:
        f.write("dt,symbol,open,close,high,low,vol,amount\n")
        for r in rows:
            f.write(f'{r["dt"]},{r["dt"]},{r["o"]},{r["c"]},{r["h"]},{r["l"]},{r["vol"]},{r["amt"]}\n')


def czsc_analyze(csv_path, freq):
    p = subprocess.run(["/Users/maoling/.venv/bin/czsc" if False else os.path.expanduser("~/czsc/.venv/bin/czsc"),
                        "analyze", csv_path, "--freq", freq, "--json"],
                       capture_output=True, text=True, timeout=180)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"error": p.stdout[-400:] + p.stderr[-400:]}


def summarize_bi(ana):
    bl = ana.get("bi_list") or []
    if not bl:
        return {"error": "no bi_list"}
    out = []
    for b in bl[-6:]:
        out.append({k: (str(b.get(k))[:19] if k in ("dt", "edt") else b.get(k))
                    for k in ("dt", "edt", "direction", "high", "low", "power", "length")})
    return {"n_bi": len(bl), "last_bi": out}


if __name__ == "__main__":
    res = {}

    # ---- 宇树科技 688836 ----
    u = kline("1.688836", 101, 60)
    u30 = kline("1.688836", 30, 120)
    res["unitree_daily"] = u[-12:]
    res["unitree_30m_last"] = u30[-20:]
    hi = max(u[-5:], key=lambda r: r["h"])
    res["unitree_note"] = {"11_09_high": max([r["h"] for r in u if r["dt"].startswith("2026-11-09")] or [0]),
                           "today": u[-1] if u else None}

    # ---- AI视频板块 15 分钟中枢 ----
    aiv = kline("90.BK1761", 15, 300)
    p = f"{BASE}/_tmp_aivideo_15m.csv"
    write_csv(aiv, p)
    ana = czsc_analyze(p, "15分钟")
    res["aivideo_15m_bi"] = summarize_bi(ana)
    res["aivideo_15m_last"] = aiv[-24:]

    # ---- 瑞芯微 15 分钟 ----
    rk = kline("1.603893", 15, 200)
    p2 = f"{BASE}/_tmp_ruixinwei_15m.csv"
    write_csv(rk, p2)
    ana2 = czsc_analyze(p2, "15分钟")
    res["ruixinwei_15m_bi"] = summarize_bi(ana2)
    res["ruixinwei_15m_today"] = [r for r in rk if r["dt"].startswith("2026-11-10")]

    # ---- 药明康德 15 分钟（151 修复）----
    ym = kline("1.603259", 15, 200)
    res["ymkd_15m_today"] = [r for r in ym if r["dt"].startswith("2026-11-10")]
    res["ymkd_15m_prev_close_levels"] = {"15m_close_max_today": max([r["c"] for r in res["ymkd_15m_today"]] or [0]),
                                         "15m_close_min_today": min([r["c"] for r in res["ymkd_15m_today"]] or [0])}

    with open(f"{BASE}/dyh_1130_struct.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print("== 宇树科技 688836 日线 ==")
    for r in res["unitree_daily"]:
        print(f'  {r["dt"]} O{r["o"]:.2f} H{r["h"]:.2f} L{r["l"]:.2f} C{r["c"]:.2f} {r["pct"]:+.2f}%')
    print("\n== AI视频 15分钟 笔 ==")
    print(json.dumps(res["aivideo_15m_bi"], ensure_ascii=False))
    print("\n== 瑞芯微 15分钟 笔 ==")
    print(json.dumps(res["ruixinwei_15m_bi"], ensure_ascii=False))
    print("\n== 瑞芯微 今日15分钟 ==")
    for r in res["ruixinwei_15m_today"]:
        print(f'  {r["dt"]} O{r["o"]:.2f} H{r["h"]:.2f} L{r["l"]:.2f} C{r["c"]:.2f} amt{r["amt"]/1e8:.2f}亿')
    print("\n== 药明康德 今日15分钟 ==")
    for r in res["ymkd_15m_today"]:
        print(f'  {r["dt"]} O{r["o"]:.2f} H{r["h"]:.2f} L{r["l"]:.2f} C{r["c"]:.2f}')
