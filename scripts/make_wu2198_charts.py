"""
wu2198 报告专用 K 线图生成器
风格：日线 K线 + 成交量 + MACD，关键位水平虚线，标签居左（带 bbox）
白色底，涨绿跌红（中国市场风格）。
"""
import os
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
import pandas as pd
import tushare as ts

# ── 颜色与样式（中国市场风格）─────────────────────
MC_UP = "#e63946"      # 红涨
MC_DOWN = "#2a9d8f"    # 绿跌
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_TXT = "#111111"
MC_KEY = "#1f6feb"     # 关键位蓝色虚线
MC_BBOX = "#dbeafe"

# 中文字体（macOS 自带）
import matplotlib.font_manager as fm
# 强制注册系统字体
for fp in [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
# 优先顺序：苹方 → 微软雅黑 → 黑体 → SimHei
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

warnings.filterwarnings("ignore")

# ── tushare ────────────────────────────────────────
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TUSHARE_TOKEN)


def fetch_daily(ts_code: str, days: int = 120) -> pd.DataFrame:
    """拉取日线（前复权）。指数用 index_daily，普通股用 daily。"""
    end = pd.Timestamp.today().strftime("%Y%m%d")
    start = (pd.Timestamp.today() - pd.Timedelta(days=days * 2)).strftime("%Y%m%d")
    is_index = (
        (ts_code.endswith(".SH") and ts_code.startswith("000")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("399"))
    )  # 大盘指数（000xxx.SH 沪指/沪深300 等，399xxx.SZ 深成/创业板）
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
    else:
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    # 拉复权因子（指数不需要）
    if not is_index:
        try:
            adj = pro.adj_factor(ts_code=ts_code, start_date=start, end_date=end)
            if adj is not None and not adj.empty:
                adj = adj.sort_values("trade_date")
                df = df.merge(adj[["trade_date", "adj_factor"]], on="trade_date", how="left")
                df["adj_factor"] = df["adj_factor"].ffill().bfill()
                latest = df["adj_factor"].iloc[-1]
                for c in ("open", "high", "low", "close"):
                    df[c] = df[c] * df["adj_factor"] / latest
        except Exception:
            pass
    df = df.tail(days).reset_index(drop=True)
    df = df.rename(columns={"trade_date": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close", "vol": "Volume"})
    df["Volume"] = df["Volume"].astype(float)
    df = df.set_index("Date")
    return df[["Open", "High", "Low", "Close", "Volume"]]


def compute_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2
    return dif, dea, macd


def draw_levels(ax, levels, color=MC_KEY):
    """画水平关键位虚线 + 居左文字标签（用 transAxes 把标签贴到图左缘）"""
    ymin, ymax = ax.get_ylim()
    for v, lbl in levels:
        ax.axhline(v, color=color, linestyle="--", linewidth=0.9, alpha=0.85, zorder=1)
        # 居左文字（贴在图最左边）
        ax.text(
            -0.005, v, f"  {lbl} {v:g}  ",
            va="center", ha="right", fontsize=9, color="#1d4ed8",
            transform=ax.get_yaxis_transform(),  # x 为 axes 比例 0-1，y 为数据
            bbox=dict(boxstyle="round,pad=0.25", fc=MC_BBOX, ec="#93c5fd", lw=0.6),
            zorder=5, clip_on=False,
        )


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 120, title_suffix: str = ""):
    df = fetch_daily(ts_code, days=days)
    if df.empty:
        print(f"  [skip] {ts_code} 无数据")
        return
    dif, dea, macd = compute_macd(df)

    # 主图
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE, facecolor=MC_FACE,
        rc={
            "axes.edgecolor": "#9ca3af", "axes.linewidth": 0.6,
            "font.family": "PingFang SC, Microsoft YaHei, Heiti SC, Hei, SimHei, sans-serif",
            "font.sans-serif": ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei"],
        },
    )
    add_plots = [
        mpf.make_addplot(dif, panel=2, color="#f59e0b", width=1.0, ylabel="MACD"),
        mpf.make_addplot(dea, panel=2, color="#1d4ed8", width=1.0),
        mpf.make_addplot(macd, type="bar", panel=2, color=MC_UP, secondary_y=False),
    ]

    fig, axes = mpf.plot(
        df, type="candle", volume=True, mav=(5, 10, 20),
        addplot=add_plots, style=style,
        figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
        title=f"{name} ({ts_code}) 日线 · K线 + MACD + 成交量{title_suffix}",
        ylabel="价格", ylabel_lower="成交量",
        xrotation=0,
    )
    ax_main = axes[0]
    # 关键位居左：贴在图左缘（transAxes 坐标系）
    draw_levels(ax_main, levels)
    # 调整 y 轴留出关键位空间
    if levels:
        vs = [v for v, _ in levels]
        ylo, yhi = ax_main.get_ylim()
        pad = (max(vs) - min(vs)) * 0.05 if len(vs) > 1 else (yhi - ylo) * 0.1
        ax_main.set_ylim(min(min(vs) - pad, ylo), max(max(vs) + pad, yhi))

    # 美化成交量柱条颜色（继承涨跌色）
    ax_vol = axes[2]
    for i, (idx, row) in enumerate(df.iterrows()):
        c = MC_UP if row["Close"] >= row["Open"] else MC_DOWN
        ax_vol.patches[i].set_facecolor(c)
        ax_vol.patches[i].set_edgecolor(c)
        ax_vol.patches[i].set_alpha(0.85)

    # MACD 子图美化
    ax_macd = axes[3]
    ax_macd.axhline(0, color="#9ca3af", linewidth=0.6, linestyle="-")

    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线)")


# ── 主入口 ─────────────────────────────────────────
if __name__ == "__main__":
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wu2198_charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    title_suffix = " (8/14 收)"
    # 关键位定义（来自 8/14-8/15 博主原帖）
    targets = [
        # 大盘
        ("000001.SH", "上证指数",
         [(3741, "B反起点"), (3903, "周五试低"), (3927, "8/14 收"), (3956, "下周目标"), (4036, "压力位")],
         title_suffix),
        ("399006.SZ", "创业板指",
         [(3158, "A杀试B点"), (3626, "8/14 收"), (3686, "拓展目标")],
         title_suffix),
        # 个股 6
        ("603629.SH", "利通电子",
         [(87.26, "12日低"), (137.50, "8/14 涨停")],
         title_suffix),
        ("603881.SH", "数据港",
         [(20.00, "前低"), (29.04, "8/14 涨停")],
         title_suffix),
        ("300017.SZ", "网宿科技",
         [(10.00, "前低"), (17.33, "8/14 20cm")],
         title_suffix),
        ("300308.SZ", "中际旭创",
         [(700.00, "60D低"), (943.00, "8/14 收")],
         title_suffix),
        ("300502.SZ", "新易盛",
         [(300.00, "60D低"), (448.08, "8/14 收")],
         title_suffix),
        ("002463.SZ", "沪电股份",
         [(25.00, "60D低"), (50.00, "突破区")],
         title_suffix),
    ]
    for ts_code, name, levels, suf in targets:
        out = out_dir / f"{ts_code.split('.')[0]}_{ts_code.split('.')[1]}.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
    print("[charts] done.")
