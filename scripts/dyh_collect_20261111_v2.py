"""都业华 2026-11-11 收评纪要 · 数据采集 v2（Tushare 口径，stk_mins 分钟限速下拆分两阶段）

阶段 A（快，不占 stk_mins 配额）：
  1) 指数（index_daily）
  2) 全市场宽度 / 涨停行业分布（pro.daily trade_date 单次全量）
  3) 板块篮子（直接用全 A 当日 pct_chg 表筛，不再逐股调 daily）
  4) 个股行情与位置（逐股 daily，一次拿 2024 起全部数据）
  5) 月线 / 周线中枢（复用第 4 步的日线聚合后喂 czsc）

阶段 B（慢，stk_mins 1 次/分钟）：15 分钟中枢
输出：reports/duyiehua-20261111/data_20261111.json
"""
import csv
import json
import os
import subprocess
import sys
import time
from collections import Counter
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
PHASE = sys.argv[1] if len(sys.argv) > 1 else "all"


def log(*a):
    print(*a, flush=True)


def get(fn, tries=5, **kw):
    for i in range(tries):
        try:
            d = fn(**kw)
            if d is not None and not d.empty:
                return d
            if d is not None:
                return d
        except Exception as e:
            log("  retry", getattr(fn, "__name__", "fn"), str(e)[:70])
        time.sleep(1.2 + i * 0.8)
    return None


# ═════════ 1. 指数 ═════════
idx_out = {}
for nm, tsc in [("上证指数", "000001.SH"), ("深证成指", "399001.SZ"), ("创业板指", "399006.SZ"),
                ("科创50", "000688.SH"), ("沪深300", "000300.SH")]:
    d = get(pro.index_daily, ts_code=tsc, start_date="20260101", end_date=DATE)
    if d is None or d.empty:
        log("[idx] FAIL", nm)
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    close, vol = d["close"], d["vol"]
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
                 for _, r in d.tail(10).iterrows()],
        "last20_low": round(float(d["low"].tail(20).min()), 2),
        "last20_high": round(float(d["high"].tail(20).max()), 2),
    }
    log(f"[idx] {nm} {idx_out[nm]['close']} {idx_out[nm]['pct']:+.2f}%")
    time.sleep(0.4)
OUT["index"] = idx_out

# ═════════ 2. 全市场宽度 + 涨停行业 ═════════
market = {}
day_tbl = {}
for d_ in (PREV, DATE):
    df = get(pro.daily, trade_date=d_)
    if df is None or df.empty:
        log("[mkt] FAIL", d_)
        continue
    day_tbl[d_] = df
    p = df["pct_chg"].dropna()
    market[d_] = {"n": len(df), "amount_yi": round(float(df["amount"].sum()) / 1e5, 1),
                  "up": int((p > 0).sum()), "down": int((p < 0).sum()), "flat": int((p == 0).sum()),
                  "median_pct": round(float(p.median()), 3),
                  "zt_ge98": int((p >= 9.8).sum()), "dt_le98": int((p <= -9.8).sum())}
    log(f"[mkt] {d_} 额={market[d_]['amount_yi']}亿 涨{market[d_]['up']}/跌{market[d_]['down']} zt{market[d_]['zt_ge98']}")
    time.sleep(0.4)

sb = get(pro.stock_basic, exchange="", list_status="L", fields="ts_code,symbol,name,industry")
nm_map = dict(zip(sb["ts_code"], sb["name"]))
ind_map = dict(zip(sb["ts_code"], sb["industry"]))
df = day_tbl.get(DATE)
if df is not None:
    df = df.copy()
    df["name"] = df["ts_code"].map(nm_map)
    df["industry"] = df["ts_code"].map(ind_map)
    zt = df[df["pct_chg"] >= 9.8].sort_values("pct_chg", ascending=False)
    market["zt_by_industry"] = dict(Counter(zt["industry"].fillna("其他")).most_common(25))
    market["zt_list"] = [{"code": r.ts_code, "name": r["name"], "pct": round(float(r.pct_chg), 2),
                          "industry": r["industry"]} for _, r in zt.iterrows()]
    kw = {"人形机器人": ["机器人", "机器", "减速", "丝杠", "伺服", "灵巧", "传感", "执行器"],
          "数据采集/视觉": ["数据", "视觉", "图像", "检测", "传感", "光学"],
          "AI/传媒": ["传媒", "文化", "影视", "数媒", "视频", "游戏", "出版", "广告"],
          "端侧/消费电子": ["电子", "光学", "精密", "科技", "智能"]}
    market["zt_kw"] = {}
    for k, words in kw.items():
        sub = zt[zt["name"].astype(str).str.contains("|".join(words), na=False)]
        market["zt_kw"][k] = {"n": len(sub), "names": [f"{r['name']}({r['industry']})" for _, r in sub.head(12).iterrows()]}
    log("[zt]", json.dumps({k: v["n"] for k, v in market["zt_kw"].items()}, ensure_ascii=False))
    log("[zt_ind] top:", json.dumps(list(market["zt_by_industry"].items())[:8], ensure_ascii=False))
OUT["market"] = market

# ═════════ 3. 板块篮子（用全 A 当日表筛，不再逐股调用） ═════════
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
if df is not None:
    pmap = dict(zip(df["ts_code"], df["pct_chg"]))
    for bname, codes in BASKET.items():
        pcts = [float(pmap[c]) for c in codes if c in pmap]
        if not pcts:
            continue
        ps = sorted(pcts)
        basket[bname] = {"n": len(pcts), "avg_pct": round(sum(pcts) / len(pcts), 2),
                         "median_pct": round(ps[len(ps) // 2], 2),
                         "up": sum(1 for x in pcts if x > 0), "zt": sum(1 for x in pcts if x >= 9.8),
                         "pcts": [round(x, 2) for x in pcts]}
    OUT["basket"] = dict(sorted(basket.items(), key=lambda x: -x[1]["avg_pct"]))
    log("[basket]", json.dumps({k: {kk: v[kk] for kk in ("n", "avg_pct", "median_pct", "up", "zt")}
                                for k, v in OUT["basket"].items()}, ensure_ascii=False))

# ═════════ 4. 个股行情与位置 + 5. 月线/周线中枢 ═════════
TARGETS = {
    "上证指数": "000001.SH", "创业板指": "399006.SZ", "科创50": "000688.SH",
    "药明康德": "603259.SH", "中国船舶": "600150.SH", "瑞芯微": "603893.SH",
    "伊利股份": "600887.SH", "中文在线": "300364.SZ", "海天瑞声": "688787.SH",
    "奥普特": "688686.SH", "柯力传感": "603662.SH", "兆易创新": "603986.SH",
    "云铝股份": "000807.SZ", "凯莱英": "002821.SZ", "昭衍新药": "603127.SH",
}
QUOTE_NAMES = ["药明康德", "中国船舶", "瑞芯微", "伊利股份", "中文在线", "海天瑞声",
               "奥普特", "柯力传感", "兆易创新", "云铝股份", "凯莱英", "昭衍新药"]
czv = {}
rows = []
daily_cache = {}
for nm, tsc in TARGETS.items():
    if tsc.startswith(("000001.SH", "399006.SZ", "000688.SH")):
        continue
    d = get(pro.daily, ts_code=tsc, start_date="20240101", end_date=DATE)
    if d is None or d.empty:
        log("[daily] FAIL", nm)
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    daily_cache[nm] = d
    time.sleep(0.35)

for nm, d in daily_cache.items():
    last = d.iloc[-1]
    hi60 = float(d["high"].tail(60).max()); lo60 = float(d["low"].tail(60).min())
    d60 = d.tail(60)
    rows.append({"名称": nm, "代码": TARGETS[nm], "收盘": round(float(last["close"]), 2),
                 "涨跌幅%": round(float(last["pct_chg"]), 2),
                 "最高": round(float(last["high"]), 2), "最低": round(float(last["low"]), 2),
                 "昨收": round(float(d["close"].iloc[-2]), 2),
                 "成交额亿": round(float(last["amount"]) / 1e5, 2),
                 "60日高": round(hi60, 2), "60日低": round(lo60, 2),
                 "60日高日期": str(d60.loc[d60["high"].idxmax(), "trade_date"]),
                 "60日低日期": str(d60.loc[d60["low"].idxmin(), "trade_date"]),
                 "距60日高%": round((float(last["close"]) / hi60 - 1) * 100, 1),
                 "60日涨幅%": round((float(last["close"]) / float(d["close"].iloc[-60]) - 1) * 100, 1),
                 "近5日涨幅%": round((float(last["close"]) / float(d["close"].iloc[-6]) - 1) * 100, 1),
                 "MA20": round(float(d["close"].rolling(20).mean().iloc[-1]), 2),
                 })
    # 月线 / 周线中枢
    d2 = d.copy()
    d2["dt"] = pd.to_datetime(d2["trade_date"])
    for tag, rule, freq in (("month", "ME", "月线"), ("week", "W-FRI", "周线")):
        g = d2.set_index("dt").resample(rule).agg({"open": "first", "high": "max", "low": "min",
                                                    "close": "last", "vol": "sum", "amount": "sum"}).dropna()
        if len(g) < 25:
            continue
        p = DATA / f"_{tag}_{nm}.csv"
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["dt", "symbol", "open", "close", "high", "low", "vol", "amount"])
            for idx, r in g.iterrows():
                w.writerow([idx.strftime("%Y-%m-%d"), nm, r["open"], r["close"], r["high"], r["low"], r["vol"], r["amount"]])
        pr = subprocess.run([CZ, "analyze", str(p), "--freq", freq, "--json"], capture_output=True, text=True, timeout=240)
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
        czv.setdefault(nm, {})[tag] = {"bi": bi[-6:], "zs_all": zss[-3:],
                                       "zs_now": zss[-1] if zss else None, "n": len(g),
                                       "last_close": round(float(g["close"].iloc[-1]), 2)}
    log(f"[daily] {nm} 收{last['close']} {last['pct_chg']:+.2f}% 60高{hi60}")
    time.sleep(0.3)

with open(DATA / "quotes_20261111.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
OUT["quotes"] = rows
OUT["czsc"] = czv

# ═════════ 6. 15 分钟中枢（新浪 15 分钟 K，替代 stk_mins 的 1 次/小时限额） ═════════
SINA_SYM = {"000001.SH": "sh000001", "399006.SZ": "sz399006", "000688.SH": "sh000688",
            "603259.SH": "sh603259", "600150.SH": "sh600150", "603893.SH": "sh603893",
            "600887.SH": "sh600887", "300364.SZ": "sz300364", "688787.SH": "sh688787",
            "688686.SH": "sh688686", "603662.SH": "sh603662", "603986.SH": "sh603986",
            "000807.SZ": "sz000807", "002821.SZ": "sz002821", "603127.SH": "sh603127"}


def sina_m15(sym, tries=4):
    import urllib.request
    url = ("https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
           f"?symbol={sym}&scale=15&ma=no&datalen=400")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8")
            m = json.loads(raw)
            if m and len(m) >= 100:
                return m
        except Exception as e:
            log("  retry sina", sym, str(e)[:70])
            time.sleep(1.5 + i)
    return None


if PHASE in ("all", "m15"):
    M15 = ["上证指数", "创业板指", "药明康德", "中国船舶", "瑞芯微", "伊利股份",
           "中文在线", "海天瑞声", "奥普特", "柯力传感", "兆易创新", "云铝股份"]
    for nm in M15:
        tsc = TARGETS[nm]
        ok = False
        for attempt in range(3):
            m = sina_m15(SINA_SYM[tsc])
            if m is None:
                log(f"[15m] {nm} 尝试{attempt+1} 新浪数据失败")
                time.sleep(3)
                continue
            m = pd.DataFrame(m)
            m = m.rename(columns={"day": "dt", "open": "o", "close": "c", "high": "h",
                                  "low": "l", "volume": "vol", "amount": "amt"})
            m = m.sort_values("dt").reset_index(drop=True)
            p = DATA / f"m15_{nm}.csv"
            with open(p, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["dt", "symbol", "open", "close", "high", "low", "vol", "amount"])
                for _, r in m.iterrows():
                    w.writerow([r["dt"], r["dt"], r["o"], r["c"], r["h"], r["l"], r["vol"], r["amt"]])
            pr = subprocess.run([CZ, "analyze", str(p), "--freq", "15分钟", "--json"],
                                capture_output=True, text=True, timeout=300)
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
            czv.setdefault(nm, {})["m15"] = {
                "n_bars": len(m), "bi": bi[-8:], "zs_all": zss[-4:],
                "zs_now": zss[-1] if zss else None,
                "last_bar": {"dt": str(m.iloc[-1]["dt"]), "c": round(float(m.iloc[-1]["c"]), 2)},
                "today_bars": int((m["dt"].astype(str).str.startswith("2026-11-11")).sum()),
                "last5": [{"dt": str(r["dt"]), "c": round(float(r["c"]), 2), "h": round(float(r["h"]), 2),
                           "l": round(float(r["l"]), 2)} for _, r in m.tail(5).iterrows()]}
            z = zss[-1] if zss else None
            log(f"[15m] OK {nm} n={len(m)} 中枢 {z['ZD'] if z else '—'}–{z['ZG'] if z else '—'}")
            ok = True
            break
        if not ok:
            log(f"[15m] {nm} 最终失败")

OUT["czsc"] = czv
(RPT / "data_20261111.json").write_text(json.dumps(OUT, ensure_ascii=False, indent=1), encoding="utf-8")
log("WROTE", RPT / "data_20261111.json")
log(json.dumps({"market": market.get(DATE), "prev": market.get(PREV)}, ensure_ascii=False, indent=1))
