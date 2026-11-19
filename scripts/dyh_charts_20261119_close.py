"""都业华 2026-11-19 高级班收评 · K 线图（日线，红涨绿跌，白底，关键位只画虚线 + 底部图例）

数据：reports/duyiehua-20261119/data_close_20261119.json（Tushare 日线，前复权）
输出：charts/{key}_DY_20261119.png
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")
REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
D = json.loads((RPT / "data_close_20261119.json").read_text(encoding="utf-8"))
SER = D["series"]
CHART_DIR = REPO / "charts"

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_SUP, C_PREV = "#1f6feb", "#e11d48", "#7c3aed", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei",
                                    "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

# name: (图文件名主键, 结构描述, [(值 or AUTO_HI/AUTO_LO, 说明, 颜色)])
SPEC = {
    "上证指数": ("000001_SH", "探低回升收阴 · 最低 3547.94 创 60 日新低 · 3623 未收复", [
        (3623.12, "压力位", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": ("399006_SZ", "未创新低 · 最低 2271.99 距 60 日低 2263.74 差 0.36%", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "药明康德": ("603259_SH", "收在全天最高 +0.19% · 距 157.8 三买门槛差 13.41", [
        (157.8, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中国船舶": ("600150_SH", "缩量微跌 -0.03% · 最低 33.98 · 距 36.75 差 2.05", [
        (36.75, "上行确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "瑞芯微": ("603893_SH", "破位延续 -4.12% · 最低 187.87 · 底分型未出", [
        (220.7, "前确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "伊利股份": ("600887_SH", "逆势红盘 +1.61% · 最高 33.10 续创 60 日新高", [
        ("AUTO_HI", "60日高", C_BLOG), (30.46, "前支撑", C_SUP)]),
    "海天瑞声": ("688787_SH", "破位 -4.36% · 最低 86.50 · 未止跌", [
        (141.0, "突破门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "兆易创新": ("603986_SH", "弱势震荡 -0.34% · 未收复 233 · 未破 224.6", [
        (233.0, "站稳位", C_EXT), (224.6, "中枢上沿高点", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "华丰科技": ("688629_SH", "破位 -4.64% · 最低 94.30 · 无二买信号", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "中芯国际": ("688981_SH", "突破 117.3 与 120.6 收 +6.21% · 高 122.65", [
        (120.6, "回抽确认位", C_EXT), (117.3, "突破位", C_SUP)]),
    "常山北明": ("000158_SZ", "放大量 +4.83% · 冲高 13.50 回落 · 涨停次日", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "拓维信息": ("002261_SZ", "大幅调整 -9.35% · 最低 22.22 · 走势起不来", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "四川长虹": ("600839_SH", "放大量 +1.41% · 涨停次日涨幅收窄", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
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
    title = (f"{name} {key} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-19 收盘）\n"
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
    fname = f"{key}_DY_20261119.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "code": key, "close": round(last, 2), "pct": round(pct, 2),
            "file": out.name}


meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts_close.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
print("done", len(meta))
