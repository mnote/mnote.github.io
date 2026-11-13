"""都业华 2026-11-13 收评 · 日线数据采集（东财日线，无分钟级接口）
输出 reports/duyiehua-20261113/data_20261113.json
"""
import json, subprocess, time
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
OUTDIR = REPO / "reports/duyiehua-20261113"
OUTDIR.mkdir(parents=True, exist_ok=True)
DATE = "2026-11-13"

IDX = {"上证指数": "1.000001", "深证成指": "0.399001", "创业板指": "0.399006",
       "沪深300": "1.000300", "科创50": "1.000688"}

STOCKS = {
    "药明康德": "1.603259", "中国船舶": "1.600150", "瑞芯微": "1.603893",
    "伊利股份": "1.600887", "中文在线": "0.300364", "海天瑞声": "1.688787",
    "奥普特": "1.688686", "柯力传感": "1.603662", "兆易创新": "1.603986",
    "云铝股份": "0.000807", "模塑科技": "0.000700", "长盈精密": "0.300115",
}

BASKETS = {
    "人形机器人": ["0.000700", "0.300115", "0.002050", "1.601689", "1.688017",
                   "1.603728", "0.003021", "1.603009", "0.300124"],
    "AI视频/传媒": ["0.300364", "0.300133", "0.300182", "0.300251", "1.603533",
                    "0.300418", "1.601595"],
    "半导体": ["1.603893", "1.603986", "1.688256", "1.688041", "1.688981", "0.002371"],
    "算力/CPO": ["1.601138", "0.300308", "0.300502", "0.002463", "0.300476"],
    "银行": ["1.600036", "1.601398", "1.601939", "1.601288", "1.601166"],
    "电力/高股息": ["1.600900", "1.600025", "1.600886", "1.600674", "1.601985"],
    "玄学链·东方字样": ["1.600776", "0.002819", "1.600637", "1.600278", "0.000301", "0.002167"],
}


def em_kline(secid, lmt=160):
    url = ("https://push2his.eastmoney.com/api/qt/stock/kline/get?"
           f"secid={secid}&klt=101&fqt=1&lmt={lmt}&end=20500101"
           "&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56,f57")
    for i in range(4):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "20",
                                "-H", "User-Agent: Mozilla/5.0",
                                "-H", "Referer: https://quote.eastmoney.com/", url],
                               capture_output=True, text=True)
            j = json.loads(r.stdout)
            d = j.get("data")
            if not d or not d.get("klines"):
                raise RuntimeError("no data")
            rows = []
            for k in d["klines"]:
                f = k.split(",")
                rows.append({"d": f[0], "o": float(f[1]), "c": float(f[2]),
                             "h": float(f[3]), "l": float(f[4]),
                             "v": float(f[5]), "amt": float(f[6])})
            return d.get("name", ""), rows
        except Exception as e:
            print("  retry", secid, str(e)[:60], flush=True)
            time.sleep(1.2 + i)
    return "", []


def summarize(rows):
    if not rows:
        return None
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else last
    w60 = rows[-60:]
    w20 = rows[-20:]
    w5 = rows[-5:]
    return {
        "date": last["d"], "open": last["o"], "high": last["h"], "low": last["l"],
        "close": last["c"], "prev_close": prev["c"],
        "pct": round((last["c"] / prev["c"] - 1) * 100, 2),
        "vol": last["v"], "amount_yi": round(last["amt"] / 1e8, 2),
        "hi60": max(r["h"] for r in w60), "lo60": min(r["l"] for r in w60),
        "vol_ma5": round(sum(r["v"] for r in w5) / 5, 0),
        "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0),
    }


res = {"date": DATE, "index": {}, "stocks": {}, "baskets": {}, "series": {}}

for name, sid in IDX.items():
    n, rows = em_kline(sid, 160)
    res["index"][name] = summarize(rows)
    res["series"][name] = [{"d": r["d"], "o": r["o"], "h": r["h"], "l": r["l"], "c": r["c"], "v": r["v"]} for r in rows]
    print("IDX", name, res["index"][name]["close"], res["index"][name]["pct"], flush=True)

for name, sid in STOCKS.items():
    n, rows = em_kline(sid, 160)
    s = summarize(rows)
    s["code"] = sid.split(".")[1]
    s["em_name"] = n
    res["stocks"][name] = s
    res["series"][name] = [{"d": r["d"], "o": r["o"], "h": r["h"], "l": r["l"], "c": r["c"], "v": r["v"]} for r in rows]
    print("STK", name, s["close"], s["pct"], "H", s["high"], "L", s["low"], flush=True)

for bname, ids in BASKETS.items():
    rows_out = []
    for sid in ids:
        n, rows = em_kline(sid, 30)
        s = summarize(rows)
        if not s:
            continue
        s["code"] = sid.split(".")[1]
        s["name"] = n
        rows_out.append(s)
    avg = round(sum(r["pct"] for r in rows_out) / len(rows_out), 2) if rows_out else 0
    res["baskets"][bname] = {
        "avg_pct": avg, "n": len(rows_out),
        "up": sum(1 for r in rows_out if r["pct"] > 0),
        "down": sum(1 for r in rows_out if r["pct"] < 0),
        "amount_yi": round(sum(r["amount_yi"] for r in rows_out), 1),
        "members": rows_out,
    }
    print("BKT", bname, avg, f"{res['baskets'][bname]['up']}/{res['baskets'][bname]['down']}", flush=True)

(OUTDIR / "data_20261113.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", OUTDIR / "data_20261113.json")
