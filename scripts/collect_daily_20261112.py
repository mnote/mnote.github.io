"""11/12 日线数据 + 板块篮子 + 全市场宽度（Tushare Pro + 东财）。

只用日线级别；不用分钟线、不用 czsc。
用法： ~/czsc/.venv/bin/python scripts/collect_daily_20261112.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

import pandas as pd
import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN")
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261112"

INDEXES = ["000001.SH", "399006.SZ", "399001.SZ", "000300.SH", "000688.SH"]

# 存储/半导体/GPU
STORAGE = ["603986.SH", "301308.SZ", "688525.SH", "001309.SZ", "300475.SZ",
           "688256.SH", "688041.SH", "688008.SH"]
# CPO / 光通信
CPO = ["300308.SZ", "300502.SZ", "300394.SZ", "601869.SH", "688498.SH",
       "300570.SZ", "002281.SZ", "002396.SZ"]
# 军工
MIL = ["600760.SH", "000768.SZ", "600435.SH", "600685.SH", "002625.SZ",
       "688297.SH", "600893.SH", "002179.SZ", "600372.SH", "600150.SH",
       "688776.SH", "002389.SZ"]
# 人形机器人 / 端侧
ROBOT = ["688836.SH", "300124.SZ", "002472.SZ", "300450.SZ", "601689.SH",
         "603662.SH", "300718.SZ", "002527.SZ", "603893.SH", "688332.SH"]

STOCKS = STORAGE + CPO + MIL + ROBOT

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
}
IDX_NAMES = {"000001.SH": "上证指数", "399006.SZ": "创业板指",
              "399001.SZ": "深证成指", "000300.SH": "沪深300",
              "000688.SH": "科创50"}

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}


def get(u, tries=3):
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=25).read())
        except Exception as e:
            print(f"    [em ERR] {e}")
            time.sleep(1.5)
    return None


def retry(fn, n=4, **kw):
    for i in range(n):
        try:
            df = fn(**kw)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            if i == n - 1:
                print(f"    [ERR] {kw} {e}")
            time.sleep(1.5)
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


def board_constituents(bk):
    url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=500&po=1&np=1"
           f"&fltt=2&invt=2&fid=f3&fs=b:{bk}&fields=f2,f3,f12,f14,f62,f100")
    d = get(url)
    if not d or not d.get("data") or not d["data"].get("diff"):
        return []
    out = []
    for x in d["data"]["diff"]:
        code = x["f12"]
        if code.startswith("6"):
            tc = code + ".SH"
        elif code.startswith(("4", "8", "9")):
            tc = code + ".BJ"
        else:
            tc = code + ".SZ"
        out.append({"ts_code": tc, "name": x.get("f14"), "pct": x.get("f3"),
                    "price": x.get("f2"), "main_net": x.get("f62")})
    return out


def all_boards():
    url = ("https://push2.eastmoney.com/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1"
           "&fltt=2&invt=2&fid=f3&fs=m:90+t:3&fields=f2,f3,f12,f14,f62")
    out = []
    for pn in range(1, 8):
        d = get(url.format(pn=pn))
        if not d or not d.get("data") or not d["data"].get("diff"):
            break
        out += d["data"]["diff"]
        time.sleep(0.15)
    return out


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)

    data, last = {}, {}
    for c in INDEXES + STOCKS:
        df = fetch_daily(c)
        if df.empty:
            print(f"  [skip] {c}")
            continue
        data[c] = df.to_dict("records")
        r = df.iloc[-1]
        pc = df.iloc[-2]
        pct = (r["Close"] / pc["Close"] - 1) * 100
        last[c] = {"name": NAMES.get(c) or IDX_NAMES.get(c, c), "close": round(r["Close"], 2),
                   "pct": round(pct, 2), "high": round(r["High"], 2),
                   "low": round(r["Low"], 2), "open": round(r["Open"], 2),
                   "prev_close": round(pc["Close"], 2), "date": r["Date"],
                   "hi60": round(df["High"].tail(60).max(), 2),
                   "lo60": round(df["Low"].tail(60).min(), 2),
                   "ma5": round(df["Close"].rolling(5).mean().iloc[-1], 2),
                   "ma20": round(df["Close"].rolling(20).mean().iloc[-1], 2)}
        print(f"  [ok] {c:10s} {last[c]['name']:6s} {r['Close']:9.2f} {pct:+6.2f}%  "
              f"H {r['High']:.2f} L {r['Low']:.2f}  60dHi {last[c]['hi60']:.2f} "
              f"60dLo {last[c]['lo60']:.2f}")
        time.sleep(0.2)

    p = out_dir / "_daily_20261112.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    (out_dir / "_last_20261112.json").write_text(
        json.dumps(last, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] {p}  ({len(data)} 标的)")

    # ── 全市场宽度（单次全量）────────────────────────
    print("\n=== 全市场宽度 ===")
    breadth = {}
    for d in ["20261112", "20261111", "20261110"]:
        df = retry(pro.daily, trade_date=d)
        if df.empty:
            continue
        amt = df["amount"].sum() / 1e5  # 千元 → 亿元
        up = int((df["pct_chg"] > 0).sum())
        dn = int((df["pct_chg"] < 0).sum())
        fl = int((df["pct_chg"] == 0).sum())
        lt = int((df["pct_chg"] >= 9.9).sum())
        dt = int((df["pct_chg"] <= -9.9).sum())
        breadth[d] = {"amount_yi": round(amt, 1), "up": up, "down": dn, "flat": fl,
                      "limit_up": lt, "limit_down": dt, "n": int(len(df))}
        print(f"  {d}  成交额 {amt:,.0f} 亿  涨 {up} / 跌 {dn} / 平 {fl}  "
              f"涨9.9+ {lt}  跌9.9- {dt}  ({len(df)} 只)")
        time.sleep(0.3)
    (out_dir / "_breadth_20261112.json").write_text(
        json.dumps(breadth, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 板块：先找 board code，再取成分 ───────────────
    print("\n=== 板块 ===")
    boards = all_boards()
    bmap = {b["f14"]: b["f12"] for b in boards}
    keys = ["存储芯片", "CPO", "光通信", "军工", "人形机器人", "算力", "光模块",
            "半导体", "GPU", "AI眼镜", "端侧", "机器人", "光伏", "消费电子",
            "国防", "航天", "低空", "固态", "液冷", "铜缆"]
    found = {}
    for k in keys:
        for name, code in bmap.items():
            if k in name:
                found.setdefault(k, (name, code))
                break
    for k, (name, code) in found.items():
        print(f"  {k:10s} -> {name} ({code})")
    (out_dir / "_board_codes_20261112.json").write_text(
        json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")

    # 板块涨幅榜（前 30）
    top = sorted([b for b in boards if isinstance(b.get("f3"), (int, float))],
                 key=lambda b: -b["f3"])[:30]
    (out_dir / "_board_top_20261112.json").write_text(
        json.dumps([{"name": b["f14"], "code": b["f12"], "pct": b["f3"],
                     "main_net": b.get("f62")} for b in top],
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n  板块涨幅 TOP15：")
    for b in top[:15]:
        print(f"    {b['f14']:14s} {b['f3']:+6.2f}%")
