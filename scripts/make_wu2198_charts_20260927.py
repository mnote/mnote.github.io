"""
wu2198 报告专用 K 线图生成器 — 2026-09-27 (周日 21:00 · 中秋节最后一天)
数据截至: 9/24 节前最后交易日(9/25-9/27 中秋休市)
标的: 1 沪指 + 1 创业板 + 6 个股
- 沪电股份 002463 (PCB/AI 服务器)
- 生益科技 600183 (覆铜板)
- 中际旭创 300308 (光模块/CPO)
- 天孚通信 300394 (光器件)
- 恒瑞医药 600276 (创新药)
- 深南电路 002916 (PCB/封装基板)

沿用博主 8/4 关键位体系:
- 大盘 4256 / 3996 / 3926 / 3900 / 3886 / 3856 / 3824
- 创业板 3686 / 3590 / 3486 / 3286 / 3220 / 3160
"""
import os
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import tushare as ts

# ── 颜色与样式（中国市场风格：红涨绿跌）──────────────
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

# ── tushare ─────────────────────────────────────────
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TUSHARE_TOKEN)


def fetch_daily(ts_code: str, end_date: str = "20260924", days: int = 120) -> pd.DataFrame:
    is_index = (
        (ts_code.endswith(".SH") and ts_code.startswith("000")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("399"))
    )
    start_date = "20260201"
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    else:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    # 拉复权因子
    if not is_index:
        try:
            adj = pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
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


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 120, title_suffix: str = ""):
    df = fetch_daily(ts_code, days=days)
    if df.empty:
        print(f"  [skip] {ts_code} 无数据")
        return
    dif, dea, macd = compute_macd(df)
    last_close = df["Close"].iloc[-1]
    last_date = df.index[-1].strftime("%Y-%m-%d")

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

    title = f"{name} ({ts_code.replace('.', '_')}) 日线 · K线 + MACD + 成交量{title_suffix} · 收 {last_close:.2f} ({last_date})"

    fig, axes = mpf.plot(
        df, type="candle", volume=True, mav=(5, 10, 20),
        addplot=add_plots, style=style,
        figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
        title=title,
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

    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线, 收 {last_close:.2f})")


# ── 主入口 ─────────────────────────────────────────
if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    title_suffix = " (9/24 收 · 中秋最后一天)"

    # 关键位定义(沿用博主 8/4 体系 + 系统识别 MA/60D 高低)
    targets = [
        # 大盘沪指 — 沿用博主 8/4 关键位
        ("000001.SH", "上证指数",
         [(4256, "8/15前顶"),
          (3996, "8/29周高"),
          (3926, "8/26上沿"),
          (3900, "整数"),
          (3888.37, "9/24收"),
          (3886, "B浪位"),
          (3856, "8/4支撑"),
          (3824, "多空线")],
         title_suffix),
        # 创业板 — 沿用博主 8/4 关键位
        ("399006.SZ", "创业板指",
         [(3686, "8/15前顶"),
          (3590, "目标位"),
          (3486, "B反位"),
          (3414, "8/26收"),
          (3370, "反抽"),
          (3322, "9/11收"),
          (3288.95, "9/24收"),
          (3286, "试破位"),
          (3220, "支撑"),
          (3160, "A杀位")],
         title_suffix),
        # PCB/AI 服务器 — 沪电股份 (博主 8/4 关注)
        ("002463.SZ", "沪电股份",
         [(94.73, "60D低"),
          (115.00, "支撑"),
          (124.05, "9/24收"),
          (140.00, "压力"),
          (142.99, "60D高")],
         title_suffix),
        # 覆铜板 — 生益科技 (博主 8/4 直接点名)
        ("600183.SH", "生益科技",
         [(97.51, "60D低"),
          (130.00, "支撑"),
          (137.33, "9/24收"),
          (170.00, "压力"),
          (166.21, "60D高")],
         title_suffix),
        # 光模块/CPO — 中际旭创 (1.6T 龙头)
        ("300308.SZ", "中际旭创",
         [(793.03, "60D低"),
          (820.00, "支撑"),
          (895.86, "9/24收"),
          (1000.00, "压力"),
          (1218.00, "60D高")],
         title_suffix),
        # 光器件平台 — 天孚通信
        ("300394.SZ", "天孚通信",
         [(155.55, "60D低"),
          (220.00, "支撑"),
          (267.93, "9/24收"),
          (295.00, "60D高"),
          (300.00, "压力")],
         title_suffix),
        # 创新药 — 恒瑞医药 (博主 8/4 关注)
        ("600276.SH", "恒瑞医药",
         [(36.36, "8/4底"),
          (41.89, "60D低"),
          (44.86, "9/24收"),
          (50.00, "压力"),
          (58.00, "60D高")],
         title_suffix),
        # PCB/封装基板 — 深南电路 (博主 8/4 关注)
        ("002916.SZ", "深南电路",
         [(284.41, "60D低"),
          (394.50, "9/24收"),
          (440.00, "压力"),
          (465.41, "60D高")],
         title_suffix),
    ]
    for ts_code, name, levels, suf in targets:
        out = out_dir / f"{ts_code.replace('.', '_')}_20260927.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
            import traceback
            traceback.print_exc()
    print("[charts] done.")
