"""wu2198 报告 K 线图 — 2026-11-17（周二 · 收盘后增补版）

增量：22:02「重新杀进来」建仓表态 + 10:28「CPO 龙头 1416.88→385（-72.82%）」自验证。
行情口径：**Tushare Pro 日线**（pro.daily / pro.index_daily），个股前复权（adj_factor）。
配色：A 股惯例 红涨绿跌。关键位：K 线图居左虚线。
输出：charts/{code}_20261117.png + charts/_kpic_20261117c.json
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

C_BLOG = "#1f6feb"    # 博主门槛 / 博主点位
C_MA = "#9ca3af"      # 当日结构
C_EXT = "#e11d48"     # 极值 / 硬门槛

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
TS = json.loads((CHART_DIR / "_ts_20261117.json").read_text(encoding="utf-8"))


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
    rows = TS["rows"].get(ts_code)
    if not rows:
        print(f"  [skip] {ts_code} 无数据")
        return None
    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["trade_date"])
    df = df.tail(days).reset_index(drop=True).set_index("Date")
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low",
                            "close": "Close", "vol": "Volume"})

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
        if _c >= _o and _c < _pc:
            _note = f"盘中探低回升\n收>{_o:.2f} 但较昨收 {_gap:+.2f}%"
        elif _c < _o and _c > _pc:
            _note = f"高开回落\n收<开{_o:.2f} 但较昨收 {_gap:+.2f}%"
        elif _c < _o and _c < _pc:
            _note = f"低开\n现{_c:.2f} 较昨收 {_gap:+.2f}%"
        else:
            _note = f"盘中上涨\n现{_c:.2f} 较昨收 {_gap:+.2f}%"
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
    for i, (_idx, row) in enumerate(df.iterrows()):
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
        "code": ts_code, "name": name,
        "close": round(float(last_close), 2), "pct": round(pct, 2),
        "prev_close": round(float(prev_close), 2),
        "open": float(df["Open"].iloc[-1]), "high": float(df["High"].iloc[-1]),
        "low": float(df["Low"].iloc[-1]),
        "ma5": round(float(ma5.iloc[-1]), 2), "ma10": round(float(ma10.iloc[-1]), 2),
        "ma20": round(float(ma20.iloc[-1]), 2),
        "dif": round(float(dif.iloc[-1]), 3), "dea": round(float(dea.iloc[-1]), 3),
        "macd_bar": round(float(macd.iloc[-1]), 3),
        "png": out_path.name,
    }


if __name__ == "__main__":
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[charts] {CHART_DIR}  收盘增补版 (Tushare 日线)")
    sfx = " (11/17 收)"

    def lv(v, lbl, c):
        return (round(float(v), 2), (lbl, c))

    sh = TS["indexes"]["000001.SH"]
    cy = TS["indexes"]["399006.SZ"]
    mt = TS["stocks"]["600519.SH"]
    hx = TS["stocks"]["688256.SH"]
    zh = TS["stocks"]["002179.SZ"]

    targets = [
        ("000001.SH", "上证指数",
         [lv(3706.00, "博主门槛 3706", C_BLOG),
          lv(sh["ma20"], "MA20", C_MA),
          lv(sh["prev_close"], "11/16收盘", C_MA),
          lv(sh["close"], "11/17收盘", C_BLOG),
          lv(3574.27, "60日低(前)", C_EXT),
          lv(sh["low"], "60日新低", C_EXT)],
         "000001_SH_20261117.png"),
        ("399006.SZ", "创业板指",
         [lv(2626.00, "博主门槛 2626", C_BLOG),
          lv(cy["ma20"], "MA20", C_MA),
          lv(cy["prev_close"], "11/16收盘", C_MA),
          lv(cy["close"], "11/17收盘", C_BLOG),
          lv(2308.90, "11/16新低", C_EXT),
          lv(cy["low"], "她的2263点", C_EXT)],
         "399006_SZ_20261117.png"),
        ("600519.SH", "贵州茅台",
         [lv(mt["hi60"], "60日高", C_EXT),
          lv(mt["close"], "11/17收盘", C_BLOG),
          lv(mt["ma20"], "MA20", C_MA),
          lv(mt["lo60"], "60日低", C_EXT)],
         "600519_SH_20261117.png"),
        ("688256.SH", "寒武纪",
         [lv(hx["hi60"], "60日高", C_EXT),
          lv(hx["close"], "11/17收盘", C_BLOG),
          lv(hx["ma20"], "MA20", C_MA),
          lv(hx["lo60"], "60日低", C_EXT)],
         "688256_SH_20261117.png"),
        ("002179.SZ", "中航光电",
         [lv(zh["ma20"], "MA20", C_MA),
          lv(zh["close"], "11/17收盘", C_BLOG),
          lv(zh["lo60"], "60日低", C_EXT)],
         "002179_SZ_20261117.png"),
        ("600036.SH", "招商银行",
         [lv(TS["stocks"]["600036.SH"]["hi60"], "60日高", C_EXT),
          lv(TS["stocks"]["600036.SH"]["close"], "11/17收盘", C_BLOG),
          lv(TS["stocks"]["600036.SH"]["ma20"], "MA20", C_MA)],
         "600036_SH_20261117.png"),
    ]
    # 招行只作「底仓垫」文字引用，报告未嵌图 → 不生成 png（避免孤立文件）
    targets = [t for t in targets if t[4] != "600036_SH_20261117.png"]

    out = {}
    for code, name, levels, png in targets:
        r = plot_one(code, name, levels, CHART_DIR / png, title_suffix=sfx)
        if r:
            r.update({k: v for k, v in TS["indexes"].get(code, TS["stocks"].get(code, {})).items()
                      if k in ("ma5", "ma10", "ma20", "hi60", "lo60", "vol_ratio5",
                               "amount_yi", "dist_hi60", "dist_lo60", "gap_3706",
                               "gap_2626", "gap_3706_pct", "gap_2626_pct")})
            out[code] = r

    # 新易盛：CPO 龙头，10:28「1416.88 → 385，-72.82%」自验证标的
    cpo = TS["cpo_check"]["300308.SZ"]
    cpo_rows = TS["rows"].get("300308.SZ")
    if cpo_rows:
        out["300308.SZ"] = {
            "code": "300308.SZ", "name": "新易盛",
            "close": cpo["close"], "pct": cpo["pct_chg"],
            "high": cpo["high"], "low": cpo["low"],
            "ma20": cpo["ma20"], "hi60": cpo["hi60"], "lo60": cpo["lo60"],
            "peak_high": cpo["peak_high"], "peak_date": cpo["peak_date"],
            "png": "300308_SZ_20261117.png",
        }
        r = plot_one("300308.SZ", "新易盛",
                     [lv(1416.88, "她说的1416.88", C_BLOG),
                      lv(cpo["ma20"], "MA20", C_MA),
                      lv(cpo["close"], "11/17收盘", C_BLOG),
                      lv(385.00, "她说的385", C_EXT),
                      lv(cpo["lo60"], "60日新低", C_EXT)],
                     CHART_DIR / "300308_SZ_20261117.png", title_suffix=" (11/17 收)")
        if r:
            r.update(out["300308.SZ"])
            r["amount_yi"] = cpo.get("amount_yi")
            r["vol_ratio5"] = cpo.get("vol_ratio5")
            out["300308.SZ"] = r

    (CHART_DIR / "_kpic_20261117c.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] {CHART_DIR/'_kpic_20261117c.json'}")
