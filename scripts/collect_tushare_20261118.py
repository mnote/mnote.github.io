"""wu2198 报告 · Tushare 日线采集 — 2026-11-18

口径：日线级别（pro.daily / pro.index_daily / pro.sw_daily），个股前复权（adj_factor）。
      禁止任何分钟级数据。禁止 czsc。
输出：charts/_ts_20261118.json
"""
import json
import os
from pathlib import Path

import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN") or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"
pro = ts.pro_api(TOKEN)

CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
TD = "20261118"
PREV = "20261117"
DAYS = 120

STOCKS = {
    "600519.SH": "贵州茅台",
    "688256.SH": "寒武纪",
    "002179.SZ": "中航光电",
    "300308.SZ": "新易盛",
    "603019.SH": "中科曙光",
    "000938.SZ": "紫光股份",
    "002463.SZ": "沪电股份",
    "000063.SZ": "中兴通讯",
    "600036.SH": "招商银行",
    "601869.SH": "长飞光纤",
    "688041.SH": "海光信息",
    "300308.SZ": "新易盛",
}
INDEXES = {
    "000001.SH": "上证指数",
    "399006.SZ": "创业板指",
    "000300.SH": "沪深300",
    "399001.SZ": "深证成指",
}


def norm(rows, key="trade_date"):
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    return sorted(rows, key=lambda r: r[key])


def fwd_adj(daily, adj):
    """前复权：close * adj_factor(最新日) / adj_factor(当日)。adj 升序 → 最新日在末尾。"""
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
            "vol": d["vol"], "amount": d["amount"],
            "pct_chg": d.get("pct_chg"),
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
            "trade_date": r["trade_date"], "open": r["open"], "high": r["high"],
            "low": r["low"], "close": r["close"], "vol": r.get("vol"),
            "amount": r.get("amount"), "pct_chg": r.get("pct_chg"),
        })
    return out, src


def summarize(rows):
    last, prev = rows[-1], rows[-2]
    closes = [r["close"] for r in rows]
    vols = [r["vol"] for r in rows if r.get("vol")]
    win = rows[-60:]
    v5 = sum(vols[-5:]) / 5 if len(vols) >= 5 else None
    hi60 = max(r["high"] for r in win)
    lo60 = min(r["low"] for r in win)
    return {
        "date": last["trade_date"], "open": last["open"], "high": last["high"],
        "low": last["low"], "close": last["close"], "vol": last.get("vol"),
        "amount": last.get("amount"), "prev_close": prev["close"],
        "pct_chg": round((last["close"] / prev["close"] - 1) * 100, 2),
        "ma5": round(sum(closes[-5:]) / 5, 2),
        "ma10": round(sum(closes[-10:]) / 10, 2),
        "ma20": round(sum(closes[-20:]) / 20, 2),
        "hi60": round(hi60, 2), "lo60": round(lo60, 2),
        "vol_ratio5": round(last["vol"] / v5 * 100, 1) if v5 else None,
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
    out = {"trade_date": TD, "stocks": {}, "indexes": {}, "rows": {}, "pools": {}, "breadth": {}}

    # ---- 全市场单次全量 daily（算涨跌家数 / 涨停 / 成交额） ----
    all_day = pro.daily(trade_date=TD).to_dict("records")
    all_prev = pro.daily(trade_date=PREV).to_dict("records")
    print(f"[all] {TD} {len(all_day)} 只 / {PREV} {len(all_prev)} 只")

    # daily 不含名称 → 补 stock_basic
    try:
        nm = {r["ts_code"]: r["name"] for r in pro.stock_basic(
            exchange="", list_status="L", fields="ts_code,name").to_dict("records")}
    except Exception as e:
        nm = {}
        print("[name] stock_basic 失败:", e)
    for r in all_day:
        r["name"] = nm.get(r["ts_code"], "")
    amt_today = sum((r.get("amount") or 0) for r in all_day) / 1e5
    amt_prev = sum((r.get("amount") or 0) for r in all_prev) / 1e5
    up = sum(1 for r in all_day if (r.get("pct_chg") or 0) > 0)
    down = sum(1 for r in all_day if (r.get("pct_chg") or 0) < 0)
    flat = len(all_day) - up - down
    out["breadth"] = {
        "amount_yi": round(amt_today, 0), "amount_prev_yi": round(amt_prev, 0),
        "amount_delta_yi": round(amt_today - amt_prev, 0),
        "amount_delta_pct": round((amt_today / amt_prev - 1) * 100, 2),
        "up": up, "down": down, "flat": flat, "total": len(all_day),
    }
    print(f"[breadth] 额 {amt_today:.0f}亿 (前 {amt_prev:.0f}) 涨{up} 跌{down} 平{flat}")

    # ---- 涨停/跌停（按板块涨跌停规则） ----
    def limit_price(code, pre_close):
        if code.startswith("30") or code.startswith("688"):
            return round(pre_close * 1.2, 2)
        if code.startswith("8") or code.startswith("4") or code.startswith("92"):
            return round(pre_close * 1.3, 2)
        return round(pre_close * 1.1, 2)

    prev_map = {r["ts_code"]: r for r in all_prev}
    zt, dt, ztb = [], [], []
    for r in all_day:
        code = r["ts_code"].split(".")[0]
        name = r.get("name", "")
        pc = prev_map.get(r["ts_code"], {}).get("close")
        if pc is None:
            continue
        pct = r.get("pct_chg") or 0
        if "ST" in name:
            continue
        lp = limit_price(code, pc)
        if r["high"] and abs(r["high"] - lp) < 0.011 and r["close"] >= lp - 0.011:
            zt.append({"code": r["ts_code"], "name": name, "pct": round(pct, 2)})
            if r["high"] > lp + 0.011:
                ztb.append({"code": r["ts_code"], "name": name})
        if r["low"] and abs(r["low"] - round(pc * 0.9, 2)) < 0.011 and r["close"] <= round(pc * 0.9, 2) + 0.011:
            dt.append({"code": r["ts_code"], "name": name, "pct": round(pct, 2)})
    out["breadth"]["zt"] = len(zt)
    out["breadth"]["dt"] = len(dt)
    out["breadth"]["zt_list"] = zt
    out["breadth"]["dt_list"] = dt
    print(f"[limit] 涨停 {len(zt)} 跌停 {len(dt)}")

    # ---- 指数 ----
    for code, name in INDEXES.items():
        rows, src = fetch_index(code)
        out["rows"][code] = rows[-DAYS:]
        s = summarize(rows)
        d, e, b = macd([r["close"] for r in rows])
        s.update({"name": name, "src": src, "dif": round(d, 3), "dea": round(e, 3),
                  "macd_bar": round(b, 3)})
        for thr, lbl in ((3706.00, "3706"), (2626.00, "2626"), (2263.00, "2263")):
            s[f"gap_{lbl}"] = round(s["close"] - thr, 2)
            s[f"gap_{lbl}_pct"] = round((s["close"] / thr - 1) * 100, 2)
        out["indexes"][code] = s
        print(f"[idx] {code} {name} {s['close']} {s['pct_chg']:+}% MA20={s['ma20']} "
              f"hi60={s['hi60']} lo60={s['lo60']}")

    # ---- 个股 ----
    for code, name in STOCKS.items():
        try:
            rows = fetch_stock(code)
        except Exception as e:
            print(f"  [stk] {code} 失败 {e}")
            continue
        if len(rows) < 30:
            continue
        out["rows"][code] = rows[-DAYS:]
        s = summarize(rows)
        d, e, b = macd([r["close"] for r in rows])
        s.update({"name": name, "dif": round(d, 3), "dea": round(e, 3), "macd_bar": round(b, 3)})
        out["stocks"][code] = s
        print(f"[stk] {code} {name} {s['close']} {s['pct_chg']:+}% MA20={s['ma20']} "
              f"hi60={s['hi60']} lo60={s['lo60']} 量比{s['vol_ratio5']}% 额{s['amount_yi']}亿")

    # ---- 申万一级行业板块均值（用全市场 daily join） ----
    try:
        sw_list = pro.index_classify(level="L1", src="SW2021").to_dict("records")
        print(f"[sw] {len(sw_list)} 个一级行业")
        day_map = {r["ts_code"]: r for r in all_day}
        sec_out = []
        for srow in sw_list:
            ic = srow["index_code"]
            try:
                mem = pro.index_member(index_code=ic).to_dict("records")
            except Exception:
                continue
            mem = [m for m in mem if (m.get("is_new") in (True, "Y", 1, "1", None))]
            rows = []
            for m in mem:
                c = m.get("ts_code") or m.get("con_code")
                if not c or c not in day_map:
                    continue
                d = day_map[c]
                if d.get("pct_chg") is None:
                    continue
                rows.append(d)
            if len(rows) < 8:
                continue
            pcts = [r["pct_chg"] for r in rows]
            amt = sum((r.get("amount") or 0) for r in rows) / 1e5
            n_zt = 0
            for r in rows:
                code = r["ts_code"].split(".")[0]
                pc = prev_map.get(r["ts_code"], {}).get("close")
                if pc is None:
                    continue
                lp = limit_price(code, pc)
                if r["high"] and abs(r["high"] - lp) < 0.011 and r["close"] >= lp - 0.011:
                    n_zt += 1
            sec_out.append({
                "code": ic, "name": srow["industry_name"], "n": len(rows),
                "avg_pct": round(sum(pcts) / len(pcts), 2),
                "up": sum(1 for p in pcts if p > 0), "down": sum(1 for p in pcts if p < 0),
                "amount_yi": round(amt, 1), "zt": n_zt,
                "max_pct": round(max(pcts), 2),
                "top": sorted([{"name": r.get("name", ""), "code": r["ts_code"], "pct": round(r["pct_chg"], 2)}
                               for r in rows], key=lambda x: -x["pct"])[:6],
            })
        sec_out.sort(key=lambda s: -s["avg_pct"])
        out["sectors"] = sec_out
        print("[sw] 行业均值 TOP10:")
        for s in sec_out[:10]:
            print(f"   {s['name']:<10} 均值{s['avg_pct']:+.2f}% {s['up']}涨{s['down']}跌 "
                  f"额{s['amount_yi']}亿 涨停{s['zt']}")
        print("[sw] 行业均值 BOTTOM5:")
        for s in sec_out[-5:]:
            print(f"   {s['name']:<10} 均值{s['avg_pct']:+.2f}% {s['up']}涨{s['down']}跌 额{s['amount_yi']}亿")
    except Exception as e:
        print("[sw] 失败:", e)

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    (CHART_DIR / "_ts_20261118.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {CHART_DIR/'_ts_20261118.json'}")


if __name__ == "__main__":
    main()
