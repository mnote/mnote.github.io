"""
wu2198 报告专用 K 线图生成器 — 2026-11-04 (周三 22:00 · 11/04 收盘)
博主 11/04 实际信号(共 33 条, 覆盖 11/03 15:40 → 11/04 18:30):
- 🟢 11/04 15:08 「今天收3686点，增量3368亿……明天收复3706点后以3574和3580形成小双底反击之势」(16089赞·当日最高)
- 🟢 11/04 16:09 「科创50指数到过1132点……今天大涨9.92%！」(7592赞)
- 🟢 11/04 09:50 「物理AI龙头冲20厘米，端侧纷纷走强！」(7680赞)
- 🟢 11/04 12:00 「按目前看人形机器人，GPU，物理AI，端侧等表现不错！」(7639赞)
- 🟢 11/04 09:00 「稀有金属，截止目前看是锗，钨涨幅领先！」(9066赞)
- 🟢 11/04 09:00 「参考大盘4256和创业板指数4380区域撤离的投资者，可以继续分批布局接回来」(1.6万赞)
- 🟢 11/04 08:50 「身似青山常自在……把每一轮大跌风险回避，拿捏住大跌后的机会」(1.1万赞)
- 🟢 11/04 14:38 「这两天很多人嘲讽"一剑封喉"……是多么的无知可笑啊！」(1.3万赞)
- 🟢 11/04 14:56 长文「在5月初4256点之后我反复提示第四大浪调整，创业板4380点后我提示三川顶……
  这两天大盘3580和创业板指数2376点又如何提示大家的？……在6月份科技股疯狂的时候我反复提醒大家科技类股的泡沫+风险」(1.4万赞)
- 🟢 11/04 14:00 「创业板指数己经返涨4% 了」「已经5.4%！」「掐指一算，创业板指数今天"一吃三"，争夺一吃四"」
- 🟡 11/04 12:00 「日本，韩国，目前都出现大跌3%以上，道指期货目前也跌333点！」
- 🟡 11/04 15:24 「今天多了好多票子，晚上白马？」
- 🟡 11/03 17:46 「CPO三大龙头这轮下跌了66至72%左右……疯狂的时候提示风险，被骂死！」

11/04 实际盘面验证:
- 沪指 3686.17 (+2.16%) 开 3605.39 低 3590.80 高=收 3686.17 → 博主 15:08 预判「收3686点」分毫不差
- 创业板 2544.73 (+6.40%) 低 2376.28 高 2559.09 → 博主 11/04 14:00「一吃三/一吃四」「已经5.4%」兑现
- 科创50 1265.47 (+9.918%≈9.92%) 高 1271.27 低 1149.10 → 博主 16:09「大涨9.92%」分毫不差
- 全市场成交额 20519 亿, 增量 3368 亿 → 博主「增量3368亿」分毫不差
- 11/03 低点: 沪指 3580.38 / 创业板 2376.39 → 博主长文「大盘3580和创业板指数2376点」分毫不差
- 10/23 低点 沪指 3574.27 → 与 11/03 的 3580 构成博主所说「3574和3580小双底」

3 大板块:
1. 🟢 科创50 半导体设备/国产替代 (177 只半导体涨超 5%, 20cm 涨停潮: 拓荆/芯源微/华峰测控/富创精密/中科飞测/思瑞浦)
2. 🟢 物理AI/人形机器人/端侧AI (开勒+20.00% / 春晖+20.02% / 艾能聚+29.99% / 瑞芯微+10.00% / 恒玄+14.62%)
3. 🟢 稀有金属 锗+钨 (云南锗业+10.00% / 中钨高新+10.01% / 东方钽业+9.99% / 博迁新材+10.00%)
附 🟡 CPO/光模块超跌反弹 (新易盛+13.35% / 中际旭创+11.07% / 天孚通信+10.02%)
附 🔴 白马回调 (茅台-2.27% / 五粮液-0.60%) → 博主「晚上白马？」当天就落空

3 个股:
- 开勒股份 301070 (物理AI/机器人丝杠 · 收 44.46 +20.00% 20cm 涨停)
- 云南锗业 002428 (锗 · 收 75.38 +10.00% 涨停)
- 中际旭创 300308 (CPO 龙头 · 收 533.38 +11.07%)

数据截至: 11/04 收盘
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
END = "20261104"

# 关键位标签配色（不同语义用不同色）
C_BLOG = "#1f6feb"   # 博主点位
C_MA = "#9ca3af"     # 均线
C_EXT = "#e11d48"    # 极值 / 硬门槛


def fetch_daily(ts_code: str, days: int = 120) -> pd.DataFrame:
    is_index = (
        (ts_code.endswith(".SH") and ts_code.startswith("000")) or
        (ts_code.endswith(".SH") and ts_code.startswith("399")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("399")) or
        (ts_code.endswith(".SZ") and ts_code.startswith("000"))
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

    title_suffix = " (11/04 收 · 科创50 +9.92% 暴力反弹)"

    # ── 先算均线值，供关键位标注 ───────────────────────────────
    ma = {}
    for code in ["000001.SH", "399006.SZ", "000688.SH", "000300.SH",
                 "301070.SZ", "002428.SZ", "300308.SZ"]:
        ma[code] = {n: ma_of(code, n) for n in (5, 10, 20)}
        print(f"  MA {code}: {ma[code]}")

    ext = {}
    for code in ["000688.SH", "301070.SZ", "002428.SZ", "300308.SZ"]:
        ext[code] = extremes(code, 60)
        print(f"  60D 极值 {code}: 高 {ext[code][0]} 低 {ext[code][1]}")

    targets = [
        # ── 沪指 — 博主 15:08 预判「收3686」分毫不差 ─────────────
        ("000001.SH", "上证指数",
         [(ma["000001.SH"][20], ("MA20", C_MA)),
          (3706, ("博主明日目标", C_BLOG)),
          (3686.17, ("11/04收=预判", C_BLOG)),
          (3624.58, ("11/04开", C_MA)),
          (3590.80, ("11/04低", C_MA)),
          (3580.38, ("11/03低·3574/3580双底", C_BLOG)),
          (3574.27, ("10/23低·双底", C_BLOG))],
         (3574.27, 3580.38, "3574/3580 小双底（博主）"),
         title_suffix),
        # ── 创业板 — +6.40%，博主 14:00「一吃三/一吃四」兑现 ────────
        ("399006.SZ", "创业板指",
         [(ma["399006.SZ"][20], ("MA20", C_MA)),
          (2559.09, ("11/04高", C_MA)),
          (2544.73, ("11/04收", C_BLOG)),
          (2471.90, ("11/03高", C_MA)),
          (2413.63, ("10/30低", C_MA)),
          (2376.28, ("11/04低=博主提示2376", C_BLOG)),
          (2391.65, ("11/03收", C_MA))],
         (2376.28, 2413.63, "2376 支撑（博主提示位）"),
         title_suffix),
        # ── 科创50 — +9.92%，博主 16:09 亲口报涨幅 ────────────────
        ("000688.SH", "科创50",
         [(ma["000688.SH"][20], ("MA20", C_MA)),
          (ext["000688.SH"][0], ("60D高", C_EXT)),
          (1271.27, ("11/04高", C_MA)),
          (1265.47, ("11/04收", C_BLOG)),
          (1184.53, ("11/03开", C_MA)),
          (1149.10, ("11/04低", C_MA)),
          (1132.33, ("11/03低=博主「到过1132」", C_BLOG)),
          (1100.00, ("博主理想搏击点", C_EXT))],
         (1100.00, 1132.33, "1100 关口（博主理想搏击点）"),
         title_suffix),
        # ── 沪深300 — 权重跟涨但弱于成长 ─────────────────────────
        ("000300.SH", "沪深300",
         [(ma["000300.SH"][20], ("MA20", C_MA)),
          (4105.86, ("11/04高", C_MA)),
          (4101.34, ("11/04收", C_BLOG)),
          (4046.87, ("10/30高", C_MA)),
          (3987.15, ("11/04低", C_MA)),
          (3969.55, ("11/03低", C_MA))],
         (3969.55, 3987.15, "3970-3987 支撑区"),
         title_suffix),
        # ── 个股 1: 物理AI 龙头 20cm ──────────────────────────────
        ("301070.SZ", "开勒股份",
         [(ma["301070.SZ"][20], ("MA20", C_MA)),
          (ma["301070.SZ"][10], ("MA10", C_MA)),
          (ma["301070.SZ"][5], ("MA5", C_MA)),
          (44.46, ("11/04收·20CM涨停", C_BLOG)),
          (35.90, ("11/04低", C_MA)),
          (ext["301070.SZ"][1], ("60D低", C_EXT))],
         None,
         " (11/04 收 · 物理AI 龙头 20cm)"),
        # ── 个股 2: 锗 龙头 涨停 ──────────────────────────────────
        ("002428.SZ", "云南锗业",
         [(ma["002428.SZ"][20], ("MA20", C_MA)),
          (ma["002428.SZ"][10], ("MA10", C_MA)),
          (ma["002428.SZ"][5], ("MA5", C_MA)),
          (75.38, ("11/04收·涨停", C_BLOG)),
          (72.00, ("11/04低", C_MA)),
          (ext["002428.SZ"][1], ("60D低", C_EXT))],
         None,
         " (11/04 收 · 锗 涨停)"),
        # ── 个股 3: CPO 龙头 超跌反弹 ─────────────────────────────
        ("300308.SZ", "中际旭创",
         [(ma["300308.SZ"][20], ("MA20", C_MA)),
          (ma["300308.SZ"][10], ("MA10", C_MA)),
          (ma["300308.SZ"][5], ("MA5", C_MA)),
          (544.00, ("11/04高", C_MA)),
          (533.38, ("11/04收", C_BLOG)),
          (ext["300308.SZ"][1], ("11/04低=60D低", C_EXT))],
         None,
         " (11/04 收 · CPO 龙头 +11%)"),
    ]

    for ts_code, name, levels, band, tsuf in targets:
        # 图表文件名一律带日期: charts/{代码}_{YYYYMMDD}.png
        # 否则会覆盖历史日报引用的共用图(10-14 日报即因此被覆盖过)
        fn = f"{ts_code.replace('.', '_')}_20261104.png"
        try:
            plot_one(ts_code, name, levels, out_dir / fn, band=band, title_suffix=tsuf)
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")
