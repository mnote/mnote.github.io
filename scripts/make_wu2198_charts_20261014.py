"""
wu2198 报告专用 K 线图生成器 — 2026-10-14 (周三 21:00 · 10/14 收盘)
博主 10/14 实际信号(共 8 条, 6 条带操盘信号):
- 🟢 10/14 15:06 「收3767点，今天不用评论……啵一个！」(12636赞 · 当日互动最高 · 收盘点位预测)
- 🟢 10/14 14:51 「布局C4」(10696赞 · 第 4 次强化 C4 表述, 且措辞由"等待"升级为"布局")
- 🟡 10/14 13:38 「等待结果！」(12807赞)
- 🟡 10/14 13:03 「反复折腾！」(9977赞 · 盘中横盘描述)
- 🟢 10/14 10:56 「耐心等待C4反抽！」(15003赞)
- 🟢 10/14 09:58 「按短线技术结构看，市场在构筑C4反弹。收到请回复666或点赞支持一下！」(19883赞 · 当日最高赞)
- 🟢 10/14 09:36 「今天早上3756点左右等侍反击……收到请回复888」(17246赞 · 早盘低点预测)
- ⚪ 10/14 09:19 「铁几？」(粉丝互动, 无信号)

10/14 实际盘面验证:
- 沪指 3767.23 (-0.88%) 低 3761.96 高 3811.81 → 博主预判「3756」「收3767」双点位几乎分毫不差
- 创业板 2866.76 (-3.10%) 低 2863.71 → 距 60D 低 2860.80 仅 0.10%, 暴跌
- 沪深300 4217.68 (-1.36%) 收在 60D 低 4214.01 上方仅 0.09%
- 中石油 +2.45% 收 12.55 盘中刷新 60D 高 12.57; 神华 +2.14% 收 50.55 刷新 60D 高 50.77
- 工行盘中触 8.54 (60D 高) 后收绿 -0.47%; 农行盘中触 7.31 (60D 高) 后收绿 -0.97% → 连续 2 日高位派发
- 宁德 -3.11% 收 280.12 = 当日最低 = 60D 低; 赣锋 -2.22% 收 41.00 逼近 60D 低 40.78

3 大板块:
1. 🟢 石油/能源(两桶油) — 唯一逆势创 60D 新高主线, 博主「两桶油提肩带」连续第 3 日验证
2. 🟡 银行/四大行 — 盘中连续第 2 日触 60D 高后收绿, 高位派发确认
3. 🔴 固态电池/锂电 — 宁德收在 60D 低, 博主「永不买电车」再获验证

6 个股:
- 中国石油 601857 (两桶油 · 收 12.55 +2.45% · 盘中刷新 60D 高 12.57)
- 中国神华 601088 (能源防御 · 收 50.55 +2.14% · 盘中刷新 60D 高 50.77)
- 工商银行 601398 (四大行 · 收 8.45 -0.47% · 盘中触 60D 高 8.54 后回落)
- 农业银行 601288 (四大行 · 收 7.18 -0.97% · 盘中触 60D 高 7.31 后回落)
- 宁德时代 300750 (固态电池 · 收 280.12 -3.11% · 收在当日最低=60D 低)
- 赣锋锂业 002460 (固态电池 · 收 41.00 -2.22% · 逼近 60D 低 40.78)

数据截至: 10/14 收盘
"""
import os
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
import numpy as np
import pandas as pd
import tushare as ts

# ── 颜色与样式（中国市场风格：红涨绿跌 · 白色底）──────────────
MC_UP = "#e63946"      # 红涨
MC_DOWN = "#2a9d8f"    # 绿跌
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_TXT = "#111111"
MC_KEY = "#1f6feb"     # 关键位蓝色虚线
MC_BBOX = "#dbeafe"

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

TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TUSHARE_TOKEN)
START = "20260101"
END = "20261014"


def fetch_daily(ts_code: str, days: int = 120) -> pd.DataFrame:
    is_index = (
        (ts_code.endswith(".SH") and ts_code.startswith("000")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("399"))
    )
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=START, end_date=END)
    else:
        df = pro.daily(ts_code=ts_code, start_date=START, end_date=END)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    if not is_index:
        try:
            adj = pro.adj_factor(ts_code=ts_code, start_date=START, end_date=END)
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
    df = df.rename(columns={"trade_date": "Date", "open": "Open", "high": "High",
                            "low": "Low", "close": "Close", "vol": "Volume"})
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


def _spread_positions(values, min_gap):
    out = {}
    prev = None
    for v in values:
        y = v if prev is None else max(v, prev + min_gap)
        out[v] = y
        prev = y
    return out


def draw_levels(ax, levels, color=MC_KEY, band=None, min_gap_frac=0.048, n_cols=2):
    """画水平关键位虚线 + 居左文字标签（防重叠 + 双列错落）。"""
    ylo, yhi = ax.get_ylim()
    span = yhi - ylo
    min_gap = span * min_gap_frac
    ordered = sorted(levels, key=lambda t: t[0])
    pos = _spread_positions([v for v, _ in ordered], min_gap)

    col_of = {}
    cur_col_y = [-np.inf, -np.inf]
    for v, _ in ordered:
        y = pos[v]
        placed = False
        for c in range(n_cols):
            if y - cur_col_y[c] >= min_gap:
                col_of[v] = c
                cur_col_y[c] = y
                placed = True
                break
        if not placed:
            c = int(np.argmin(cur_col_y))
            col_of[v] = c
            cur_col_y[c] = y

    col_x = [-0.006, -0.135]
    for v, lbl in ordered:
        ax.axhline(v, color=color, linestyle="--", linewidth=0.9, alpha=0.85, zorder=1)
        c = col_of[v]
        y = pos[v]
        x = col_x[c]
        if abs(y - v) > span * 0.004:
            ax.plot([x, x + 0.006], [y, v], color=color, lw=0.6, alpha=0.55,
                    zorder=4, clip_on=False, transform=ax.get_yaxis_transform())
        ax.text(
            x, y, f"  {lbl} {v:g}  ",
            va="center", ha="right", fontsize=9, color="#1d4ed8",
            transform=ax.get_yaxis_transform(),
            bbox=dict(boxstyle="round,pad=0.25", fc=MC_BBOX, ec="#93c5fd", lw=0.6),
            zorder=5, clip_on=False,
        )


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 60,
             title_suffix: str = "", band=None):
    df = fetch_daily(ts_code, days=days)
    if df.empty:
        print(f"  [skip] {ts_code} 无数据")
        return
    dif, dea, macd = compute_macd(df)
    last_close = df["Close"].iloc[-1]
    last_date = df.index[-1].strftime("%Y-%m-%d")
    prev_close = df["Close"].iloc[-2]
    pct = (last_close / prev_close - 1) * 100
    pct_s = f"{pct:+.2f}%"

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

    title = f"{name} ({ts_code.replace('.', '_')}) 日线 · K线 + MACD + 成交量{title_suffix} · 收 {last_close:.2f} ({pct_s}) · {last_date}"

    fig, axes = mpf.plot(
        df, type="candle", volume=True, mav=(5, 10, 20),
        addplot=add_plots, style=style,
        figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
        title=title,
        ylabel="价格", ylabel_lower="成交量",
        xrotation=0,
    )
    ax_main = axes[0]
    if levels:
        vs = [v for v, _ in levels]
        ylo, yhi = ax_main.get_ylim()
        pad = (max(vs) - min(vs)) * 0.06 if len(vs) > 1 else (yhi - ylo) * 0.1
        lo_b, hi_b = min(min(vs) - pad, ylo), max(max(vs) + pad, yhi)
        if band:
            lo_b = min(lo_b, band[0] - pad)
            hi_b = max(hi_b, band[1] + pad)
        extra = (hi_b - lo_b) * 0.045
        ax_main.set_ylim(lo_b - extra, hi_b + extra)

    if band:
        lo, hi, blbl = band
        ax_main.axhspan(lo, hi, color="#bfdbfe", alpha=0.18, zorder=0)
        ax_main.text(
            0.012, (lo + hi) / 2, f"关键支撑带 {blbl}", va="center", ha="left",
            fontsize=9, color="#1e40af", zorder=4,
        )
    draw_levels(ax_main, levels)

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
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线, 收 {last_close:.2f} {pct_s})")


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    title_suffix = " (10/14 收 · C4 布局 vs 创业板暴跌)"

    targets = [
        # ── 大盘沪指 — 博主 3756 低点 + 3767 收盘双预判, 均命中 ─────
        ("000001.SH", "上证指数",
         [(3870.85, "MA20"),
          (3836, "博主收复门槛"),
          (3831.22, "MA10"),
          (3811.81, "10/14高"),
          (3798.21, "MA5"),
          (3767.23, "10/14收"),
          (3761.96, "10/14低"),
          (3741.11, "60D低")],
         (3741.11, 3767.23, "60D低 3741 — 博主收盘预测 3767"),
         title_suffix),
        # ── 创业板 — -3.10% 暴跌, 距 60D 低仅 0.10% ──────────────
        ("399006.SZ", "创业板指",
         [(3095.51, "MA10"),
          (2973.78, "MA5"),
          (2962.73, "10/14高"),
          (2866.76, "10/14收"),
          (2863.71, "10/14低"),
          (2860.80, "60D低")],
         None,
         title_suffix),
        # ── 沪深300 — 收在 60D 低上方仅 0.09%, 权重同步破位 ──────
        ("000300.SH", "沪深300",
         [(4340.89, "MA10"),
          (4281.77, "MA5"),
          (4281.46, "10/14高"),
          (4217.68, "10/14收"),
          (4214.01, "60D低/10-14低")],
         (4214.01, 4217.68, "60D 低 4214 — 收盘 4217"),
         title_suffix),
        # ── 两桶油/能源 — 今日唯一逆势创新高主线 ──────────────────
        ("601857.SH", "中国石油",
         [(11.16, "MA20"),
          (11.51, "MA10"),
          (11.98, "MA5"),
          (12.55, "10/14收"),
          (12.57, "60D新高")],
         None,
         title_suffix),
        ("601088.SH", "中国神华",
         [(47.72, "MA20"),
          (48.40, "MA10"),
          (49.06, "MA5"),
          (50.55, "10/14收"),
          (50.77, "60D新高")],
         None,
         title_suffix),
        # ── 四大行 — 连续 2 日触 60D 高后收绿, 高位派发 ───────────
        ("601398.SH", "工商银行",
         [(8.19, "MA20"),
          (8.27, "MA10"),
          (8.38, "MA5"),
          (8.45, "10/14收"),
          (8.54, "60D高")],
         None,
         title_suffix),
        ("601288.SH", "农业银行",
         [(6.95, "MA20"),
          (7.01, "MA10"),
          (7.12, "MA5"),
          (7.18, "10/14收"),
          (7.31, "60D高")],
         None,
         title_suffix),
        # ── 固态电池/锂电 — 宁德收在 60D 低, 赣锋逼近 60D 低 ──────
        ("300750.SZ", "宁德时代",
         [(304.44, "MA20"),
          (291.65, "MA10"),
          (290.42, "MA5"),
          (280.12, "60D低/10-14收")],
         None,
         title_suffix),
        ("002460.SZ", "赣锋锂业",
         [(45.07, "MA20"),
          (43.42, "MA10"),
          (43.26, "MA5"),
          (41.00, "10/14收"),
          (40.78, "60D低")],
         None,
         title_suffix),
    ]

    for ts_code, name, levels, band, tsuf in targets:
        fn = f"{ts_code.replace('.', '_')}_{name}.png"
        try:
            plot_one(ts_code, name, levels, out_dir / fn, band=band, title_suffix=tsuf)
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")