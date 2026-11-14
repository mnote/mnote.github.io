"""板块对比页 K 线（半导体/GPU/算力/CPO/存储/端侧/机器人 各一只代表 + 上证指数）。

红涨绿跌（A 股惯例）、白底、MACD、关键位虚线 + 底部图例。
数据：charts/_daily_20261113.json（东财/Tushare 前复权 130 根），缺的长鑫科技现拉并回写。

用法： python3 scripts/charts_sector_compare_20261113.py
输出： charts/{code}_SC_20261113.png
"""
import json
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
import mplfinance as mpf
import tushare as ts
import os

warnings.filterwarnings("ignore")
REPO = Path("/Users/maoling/workspace/mnote.github.io")
CHART_DIR = REPO / "charts"
DAILY = CHART_DIR / "_daily_20261113.json"
TOKEN = os.environ.get("TUSHARE_TOKEN") or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT = "#1f6feb", "#e11d48"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei",
                                     "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

# 名称, 代码, 图注, 关键位[(值或AUTO_HI/AUTO_LO, 标签, 颜色)]
SPEC = [
    ("上证指数", "000001.SH", "缩量阴跌 · 3634.35 · 3750 仍未触", [
        (3750.0, "向上确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    ("长鑫科技", "688825.SH", "缩量回调 · PE 19.5 · 距 60 日高 -35%", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    ("寒武纪", "688256.SH", "逆势翻红 +0.60% · GPU 端抗跌核心", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    ("中际旭创", "300308.SZ", "放量跌 8.39% · 距 60 日高 -54% · PE 21", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    ("天孚通信", "300394.SZ", "跌 10.94% · CPO 中游杀跌最深一档", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    ("江波龙", "301308.SZ", "存储模厂 · PE 6.7 周期底部定价", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    ("瑞芯微", "603893.SH", "端侧 SoC 龙头 · 距前高 237.37 仅 -8.2%", [
        (237.37, "日线前高", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    ("宇树科技", "688836.SH", "次新本体龙头 · PE 502 · 20 日 +63% 后回撤", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
]


def fetch_missing(ts_code, days=130):
    """补拉前复权日线（Tushare daily + adj_factor），返回 mpf 格式列表。"""
    pro = ts.pro_api(TOKEN)
    df = pro.daily(ts_code=ts_code, start_date="20260101", end_date="20261113")
    adj = pro.adj_factor(ts_code=ts_code, start_date="20260101", end_date="20261113")
    if df.empty or adj.empty:
        return []
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    adj = adj.copy()
    adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
    adj = adj.sort_values("trade_date")
    df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
    df["adj_factor"] = df["adj_factor"].ffill().bfill()
    latest = df["adj_factor"].iloc[-1]
    for c in ("open", "high", "low", "close"):
        df[c] = df[c] * df["adj_factor"] / latest
    df = df.tail(days)
    return [{"Date": d.strftime("%Y-%m-%d"), "Open": round(o, 2), "High": round(h, 2),
             "Low": round(l, 2), "Close": round(c, 2), "Volume": float(v)}
            for d, o, h, l, c, v in zip(df["trade_date"], df["open"], df["high"],
                                        df["low"], df["close"], df["vol"])]


def to_df(rows):
    df = pd.DataFrame(rows).rename(columns={"Date": "Date", "d": "Date", "o": "Open",
                                             "h": "High", "l": "Low", "c": "Close",
                                             "v": "Volume"})
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
    fig.legend(handles=handles, loc="lower center", ncol=1 if len(handles) <= 2 else 2,
               frameon=False, fontsize=10, handlelength=2.2, columnspacing=2.4,
               bbox_to_anchor=(0.5, 0.0))


def plot_one(name, code, suffix, levels):
    data = DAILY_DATA.get(code)
    if not data:
        print(f"  [fetch] {code}")
        data = fetch_missing(code)
        if data:
            DAILY_DATA[code] = data
    df = to_df(data[-60:])
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last, prev = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    pct = (last / prev - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK,
                                volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE,
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
    title = (f"{name} {code[:6]} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-13 收盘）\n"
             f"{suffix} · 收 {last:.2f} ({pct:+.2f}%)")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                          figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                          title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax = axes[0]
    for v, lbl, lc in levels:
        ax.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax.axhline(prev, color="#334155", linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    fname = f"{code.replace('.', '_')}_SC_20261113.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "code": code, "close": round(last, 2),
            "pct": round(pct, 2), "file": fname}


if __name__ == "__main__":
    DAILY_DATA = json.loads(DAILY.read_text(encoding="utf-8"))
    meta = []
    for nm, cd, sfx, lv in SPEC:
        meta.append(plot_one(nm, cd, sfx, lv))
        time.sleep(0.2)
    DAILY.write_text(json.dumps(DAILY_DATA, ensure_ascii=False), encoding="utf-8")
    rpt = REPO / "reports/sector-compare-20261113"
    rpt.mkdir(parents=True, exist_ok=True)
    (rpt / "charts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    print("done", len(meta))
