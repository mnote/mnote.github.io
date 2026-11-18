"""wu2198 报告 · 市场情绪/连板/行业分布 — 2026-11-18

口径：Tushare Pro 日线。涨停判定用 pro.daily 的 high/close 对比前收涨跌停价。
输出：charts/_mkt_20261118.json
"""
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import tushare as ts

pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN"))
CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
DATES = ["20261112", "20261113", "20261116", "20261117", "20261118"]


def lp(code, pc, name):
    if "ST" in name:
        return round(pc * 1.05, 2)
    if code.startswith("30") or code.startswith("688"):
        return round(pc * 1.2, 2)
    if code.startswith("8") or code.startswith("4") or code.startswith("92"):
        return round(pc * 1.3, 2)
    return round(pc * 1.1, 2)


def main():
    nm = {r["ts_code"]: r["name"] for r in pro.stock_basic(
        exchange="", list_status="L", fields="ts_code,name").to_dict("records")}
    # 申万一级行业映射
    sw1 = {r["index_code"]: r["industry_name"] for r in pro.index_classify(
        level="L1", src="SW2021").to_dict("records")}
    code2ind = {}
    for ic in sw1:
        for m in pro.index_member(index_code=ic).to_dict("records"):
            c = m.get("ts_code") or m.get("con_code")
            if c and m.get("is_new") in (True, "Y", 1, "1", None):
                code2ind[c] = sw1[ic]

    daily = {}
    for d in DATES:
        daily[d] = {r["ts_code"]: r for r in pro.daily(trade_date=d).to_dict("records")}

    out = {"days": {}}
    ztset = {}
    for i, d in enumerate(DATES):
        prev_d = DATES[i - 1] if i > 0 else None
        if not prev_d:
            continue
        # 沪深两市成交额（daily_info：SH_MARKET + SZ_MARKET，单位亿元）
        try:
            di = {r["ts_code"]: r for r in pro.daily_info(trade_date=d).to_dict("records")}
            sz_amount = (di.get("SH_MARKET", {}).get("amount") or 0) + \
                        (di.get("SZ_MARKET", {}).get("amount") or 0)
        except Exception:
            sz_amount = None
        dd, pd = daily[d], daily[prev_d]
        zt, dt = [], []
        for code, r in dd.items():
            pc = pd.get(code, {}).get("close")
            if pc is None:
                continue
            name = nm.get(code, "")
            up = lp(code.split(".")[0], pc, name)
            if "ST" in name:
                dm = 0.95
            elif code.split(".")[0][:2] in ("30", "68"):
                dm = 0.8
            elif code.split(".")[0][0] in "489":
                dm = 0.7
            else:
                dm = 0.9
            low_p = round(pc * dm, 2)
            if r["high"] and abs(r["high"] - up) < 0.011 and r["close"] >= up - 0.011:
                zt.append(code)
            if r["low"] and abs(r["low"] - low_p) < 0.011 and r["close"] <= low_p + 0.011:
                dt.append(code)
        amt = sum((r.get("amount") or 0) for r in dd.values()) / 1e5
        up_n = sum(1 for r in dd.values() if (r.get("pct_chg") or 0) > 0)
        dn_n = sum(1 for r in dd.values() if (r.get("pct_chg") or 0) < 0)
        out["days"][d] = {
            "amount_yi": round(amt, 0), "zt": len(zt), "dt": len(dt),
            "up": up_n, "down": dn_n, "total": len(dd),
            "sz_amount_yi": round(sz_amount, 2) if sz_amount else None,
        }
        ztset[d] = set(zt)
        print(f"[day] {d} 额{amt:.0f}亿 沪深{sz_amount} 涨{up_n} 跌{dn_n} 涨停{len(zt)} 跌停{len(dt)}")

    # 连板梯队（11/18）
    ladder = defaultdict(list)
    seq = ["20261112", "20261113", "20261116", "20261117", "20261118"]
    for code in ztset["20261118"]:
        n = 1
        for j in range(len(seq) - 2, -1, -1):
            if code in ztset.get(seq[j], set()):
                n += 1
            else:
                break
        ladder[n].append(code)
    print("\n[连板梯队 11/18]")
    for n in sorted(ladder, reverse=True):
        names = [f"{nm.get(c,'')}({c})" for c in sorted(ladder[n])]
        print(f"  {n} 板 {len(ladder[n])} 家: {', '.join(names)}")
    out["ladder"] = {str(n): [f"{nm.get(c,'')} {c}" for c in sorted(v)]
                     for n, v in sorted(ladder.items(), reverse=True)}

    # 涨停行业分布
    dist = Counter(code2ind.get(c, "其他") for c in ztset["20261118"])
    print("\n[涨停行业分布 11/18]")
    for k, v in dist.most_common():
        print(f"  {k}: {v}")
    out["zt_industry"] = dict(dist.most_common())

    # 算力/IDC 涨停明细（11/18）
    idc = ["000815.SZ", "000889.SZ", "002929.SZ", "600410.SH", "603887.SH",
           "603629.SH", "603985.SH", "600405.SH", "600602.SH", "300738.SZ",
           "603881.SH", "600845.SH", "300846.SZ", "300017.SZ", "002229.SZ",
           "603912.SH", "002335.SZ", "300442.SZ", "002837.SZ"]
    out["idc_zt"] = [f"{nm.get(c,'')} {c}" for c in idc if c in ztset["20261118"]]
    print("\n[算力/IDC 池涨停]", len(out["idc_zt"]), out["idc_zt"])

    (CHART_DIR / "_mkt_20261118.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {CHART_DIR/'_mkt_20261118.json'}")


if __name__ == "__main__":
    main()
