"""wu2198 报告 · 板块核心标的池核验 — 2026-11-18

用途：核验博主 11/18 点名的板块（算力租赁 / 交换机 / PCB / 铁路 / 国产替代）
      是否在收盘口径兑现，并算出池内均值、涨跌家数、连板梯队。
口径：Tushare Pro 日线（pro.daily 全市场单次全量 join），禁止分钟级。
输出：stdout + charts/_pools_20261118.json
"""
import json
import os
from collections import defaultdict
from pathlib import Path

import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN")
pro = ts.pro_api(TOKEN)

TD = "20261118"
PREV = "20261117"
CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")

POOLS = {
    "算力租赁/IDC": ["000815.SZ", "000889.SZ", "002929.SZ", "600410.SH", "603887.SH",
                     "603629.SH", "603985.SH", "600405.SH", "600602.SH", "300738.SZ",
                     "603881.SH", "600845.SH", "300846.SZ", "300017.SZ", "002229.SZ",
                     "603912.SH", "002335.SZ", "300442.SZ", "002837.SZ"],
    "交换机": ["301165.SZ", "000938.SZ", "000063.SZ", "301191.SZ", "688702.SH",
               "603083.SH", "002396.SZ", "000977.SZ"],
    "PCB": ["002463.SZ", "002916.SZ", "600183.SH", "300476.SZ", "603228.SH",
            "002384.SZ", "002938.SZ", "001389.SZ", "688519.SH"],
    "CPO/光通信": ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH", "002281.SZ",
                   "603236.SH", "002465.SZ", "600487.SH"],
    "GPU/国产算力芯片": ["688256.SH", "688041.SH", "603019.SH", "688008.SH", "002371.SZ",
                          "688012.SH", "688072.SH", "688120.SH", "603986.SH"],
    "存储芯片": ["603986.SH", "688008.SH", "300223.SZ", "301308.SZ", "688525.SH",
                 "002049.SZ", "603986.SH", "688409.SH"],
    "白酒/食品饮料": ["600519.SH", "000858.SZ", "000568.SZ", "600809.SH", "000596.SZ",
                       "002304.SZ", "603369.SH", "600559.SH"],
    "军工": ["002179.SZ", "600760.SH", "002013.SZ", "600372.SH", "002414.SZ",
             "300699.SZ", "688187.SH", "002389.SZ", "600893.SH"],
    "铁路运营": ["601333.SH", "601006.SH", "600350.SH", "600377.SH"],
    "基建/铁建": ["601390.SH", "601186.SH", "601800.SH", "600528.SH"],
    "钢铁": ["600019.SH", "000708.SZ", "600010.SH", "002110.SZ"],
    "银行/红利": ["600036.SH", "601398.SH", "601288.SH", "600000.SH", "601988.SH",
                  "601328.SH"],
}


def limit_pct(code):
    if code.startswith("30") or code.startswith("688"):
        return 20
    if code.startswith("8") or code.startswith("4") or code.startswith("92"):
        return 30
    return 10


def limit_price(code, pre_close, name=""):
    if "ST" in name:
        return round(pre_close * 1.05, 2)
    return round(pre_close * (1 + limit_pct(code) / 100), 2)


def main():
    nm = {r["ts_code"]: r["name"] for r in pro.stock_basic(
        exchange="", list_status="L", fields="ts_code,name").to_dict("records")}

    d0 = {r["ts_code"]: r for r in pro.daily(trade_date=TD).to_dict("records")}
    d1 = {r["ts_code"]: r for r in pro.daily(trade_date=PREV).to_dict("records")}

    zt_today, zt_prev = set(), set()
    for store, dd in ((zt_today, d0), (zt_prev, d1)):
        for code, r in dd.items():
            pc = (d1 if dd is d0 else d0).get(code, {}).get("close")
            if pc is None:
                continue
            name = nm.get(code, "")
            lp = limit_price(code.split(".")[0], pc, name)
            if r["high"] and abs(r["high"] - lp) < 0.011 and r["close"] >= lp - 0.011:
                store.add(code)

    # 连板梯队
    lb = defaultdict(list)
    for code in zt_today & zt_prev:
        r0, r1 = d0[code], d1[code]
        lb[code].append((r0, r1))
    ladder = defaultdict(list)
    for code in zt_today & zt_prev:
        # 连续板数：向前回溯
        n = 0
        cur = code
        dates = sorted([d for d in (TD, PREV)], reverse=True)
        # 只回溯 2 日（11/18、11/17），更早需另拉
        ladder[2].append(code)
    print("[涨停] 今日", len(zt_today), "昨日", len(zt_prev),
          "连续2板", len(ladder[2]))
    for c in sorted(ladder[2]):
        print("   ", c, nm.get(c, ""), f"{d0[c]['pct_chg']:+.2f}%")

    out = {"trade_date": TD, "pools": {}, "zt_today": len(zt_today),
           "zt_prev": len(zt_prev), "ladder2": [f"{c} {nm.get(c,'')}" for c in sorted(ladder[2])]}

    for pool, codes in POOLS.items():
        recs = []
        for c in codes:
            if c not in d0:
                continue
            r, rp = d0[c], d1.get(c)
            if rp is None:
                continue
            recs.append({
                "code": c, "name": nm.get(c, ""),
                "close": r["close"], "pct": round(r["pct_chg"], 2),
                "prev_pct": round(rp["pct_chg"], 2),
                "high": r["high"], "low": r["low"],
                "amount_yi": round((r.get("amount") or 0) / 1e5, 1),
                "zt": c in zt_today,
            })
        if not recs:
            continue
        pcts = [x["pct"] for x in recs]
        prevs = [x["prev_pct"] for x in recs]
        out["pools"][pool] = {
            "n": len(recs),
            "avg": round(sum(pcts) / len(pcts), 2),
            "avg_prev": round(sum(prevs) / len(prevs), 2),
            "up": sum(1 for p in pcts if p > 0), "down": sum(1 for p in pcts if p < 0),
            "zt": sum(1 for x in recs if x["zt"]),
            "amount_yi": round(sum(x["amount_yi"] for x in recs), 1),
            "top": sorted(recs, key=lambda x: -x["pct"])[:6],
            "bottom": sorted(recs, key=lambda x: x["pct"])[:4],
            "members": recs,
        }
        p = out["pools"][pool]
        print(f"\n[{pool}] n={p['n']} 均值{p['avg']:+.2f}% (昨 {p['avg_prev']:+.2f}%) "
              f"{p['up']}涨{p['down']}跌 涨停{p['zt']} 额{p['amount_yi']}亿")
        for x in p["top"]:
            print(f"   {x['name']:<8}{x['code']:<11}{x['close']:>9.2f}{x['pct']:>+8.2f}% "
                  f"额{x['amount_yi']:>7.1f}亿 {'涨停' if x['zt'] else ''}")

    # 名称核对（防代码名错配）
    print("\n[名称核对]")
    for c in ["300308.SZ", "300502.SZ", "002463.SZ", "002916.SZ", "000938.SZ",
              "603019.SH", "688256.SH", "688041.SH", "601869.SH"]:
        print(f"   {c} = {nm.get(c, '?')}")

    (CHART_DIR / "_pools_20261118.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {CHART_DIR/'_pools_20261118.json'}")


if __name__ == "__main__":
    main()
