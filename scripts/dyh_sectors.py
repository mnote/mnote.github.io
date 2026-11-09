"""板块快照 + 指数成交额 → sectors_20261109.json / index_20261109.json"""
import json
import os
import time
from pathlib import Path

import requests
import tushare as ts

OUT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261109")
TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def boards(fs):
    out = []
    for pn in range(1, 8):
        url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1&fltt=2&invt=2"
               f"fid=f3&fs={fs}&fields=f12,f14,f3,f104,f105,f128,f136")
        try:
            js = requests.get(url, headers=UA, timeout=25).json()
            diff = (js.get("data") or {}).get("diff") or []
            if not diff:
                break
            out += diff
        except Exception as e:
            print("err", fs, pn, e)
        time.sleep(0.6)
    return out


ind = boards("m:90+t:2")      # 行业板块
con = boards("m:90+t:3")      # 概念板块
allb = {b["f14"]: {"code": b["f12"], "pct": b["f3"], "up": b["f104"], "down": b["f105"],
                   "leader": b["f128"], "leader_pct": b["f136"]} for b in ind}
allc = {b["f14"]: {"code": b["f12"], "pct": b["f3"], "up": b["f104"], "down": b["f105"],
                   "leader": b["f128"], "leader_pct": b["f136"]} for b in con}
(OUT / "sectors_20261109.json").write_text(json.dumps({"行业": allb, "概念": allc}, ensure_ascii=False, indent=1), encoding="utf-8")

KEEP_IND = ["光伏设备", "光伏主材", "光伏辅材", "光伏电池组件", "光伏发电", "光伏加工设备",
            "元件", "半导体", "半导体设备", "半导体材料", "机器人", "消费电子", "消费电子零部件及组装",
            "电池", "锂电池", "电池化学品", "光学元件", "被动元件", "电子", "通信设备", "军工电子"]
KEEP_CON = ["光通信模块", "CPO概念", "光纤概念", "液冷服务器", "激光雷达", "光刻机", "储能", "算力租赁"]
sel = {"行业": {k: allb[k] for k in KEEP_IND if k in allb},
       "概念": {k: allc[k] for k in KEEP_CON if k in allc}}
print(json.dumps(sel, ensure_ascii=False, indent=1))

# 指数成交额
idx = {}
for code, nm in [("000001.SH", "上证指数"), ("399001.SZ", "深证成指"), ("399006.SZ", "创业板指"),
                 ("000300.SH", "沪深300"), ("000688.SH", "科创50")]:
    try:
        df = pro.index_daily(ts_code=code, start_date="20261001", end_date="20261109")
        df = df.sort_values("trade_date")
        last, prev = df.iloc[-1], df.iloc[-2]
        idx[nm] = {"code": code, "close": round(float(last["close"]), 2),
                   "pct": round((float(last["close"]) / float(prev["close"]) - 1) * 100, 2),
                   "amount_yi": round(float(last["amount"]) / 1e5, 1),
                   "prev_amount_yi": round(float(prev["amount"]) / 1e5, 1),
                   "vol": int(last["vol"]), "prev_vol": int(prev["vol"])}
        time.sleep(0.4)
    except Exception as e:
        idx[nm] = {"error": str(e)}
(OUT / "index_20261109.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(idx, ensure_ascii=False, indent=1))
