"""都业华 2026-11-12 午评纪要 · 数据采集（盘中版）

⛔ 遵守用户 2026-11-11 禁令：只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。

数据源：
  - 东财 push2 实时快照（f43 现价 / f44 高 / f45 低 / f46 开 / f47 量 / f48 额 / f60 昨收 / f169 涨跌 / f170 涨跌幅）
  - 东财 push2 ulist.np 批量报价
  - 东财 push2ex 涨停池（盘中）
  - Tushare Pro 日线（到前一交易日 20261111）+ 复权因子

输出：reports/duyiehua-20261112/data_20261112.json
"""
import json
import os
import time
import urllib.request
from pathlib import Path

import pandas as pd
import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261112"
RPT.mkdir(parents=True, exist_ok=True)
pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}
PREV_DATE = "20261111"
DATE = "20261112"
OUT = {}


def log(*a):
    print(*a, flush=True)


def em_get(url, tries=4, headers=None):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or UA)
            raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")
            j = json.loads(raw)
            if j.get("rc") == 0:
                return j
        except Exception as e:
            log("  retry em", str(e)[:70])
            time.sleep(1.5 + i)
    return None


def sina_quotes(symbols, tries=3):
    """新浪实时批量：返回 {symbol: {name,open,prev,price,high,low,vol(股),amount(元),date,time}}"""
    out = {}
    hdr = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
    for i in range(0, len(symbols), 40):
        chunk = symbols[i:i + 40]
        url = "https://hq.sinajs.cn/list=" + ",".join(chunk)
        data = None
        for t in range(tries):
            try:
                req = urllib.request.Request(url, headers=hdr)
                raw = urllib.request.urlopen(req, timeout=20).read()
                data = raw.decode("gbk", "ignore")
                break
            except Exception as e:
                log("  retry sina", str(e)[:60])
                time.sleep(1.2 + t)
        if not data:
            continue
        for line in data.split("\n"):
            if "hq_str_" not in line:
                continue
            sym = line.split("hq_str_")[1].split("=")[0].strip()
            body = line.split('"')[1] if '"' in line else ""
            f = body.split(",")
            if len(f) < 10 or not f[0]:
                continue
            try:
                out[sym] = {"name": f[0], "open": float(f[1]), "prev": float(f[2]),
                            "price": float(f[3]), "high": float(f[4]), "low": float(f[5]),
                            "vol": float(f[8]), "amount": float(f[9]),
                            "date": f[30] if len(f) > 30 else "", "time": f[31] if len(f) > 31 else ""}
            except Exception:
                continue
        time.sleep(0.35)
    return out


# ───────────── 标的清单 ─────────────
IDX = {
    "上证指数": "1.000001", "深证成指": "0.399001", "创业板指": "0.399006",
    "科创50": "1.000688", "沪深300": "1.000300", "深证综指": "0.399106",
}
MID = {   # 中线 8 只
    "药明康德": "1.603259", "中国船舶": "1.600150", "瑞芯微": "1.603893", "伊利股份": "1.600887",
    "中文在线": "0.300364", "海天瑞声": "1.688787", "奥普特": "1.688686", "柯力传感": "1.603662",
}
SHORT = {  # 短线 5 只
    "兆易创新": "1.603986", "云铝股份": "0.000807", "模塑科技": "0.000700",
    "汉威科技": "0.300007", "长盈精密": "0.300115",
}
REF = {"凯莱英": "0.002821", "乐鑫科技": "1.688018"}
ALL = {**MID, **SHORT, **REF}

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
    "CPO/光模块": ["300308.SZ", "300502.SZ", "300394.SZ", "300548.SZ", "300570.SZ", "300620.SZ",
               "688313.SH", "688498.SH", "002281.SZ", "601869.SH", "603083.SH", "300936.SZ"],
    "电子化学品": ["300537.SZ", "002741.SZ", "603078.SH", "300398.SZ", "688126.SH", "002648.SZ",
                "300429.SZ", "603688.SH", "688199.SH", "300285.SZ"],
    "防守/消费": ["000858.SZ", "000596.SZ", "603369.SH", "600809.SH", "000568.SZ", "002304.SZ",
               "603198.SH", "002507.SZ", "600519.SH", "000895.SZ"],
}
SEMI = ["603986.SH", "603501.SH", "002371.SZ", "688981.SH", "300782.SZ", "688008.SH",
        "688012.SH", "603160.SH"]


def secid(ts_code):
    c, ex = ts_code.split(".")
    return ("1." if ex == "SH" else "0.") + c


# ───────────── 1. 实时快照：指数 ─────────────
idx_out = {}
idx_sym = {"上证指数": "sh000001", "深证成指": "sz399001", "创业板指": "sz399006",
           "科创50": "sh000688", "沪深300": "sh000300", "深证综指": "sz399106"}
qs_all = sina_quotes(list(idx_sym.values()))
log("[quote] 新浪取得", len(qs_all), "只")

for nm, sym in idx_sym.items():
    s = qs_all.get(sym)
    if not s:
        log("[idx] FAIL", nm)
        continue
    idx_out[nm] = {"code": sym, "name": s["name"], "price": s["price"], "high": s["high"],
                    "low": s["low"], "open": s["open"], "prev": s["prev"],
                    "vol": int(s["vol"]), "amount_yi": round(s["amount"] / 1e8, 1),
                    "chg": round(s["price"] - s["prev"], 2),
                    "pct": round((s["price"] / s["prev"] - 1) * 100, 2),
                    "quote_time": s["time"]}
    log(f"[idx] {nm} {s['price']} {idx_out[nm]['pct']:+.2f}% 高{s['high']} 低{s['low']} 额{idx_out[nm]['amount_yi']}亿")
OUT["index"] = idx_out

# ───────────── 2. 实时快照：个股 + 篮子（新浪批量） ─────────────
def sym_of(ts_code):
    c, ex = ts_code.split(".")
    return ("sh" if ex == "SH" else "sz") + c


need_syms = []
for nm, sid in ALL.items():
    code = sid.split(".")[1]
    need_syms.append(("sh" if sid.startswith("1.") else "sz") + code)
for codes in BASKET.values():
    for c in codes:
        need_syms.append(sym_of(c))
need_syms = list(dict.fromkeys([x for x in need_syms if x]))
qs_all2 = sina_quotes(need_syms)
log("[quote] 新浪第二批", len(qs_all2), "只")

q = {}
for sym, s in qs_all2.items():
    rec = {"name": s["name"], "price": s["price"], "prev": s["prev"], "open": s["open"],
           "high": s["high"], "low": s["low"], "vol": int(s["vol"]),
           "amount_yi": round(s["amount"] / 1e8, 2),
           "pct": round((s["price"] / s["prev"] - 1) * 100, 2),
           "quote_time": s["time"]}
    q[sym] = rec
    q[sym[2:]] = rec          # 同时用裸代码索引，便于篮子/列表查找

# ───────────── 3. 日线 + 位置 ─────────────
rows = []
hist = {}
for nm, sid in ALL.items():
    tsc = secid(sid).replace("1.", "1.", 1)
    code = sid.split(".")[1]
    tsc = code + ("." + ("SH" if sid.startswith("1.") else "SZ"))
    d = pro.daily(ts_code=tsc, start_date="20250901", end_date=PREV_DATE)
    if d is None or d.empty:
        log("[daily] FAIL", nm)
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    hist[nm] = d
    last = d.iloc[-1]
    hi60 = float(d["high"].tail(60).max()); lo60 = float(d["low"].tail(60).min())
    snap = q.get(code, {})
    r = {"名称": nm, "代码": tsc, "现价": snap.get("price"), "涨跌幅%": snap.get("pct"),
         "最高": snap.get("high"), "最低": snap.get("low"), "开盘": snap.get("open"),
         "昨收": last["close"], "成交额亿": snap.get("amount_yi"),
         "今日量(手)": int((snap.get("vol") or 0) / 100), "昨日量(手)": int(last["vol"]),
         "60日高": round(hi60, 2), "60日低": round(lo60, 2),
         "60日高日期": str(d.tail(60).loc[d.tail(60)["high"].idxmax(), "trade_date"]),
         "距60日高%": round((snap.get("price") or last["close"]) / hi60 * 100 - 100, 1),
         "昨日量比(今累计/昨全天)": round((snap.get("vol") or 0) / 100 / float(last["vol"]) * 100, 1),
         "MA20": round(float(d["close"].rolling(20).mean().iloc[-1]), 2),
         "昨日涨跌幅%": round(float(last["pct_chg"]), 2)}
    rows.append(r)
    time.sleep(0.3)
OUT["quotes"] = rows

# ───────────── 4. 板块篮子（实时） ─────────────
basket = {}
for bname, codes in BASKET.items():
    pcts, zt, ok = [], 0, 0
    detail = []
    for c in codes:
        code = c.split(".")[0]
        s = q.get(code)
        if not s:
            continue
        ok += 1
        pcts.append(s["pct"])
        if s["pct"] >= 9.8:
            zt += 1
        detail.append({"名称": s["name"], "代码": c, "涨跌幅%": round(s["pct"], 2), "额亿": s["amount_yi"]})
    if not pcts:
        continue
    ps = sorted(pcts)
    basket[bname] = {"n": ok, "avg_pct": round(sum(pcts) / len(pcts), 2),
                     "median_pct": round(ps[len(ps) // 2], 2),
                     "up": sum(1 for x in pcts if x > 0), "zt": zt,
                     "detail": sorted(detail, key=lambda x: -x["涨跌幅%"])}
OUT["basket"] = dict(sorted(basket.items(), key=lambda x: -x[1]["avg_pct"]))
log("[basket]", json.dumps({k: {kk: v[kk] for kk in ("n", "avg_pct", "up", "zt")} for k, v in OUT["basket"].items()},
                            ensure_ascii=False))

# ───────────── 5. 半导体量能核验（老师核心警示） ─────────────
semi_rows = []
for c in SEMI:
    code = c.split(".")[0]
    s = q.get(code)
    if not s:
        continue
    tsc = c
    semi_rows.append({"名称": s["name"], "代码": c, "涨跌幅%": round(s["pct"], 2),
                      "今日量(手)": s["vol"], "额亿": s["amount_yi"]})
OUT["semi_quote"] = sorted(semi_rows, key=lambda x: -x["涨跌幅%"])
log("[semi]", json.dumps(OUT["semi_quote"], ensure_ascii=False))

# ───────────── 6. 涨停池（盘中） ─────────────
zt = em_get("https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989"
             "&dpt=wz.ztzt&pageindex=0&pagesize=300&sort=fbt:asc&date=%s" % DATE,
             headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"})
if zt and zt.get("data"):
    pool = zt["data"].get("pool") or []
    from collections import Counter
    ind = Counter(p.get("hybk", "其他") for p in pool)
    OUT["zt_pool"] = {"n": zt["data"].get("tc"), "by_industry": dict(ind.most_common(25)),
                      "list": [{"代码": p.get("c"), "名称": p.get("n"), "涨跌幅%": round(p.get("zdp", 0), 2),
                                "行业": p.get("hybk"), "连板": p.get("lbc")} for p in pool]}
    log("[zt] 盘中涨停", OUT["zt_pool"]["n"], "| 行业 top", list(OUT["zt_pool"]["by_industry"].items())[:8])

# ───────────── 7. 昨日（11/11）全市场基准 ─────────────
df = pro.daily(trade_date=PREV_DATE)
p = df["pct_chg"].dropna()
OUT["prev_market"] = {"n": len(df), "amount_yi": round(float(df["amount"].sum()) / 1e5, 1),
                      "up": int((p > 0).sum()), "down": int((p < 0).sum()),
                      "zt_ge98": int((p >= 9.8).sum()), "dt_le98": int((p <= -9.8).sum())}
# 两市成交额口径（上证综指 + 深证综指）
for c, k in (("000001.SH", "sh"), ("399106.SZ", "sz")):
    d = pro.index_daily(ts_code=c, start_date=PREV_DATE, end_date=PREV_DATE)
    if d is not None and not d.empty:
        OUT["prev_market"][k + "_amount_yi"] = round(float(d.iloc[-1]["amount"]) / 1e5, 1)
log("[prev_market]", json.dumps(OUT["prev_market"], ensure_ascii=False))

# ───────────── 8. 指数日线（均量线、20 日线） ─────────────
ix_daily = {}
for nm, sid in IDX.items():
    tsc = {"1.000001": "000001.SH", "0.399001": "399001.SZ", "0.399006": "399006.SZ",
           "1.000688": "000688.SH", "1.000300": "000300.SH", "0.399106": "399106.SZ"}[sid]
    d = pro.index_daily(ts_code=tsc, start_date="20260101", end_date=PREV_DATE)
    if d is None or d.empty:
        continue
    d = d.sort_values("trade_date").reset_index(drop=True)
    v = d["vol"]
    ix_daily[nm] = {"ma20": round(float(d["close"].rolling(20).mean().iloc[-1]), 2),
                    "vol_ma5": round(float(v.rolling(5).mean().iloc[-1]), 0),
                    "vol_ma20": round(float(v.rolling(20).mean().iloc[-1]), 0),
                    "vol_bear_ma": bool(v.rolling(5).mean().iloc[-1] < v.rolling(20).mean().iloc[-1]),
                    "last_close": float(d["close"].iloc[-1]),
                    "last_high": float(d["high"].iloc[-1]), "last_low": float(d["low"].iloc[-1]),
                    "tail": [{"d": str(r.trade_date), "c": round(float(r.close), 2), "v": round(float(r.vol), 0)}
                             for _, r in d.tail(6).iterrows()]}
    time.sleep(0.3)
OUT["index_daily"] = ix_daily

OUT["snapshot_time"] = time.strftime("%Y-%m-%d %H:%M")
(RPT / "data_20261112.json").write_text(json.dumps(OUT, ensure_ascii=False, indent=1), encoding="utf-8")
log("WROTE", RPT / "data_20261112.json")
