"""11/10 板块成分统计（剔除 2026-10 以后上市的次新，避免首日暴涨污染均值）。

用法： ~/czsc/.venv/bin/python scripts/collect_sectors_20261110.py
"""
import json
import os
import urllib.request

import tushare as ts

ts.set_token(os.environ.get(
    "TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
pro = ts.pro_api()
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}


def get(u):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=25).read())


basic = pro.stock_basic(ts_code="", list_status="L", fields="ts_code,name,list_date")
ld = {r.ts_code: str(r.list_date) for r in basic.itertuples()}

BOARDS = [
    ("BK1184", "人形机器人"),
    ("BK1178", "AI眼镜(端侧)"),
    ("BK0641", "智能穿戴"),
    ("BK1127", "AI芯片"),
    ("BK1090", "机器人概念"),
    ("BK1162", "AI手机"),
    ("BK1766", "智能音箱"),
    ("BK1125", "电子后视镜"),
]


def board(bk, name, drop_after="20260930"):
    url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=300&po=1&np=1"
           f"&fltt=2&invt=2&fid=f3&fs=b:{bk}&fields=f2,f3,f12,f14,f62")
    d = get(url)["data"]["diff"]
    rows = []
    for x in d:
        code = x["f12"]
        ts_code = (code + ".SH") if code.startswith("6") else (code + ".SZ")
        if code.startswith(("4", "8", "9")):
            ts_code = code + ".BJ"
        if ts_code in ld and ld[ts_code] >= drop_after:
            continue
        rows.append(x)
    avg = sum(x["f3"] for x in rows) / len(rows)
    up = sum(1 for x in rows if x["f3"] > 0)
    flow = sum(x["f62"] for x in rows
               if isinstance(x["f62"], (int, float))) / 1e8
    print(f"{name}: 样本{len(rows)} 均值{avg:+.2f}% 上涨{up}/{len(rows)} "
          f"主力{flow:+.1f}亿")
    print("   前8: " + ", ".join(f'{x["f14"]}{x["f3"]:+.2f}' for x in rows[:8]))
    return rows


if __name__ == "__main__":
    for bk, name in BOARDS:
        board(bk, name)
