"""
wu2198 报告专用 K 线图生成器 — 2026-10-06 (周二 21:00 · 🇨🇳 国庆假期倒数第 2 天)
博主最近一天(10/05 + 10/06)新增信号:
- 🟢 10/06 06:45 #中国空心光纤网速更快了#利好什么板块？(板块提问 → 光通信/光模块)
- 🟡 10/06 06:45 #未来几年能留住现金流最重要#(风控/防御)
- ⚪ 10/06 12:38 "过两天大A就营业了"(节后 10/8 周三开盘提示)

沿用主线(10/03 + 10/02 + 10/01 + 9/29-9/30):
- 🟢 半导体/硬科技(10/3 美股纳指 ATH + 10/1 美光财报 +380%/+1077%)
- 🟢 银行/四大行(9/29 提肩带 + 9/30 老登股局部上涨 + 央行 PSL -25bp)

3 大板块(博主 10/06 实际提及 + 沿用主线):
1. 🟢 光通信/光模块/光纤 — 博主 10/06 06:45 "空心光纤利好什么板块" 直接点名
2. 🟢 半导体/硬科技 — 沿用 10/03 美股纳指 ATH + 10/01 美光财报
3. 🟢 银行/四大行 — 沿用 9/29-9/30 主线 + 10/06 06:45 现金流风控

6 个股:
- 中际旭创 300308 (1.6T 光模块龙头 — 空心光纤直接利好)
- 长飞光纤 601869 (光纤光缆龙头 — 空心光纤直接利好)
- 兆易创新 603986 (NOR+DRAM — 沿用美光财报 + 硬科技主线)
- 澜起科技 688008 (DDR5 接口芯片 — 沿用美光财报 + 硬科技主线)
- 工商银行 601398 (国有大行底仓 — 沿用博主长期底仓 + 节后防御)
- 农业银行 601288 (国有大行 — 沿用 9/29 提肩带 + 节后防御)

数据截至: 9/30 节前最后交易日(10/1-10/8 国庆休市)
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

    title_suffix = " (10/6 收 · 国庆假期倒数第 2 天 · 节后 10/8 周三开盘)"

    # 关键位定义(沿用博主关键位体系 + 9/30 实际收盘价 + 60D/120D 高低)
    targets = [
        # ── 大盘沪指 — 沿用博主关键位 + 9/30 收 ─────────
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
        # ── 创业板 — 沿用博主关键位 ──────────────────
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
        # ── 板块1: 光通信/光模块 — 中际旭创 (博主 10/6 空心光纤直接利好) ──
        ("300308.SZ", "中际旭创",
         [(1100.0, "60D高"),
          (950.0, "压力区"),
          (808.44, "9/30收"),
          (700.0, "60D低")],
         title_suffix),
        # ── 板块1: 光纤 — 长飞光纤 (空心光纤直接利好) ──
        ("601869.SH", "长飞光纤",
         [(530.0, "60D高"),
          (470.0, "压力"),
          (411.16, "9/30收"),
          (340.0, "60D低")],
         title_suffix),
        # ── 板块2: 半导体 — 兆易创新 (沿用 10/3 美股硬科技 + 10/1 美光财报) ──
        ("603986.SH", "兆易创新",
         [(707.97, "60D高"),
          (500.0, "中线位"),
          (353.90, "9/30收"),
          (337.10, "60D低")],
         title_suffix),
        # ── 板块2: DDR5 接口 — 澜起科技 (沿用美光 HBM) ──
        ("688008.SH", "澜起科技",
         [(297.96, "60D高"),
          (240.0, "中线位"),
          (202.31, "9/30收"),
          (180.25, "60D低")],
         title_suffix),
        # ── 板块3: 银行 — 工商银行 (博主长期底仓 + 节后防御) ──
        ("601398.SH", "工商银行",
         [(8.30, "60D高/压"),
          (8.28, "9/30收"),
          (7.50, "中线支"),
          (7.16, "60D低")],
         title_suffix),
        # ── 板块3: 银行 — 农业银行 (9/29 提肩带验证) ──
        ("601288.SH", "农业银行",
         [(7.11, "60D高"),
          (6.97, "9/30收"),
          (6.50, "中线支"),
          (5.97, "60D低")],
         title_suffix),
    ]
    for ts_code, name, levels, suf in targets:
        out = out_dir / f"{ts_code.replace('.', '_')}_20261006.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
            import traceback
            traceback.print_exc()
    print("[charts] done.")
