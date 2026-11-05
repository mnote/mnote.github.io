"""
wu2198 报告专用 K 线图生成器 — 2026-11-05 (周四 23:00 · 11/05 收盘)
博主 11/05 实际信号(共 17 条, 覆盖 11/04 13:50 → 11/05 18:07):
- 🟢 11/05 15:08「在外围大跌的情况下,今天两市均能低开震荡走强收红盘,说明大A市场构筑波段的步骤不变……」(15666赞·当日最高)
- 🟢 11/05 09:30「低开不惧,轻仓可吸……支持的点赞！」(14546赞·当日第二高)
- 🟡 11/05 13:54「反弹行情是一个过程,不是一两天！明白666」(11482赞)
- 🟢 11/05 10:19「端侧龙头两连板,算力租凭龙二冲板。固态整体表现出色！」(9996赞)
- 🟢 11/05 10:02「固态、端侧、算力租凭……目前继续领先！」(9339赞)
- 🟡 11/05 13:35「人形机器人龙头这波反弹明显比大盘指数要提前,也强很多。」(8593赞)
- 🟡 11/05 14:19「今天主要是CPO和存储芯片压创板指数,如果这两个权重板块尾盘有资金自救的话,指数有望收高！」(7507赞)
- 🟡 11/05 06:41「昨晚美国市场是软科技大涨、存储芯片板块大跌,分化非常大！」(10302赞·早安帖)
- 🟢 11/05 15:02「今天端侧非常"标土浮"……龙头连续拉了2个板,几只改写新高！」(7881赞)
- ⚪ 11/05 14:27/14:36/14:41/14:50 + 17:33/17:47/18:07(春节放假安排)+ 11/04 13:50(创业板返涨4%)

11/05 实际盘面验证:
- 沪指 3689.91 (+0.10%) 开 3646.57(当日最低=开盘) 低 3646.57 高 3701.59
  → 博主 09:30「低开不惧,轻仓可吸」✅ 低开 -1.07% 后走强收红
  → 博主 11/04 15:08「明天收复 3706 点」→ 实际最高 3701.59,差 4.41 点未收复 ❌(仅差 0.12%)
  → 博主 11/04「3574/3580 小双底」→ 11/05 最低 3646.57,根本没回踩双底 ❌
- 创业板 2566.80 (+0.87%) 低 2493.67 高 2625.98
  → 博主 14:19「CPO和存储芯片压创板指数……尾盘资金自救,指数有望收高」✅
     从低点 2493.67 拉到收 2566.80(+2.93%),最高 2625.98(自低点 +5.31%)
- 科创50 1286.68 (+1.68%) 低 1236.01 高 1329.14
  → 博主 10/23 自设「1100 关口才是理想搏击点」→ 11/05 最低 1236.01,还差 12.3% ❌
- 沪深300 4113.41 (+0.29%) → 明显弱于成长股
- 全市场成交额 21351 亿(增量 832 亿) · 涨停 132 家(前日 372)跌停 6 家(前日 16) · 20cm 涨停 12 家

3 大板块:
1. 🟢 端侧AI/算力租赁 (博主的绝对主线, 两次点名)
   瑞芯微 603893 11/04+10.00% → 11/05+10.00% 两连板涨停 ✅「龙头连续拉了2个板」
   博通集成 603068 11/05+9.99% 涨停 · 全志科技 +5.47% · 恒玄科技 +5.13%
   润泽科技 300442 +11.59%(最高 61.15 未封板)· 首都在线 300846 +9.38%(最高 17.55 未封板)
2. 🟢 固态电池 (博主 10:02/10:19 连续确认)
   宁德时代 300750 +4.42% 成交 184.02 亿 · 赣锋锂业 002460 +6.27% · 德尔股份 +5.45% · 当升科技 +3.82%
3. 🟡 人形机器人 (博主 13:35 单独点名「比大盘提前也强很多」)
   11/05 15 只样本均值 +1.56% vs 沪指 +0.10% · 兆威机电 +6.33% · 绿的谐波 +2.62%
附 🔴 CPO/光模块+存储芯片 (博主 14:19 点名但当日领跌)
   中际旭创 300308 -7.51% · 新易盛 -5.54% · 天孚通信 -4.78% · 兆易创新 -3.03% · 澜起科技 -2.40%

3 个股:
- 瑞芯微 603893 (端侧AI龙头 · 两连板涨停 · 收 217.81 +10.00%)
- 润泽科技 300442 (算力租赁龙头 · 收 59.78 +11.59% · 量比 1.79)
- 宁德时代 300750 (固态电池龙头 · 收 264.06 +4.42% · 成交 184 亿)
附 🔴 中际旭创 300308 (CPO龙头对照组 · 收 493.33 -7.51%)

数据截至: 11/05 收盘
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
END = "20261105"

INDEX_CODES = {"000001.SH", "399006.SZ", "000688.SH", "000300.SH"}

# 关键位标签配色（不同语义用不同色）
C_BLOG = "#1f6feb"   # 博主点位
C_MA = "#9ca3af"     # 均线
C_EXT = "#e11d48"    # 极值 / 硬门槛


def fetch_daily(ts_code: str, days: int = 120) -> pd.DataFrame:
    is_index = ts_code in INDEX_CODES
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
            adj = pro.adj_factor(ts_code=ts_code, start_date=START, end_date=END).copy()
            adj["trade_date"] = pd.to_datetime(adj["trade_date"], format="%Y%m%d")
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


def draw_levels(ax, levels, color=MC_KEY, min_gap_frac=0.048, n_cols=2):
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
        lc = color
        if isinstance(lbl, tuple):
            lbl, lc = lbl
        ax.axhline(v, color=lc, linestyle="--", linewidth=0.9, alpha=0.85, zorder=1)
        c = col_of[v]
        y = pos[v]
        x = col_x[c]
        if abs(y - v) > span * 0.004:
            ax.plot([x, x + 0.006], [y, v], color=lc, lw=0.6, alpha=0.55,
                    zorder=4, clip_on=False, transform=ax.get_yaxis_transform())
        ax.text(
            x, y, f"  {lbl} {v:g}  ",
            va="center", ha="right", fontsize=9, color=lc,
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
    ma5 = df["Close"].rolling(5).mean()
    ma10 = df["Close"].rolling(10).mean()
    ma20 = df["Close"].rolling(20).mean()

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
        mpf.make_addplot(ma5, panel=0, color="#f59e0b", width=0.8),
        mpf.make_addplot(ma10, panel=0, color="#8b5cf6", width=0.8),
        mpf.make_addplot(ma20, panel=0, color="#0ea5e9", width=0.9),
        mpf.make_addplot(dif, panel=2, color="#f59e0b", width=1.0, ylabel="MACD"),
        mpf.make_addplot(dea, panel=2, color="#1d4ed8", width=1.0),
        mpf.make_addplot(macd, type="bar", panel=2, color=MC_UP, secondary_y=False),
    ]

    title = f"{name} ({ts_code.replace('.', '_')}) 日线 · K线 + MACD + 成交量{title_suffix} · 收 {last_close:.2f} ({pct_s}) · {last_date}"

    fig, axes = mpf.plot(
        df, type="candle", volume=True,
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
            0.60, (lo + hi) / 2, f"关键支撑带 {blbl}", va="center", ha="left",
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


def ma_of(ts_code, n, days=120):
    df = fetch_daily(ts_code, days=days)
    return round(df["Close"].rolling(n).mean().iloc[-1], 2)


def extremes(ts_code, days=60):
    """返回最近 N 个交易日的 (最高, 最低)。"""
    df = fetch_daily(ts_code, days=days)
    return round(df["High"].max(), 2), round(df["Low"].min(), 2)


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    title_suffix = " (11/05 收 · 低开走强收红盘)"

    # ── 先算均线值，供关键位标注 ───────────────────────────────
    ma = {}
    for code in ["000001.SH", "399006.SZ", "000688.SH", "000300.SH",
                 "603893.SH", "300442.SZ", "300750.SZ", "300308.SZ"]:
        ma[code] = {n: ma_of(code, n) for n in (5, 10, 20)}
        print(f"  MA {code}: {ma[code]}")

    ext = {}
    for code in ["000688.SH", "000300.SH", "603893.SH", "300442.SZ", "300750.SZ", "300308.SZ"]:
        ext[code] = extremes(code, 60)
        print(f"  60D 极值 {code}: 高 {ext[code][0]} 低 {ext[code][1]}")

    targets = [
        # ── 沪指 — 博主 09:30「低开不惧」兑现；但 3706 差 4.41 点未收复 ─────
        ("000001.SH", "上证指数",
         [(ma["000001.SH"][20], ("MA20", C_MA)),
          (3706.00, ("博主昨日目标", C_BLOG)),
          (3701.59, ("11/05高", C_MA)),
          (3689.91, ("11/05收", C_BLOG)),
          (ma["000001.SH"][10], ("MA10", C_MA)),
          (3646.57, ("11/05开=最低", C_MA)),
          (3574.27, ("10/23低·双底", C_BLOG))],
         (3574.27, 3580.38, "3574/3580 小双底（博主）"),
         title_suffix),
        # ── 创业板 — 博主 14:19「尾盘资金自救收高」兑现 ──────────
        ("399006.SZ", "创业板指",
         [(ma["399006.SZ"][20], ("MA20", C_MA)),
          (2625.98, ("11/05高", C_MA)),
          (2566.80, ("11/05收", C_BLOG)),
          (ma["399006.SZ"][10], ("MA10", C_MA)),
          (2493.67, ("11/05低=开盘", C_MA)),
          (2376.28, ("11/04低=博主提示位", C_BLOG))],
         (2376.28, 2391.65, "2376 支撑（博主提示位）"),
         title_suffix),
        # ── 科创50 — 博主 1100 理想买点又没等到 ───────────────────
        ("000688.SH", "科创50",
         [(ma["000688.SH"][20], ("MA20", C_MA)),
          (1329.14, ("11/05高", C_MA)),
          (1286.68, ("11/05收", C_BLOG)),
          (ma["000688.SH"][10], ("MA10", C_MA)),
          (1236.01, ("11/05开=最低", C_MA)),
          (1132.33, ("11/03低", C_BLOG)),
          (1100.00, ("博主理想搏击点", C_EXT))],
         (1100.00, 1132.33, "1100 关口（博主理想搏击点）"),
         title_suffix),
        # ── 沪深300 — 权重弱于成长 ──────────────────────────────
        ("000300.SH", "沪深300",
         [(ma["000300.SH"][20], ("MA20", C_MA)),
          (4136.80, ("11/05高", C_MA)),
          (4113.41, ("11/05收", C_BLOG)),
          (ma["000300.SH"][10], ("MA10", C_MA)),
          (4065.72, ("11/05开=最低", C_MA)),
          (3958.14, ("60D低", C_EXT))],
         None,
         title_suffix),
        # ── 个股 1: 端侧AI 龙头 两连板 ──────────────────────────
        ("603893.SH", "瑞芯微",
         [(ma["603893.SH"][20], ("MA20", C_MA)),
          (ma["603893.SH"][10], ("MA10", C_MA)),
          (ma["603893.SH"][5], ("MA5", C_MA)),
          (217.81, ("11/05收·两连板涨停", C_BLOG)),
          (198.01, ("11/04收·一板", C_MA)),
          (ext["603893.SH"][0], ("60D高", C_EXT))],
         None,
         " (11/05 收 · 端侧AI 龙头 两连板)"),
        # ── 个股 2: 算力租赁 龙头 冲板未封 ─────────────────────
        ("300442.SZ", "润泽科技",
         [(ma["300442.SZ"][20], ("MA20", C_MA)),
          (ma["300442.SZ"][10], ("MA10", C_MA)),
          (ma["300442.SZ"][5], ("MA5", C_MA)),
          (61.71, ("MA60", C_MA)),
          (61.15, ("11/05高", C_MA)),
          (59.78, ("11/05收", C_BLOG)),
          (ext["300442.SZ"][0], ("60D高", C_EXT))],
         None,
         " (11/05 收 · 算力租赁 +11.59%)"),
        # ── 个股 3: 固态电池 龙头 ───────────────────────────────
        ("300750.SZ", "宁德时代",
         [(ma["300750.SZ"][20], ("MA20", C_MA)),
          (ma["300750.SZ"][10], ("MA10", C_MA)),
          (ma["300750.SZ"][5], ("MA5", C_MA)),
          (272.19, ("11/05高", C_MA)),
          (264.06, ("11/05收", C_BLOG)),
          (ext["300750.SZ"][0], ("60D高", C_EXT))],
         None,
         " (11/05 收 · 固态电池 龙头)"),
        # ── 个股 4: CPO 龙头 对照组（博主点名但当日领跌）─────────
        ("300308.SZ", "中际旭创",
         [(ma["300308.SZ"][20], ("MA20", C_MA)),
          (ma["300308.SZ"][10], ("MA10", C_MA)),
          (ma["300308.SZ"][5], ("MA5", C_MA)),
          (493.33, ("11/05收", C_BLOG)),
          (475.10, ("11/05低", C_MA)),
          (ext["300308.SZ"][1], ("60D低", C_EXT))],
         None,
         " (11/05 收 · CPO 龙头 -7.51%)"),
    ]

    for ts_code, name, levels, band, tsuf in targets:
        # 图表文件名一律带日期: charts/{代码}_{YYYYMMDD}.png
        fn = f"{ts_code.replace('.', '_')}_20261105.png"
        try:
            plot_one(ts_code, name, levels, out_dir / fn, band=band, title_suffix=tsuf)
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")
