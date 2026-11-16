"""11/16 补充口径：银行/红利 + 算力租赁 两个板块篮子（博主 11/16 唯一点名的两个方向）。

用法： python3 scripts/collect_extra_20261116.py
依赖： charts/_daily_20261116.json（主采集产物）→ 追加标的并重算板块均值
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_daily_20261116 import fetch_daily, retry, pro  # noqa: E402

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")

BANK = ["601398.SH", "601939.SH", "601288.SH", "601988.SH", "601328.SH",
        "600036.SH", "601166.SH", "600000.SH", "601818.SH", "000001.SZ"]
CALC = ["300442.SZ", "603881.SH", "300383.SZ", "300738.SZ", "002335.SZ",
        "603887.SH", "600602.SH", "300846.SZ", "300383.SZ", "300383.SZ"]
CALC = sorted(set(CALC))

NAMES = {
    "601398.SH": "工商银行", "601939.SH": "建设银行", "601288.SH": "农业银行",
    "601988.SH": "中国银行", "601328.SH": "交通银行", "600036.SH": "招商银行",
    "601166.SH": "兴业银行", "600000.SH": "浦发银行", "601818.SH": "光大银行",
    "000001.SZ": "平安银行",
    "300442.SZ": "润泽科技", "603881.SH": "数据港", "300383.SZ": "光环新网",
    "300738.SZ": "奥飞数据", "002335.SZ": "科华数据", "603887.SH": "城地香江",
    "600602.SH": "云赛智联", "300846.SZ": "首都在线",
}
EXTRA = {"银行/红利": BANK, "算力租赁/IDC": CALC}


def main():
    daily = json.loads((CH / "_daily_20261116.json").read_text(encoding="utf-8"))
    last = json.loads((CH / "_last_20261116.json").read_text(encoding="utf-8"))

    for c in BANK + CALC:
        if c in daily:
            continue
        df = fetch_daily(c)
        if df.empty:
            print(f"  [skip] {c}")
            continue
        daily[c] = df.to_dict("records")
        r, pc = df.iloc[-1], df.iloc[-2]
        pct = (r["Close"] / pc["Close"] - 1) * 100
        last[c] = {"name": NAMES.get(c, c), "close": round(r["Close"], 2),
                   "pct": round(pct, 2), "high": round(r["High"], 2),
                   "low": round(r["Low"], 2), "open": round(r["Open"], 2),
                   "prev_close": round(pc["Close"], 2), "date": r["Date"],
                   "hi60": round(df["High"].tail(60).max(), 2),
                   "lo60": round(df["Low"].tail(60).min(), 2),
                   "ma5": round(df["Close"].rolling(5).mean().iloc[-1], 2),
                   "ma10": round(df["Close"].rolling(10).mean().iloc[-1], 2),
                   "ma20": round(df["Close"].rolling(20).mean().iloc[-1], 2)}
        print(f"  [ok] {c:10s} {NAMES.get(c,c):6s} {r['Close']:9.2f} {pct:+6.2f}%")
        time.sleep(0.15)

    # 全量单日表 → 算新增板块篮子
    df_all = retry(pro.daily, trade_date="20261116")
    full = df_all.set_index("ts_code")[["pct_chg", "close", "amount"]].to_dict("index")

    sec = json.loads((CH / "_sectors_20261116.json").read_text(encoding="utf-8"))
    for pname, codes in EXTRA.items():
        rows, pcts, amts = [], [], []
        for c in codes:
            rec = full.get(c)
            if not rec:
                continue
            p = rec["pct_chg"]
            pcts.append(p)
            amts.append(rec["amount"] / 1e5)
            rows.append({"code": c, "name": NAMES.get(c, c), "pct": round(p, 2),
                         "amount_yi": round(rec["amount"] / 1e5, 2),
                         "close": round(rec["close"], 2)})
        if not pcts:
            continue
        rows.sort(key=lambda x: -x["pct"])
        sec["pools"][pname] = {
            "n": len(pcts), "avg_pct": round(sum(pcts) / len(pcts), 2),
            "up": sum(1 for x in pcts if x > 0), "down": sum(1 for x in pcts if x < 0),
            "amount_yi": round(sum(amts), 1),
            "max_pct": round(max(pcts), 2), "min_pct": round(min(pcts), 2)}
        sec["members"][pname] = rows
        s = sec["pools"][pname]
        print(f"  {pname:14s} 均值 {s['avg_pct']:+6.2f}%  涨 {s['up']} / 跌 {s['down']}  "
              f"额 {s['amount_yi']:,.0f} 亿")

    (CH / "_daily_20261116.json").write_text(json.dumps(daily, ensure_ascii=False), encoding="utf-8")
    (CH / "_last_20261116.json").write_text(json.dumps(last, ensure_ascii=False, indent=2), encoding="utf-8")
    (CH / "_sectors_20261116.json").write_text(json.dumps(sec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] {CH} 共 {len(daily)} 标的")


if __name__ == "__main__":
    main()
