"""都业华 2026-11-16 收评（高级班）· 收盘版 K 线图

⛔ 只用日线；红涨绿跌；关键位只画虚线 + 底部图例；标题两行。
数据：reports/duyiehua-20261116/data_20261116_close.json
输出：charts/{code}_DY_20261116C.png
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
RPT = REPO / "reports/duyiehua-20261116"
D = json.loads((RPT / "data_20261116_close.json").read_text(encoding="utf-8"))
SER, IX, ST = D["series"], D["index"], D["stocks"]
CHART_DIR = REPO / "charts"
SUF = "20261116C"

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


def snap(name):
    if name in ST:
        return ST[name]["snap"]
    return IX[name + "_sina"]


def desc(name, text):
    return text


# 名称: (图文件名主键, 结构描述, [(值 or AUTO_HI/AUTO_LO, 说明, 颜色)])
SPEC = {
    "上证指数": ("000001_SH", "创新低 3586.57 · 逼近 60 日低 3574 · 3750 未触", [
        (3750.0, "向上确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": ("399006_SZ", "冲高回落 -4.37% · 最低 2308.90 贴近 60 日低", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "药明康德": ("603259_SH", "低开破位 -1.29% · 最高 146.72 远未触 157.8 三买", [
        (157.8, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中国船舶": ("600150_SH", "逆势微红 +0.09% · 相对抗跌 · 但结构未止跌", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "瑞芯微": ("603893_SH", "跌破 208 至 206.89 · 收 208.60 · 等日线底分型", [
        (208.0, "回调目标位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "伊利股份": ("600887_SH", "逆势创新高 32.21 · +1.45% · 位置偏高不追", [
        (30.46, "前支撑", C_SUP), ("AUTO_HI", "60日高", C_BLOG)]),
    "中文在线": ("300364_SZ", "低开破位 -5.23% · 最低 25.56 回到 11/09 低点", [
        (30.38, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "海天瑞声": ("688787_SH", "低开破位 -6.89% · 最低 104.60 · 未止跌", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "奥普特": ("688686_SH", "触及 140 下沿 140.20 · 收 141.96 · 等底分型", [
        (186.8, "三买门槛", C_EXT), (140.0, "中枢下沿", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "柯力传感": ("603662_SH", "跌破 53 支撑至 51.10 · 收 52.52 · 未止跌", [
        (53.0, "回调支撑", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "兆易创新": ("603986_SH", "盘中触跌停 221.42 · 收 -9.27% · 继续创新低", [
        (237.28, "11/09 前低", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
    "模塑科技": ("000700_SZ", "低开重挫 -8.55% · 最低 15.06 距 14.95 差 0.11", [
        (14.95, "回调支撑", C_SUP), (17.69, "前高突破位", C_EXT)]),
    "长盈精密": ("300115_SZ", "低开破位 -5.93% · 最低 26.43 · 未止跌", [
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
    title = (f"{name} {key} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-16 收盘）\n"
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
    fname = f"{key}_DY_{SUF}.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "close": round(last, 2), "pct": round(pct, 2), "file": out.name}


meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts_close.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
print("done", len(meta))
