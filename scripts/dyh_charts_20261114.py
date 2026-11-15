"""都业华 2026-11-14（周六）周末直播纪要 · K 线图（日线，红涨绿跌，白底，关键位只画虚线+底部图例）
数据：reports/duyiehua-20261114/data_20261114.json（Tushare 日线，前复权）
输出：charts/{code}_DY_20261114.png
"""
import json, warnings, urllib.request
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
RPT = REPO / "reports/duyiehua-20261114"
D = json.loads((RPT / "data_20261114.json").read_text(encoding="utf-8"))
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


def sina_gold():
    """沪金连续 AU0 日线（新浪内盘期货）"""
    url = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_AU0=/"
           "InnerFuturesNewService.getDailyKLine?symbol=AU0")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                               "Referer": "https://finance.sina.com.cn"})
    txt = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
    arr = json.loads(txt[txt.find("(") + 1:txt.rfind(")")])
    rows = [{"d": r["d"], "o": float(r["o"]), "h": float(r["h"]), "l": float(r["l"]),
             "c": float(r["c"]), "v": float(r["v"])} for r in arr if r["d"] <= "2026-11-13"]
    SER["沪金连续"] = rows
    print("[gold] rows", len(rows), "last", rows[-1])
    return rows


SPEC = {
    "上证指数": (None, "缩量阴跌 · 最低 3623.84 破前低 · 3750 未触", [
        (3750.0, "向上确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": (None, "最弱 · 距 60 日低 2376.28 仅 2.1%", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "海天瑞声": ("688787_SH", "两连阴 · 收 114.00 仍高于 107.2 第一档止损", [
        (107.2, "第一档止损", C_EXT), (100.0, "第二档止损", C_SUP), ("AUTO_HI", "60日高", C_BLOG)]),
    "凯莱英": ("002821_SZ", "低 146.85 未破 144.39 支撑 · 成本 134.4 被套", [
        (144.39, "支撑位(破=跌穿)", C_SUP), (100.0, "止损参考", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "国电南瑞": ("600406_SH", "抗跌收红 · 最低 22.93 距 22.8 离场线仅 0.13 元", [
        (22.8, "跌破离场线", C_EXT), ("AUTO_HI", "60日高", C_SUP)]),
    "银之杰": ("300085_SZ", "高位回落 · 收 27.10 远高于 20.26 减仓位", [
        (20.26, "planB减仓位", C_EXT), ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "华峰测控": ("688200_SH", "收 226.52 已进入 227 接回区 · 高 250.94", [
        (247.0, "卖出价", C_EXT), (227.0, "接回区(20元差价)", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "工业富联": ("601138_SH", "再创新低 39.81 · -7.50% · 未止跌", [
        ("AUTO_LO", "60日低(新低)", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
    "当升科技": ("300073_SZ", "双盲测试标的 · 收 32.39 贴近 60 日低 31.96", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "华胜天成": ("600410_SH", "涨停 +10.00% · 成本 11.32 → 老师口径只做反弹止盈", [
        (11.32, "成本位", C_BLOG), (14.30, "涨停价(止盈区)", C_EXT), ("AUTO_LO", "60日低", C_SUP)]),
    "华能国际": ("600011_SH", "高 7.88 = 60 日新高 · 已越过 7.49 前高", [
        (7.49, "前高", C_SUP), ("AUTO_HI", "60日高", C_EXT)]),
    "斯迪克": ("300806_SZ", "单日 -14.64% · 自 11/10 高 48.84 回落 20%", [
        (48.84, "11/10高点", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "美格智能": ("002881_SZ", "新买标的 · 收 41.94 低 41.73 · 41.6 止损未破", [
        (41.6, "止损位", C_EXT), (40.67, "防假突破", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "沪金连续": ("AU0", "三连阴 · 873.30 → 852.50 → 839.00 · 未止跌", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
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
    fname = f"{key or ('000001_SH' if name == '上证指数' else '399006_SZ')}_DY_20261114.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "code": key, "close": round(last, 2), "pct": round(pct, 2), "file": out.name}


sina_gold()
meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
D["series"]["沪金连续"] = D["series"]["沪金连续"][-60:]      # 落盘只留 60 根，避免 json 膨胀
(RPT / "data_20261114.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
print("done", len(meta))
