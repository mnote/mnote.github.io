"""wu2198 报告 K 线图 — 2026-11-11（周三 · 收盘版）

窗口：11/10 15:39（上期截断）→ 11/11 收盘 + 盘后
关键新增：11/11 13:27「CPO、光纤、存储芯片接力反击。」
        11/11 13:56「大盘指数收复3706点，创业板指数收复2626点……之后，我们订KTV或白马……支持吗？」
        11/11 14:42「洗干净了就可以等起飞！」
        11/11 14:52「我们先退单吧，明天再订吧……」
        11/11 15:03「今天市场如期小时幅反弹，我们明天等大盘指数收复3706点，创业板指数收复2626点」
        11/11 16:22「及时有文章分析了的！第四浪的底部位置」

行情口径：Tushare Pro，11/11 收盘（前复权）
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

# ── 配色（A 股惯例：红涨绿跌 · 白底）────────────────────────────
MC_UP = "#e63946"
MC_DOWN = "#2a9d8f"
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_BBOX = "#dbeafe"

C_BLOG = "#1f6feb"   # 博主点位 / 博主门槛
C_MA = "#9ca3af"     # 均线 / 昨日结构
C_EXT = "#e11d48"    # 极值 / 硬门槛
C_PREV = "#334155"   # 昨收参考线

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

CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
DAILY = json.loads((CHART_DIR / "_daily_20261111c.json").read_text(encoding="utf-8"))


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
    """画水平关键位虚线 + 居左文字标签（防重叠 + 双列错落）。"""
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

    # 颜色口径提示：K 线颜色看「收 vs 开」，与「收 vs 昨收」可能相反
    try:
        _o, _c, _pc = df["Open"].iloc[-1], df["Close"].iloc[-1], df["Close"].iloc[-2]
        _gap = (_c / _pc - 1) * 100
        _span = df["High"].max() - df["Low"].min()
        _note = None
        if _c >= _o and _c < _pc:
            _note = f"低开高走\n收>{_o:.2f} 但较昨收 {_gap:+.2f}%"
        elif _c < _o and _c > _pc:
            _note = f"高开回落\n收<开{_o:.2f} 但较昨收 {_gap:+.2f}%"
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

    # 左侧只留给「关键点位」标签：主图价格刻度与轴标题移到右侧
    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")
    _shift = 0.075
    for _ax in axes:
        _pos = _ax.get_position()
        _ax.set_position([_pos.x0 + _shift, _pos.y0, _pos.width - _shift, _pos.height])
    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线, 收 {last_close:.2f} {pct_s})")

    return {
        "close": round(float(last_close), 2), "pct": round(pct, 2), "date": last_date,
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
    }


if __name__ == "__main__":
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[charts] {CHART_DIR}")

    sufx = " (11/11 收)"

    targets = [
        ("000001.SH", "上证指数",
         [(3706.00, ("博主门槛 11/09", C_BLOG)),
          (3689.65, ("11/11最高", C_MA)),
          (3680.64, ("11/11收盘", C_BLOG)),
          (3675.29, ("MA20", C_MA)),
          (3650.31, ("11/11最低", C_MA)),
          (3608.10, ("11/03低", C_MA)),
          (3574.27, ("60D低 / 10/23低", C_EXT))],
         (3650.31, 3668.85), sufx),

        ("399006.SZ", "创业板指",
         [(2626.00, ("博主门槛 11/11", C_BLOG)),
          (2585.06, ("MA20", C_MA)),
          (2580.34, ("11/11最高", C_MA)),
          (2572.07, ("11/11收盘", C_BLOG)),
          (2494.40, ("11/10收盘", C_MA)),
          (2458.56, ("11/09收盘", C_MA)),
          (2376.28, ("60D低", C_EXT))],
         (2490.10, 2511.41), sufx),

        ("000300.SH", "沪深300",
         [(4136.80, ("11/05最高", C_MA)),
          (4085.00, ("11/11最高", C_MA)),
          (4083.34, ("MA20", C_MA)),
          (4075.71, ("11/11收盘", C_BLOG)),
          (4051.31, ("MA10", C_MA)),
          (4035.40, ("11/11最低", C_MA)),
          (3958.14, ("60D低", C_EXT))],
         (4035.40, 4051.31), sufx),

        ("300308.SZ", "中际旭创",
         [(547.79, ("11/11最高", C_MA)),
          (542.00, ("11/11收盘", C_BLOG)),
          (510.50, ("MA10", C_MA)),
          (471.00, ("昨收 / 11/10收", C_PREV)),
          (427.34, ("11/06低 · 本轮底", C_EXT))],
         None, sufx + " · CPO龙头 · 博主10:58具名"),

        ("300502.SZ", "新易盛",
         [(216.35, ("11/11最高", C_MA)),
          (215.00, ("11/11收盘", C_BLOG)),
          (191.82, ("MA10", C_MA)),
          (183.80, ("昨收 / 11/10收", C_PREV)),
          (161.16, ("11/06低 · 本轮底", C_EXT))],
         None, sufx + " · CPO龙头 · 博主10:58具名"),

        ("603986.SH", "兆易创新",
         [(260.58, ("11/11最高", C_MA)),
          (259.62, ("11/11收盘", C_BLOG)),
          (256.62, ("MA10", C_MA)),
          (244.57, ("昨收 / 11/10收", C_PREV)),
          (237.28, ("11/09低 · 本轮底", C_EXT))],
         None, sufx + " · 存储芯片龙头 · 博主11:11具名"),
    ]

    kpi = []
    for ts_code, name, levels, band, tsuf in targets:
        fn = f"{ts_code.replace('.', '_')}_20261111.png"
        try:
            stats = plot_one(ts_code, name, levels, CHART_DIR / fn,
                             band=band, title_suffix=tsuf)
            if stats:
                stats.update({"code": ts_code, "name": name,
                              "chart": f"/charts/{fn}",
                              "wu2198_levels": [{"price": v, "label": (l[0] if isinstance(l, tuple) else l)}
                                                for v, l in levels]})
                kpi.append(stats)
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")

    kpi_path = CHART_DIR / "_kpi_20261111c.json"
    kpi_path.write_text(json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[kpi] {kpi_path}  ({len(kpi)} 项)")
