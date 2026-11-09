"""都业华 11/09 收评 · 缠论结构核验 + 玄学链样本表现"""
import json
import os
import time
from pathlib import Path

import pandas as pd
import tushare as ts

OUT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261109")
TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)

cz = json.loads((OUT / "czsc_15m.json").read_text(encoding="utf-8"))


def zhongshu(bi_list):
    """按标准缠论：连续 3 笔重叠区间 → 中枢 (ZG=max low, ZD=min high)。"""
    out = []
    for i in range(len(bi_list) - 2):
        s = bi_list[i: i + 3]
        zg = min(b["high"] for b in s)
        zd = max(b["low"] for b in s)
        if zg > zd:
            out.append({
                "from": s[0]["sdt"], "to": s[-1]["edt"],
                "ZG": round(zg, 2), "ZD": round(zd, 2),
                "direction": s[1]["direction"],
                "bi3_power": s[2].get("power"),
            })
    return out


def verdict(name):
    d = cz.get(name)
    if not d:
        return {}
    bi = d["czsc"]["bi_list"]
    zs = zhongshu(bi)
    last3 = bi[-3:]
    # 最后一笔方向 / 是否创新低
    last_bi = bi[-1]
    lows = [b["low"] for b in bi]
    res = {
        "n_bi": len(bi),
        "last_bi": {"dir": last_bi["direction"], "from": last_bi["sdt"], "to": last_bi["edt"],
                    "high": last_bi["high"], "low": last_bi["low"], "power": last_bi.get("power")},
        "last3": [{"dir": b["direction"], "high": b["high"], "low": b["low"], "power": b.get("power")} for b in last3],
        "zs_list": zs[-4:],
        "n_zs": len(zs),
        "zs_now": zs[-1] if zs else None,
    }
    # 背驰粗判：同向两笔，后一笔力度(power) 小于前一笔 且 价格创新低/新高
    if len(bi) >= 4:
        a, b = bi[-3], bi[-2]
        if a["direction"] == b["direction"] and a.get("power") and b.get("power"):
            if a["direction"] == "向下" and b["low"] < a["low"]:
                res["divergence"] = "底背驰(疑)" if b["power"] < a["power"] else "无底背驰(下跌延续)"
            if a["direction"] == "向上" and b["high"] > a["high"]:
                res["divergence"] = "顶背驰(疑)" if b["power"] < a["power"] else "无顶背驰(上涨延续)"
    # 相对 40 日位置
    df = pd.read_csv(OUT / "data" / f"{d['code'].replace('.', '_')}_15m.csv")
    last = df["close"].iloc[-1]
    res["last15m_close"] = round(float(last), 2)
    res["bar_high_5d"] = round(float(df["high"].tail(80).max()), 2)
    res["bar_low_5d"] = round(float(df["low"].tail(80).min()), 2)
    return res


names = ["药明康德", "中国船舶", "瑞芯微", "伊利股份", "江波龙", "兆易创新",
         "海天瑞声", "华策影视", "云铝股份", "上证指数", "创业板指"]
out = {n: verdict(n) for n in names}
(OUT / "czsc_verdict.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for n, v in out.items():
    print(n, json.dumps(v.get("zs_now"), ensure_ascii=False), "| last:", json.dumps(v.get("last_bi"), ensure_ascii=False),
          "| div:", v.get("divergence"))

# ── 玄学链样本 11/09 表现 ───────────────────────────────
YANG = {
    "三羊马": "001317.SZ", "水羊股份": "300740.SZ", "阳光照明": "601261.SH", "明阳电路": "603739.SH",
    "圣阳股份": "002580.SZ", "海洋王": "002194.SZ", "东方海洋": "002086.SZ", "襄阳轴承": "000678.SZ",
    "七匹狼": "002029.SZ", "鲁阳节能": "002088.SZ", "太阳能": "000591.SZ", "大西洋": "600558.SH",
    "九阳股份": "002242.SZ", "东方环宇": "603706.SH", "日出东方": "603366.SH", "东方嘉盛": "002889.SZ",
    "东方通信": "600776.SH", "大东方": "600327.SH", "东方创业": "600278.SH", "东方新能": "002310.SZ",
    "明阳智能": "601615.SH", "扬子新材": "600652.SH", "扬杰科技": "300373.SZ", "久之洋": "300164.SZ",
    "澳洋健康": "002172.SZ", "长阳科技": "688299.SH", "岳阳兴长": "000819.SZ", "盛洋科技": "603703.SH",
}
rows = []
d = pro.daily(trade_date="20261109")
for n, c in YANG.items():
    r = d[d["ts_code"] == c]
    if r.empty:
        continue
    r = r.iloc[0]
    rows.append({"名称": n, "代码": c, "收盘": round(float(r["close"]), 2),
                 "涨跌幅%": round(float(r["pct_chg"]), 2), "成交额万": round(float(r["amount"]) / 1e4, 1),
                 "换手%": round(float(r.get("turnover_rate", 0) or 0), 2)})
dfy = pd.DataFrame(rows).sort_values("涨跌幅%", ascending=False)
dfy.to_csv(OUT / "data" / "xuanxue_20261109.csv", index=False)
print(dfy.to_string(index=False))
