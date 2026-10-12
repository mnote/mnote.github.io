"""
wu2198 报告专用 K 线图生成器 — 2026-10-12 (周一 21:00 · 国庆节后第 3 个交易日 · 10/12 收盘)
博主 10/12 实际新增信号(共 9 条,3 条带操盘信号):
- 🔴 10/12 15:05 「今评价一个字"软"……还属于C3的调整中,暂时还没有形成C4反弹」 (10357赞 · 11504综合分 · 当日互动最高 · 博主收盘定调 C3 调整未完)
- 🔴 10/12 14:35 「今天也就这样了!」
- 🔴 10/12 13:38 「死鬼,软软绵绵……」
- 🔴 10/12 11:41 / 10:06 「真的急不来的!」/「急不来的!」
- 🟡 10/12 10:39 「收到请回复666或点赞支持一下!」(互动粉丝文化)
- 🟢 10/12 09:50 「最近几个交易日资金流入明显!」
- 🟢 10/12 09:47 「大盘指数早盘先观察 3786--3836 之间的取向」(博主 10/12 唯一明确关键区间)
- 🟢 10/12 09:44 「四大行,两桶油等继续提肩带!」(博主 10/12 唯一点名主线 → 银行 + 石油)

10/12 实际盘面验证:
- 沪指 3797.24 (-0.43%) 高 3828.22 低 3790.99 → 完全落在博主 3786--3836 区间内 ✅
- 创业板 2963.82 (-2.61%) 低 2962.24 → 跌破 10/9 前低区,续跌
- 沪深300 4287.98 (-0.68%)
- 四大行全线爆发收在 60D 高: 工行 +2.68% / 农行 +3.01% / 建行 +3.01% / 中行 +2.95% ✅ 完美验证「提肩带」
- 两桶油: 中石油 +2.59%(收 11.90 = 60D 高) / 中石化 +0.74% ✅
- 能源防御: 神华 +2.02%(收 49.38,逼近 60D 高 49.48)
- 固态电池分化走弱: 宁德 +0.21%(逆势抗跌) / 赣锋 -3.94%

3 大板块:
1. 🟢 银行/四大行 (博主 10/12 09:44 点名「提肩带」→ 今日最强主线,4 只全部收在 60D 高)
2. 🟢 石油·两桶油/能源防御 (博主 10/12 09:44 点名「两桶油」→ 中石油收 60D 高)
3. 🟡 固态电池/锂电 (沿用 10/8+10/9+10/10 三次确认,但今日分化: 宁德逆势 +0.21% / 赣锋 -3.94%;博主本人仍观望)

6 个股:
- 工商银行 601398 (四大行 · 收 8.44 = 60D 高 · 突破)
- 农业银行 601288 (四大行 · 收 7.19 = 60D 高 · 突破)
- 中国石油 601857 (两桶油 · 收 11.90 = 60D 高 · 突破)
- 中国神华 601088 (能源防御 · 收 49.38 逼近 60D 高 49.48)
- 宁德时代 300750 (固态电池 · 收 298.38 逆势 +0.21% · MA20 下方)
- 赣锋锂业 002460 (固态电池 · 收 43.68 -3.94% · 逼近 60D 低 41.67)

数据截至: 10/12 (国庆节后第 3 个交易日) 收盘
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
START = "20260101"
END = "20261012"


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
        # 前复权，保证均线/关键位与最新价可比
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
    """贪心下推，保证相邻标签 y 至少间隔 min_gap，返回 {value: label_y}"""
    out = {}
    prev = None
    for v in values:
        y = v if prev is None else max(v, prev + min_gap)
        out[v] = y
        prev = y
    return out


def draw_levels(ax, levels, color=MC_KEY, band=None, min_gap_frac=0.048, n_cols=2):
    """画水平关键位虚线 + 居左文字标签。

    指数图上 10 条关键位常常挤在 150 点窗口里（例如博主给出的 3786--3836
    窄区间 + 10/12 高低收 + 4 条均线），单列标签必然重叠。这里做两件事：
      1. 纵向防重叠：按真实价位贪心下推，保证相邻标签至少隔 min_gap；
      2. 双列错落：仍在同一条纵向带上的标签交替放进左一/左二两列。
    被推开的标签用细连接线接回它对应的真实价位虚线。
    """
    ylo, yhi = ax.get_ylim()
    span = yhi - ylo
    min_gap = span * min_gap_frac
    ordered = sorted(levels, key=lambda t: t[0])
    pos = _spread_positions([v for v, _ in ordered], min_gap)

    # 同一列内按 label_y 再次防重叠，再把仍然拥挤的标签分到第二列
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


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 120,
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
    # 先按关键位 / 博主区间撑开 y 轴范围，再画标签(标签防重叠需要已知量程)
    if levels:
        vs = [v for v, _ in levels]
        ylo, yhi = ax_main.get_ylim()
        pad = (max(vs) - min(vs)) * 0.06 if len(vs) > 1 else (yhi - ylo) * 0.1
        lo_b, hi_b = min(min(vs) - pad, ylo), max(max(vs) + pad, yhi)
        if band:
            lo_b = min(lo_b, band[0] - pad)
            hi_b = max(hi_b, band[1] + pad)
        # 为错落后可能上移/下移的标签再留一点余量
        extra = (hi_b - lo_b) * 0.045
        ax_main.set_ylim(lo_b - extra, hi_b + extra)

    # 博主关键区间底色（10/12 09:47 博主给出 3786--3836）
    if band:
        lo, hi, blbl = band
        ax_main.axhspan(lo, hi, color="#bfdbfe", alpha=0.18, zorder=0)
        ax_main.text(
            0.012, (lo + hi) / 2, f"博主关注区间 {blbl}", va="center", ha="left",
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


# ── 主入口 ─────────────────────────────────────────
if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    # 2026-10-12 周一收盘(国庆节后第 3 个交易日)
    title_suffix = " (10/12 收 · 国庆节后第 3 交易日)"

    # 关键位定义 = 博主 10/12 关键区间 + 10/12 实际高低收 + MA 均线 + 60D/120D 结构位
    targets = [
        # ── 大盘沪指 — 博主 10/12 09:47 明确给出 3786--3836 ─────
        ("000001.SH", "上证指数",
         [(3894.36, "MA60"),
          (3886.10, "MA20"),
          (3864.61, "MA10"),
          (3836, "博主上沿"),
          (3828.22, "10/12高"),
          (3819.12, "MA5"),
          (3797.24, "10/12收"),
          (3791.00, "10/12低"),
          (3786, "博主下沿"),
          (3741.11, "60D低")],
         (3786, 3836, "3786--3836"),
         title_suffix),
        # ── 创业板 — 10/12 -2.61% 续跌,失守 10/9 前低区 ─────────
        ("399006.SZ", "创业板指",
         [(3260.97, "MA20"),
          (3192.96, "MA10"),
          (3064.33, "MA5"),
          (3049.34, "10/12高"),
          (2963.82, "10/12收"),
          (2962.24, "10/12低"),
          (2932.80, "10/9前低")],
         None,
         title_suffix),
        # ── 沪深300 — 老登权重护盘但随大盘回落 ──────────────────
        ("000300.SH", "沪深300",
         [(4457.13, "MA20"),
          (4399.97, "MA10"),
          (4334.29, "10/12高"),
          (4323.67, "MA5"),
          (4287.98, "10/12收"),
          (4279.71, "10/12低"),
          (4239.74, "60D低")],
         None,
         title_suffix),
        # ── 板块1: 银行 — 工商银行 (博主 10/12 09:44「四大行提肩带」· 收 60D 高突破) ──
        ("601398.SH", "工商银行",
         [(8.44, "60D高·收"),
          (8.28, "MA5"),
          (8.20, "MA10"),
          (8.14, "MA20"),
          (7.89, "MA60"),
          (7.29, "60D低")],
         None,
         title_suffix),
        # ── 板块1: 银行 — 农业银行 (博主 9/29 四大行提肩带验证 · 收 60D 高突破) ──
        ("601288.SH", "农业银行",
         [(7.19, "60D高·收"),
          (7.02, "MA5"),
          (6.95, "MA10"),
          (6.91, "MA20"),
          (6.75, "MA60"),
          (6.20, "60D低")],
         None,
         title_suffix),
        # ── 板块2: 石油 — 中国石油 (博主 10/12 09:44「两桶油提肩带」· 收 60D 高突破) ──
        ("601857.SH", "中国石油",
         [(11.90, "60D高·收"),
          (11.48, "MA5"),
          (11.17, "MA10"),
          (11.01, "MA20"),
          (10.74, "MA60"),
          (9.08, "60D低")],
         None,
         title_suffix),
        # ── 板块2: 能源 — 中国神华 (能源防御 · 逼近 60D 高 49.48) ──
        ("601088.SH", "中国神华",
         [(49.48, "60D高"),
          (49.38, "10/12收"),
          (48.07, "MA5"),
          (47.83, "MA10"),
          (47.34, "MA20"),
          (46.10, "MA60"),
          (40.72, "60D低")],
         None,
         title_suffix),
        # ── 板块3: 固态电池 — 宁德时代 (10/8+10/9+10/10 三次确认 · 10/12 逆势 +0.21%) ──
        ("300750.SZ", "宁德时代",
         [(408.51, "60D高"),
          (357.31, "MA60"),
          (310.17, "MA20"),
          (306.71, "10/12高"),
          (298.38, "10/12收"),
          (294.90, "MA10"),
          (292.16, "MA5"),
          (285.17, "60D低")],
         None,
         title_suffix),
        # ── 板块3: 固态电池 — 赣锋锂业 (10/12 -3.94% 走弱 · 逼近 60D 低) ──
        ("002460.SZ", "赣锋锂业",
         [(56.89, "60D高"),
          (49.68, "MA60"),
          (45.82, "MA20"),
          (45.78, "10/12高"),
          (44.42, "MA10"),
          (44.03, "MA5"),
          (43.68, "10/12收"),
          (41.67, "60D低")],
         None,
         title_suffix),
    ]
    for ts_code, name, levels, band, suf in targets:
        out = out_dir / f"{ts_code.replace('.', '_')}_20261012.png"
        try:
            plot_one(ts_code, name, levels, out, days=120, title_suffix=suf, band=band)
        except Exception as e:
            print(f"  [fail] {ts_code} {name}: {e}")
            import traceback
            traceback.print_exc()
    print("[charts] done.")