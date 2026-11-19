"""都业华 2026-11-19 午评（高级班·午盘）· K 线图（日线，红涨绿跌，白底，关键位只画虚线+底部图例）

数据：reports/duyiehua-20261119/data_20261119.json（同花顺日线 + 13:2x 实时快照）
输出：charts/{code}_DY_20261119N.png
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")
REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
D = json.loads((RPT / "data_20261119.json").read_text(encoding="utf-8"))
SER = D["series"]
CHART_DIR = REPO / "charts"
SNAP = D.get("snapshot_time", "13:25")

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_SUP, C_PREV = "#1f6feb", "#e11d48", "#7c3aed", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

# name: (图文件名主键, 结构描述, [(值 or AUTO_HI/AUTO_LO, 说明, 颜色)])
SPEC = {
    "上证指数": ("000001_SH", "低开探底回升 · 最低 3547.94 创 60 日新低 · 3623 未收复", [
        (3750.0, "向上确认位", C_EXT), (3623.12, "压力位", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": ("399006_SZ", "弱势下探 · 最低 2271.99 距 60 日低 2263.74 仅 0.36%", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "药明康德": ("603259_SH", "再创短线新低 140.87 · 距 157.8 三买门槛差 16.93", [
        (157.8, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中国船舶": ("600150_SH", "弱势回落 -0.43% · 最低 33.98 · 未止跌", [
        (36.75, "上行确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "瑞芯微": ("603893_SH", "破位延续 -1.92% · 最低 187.87 · 底分型未出", [
        (220.7, "前确认位", C_EXT), (208.0, "回调目标位", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "伊利股份": ("600887_SH", "逆势红盘 +1.11% · 最高 32.97 续创 60 日新高", [
        ("AUTO_HI", "60日高", C_BLOG), (30.46, "前支撑", C_SUP)]),
    "海天瑞声": ("688787_SH", "破位 -2.51% · 最低 86.50 再破前低", [
        (141.0, "突破门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "奥普特": ("688686_SH", "弱势 -0.79% · 最低 126.64 · 破位待修复", [
        (140.0, "突破门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "柯力传感": ("603662_SH", "回落 -1.18% · 最低 45.75 · 未止跌", [
        (53.0, "突破门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中文在线": ("300364_SZ", "破位 -1.98% · 最低 22.51 · 三买远未到", [
        (30.38, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "兆易创新": ("603986_SH", "弱势震荡 -0.94% · 未收复 233 · 未止跌", [
        (233.0, "站稳位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "模塑科技": ("000700_SZ", "继续创新低 13.79 · 破 14.95 支撑 · 底分型未出", [
        (14.95, "回调支撑", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "长盈精密": ("300115_SZ", "下跌 -1.66% · 最低 22.53 · 无止跌", [
        (32.08, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
}


def to_df(name):
    rows = SER[name][-60:]
    df = pd.DataFrame(rows).rename(columns={"d": "Date", "o": "Open", "h": "High",
                                            "l": "Low", "c": "Close", "v": "Volume"})
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]


def compute_macd(df, fast=12, slow=26, signal=9):
    dif = df["Close"].ewm(span=fast, adjust=False).mean() - df["Close"].ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, (dif - dea) * 2


def resolve_levels(levels, df):
    hi, lo = float(df["High"].max()), float(df["Low"].min())
    out = []
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
    fig.legend(handles=handles, loc="lower center",
               ncol=1 if len(handles) <= 2 else 2, frameon=False, fontsize=10,
               handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def plot_one(name, key, suffix, levels):
    df = to_df(name)
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last, prev = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    pct = (last / prev - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE, facecolor=MC_FACE,
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
    title = (f"{name} {key} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-19 {SNAP} 盘中，未走完）\n"
             f"{suffix} · 收 {last:.2f} ({pct:+.2f}%)")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                         figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                         title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax = axes[0]
    for v, lbl, lc in levels:
        ax.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax.axhline(prev, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    fname = f"{key}_DY_20261119N.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "code": key, "close": round(last, 2), "pct": round(pct, 2), "file": out.name}


meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print("done", len(meta))
