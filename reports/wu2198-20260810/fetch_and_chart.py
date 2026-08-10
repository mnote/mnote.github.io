#!/usr/bin/env python
"""Fetch daily K-line + draw chart with key levels for wu2198 report."""
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

# 中文字体: macOS 自带 PingFang SC,Windows 也有 fallback
for font_path in [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Users/maoling/Library/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]:
    if os.path.exists(font_path):
        try:
            font_manager.fontManager.addfont(font_path)
        except Exception:
            pass

matplotlib.rcParams["font.sans-serif"] = [
    "PingFang SC", "Heiti SC", "Microsoft YaHei", "WenQuanYi Zen Hei",
    "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

OUT_DIR = os.path.expanduser("~/workspace/mnote.github.io/reports/wu2198-20260810")
CHART_DIR = os.path.join(OUT_DIR, "charts")
DATA_DIR = os.path.join(OUT_DIR, "data")
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# 标的: (代码, 名称, 关键位 [(label, price, color)], 起点日期)
TARGETS = [
    {
        "ts_code": "000001.SH",
        "name": "上证指数",
        "title": "上证指数 (000001.SH) — 收 3966.59 · B 反未变 · 明天反击 3982/3996",
        "levels": [
            ("B反起点 3741", 3741, "#52c41a"),
            ("已收复 3856", 3856, "#52c41a"),
            ("已收复 3956", 3956, "#1890ff"),
            ("B反连线 3967", 3967, "#722ed1"),
            ("明天反击 3982", 3982, "#f5222d"),
            ("明天反击 3996", 3996, "#fa541c"),
        ],
    },
    {
        "ts_code": "301308.SZ",
        "name": "江波龙",
        "title": "江波龙 (301308.SZ) — 存储芯片龙头 · 中报营收+136% 归母+71528% (8/10 披露)",
        "levels": [
            ("中报披露 8/10", None, "#722ed1"),
        ],
        "mark_dates": {"20260810": "中报披露 8/10"},
    },
    {
        "ts_code": "603986.SH",
        "name": "兆易创新",
        "title": "兆易创新 (603986.SH) — 存储芯片 (长鑫科技纳入 MSCI 利好)",
        "levels": [],
    },
    {
        "ts_code": "002371.SZ",
        "name": "北方华创",
        "title": "北方华创 (002371.SZ) — 半导体设备龙头 (8/10 板块领先)",
        "levels": [],
    },
    {
        "ts_code": "688012.SH",
        "name": "中微公司",
        "title": "中微公司 (688012.SH) — 半导体刻蚀设备龙头",
        "levels": [],
    },
    {
        "ts_code": "600276.SH",
        "name": "恒瑞医药",
        "title": "恒瑞医药 (600276.SH) — 化学制药/创新药龙头",
        "levels": [],
    },
    {
        "ts_code": "000661.SZ",
        "name": "长春高新",
        "title": "长春高新 (000661.SZ) — 生物制品龙头",
        "levels": [],
    },
]


def fetch_one(ts_code, name, days=180, is_index=False):
    """Fetch daily K-line. 指数走 index_daily, 个股走 pro_bar."""
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    pro = ts.pro_api()
    if is_index:
        df = pro.index_daily(ts_code=ts_code, start_date=start, end_date=end)
    else:
        try:
            df = ts.pro_bar(
                ts_code=ts_code,
                start_date=start,
                end_date=end,
                adj="qfq",
                freq="D",
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
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    df["DIF"] = ema_fast - ema_slow
    df["DEA"] = df["DIF"].ewm(span=signal, adjust=False).mean()
    df["MACD"] = (df["DIF"] - df["DEA"]) * 2
    return df


def make_chart(df, levels, title, out_path, mark_dates=None):
    """Draw K-line + volume + MACD with key levels as left-anchored dashed lines."""
    df = calc_macd(df)

    # Convert Volume to shares (万股) for readability
    df["Volume_Plot"] = df["Volume"] / 1e4

    # Build horizontal level lines spanning the whole chart
    hlines = []
    hline_colors = []
    for label, price, color in (levels or []):
        if price is None:
            continue
        hlines.append(price)
        hline_colors.append(color)

    # Mark event date with a vertical line + text
    vlines_dict = {}
    if mark_dates:
        for d_str, label in mark_dates.items():
            d = pd.to_datetime(d_str)
            if d in df.index:
                vlines_dict[d] = label

    # Add mplfinance panels: main (candle + MA), volume, MACD
    mc = mpf.make_marketcolors(
        up="r", down="g", edge="inherit",
        wick="inherit", volume="inherit",
    )
    style = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle="--",
        gridcolor="#d9d9d9",
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
        df,
        type="candle",
        style=style,
        title=title,
        ylabel="价格",
        volume=True,
        volume_panel=1,
        ylabel_lower="成交量(万手)",
        addplot=add_plots,
        panel_ratios=(4, 1.5, 2),
        figsize=(13, 7),
        hlines=dict(
            hlines=hlines,
            colors=hline_colors,
            linestyle="--",
            linewidths=1.2,
        ),
        vlines=dict(
            vlines=list(vlines_dict.keys()),
            colors=["#722ed1"] * len(vlines_dict),
            linestyle=":",
            linewidths=1.5,
        ),
        returnfig=True,
    )

    # Annotate horizontal level labels on the LEFT side of the price panel
    ax_price = axes[0]
    ymin, ymax = ax_price.get_ylim()
    xmin, xmax = ax_price.get_xlim()
    # Place label at leftmost x position
    label_x = xmin + (xmax - xmin) * 0.005
    # Sort levels by price so nearby ones get offset vertically
    sorted_levels = sorted(
        [(l, p, c) for l, p, c in (levels or []) if p is not None],
        key=lambda t: t[1],
    )
    last_y = None
    min_gap = (ymax - ymin) * 0.05  # 5% of y range
    for label, price, color in sorted_levels:
        if not (ymin <= price <= ymax):
            continue
        # If too close to last label, nudge up
        y_pos = price
        if last_y is not None and abs(y_pos - last_y) < min_gap:
            y_pos = last_y + min_gap
        ax_price.annotate(
            f" {label} ({price:.0f})",
            xy=(label_x, y_pos),
            color=color,
            fontsize=10,
            fontweight="bold",
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.9, linewidth=1.2),
        )
        last_y = y_pos

    # Annotate vline event labels (top of price panel)
    for d, label in vlines_dict.items():
        try:
            x_pos = df.index.get_loc(d)
            ax_price.annotate(
                f" ▼ {label}",
                xy=(x_pos, ymax - (ymax - ymin) * 0.03),
                color="#722ed1",
                fontsize=9,
                fontweight="bold",
                ha="center",
                va="top",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#f9f0ff",
                          edgecolor="#722ed1", alpha=0.95, linewidth=1.2),
            )
        except Exception:
            pass

    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt_close = __import__("matplotlib.pyplot", fromlist=["close"]).close
    plt_close(fig)
    print(f"  saved {out_path}")


def main():
    pro = ts.pro_api()
    print(f"== wu2198 report: fetch + chart for {len(TARGETS)} targets ==")
    summary = []
    for t in TARGETS:
        code = t["ts_code"]
        name = t["name"]
        print(f"[{code}] {name}")
        df = fetch_one(code, name, is_index=code.endswith(".SH") and code.startswith("000") or code.startswith("399"))
        if df is None or df.empty:
            print(f"  [WARN] no data for {code}")
            continue
        # Save raw data
        csv_path = os.path.join(DATA_DIR, f"{code.replace('.', '_')}.csv")
        df.to_csv(csv_path)
        last_close = float(df["Close"].iloc[-1])
        last_date = df.index[-1].strftime("%Y-%m-%d")
        # Draw chart
        out = os.path.join(CHART_DIR, f"{code.replace('.', '_')}.png")
        try:
            make_chart(
                df, t.get("levels", []), t["title"], out,
                mark_dates=t.get("mark_dates"),
            )
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
