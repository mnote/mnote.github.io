"""都业华 2026-11-20 午评（高级班·午盘）· K 线图（日线，红涨绿跌，白底，关键位只画虚线+底部图例）

最后一根 = 2026-11-20 上午 11:30 未走完 K 线（腾讯 5 日分时点位 + 同花顺日线历史）
输出：charts/{code}_DY_20261120N.png
"""
import json
import subprocess
import time
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
RPT = REPO / "reports/duyiehua-20261120"
D = json.loads((RPT / "data_20261120.json").read_text(encoding="utf-8"))
SER = D["series"]
CHART_DIR = REPO / "charts"
SNAP = "11:30"
D8 = "20261120"

MC_UP, MC_DOWN, MC_WICK = "#e63946", "#2a9d8f", "#666"
MC_GRID, MC_FACE = "#e5e7eb", "#ffffff"
C_BLOG, C_EXT, C_SUP, C_PREV = "#1f6feb", "#e11d48", "#7c3aed", "#334155"

for fp in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]:
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "Heiti SC", "Hei", "SimHei", "STHeiti", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10


def sina_sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


def tx_morning(symbol):
    """腾讯 5 日分时 → 今日上午点位 + 11:30 累计量（手，×100 → 股）

    ⚠️ 入参必须是完整交易所前缀（如 sh000001），不能由 6 位代码推前缀：
       上证指数是 sh000001，而 000001 若按深市推会取到平安银行。
    """
    s = symbol
    url = f"https://web.ifzq.gtimg.cn/appstock/app/day/query?code={s}"
    for i in range(3):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "20", "-H", "User-Agent: Mozilla/5.0", url],
                               capture_output=True)
            j = json.loads(r.stdout.decode("utf-8", "ignore"))
            for day in j["data"][s]["data"]:
                d = str(day.get("date", ""))
                if d not in ("20261120", "2026-11-20"):
                    continue
                rows, am = day.get("data") or [], []
                amt1130 = vol1130 = None
                for row in rows:
                    p = row.split() if isinstance(row, str) else row
                    try:
                        t = str(p[0])
                        px, vol, amt = float(p[1]), float(p[2]), float(p[3])
                    except Exception:
                        continue
                    if t <= "1130":
                        am.append((t, px))
                        if t == "1130":
                            amt1130, vol1130 = amt, vol
                if not am:
                    continue
                cl = [px for t, px in am if t == "1130"]
                return {"o": am[0][1], "h": max(p for _, p in am), "l": min(p for _, p in am),
                        "c": cl[-1] if cl else am[-1][1],
                        "v": (vol1130 or 0) * 100, "amt": amt1130}
        except Exception:
            time.sleep(0.6 + i)
    return None


# name: (图文件名主键, 结构描述, [(值 or AUTO_HI/AUTO_LO, 说明, 颜色)])
SPEC = {
    "上证指数": ("000001_SH", "低开下探 · 上午低 3501.71 创 60 日新低 · 11:30 收 3521.40 带下影线 · 3620 未到", [
        (3620.0, "小级别中枢上沿压力", C_EXT), (3600.0, "放低确认标准", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "创业板指": ("399006_SZ", "低开下探 · 上午低 2223.57 创 60 日新低 · 11:30 微阳十字星", [
        ("AUTO_HI", "60日高", C_BLOG), ("AUTO_LO", "60日低", C_BLOG)]),
    "药明康德": ("603259_SH", "继续下跌 · 上午低 138.25 · 距 157.8 三买门槛差 19.51", [
        (157.8, "三买门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中国船舶": ("600150_SH", "弱势 -2.54% · 上午低 33.66 · 未翻过 36.75 压力", [
        (36.75, "上行确认位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "瑞芯微": ("603893_SH", "探低回升 · 低 181.12 收 188.00 · 超跌反弹非止跌", [
        (220.7, "前确认位", C_EXT), (208.0, "回调目标位", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "伊利股份": ("600887_SH", "逆势抗跌 -0.52% · 最高 33.05 逼近 60 日高 · 未破 31.9", [
        ("AUTO_HI", "60日高", C_BLOG), (31.9, "顶背驰触发位", C_SUP)]),
    "海天瑞声": ("688787_SH", "超跌反弹 +4.00% · 低 82.43 拉回 90.79 · 未出止跌", [
        (141.0, "突破门槛", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "兆易创新": ("603986_SH", "创新低 207.10 破 60 日低 · 距 224.6 中枢上沿差 14.79", [
        (233.0, "站稳位", C_EXT), (224.6, "中枢上沿压力", C_SUP), ("AUTO_LO", "60日低", C_BLOG)]),
    "华丰科技": ("688629_SH", "大阴线调整 -9.96% · 低 86.20 · 距 80.6 回调目标还差 5.58", [
        (80.6, "回调目标位", C_EXT), ("AUTO_LO", "60日低", C_BLOG)]),
    "中芯国际": ("688981_SH", "抗跌 +0.20% · 高 124.69 破 120.6 · 回抽确认未完成", [
        (120.6, "前高确认位", C_EXT), ("AUTO_HI", "60日高", C_BLOG)]),
}

# 腾讯代码 -> 股票代码
TXCODE = {"上证指数": "sh000001", "创业板指": "sz399006"}
for nm in ["药明康德", "中国船舶", "瑞芯微", "伊利股份", "海天瑞声",
           "兆易创新", "华丰科技", "中芯国际"]:
    TXCODE[nm] = sina_sym(D["stocks"][nm]["code"])


def to_df(name):
    rows = [dict(r) for r in SER[name][-60:]]
    m = tx_morning(TXCODE[name])
    if m:
        if rows and rows[-1]["d"] == D8:
            rows[-1].update({"o": m["o"], "h": m["h"], "l": m["l"], "c": m["c"],
                             "v": m["v"], "amt": m["amt"]})
        else:
            rows.append({"d": D8, "o": m["o"], "h": m["h"], "l": m["l"], "c": m["c"],
                         "v": m["v"], "amt": m["amt"]})
    df = pd.DataFrame(rows).rename(columns={"d": "Date", "o": "Open", "h": "High",
                                            "l": "Low", "c": "Close", "v": "Volume"})
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]


def compute_macd(df, fast=12, slow=26, signal=9):
    dif = df["Close"].ewm(span=fast, adjust=False).mean() - df["Close"].ewm(span=slow, adjust=False).mean()
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, (dif - dea) * 2


def resolve_levels(levels, df):
    hi, lo = float(df["High"].max()), float(df["Low"].min())
    out = []
    for v, lbl, lc in levels:
        if v == "AUTO_HI":
            v = round(hi, 2)
        elif v == "AUTO_LO":
            v = round(lo, 2)
        out.append((float(v), lbl, lc))
    return out


def add_legend(fig, levels):
    handles = [Line2D([0], [0], color=lc, lw=1.6, ls="--", label=f"{lbl} {v:g}")
               for v, lbl, lc in levels]
    fig.legend(handles=handles, loc="lower center",
               ncol=1 if len(handles) <= 2 else 2, frameon=False, fontsize=10,
               handlelength=2.2, columnspacing=2.4, bbox_to_anchor=(0.5, 0.0))


def plot_one(name, key, suffix, levels):
    df = to_df(name)
    levels = resolve_levels(levels, df)
    dif, dea, macd = compute_macd(df)
    last, prev = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    pct = (last / prev - 1) * 100
    ma5, ma10, ma20 = (df["Close"].rolling(n).mean() for n in (5, 10, 20))
    mc = mpf.make_marketcolors(up=MC_UP, down=MC_DOWN, edge="inherit", wick=MC_WICK, volume="inherit")
    style = mpf.make_mpf_style(
        marketcolors=mc, gridcolor=MC_GRID, gridstyle=":", figcolor=MC_FACE, facecolor=MC_FACE,
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
    title = (f"{name} {key} · 日线 K线 + MACD + 成交量（最后一根为 2026-11-20 {SNAP} 上午盘中，未走完）\n"
             f"{suffix} · 收 {last:.2f} ({pct:+.2f}%)")
    fig, axes = mpf.plot(df, type="candle", volume=True, addplot=add_plots, style=style,
                         figsize=(15.5, 8.8), tight_layout=False, returnfig=True,
                         title=title, ylabel="价格", ylabel_lower="成交量", xrotation=0)
    ax = axes[0]
    for v, lbl, lc in levels:
        ax.axhline(v, color=lc, linestyle="--", linewidth=1.0, alpha=0.9, zorder=1)
    ax.axhline(prev, color=C_PREV, linestyle=":", linewidth=0.9, alpha=0.9)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.055)
    add_legend(fig, levels)
    fname = f"{key}_DY_20261120N.png"
    out = CHART_DIR / fname
    fig.savefig(out, dpi=110, facecolor=MC_FACE, bbox_inches="tight")
    plt.close(fig)
    print(f"[chart] {name} -> {out.name}  {last:.2f} {pct:+.2f}%")
    return {"name": name, "code": key, "close": round(last, 2), "pct": round(pct, 2), "file": out.name}


meta = [plot_one(nm, k, sfx, lv) for nm, (k, sfx, lv) in SPEC.items()]
(RPT / "charts_20261120.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print("done", len(meta))
