"""都业华 2026-11-11 收评纪要 · 数据采集（tushare 口径，东财限流时的降级方案）
指数 / 全市场宽度 / 申万行业 / 涨停（涨幅口径）/ 15 分钟中枢（stk_mins）/ 月线中枢（日线聚合）
"""
import csv
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd
import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261111"
DATA = RPT / "data"
for p in (RPT, DATA):
    p.mkdir(parents=True, exist_ok=True)
CZ = os.path.expanduser("~/czsc/.venv/bin/czsc")
pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
DATE, PREV = "20261111", "20261110"
OUT = {}

TARGETS = {
    "上证指数": "000001.SH", "创业板指": "399006.SZ", "科创50": "000688.SH",
    "药明康德": "603259.SH", "中国船舶": "600150.SH", "瑞芯微": "603893.SH",
    "伊利股份": "600887.SH", "中文在线": "300364.SZ", "海天瑞声": "688787.SH",
    "奥普特": "688686.SH", "柯力传感": "603662.SH", "兆易创新": "603986.SH",
    "云铝股份": "000807.SZ", "凯莱英": "002821.SZ", "昭衍新药": "603127.SH",
}


def ts_name(tsc):
    return f"{tsc.split('.')[0]}.{tsc.split('.')[1]}"


def get(fn, tries=4, **kw):
    for i in range(tries):
        try:
            d = fn(**kw)
            if d is not None:
                return d
        except Exception as e:
            print("retry", getattr(fn, "__name__", "fn"), str(e)[:80])
        time.sleep(1.5 + i)
    return None


# ═════════ 1. 指数 ═════════
idx_out = {}
for nm, tsc in [("上证指数", "000001.SH"), ("深证成指", "399001.SZ"), ("创业板指", "399006.SZ"),
                ("科创50", "000688.SH"), ("沪深300", "000300.SH")]:
    d = get(pro.index_daily, ts_code=tsc, start_date="20260101", end_date=DATE)
    if d is None or d.empty:
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    close = d["close"]
    vol = d["vol"]
    idx_out[nm] = {
        "code": tsc, "date": str(d.iloc[-1]["trade_date"]),
        "close": round(float(close.iloc[-1]), 2), "prev": round(float(close.iloc[-2]), 2),
        "open": round(float(d.iloc[-1]["open"]), 2), "high": round(float(d.iloc[-1]["high"]), 2),
        "low": round(float(d.iloc[-1]["low"]), 2),
        "pct": round((float(close.iloc[-1]) / float(close.iloc[-2]) - 1) * 100, 2),
        "amount_yi": round(float(d.iloc[-1]["amount"]) / 1e5, 1),
        "ma20": round(float(close.rolling(20).mean().iloc[-1]), 2),
        "above_ma20": bool(close.iloc[-1] > close.rolling(20).mean().iloc[-1]),
        "vol_ma5": round(float(vol.rolling(5).mean().iloc[-1]), 0),
        "vol_ma20": round(float(vol.rolling(20).mean().iloc[-1]), 0),
        "vol_bear_ma": "空头排列" if vol.rolling(5).mean().iloc[-1] < vol.rolling(20).mean().iloc[-1] else "非空头",
        "tail": [{"d": str(r.trade_date), "c": round(float(r.close), 2), "v": round(float(r.vol), 0)}
                 for _, r in d.tail(8).iterrows()],
    }
    time.sleep(0.4)
OUT["index"] = idx_out

# ═════════ 2. 全市场宽度与成交额（两日） ═════════
market = {}
for d_ in (PREV, DATE):
    df = get(pro.daily, trade_date=d_)
    if df is None or df.empty:
        continue
    p = df["pct_chg"].dropna()
    market[d_] = {"n": len(df), "amount_yi": round(float(df["amount"].sum()) / 1e5, 1),
                  "up": int((p > 0).sum()), "down": int((p < 0).sum()), "flat": int((p == 0).sum()),
                  "median_pct": round(float(p.median()), 3),
                  "zt_ge98": int((p >= 9.8).sum()), "dt_le98": int((p <= -9.8).sum())}
    time.sleep(0.5)

# 涨停个股 + 行业分布（用 tushare 行业口径，替代东财概念板块）
sb = get(pro.stock_basic, exchange="", list_status="L", fields="ts_code,symbol,name,industry")
nm_map = dict(zip(sb["ts_code"], sb["name"]))
ind_map = dict(zip(sb["ts_code"], sb["industry"]))
df = get(pro.daily, trade_date=DATE)
df["name"] = df["ts_code"].map(nm_map)
df["industry"] = df["ts_code"].map(ind_map)
zt = df[df["pct_chg"] >= 9.8].sort_values("pct_chg", ascending=False)
from collections import Counter
market["zt_by_industry"] = dict(Counter(zt["industry"].fillna("其他")).most_common(25))
market["zt_list"] = [{"code": r.ts_code, "name": r["name"], "pct": round(float(r.pct_chg), 2),
                      "industry": r["industry"]} for _, r in zt.iterrows()]
# 机器人 / 数据采集 关键词统计
kw = {"人形机器人": ["机器人", "机器", "减速", "丝杠", "伺服", "灵巧", "传感", "执行器"],
      "数据采集/视觉": ["数据", "视觉", "图像", "检测", "传感", "光学", "视觉"],
      "AI/传媒": ["传媒", "文化", "影视", "数媒", "视频", "游戏", "出版", "广告"],
      "端侧/消费电子": ["电子", "光学", "精密", "科技", "智能"]}
market["zt_kw"] = {}
for k, words in kw.items():
    sub = zt[zt["name"].astype(str).str.contains("|".join(words), na=False)]
    market["zt_kw"][k] = {"n": len(sub), "names": [f"{r['name']}({r['industry']})" for _, r in sub.head(12).iterrows()]}
OUT["market"] = market

# ═════════ 3. 板块篮子（东财概念板块不可用时的可复算替代口径） ═════════
BASKET = {
    "人形机器人": ["603662.SH", "688787.SH", "688686.SH", "601689.SH", "688017.SH", "300124.SZ",
                "603728.SH", "003021.SZ", "601100.SH", "002472.SZ", "300503.SZ", "688160.SH",
                "688698.SH", "688320.SH", "002896.SZ", "300607.SZ", "688322.SH", "002527.SZ"],
    "AI视频/传媒": ["300364.SZ", "300133.SZ", "300624.SZ", "603533.SH", "002343.SZ", "002425.SZ",
                "300413.SZ", "300251.SZ", "300058.SZ", "002027.SZ", "600977.SH", "000719.SZ"],
    "端侧AI": ["603893.SH", "002241.SZ", "002600.SZ", "300433.SZ", "688036.SH", "002351.SZ",
            "002273.SZ", "603501.SH", "002456.SZ", "300136.SZ"],
    "算力硬件": ["300308.SZ", "300502.SZ", "300394.SZ", "601138.SH", "000977.SZ", "000938.SZ",
              "002371.SZ", "688041.SH", "688256.SH", "603496.SH", "300548.SZ"],
    "半导体": ["603986.SH", "603501.SH", "002371.SZ", "688981.SH", "300782.SZ", "688008.SH",
            "688012.SH", "603160.SH"],
    "光伏设备": ["601012.SH", "002129.SZ", "300274.SZ", "688599.SH", "603806.SH", "002056.SZ",
              "300118.SZ", "605117.SH"],
}
basket = {}
zt_codes = set(zt["ts_code"])
for bname, codes in BASKET.items():
    pcts, ztn, ok = [], 0, 0
    for c in codes:
        d = get(pro.daily, ts_code=c, start_date="20261105", end_date=DATE)
        if d is None or d.empty:
            continue
        d = d.sort_values("trade_date")
        pcts.append(float(d.iloc[-1]["pct_chg"]))
        ok += 1
        if float(d.iloc[-1]["pct_chg"]) >= 9.8:
            ztn += 1
        time.sleep(0.12)
    if pcts:
        basket[bname] = {"n": ok, "avg_pct": round(sum(pcts) / len(pcts), 2),
                         "median_pct": round(sorted(pcts)[len(pcts) // 2], 2),
                         "up": sum(1 for x in pcts if x > 0), "zt": ztn,
                         "pcts": [round(x, 2) for x in pcts]}
OUT["basket"] = dict(sorted(basket.items(), key=lambda x: -x[1]["avg_pct"]))
print("板块篮子:", json.dumps({k: {kk: v[kk] for kk in ("n", "avg_pct", "up", "zt")} for k, v in OUT["basket"].items()}, ensure_ascii=False))

# ═════════ 4. 15 分钟中枢（stk_mins） ═════════
czv = {}
for nm, tsc in TARGETS.items():
    time.sleep(62)   # stk_mins 频率限制 1 次/分钟
    m = get(pro.stk_mins, ts_code=ts_name(tsc), freq="15min",
            start_date="2026-10-28 09:00:00", end_date="2026-11-11 15:30:00")
    if m is None or len(m) < 40:
        print(f"[15m] {nm}: 数据不足 ({0 if m is None else len(m)})")
        continue
    m = m.sort_values("trade_time").reset_index(drop=True)
    m = m[["trade_time", "open", "close", "high", "low", "vol", "amount"]].copy()
    m.columns = ["dt", "o", "c", "h", "l", "vol", "amt"]
    p = DATA / f"m15_{nm}.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dt", "symbol", "open", "close", "high", "low", "vol", "amount"])
        for _, r in m.iterrows():
            w.writerow([r["dt"], r["dt"], r["o"], r["c"], r["h"], r["l"], r["vol"], r["amt"]])
    pr = subprocess.run([CZ, "analyze", str(p), "--freq", "15分钟", "--json"], capture_output=True, text=True, timeout=240)
    try:
        ana = json.loads(pr.stdout)
    except Exception:
        ana = {}
    bl = ana.get("bi_list") or []
    bi = [{"edt": str(b.get("edt"))[:16], "dir": b.get("direction"), "high": b.get("high"),
           "low": b.get("low"), "power": b.get("power"), "length": b.get("length")} for b in bl]
    zss = []
    for i in range(len(bi) - 2):
        a, b, c = bi[i], bi[i + 1], bi[i + 2]
        lo = max(min(a["low"], a["high"]), min(b["low"], b["high"]), min(c["low"], c["high"]))
        hi = min(max(a["low"], a["high"]), max(b["low"], b["high"]), max(c["low"], c["high"]))
        if lo < hi:
            zss.append({"from": a["edt"], "to": c["edt"], "ZD": round(lo, 2), "ZG": round(hi, 2)})
    czv[nm] = {"n_bars": len(m), "bi": bi[-8:], "zs_all": zss[-4:], "zs_now": zss[-1] if zss else None,
               "last_bar": {"dt": str(m.iloc[-1]["dt"]), "c": round(float(m.iloc[-1]["c"]), 2)},
               "today_bars": int((m["dt"].astype(str).str.startswith("2026-11-11")).sum())}
    z = zss[-1] if zss else None
    print(f"[15m] {nm}: n={len(m)} 中枢 {z['ZD'] if z else '—'}–{z['ZG'] if z else '—'}", flush=True)

# ═════════ 5. 月线 / 周线中枢（日线聚合） ═════════
for nm, tsc in TARGETS.items():
    if nm not in czv:
        continue
    d = get(pro.daily, ts_code=tsc, start_date="20240101", end_date=DATE)
    if d is None or d.empty:
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    d["dt"] = pd.to_datetime(d["trade_date"])
    for tag, rule in (("month", "ME"), ("week", "W-FRI")):
        g = d.set_index("dt").resample(rule).agg({"open": "first", "high": "max", "low": "min",
                                                  "close": "last", "vol": "sum", "amount": "sum"}).dropna()
        if len(g) < 30:
            continue
        p = DATA / f"_{tag}_{nm}.csv"
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["dt", "symbol", "open", "close", "high", "low", "vol", "amount"])
            for idx, r in g.iterrows():
                w.writerow([idx.strftime("%Y-%m-%d"), nm, r["open"], r["close"], r["high"], r["low"], r["vol"], r["amount"]])
        pr = subprocess.run([CZ, "analyze", str(p), "--freq", "月线" if tag == "month" else "周线",
                             "--json"], capture_output=True, text=True, timeout=240)
        try:
            ana = json.loads(pr.stdout)
        except Exception:
            ana = {}
        bl = ana.get("bi_list") or []
        bi = [{"edt": str(b.get("edt"))[:10], "dir": b.get("direction"), "high": b.get("high"),
               "low": b.get("low"), "power": b.get("power")} for b in bl]
        zss = []
        for i in range(len(bi) - 2):
            a, b, c = bi[i], bi[i + 1], bi[i + 2]
            lo = max(min(a["low"], a["high"]), min(b["low"], b["high"]), min(c["low"], c["high"]))
            hi = min(max(a["low"], a["high"]), max(b["low"], b["high"]), max(c["low"], c["high"]))
            if lo < hi:
                zss.append({"from": a["edt"], "to": c["edt"], "ZD": round(lo, 2), "ZG": round(hi, 2)})
        czv[nm][tag] = {"bi": bi[-6:], "zs_all": zss[-3:], "zs_now": zss[-1] if zss else None,
                        "n": len(g), "last_close": round(float(g["close"].iloc[-1]), 2)}
    time.sleep(0.3)
OUT["czsc"] = czv

# ═════════ 6. 个股行情与位置 ═════════
rows = []
for nm, tsc in TARGETS.items():
    if tsc in ("000001.SH", "399006.SZ", "000688.SH"):
        continue
    d = get(pro.daily, ts_code=tsc, start_date="20260601", end_date=DATE)
    if d is None or d.empty:
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    last = d.iloc[-1]
    hi60 = float(d["high"].tail(60).max()); lo60 = float(d["low"].tail(60).min())
    rows.append({"名称": nm, "代码": tsc, "收盘": round(float(last["close"]), 2),
                 "涨跌幅%": round(float(last["pct_chg"]), 2),
                 "最高": round(float(last["high"]), 2), "最低": round(float(last["low"]), 2),
                 "昨收": round(float(d["close"].iloc[-2]), 2),
                 "成交额亿": round(float(last["amount"]) / 1e5, 2),
                 "60日高": round(hi60, 2), "60日低": round(lo60, 2),
                 "距60日高%": round((float(last["close"]) / hi60 - 1) * 100, 1),
                 "60日涨幅%": round((float(last["close"]) / float(d["close"].iloc[-60]) - 1) * 100, 1),
                 "近5日涨幅%": round((float(last["close"]) / float(d["close"].iloc[-6]) - 1) * 100, 1),
                 "MA20": round(float(d["close"].rolling(20).mean().iloc[-1]), 2),
                 })
    time.sleep(0.35)
with open(DATA / "quotes_20261111.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
OUT["quotes"] = rows

(RPT / "data_20261111.json").write_text(json.dumps(OUT, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"market": market.get(DATE), "prev": market.get(PREV)}, ensure_ascii=False, indent=1))
