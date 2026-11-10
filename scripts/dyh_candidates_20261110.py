"""都业华 2026-11-10 收评纪要 · 潜在强势股候选测算
按老师原文逻辑：热点细分中表现强势标的 → 剔除涨幅大的 → 保留位置不高、中线有上涨概率
输出：reports/duyiehua-20261110/data/candidates_20261110.csv
"""
import csv
import json
import os
import time
from pathlib import Path

import tushare as ts

pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
RPT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261110")
DATA = RPT / "data"
market = json.loads((RPT / "market_20261110.json").read_text(encoding="utf-8"))
pool = market.get("zt_pool", [])

# 老师认定的三条主线 + 相关细分
HOT = ["汽车零部", "通用设备", "光学光电", "专用设备", "消费电子", "影视院线", "广告营销",
       "游戏Ⅱ", "游戏", "数字媒体", "自动化设", "自动化设备", "出版", "通信设备", "元件",
       "半导体", "计算机设", "计算机设备", "IT服务Ⅱ", "IT服务", "软件开发", "影视院线"]

rows = []
for p in pool:
    if p["hy"] not in HOT:
        continue
    code = p["code"]
    ts_code = f"{code}.SH" if code[0] in "56" else f"{code}.SZ"
    for _ in range(3):
        try:
            df = pro.daily(ts_code=ts_code, start_date="20260601", end_date="20261110")
            break
        except Exception:
            time.sleep(1.2)
    if df is None or len(df) < 60:
        continue
    df = df.sort_values("trade_date").reset_index(drop=True)
    last = df.iloc[-1]
    hi60 = float(df["high"].tail(60).max())
    lo60 = float(df["low"].tail(60).min())
    ret60 = round((float(last["close"]) / float(df["close"].iloc[-60]) - 1) * 100, 1)
    ret5 = round((float(last["close"]) / float(df["close"].iloc[-6]) - 1) * 100, 1)
    vol_ratio = round(float(last["vol"]) / float(df["vol"].tail(5).iloc[:-1].mean()), 2)
    rows.append({
        "名称": p["name"], "代码": ts_code, "收盘": round(float(last["close"]), 2),
        "涨跌幅%": p["pct"], "连板": p["lbc"], "行业": p["hy"],
        "60日涨幅%": ret60, "距60日高%": round((float(last["close"]) / hi60 - 1) * 100, 1),
        "近5日涨幅%": ret5, "今日量/5日均量": vol_ratio,
    })
    time.sleep(0.12)

rows.sort(key=lambda r: r["距60日高%"])
with open(DATA / "candidates_20261110.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(json.dumps(rows, ensure_ascii=False, indent=1))
