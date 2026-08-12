#!/usr/bin/env python
"""wu2198 2026-08-12 投资日报 — 拉日线 + 画 K 线图(关键位居左虚线)"""
import os
import json
import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import tushare as ts
import mplfinance as mpf
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

warnings.filterwarnings("ignore")

# ── 中文字体: macOS 自带 PingFang SC + Windows/Linux 兜底 ──
for fp in [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Users/maoling/Library/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]:
    if os.path.exists(fp):
        try:
            font_manager.fontManager.addfont(fp)
        except Exception:
            pass
matplotlib.rcParams["font.sans-serif"] = [
    "PingFang SC", "Heiti SC", "Microsoft YaHei", "WenQuanYi Zen Hei",
    "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

OUT_DIR = os.path.expanduser("~/workspace/mnote.github.io/reports/wu2198-20260812")
CHART_DIR = os.path.join(OUT_DIR, "charts")
DATA_DIR = os.path.join(OUT_DIR, "data")
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ── 标的清单: (代码, 名称, 关键位 [(label, price, color)], 标题, 类型) ──
# 颜色: #52c41a 绿(已收复/支撑) / #f5222d 红(压力/目标) / #1890ff 蓝(当前) / #722ed1 紫(事件)
TARGETS = [
    # ───── 大盘 ─────
    {
        "ts_code": "000001.SH",
        "name": "上证指数",
        "title": "上证指数 (000001.SH) · B反未坏 · 阻力 3982/3996 · 支撑 3906/3886",
        "is_index": True,
        "levels": [
            ("B反起点 3741", 3741, "#52c41a"),
            ("支撑 3886", 3886, "#52c41a"),
            ("支撑 3906", 3906, "#52c41a"),
            ("阻力 3982", 3982, "#f5222d"),
            ("阻力 3996", 3996, "#fa541c"),
        ],
    },
    {
        "ts_code": "399006.SZ",
        "name": "创业板指",
        "title": "创业板指 (399006.SZ) · 收复 3590 · 关键 3626 · 拓展 3686",
        "is_index": True,
        "levels": [
            ("A杀底 3160", 3160, "#52c41a"),
            ("已收复 3590", 3590, "#52c41a"),
            ("关键 3626", 3626, "#f5222d"),
            ("目标 3686", 3686, "#fa541c"),
        ],
    },
    # ───── 板块 A: MLCC / 电容 (博主直接点名) ─────
    {
        "ts_code": "300408.SZ",
        "name": "三环集团",
        "title": "三环集团 (300408.SZ) · MLCC + 陶瓷封装龙头 · B反累计涨幅80% 主线",
        "levels": [
            ("B反起点 45", 45.75, "#52c41a"),
            ("平台支撑 90", 90.0, "#1890ff"),
            ("前高 150", 150.0, "#f5222d"),
        ],
    },
    {
        "ts_code": "000636.SZ",
        "name": "风华高科",
        "title": "风华高科 (000636.SZ) · MLCC 龙头 · 8/11+6.7% 8/12+1% 连续走强",
        "levels": [
            ("B反起点 16", 16.33, "#52c41a"),
            ("平台支撑 50", 50.0, "#1890ff"),
            ("前高压力 70", 70.0, "#f5222d"),
        ],
    },
    {
        "ts_code": "603678.SH",
        "name": "火炬电子",
        "title": "火炬电子 (603678.SH) · 军用 MLCC + 电容 · 突破 50 关口",
        "levels": [
            ("B反起点 30", 30.91, "#52c41a"),
            ("已突破 50", 50.0, "#1890ff"),
            ("前高 90", 90.0, "#f5222d"),
        ],
    },
    # ───── 板块 B: 创业板权重 / 锂电池 / 算力 (博主强调创业板领先) ─────
    {
        "ts_code": "300750.SZ",
        "name": "宁德时代",
        "title": "宁德时代 (300750.SZ) · 创业板第一权重 · 锂电池全球龙头",
        "levels": [
            ("A杀底 333", 333.01, "#52c41a"),
            ("B反阻力 410", 410.0, "#f5222d"),
        ],
    },
    {
        "ts_code": "300059.SZ",
        "name": "东方财富",
        "title": "东方财富 (300059.SZ) · 创业板权重 + 券商龙头 · B反人气标的",
        "levels": [
            ("B反起点 17", 17.22, "#52c41a"),
            ("B反阻力 22", 22.0, "#f5222d"),
        ],
    },
    # ───── 板块 C: 券商 / 大金融 (B反突破主力) ─────
    {
        "ts_code": "600030.SH",
        "name": "中信证券",
        "title": "中信证券 (600030.SH) · 券商龙头 · B反突破风向标",
        "levels": [
            ("B反起点 23", 23.77, "#52c41a"),
            ("B反阻力 30", 30.0, "#f5222d"),
        ],
    },
]


def fetch_one(ts_code, name, days=180, is_index=False):
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    pro = ts.pro_api()
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
    else:
        try:
            df = ts.pro_bar(
                ts_code=ts_code, start_date=start, end_date=end,
                adj="qfq", freq="D",
            )
        except Exception as e:
            print(f"  [pro_bar failed] {ts_code} {e}, fallback to daily")
            df = pro.daily(ts_code=ts_code, start_date=start, end_date=end)
    if df is None or df.empty:
        return None
    df = df.sort_values("trade_date").reset_index(drop=True)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.set_index("trade_date")
    keep = ["open", "high", "low", "close", "vol"]
    df = df[keep]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df


def calc_macd(df, fast=12, slow=26, signal=9):
    close = df["Close"]
    df["DIF"] = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    df["DEA"] = df["DIF"].ewm(span=signal, adjust=False).mean()
    df["MACD"] = (df["DIF"] - df["DEA"]) * 2
    return df


def make_chart(df, levels, title, out_path, mark_dates=None):
    df = calc_macd(df)
    df["Volume_Plot"] = df["Volume"] / 1e4

    hlines, hline_colors = [], []
    for label, price, color in (levels or []):
        if price is None:
            continue
        hlines.append(price)
        hline_colors.append(color)

    vlines_dict = {}
    if mark_dates:
        for d_str, label in mark_dates.items():
            d = pd.to_datetime(d_str)
            if d in df.index:
                vlines_dict[d] = label

    mc = mpf.make_marketcolors(
        up="r", down="g", edge="inherit",
        wick="inherit", volume="inherit",
    )
    style = mpf.make_mpf_style(
        marketcolors=mc, gridstyle="--", gridcolor="#d9d9d9",
        rc={
            "font.family": ["PingFang SC", "Heiti SC", "Microsoft YaHei",
                            "Noto Sans CJK SC", "SimHei", "DejaVu Sans"],
            "axes.unicode_minus": False,
        },
    )

    add_plots = [
        mpf.make_addplot(df["DIF"], panel=2, color="#fa8c16", width=1.2, ylabel="DIF"),
        mpf.make_addplot(df["DEA"], panel=2, color="#1890ff", width=1.2, ylabel="DEA"),
        mpf.make_addplot(
            df["MACD"], panel=2, type="bar",
            color=["#ef232a" if v >= 0 else "#14b143" for v in df["MACD"]],
            ylabel="MACD",
        ),
    ]

    fig, axes = mpf.plot(
        df, type="candle", style=style, title=title,
        ylabel="价格", volume=True, volume_panel=1,
        ylabel_lower="成交量(万手)", addplot=add_plots,
        panel_ratios=(4, 1.5, 2), figsize=(13, 7),
        hlines=dict(hlines=hlines, colors=hline_colors,
                    linestyle="--", linewidths=1.2),
        vlines=dict(vlines=list(vlines_dict.keys()),
                    colors=["#722ed1"] * len(vlines_dict),
                    linestyle=":", linewidths=1.5),
        returnfig=True,
    )

    # ── 关键位标签: 左对齐, 虚线已在 hlines 中画好 ──
    ax_price = axes[0]
    ymin, ymax = ax_price.get_ylim()
    xmin, xmax = ax_price.get_xlim()
    label_x = xmin + (xmax - xmin) * 0.005
    sorted_levels = sorted(
        [(l, p, c) for l, p, c in (levels or []) if p is not None],
        key=lambda t: t[1],
    )
    last_y = None
    min_gap = (ymax - ymin) * 0.05
    for label, price, color in sorted_levels:
        if not (ymin <= price <= ymax):
            continue
        y_pos = price
        if last_y is not None and abs(y_pos - last_y) < min_gap:
            y_pos = last_y + min_gap
        ax_price.annotate(
            f" {label} ({price:.0f})",
            xy=(label_x, y_pos), color=color, fontsize=10,
            fontweight="bold", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.9, linewidth=1.2),
        )
        last_y = y_pos

    for d, label in vlines_dict.items():
        try:
            x_pos = df.index.get_loc(d)
            ax_price.annotate(
                f" ▼ {label}",
                xy=(x_pos, ymax - (ymax - ymin) * 0.03),
                color="#722ed1", fontsize=9, fontweight="bold",
                ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#f9f0ff",
                          edgecolor="#722ed1", alpha=0.95, linewidth=1.2),
            )
        except Exception:
            pass

    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {out_path}")


def main():
    print(f"== wu2198 2026-08-12: fetch + chart for {len(TARGETS)} targets ==")
    summary = []
    for t in TARGETS:
        code = t["ts_code"]
        name = t["name"]
        print(f"[{code}] {name}")
        df = fetch_one(code, name, is_index=t.get("is_index", False))
        if df is None or df.empty:
            print(f"  [WARN] no data for {code}")
            continue
        csv_path = os.path.join(DATA_DIR, f"{code.replace('.', '_')}.csv")
        df.to_csv(csv_path)
        last_close = float(df["Close"].iloc[-1])
        last_date = df.index[-1].strftime("%Y-%m-%d")
        out = os.path.join(CHART_DIR, f"{code.replace('.', '_')}.png")
        try:
            make_chart(df, t.get("levels", []), t["title"], out,
                       mark_dates=t.get("mark_dates"))
        except Exception as e:
            print(f"  [CHART ERR] {e}")
            continue
        summary.append({
            "ts_code": code, "name": name, "title": t["title"],
            "last_close": last_close, "last_date": last_date,
            "chart": f"charts/{os.path.basename(out)}",
            "levels": t.get("levels", []),
        })

    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] summary -> {os.path.join(OUT_DIR, 'summary.json')}")


if __name__ == "__main__":
    main()
