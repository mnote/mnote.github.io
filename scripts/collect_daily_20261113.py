"""11/13 日线数据 + 全市场宽度 + 板块篮子（Tushare Pro + 东财 push2ex）。

只用日线级别；不用分钟线、不用 czsc。
用法： python3 scripts/collect_daily_20261113.py
产物： charts/_daily_20261113.json / _last_20261113.json / _breadth_20261113.json
"""
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd
import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN") or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261113"

INDEXES = ["000001.SH", "399006.SZ", "399001.SZ", "000300.SH", "000688.SH"]

# 核心标的池（沿用 11/12 口径，保证跨期可比）
STORAGE = ["603986.SH", "301308.SZ", "688525.SH", "001309.SZ", "300475.SZ",
           "688256.SH", "688041.SH", "688008.SH"]
CPO = ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH", "688498.SH",
       "300570.SZ", "002281.SZ", "002396.SZ"]
MIL = ["600760.SH", "000768.SZ", "600435.SH", "600685.SH", "002625.SZ",
       "688297.SH", "600893.SH", "002179.SZ", "600372.SH", "600150.SH",
       "688776.SH", "002389.SZ"]
ROBOT = ["688836.SH", "300124.SZ", "002472.SZ", "300450.SZ", "601689.SH",
         "603662.SH", "300718.SZ", "002527.SZ", "603893.SH", "688332.SH"]
# 白酒/大消费（11/08 泡沫警示方向，做对照）
CONSUMER = ["600519.SH", "000858.SZ", "000568.SZ", "600809.SH", "000596.SZ"]
# 固态电池 / 锂电（博主常提，做对照）
SOLID = ["300750.SZ", "002074.SZ", "300568.SZ", "688779.SH", "300014.SZ"]

POOLS = {
    "存储/半导体/GPU": STORAGE,
    "CPO/光通信": CPO,
    "军工": MIL,
    "人形机器人/端侧": ROBOT,
    "白酒/大消费": CONSUMER,
    "固态/锂电": SOLID,
}
ALL_STOCKS = sorted({c for v in POOLS.values() for c in v})

NAMES = {
    "603986.SH": "兆易创新", "301308.SZ": "江波龙", "688525.SH": "佰维存储",
    "001309.SZ": "德明利", "300475.SZ": "香农芯创", "688256.SH": "寒武纪",
    "688041.SH": "海光信息", "688008.SH": "澜起科技",
    "300308.SZ": "中际旭创", "300502.SZ": "新易盛", "300394.SZ": "天孚通信",
    "601869.SH": "长飞光纤", "688498.SH": "源杰科技", "300570.SZ": "太辰光",
    "002281.SZ": "光迅科技", "002396.SZ": "星网锐捷",
    "600760.SH": "中航沈飞", "000768.SZ": "中航西飞", "600435.SH": "北方导航",
    "600685.SH": "中船防务", "002625.SZ": "光启技术", "688297.SH": "中无人机",
    "600893.SH": "航发动力", "002179.SZ": "中航光电", "600372.SH": "中航机载",
    "600150.SH": "中国船舶", "688776.SH": "国光电气", "002389.SZ": "航天彩虹",
    "688836.SH": "宇树科技", "300124.SZ": "汇川技术", "002472.SZ": "双环传动",
    "300450.SZ": "先导智能", "601689.SH": "拓普集团", "603662.SH": "柯银科技",
    "300718.SZ": "长盛轴承", "002527.SZ": "新时达", "603893.SH": "瑞芯微",
    "688332.SH": "芯原股份",
    "600519.SH": "贵州茅台", "000858.SZ": "五粮液", "000568.SZ": "泸州老窖",
    "600809.SH": "山西汾酒", "000596.SZ": "古井贡酒",
    "300750.SZ": "宁德时代", "002074.SZ": "国轩高科", "300568.SZ": "星源材质",
    "688779.SH": "长远锂科", "300014.SZ": "亿纬锂能",
}
IDX_NAMES = {"000001.SH": "上证指数", "399006.SZ": "创业板指",
              "399001.SZ": "深证成指", "000300.SH": "沪深300",
              "000688.SH": "科创50"}


def retry(fn, n=4, **kw):
    for i in range(n):
        try:
            df = fn(**kw)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            if i == n - 1:
                print(f"    [ERR] {kw} {e}", flush=True)
            time.sleep(1.2)
    return pd.DataFrame()


def fetch_daily(ts_code, days=130):
    idx = ts_code in ("000001.SH", "399006.SZ", "399001.SZ", "000300.SH", "000688.SH")
    if idx:
        df = retry(pro.index_daily, ts_code=ts_code, start_date=START, end_date=END)
        adj = None
    else:
        df = retry(pro.daily, ts_code=ts_code, start_date=START, end_date=END)
        adj = retry(pro.adj_factor, ts_code=ts_code, start_date=START, end_date=END)
    if df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    if adj is not None and not adj.empty:
        adj = adj.copy()
        adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
        adj = adj.sort_values("trade_date")
        df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
        df["adj_factor"] = df["adj_factor"].ffill().bfill()
        latest = df["adj_factor"].iloc[-1]
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] * df["adj_factor"] / latest
    df = df.tail(days).reset_index(drop=True)
    df = df.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                            "low": "Low", "close": "Close", "vol": "Volume"})
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Volume"] = df["Volume"].astype(float)
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]]


def em_pool(kind, date):
    """东财涨停/炸板/跌停池（push2ex，curl 抓）。"""
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool"
           f"?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0"
           f"&pagesize=300&sort=fbt:asc&date={date}")
    try:
        r = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0",
             "-H", "Referer: https://quote.eastmoney.com/", url],
            capture_output=True, timeout=30)
        return json.loads(r.stdout.decode("utf-8", "ignore"))
    except Exception as e:
        print(f"    [em {kind}] {e}", flush=True)
        return None


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)

    data, last = {}, {}
    for c in INDEXES + ALL_STOCKS:
        df = fetch_daily(c)
        if df.empty:
            print(f"  [skip] {c}", flush=True)
            continue
        data[c] = df.to_dict("records")
        r = df.iloc[-1]
        pc = df.iloc[-2]
        pct = (r["Close"] / pc["Close"] - 1) * 100
        last[c] = {"name": NAMES.get(c) or IDX_NAMES.get(c, c),
                   "close": round(r["Close"], 2), "pct": round(pct, 2),
                   "high": round(r["High"], 2), "low": round(r["Low"], 2),
                   "open": round(r["Open"], 2), "prev_close": round(pc["Close"], 2),
                   "date": r["Date"],
                   "hi60": round(df["High"].tail(60).max(), 2),
                   "lo60": round(df["Low"].tail(60).min(), 2),
                   "ma5": round(df["Close"].rolling(5).mean().iloc[-1], 2),
                   "ma10": round(df["Close"].rolling(10).mean().iloc[-1], 2),
                   "ma20": round(df["Close"].rolling(20).mean().iloc[-1], 2)}
        print(f"  [ok] {c:10s} {last[c]['name']:6s} {r['Close']:9.2f} {pct:+6.2f}%  "
              f"H {r['High']:.2f} L {r['Low']:.2f}  {last[c]['date']}", flush=True)
        time.sleep(0.15)

    (out_dir / "_daily_20261113.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8")
    (out_dir / "_last_20261113.json").write_text(
        json.dumps(last, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] _daily_20261113.json  ({len(data)} 标的)", flush=True)

    # ── 全市场宽度 + 板块篮子均值（单次全量）─────────────
    print("\n=== 全市场宽度 ===", flush=True)
    breadth, full = {}, {}
    for d in ["20261113", "20261112", "20261111"]:
        df = retry(pro.daily, trade_date=d)
        if df.empty:
            continue
        amt = df["amount"].sum() / 1e5
        up = int((df["pct_chg"] > 0).sum())
        dn = int((df["pct_chg"] < 0).sum())
        fl = int((df["pct_chg"] == 0).sum())
        lt = int((df["pct_chg"] >= 9.9).sum())
        dt = int((df["pct_chg"] <= -9.9).sum())
        breadth[d] = {"amount_yi": round(amt, 1), "up": up, "down": dn, "flat": fl,
                      "limit_up": lt, "limit_down": dt, "n": int(len(df))}
        if d == "20261113":
            full = df.set_index("ts_code")[["pct_chg", "close", "amount"]].to_dict("index")
        print(f"  {d}  成交额 {amt:,.0f} 亿  涨 {up} / 跌 {dn} / 平 {fl}  "
              f"涨9.9+ {lt}  跌9.9- {dt}  ({len(df)} 只)", flush=True)
        time.sleep(0.4)

    (out_dir / "_breadth_20261113.json").write_text(
        json.dumps(breadth, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 板块篮子均值 ────────────────────────────────────
    print("\n=== 板块篮子（核心标的池）===", flush=True)
    sectors = {"pools": {}, "members": {}}
    for pname, codes in POOLS.items():
        rows, pcts, amts = [], [], []
        for c in codes:
            rec = full.get(c)
            if not rec:
                continue
            p = rec["pct_chg"]
            pcts.append(p)
            amts.append(rec["amount"] / 1e5)
            rows.append({"code": c, "name": NAMES.get(c, c),
                         "pct": round(p, 2), "amount_yi": round(rec["amount"] / 1e5, 2),
                         "close": round(rec["close"], 2)})
        if not pcts:
            continue
        rows.sort(key=lambda x: -x["pct"])
        sectors["pools"][pname] = {
            "n": len(pcts), "avg_pct": round(sum(pcts) / len(pcts), 2),
            "up": sum(1 for p in pcts if p > 0), "down": sum(1 for p in pcts if p < 0),
            "amount_yi": round(sum(amts), 1),
            "max_pct": round(max(pcts), 2), "min_pct": round(min(pcts), 2),
        }
        sectors["members"][pname] = rows
        s = sectors["pools"][pname]
        print(f"  {pname:14s} 均值 {s['avg_pct']:+6.2f}%  涨 {s['up']} / 跌 {s['down']}  "
              f"额 {s['amount_yi']:,.0f} 亿  [{s['max_pct']:+.2f}%, {s['min_pct']:+.2f}%]", flush=True)

    # 全 A 涨幅榜 TOP30
    top = sorted([{"code": c, "name": NAMES.get(c, c), "pct": round(r["pct_chg"], 2),
                   "amount_yi": round(r["amount"] / 1e5, 2)}
                  for c, r in full.items() if r["pct_chg"] is not None],
                 key=lambda x: -x["pct"])[:30]
    sectors["top_gainers"] = top
    print("\n  涨幅 TOP10：", flush=True)
    for t in top[:10]:
        print(f"    {t['name']:8s} {t['code']:10s} {t['pct']:+7.2f}%  {t['amount_yi']:,.1f} 亿", flush=True)

    (out_dir / "_sectors_20261113.json").write_text(
        json.dumps(sectors, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 东财涨停/炸板/跌停池 + 行业分布 ────────────────────
    print("\n=== 涨停池行业分布 ===", flush=True)
    pools = {}
    for kind, key in [("ZT", "zt"), ("ZB", "zb"), ("DT", "dt")]:
        d = em_pool(kind, "20261113")
        if not d or not d.get("data"):
            print(f"  [em {kind}] 无数据", flush=True)
            continue
        tc = d["data"].get("tc", 0)
        arr = d["data"].get("pool") or []
        ind = {}
        for x in arr:
            ind[x.get("hybk", "未知")] = ind.get(x.get("hybk", "未知"), 0) + 1
        pools[key] = {"tc": tc, "n": len(arr),
                      "industry": dict(sorted(ind.items(), key=lambda kv: -kv[1])),
                      "members": [{"code": x.get("c"), "name": x.get("n"),
                                   "pct": x.get("zdp"), "lbc": x.get("lbc"),
                                   "ind": x.get("hybk")} for x in arr]}
        print(f"  {key}: {tc} 只", flush=True)
        for k, v in list(pools[key]["industry"].items())[:12]:
            print(f"    {k}: {v}", flush=True)
        time.sleep(0.3)

    (out_dir / "_em_pools_20261113.json").write_text(
        json.dumps(pools, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n[done]", flush=True)
