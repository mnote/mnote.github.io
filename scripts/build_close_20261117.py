"""11/17 收盘版：图表数据 + KPI + 板块篮子（东财口径单源，前复权）。

输入： charts/_close_20261117.json
输出： charts/_chartdata_20261117.json、_kpi_20261117.json、_pools_20261117.json
"""
import json
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")
CLOSE = json.loads((CH / "_close_20261117.json").read_text(encoding="utf-8"))
SER = CLOSE["series"]
SNAP = CLOSE["snapshot"]

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


def secid_of(code):
    num, mkt = code.split(".")
    return f"{1 if mkt == 'SH' else 0}.{num}"


def snap_of(code):
    return SNAP.get(secid_of(code))


if __name__ == "__main__":
    chartdata, kpi = {}, {}
    for c, rows in SER.items():
        if not rows:
            continue
        chartdata[c] = rows
        closes = [r["Close"] for r in rows]
        vols = [r["Volume"] for r in rows]
        s = snap_of(c) or {}
        last, prev = rows[-1], rows[-2]
        kpi[c] = {
            "name": s.get("name") or c,
            "close": round(last["Close"], 2),
            "pct": round(s.get("pct") if s.get("pct") is not None
                         else (last["Close"] / prev["Close"] - 1) * 100, 2),
            "open": round(last["Open"], 2), "high": round(last["High"], 2),
            "low": round(last["Low"], 2),
            "prev_close": round(prev["Close"], 2),
            "amount_yi": round(last["Amount"] / 1e8, 2),
            "ma5": round(sum(closes[-5:]) / 5, 2),
            "ma10": round(sum(closes[-10:]) / 10, 2),
            "ma20": round(sum(closes[-20:]) / 20, 2),
            "hi60": round(max(r["High"] for r in rows[-60:]), 2),
            "lo60": round(min(r["Low"] for r in rows[-60:]), 2),
            "vol": round(vols[-1], 0),
            "vol_ma5": round(sum(vols[-5:]) / 5, 0),
            "vol_ratio": round(vols[-1] / (sum(vols[-5:]) / 5) * 100, 1),
            "date": last["Date"], "bars": len(rows),
        }

    pools = {}
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
        pools[pname] = {
            "n": len(pcts), "avg_pct": round(sum(pcts) / len(pcts), 2),
            "up": sum(1 for x in pcts if x > 0), "down": sum(1 for x in pcts if x < 0),
            "amount_yi": round(sum(amts), 1),
            "max_pct": round(max(pcts), 2), "min_pct": round(min(pcts), 2),
            "members": rows}

    (CH / "_chartdata_20261117.json").write_text(
        json.dumps(chartdata, ensure_ascii=False), encoding="utf-8")
    (CH / "_kpi_20261117.json").write_text(
        json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    (CH / "_pools_20261117.json").write_text(
        json.dumps(pools, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] chartdata {len(chartdata)} / kpi {len(kpi)} / pools {len(pools)}\n")
    print("板块（收盘）：")
    for k, v in sorted(pools.items(), key=lambda kv: -kv[1]["avg_pct"]):
        print(f"  {k:16s} 均值 {v['avg_pct']:+6.2f}%  涨{v['up']}/跌{v['down']}"
              f"  额{v['amount_yi']:>8,.0f}亿  [{v['min_pct']:+.2f},{v['max_pct']:+.2f}]")
    print("\n指数/个股：")
    for c in ["000001.SH", "399006.SZ", "399001.SZ", "000300.SH", "000688.SH",
              "300442.SZ", "688256.SH", "002179.SZ", "600036.SH", "600519.SH"]:
        v = kpi.get(c)
        if v:
            print(f"  {c:11s} {v['name']:10s} 收 {v['close']:>9.2f} {v['pct']:+6.2f}%"
                  f"  H {v['high']:>9.2f} L {v['low']:>9.2f} MA20 {v['ma20']:>9.2f}"
                  f"  60高 {v['hi60']:>9.2f} 60低 {v['lo60']:>9.2f} 量比 {v['vol_ratio']}%")
