"""11/12 板块口径（东财 push2 已限流 → 改用 Tushare 申万成分 + 核心概念池）。

口径说明（写进报告「附录口径」）：
- 军工：用申万一级「国防军工 801740.SI」全部在册成分（可复现）
- 存储/半导体、CPO/光通信、人形机器人：核心标的池（成分逐一列明）
- 冲板判定：当日最高价 == 涨停价（主板 10%、创业板/科创板 20%、ST 5%）

用法： ~/czsc/.venv/bin/python scripts/collect_sectors_20261112.py
"""
import json
import os
import time
from pathlib import Path

import pandas as pd
import tushare as ts

pro = ts.pro_api(os.environ["TUSHARE_TOKEN"])
OUT = Path("/Users/maoling/workspace/mnote.github.io/charts")

POOLS = {
    "存储/半导体/GPU": ["603986.SH", "301308.SZ", "688525.SH", "001309.SZ",
                        "300475.SZ", "688256.SH", "688041.SH", "688008.SH"],
    "CPO/光通信": ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH",
                    "688498.SH", "300570.SZ", "002281.SZ", "002396.SZ"],
    "军工": ["600760.SH", "000768.SZ", "600435.SH", "600685.SH", "002625.SZ",
             "688297.SH", "600893.SH", "002179.SZ", "600372.SH", "600150.SH",
             "688776.SH", "002389.SZ"],
    "人形机器人/端侧": ["688836.SH", "300124.SZ", "002472.SZ", "300450.SZ",
                         "601689.SH", "603662.SH", "300718.SZ", "002527.SZ",
                         "603893.SH", "688332.SH"],
}
NAMES = {
    "603986.SH": "兆易创新", "301308.SZ": "江波龙", "688525.SH": "佰维存储",
    "001309.SZ": "德明利", "300475.SZ": "香农芯创", "688256.SH": "寒武纪",
    "688041.SH": "海光信息", "688008.SH": "澜起科技", "300308.SZ": "中际旭创",
    "300502.SZ": "新易盛", "300394.SZ": "天孚通信", "601869.SH": "长飞光纤",
    "688498.SH": "源杰科技", "300570.SZ": "太辰光", "002281.SZ": "光迅科技",
    "002396.SZ": "星网锐捷", "600760.SH": "中航沈飞", "000768.SZ": "中航西飞",
    "600435.SH": "北方导航", "600685.SH": "中船防务", "002625.SZ": "光启技术",
    "688297.SH": "中无人机", "600893.SH": "航发动力", "002179.SZ": "中航光电",
    "600372.SH": "中航机载", "600150.SH": "中国船舶", "688776.SH": "国光电气",
    "002389.SZ": "航天彩虹", "688836.SH": "宇树科技", "300124.SZ": "汇川技术",
    "002472.SZ": "双环传动", "300450.SZ": "先导智能", "601689.SH": "拓普集团",
    "603662.SH": "柯银科技", "300718.SZ": "长盛轴承", "002527.SZ": "新时达",
    "603893.SH": "瑞芯微", "688332.SH": "芯原股份",
}


def limit_price(code, pre_close, name=""):
    if "ST" in name.upper():
        return round(pre_close * 1.05, 2)
    if code.startswith(("300", "301", "688")):
        return round(pre_close * 1.20, 2)
    if code.startswith(("8", "4", "9")):
        return round(pre_close * 1.30, 2)
    return round(pre_close * 1.10, 2)


def main():
    df = pro.daily(trade_date="20261112")
    df["ts_code"] = df["ts_code"]
    basic = pro.stock_basic(exchange="", list_status="L", fields="ts_code,name")
    nm = dict(zip(basic["ts_code"], basic["name"]))
    df["name"] = df["ts_code"].map(nm).fillna("")
    print(f"[daily] 20261112 {len(df)} 只")

    # 申万国防军工成分
    mem = pro.index_member(index_code="801740.SI")
    mil = sorted(set(mem["con_code"]))
    print(f"[SW 801740] 成分 {len(mil)} 只")

    out = {"date": "20261112", "pools": {}, "sw_mil": {}}

    # 1) 核心概念池
    for pname, codes in POOLS.items():
        sub = df[df["ts_code"].isin(codes)].copy()
        if sub.empty:
            continue
        sub["limit"] = [limit_price(c, p, n) for c, p, n in
                        zip(sub["ts_code"], sub["pre_close"], sub["name"])]
        sub["hit_limit"] = sub["high"] >= sub["limit"] - 0.011
        rows = sorted(sub.to_dict("records"), key=lambda r: -r["pct_chg"])
        avg = sub["pct_chg"].mean()
        out["pools"][pname] = {
            "n": len(sub), "avg": round(float(avg), 2),
            "up": int((sub["pct_chg"] > 0).sum()), "down": int((sub["pct_chg"] < 0).sum()),
            "amount_yi": round(float(sub["amount"].sum() / 1e5), 1),
            "hit_limit": int(sub["hit_limit"].sum()),
            "members": [{"code": r["ts_code"], "name": r["name"], "name2": NAMES.get(r["ts_code"], r["name"]),
                         "pct": round(r["pct_chg"], 2), "close": r["close"],
                         "high": r["high"], "low": r["low"], "pre_close": r["pre_close"],
                         "limit": r["limit"], "hit_limit": bool(r["hit_limit"]),
                         "amount_yi": round(r["amount"] / 1e5, 1),
                         "turnover": r.get("turn")} for r in rows],
        }
        print(f"  {pname:18s} n={len(sub):2d} 均值 {avg:+6.2f}%  "
              f"涨{int((sub['pct_chg']>0).sum())}/跌{int((sub['pct_chg']<0).sum())}  "
              f"冲板{int(sub['hit_limit'].sum())}  额{sub['amount'].sum()/1e5:,.0f}亿")

    # 2) 申万国防军工全成分
    sub = df[df["ts_code"].isin(mil)].copy()
    sub["limit"] = [limit_price(c, p, n) for c, p, n in
                    zip(sub["ts_code"], sub["pre_close"], sub["name"])]
    sub["hit_limit"] = sub["high"] >= sub["limit"] - 0.011
    rows = sorted(sub.to_dict("records"), key=lambda r: -r["pct_chg"])
    hit = rows and [r for r in rows if r["hit_limit"]]
    out["sw_mil"] = {
        "index": "801740.SI 国防军工", "n": len(sub),
        "avg": round(float(sub["pct_chg"].mean()), 2),
        "up": int((sub["pct_chg"] > 0).sum()), "down": int((sub["pct_chg"] < 0).sum()),
        "amount_yi": round(float(sub["amount"].sum() / 1e5), 1),
        "hit_limit": int(sub["hit_limit"].sum()),
        "hit_limit_list": [{"code": r["ts_code"], "name": r["name"],
                            "pct": round(r["pct_chg"], 2), "high": r["high"],
                            "limit": r["limit"]} for r in hit] if hit else [],
        "top": [{"code": r["ts_code"], "name": r["name"], "pct": round(r["pct_chg"], 2),
                 "high": r["high"], "limit": r["limit"], "hit": bool(r["hit_limit"]),
                 "amount_yi": round(r["amount"] / 1e5, 1)} for r in rows[:15]],
        "bottom": [{"code": r["ts_code"], "name": r["name"], "pct": round(r["pct_chg"], 2)}
                   for r in rows[-8:]],
    }
    print(f"\n  申万国防军工 n={len(sub)} 均值 {out['sw_mil']['avg']:+.2f}% "
          f"涨{out['sw_mil']['up']}/跌{out['sw_mil']['down']} 冲板 {out['sw_mil']['hit_limit']} 只")
    for r in out["sw_mil"]["hit_limit_list"]:
        print(f"    * 冲板 {r['name']}({r['code']}) 高{r['high']} 涨停价{r['limit']} 收{r['pct']:+.2f}%")
    print("  涨幅前 8：", ", ".join(f"{r['name']}{r['pct']:+.2f}%" for r in out["sw_mil"]["top"][:8]))

    # 3) 申万电子 / 通信（对照）
    for idx, iname in (("801080.SI", "电子"), ("801770.SI", "通信")):
        m2 = pro.index_member(index_code=idx)
        codes = sorted(set(m2["con_code"]))
        s2 = df[df["ts_code"].isin(codes)]
        if s2.empty:
            continue
        out.setdefault("sw_industry", {})[iname] = {
            "index": idx, "n": len(s2), "avg": round(float(s2["pct_chg"].mean()), 2),
            "up": int((s2["pct_chg"] > 0).sum()), "down": int((s2["pct_chg"] < 0).sum()),
            "amount_yi": round(float(s2["amount"].sum() / 1e5), 1),
        }
        print(f"  申万{iname} n={len(s2)} 均值 {out['sw_industry'][iname]['avg']:+.2f}%")
        time.sleep(0.4)

    (OUT / "_sectors_20261112.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {OUT/'_sectors_20261112.json'}")


if __name__ == "__main__":
    main()
