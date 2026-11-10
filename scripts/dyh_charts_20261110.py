"""都业华 2026-11-10 收评纪要 · K 线图生成
日线（Tushare Pro，前复权）+ MACD + 成交量；A 股惯例红涨绿跌、白底
关键位：都业华 11/10 原文点位 + 40 日高低（AUTO 动态）
输出：~/workspace/mnote.github.io/charts/{code}_DY_20261110.png
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
MC_GRID, MC_FACE, MC_BBOX = "#e5e7eb", "#ffffff", "#dbeafe"
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
START, END = "20260101", "20261110"
INDEX_CODES = {"000001.SH", "399006.SZ", "399001.SZ", "000688.SH", "000300.SH"}
CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

SPEC = {
    "上证指数": ("000001.SH", "15 分钟下跌中枢 3664.40–3689.91 · 收盘跌破下沿 · 向上 3750 未确认", [
        (3750.0, "向上确认位", C_EXT),
        (3664.40, "15分钟中枢下沿", C_BLOG),
        (3653.05, "前低（11/09）", "#64748b"),
        ("AUTO_LO", "40日低", C_BLOG),
    ]),
    "创业板指": ("399006.SZ", "15 分钟中枢 2529.73–2570.23 · 收盘位于中枢下方", [
        (2529.73, "15分钟中枢下沿", C_BLOG),
        ("AUTO_HI", "40日高", C_BLOG),
        ("AUTO_LO", "40日低", C_BLOG),
    ]),
    "药明康德": ("603259.SH", "大医药 · 高开回落 · 等 15 分钟二买 + 日线底分型", [
        (151.0, "突破门槛（未站稳）", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中国船舶": ("600150.SH", "船舶 · 下跌中枢延伸 · 等收复上沿 35.58", [
        (35.58, "中枢上沿（未收复）", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "瑞芯微": ("603893.SH", "端侧 AI · 今日涨停 · 前高 248.49 为 2025-09 年线级高点", [
        (248.49, "年线级前高（2025-09-01）", C_EXT),
        (233.20, "今日涨停价", C_BLOG),
        (211.00, "今日低点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "伊利股份": ("600887.SH", "大消费防守 · 调整不充分 · 窄幅震荡", [
        (31.65, "60日高（加速上涨顶）", C_EXT),
        (30.74, "今日低点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "江波龙": ("301308.SZ", "存储 · 短线剔除跟踪 · 重设止损 208", [
        (208.0, "止损位", C_EXT),
        (225.95, "今日高点", "#64748b"),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "兆易创新": ("603986.SH", "存储 · 11/09 创 237.28 新低 · 等底背驰 / 三买", [
        (237.28, "11/09 新低（破位）", C_EXT),
        (248.88, "今日高点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "海天瑞声": ("688787.SH", "人形机器人 · 141 未站住 · 前高 155.50（10/26）", [
        (141.0, "突破门槛（未过）", C_EXT),
        (155.50, "前高（10/26）", C_BLOG),
        (138.00, "今日高点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "华策影视": ("300133.SZ", "AI 视频 · 触涨停未封 · 短线放弃剔除跟踪", [
        (11.64, "今日涨停价（未封住）", C_EXT),
        (9.75, "今日低点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "云铝股份": ("000807.SZ", "非热点 · 震荡向下 · 等突破 25.91 / 站住 25.13", [
        (25.91, "突破位（稳健）", C_EXT),
        (25.13, "站住位（激进）", C_EXT),
        (25.08, "今日高点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "万兴科技": ("300624.SZ", "AI 视频 · 作业候选 · 位置不高（距 60 日高 -11.3%）", [
        (59.77, "60日高", C_BLOG),
        (50.51, "今日低点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中文在线": ("300364.SZ", "AI 视频 · 作业候选 · 位置偏高（距 60 日高 -2.8%）", [
        (29.90, "60日高", C_BLOG),
        (29.83, "今日高点", "#64748b"),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
}


def fetch_daily(ts_code, days=120):
    is_index = ts_code in INDEX_CODES
    for _ in range(3):
        try:
            df = pro.index_daily(ts_code=ts_code, start_date=START, end_date=END) if is_index \
                 else pro.daily(ts_code=ts_code, start_date=START, end_date=END)
            if df is not None and not df.empty:
                break
        except Exception as e:
            print("retry", ts_code, e)
        import time; time.sleep(1)
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
        except Exception:
            pass
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
    hi = float(df["High"].tail(40).max())
    lo = float(df["Low"].tail(40).min())
    for v, lbl, lc in levels:
        if v == "AUTO_HI":
            v = round(hi, 2)
        elif v == "AUTO_LO":
            v = round(lo, 2)
        out.append((float(v), lbl, lc))
    return out


def add_legend(fig, levels):
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}")
               for v, lbl, lc in levels]
    ncol = 1 if len(handles) <= 2 else 2
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False,
               fontsize=10, handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def plot_one(name, ts_code, suffix, levels):
    df = fetch_daily(ts_code)
    if df.empty:
        print(f"[skip] {name}")
        return None
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
    title = (f"{name} {ts_code} · 日线 K线 + MACD + 成交量\n"
             f"{suffix} · 收 {last_close:.2f} ({pct:+.2f}%) · {df.index[-1].strftime('%Y-%m-%d')}")

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
    out = CHART_DIR / f"{ts_code.replace('.', '_')}_DY_20261110.png"
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  close={last_close:.2f} {pct:+.2f}%")
    return {"name": name, "code": ts_code, "close": round(last_close, 2), "pct": round(pct, 2), "file": out.name}


meta = []
for nm, (code, suffix, lv) in SPEC.items():
    r = plot_one(nm, code, suffix, lv)
    if r:
        meta.append(r)

Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261110").mkdir(parents=True, exist_ok=True)
Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261110/charts.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False))
