"""都业华 2026-11-13 收评 · K 线图（日线，红涨绿跌，白底，关键位只画虚线+底部图例）
数据：reports/duyiehua-20261113/data_20261113.json（东财日线 前复权 160 根）
输出：charts/{code}_DY_20261113.png
"""
import json, warnings
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D
import mplfinance as mpf
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261113"
D = json.loads((RPT / "data_20261113.json").read_text(encoding="utf-8"))
SER = D["series"]
CHART_DIR = REPO / "charts"

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_SUP, C_PREV = "#1f6feb", "#e11d48", "#7c3aed", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try: fm.fontManager.addfont(fp)
    except Exception: pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

SPEC = {
    "上证指数": (None, "破前日低 3647.44 · 收于全天低位区 · 3750 未触", [
        (3750.0, "向上确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": (None, "低开低走 · 距 60 日低仅 2.1% · 全天最弱", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "药明康德": ("603259_SH", "窄幅震荡后放量下跌 · 最高 150.38 未触 157.8", [
        (157.8, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中国船舶": ("600150_SH", "缩量小跌 · 最低 33.80 再破前低 · 未止跌", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "瑞芯微": ("603893_SH", "冲高 228 回落 · 前高 237.37 未过 · 缩量", [
        (237.37, "日线前高", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "伊利股份": ("600887_SH", "放量逆势向上 · 最高 31.75 = 60 日新高", [
        (31.75, "今日高点(60日新高)", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中文在线": ("300364_SZ", "逆势收红 · 最高 28.77 未触 30.38 · 仍在震荡区", [
        (30.38, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "海天瑞声": ("688787_SH", "大跌 · 最低 112.24 破 11/12 低点 · 缩量", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "奥普特": ("688686_SH", "小幅回落 · 最低 148.36 贴近 140 下沿", [
        (186.8, "三买门槛", C_EXT), (140.0, "中枢下沿", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "柯力传感": ("603662_SH", "缩量小跌 · 最低 53.81 · 未创新低", [
        (53.0, "回调支撑", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "兆易创新": ("603986_SH", "高开低走 · 最低 244.58 未破 237.28 前低", [
        (237.28, "11/09 前低", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
    "云铝股份": ("000807_SZ", "缩量再跌 · 最低 22.95 = 60 日新低", [
        (22.95, "今日低点(60日新低)", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
    "模塑科技": ("000700_SZ", "盘中触涨停 17.15 未封板 · 放量 1.4 倍", [
        (17.69, "前高(突破位)", C_EXT), (14.95, "回调支撑", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "长盈精密": ("300115_SZ", "缩量小跌 · 最高 29.66 未破 32.08", [
        (32.08, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
}


def to_df(name):
    rows = SER[name][-60:]
    df = pd.DataFrame(rows).rename(columns={"d": "Date", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
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
        if v == "AUTO_HI": v = round(hi, 2)
        elif v == "AUTO_LO": v = round(lo, 2)
        out.append((float(v), lbl, lc))
    return out


def add_legend(fig, levels):
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}") for v, lbl, lc in levels]
    fig.legend(handles=handles, loc="lower center", ncol=1 if len(handles) <= 2 else 2,
               frameon=False, fontsize=10, handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def plot_one(name, key, suffix, levels):
    df = to_df(name)
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last, prev = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    pct = (last / prev - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE,
                               facecolor=MC_FACE,
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
    title = (f"{name} {key or ''} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-13 收盘）\n"
             f"{suffix} · 收 {last:.2f} ({pct:+.2f}%)")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                         figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                         title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax = axes[0]
    for v, lbl, lc in levels:
        ax.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax.axhline(prev, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout(); fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    fname = f"{key or ('000001_SH' if name == '上证指数' else '399006_SZ')}_DY_20261113.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "close": round(last, 2), "pct": round(pct, 2), "file": out.name}


meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print("done", len(meta))
