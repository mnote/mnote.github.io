#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""十点看盘核验 v3：成交额同比 / 上证关键位 / 外围 / 涨停家数"""
import json
import os
import time
import urllib.request

import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(1.5)


out = {}

# ---- 1) 11/09 全 A 成交额 / 涨跌家数 ----
for _ in range(4):
    try:
        df = pro.daily(trade_date="20261109")
        break
    except Exception as e:
        print("tushare retry", e)
        time.sleep(2)
out["a_share_20261109"] = {
    "n": len(df),
    "amount_yi": round(df["amount"].sum() / 1e5, 0),
    "up": int((df["pct_chg"] > 0).sum()),
    "down": int((df["pct_chg"] < 0).sum()),
    "limit_up": int((df["pct_chg"] >= 9.8).sum()),
}
sh = df[df["ts_code"].str.endswith(".SH")]
sz = df[df["ts_code"].str.endswith(".SZ")]
out["a_share_20261109"]["sh_amount_yi"] = round(sh["amount"].sum() / 1e5, 0)
out["a_share_20261109"]["sz_amount_yi"] = round(sz["amount"].sum() / 1e5, 0)

# ---- 2) 上证 11/09 日线 + 近 20 日 ----
try:
    idx = pro.index_daily(ts_code="000001.SH", start_date="20261001", end_date="20261110")
    idx = idx.sort_values("trade_date")
    out["sh_index"] = idx.tail(8)[["trade_date", "open", "high", "low", "close", "amount"]].to_dict("records")
    out["sh_amount_note"] = "index_daily amount 单位千元"
except Exception as e:
    print("idx fail", e)

# ---- 3) 外围：美股 11/09 收盘 ----
try:
    for code, nm in [("DJI", "道琼斯"), ("IXIC", "纳斯达克"), ("SPX", "标普500")]:
        g = pro.index_global(ts_code=code, start_date="20261105", end_date="20261110")
        g = g.sort_values("trade_date")
        out.setdefault("us", {})[nm] = g.tail(3)[["trade_date", "close", "pct_chg"]].to_dict("records")
except Exception as e:
    print("us fail", e)

# ---- 4) 沪深分时 2 天，算 11/09 同期成交额 ----
for nm, secid in [("上证", "1.000001"), ("深证", "0.399001")]:
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={secid}"
              "&ndays=2&iscr=0&iscca=0&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
              "&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
    if not d or not d.get("data"):
        continue
    day = {}
    for line in (d["data"].get("trends") or []):
        p = line.split(",")
        if len(p) < 7:
            continue
        dt = p[0][:10]
        try:
            day.setdefault(dt, []).append(float(p[6]))
        except Exception:
            pass
    res = {}
    for dt, amts in day.items():
        res[dt] = {"全日累计(亿)": round(sum(amts) / 1e8, 0), "至10:30(亿)": round(sum(a for a in amts[:61]) / 1e8, 0)}
    out.setdefault("intraday_amount", {})[nm] = res

# ---- 5) 涨停/跌停家数（实时） ----
for kind, api in [("涨停", "getTopicZTPool"), ("跌停", "getTopicDTPool")]:
    d = fetch(f"https://push2ex.eastmoney.com/{api}?ut=7eea3edcaed734bea9cbfc24409ed989"
              "&dpt=wz.ztzt&pageindex=0&pagesize=1&sort=fbt:asc&date=20261110")
    if d and d.get("data"):
        out.setdefault("limit", {})[kind] = d["data"].get("tc")
    else:
        out.setdefault("limit", {})[kind] = None

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
with open("/Users/maoling/.minimax/sessions/mvs_8fd393de9e26477a84613df387fd3774/workspace/dyh_1010_volume.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
