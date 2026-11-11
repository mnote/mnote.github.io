"""11/11 盘中板块成分统计（东财接口，翻页取全板块 + 板块成分明细）。

口径与 11/10 一致：剔除 2026-09-30 以后上市的次新，避免首日暴涨污染均值。

用法： ~/czsc/.venv/bin/python scripts/collect_sectors_20261111.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

import tushare as ts

ts.set_token(os.environ.get(
    "TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
pro = ts.pro_api()

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}
DROP_AFTER = "20260930"


def get(u):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=25).read())


def all_boards():
    base = ("https://push2.eastmoney.com/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1"
            "&fltt=2&invt=2&fid=f3&fs=m:90+t:3&fields=f2,f3,f12,f14,f62")
    out = []
    for pn in range(1, 12):
        d = get(base.format(pn=pn)).get("data")
        if not d or not d.get("diff"):
            break
        out += d["diff"]
        time.sleep(0.12)
    return out


_ld = None


def list_dates():
    global _ld
    if _ld is None:
        basic = pro.stock_basic(ts_code="", list_status="L",
                                fields="ts_code,name,list_date")
        _ld = {r.ts_code: str(r.list_date) for r in basic.itertuples()}
    return _ld


def board(bk, name, topn=10):
    url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=300&po=1&np=1"
           f"&fltt=2&invt=2&fid=f3&fs=b:{bk}&fields=f2,f3,f12,f14,f62")
    try:
        data = get(url).get("data")
        d = data["diff"] if data else []
    except Exception as e:
        print(f"{name}: ERR {e}")
        return None
    if not d:
        print(f"{name}: empty")
        return None

    ld = list_dates()
    rows, dropped = [], 0
    for x in d:
        code = x["f12"]
        ts_code = (code + ".SH") if code.startswith("6") else (code + ".SZ")
        if code.startswith(("4", "8", "9")):
            ts_code = code + ".BJ"
        if ts_code in ld and ld[ts_code] >= DROP_AFTER:
            dropped += 1
            continue
        rows.append(x)

    vals = [x["f3"] for x in rows if isinstance(x.get("f3"), (int, float))]
    avg = sum(vals) / len(vals)
    up = sum(1 for v in vals if v > 0)
    flow = sum(x["f62"] for x in rows
               if isinstance(x.get("f62"), (int, float))) / 1e8
    head = ", ".join(f'{x["f14"]}{x["f3"]:+.2f}' for x in rows[:topn])
    print(f"{name} ({bk}): 样本{len(rows)}（剔次新{dropped}） 均值{avg:+.2f}% "
          f"上涨{up}/{len(vals)} 主力{flow:+.1f}亿")
    print(f"   {head}")
    return {
        "bk": bk, "name": name, "n": len(rows), "dropped": dropped,
        "avg": round(avg, 2), "up": up, "total": len(vals),
        "flow_yi": round(flow, 1),
        "top": [{"name": x["f14"], "code": x["f12"], "pct": x["f3"],
                 "flow_yi": round((x.get("f62") or 0) / 1e8, 2)} for x in rows[:topn]],
    }


BOARDS = [
    ("BK1128", "CPO概念"),
    ("BK1136", "光通信模块"),
    ("BK1660", "光纤概念"),
    ("BK1137", "存储芯片"),
    ("BK1178", "AI眼镜/端侧"),
    ("BK1184", "人形机器人"),
    ("BK1090", "机器人概念"),
    ("BK0641", "智能穿戴"),
    ("BK1162", "AI手机"),
    ("BK1766", "智能音箱"),
    ("BK1125", "电子后视镜"),
    ("BK1127", "AI芯片"),
]

if __name__ == "__main__":
    boards = all_boards()
    print(f"[boards] 共 {len(boards)} 个概念板块\n")
    out = []
    for bk, name in BOARDS:
        r = board(bk, name, 8)
        if r:
            out.append(r)
        time.sleep(0.15)
    p = Path("/Users/maoling/workspace/mnote.github.io/charts/_sectors_20261111.json")
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {p}")
