"""都业华 2026-11-12 午评纪要 · K 线图生成（盘中版）

⛔ 只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。
K 线 = 前一交易日日线（Tushare 前复权）+ 今日实时未完成 K 线（新浪快照）。
A股惯例红涨绿跌、白底；关键位全部放底部图例，不画在图内。
输出：~/workspace/mnote.github.io/charts/{code}_DY_20261112.png
"""
import json
import os
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D
import mplfinance as mpf
import numpy as np
import pandas as pd
import tushare as ts

warnings.filterwarnings("ignore")

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_PREV = "#1f6feb", "#e11d48", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
START, END = "20260101", "20261111"
CHART_DIR = Path("/Users/maoling/workspace/mnote.github.io/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)
RPT = Path("/Users/maoling/workspace/mnote.github.io/reports/duyiehua-20261112")
D = json.loads((RPT / "data_20261112.json").read_text(encoding="utf-8"))
SNAP_TIME = D["snapshot_time"][-5:]
Q = {r["名称"]: r for r in D["quotes"]}
IX = D["index"]

# 图清单：名称 -> (ts_code, 副标题描述, 关键位[(值,标签,颜色)])
SPEC = {
    "上证指数": ("000001.SH", "偏弱震荡 · 未突破压力 3750 · 仍看成弱势", [
        (3750.0, "向上确认位", C_EXT),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "创业板指": ("399006.SZ", "冲高回落 · 科创强创业板弱 · 放量上冲后回落", [
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "药明康德": ("603259.SH", "对称震荡 · 结构不清晰 · 距买点差火候", [
        (151.0, "突破门槛", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中国船舶": ("600150.SH", "公告后高开 · 走势依旧没止跌 · 不操作", [
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "瑞芯微": ("603893.SH", "上午调整 · 倾向拉回小中枢震荡 · 下午观察", [
        (248.49, "三买确认位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "伊利股份": ("600887.SH", "相对抗跌 · 倾向跌破 30.46 后拉回 · 日线无有力度底分型", [
        (30.46, "支撑位（跌破后拉回）", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "中文在线": ("300364.SZ", "AI 视频 · 等突破前高 30.38 出三买 · 当下不满足", [
        (30.38, "前高突破位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "海天瑞声": ("688787.SH", "机器人 · 等对称震荡形成 · 当下尚未形成", [
        (155.50, "60日高(10/26)", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "奥普特": ("688686.SH", "机器视觉 · 等破 186.8 或回调到下沿 140 附近止跌", [
        (186.8, "突破位", C_EXT),
        (140.0, "回调目标位", C_EXT),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "柯力传感": ("603662.SH", "顶分型调整中 · 第一支撑 53 附近 · 调整不充分", [
        (53.0, "第一支撑位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "兆易创新": ("603986.SH", "分型确认中 · 临近上方短线压力 · 不要随意伸手", [
        (249.0, "止损参考", C_BLOG),
        (237.28, "11/09 新低", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "汉威科技": ("300007.SZ", "日线顶分型已出现 · 下午继续往下则短期出高点", [
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
    "长盈精密": ("300115.SZ", "类二买 · 等突破 32.08 后出三买 · 尚未突破", [
        (32.08, "突破位", C_EXT),
        ("AUTO_HI", "60日高", C_BLOG),
        ("AUTO_LO", "60日低", C_BLOG),
    ]),
}
# 额外关键位（用今日实时高低点）
TODAY_LV = {
    "上证指数": [("今日高", "C_EXT"), ("今日低", "C_BLOG")],
}


def fetch_daily(ts_code, days=120):
    is_index = ts_code in ("000001.SH", "399006.SZ", "399001.SZ", "000688.SH", "000300.SH")
    for _ in range(4):
        try:
            df = pro.index_daily(ts_code=ts_code, start_date=START, end_date=END) if is_index \
                 else pro.daily(ts_code=ts_code, start_date=START, end_date=END)
            if df is not None and not df.empty:
                break
        except Exception as e:
            print("retry", ts_code, e)
        import time; time.sleep(1.5)
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
        except Exception as e:
            print("adj fail", ts_code, e)
    df = df.tail(days).reset_index(drop=True).rename(columns={
        "trade_date": "Date", "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "vol": "Volume"})
    df["Volume"] = df["Volume"].astype(float)
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]


def compute_macd(df, fast=12, slow=26, signal=9):
    dif = df["Close"].ewm(span=fast, adjust=False).mean() - df["Close"].ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, (dif - dea) * 2


def resolve_levels(levels, df):
    out = []
    hi = float(df["High"].tail(60).max())
    lo = float(df["Low"].tail(60).min())
    for v, lbl, lc in levels:
        if v == "AUTO_HI":
            v = round(hi, 2)
        elif v == "AUTO_LO":
            v = round(lo, 2)
        out.append((float(v), lbl, lc))
    return out


def add_legend(fig, levels):
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}") for v, lbl, lc in levels]
    ncol = 1 if len(handles) <= 2 else 2
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False,
               fontsize=10, handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def snap_of(name):
    if name in Q:
        r = Q[name]
        return {"price": r["现价"], "high": r["最高"], "low": r["最低"], "open": r["开盘"],
                "prev": r["昨收"], "pct": r["涨跌幅%"], "vol": r["今日量(手)"]}
    if name in IX:
        s = IX[name]
        return {"price": s["price"], "high": s["high"], "low": s["low"], "open": s["open"],
                "prev": s["prev"], "pct": s["pct"], "vol": s["vol"] // 100}
    return None


def plot_one(name, ts_code, suffix, levels):
    df = fetch_daily(ts_code)
    if df.empty:
        print(f"[skip] {name}")
        return None
    s = snap_of(name)
    # 拼今日实时未完成 K 线
    if s:
        today = pd.DataFrame([{"Date": pd.Timestamp("2026-11-12"), "Open": s["open"],
                               "High": s["high"], "Low": s["low"], "Close": s["price"],
                               "Volume": s["vol"]}]).set_index("Date")
        df = pd.concat([df, today])
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])
    pct = (last_close / prev_close - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(marketcolors=mc, gridcolor=MC_GRID, gridstyle=":",
                               figcolor=MC_FACE, facecolor=MC_FACE,
                               rc={"axes.edgecolor": "#9ca3af", "axes.linewidth": 0.6,
                                   "font.family": "PingFang SC, Microsoft YaHei, Heiti SC, Hei, SimHei, sans-serif",
                                   "font.sans-serif": ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei"]})
    add_plots = [
        mpf.make_addplot(ma5, panel=0, color="#f59e0b", width=0.8),
        mpf.make_addplot(ma10, panel=0, color="#8b5cf6", width=0.8),
        mpf.make_addplot(ma20, panel=0, color="#0ea5e9", width=0.9),
        mpf.make_addplot(dif, panel=2, color="#f59e0b", width=1.0, ylabel="MACD"),
        mpf.make_addplot(dea, panel=2, color="#1d4ed8", width=1.0),
        mpf.make_addplot(macd.where(macd >= 0, other=np.nan), type="bar", panel=2, color=MC_UP),
        mpf.make_addplot(macd.where(macd < 0, other=np.nan), type="bar", panel=2, color=MC_DOWN),
    ]
    title = (f"{name} {ts_code} · 日线 K线 + MACD + 成交量（最后一根为盘中未完成 K 线）\n"
             f"{suffix} · 现 {last_close:.2f} ({pct:+.2f}%) · 截至 {SNAP_TIME}")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                          figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                          title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax_main = axes[0]
    for v, lbl, lc in levels:
        ax_main.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax_main.axhline(prev_close, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    out = CHART_DIR / f"{ts_code.replace('.', '_')}_DY_20261112.png"
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last_close:.2f} {pct:+.2f}%")
    return {"name": name, "code": ts_code, "close": round(last_close, 2),
            "pct": round(pct, 2), "file": out.name}


meta = []
for nm, (code, suffix, lv) in SPEC.items():
    r = plot_one(nm, code, suffix, lv)
    if r:
        meta.append(r)
(RPT / "charts.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False))
