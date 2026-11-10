"""校验各图表最后一根 K 线的颜色是否与 open/close 一致（A 股惯例：close>=open 红）。"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import tushare as ts
from PIL import Image

TOKEN = os.environ.get("TUSHARE_TOKEN", "a4d50551c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")
pro = ts.pro_api(TOKEN)
CHARTS = Path("/Users/maoling/workspace/mnote.github.io/charts")
MC_UP = (230, 57, 70)
MC_DOWN = (42, 157, 143)


def close_mask(a, rgb, tol=25):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (abs(r - rgb[0]) < tol) & (abs(g - rgb[1]) < tol) & (abs(b - rgb[2]) < tol)


def clusters(cols, gap=3):
    if not len(cols):
        return []
    out, s, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > gap:
            out.append((s, prev))
            s = c
        prev = c
    out.append((s, prev))
    return out


def ohlc(code):
    is_idx = code.endswith((".SH", ".SZ")) and code.startswith(("000", "399"))
    df = (pro.index_daily(ts_code=code, start_date="20260101", end_date="20261110")
          if code in {"000001.SH", "399006.SZ", "000300.SH"}
          else pro.daily(ts_code=code, start_date="20260101", end_date="20261110"))
    df = df.sort_values("trade_date")
    return df


results = []
for png in sorted(CHARTS.glob("*_20261110.png")):
    code = png.name.split("_")[0] + "." + png.name.split("_")[1].split("_")[0]
    df = ohlc(code)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    expect_up = last["close"] >= last["open"]

    im = Image.open(png).convert("RGB")
    a = np.array(im)
    red = close_mask(a, MC_UP)
    green = close_mask(a, MC_DOWN)
    # 主图区：找出最右侧实体簇（红/绿中 x 更大者所在簇）
    main_red, main_green = red[:520, :], green[:520, :]
    cr = clusters(np.where(main_red.any(axis=0))[0])
    cg = clusters(np.where(main_green.any(axis=0))[0])
    last_red = cr[-1] if cr else None
    last_green = cg[-1] if cg else None
    x_red = last_red[1] if last_red else -1
    x_green = last_green[1] if last_green else -1
    is_red = x_red > x_green
    # 成交量面板最右侧柱
    vr = np.where(red[540:700, :].any(axis=0))[0]
    vg = np.where(green[540:700, :].any(axis=0))[0]
    vol_is_red = (vr.max() if len(vr) else -1) > (vg.max() if len(vg) else -1)

    ok = (is_red == expect_up) and (vol_is_red == expect_up)
    results.append({
        "code": code, "png": png.name,
        "date": last["trade_date"],
        "open": round(float(last["open"]), 2), "close": round(float(last["close"]), 2),
        "prev_close": round(float(prev["close"]), 2),
        "pct_chg": round(float(last["pct_chg"]), 2),
        "expect_red": bool(expect_up), "chart_red": bool(is_red), "vol_red": bool(vol_is_red),
        "match": bool(ok),
    })

print(f"{'代码':<12}{'日期':<10}{'开':>10}{'收':>10}{'昨收':>10}{'日涨跌':>9}  "
      f"{'应为':<6}{'K线':<6}{'量柱':<6}{'一致'}")
for r in results:
    print(f"{r['code']:<12}{r['date']:<10}{r['open']:>10}{r['close']:>10}"
          f"{r['prev_close']:>10}{r['pct_chg']:>8}%  "
          f"{'红' if r['expect_red'] else '绿':<6}"
          f"{'红' if r['chart_red'] else '绿':<6}"
          f"{'红' if r['vol_red'] else '绿':<6}"
          f"{'✅' if r['match'] else '❌'}")

print()
for r in results:
    if r["expect_red"] and r["pct_chg"] < 0:
        print(f"⚠️  {r['code']} {r['date']}: 日跌 {r['pct_chg']}% 但收({r['close']})>开({r['open']}) "
              f"→ 低开高走，按开/收判定为阳线(红)")
Path("/tmp/kcolor_check.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
