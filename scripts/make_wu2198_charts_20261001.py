"""
wu2198 报告专用 K 线图生成器 — 2026-10-01 (国庆节第一天 · 周四 21:00)
数据截至: 9/30 节前最后交易日(10/1-10/8 国庆休市)
标的: 1 沪指 + 1 创业板 + 6 个股
- 兆易创新 603986 (存储芯片 — 博主 10/1 美光财报隐含新关注)
- 澜起科技 688008 (DDR5 内存接口芯片 — 存储芯片)
- 工商银行 601398 (银行/防御 — 博主 9/29 提肩带)
- 农业银行 601288 (银行/防御 — 博主 9/30 老登股)
- 恒瑞医药 600276 (创新药 — 博主 9/30 14:13 生物制品黑马)
- 百济神州 688235 (创新药出海 — 博主 9/30 医药局部上涨)

沿用博主关键位体系:
- 大盘 4258 / 4242 / 4036 / 3996 / 3926 / 3900 / 3886 / 3856 / 3842 / 3800 / 3764
- 创业板 4371 / 4018 / 3686 / 3590 / 3486 / 3370 / 3286 / 3220 / 3160 / 3135
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


def fetch_daily(ts_code: str, end_date: str = "20260930", days: int = 120) -> pd.DataFrame:
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

    title_suffix = " (9/30 收 · 国庆节第一天)"

    # 关键位定义(沿用博主关键位体系 + 9/30 实际收盘价)
    targets = [
        # 大盘沪指 — 沿用博主 8/4 关键位 + 9/30 收
        ("000001.SH", "上证指数",
         [(4258, "年大顶"),
          (4242, "120D高"),
          (4036, "60D高"),
          (3996, "8/29周高"),
          (3926, "8/26上沿"),
          (3900, "整数"),
          (3886, "B浪位"),
          (3856, "8/4支撑"),
          (3842.19, "9/30收"),
          (3800, "多方抵抗"),
          (3764, "60D低")],
         title_suffix),
        # 创业板 — 沿用博主 8/4 关键位
        ("399006.SZ", "创业板指",
         [(4371, "120D高"),
          (4018, "60D高"),
          (3686, "8/15前顶"),
          (3590, "目标位"),
          (3486, "B反位"),
          (3370, "反抽区"),
          (3286, "试破位"),
          (3220, "支撑"),
          (3160, "A杀位"),
          (3135.28, "9/30收")],
         title_suffix),
        # 存储芯片 (博主 10/1 美光财报隐含新关注) — 兆易创新
        ("603986.SH", "兆易创新",
         [(663.49, "60D高"),
          (485.05, "中线位"),
          (353.90, "9/30收"),
          (340.74, "60D低")],
         title_suffix),
        # 存储芯片 — 澜起科技 (DDR5 接口)
        ("688008.SH", "澜起科技",
         [(285.80, "60D高"),
          (235.00, "中线位"),
          (202.31, "9/30收"),
          (183.60, "60D低")],
         title_suffix),
        # 银行/防御 — 工商银行 (博主 9/29-9/30 提肩带)
        ("601398.SH", "工商银行",
         [(8.28, "9/30收"),
          (8.30, "60D高/压"),
          (7.50, "中线支"),
          (7.27, "60D低")],
         title_suffix),
        # 银行/防御 — 农业银行
        ("601288.SH", "农业银行",
         [(7.11, "60D高"),
          (6.97, "9/30收"),
          (6.50, "中线支"),
          (6.11, "60D低")],
         title_suffix),
        # 创新药 — 恒瑞医药 (博主 9/30 14:13 生物制品黑马)
        ("600276.SH", "恒瑞医药",
         [(58.00, "60D高"),
          (50.00, "压力"),
          (47.20, "9/30收"),
          (42.67, "60D低")],
         title_suffix),
        # 创新药出海 — 百济神州 (博主 9/30 14:08 老登股医药局部上涨)
        ("688235.SH", "百济神州",
         [(300.30, "60D高"),
          (270.00, "压力"),
          (264.41, "9/30收"),
          (247.30, "60D低")],
         title_suffix),
    ]
    for ts_code, name, levels, suf in targets:
        out = out_dir / f"{ts_code.replace('.', '_')}_20261001.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
            import traceback
            traceback.print_exc()
    print("[charts] done.")