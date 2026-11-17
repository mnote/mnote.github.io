"""wu2198 报告 · Tushare 日线采集 — 2026-11-17（收盘后增补版）

用途：给 11/17 报告补 4 条晚间新帖（09:54 / 10:28 / 21:46 / 22:02），
     并用 Tushare 日线重算指数 + 3 只个股的关键位（MA/60日高低/MACD），
     同时核验博主 10:28「CPO 龙头 1416.88 → 385，跌 72.82%」。

口径：日线级别（pro.daily / pro.index_daily），个股前复权（adj_factor）。
      禁止任何分钟级数据。
输出：charts/_ts_20261117.json
"""
import json
import os
from pathlib import Path

import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN") or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"
pro = ts.pro_api(TOKEN)

CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
TD = "20261117"
DAYS = 120

# 报告选定的 3 只个股 + 指数 + CPO 核验池
STOCKS = {
    "002179.SZ": "中航光电",
    "600519.SH": "贵州茅台",
    "688256.SH": "寒武纪",
    "600036.SH": "招商银行",
}
INDEXES = {
    "000001.SH": "上证指数",
    "399006.SZ": "创业板指",
}
# 10:28 「CPO 龙头 1416.88 → 385，-72.82%」核验候选
CPO_POOL = ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH", "002281.SZ", "603236.SH"]


def norm(rows, key="trade_date"):
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    return sorted(rows, key=lambda r: r[key])


def fwd_adj(daily, adj):
    """前复权：close * adj_factor(最新日) / adj_factor(当日)

    ⚠️ adj 已按 trade_date 升序，最新日在末尾 → 用 adj[-1] 作基准。
    """
    if not adj:
        return list(daily)
    today = adj[-1]["adj_factor"]
    f = {r["trade_date"]: r["adj_factor"] for r in adj}
    out = []
    for d in daily:
        r = f.get(d["trade_date"])
        if not r:
            continue
        k = today / r
        out.append({
            "trade_date": d["trade_date"],
            "open": round(d["open"] * k, 2),
            "high": round(d["high"] * k, 2),
            "low": round(d["low"] * k, 2),
            "close": round(d["close"] * k, 2),
            "vol": d["vol"],
            "amount": d["amount"],
        })
    return out


def fetch_stock(ts_code):
    daily = norm(pro.daily(ts_code=ts_code, start_date="20250801", end_date=TD))
    adj = norm(pro.adj_factor(ts_code=ts_code, start_date="20250801", end_date=TD))
    return fwd_adj(daily, adj)


def fetch_index(ts_code):
    try:
        rows = norm(pro.index_daily(ts_code=ts_code, start_date="20250801", end_date=TD))
        src = "index_daily"
    except Exception:
        rows = norm(pro.daily(ts_code=ts_code, start_date="20250801", end_date=TD))
        src = "daily"
    out = []
    for r in rows:
        out.append({
            "trade_date": r["trade_date"],
            "open": r["open"], "high": r["high"], "low": r["low"],
            "close": r["close"], "vol": r.get("vol"), "amount": r.get("amount"),
        })
    return out, src


def summarize(rows):
    """末根 + MA + 60 日高低 + 量能比 + 关键位差"""
    import statistics
    last = rows[-1]
    prev = rows[-2]
    closes = [r["close"] for r in rows]
    vols = [r["vol"] for r in rows if r.get("vol")]
    win = rows[-60:]
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    ma20 = sum(closes[-20:]) / 20
    hi60 = max(r["high"] for r in win)
    lo60 = min(r["low"] for r in win)
    v5 = sum(vols[-5:]) / 5 if len(vols) >= 5 else None
    return {
        "date": last["trade_date"],
        "open": last["open"], "high": last["high"], "low": last["low"],
        "close": last["close"], "vol": last.get("vol"), "amount": last.get("amount"),
        "prev_close": prev["close"],
        "pct_chg": round((last["close"] / prev["close"] - 1) * 100, 2),
        "ma5": round(ma5, 2), "ma10": round(ma10, 2), "ma20": round(ma20, 2),
        "hi60": round(hi60, 2), "lo60": round(lo60, 2),
        # 量比口径与历史报告一致：当日量 / 含当日的 5 日均量
        "vol_ratio5": round(last["vol"] / v5 * 100, 1) if v5 else None,
        # Tushare amount 单位 = 千元 → 亿元 = amount / 1e5
        "amount_yi": round(last["amount"] / 1e5, 2) if last.get("amount") else None,
        "dist_hi60": round((last["close"] / hi60 - 1) * 100, 2),
        "dist_lo60": round((last["close"] / lo60 - 1) * 100, 2),
        "bars": len(rows),
    }


def macd(closes, fast=12, slow=26, signal=9):
    import pandas as pd
    s = pd.Series(closes)
    dif = s.ewm(span=fast, adjust=False).mean() - s.ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif.iloc[-1], dea.iloc[-1], (dif.iloc[-1] - dea.iloc[-1]) * 2


def main():
    out = {"trade_date": TD, "stocks": {}, "indexes": {}, "cpo_check": {}, "rows": {}}

    for code, name in INDEXES.items():
        rows, src = fetch_index(code)
        out["rows"][code] = rows[-DAYS:]
        s = summarize(rows)
        d, e, b = macd([r["close"] for r in rows])
        s.update({"name": name, "src": src, "dif": round(d, 3), "dea": round(e, 3), "macd_bar": round(b, 3)})
        out["indexes"][code] = s
        print(f"[idx] {code} {name} {s['close']} {s['pct_chg']:+}% src={src} bars={len(rows)}")
        # 门槛差距
        for thr, lbl in ((3706.00, "3706"), (2626.00, "2626")):
            s[f"gap_{lbl}"] = round(s["close"] - thr, 2)
            s[f"gap_{lbl}_pct"] = round((s["close"] / thr - 1) * 100, 2)

    for code, name in STOCKS.items():
        rows = fetch_stock(code)
        out["rows"][code] = rows[-DAYS:]
        s = summarize(rows)
        d, e, b = macd([r["close"] for r in rows])
        s.update({"name": name, "dif": round(d, 3), "dea": round(e, 3), "macd_bar": round(b, 3)})
        out["stocks"][code] = s
        print(f"[stk] {code} {name} {s['close']} {s['pct_chg']:+}% MA20={s['ma20']} hi60={s['hi60']} lo60={s['lo60']}")

    # 10:28 「CPO 龙头这波从 1416.88 到今天的 385 元，跌了 1031.88 元，幅度达 72.82%」
    for code in CPO_POOL:
        try:
            rows = fetch_stock(code)
        except Exception as e:
            print(f"  [cpo] {code} 失败 {e}")
            continue
        if len(rows) < 30:
            continue
        last = rows[-1]
        peak = max(rows, key=lambda r: r["high"])
        s = summarize(rows)
        out["rows"][code] = rows[-DAYS:]
        drop = round((peak["high"] - last["close"]) / peak["high"] * 100, 2)
        out["cpo_check"][code] = {
            "date": last["trade_date"], "close": last["close"],
            "high": last["high"], "low": last["low"], "pct_chg": s["pct_chg"],
            "peak_date": peak["trade_date"], "peak_high": peak["high"],
            "peak_close": peak["close"],
            "drop_from_peak_high_pct": drop,
            "drop_from_peak_close_pct": round((peak["close"] - last["close"]) / peak["close"] * 100, 2),
            "ma20": s["ma20"], "hi60": s["hi60"], "lo60": s["lo60"], "amount_yi": s["amount_yi"],
        }
        print(f"[cpo] {code} close={last['close']} peak {peak['trade_date']} high={peak['high']} "
              f"close={peak['close']} → -peakClose {out['cpo_check'][code]['drop_from_peak_close_pct']}% "
              f"-peakHigh {drop}%")

    # 反推 1416.88 / 385 的组合
    print("\n[反推] 目标：peak_close=1416.88, today=385, drop=72.82%")
    for code, v in out["cpo_check"].items():
        if abs(v["close"] - 385) < 1.0:
            print(f"  ★ {code} 今日收盘 {v['close']} 匹配 385；"
                  f"峰值收盘 {v['peak_close']} (peak {v['peak_date']}) "
                  f"峰→今 {v['drop_from_peak_close_pct']}% / 峰高→今 {v['drop_from_peak_high_pct']}%")

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    (CHART_DIR / "_ts_20261117.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {CHART_DIR/'_ts_20261117.json'}")


if __name__ == "__main__":
    main()
