"""校验 11/11 图表最后一根 K 线的颜色是否与 open/close 一致（A 股惯例：close>=open 红）。

11/11 未收盘，OHLC 取自东方财富实时快照（charts/_quote_20261111.json）。
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

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


kpi = {x["code"]: x for x in
       json.loads((CHARTS / "_kpi_20261111.json").read_text(encoding="utf-8"))}

results = []
for png in sorted(CHARTS.glob("*_20261111.png")):
    code = png.name.split("_")[0] + "." + png.name.split("_")[1].split("_")[0]
    k = kpi.get(code)
    if not k:
        print(f"  [skip] {png.name} 无 KPI")
        continue
    expect_up = k["open"] is not None and k["close"] >= k["open"]

    im = Image.open(png).convert("RGB")
    a = np.array(im)
    H, W = a.shape[:2]
    red = close_mask(a, MC_UP)
    green = close_mask(a, MC_DOWN)

    # 主图区：上 60% 找最右侧实体簇
    main_h = int(H * 0.60)
    cr = clusters(np.where(red[:main_h, :].any(axis=0))[0])
    cg = clusters(np.where(green[:main_h, :].any(axis=0))[0])
    x_red = cr[-1][1] if cr else -1
    x_green = cg[-1][1] if cg else -1
    is_red = x_red > x_green

    # 成交量面板：中间 25% 区域，取最右侧柱色
    vr = np.where(red[int(H * 0.60):int(H * 0.80), :].any(axis=0))[0]
    vg = np.where(green[int(H * 0.60):int(H * 0.80), :].any(axis=0))[0]
    vol_is_red = (vr.max() if len(vr) else -1) > (vg.max() if len(vg) else -1)

    ok = (is_red == expect_up) and (vol_is_red == expect_up)
    results.append({
        "code": code, "png": png.name, "date": k["date"],
        "open": k["open"], "close": k["close"], "prev_close": k["prev_close"],
        "pct": k["pct"], "expect_red": bool(expect_up),
        "chart_red": bool(is_red), "vol_red": bool(vol_is_red),
        "match": bool(ok),
    })

print(f"{'代码':<12}{'开':>10}{'收':>10}{'昨收':>10}{'涨跌':>9}  "
      f"{'应为':<6}{'K线':<6}{'量柱':<6}{'一致'}")
for r in results:
    print(f"{r['code']:<12}{r['open']:>10.2f}{r['close']:>10.2f}{r['prev_close']:>10.2f}"
          f"{r['pct']:>8}%  {'红' if r['expect_red'] else '绿':<6}"
          f"{'红' if r['chart_red'] else '绿':<6}{'红' if r['vol_red'] else '绿':<6}"
          f"{'✅' if r['match'] else '❌'}")

print()
for r in results:
    if r["expect_red"] and r["pct"] < 0:
        print(f"⚠️  {r['code']}: 日跌 {r['pct']}% 但收({r['close']})>开({r['open']}) "
              f"→ 低开高走，按开/收判定为阳线(红)")
    if not r["expect_red"] and r["pct"] > 0:
        print(f"⚠️  {r['code']}: 日涨 {r['pct']}% 但收({r['close']})<开({r['open']}) "
              f"→ 高开回落，按开/收判定为阴线(绿)")
print(f"\n合计 {sum(1 for r in results if r['match'])}/{len(results)} 一致")
Path("/tmp/kcolor_check_20261111.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2))
