#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""都业华【两点看盘】2026-11-10 核验：端侧AI / 算力午后资金 / 上证1分钟三买"""
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


def kline(secid, klt=101, lmt=100):
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


def trends(secid, ndays=1):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={secid}"
              f"&ndays={ndays}&iscr=0&iscca=0&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
              "&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
    if not d or not d.get("data"):
        return None, []
    prev = d["data"].get("preClose")
    pts = []
    for line in (d["data"].get("trends") or []):
        p = line.split(",")
        if len(p) < 7:
            continue
        try:
            pts.append({"t": p[0], "o": float(p[1]), "c": float(p[2]), "h": float(p[3]),
                        "l": float(p[4]), "vol": float(p[5]), "amt": float(p[6]), "avg": float(p[7])})
        except Exception:
            pass
    for p in pts:
        p["pct"] = (p["c"] / prev - 1) * 100
    return prev, pts


def board_flow(bk):
    """板块资金流分时（主力净流入）"""
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=1&secid=90.{bk}"
              "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65")
    if not d or not d.get("data"):
        return []
    out = []
    for kk in (d["data"].get("klines") or []):
        p = kk.split(",")
        try:
            out.append({"t": p[0], "main": float(p[1]), "small": float(p[2]), "mid": float(p[3]),
                        "big": float(p[4]), "super": float(p[5])})
        except Exception:
            pass
    return out


def czsc(csv_path, freq):
    p = subprocess.run([os.path.expanduser("~/czsc/.venv/bin/czsc"), "analyze", csv_path,
                        "--freq", freq, "--json"], capture_output=True, text=True, timeout=240)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"error": (p.stdout or "")[-300:] + (p.stderr or "")[-300:]}


if __name__ == "__main__":
    out = {}

    # ---- 1) 找端侧AI 相关板块 ----
    boards = {}
    for bs in ("m:90+t:3", "m:90+t:2"):
        for pn in range(1, 12):
            d = fetch(f"https://push2.eastmoney.com/api/qt/clist/get?fs={bs}&pn={pn}&pz=100"
                      "&po=1&np=1&fltt=2&invt=2&fid=f3&fields=f2,f3,f6,f12,f14,f62,f104,f105,f184")
            if not d or not d.get("data") or not d["data"].get("diff"):
                break
            diff = d["data"]["diff"]
            if isinstance(diff, dict):
                diff = list(diff.values())
            for it in diff:
                boards[it["f12"]] = it
            if len(diff) < 100:
                break
            time.sleep(0.2)
    keys = ["端侧", "AI手机", "AI眼镜", "AI PC", "AIPC", "AI硬件", "智能穿戴", "消费电子", "AI终端", "端侧AI"]
    hits = {c: v for c, v in boards.items() if any(k in v["f14"] for k in keys)}
    out["edge_board_hits"] = {c: {"name": v["f14"], "pct": v.get("f3"),
                                 "amount_yi": round((v.get("f6") or 0) / 1e8, 1),
                                 "up": v.get("f104"), "down": v.get("f105"),
                                 "main_net_yi": round((v.get("f62") or 0) / 1e8, 2),
                                 "main_pct": v.get("f184")} for c, v in hits.items()}
    # 相关板块近 10 日（看"前期抗跌"）
    rel = {}
    for c, v in hits.items():
        ks = kline("90." + c, 101, 12)
        rel[v["f14"]] = [{"d": r["dt"][:10], "c": r["c"], "pct": r["pct"], "amt_yi": round(r["amt"] / 1e8, 1)} for r in ks]
        time.sleep(0.2)
    out["edge_board_10d"] = rel

    # ---- 2) 端侧AI + 算力 分时 ----
    for tag, bk in [("端侧AI", "BK1176"), ("AIPC", "BK1164"), ("算力概念", "BK1134")]:
        prev, pts = trends("90." + bk)
        if not pts:
            continue
        am = pts[0]["t"][11:16]
        pm = [p for p in pts if p["t"][11:16] >= "13:00"]
        out.setdefault("trend", {})[tag] = {
            "open_pct": round(pts[0]["pct"], 2), "now_pct": round(pts[-1]["pct"], 2),
            "am_end_pct": round([p for p in pts if p["t"][11:16] <= "11:30"][-1]["pct"], 2),
            "pm_high_pct": round(max(p["pct"] for p in pm), 2) if pm else None,
            "pm_low_pct": round(min(p["pct"] for p in pm), 2) if pm else None,
            "amt_yi": round(pts[-1]["amt"] / 1e8, 1),
            "last_t": pts[-1]["t"],
        }
    # ---- 3) 算力板块资金流（午后主力净流入）----
    fl = board_flow("BK1134")
    if fl:
        am = [f for f in fl if f["t"][11:16] <= "11:30"]
        pm = [f for f in fl if f["t"][11:16] >= "13:00"]
        out["su_li_flow"] = {
            "n": len(fl), "last_t": fl[-1]["t"],
            "main_total_yi": round(fl[-1]["main"] / 1e8, 2),
            "main_pm_yi": round((fl[-1]["main"] - (am[-1]["main"] if am else 0)) / 1e8, 2),
            "main_am_yi": round((am[-1]["main"] if am else 0) / 1e8, 2),
            "pm_points": [{"t": f["t"][11:16], "main_yi": round(f["main"] / 1e8, 2)} for f in pm[-20:]],
        }
    # 端侧AI 板块代码待定后补

    # ---- 4) 上证 1 分钟 K + czsc ----
    m1 = kline("1.000001", 1, 1400)
    out["sh_1m_count"] = len(m1)
    if m1:
        p = f"{BASE}/_tmp_sh_1m.csv"
        with open(p, "w") as f:
            f.write("dt,symbol,open,close,high,low,vol,amount\n")
            for r in m1:
                f.write(f'{r["dt"]},{r["dt"]},{r["o"]},{r["c"]},{r["h"]},{r["l"]},{r["vol"]},{r["amt"]}\n')
        ana = czsc(p, "1分钟")
        bl = ana.get("bi_list") or []
        out["sh_1m_bi"] = [{"edt": str(b.get("edt"))[:19], "dir": b.get("direction"),
                             "high": b.get("high"), "low": b.get("low"), "power": b.get("power")}
                            for b in bl[-10:]]
        out["sh_1m_fx"] = [{"dt": str(f.get("dt"))[:19], "mark": f.get("mark"),
                            "high": f.get("high"), "low": f.get("low")} for f in (ana.get("fx_list") or [])[-10:]]
        today = [r for r in m1 if r["dt"].startswith("2026-11-10")]
        out["sh_1m_today_range"] = {"n": len(today),
                                    "high": max((r["h"] for r in today), default=None),
                                    "low": min((r["l"] for r in today), default=None),
                                    "last": today[-1] if today else None}
        out["sh_1m_tail"] = m1[-30:]

    # ---- 5) 午后成交额 ----
    for nm, sid in [("上证", "1.000001"), ("深证", "0.399001")]:
        prev, pts = trends(sid, 2)
        if not pts:
            continue
        day = {}
        for p_ in pts:
            day.setdefault(p_["t"][:10], []).append(p_)
        r = {}
        for dt, ps in day.items():
            r[dt] = {"至11:30": round(sum(x["amt"] for x in ps if x["t"][11:16] <= "11:30") / 1e8, 0),
                     "至14:15": round(sum(x["amt"] for x in ps if x["t"][11:16] <= "14:15") / 1e8, 0),
                     "全日累计": round(sum(x["amt"] for x in ps) / 1e8, 0)}
        out.setdefault("amount_by_day", {})[nm] = r

    with open(f"{BASE}/dyh_1400_check.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out.get("edge_board_hits", {}), ensure_ascii=False, indent=2))
    print("\n== 分时 ==")
    print(json.dumps(out.get("trend", {}), ensure_ascii=False, indent=2))
    print("\n== 算力资金流 ==")
    print(json.dumps(out.get("su_li_flow", {}), ensure_ascii=False, indent=2))
    print("\n== 上证1分钟笔 ==")
    print(json.dumps(out.get("sh_1m_bi", {}), ensure_ascii=False, indent=2))
    print("\n== 上证1分钟分型 ==")
    print(json.dumps(out.get("sh_1m_fx", {}), ensure_ascii=False, indent=2))
    print("\n== 今日1分钟区间 ==")
    print(json.dumps(out.get("sh_1m_today_range", {}), ensure_ascii=False, indent=2))
    print("\n== 成交额 ==")
    print(json.dumps(out.get("amount_by_day", {}), ensure_ascii=False, indent=2))
