"""导出 11/12 收评版 K 线图的数据底座（日线序列 + 关键位），供 JS 交互式 K 线组件使用。

⛔ 只用日线，不调用任何分钟级 K 线、不调用 czsc。
输出：reports/duyiehua-20261112/kline_data.json
结构：
{
  "meta": {"date": "2026-11-12", "source": "Tushare daily / index_daily（前复权）"},
  "series": {
     "603259.SH": {"name": "药明康德", "levels": [{"v":157.8,"label":"上沿高点(三买门槛)","color":"#e11d48"}],
                   "bars": [{"d":"2026-03-01","o":..,"h":..,"l":..,"c":..,"v":..,"ma5":..,"ma10":..,"ma20":..,
                             "dif":..,"dea":..,"macd":..}, ...]}
  }
}
"""
import json
import os
from pathlib import Path

import pandas as pd
import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261112"
D = json.loads((RPT / "data_20261112_close.json").read_text(encoding="utf-8"))
Q = {r["名称"]: r for r in D["quotes"]}
IX = D["index"]

pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN",
                                "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
START, END = "20260101", "20261111"
BARS = 120

MC_UP, MC_DOWN = "#e63946", "#2a9d8f"
C_BLOG, C_EXT = "#1f6feb", "#e11d48"

# 关键位（与收盘版 PNG 图例一一对应）：(值, 标签, 颜色)
SPEC = {
    "000001.SH": ("上证指数", [(3750.0, "向上确认位", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "399006.SZ": ("创业板指", [("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "603259.SH": ("药明康德", [(157.8, "上沿高点(三买门槛)", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "600150.SH": ("中国船舶", [("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "603893.SH": ("瑞芯微", [(248.49, "三买确认位", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "600887.SH": ("伊利股份", [(30.46, "支撑位(跌破后拉回)", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "300364.SZ": ("中文在线", [(30.38, "前高突破位", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "688787.SH": ("海天瑞声", [(155.50, "60日高(10/26)", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "688686.SH": ("奥普特", [(186.8, "突破位", C_EXT), (140.0, "回调目标位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "603662.SH": ("柯力传感", [(53.0, "11/05 低点支撑", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "603986.SH": ("兆易创新", [(252.85, "止损参考(老师给)", C_EXT), (237.28, "11/09 新低", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "000807.SZ": ("云铝股份", [(23.0, "60日低(11/11)", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
    "000700.SZ": ("模塑科技", [(14.95, "回调支撑位", C_EXT), (17.09, "昨收(顶分型未现)", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "300007.SZ": ("汉威科技", [(40.0, "整数关口", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "300115.SZ": ("长盈精密", [(32.08, "突破位", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
}
IDX_CODES = ("000001.SH", "399006.SZ")


def fetch(ts_code):
    is_idx = ts_code in IDX_CODES
    df = (pro.index_daily if is_idx else pro.daily)(ts_code=ts_code, start_date=START, end_date=END)
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    if not is_idx:
        adj = pro.adj_factor(ts_code=ts_code, start_date=START, end_date=END).copy()
        adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
        adj = adj.sort_values("trade_date")
        df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
        df["adj_factor"] = df["adj_factor"].ffill().bfill()
        latest = df["adj_factor"].iloc[-1]
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] * df["adj_factor"] / latest
    df = df.rename(columns={"trade_date": "d", "open": "o", "high": "h", "low": "l", "close": "c", "vol": "v"})
    return df[["d", "o", "h", "l", "c", "v"]].tail(BARS).reset_index(drop=True)


def today_bar(ts_code, name):
    """今日 K 线来自新浪收盘快照（与 PNG 图保持同一根）"""
    if ts_code in IDX_CODES:
        s = IX[name]
        return {"d": pd.Timestamp("2026-11-12"), "o": s["open"], "h": s["high"], "l": s["low"], "c": s["price"], "v": s["vol"]}
    r = Q[name]
    return {"d": pd.Timestamp("2026-11-12"), "o": r["开盘"], "h": r["最高"], "l": r["最低"], "c": r["现价"], "v": r["今日量(手)"]}


out = {"meta": {"date": "2026-11-12", "source": "Tushare daily/index_daily 前复权 + 新浪收盘快照",
                "up": MC_UP, "down": MC_DOWN}, "series": {}}

for code, (name, levels) in SPEC.items():
    df = fetch(code)
    bars = df.to_dict("records")
    bars.append(today_bar(code, name))
    d = pd.DataFrame(bars)
    for n, key in ((5, "ma5"), (10, "ma10"), (20, "ma20")):
        d[key] = d["c"].rolling(n).mean().round(3)
    ema12 = d["c"].ewm(span=12, adjust=False).mean()
    ema26 = d["c"].ewm(span=26, adjust=False).mean()
    d["dif"] = (ema12 - ema26).round(3)
    d["dea"] = d["dif"].ewm(span=9, adjust=False).mean().round(3)
    d["macd"] = ((d["dif"] - d["dea"]) * 2).round(3)
    d["d"] = d["d"].dt.strftime("%Y-%m-%d")
    bars = d.round(3).to_dict("records")
    for b in bars:
        for k in ("ma5", "ma10", "ma20", "dif", "dea", "macd"):
            if pd.isna(b[k]):
                b[k] = None
    hi60 = d["h"].tail(60).max()
    lo60 = d["l"].tail(60).min()
    lv = []
    for v, lbl, lc in levels:
        if v == "AUTO_HI":
            v = round(float(hi60), 2)
        elif v == "AUTO_LO":
            v = round(float(lo60), 2)
        lv.append({"v": float(v), "label": lbl, "color": lc})
    out["series"][code] = {"name": name, "levels": lv, "bars": bars}
    print(f"[kline] {name} {code} bars={len(bars)} last={bars[-1]['c']}")

(RPT / "kline_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("written:", RPT / "kline_data.json", round((RPT / "kline_data.json").stat().st_size / 1024), "KB")
