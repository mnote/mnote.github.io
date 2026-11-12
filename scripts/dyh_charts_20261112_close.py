"""都业华 2026-11-12 收评纪要 · K 线图生成（收盘版）

⛔ 只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。
K 线 = 前一交易日日线（Tushare 前复权）+ 今日收盘 K 线（新浪收盘快照）。
A股惯例红涨绿跌、白底；关键位全部放底部图例，不画在图内。
输出：~/workspace/mnote.github.io/charts/{code}_DY_20261112C.png
（用 C 后缀区分，不覆盖已上线的午评图 *_DY_20261112.png）
"""
import json
import os
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D
import mplfinance as mpf
import numpy as np
import pandas as pd
import tushare as ts

warnings.filterwarnings("ignore")

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_PREV = "#1f6feb", "#e11d48", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261112"
CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)
RPT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261112")
D = json.loads((RPT / "data_20261112_close.json").read_text(encoding="utf-8"))
SNAP_TIME = D["snapshot_time"][-5:]
Q = {r["名称"]: r for r in D["quotes"]}
IX = D["index"]

# 图清单：名称 -> (ts_code, 副标题, 关键位[(值,标签,颜色)])
SPEC = {
    "上证指数": ("000001.SH", "冲高回落收跌 · 最低 3647.44 创新低 · 压力 3750 未破", [
        (3750.0, "向上确认位", C_EXT),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "创业板指": ("399006.SZ", "冲高 2620 后回落收跌 2.44% · 全场最弱指数之一", [
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "药明康德": ("603259.SH", "收涨 1.10% · 最高 151.70 未触 157.8（= 11/10 最高价） · 结构仍不清晰", [
        (157.8, "上沿高点(三买门槛)", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中国船舶": ("600150.SH", "收涨 0.41% · 最低 33.90 破昨日低 33.92 · 未止跌（老师口径）", [
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "瑞芯微": ("603893.SH", "一路走低收跌 6.08% · 最低 220 远低于 248.49 · 未拉回", [
        (248.49, "三买确认位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "伊利股份": ("600887.SH", "相对抗跌收涨 1.27% · 最低 30.50 未破 30.46", [
        (30.46, "支撑位（跌破后拉回）", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中文在线": ("300364.SZ", "AI 视频 · 收跌 7.69% · 最高 29.49 未触 30.38 · 三买不成立", [
        (30.38, "前高突破位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "海天瑞声": ("688787.SH", "机器人 · 收跌 14.21% · 最低 121.31 · 对称震荡未形成", [
        (155.50, "60日高(10/26)", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "奥普特": ("688686.SH", "机器视觉 · 收跌 12.71% · 最低 151.38 · 距下沿 140 还差 7.5%", [
        (186.8, "突破位", C_EXT),
        (140.0, "回调目标位", C_EXT),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "柯力传感": ("603662.SH", "收跌 4.70% · 最低 54.61 未到 53 · 相对机器人板块抗跌", [
        (53.0, "11/05 低点支撑", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "兆易创新": ("603986.SH", "开盘冲高 273.68 后回落收跌 0.30% · 止损 252.85 未破", [
        (252.85, "止损参考(老师给)", C_EXT),
        (237.28, "11/09 新低", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "云铝股份": ("000807.SZ", "收跌 0.43% 且收在全天最低 · 距 60 日低 23.00 仅 1.3% · 缩量", [
        (23.0, "60日低(11/11)", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
    ]),
    "模塑科技": ("000700.SZ", "收跌 8.78% · 最高 16.99 未超昨收 17.09 · 最低 15.55 未到 14.95", [
        (14.95, "回调支撑位", C_EXT),
        (17.09, "昨收(顶分型未现)", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "汉威科技": ("300007.SZ", "顶分型已出现后继续下行 · 收跌 7.15% · 跌破 40", [
        (40.0, "整数关口", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "长盈精密": ("300115.SZ", "类二买 · 收跌 5.55% · 最高 30.39 未破 32.08", [
        (32.08, "突破位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
}


def fetch_daily(ts_code, days=60):
    is_index = ts_code in ("000001.SH", "399006.SZ", "399001.SZ", "000688.SH", "000300.SH")
    df = None
    for _ in range(4):
        try:
            df = pro.index_daily(ts_code=ts_code, start_date=START, end_date=END) if is_index \
                 else pro.daily(ts_code=ts_code, start_date=START, end_date=END)
            if df is not None and not df.empty:
                break
        except Exception as e:
            print("retry", ts_code, e)
        import time; time.sleep(1.5)
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    if not is_index:
        try:
            adj = pro.adj_factor(ts_code=ts_code, start_date=START, end_date=END).copy()
            adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
            adj = adj.sort_values("trade_date")
            df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
            df["adj_factor"] = df["adj_factor"].ffill().bfill()
            latest = df["adj_factor"].iloc[-1]
            for c in ("open", "high", "low", "close"):
                df[c] = df[c] * df["adj_factor"] / latest
        except Exception as e:
            print("adj fail", ts_code, e)
    df = df.tail(days).reset_index(drop=True).rename(columns={
        "trade_date": "Date", "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "vol": "Volume"})
    df["Volume"] = df["Volume"].astype(float)
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]


def compute_macd(df, fast=12, slow=26, signal=9):
    dif = df["Close"].ewm(span=fast, adjust=False).mean() - df["Close"].ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, (dif - dea) * 2


def resolve_levels(levels, df):
    out = []
    hi = float(df["High"].tail(60).max())
    lo = float(df["Low"].tail(60).min())
    for v, lbl, lc in levels:
        if v == "AUTO_HI":
            v = round(hi, 2)
        elif v == "AUTO_LO":
            v = round(lo, 2)
        out.append((float(v), lbl, lc))
    return out


def add_legend(fig, levels):
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}") for v, lbl, lc in levels]
    ncol = 1 if len(handles) <= 2 else 2
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False,
               fontsize=10, handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def snap_of(name):
    if name in Q:
        r = Q[name]
        return {"price": r["现价"], "high": r["最高"], "low": r["最低"], "open": r["开盘"],
                "prev": r["昨收"], "pct": r["涨跌幅%"], "vol": r["今日量(手)"]}
    if name in IX:
        s = IX[name]
        return {"price": s["price"], "high": s["high"], "low": s["low"], "open": s["open"],
                "prev": s["prev"], "pct": s["pct"], "vol": s["vol"] // 100}
    return None


def plot_one(name, ts_code, suffix, levels):
    df = fetch_daily(ts_code)
    if df.empty:
        print(f"[skip] {name}")
        return None
    # 窗口 60 根：与图例「60 日高 / 60 日低」口径一致（原来画 120 根却标 60 日，读者会以为图错）。
    # 数据口径统一：全部用 Tushare（11/12 收盘数据已出），不再拼新浪快照。
    # 原因：新浪 vol 与 Tushare index_daily vol 不同口径（上证相同、创业板指为深市全市场口径），
    # 且旧代码对指数做了 //100，导致今日那根成交量柱量纲错误（创业板爆高 5 倍、上证矮 100 倍）。
    s = snap_of(name)
    if s:
        tushare_close = float(df["Close"].iloc[-1])
        if abs(tushare_close - s["price"]) / s["price"] > 0.0005:
            print(f"[WARN] {name} 收盘价不一致: Tushare {tushare_close:.2f} vs 新浪 {s['price']:.2f}")
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])
    pct = (last_close / prev_close - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(marketcolors=mc, gridcolor=MC_GRID, gridstyle=":",
                               figcolor=MC_FACE, facecolor=MC_FACE,
                               rc={"axes.edgecolor": "#9ca3af", "axes.linewidth": 0.6,
                                   "font.family": "PingFang SC, Microsoft YaHei, Heiti SC, Hei, SimHei, sans-serif",
                                   "font.sans-serif": ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei"]})
    add_plots = [
        mpf.make_addplot(ma5, panel=0, color="#f59e0b", width=0.8),
        mpf.make_addplot(ma10, panel=0, color="#8b5cf6", width=0.8),
        mpf.make_addplot(ma20, panel=0, color="#0ea5e9", width=0.9),
        mpf.make_addplot(dif, panel=2, color="#f59e0b", width=1.0, ylabel="MACD"),
        mpf.make_addplot(dea, panel=2, color="#1d4ed8", width=1.0),
        mpf.make_addplot(macd.where(macd >= 0, other=np.nan), type="bar", panel=2, color=MC_UP),
        mpf.make_addplot(macd.where(macd < 0, other=np.nan), type="bar", panel=2, color=MC_DOWN),
    ]
    title = (f"{name} {ts_code} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-12 收盘 K 线）\n"
             f"{suffix} · 收 {last_close:.2f} ({pct:+.2f}%)")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                          figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                          title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax_main = axes[0]
    for v, lbl, lc in levels:
        ax_main.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax_main.axhline(prev_close, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    out = CHART_DIR / f"{ts_code.replace('.', '_')}_DY_20261112C.png"
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last_close:.2f} {pct:+.2f}%")
    return {"name": name, "code": ts_code, "close": round(last_close, 2),
            "pct": round(pct, 2), "file": out.name}


meta = []
for nm, (code, suffix, lv) in SPEC.items():
    r = plot_one(nm, code, suffix, lv)
    if r:
        meta.append(r)
(RPT / "charts_close.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False))
