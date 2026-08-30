"""
wu2198 报告专用 K 线图生成器 - 2026-08-30 周日版
基于最近一个交易日（8/28 周五）的市场环境
使用 wu2198 8/24-8/28 关键观点
"""
import os
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
import pandas as pd
import tushare as ts

# 颜色与样式（中国市场风格）
MC_UP = "#e63946"      # 红涨
MC_DOWN = "#2a9d8f"    # 绿跌
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_BBOX = "#dbeafe"

# 中文字体
for fp in [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

warnings.filterwarnings("ignore")

# tushare
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TUSHARE_TOKEN)


def fetch_daily(ts_code: str, days: int = 120) -> pd.DataFrame:
    """拉取日线（前复权）。指数用 index_daily，普通股用 daily。"""
    end = "20260830"
    start = "20260201"
    is_index = (
        (ts_code.endswith(".SH") and ts_code.startswith("000")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("399"))
    )
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
    else:
        df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
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
    df = df.rename(columns={
        "trade_date": "Date", "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "vol": "Volume"
    })
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


def draw_levels(ax, levels, color="#1d4ed8"):
    """画水平关键位虚线 + 居左文字标签"""
    for v, lbl in levels:
        ax.axhline(v, color=color, linestyle="--", linewidth=0.9, alpha=0.85, zorder=1)
        ax.text(
            -0.005, v, f"  {lbl} {v:g}  ",
            va="center", ha="right", fontsize=9, color="#1d4ed8",
            transform=ax.get_yaxis_transform(),
            bbox=dict(boxstyle="round,pad=0.25", fc=MC_BBOX, ec="#93c5fd", lw=0.6),
            zorder=5, clip_on=False,
        )


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 120, title: str = ""):
    df = fetch_daily(ts_code, days=days)
    if df.empty:
        print(f"  [skip] {ts_code} 无数据")
        return
    dif, dea, macd = compute_macd(df)

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
        title=title or f"{name} ({ts_code}) 日线 · K线 + MACD + 成交量",
        ylabel="价格", ylabel_lower="成交量",
        xrotation=0,
    )
    ax_main = axes[0]
    draw_levels(ax_main, levels)
    if levels:
        vs = [v for v, _ in levels]
        ylo, yhi = ax_main.get_ylim()
        pad = (max(vs) - min(vs)) * 0.05 if len(vs) > 1 else (yhi - ylo) * 0.1
        ax_main.set_ylim(min(min(vs) - pad, ylo), max(max(vs) + pad, yhi))

    ax_vol = axes[2]
    for i, (idx, row) in enumerate(df.iterrows()):
        c = MC_UP if row["Close"] >= row["Open"] else MC_DOWN
        ax_vol.patches[i].set_facecolor(c)
        ax_vol.patches[i].set_edgecolor(c)
        ax_vol.patches[i].set_alpha(0.85)

    ax_macd = axes[3]
    ax_macd.axhline(0, color="#9ca3af", linewidth=0.6, linestyle="-")

    # 现价标注
    last_close = df["Close"].iloc[-1]
    last_date = df.index[-1]
    ax_main.annotate(
        f"现价 {last_close:.2f}",
        xy=(last_date, last_close),
        xytext=(8, 0), textcoords="offset points",
        fontsize=10, color="#c1272d", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#fff8e1", ec="#c1272d", lw=0.8),
    )

    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线, 现价 {last_close:.2f})")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/wu2198_20260830_charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    # 关键位基于 wu2198 8/24-8/28 观点
    targets = [
        # 大盘 - 上证指数
        ("000001.SH", "上证指数",
         [(4256, "前高强压"), (3994, "B反阻力"), (3956, "8/27收"), (3926, "8/24区间底"),
          (3856, "关键支持"), (3800, "C浪极支"), (3767, "趋势线"), (3741, "趋势线")],
         "上证指数 (000001.SH) 日线 · 关键位标注（8/28收 3952.18）"),
        # 创业板 - 仅 wu2198 提到的位
        ("399006.SZ", "创业板指",
         [(3747, "B反顶试"), (3160, "B反起点")],
         "创业板指 (399006.SZ) 日线 · 关键位标注（8/28收 3458.31）"),
        # 科创 50 - 8/24 wu2198 给的关键位
        ("000688.SH", "科创50",
         [(2255, "M头左肩"), (2233, "M头右肩"), (1900, "M头目标"), (1549, "深跌目标"), (1274, "极端目标")],
         "科创50 (000688.SH) 日线 · wu2198 8/24 关键位标注（8/28收 1676）"),
        # 个股 6
        # 1. 西部黄金 - 黄金
        ("601069.SH", "西部黄金",
         [(40.0, "强压力"), (35.0, "压力"), (28.5, "支持"), (24.0, "强支持")],
         "西部黄金 (601069.SH) · 黄金 · 半年报+315.67% 净利润（8/28收 31.11）"),
        # 2. 中际旭创 - AI 算力光模块
        ("300308.SZ", "中际旭创",
         [(1500, "历史高"), (900, "强压力"), (550, "压力"), (400, "支持"), (300, "强支持")],
         "中际旭创 (300308.SZ) · AI光模块 · 半年报营收417.78亿(+182%)（8/28收 612.20）"),
        # 3. 天赐材料 - 锂电
        ("002709.SZ", "天赐材料",
         [(60.0, "强压力"), (45.0, "压力"), (30.0, "支持"), (22.0, "强支持")],
         "天赐材料 (002709.SZ) · 锂电 · 半年报营收147.10亿(+109%) 净利+967%（8/28收 36.50）"),
        # 4. 东山精密 - PCB / AI硬件
        ("002384.SZ", "东山精密",
         [(75.0, "强压力"), (55.0, "压力"), (35.0, "支持"), (25.0, "强支持")],
         "东山精密 (002384.SZ) · PCB/AI硬件 · 半年报营收277.98亿(+63.95%)（8/28收 51.40）"),
        # 5. 石头科技 - 智能制造
        ("688169.SH", "石头科技",
         [(175.0, "强压力"), (145.0, "压力"), (118.0, "支持"), (95.0, "强支持")],
         "石头科技 (688169.SH) · 扫地机器人 · 8/25 封20cm板（8/28收 128.60）"),
        # 6. 影石创新 - 全景相机
        ("688775.SH", "影石创新",
         [(175.0, "强压力"), (135.0, "压力"), (118.0, "支持"), (98.0, "强支持")],
         "影石创新 (688775.SH) · 全景相机 · AI影像主题（8/28收 119.30）"),
    ]
    for ts_code, name, levels, title in targets:
        suffix = ts_code.split(".")[0] + "_" + ts_code.split(".")[1]
        out = out_dir / f"20260830_{suffix}_{name}.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title=title)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
    print("[charts] done.")
