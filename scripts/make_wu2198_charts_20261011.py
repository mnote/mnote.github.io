"""
wu2198 报告专用 K 线图生成器 — 2026-10-11 (周日 21:00 · 国庆节后周末 · 沿用 10/9 收盘)
博主最近一天(10/10 + 10/11)新增信号:
- 🟡 10/10 20:15 「起码等固态电池技术成熟之后吧」 (4770 赞 · 5092 综合分 · 10/10 唯一新增行业信号 · 博主第三次确认固态电池主线)
- 🔴 10/10 16:52 「坦白说,我从来没有购买电车的想法。因为,我怕没有人喊我加油」 (6002 赞 · 6576 综合分 · 博主对电车持续看空)
- 🔴 10/10 11:03 「我认真看了我的刹车踏板,木有任何问题」 (4373 赞 · 4723 综合分 · 博主对电车/新能源板块二次看空)
- ⚪ 10/10/11 其他 7 条:晚安/广西大学/王皓/飞天奖/男领导/梅艳芳/女局长 — 鸡汤 + 社会新闻 + 生活 (周日 + 周六非交易日 + 节后周末模式)

沿用主线 (10/8 + 10/9 + 10/10 三次确认):
- 🟡 固态电池/锂电池 (10/8 + 10/9 + 10/10 三次确认:资金活动明显但博主等成熟)
- 🟢 银行/四大行 (沿用 9/29-10/8 提肩带 + 央行 PSL -25bp + 节后防御主线)
- 🟢 煤炭+石油/能源防御 (沿用 9/29-10/8 防御主线 + C4 反弹期待权重护盘)

3 大板块 (博主 10/10 实际提及 + 沿用主线):
1. 🟡 固态电池/锂电池 (博主 10/8 + 10/9 + 10/10 三次确认,博主本人持观望)
2. 🟢 银行/四大行 (沿用 9/29-10/8 + 节后防御主线)
3. 🟢 煤炭+石油/能源防御 (沿用主线 + C4 反弹期待权重护盘)

6 个股:
- 宁德时代 300750 (全球动力电池龙头 · 固态电池技术布局领先)
- 赣锋锂业 002460 (锂矿龙头 + 固态电池产业链)
- 工商银行 601398 (国有大行底仓 · 节后防御首选)
- 农业银行 601288 (博主 9/29 四大行提肩带验证)
- 中国神华 601088 (煤电路港航化一体化 · C4 反弹权重护盘)
- 中国石油 601857 (OPEC+ + 中东地缘 · C4 反弹权重护盘)

数据截至: 10/9 节后第 2 个交易日 (10/10/11 为周末休市)
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


def fetch_daily(ts_code: str, end_date: str = "20261009", days: int = 120) -> pd.DataFrame:
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

    title_suffix = " (10/9 收 · 10/10+11 周末休市 · 沿用节后第 2 交易日)"

    # 关键位定义 (沿用博主关键位体系 + 10/9 实际收盘 + 60D/120D 高低)
    targets = [
        # ── 大盘沪指 — 沿用博主关键位 + 10/9 收 ─────────
        ("000001.SH", "上证指数",
         [(4258, "年大顶"),
          (4143, "60D高"),
          (4036, "周压"),
          (3954, "10/9试"),
          (3825, "10/9抽高"),
          (3813.79, "10/9收"),
          (3800, "整数"),
          (3754.14, "10/9低"),
          (3741, "60D低")],
         title_suffix),
        # ── 创业板 — 沿用博主关键位 ──────────────────
        ("399006.SZ", "创业板指",
         [(4371, "120D高"),
          (4361.82, "60D高"),
          (4380, "5/9顶"),
          (3590, "博主目标"),
          (3160, "A杀位"),
          (3053, "10/9抽高"),
          (3043.33, "10/9收"),
          (3012.03, "60D低"),
          (2932.80, "10/9新低")],
         title_suffix),
        # ── 板块1: 固态电池 — 宁德时代 (博主 10/8 + 10/9 + 10/10 三次确认) ──
        ("300750.SZ", "宁德时代",
         [(410.0, "60D高"),
          (358.61, "MA60"),
          (312.80, "MA20"),
          (297.75, "10/9收"),
          (290.88, "MA5"),
          (285.17, "60D低")],
         title_suffix),
        # ── 板块1: 固态电池 — 赣锋锂业 (博主三次确认 + 10/9 +2.85% 反弹) ──
        ("002460.SZ", "赣锋锂业",
         [(66.72, "60D高"),
          (50.10, "MA60"),
          (46.20, "MA20"),
          (45.47, "10/9收"),
          (42.50, "MA5"),
          (41.67, "60D低")],
         title_suffix),
        # ── 板块2: 银行 — 工商银行 (博主长期底仓 + 节后防御) ──
        ("601398.SH", "工商银行",
         [(8.38, "60D高"),
          (8.41, "MA60"),
          (8.33, "MA20"),
          (8.22, "10/9收"),
          (7.96, "60D低")],
         title_suffix),
        # ── 板块2: 银行 — 农业银行 (博主 9/29 四大行提肩带验证) ──
        ("601288.SH", "农业银行",
         [(7.11, "60D高"),
          (7.04, "MA60"),
          (7.04, "MA20"),
          (6.98, "10/9收"),
          (6.87, "60D低")],
         title_suffix),
        # ── 板块3: 煤炭 — 中国神华 (C4 反弹权重护盘) ──
        ("601088.SH", "中国神华",
         [(49.48, "60D高"),
          (45.50, "MA60"),
          (47.80, "MA20"),
          (48.40, "10/9收"),
          (39.97, "60D低")],
         title_suffix),
        # ── 板块3: 石油 — 中国石油 (OPEC+ + 中东地缘) ──
        ("601857.SH", "中国石油",
         [(11.63, "60D高"),
          (11.30, "MA60"),
          (11.20, "MA20"),
          (11.60, "10/9收"),
          (8.93, "60D低")],
         title_suffix),
    ]
    for ts_code, name, levels, suf in targets:
        out = out_dir / f"{ts_code.replace('.', '_')}_20261011.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
            import traceback
            traceback.print_exc()
    print("[charts] done.")