"""wu2198 报告 K 线图 — 2026-11-13（周五 · 收盘版）

窗口：11/13 07:03 → 22:52（17 条）
关键新增：11/13 12:24「在C3低点的时候会有一批股提前见底。如近期端侧、人形机器人、GPU等……C3之后坚持以分批布局为主」
        11/13 15:12 收盘长文「3706 / 2626 都没有实现收复……周线看，市场属于ABC结构调整重的C杀尾段，
        个人策略偏向于分批承接或坚持为主，不在杀跌的尾段杀跌」
        11/13 12:37「昨晚借利空消息扫货英伟达（试了148.8美元，收在166.19美元）……接下来等待反弹到200美元」

行情口径：Tushare Pro，11/13 收盘（个股前复权）
配色：A 股惯例 红涨绿跌
关键点位：K 线图居左虚线标注
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


MC_UP = "#e63946"
MC_DOWN = "#2a9d8f"
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_BBOX = "#dbeafe"

C_BLOG = "#1f6feb"    # 博主门槛
C_MA = "#9ca3af"      # 当日结构
C_EXT = "#e11d48"     # 极值 / 硬门槛
C_PREV = "#334155"    # 昨收参考

for fp in ["/System/Library/Fonts/PingFang.ttc",
           "/System/Library/Fonts/STHeiti Medium.ttc",
           "/System/Library/Fonts/STHeiti Light.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
DAILY = json.loads((CHART_DIR / "_daily_20261113.json").read_text(encoding="utf-8"))


def compute_macd(df, fast=12, slow=26, signal=9):
    dif = df["Close"].ewm(span=fast, adjust=False).mean() - \
        df["Close"].ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, (dif - dea) * 2


def _spread_positions(values, min_gap):
    out, prev = {}, None
    for v in values:
        y = v if prev is None else max(v, prev + min_gap)
        out[v] = y
        prev = y
    return out


def draw_levels(ax, levels, color="#1f6feb", min_gap_frac=0.054, n_cols=2):
    """水平关键位虚线 + 居左文字标签（防重叠 + 双列错落）。"""
    ylo, yhi = ax.get_ylim()
    span = yhi - ylo
    min_gap = span * min_gap_frac
    ordered = sorted(levels, key=lambda t: t[0])
    pos = _spread_positions([v for v, _ in ordered], min_gap)

    col_of, cur_col_y = {}, [-np.inf, -np.inf]
    for v, _ in ordered:
        y = pos[v]
        for c in range(n_cols):
            if y - cur_col_y[c] >= min_gap:
                col_of[v] = c
                cur_col_y[c] = y
                break
        else:
            c = int(np.argmin(cur_col_y))
            col_of[v] = c
            cur_col_y[c] = y

    col_x = [-0.006, -0.118]
    for v, lbl in ordered:
        lc, ls = color, "--"
        if isinstance(lbl, tuple):
            parts = lbl
            lbl = parts[0]
            lc = parts[1]
            if len(parts) > 2:
                ls = parts[2]
        ax.axhline(v, color=lc, linestyle=ls, linewidth=0.9, alpha=0.85, zorder=1)
        c = col_of[v]
        y = pos[v]
        x = col_x[c]
        if abs(y - v) > span * 0.004:
            ax.plot([x, x + 0.006], [y, v], color=lc, lw=0.6, alpha=0.55,
                    zorder=4, clip_on=False, transform=ax.get_yaxis_transform())
        ax.text(
            x, y, f"  {lbl} {v:g}  ",
            va="center", ha="right", fontsize=8.3, color=lc,
            transform=ax.get_yaxis_transform(),
            bbox=dict(boxstyle="round,pad=0.25", fc=MC_BBOX, ec="#93c5fd", lw=0.6),
            zorder=5, clip_on=False,
        )


def plot_one(ts_code, name, levels, out_path, days=60, title_suffix="", band=None):
    rows = DAILY.get(ts_code)
    if not rows:
        print(f"  [skip] {ts_code} 无数据")
        return None
    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.tail(days).reset_index(drop=True)
    df = df.set_index("Date")

    dif, dea, macd = compute_macd(df)
    last_close = df["Close"].iloc[-1]
    last_date = df.index[-1].strftime("%Y-%m-%d")
    prev_close = df["Close"].iloc[-2]
    pct = (last_close / prev_close - 1) * 100
    pct_s = f"{pct:+.2f}%"
    ma5 = df["Close"].rolling(5).mean()
    ma10 = df["Close"].rolling(10).mean()
    ma20 = df["Close"].rolling(20).mean()

    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit",
                               wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE,
        facecolor=MC_FACE,
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
        mpf.make_addplot(macd.where(macd >= 0, other=np.nan), type="bar", panel=2,
                         color=MC_UP, secondary_y=False),
        mpf.make_addplot(macd.where(macd < 0, other=np.nan), type="bar", panel=2,
                         color=MC_DOWN, secondary_y=False),
    ]

    title = (f"{name} ({ts_code.replace('.', '_')}) 日线 · K线 + MACD + 成交量{title_suffix} · "
             f"收 {last_close:.2f} ({pct_s}) · {last_date}")

    fig, axes = mpf.plot(
        df, type="candle", volume=True,
        addplot=add_plots, style=style,
        figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
        title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0,
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

    try:
        _o, _c, _pc = df["Open"].iloc[-1], df["Close"].iloc[-1], df["Close"].iloc[-2]
        _gap = (_c / _pc - 1) * 100
        _span = df["High"].max() - df["Low"].min()
        _note = None
        if _c >= _o and _c < _pc:
            _note = f"低开高走\n收>{_o:.2f} 但较昨收 {_gap:+.2f}%"
        elif _c < _o and _c > _pc:
            _note = f"高开回落\n收<开{_o:.2f} 但较昨收 {_gap:+.2f}%"
        elif _c < _o and _c < _pc:
            _note = f"低开低走\n收{_c:.2f} 较昨收 {_gap:+.2f}%"
        if _note:
            ax_main.annotate(
                _note,
                xy=(len(df) - 1, df["High"].iloc[-1]),
                xytext=(len(df) - 17, df["High"].iloc[-1] + _span * 0.13),
                fontsize=8.5, color="#b45309",
                bbox=dict(boxstyle="round,pad=0.32", fc="#fffbeb", ec="#f59e0b", lw=0.9),
                arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=1.0),
                zorder=6,
            )
    except Exception:
        pass

    if band:
        lo, hi = band[0], band[1]
        ax_main.axhspan(lo, hi, color="#bfdbfe", alpha=0.18, zorder=0)
    draw_levels(ax_main, levels)

    ax_vol = axes[2]
    for i, (idx, row) in enumerate(df.iterrows()):
        c = MC_UP if row["Close"] >= row["Open"] else MC_DOWN
        ax_vol.patches[i].set_facecolor(c)
        ax_vol.patches[i].set_edgecolor(c)
        ax_vol.patches[i].set_alpha(0.85)

    axes[3].axhline(0, color="#9ca3af", linewidth=0.6, linestyle="-")

    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")
    _shift = 0.075
    for _ax in axes:
        _pos = _ax.get_position()
        _ax.set_position([_pos.x0 + _shift, _pos.y0, _pos.width - _shift, _pos.height])
    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根, 收 {last_close:.2f} {pct_s})")

    return {
        "code": ts_code, "name": name, "close": round(float(last_close), 2),
        "pct": round(pct, 2), "date": last_date,
        "open": round(float(df["Open"].iloc[-1]), 2),
        "high": round(float(df["High"].iloc[-1]), 2),
        "low": round(float(df["Low"].iloc[-1]), 2),
        "prev_close": round(float(prev_close), 2),
        "ma5": round(ma5.iloc[-1], 2), "ma10": round(ma10.iloc[-1], 2),
        "ma20": round(ma20.iloc[-1], 2),
        "dif": round(dif.iloc[-1], 3), "dea": round(dea.iloc[-1], 3),
        "macd_bar": round(macd.iloc[-1], 3),
        "hi60": round(df["High"].tail(60).max(), 2),
        "lo60": round(df["Low"].tail(60).min(), 2),
        "vol": float(df["Volume"].iloc[-1]),
        "vol_ma5": round(df["Volume"].rolling(5).mean().iloc[-1], 2),
        "png": out_path.name,
    }


if __name__ == "__main__":
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[charts] {CHART_DIR}")
    sfx = " (11/13 收)"

    targets = [
        ("000001.SH", "上证指数",
         [(3706.00, ("博主门槛 3706", C_BLOG)),
          (3669.44, ("11/13最高", C_MA)),
          (3634.35, ("11/13收盘", C_BLOG)),
          (3623.84, ("11/13最低", C_MA)),
          (3574.27, ("60日低", C_EXT))],
         "000001_SH_20261113.png"),
        ("399006.SZ", "创业板指",
         [(2626.00, ("博主门槛 2626", C_BLOG)),
          (2528.99, ("11/13最高", C_MA)),
          (2426.08, ("11/13收盘", C_BLOG)),
          (2417.22, ("11/13最低", C_MA)),
          (2376.28, ("60日低", C_EXT))],
         "399006_SZ_20261113.png"),
        ("688256.SH", "寒武纪",
         [(1170.00, ("60日高", C_EXT)),
          (1033.18, ("11/13最高", C_MA)),
          (978.88, ("11/13收盘", C_BLOG)),
          (968.01, ("11/13最低", C_MA)),
          (750.01, ("60日低", C_EXT))],
         "688256_SH_20261113.png"),
        ("603893.SH", "瑞芯微",
         [(237.37, ("60日高", C_EXT)),
          (228.00, ("11/13最高", C_MA)),
          (217.80, ("11/13收盘", C_BLOG)),
          (215.65, ("11/13最低", C_MA)),
          (159.34, ("60日低", C_EXT))],
         "603893_SH_20261113.png"),
        ("688836.SH", "宇树科技",
         [(1100.00, ("60日高", C_EXT)),
          (718.70, ("11/13最高", C_MA)),
          (696.00, ("11/13收盘", C_BLOG)),
          (689.20, ("11/13最低", C_MA)),
          (404.03, ("60日低", C_EXT))],
         "688836_SH_20261113.png"),
    ]

    kpi = {}
    for code, name, levels, png in targets:
        r = plot_one(code, name, levels, CHART_DIR / png, title_suffix=sfx)
        if r:
            kpi[code] = r

    (CHART_DIR / "_kpi_20261113.json").write_text(
        json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] {CHART_DIR/'_kpi_20261113.json'}")
