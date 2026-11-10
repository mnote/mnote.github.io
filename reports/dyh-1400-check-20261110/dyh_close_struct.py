#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""11/10 收评核验 v1：1 分钟/15 分钟中枢结构（上证/深成/创业板/AI视频）+ 关键位"""
import json
import os
import subprocess
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace"
CZ = os.path.expanduser("~/czsc/.venv/bin/czsc")


def fetch(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(1.5)


def kline(secid, klt=101, lmt=100):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}"
              f"&klt={klt}&fqt=1&lmt={lmt}&end=20500101"
              "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61")
    out = []
    for kk in (d.get("data") or {}).get("klines", []):
        p = kk.split(",")
        out.append({"dt": p[0], "o": float(p[1]), "c": float(p[2]), "h": float(p[3]),
                    "l": float(p[4]), "vol": float(p[5]), "amt": float(p[6]), "pct": float(p[8])})
    return out


def analyze(rows, freq, tag):
    if not rows:
        return None
    p = f"{BASE}/_tmp_{tag}.csv"
    with open(p, "w") as f:
        f.write("dt,symbol,open,close,high,low,vol,amount\n")
        for r in rows:
            f.write(f'{r["dt"]},{r["dt"]},{r["o"]},{r["c"]},{r["h"]},{r["l"]},{r["vol"]},{r["amt"]}\n')
    pr = subprocess.run([CZ, "analyze", p, "--freq", freq, "--json"], capture_output=True, text=True, timeout=240)
    try:
        ana = json.loads(pr.stdout)
    except Exception:
        return {"error": (pr.stdout or "")[-200:]}
    bl = ana.get("bi_list") or []
    return {"bi": [{"edt": str(b.get("edt"))[:16], "dir": b.get("direction"), "high": b.get("high"),
                    "low": b.get("low"), "power": b.get("power"), "length": b.get("length")} for b in bl[-12:]]}


def zs_from_bi(bi):
    """三笔重叠算中枢序列"""
    zss = []
    for i in range(len(bi) - 2):
        a, b, c = bi[i], bi[i + 1], bi[i + 2]
        lo = max(min(a["low"], a["high"]), min(b["low"], b["high"]), min(c["low"], c["high"]))
        hi = min(max(a["low"], a["high"]), max(b["low"], b["high"]), max(c["low"], c["high"]))
        if lo < hi:
            zss.append({"from": a["edt"], "to": c["edt"], "ZD": round(lo, 2), "ZG": round(hi, 2)})
    return zss


if __name__ == "__main__":
    out = {}

    # ---- 1) 三个指数 1 分钟 + 15 分钟 ----
    for tag, sid, nm in [("sh", "1.000001", "上证"), ("sz", "0.399001", "深成"), ("cy", "0.399006", "创业板")]:
        m1 = kline(sid, 1, 1500)
        m15 = kline(sid, 15, 200)
        a1 = analyze(m1, "1分钟", f"{tag}_1m")
        a15 = analyze(m15, "15分钟", f"{tag}_15m")
        out[nm] = {
            "m1_bi": (a1 or {}).get("bi"),
            "m1_zs": zs_from_bi((a1 or {}).get("bi") or []),
            "m15_bi": (a15 or {}).get("bi"),
            "m15_zs": zs_from_bi((a15 or {}).get("bi") or []),
            "m15_tail": m15[-16:],
        }
        time.sleep(0.3)

    # ---- 2) AI视频 15 分钟 ----
    aiv = kline("90.BK1761", 15, 400)
    aa = analyze(aiv, "15分钟", "aivideo_15m")
    out["AI视频"] = {"bi": (aa or {}).get("bi"), "zs": zs_from_bi((aa or {}).get("bi") or [])}

    # ---- 3) 关键位：瑞芯微 248.49 / 海天瑞声 155.5 / 伊利 / 中国船舶 / 兆易 ----
    key = {}
    for nm, code, days in [("瑞芯微", "1.603893", 120), ("海天瑞声", "1.688787", 120),
                           ("伊利股份", "1.600887", 120), ("中国船舶", "1.600150", 120),
                           ("兆易创新", "1.603986", 120), ("江波龙", "0.301308", 120),
                           ("药明康德", "1.603259", 120), ("云铝股份", "0.000807", 120),
                           ("华策影视", "0.300133", 120)]:
        d = kline(code, 101, days)
        if not d:
            continue
        hi60 = max(r["h"] for r in d[-60:])
        hi_all = max(r["h"] for r in d)
        last = d[-1]
        prev = d[-2] if len(d) > 1 else None
        key[nm] = {
            "close": last["c"], "high": last["h"], "low": last["l"], "pct": last["pct"],
            "high60": hi60, "high_all": hi_all,
            "high60_date": next((r["dt"][:10] for r in d[-60:] if r["h"] == hi60), None),
            "high_all_date": next((r["dt"][:10] for r in d if r["h"] == hi_all), None),
            "prev_low": prev["l"] if prev else None,
            "dist_high60_pct": round((last["c"] / hi60 - 1) * 100, 2),
            "tail": [{"d": r["dt"][:10], "c": r["c"], "h": r["h"], "l": r["l"], "pct": r["pct"]} for r in d[-8:]],
        }
        time.sleep(0.25)
    out["key_levels"] = key

    with open(f"{BASE}/dyh_close_struct.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for nm in ("上证", "深成", "创业板"):
        print(f"===== {nm} 1分钟中枢序列 =====")
        for z in out[nm]["m1_zs"][-4:]:
            print("   ", z)
        print(f"----- {nm} 15分钟中枢序列 -----")
        for z in out[nm]["m15_zs"][-4:]:
            print("   ", z)
    print("===== AI视频 15分钟 =====")
    for z in out["AI视频"]["zs"][-5:]:
        print("   ", z)
    print("   笔:", json.dumps(out["AI视频"]["bi"], ensure_ascii=False))
    print("\n===== 关键位 =====")
    for nm, v in out["key_levels"].items():
        print(f"  {nm}: 收{v['close']:.2f} {v['pct']:+.2f}% 60日高{v['high60']:.2f}({v['high60_date']}) 全期高{v['high_all']:.2f}({v['high_all_date']}) 距60日高{v['dist_high60_pct']:+.1f}%")
