"""都业华 2026-11-09 收评纪要 · K 线图生成
日线（Tushare Pro，前复权）+ MACD + 成交量；A 股惯例红涨绿跌、白底
关键位：都业华原文点位 + 40 日高低
输出：~/workspace/mnote.github.io/charts/{code}_DY_20261109.png
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

for fp in ["/System/Library/Fonts/PingFang.ttc",
           "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261109"
INDEX_CODES = {"000001.SH", "399006.SZ", "399001.SZ", "000688.SH", "000300.SH"}

CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

# 名称 → (ts_code, 标签后缀, 关键位 [(值, 文字, 颜色)])
SPEC = {
    "药明康德": ("603259.SH", "大医药 · 等15分钟二买", [
        (151.0, "突破门槛（未站稳）", C_EXT),
        (171.2, "40日高", C_BLOG),
        (131.9, "40日低", C_BLOG),
    ]),
    "中国船舶": ("600150.SH", "等收复中枢上沿后做共振上涨中枢", [
        (41.43, "40日高", C_BLOG),
        (33.13, "40日低", C_BLOG),
    ]),
    "瑞芯微":   ("603893.SH", "端侧 AI · 前高附近横盘", [
        (228.74, "前高", C_EXT),
        (159.34, "40日低", C_BLOG),
    ]),
    "伊利股份": ("600887.SH", "大消费防守 · 加速上涨后调整", [
        (31.65, "40日高（加速上涨顶）", C_EXT),
        (25.86, "40日低", C_BLOG),
    ]),
    "江波龙":   ("301308.SZ", "存储 · 止损 208", [
        (208.0, "止损位", C_EXT),
        (368.0, "40日高", C_BLOG),
        (199.81, "40日低", C_BLOG),
    ]),
    "兆易创新": ("603986.SH", "存储 · 止损今日跌破", [
        (237.28, "今日低点（破位）", C_EXT),
        (413.43, "40日高", C_BLOG),
    ]),
    "海天瑞声": ("688787.SH", "人形机器人 · 141 未站住", [
        (141.0, "突破门槛", C_EXT),
        (155.5, "40日高", C_BLOG),
    ]),
    "华策影视": ("300133.SZ", "AI视频 · 冲高回落", [
        (11.04, "今日冲高（回落）", C_EXT),
        (6.89, "40日低", C_BLOG),
    ]),
    "云铝股份": ("000807.SZ", "非热点 · 等突破 25.91 / 站住 25.13", [
        (25.91, "突破位（稳健）", C_EXT),
        (25.13, "站住位（激进）", C_EXT),
        (29.13, "40日高", C_BLOG),
    ]),
    "上证指数": ("000001.SH", "15 分钟中枢 3664.40–3689.91 · 向上 3750 未确认突破", [
        (3750.0, "向上确认位", C_EXT),
        (3574.27, "40日低", C_BLOG),
    ]),
    "创业板指": ("399006.SZ", "15 分钟中枢 2529.73–2570.23 · 收盘位于中枢下方", [
        (3472.47, "40日高", C_BLOG),
        (2376.28, "40日低", C_BLOG),
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


def _spread(values, min_gap):
    out, prev = {}, None
    for v in values:
        y = v if prev is None else max(v, prev + min_gap)
        out[v] = y
        prev = y
    return out


def draw_levels(ax, levels):
    """图内只画虚线，不放文字框（避免遮挡 K 线与价格刻度）；关键位说明走底部图例。"""
    for v, lbl, lc in levels:
        ax.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)


def add_legend(fig, levels):
    """关键位图例：图底部居中，颜色与虚线一一对应。"""
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}")
               for v, lbl, lc in levels]
    ncol = 1 if len(handles) <= 2 else 2
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False,
               fontsize=10, handlelength=2.2, columnspacing=2.4,
               bbox_to_anchor=(0.5, 0.0))



def plot_one(name, ts_code, suffix, levels):
    df = fetch_daily(ts_code)
    if df.empty:
        print(f"[skip] {name}")
        return None
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
    draw_levels(ax_main, levels)
    # 昨收参考线
    ax_main.axhline(prev_close, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    out = CHART_DIR / f"{ts_code.replace('.', '_')}_DY_20261109.png"
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  close={last_close:.2f} {pct:+.2f}%")
    return {"name": name, "code": ts_code, "close": round(last_close, 2), "pct": round(pct, 2),
            "file": out.name}


meta = []
for nm, (code, suffix, lv) in SPEC.items():
    r = plot_one(nm, code, suffix, lv)
    if r:
        meta.append(r)

Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261109").mkdir(parents=True, exist_ok=True)
Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261109/charts.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False))
