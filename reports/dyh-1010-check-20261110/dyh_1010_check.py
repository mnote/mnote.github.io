#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""都业华【十点看盘】2026-11-10 观点核验
核验点：
1) 上证是否高开 / 是否站上 3750 / 早盘是否震荡下行
2) 成交额：早盘实际 vs 全日预估 1.5 万亿
3) 算力板块早盘高开后是否震荡下行
4) AI应用 / AI短剧 / 游戏 / 传媒板块活跃度
"""
import json
import re
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:120], e)
                return None
            time.sleep(1.5)


def em_snapshot(secid):
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}"
              "&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f168,f169,f170")
    if not d or not d.get("data"):
        return None
    x = d["data"]
    return {
        "name": x.get("f58"), "code": x.get("f57"),
        "price": x.get("f43") / 100, "high": x.get("f44") / 100, "low": x.get("f45") / 100,
        "open": x.get("f46") / 100, "prev": x.get("f60") / 100,
        "amount_yi": (x.get("f48") or 0) / 1e8,
        "pct": x.get("f170") / 100, "chg": x.get("f169") / 100,
    }


def concept_boards(bs="m:90+t:3"):
    out = []
    for pn in range(1, 12):
        d = fetch(f"https://push2.eastmoney.com/api/qt/clist/get?fs={bs}&pn={pn}&pz=100"
                  "&po=1&np=1&fltt=2&invt=2&fid=f3&fields=f2,f3,f6,f12,f14,f62,f104,f105,f128,f140")
        if not d or not d.get("data") or not d["data"].get("diff"):
            break
        diff = d["data"]["diff"]
        if isinstance(diff, dict):
            diff = list(diff.values())
        for it in diff:
            out.append(it)
        if len(diff) < 100:
            break
        time.sleep(0.3)
    return out


def board_trend(bk):
    """板块分时，算开盘涨跌幅 / 当前涨跌幅 / 冲高回落幅度"""
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid=90.{bk}"
              "&ndays=1&iscr=0&iscca=0&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
              "&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
    if not d or not d.get("data"):
        return None
    tr = d["data"].get("trends") or []
    if not tr:
        return None
    pts = []
    for line in tr:
        p = line.split(",")
        try:
            pts.append((p[0], float(p[2]), float(p[3]), float(p[8])))
        except Exception:
            pass
    if not pts:
        return None
    prev = float(d["data"]["preClose"])
    opens = [p for p in pts if "09:30" in p[0]]
    first = opens[0] if opens else pts[0]
    hi = max(p[2] for p in pts)
    lo = min(p[2] for p in pts)
    last = pts[-1]
    return {
        "open_pct": round((first[1] / prev - 1) * 100, 2),
        "now_pct": round((last[1] / prev - 1) * 100, 2),
        "high_pct": round((hi / prev - 1) * 100, 2),
        "low_pct": round((lo / prev - 1) * 100, 2),
        "amount_yi": round(last[3] / 1e8, 2),
        "n": len(pts),
    }


if __name__ == "__main__":
    out = {}

    # 1) 指数
    idx = {}
    for secid, nm in [("1.000001", "上证指数"), ("0.399001", "深证成指"), ("0.399006", "创业板指"),
                      ("1.000688", "科创50"), ("0.399905", "中证500"), ("1.000300", "沪深300")]:
        s = em_snapshot(secid)
        if s:
            s["secid"] = secid
            s["gap_pct"] = round((s["open"] / s["prev"] - 1) * 100, 2)
            s["from_high_pct"] = round((s["price"] / s["high"] - 1) * 100, 2)
            idx[nm] = s
    out["index"] = idx

    # 2) 概念板块快照
    boards = concept_boards("m:90+t:3")
    out["concept_n"] = len(boards)
    keys = ["算力", "短剧", "AI应用", "游戏", "传媒", "AIGC", "人工智能", "影视", "IP", "ChatGPT", "多模态", "液冷", "服务器", "光模块", "CPO", "数据中心"]
    hit = {}
    for b in boards:
        nm = b.get("f14", "")
        for k in keys:
            if k in nm:
                hit.setdefault(nm, b)
    out["concept_hits"] = [
        {"name": b.get("f14"), "code": b.get("f12"), "pct": b.get("f3"), "amount_yi": round((b.get("f6") or 0) / 1e8, 2),
         "up": b.get("f104"), "down": b.get("f105"), "main_net_yi": round((b.get("f62") or 0) / 1e8, 2)}
        for b in hit.values()
    ]

    # 3) 重点板块分时
    focus = []
    for nm in ["算力租赁", "算力概念", "AI应用", "AI短剧", "短剧游戏", "游戏", "文化传媒", "AIGC概念"]:
        for b in hit.values():
            if b.get("f14") == nm:
                t = board_trend(b["f12"])
                if t:
                    t["name"] = nm
                    t["code"] = b["f12"]
                    t["snap_pct"] = b.get("f3")
                    focus.append(t)
                break
    out["focus_trend"] = focus

    with open("/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace/dyh_1010_market.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2)[:6000])
