"""11/17 盘中板块篮子 + KPI + 图表用数据（含今日未完成 K 线）。

用法： python3 scripts/build_intraday_20261117.py
输入： charts/_daily_20261116.json（到 11/16 日线）、charts/_intraday_20261117.json（盘中快照）
产物： charts/_pools_20261117.json、charts/_kpi_20261117.json、charts/_chartdata_20261117.json
"""
import json
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")

DAILY = json.loads((CH / "_daily_20261116.json").read_text(encoding="utf-8"))
INTRA = json.loads((CH / "_intraday_20261117.json").read_text(encoding="utf-8"))
SNAP = INTRA["snapshot"]
STAMP = INTRA["stamp"]
TODAY = "2026-11-17"

POOLS = {
    "存储/半导体/GPU": ["603986.SH", "301308.SZ", "688525.SH", "001309.SZ", "300475.SZ",
                        "688256.SH", "688041.SH", "688008.SH"],
    "CPO/光通信": ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH", "688498.SH",
                   "300570.SZ", "002281.SZ", "002396.SZ"],
    "军工": ["600760.SH", "000768.SZ", "600435.SH", "600685.SH", "002625.SZ",
             "688297.SH", "600893.SH", "002179.SZ", "600372.SH", "600150.SH",
             "688776.SH", "002389.SH"],
    "人形机器人/端侧": ["688836.SH", "300124.SZ", "002472.SZ", "300450.SZ", "601689.SH",
                        "603662.SH", "300718.SZ", "002527.SZ", "603893.SH", "688332.SH"],
    "白酒/大消费": ["600519.SH", "000858.SZ", "000568.SZ", "600809.SH", "000596.SZ"],
    "固态/锂电": ["300750.SZ", "002074.SZ", "300568.SZ", "688779.SH", "300014.SZ"],
    "银行/红利": ["601398.SH", "601939.SH", "601288.SH", "601988.SH", "601328.SH",
                  "600036.SH", "601166.SH", "600000.SH", "601818.SH", "000001.SZ"],
    "算力租赁/IDC": ["300442.SZ", "603881.SH", "300383.SZ", "300738.SZ", "002335.SZ",
                      "603887.SH", "600602.SH", "300846.SZ"],
}
NAMES = json.loads((CH / "_sectors_20261116.json").read_text(encoding="utf-8"))["members"]


def secid_of(ts_code):
    num, mkt = ts_code.split(".")
    return f"{1 if mkt == 'SH' else 0}.{num}"


def snap_of(ts_code):
    return SNAP.get(secid_of(ts_code))


def pool_stats():
    out = {}
    for pname, codes in POOLS.items():
        rows, pcts, amts = [], [], []
        for c in codes:
            s = snap_of(c)
            if not s:
                continue
            pcts.append(s["pct"])
            amts.append((s["amount"] or 0) / 1e8)
            rows.append({"code": c, "name": s["name"], "pct": round(s["pct"], 2),
                         "amount_yi": round((s["amount"] or 0) / 1e8, 2),
                         "price": round(s["price"], 2),
                         "high": round(s["high"], 2), "low": round(s["low"], 2),
                         "open": round(s["open"], 2)})
        if not pcts:
            continue
        rows.sort(key=lambda x: -x["pct"])
        out[pname] = {
            "n": len(pcts), "avg_pct": round(sum(pcts) / len(pcts), 2),
            "up": sum(1 for x in pcts if x > 0), "down": sum(1 for x in pcts if x < 0),
            "amount_yi": round(sum(amts), 1),
            "max_pct": round(max(pcts), 2), "min_pct": round(min(pcts), 2),
            "members": rows,
        }
    return out


def chart_series(ts_code):
    """日线（到 11/16）+ 今日未完成 K 线。"""
    rows = DAILY.get(ts_code)
    if not rows:
        return None
    out = [dict(r) for r in rows]
    s = snap_of(ts_code)
    if s:
        out.append({"Date": TODAY, "Open": round(s["open"], 3),
                    "High": round(s["high"], 3), "Low": round(s["low"], 3),
                    "Close": round(s["price"], 3),
                    "Volume": float(s["vol_hand"] or 0)})
    return out


if __name__ == "__main__":
    pools = pool_stats()
    print(f"[pools] 盘中快照 {STAMP}")
    for k, v in sorted(pools.items(), key=lambda kv: -kv[1]["avg_pct"]):
        print(f"  {k:16s} 均值 {v['avg_pct']:+6.2f}%  涨 {v['up']}/跌 {v['down']}"
              f"  额 {v['amount_yi']:>8,.0f} 亿  [{v['min_pct']:+.2f},{v['max_pct']:+.2f}]")

    targets = ["000001.SH", "399006.SZ", "399001.SZ", "000300.SH", "000688.SH",
               "300442.SZ", "603881.SH", "300846.SZ", "002335.SZ", "002179.SZ",
               "600760.SH", "688256.SH", "600036.SH", "600519.SH", "603986.SH",
               "688836.SH", "603893.SH", "300750.SZ", "600000.SH", "601288.SH",
               "601166.SH", "000568.SZ", "600809.SH", "688041.SH", "688525.SH",
               "300308.SZ", "300502.SZ", "002396.SZ", "002281.SZ", "601869.SH"]
    seen = []
    for t in targets:
        if t not in seen:
            seen.append(t)

    chartdata, kpi = {}, {}
    for c in seen:
        ser = chart_series(c)
        if not ser:
            continue
        chartdata[c] = ser
        rows = DAILY[c]
        last = rows[-1]
        s = snap_of(c)
        closes = [r["Close"] for r in ser]
        kpi[c] = {
            "name": (s or {}).get("name") or c,
            "prev_close": round(last["Close"], 2),
            "close": round(s["price"], 2) if s else round(last["Close"], 2),
            "pct": round(s["pct"], 2) if s else 0.0,
            "open": round(s["open"], 2) if s else None,
            "high": round(s["high"], 2) if s else None,
            "low": round(s["low"], 2) if s else None,
            "amount_yi": round((s["amount"] or 0) / 1e8, 2) if s else None,
            "ma5": round(sum(closes[-5:]) / 5, 2),
            "ma10": round(sum(closes[-10:]) / 10, 2),
            "ma20": round(sum(closes[-20:]) / 20, 2),
            "hi60": round(max(r["High"] for r in rows[-60:]), 2),
            "lo60": round(min(r["Low"] for r in rows[-60:]), 2),
            "prev_high": round(last["High"], 2),
            "prev_low": round(last["Low"], 2),
            "prev_date": last["Date"],
            "bars": len(ser),
        }

    (CH / "_pools_20261117.json").write_text(
        json.dumps(pools, ensure_ascii=False, indent=2), encoding="utf-8")
    (CH / "_chartdata_20261117.json").write_text(
        json.dumps(chartdata, ensure_ascii=False), encoding="utf-8")
    (CH / "_kpi_20261117.json").write_text(
        json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] pools {len(pools)} / chartdata {len(chartdata)} / kpi {len(kpi)}")
    for c in ["000001.SH", "399006.SZ", "600036.SH", "600519.SH", "300442.SZ"]:
        if c in kpi:
            v = kpi[c]
            print(f"  {c:11s} {v['name']:8s} 现 {v['close']:>9.2f} {v['pct']:+6.2f}%  "
                  f"H {v['high']} L {v['low']}  MA20 {v['ma20']}  60高 {v['hi60']} 60低 {v['lo60']}")
