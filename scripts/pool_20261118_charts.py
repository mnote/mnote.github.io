"""类二买共振股池 2026-11-18 · 指标计算 + 日线 K 线图（红涨绿跌，白底）
输出：reports/pool-20261118/pool_stats.json + charts/{code}_POOL_20261118.png
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
from matplotlib.lines import Line2D

warnings.filterwarnings("ignore")
REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/pool-20261118"
CHART_DIR = REPO / "charts"
POOL = json.loads((RPT / "pool.json").read_text(encoding="utf-8"))

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_HI, C_LO, C_ENTRY = "#1f6feb", "#7c3aed", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10


def stats(s):
    rows = s["series"]
    df = pd.DataFrame(rows).rename(columns={"d": "Date", "o": "Open", "h": "High", "l": "Low",
                                            "c": "Close", "v": "Volume"})
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]
    win = df.tail(60)
    hi60, lo60 = float(win["High"].max()), float(win["Low"].min())
    last = float(df["Close"].iloc[-1])
    ma = {n: float(df["Close"].rolling(n).mean().iloc[-1]) for n in (5, 10, 20, 60)}
    vols = df["Volume"].tolist()
    vr = vols[-1] / (sum(vols[-5:]) / 5)
    dif = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_now, macd_prev = dif.iloc[-1] - dea.iloc[-1], dif.iloc[-2] - dea.iloc[-2]
    cross = "金叉" if macd_prev <= 0 < macd_now else ("死叉" if macd_prev >= 0 > macd_now else
                                                    ("多头" if macd_now > 0 else "空头"))
    # 最近 20 日出现过 MACD 金叉的日期
    dif20, dea20 = dif.tail(25), dea.tail(25)
    d = dif20 - dea20
    gold = [str(d.index[i].date()) for i in range(1, len(d)) if d.iloc[i - 1] <= 0 < d.iloc[i]]
    hi_date = str(win["High"].idxmax().date())
    return dict(
        df=df, close=round(last, 2), hi60=round(hi60, 2), lo60=round(lo60, 2), hi_date=hi_date,
        from_hi=round((last / hi60 - 1) * 100, 1), from_lo=round((last / lo60 - 1) * 100, 1),
        ma5=round(ma[5], 2), ma10=round(ma[10], 2), ma20=round(ma[20], 2), ma60=round(ma[60], 2),
        above20=last > ma[20], above60=last > ma[60], vol_ratio=round(vr, 2),
        macd=cross, macd_dif=round(float(dif.iloc[-1]), 2), macd_dea=round(float(dea.iloc[-1]), 2),
        last_gold=gold[-1] if gold else "-",
        hi20=round(float(df["High"].tail(20).max()), 2),
        lo20=round(float(df["Low"].tail(20).min()), 2),
    )


def tag_of(st):
    """结构标签：距 60 日高 -2% 内 = 新高附近；站上 MA20+MA60 = 中继向上；仅站上 MA20 = 修复中；其余破位"""
    if st["from_hi"] >= -2:
        return "新高附近"
    if st["above20"] and st["above60"]:
        return "中继向上"
    if st["above20"]:
        return "修复中"
    return "破位区"


def plot(s, st):
    df = st["df"].tail(60)
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE, facecolor=MC_FACE,
        rc={"axes.edgecolor": "#9ca3af", "axes.linewidth": 0.6,
            "font.sans-serif": ["PingFang SC", "Microsoft YaHei", "Heiti SC", "SimHei"]})
    dif = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    macd = (dif - dea) * 2
    ap = [
        mpf.make_addplot(ma5, panel=0, color="#f59e0b", width=0.8),
        mpf.make_addplot(ma10, panel=0, color="#8b5cf6", width=0.8),
        mpf.make_addplot(ma20, panel=0, color="#0ea5e9", width=0.9),
        mpf.make_addplot(dif, panel=2, color="#f59e0b", width=1.0, ylabel="MACD"),
        mpf.make_addplot(dea, panel=2, color="#1d4ed8", width=1.0),
        mpf.make_addplot(macd.where(macd >= 0, other=np.nan), type="bar", panel=2, color=MC_UP),
        mpf.make_addplot(macd.where(macd < 0, other=np.nan), type="bar", panel=2, color=MC_DOWN),
    ]
    title = (f"{s['name']} {s['code'].split('.')[0]} · 日线 K线 + MACD + 成交量（近 60 交易日）\n"
             f"{s['tag']} · 收 {st['close']:.2f} ({s['pct']:+.2f}%) · 距 60 日高 {st['from_hi']:+.1f}%"
             f" · 入池 {s['in_date'][4:6]}/{s['in_date'][6:]} 以来 {s['entry_pct']:+.1f}%")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=ap, style=style,
                         figsize=(13.0, 6.6), tight_layout=False, returnfig=True,
                         title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax = axes[0]
    ax.axhline(st["hi60"], color=C_HI, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax.axhline(s["entry_close"], color=C_ENTRY, linestyle=":", linewidth=1.0, alpha=0.9, zorder=1)
    handles = [
        Line2D([0], [0], color=C_HI, lw=1.6, ls="--", label=f"60日高 {st['hi60']:g}"),
        Line2D([0], [0], color=C_ENTRY, lw=1.6, ls=":", label=f"入池价 {s['entry_close']:g}"),
        Line2D([0], [0], color="#f59e0b", lw=1.4, label="MA5"),
        Line2D([0], [0], color="#8b5cf6", lw=1.4, label="MA10"),
        Line2D([0], [0], color="#0ea5e9", lw=1.4, label="MA20"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=9.5,
               handlelength=2.2, columnspacing=2.0, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.06)
    fname = f"{s['code'].replace('.', '_')}_POOL_20261118.png"
    fig.savefig(CHART_DIR / fname, dpi=105, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    return fname


res = []
for s in POOL:
    st = stats(s)
    s["tag"] = tag_of(st)
    s["chart"] = plot(s, st)
    s.update({k: v for k, v in st.items() if k != "df"})
    res.append(s)
    print(f"[chart] {s['name']:6s} {s['tag']:5s} 收{s['close']:7.2f} {s['pct']:+6.2f}% "
          f"距高{s['from_hi']:+6.1f}% MA20{'上' if s['above20'] else '下'} {s['macd']} 量比{s['vol_ratio']:.2f}")

(RPT / "pool_stats.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("done", len(res))
