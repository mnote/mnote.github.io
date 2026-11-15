"""都业华 2026-11-14（周六）周末直播 · 日线数据采集（Tushare，无分钟级接口）
输出 reports/duyiehua-20261114/data_20261114.json
"""
import json, os, time
from pathlib import Path
import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
OUTDIR = REPO / "reports/duyiehua-20261114"
OUTDIR.mkdir(parents=True, exist_ok=True)
DATE = "20261113"          # 最近交易日 = 11/13 周五
START = "20260601"         # 日线窗口起点（>60 个交易日）

tok = os.environ.get("TUSHARE_TOKEN") or open(os.path.expanduser("~/.tushare_token")).read().strip()
ts.set_token(tok)
pro = ts.pro_api()

IDX = {"上证指数": "000001.SH", "深证成指": "399001.SZ", "创业板指": "399006.SZ",
       "沪深300": "000300.SH", "科创50": "000688.SH"}

# 本期直播点名的标的（按老师给出的可执行价格判据排序）
STOCKS = {
    "海天瑞声": "688787.SH",     # 止损 107.2 / 100（成本 112.9）
    "凯莱英": "002821.SZ",       # 支撑 144.39；止损 106/100；反弹 132 减成本
    "国电南瑞": "600406.SH",     # 跌破 22.8 走；中枢上沿为压力
    "银之杰": "300085.SZ",       # 涨停价 20.26 为 plan B 减仓位
    "工业富联": "601138.SH",     # 未止跌，小背驰后创新低 → 止损离场
    "华能国际": "600011.SH",     # 前高 7.49 止损
    "华峰测控": "688200.SH",     # 247 卖 / 50 接回（倒差价）
    "东方盛虹": "000301.SZ",     # 三卖成立 → 找机会减
    "华胜天成": "600410.SH",     # 成本 113.2，只做反弹不追趋势
    "当升科技": "300073.SZ",     # 双盲测试揭晓标的
    "晨光股份": "603899.SH",     # 套 20 点，压力在缺口
    "斯迪克": "300806.SZ",       # 阴线 15 个点，两档止损
    "星辰科技": "920885.BJ",     # 成本 118，跌穿减
    "宁德时代": "300750.SZ",     # 成本 270，看能否组织起那一波
    "双环传动": "002472.SZ",     # 下影线处放止损，机器人题材前提
    "南大光电": "300346.SZ",     # 底仓不保险，等站住
    "寒武纪": "688256.SH",       # 小底背驰但明显压力，不推荐买
    "天孚通信": "300394.SZ",     # 深套，倒差价
    "东材科技": "601208.SH",     # 玻纤反弹弱，过不去就主动走
    "春风动力": "603129.SH",     # 历史新高 329.66；成交额需 >10 亿
    "美格智能": "002881.SZ",     # 新开仓止损 41.6 / 40.67
    "三花智控": "002249.SZ",     # 机器人；周三 45 买，跌破下沿走
    "中际旭创": "300308.SZ",     # 算力；220 卖 / 181-188 接回
    "新风光": "688663.SH",       # 备选对照（字幕「新风动力」）
}


def fetch(code, api="daily"):
    for i in range(4):
        try:
            if api == "daily":
                df = pro.daily(ts_code=code, start_date=START, end_date=DATE)
            else:
                df = pro.index_daily(ts_code=code, start_date=START, end_date=DATE)
            if df is None or len(df) == 0:
                raise RuntimeError("empty")
            df = df.sort_values("trade_date").reset_index(drop=True)
            return df
        except Exception as e:
            print("  retry", code, str(e)[:70], flush=True)
            time.sleep(1.0 + i)
    return None


def summarize(df, close_col="close"):
    if df is None or len(df) == 0:
        return None
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    w60 = df.tail(60)
    w20 = df.tail(20)
    w5 = df.tail(5)
    amt_col = "amount" if "amount" in df.columns else None
    vol_col = "vol" if "vol" in df.columns else None
    return {
        "date": last["trade_date"],
        "open": round(float(last["open"]), 3),
        "high": round(float(last["high"]), 3),
        "low": round(float(last["low"]), 3),
        "close": round(float(last[close_col]), 3),
        "prev_close": round(float(prev[close_col]), 3),
        "pct": round(float(last["pct_chg"]), 2) if "pct_chg" in df.columns else None,
        "vol": float(last[vol_col]) if vol_col else None,
        "amount": round(float(last[amt_col]) / 1e5, 2) if amt_col else None,   # 千元 -> 亿元
        "hi60": round(float(w60["high"].max()), 3),
        "lo60": round(float(w60["low"].min()), 3),
        "vol_ma5": round(float(w5[vol_col].mean()), 0) if vol_col else None,
        "vol_ma20": round(float(w20[vol_col].mean()), 0) if vol_col else None,
    }


def series(df, close_col="close"):
    return [{"d": r["trade_date"], "o": float(r["open"]), "h": float(r["high"]),
             "l": float(r["low"]), "c": float(r[close_col]),
             "v": float(r["vol"]) if "vol" in r else 0.0}
            for _, r in df.iterrows()]


res = {"date": DATE, "index": {}, "stocks": {}, "series": {}}

for name, code in IDX.items():
    df = fetch(code, "index_daily")
    s = summarize(df)
    res["index"][name] = s
    res["series"][name] = series(df)
    print("IDX", name, s and s["close"], s and s["pct"], flush=True)
    time.sleep(0.25)

for name, code in STOCKS.items():
    df = fetch(code)
    s = summarize(df)
    if s:
        s["code"] = code.split(".")[0]
        res["stocks"][name] = s
        res["series"][name] = series(df)
    print("STK", name, code, s and s["close"], s and s["pct"],
          "H", s and s["high"], "L", s and s["low"], flush=True)
    time.sleep(0.25)

# 全市场宽度（11/13）
try:
    df = pro.daily(trade_date=DATE)
    res["breadth"] = {
        "n": int(len(df)),
        "up": int((df["pct_chg"] > 0).sum()),
        "down": int((df["pct_chg"] < 0).sum()),
        "flat": int((df["pct_chg"] == 0).sum()),
        "limit_up_98": int((df["pct_chg"] >= 9.8).sum()),
        "limit_dn_98": int((df["pct_chg"] <= -9.8).sum()),
        "amount_yi": round(float(df["amount"].sum()) / 1e5, 1),
    }
    print("BREADTH", res["breadth"], flush=True)
except Exception as e:
    print("breadth fail", e, flush=True)

(OUTDIR / "data_20261114.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", OUTDIR / "data_20261114.json")
