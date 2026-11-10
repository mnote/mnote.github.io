"""
wu2198 报告 K 线图 + KPI 数据生成 — 2026-11-10（周二）

窗口：11/09 12:03（上期截断）→ 11/10 15:39
关键新增：11/10 10:04「目前三大人形机器人龙头领涨，龙大改写本轮新高，涨幅接近涨翻番了！」
        11/10 13:47「机构一直这么干的！不敢坚持板块发展方向，不懂分批布局的早就冼干净完了！」
        11/10 14:42「端侧今天够猛，两大龙头依然封板！」
        11/10 14:52「端侧虽然有几只连续改写新高的，但是还有磨在底部的，业绩增长速度明显了」
        11/10 14:56「不点评大盘，等待即可」
        11/10 06:26 早安帖：美股道指涨1104点 / 纳指涨673点 / 标普涨173点
        11/10 14:32「日本股市涨1684点，涨2.87%。韩国股市涨4.39%」
        11/09 18:40「上纬从大盘C3低点时至今已经涨了一倍多。宇树从大盘C3低点时至今涨了88%」

行情口径：Tushare Pro，11/10 收盘
配色：A 股惯例 红涨绿跌
关键点位：K 线图居左虚线标注
"""
import json
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

warnings.filterwarnings("ignore")


# ── 配色（A 股惯例：红涨绿跌 · 白底）────────────────────────────
MC_UP = "#e63946"
MC_DOWN = "#2a9d8f"
MC_WICK = "#666"
MC_GRID = "#e5e7eb"
MC_FACE = "#ffffff"
MC_BBOX = "#dbeafe"

C_BLOG = "#1f6feb"   # 博主点位
C_MA = "#9ca3af"     # 均线
C_EXT = "#e11d48"    # 极值 / 硬门槛
C_PREV = "#334155"   # 昨收参考线（跳空缺口）· 深石板灰，与各均线色不冲突

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

TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TUSHARE_TOKEN)
START = "20260101"
END = "20261110"

INDEX_CODES = {"000001.SH", "399006.SZ", "000300.SH", "000688.SH"}


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


def plot_one(ts_code: str, name: str, levels, out_path: Path, days: int = 60,
             title_suffix: str = "", band=None):
    df = fetch_daily(ts_code, days=days)
    if df.empty:
        print(f"  [skip] {ts_code} 无数据")
        return None
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
        # MACD 柱：零轴上红、零轴下绿（A 股惯例）
        # 用 NaN 屏蔽另一半，避免 where(other=...) 把负值也画成红柱
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

    # 颜色口径提示（两个方向都要标，否则读者会用「K 线颜色」反推「今天涨跌」）：
    #   ① 低开高走：收 >= 开（红/阳线）但较昨收下跌 —— 跳空缺口，红 K 不代表上涨
    #   ② 高开回落：收 < 开（绿/阴线）但较昨收上涨 —— 绿 K 不代表下跌
    try:
        _d = fetch_daily(ts_code, days=120)
        if len(_d) >= 2:
            _o, _c, _pc = _d["Open"].iloc[-1], _d["Close"].iloc[-1], _d["Close"].iloc[-2]
            _gap = (_c / _pc - 1) * 100
            _span = _d["High"].max() - _d["Low"].min()
            _note = None
            if _c >= _o and _c < _pc:
                _note = f"低开高走\n收>{_o:.2f} 但较昨收 {_gap:+.2f}%"
            elif _c < _o and _c > _pc:
                _note = f"高开回落\n收<开{_o:.2f} 但较昨收 {_gap:+.2f}%"
            if _note:
                ax_main.annotate(
                    _note,
                    xy=(len(df) - 1, _d["High"].iloc[-1]),
                    xytext=(len(df) - 17, _d["High"].iloc[-1] + _span * 0.13),
                    fontsize=8.5, color="#b45309",
                    bbox=dict(boxstyle="round,pad=0.32", fc="#fffbeb", ec="#f59e0b", lw=0.9),
                    arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=1.0),
                    zorder=6,
                )
    except Exception:
        pass

    if band:
        lo, hi, blbl = band
        # 支撑带用浅蓝底纹表示；上下沿已在左侧标签中标注，不再叠加文字（避免遮挡）
        ax_main.axhspan(lo, hi, color="#bfdbfe", alpha=0.18, zorder=0)
    draw_levels(ax_main, levels)

    ax_vol = axes[2]
    for i, (idx, row) in enumerate(df.iterrows()):
        c = MC_UP if row["Close"] >= row["Open"] else MC_DOWN
        ax_vol.patches[i].set_facecolor(c)
        ax_vol.patches[i].set_edgecolor(c)
        ax_vol.patches[i].set_alpha(0.85)

    axes[3].axhline(0, color="#9ca3af", linewidth=0.6, linestyle="-")

    # 左侧只留给「关键点位」标签：主图价格刻度与轴标题移到右侧（A股行情软件惯例）
    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")
    # 三个面板整体右移，给轴外的关键位标签腾出空间（否则会压住 Y 轴刻度数字）
    _shift = 0.075
    for _ax in axes:
        _pos = _ax.get_position()
        _ax.set_position([_pos.x0 + _shift, _pos.y0, _pos.width - _shift, _pos.height])
    fig.savefig(out_path, dpi=120, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {out_path.name}  ({len(df)} 根 K线, 收 {last_close:.2f} {pct_s})")

    return {
        "close": round(last_close, 2), "pct": round(pct, 2), "date": last_date,
        "open": round(df["Open"].iloc[-1], 2), "high": round(df["High"].iloc[-1], 2),
        "low": round(df["Low"].iloc[-1], 2),
        "ma5": round(ma5.iloc[-1], 2), "ma10": round(ma10.iloc[-1], 2),
        "ma20": round(ma20.iloc[-1], 2),
        "dif": round(dif.iloc[-1], 3), "dea": round(dea.iloc[-1], 3),
        "macd_bar": round(macd.iloc[-1], 3),
        "hi60": round(df["High"].tail(60).max(), 2),
        "lo60": round(df["Low"].tail(60).min(), 2),
        "hi20": round(df["High"].tail(20).max(), 2),
        "lo20": round(df["Low"].tail(20).min(), 2),
        "vol": float(df["Volume"].iloc[-1]),
        "vol_ma5": round(df["Volume"].rolling(5).mean().iloc[-1], 2),
    }


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[charts] 输出目录: {out_dir}")

    sufx = " (11/10 收)"
    targets = [
        ("000001.SH", "上证指数",
         [(3706.00, ("博主确认位", C_BLOG)),
          (3683.73, ("11/10最高", C_MA)),
          (3663.72, ("11/10收盘", C_BLOG)),
          (3650.00, ("三角下沿", C_EXT)),
          (3608.10, ("11/03低", C_MA)),
          (3574.27, ("60D低 / 10/23低", C_EXT))],
         (3608.10, 3650.00, "3608-3650"), sufx),
        ("399006.SZ", "创业板指",
         [(2599.80, ("MA20", C_MA)),
          (2520.01, ("11/10最高", C_MA)),
          (2494.40, ("11/10收盘", C_BLOG)),
          (2458.56, ("昨收", C_PREV, (0, (7, 3)))),
          (2438.72, ("11/06最低", C_MA)),
          (2376.28, ("60D低", C_EXT))],
         (2438.72, 2458.56, "2439-2459"), sufx),
        ("000300.SH", "沪深300",
         [(4136.80, ("11/05最高", C_MA)),
          (4090.44, ("MA20", C_MA)),
          (4090.38, ("11/10最高", C_MA)),
          (4059.11, ("11/10收盘", C_BLOG)),
          (4013.79, ("11/06最低", C_MA)),
          (3958.14, ("60D低", C_EXT))],
         (4013.79, 4056.11, "4014-4056"), sufx),
        ("688836.SH", "宇树科技",
         [(809.00, ("11/10最高", C_MA)),
          (761.01, ("11/10收盘", C_BLOG)),
          (716.00, ("昨收", C_PREV, (0, (7, 3)))),
          (693.93, ("MA5", C_MA)),
          (600.33, ("MA20", C_MA)),
          (404.03, ("上市低点 / C3区", C_EXT))],
         None,
         " (11/10 收 · 人形机器人龙头 · 博主点名)"),
        ("603893.SH", "瑞芯微",
         [(233.20, ("11/10收盘 涨停新高", C_BLOG)),
          (214.74, ("MA5", C_MA)),
          (212.00, ("昨收", C_PREV, (0, (7, 3)))),
          (201.03, ("MA10", C_MA)),
          (197.09, ("MA20", C_MA)),
          (159.34, ("60D低", C_EXT))],
         None,
         " (11/10 收 · 端侧AI芯片龙头 涨停)"),
        ("688585.SH", "上纬新材",
         [(236.00, ("11/10最高", C_MA)),
          (223.97, ("11/10开盘", C_MA)),
          (218.86, ("11/10收盘", C_BLOG)),
          (216.02, ("昨收", C_PREV, (0, (7, 3)))),
          (193.87, ("MA5", C_MA)),
          (102.68, ("60D低 / C3区", C_EXT))],
         None,
         " (11/10 收 · 机器人材料 · 博主点名)"),
    ]

    kpi = []
    for ts_code, name, levels, band, tsuf in targets:
        fn = f"{ts_code.replace('.', '_')}_20261110.png"
        try:
            stats = plot_one(ts_code, name, levels, out_dir / fn, band=band, title_suffix=tsuf)
            if stats:
                stats.update({"code": ts_code, "name": name,
                              "chart": f"/charts/{fn}",
                              "wu2198_levels": [{"price": v, "label": (l[0] if isinstance(l, tuple) else l)}
                                                for v, l in levels]})
                kpi.append(stats)
        except Exception as e:
            print(f"  [ERR] {fn}: {e}")

    kpi_path = out_dir / "_kpi_20261110.json"
    kpi_path.write_text(json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[kpi] {kpi_path}  ({len(kpi)} 项)")
