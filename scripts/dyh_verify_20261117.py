"""都业华 2026-11-17 午评 · 关键位核验（日线触达判据）"""
import json
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261117"
D = json.loads((RPT / "data_20261117.json").read_text(encoding="utf-8"))
B = json.loads((RPT / "breadth_20261117.json").read_text(encoding="utf-8"))
raw = D["snapshot_raw"]

print("=" * 70)
print("【指数】")
for name, s in D["index"].items():
    if name.endswith("_snap"):
        print(f"  {name[:-5]:8s} 现{s['close']:.2f} {s['pct']:+.2f}% 开{s['open']:.2f} "
              f"高{s['high']:.2f} 低{s['low']:.2f} 昨收{s['prev_close']:.2f} @{s['time']}")
for nm in ("上证指数", "深证成指", "创业板指", "沪深300", "科创50"):
    st = D["index"].get(nm)
    if st:
        print(f"  日线 {nm}: 昨收{st['close']:.2f} 高{st['high']:.2f} 低{st['low']:.2f} "
              f"60日高{st['hi60']:.2f} 60日低{st['lo60']:.2f}")
for sym, nm in (("sh000680", "科创综指"), ("sh000905", "中证500")):
    s = raw.get(sym)
    if s:
        print(f"  {nm}: {s['price']:.2f} {(s['price']/s['prev']-1)*100:+.2f}% "
              f"高{s['high']:.2f} 低{s['low']:.2f}")

print("\n【上证关键位】")
sh = D["index"]["上证指数_snap"]
ser = D["series"]["上证指数"]
prev_rows = [r for r in ser if r["d"] == "20261116"]
print(f"  11/16 日线: O{prev_rows[0]['o']:.2f} H{prev_rows[0]['h']:.2f} "
      f"L{prev_rows[0]['l']:.2f} C{prev_rows[0]['c']:.2f}")
print(f"  今日 O{sh['open']:.2f} H{sh['high']:.2f} L{sh['low']:.2f} C{sh['close']:.2f}")
print(f"  今日低 {sh['low']:.2f} vs 11/16 低 {prev_rows[0]['l']:.2f} → 创新低? {sh['low'] < prev_rows[0]['l']}")
print(f"  今日高 {sh['high']:.2f} vs 昨日上午高 3623.12 → 翻过? {sh['high'] > 3623.12}")
print(f"  今日高 {sh['high']:.2f} vs 3750 → 差 {3750 - sh['high']:.2f} 点")
print(f"  自日内低点回升 {(sh['close'] - sh['low']) / sh['low'] * 100:.2f}%")
w60 = [r for r in ser if r["d"] != "20261117"][-60:]
print(f"  60日低(不含今日) {min(r['l'] for r in w60):.2f}；今日低 {sh['low']:.2f} → "
      f"{'跌破' if sh['low'] < min(r['l'] for r in w60) else '未破'}（60日低 {min(r['l'] for r in w60):.2f}）")

print("\n【成交额同时点同比】")
tx = D["tx_amount"]
for k in ("sh", "sz"):
    for d, v in sorted(tx.get(k, {}).items()):
        a1130 = v.get("amt_1130")
        print(f"  {k} {d} 11:30累计 {a1130/1e8 if a1130 else None:.1f} 亿" if a1130 else f"  {k} {d} 无 11:30")
sh1130 = tx["sh"]["20261117"]["amt_1130"] / 1e8
sh1130_prev = tx["sh"]["20261116"]["amt_1130"] / 1e8
sz1130 = tx["sz"]["20261117"]["amt_1130"] / 1e8
sz1130_prev = tx["sz"]["20261116"]["amt_1130"] / 1e8
print(f"  两市 11:30 合计 {sh1130 + sz1130:.1f} 亿 vs 11/16 {sh1130_prev + sz1130_prev:.1f} 亿 "
      f"→ {((sh1130 + sz1130) / (sh1130_prev + sz1130_prev) - 1) * 100:+.2f}%")
print(f"  沪 {sh1130:.1f} vs {sh1130_prev:.1f} ({(sh1130/sh1130_prev-1)*100:+.2f}%) | "
      f"深 {sz1130:.1f} vs {sz1130_prev:.1f} ({(sz1130/sz1130_prev-1)*100:+.2f}%)")
print(f"  13:25 累计两市 {D['amount']['total_yi']} 亿（沪 {D['amount']['sh_yi']} + 深 {D['amount']['sz_yi']}）")
prev_amt = D.get("prev_day", {})
print(f"  11/16 全天: 沪 {prev_amt.get('上证指数',{}).get('20261116',{}).get('amt_yi')} 亿 / "
      f"深 {prev_amt.get('深证成指',{}).get('20261116',{}).get('amt_yi')} 亿")

print("\n【宽度】", B)
print("\n【涨跌停池】")
for k, p in D["pools"].items():
    print(f"  {k}: {p['tc']}")
from collections import Counter
ztc = Counter(x.get("hybk") for x in D["pools"]["zt"]["pool"])
print("  涨停行业:", ztc.most_common(12))
dtc = Counter(x.get("hybk") for x in D["pools"]["dt"]["pool"])
print("  跌停行业:", dtc.most_common(10))
print("  涨停名单:", [(x.get("c"), x.get("n"), x.get("zdp")) for x in D["pools"]["zt"]["pool"]][:60])
print("  跌停名单:", [(x.get("c"), x.get("n"), x.get("zdp")) for x in D["pools"]["dt"]["pool"]][:40])

print("\n【篮子】")
for b, v in sorted(D["baskets"].items(), key=lambda x: -x[1]["avg_pct"]):
    print(f"  {b:12s} {v['avg_pct']:+6.2f}%  涨{v['up']}/跌{v['down']}/共{v['n']}  "
          f"额{v['amount_yi']}亿")
    for m in v["members"]:
        print(f"      {m['code']} {m['name']:8s} {m['pct']:+6.2f}% 收{m['close']:.2f} "
              f"低{m['low']:.2f} 高{m['high']:.2f}")

print("\n【个股关键位核验】")
LEVELS = {
    "药明康德": [157.8, ("三买门槛", 157.8)],
    "中国船舶": [],
    "瑞芯微": [208.0, 237.37],
    "伊利股份": [30.46],
    "中文在线": [30.38, 25.65],
    "海天瑞声": [141.0, 155.5],
    "奥普特": [186.8, 140.0],
    "柯力传感": [53.0],
    "兆易创新": [233.0, 237.28],
    "模塑科技": [14.95, 17.69],
    "长盈精密": [32.08],
}
for name, st in D["stocks"].items():
    s = st.get("snap")
    if not s:
        print(f"  {name} 无快照")
        continue
    ser2 = D["series"][name]
    w60 = [r for r in ser2 if r["d"] != "20261117"][-60:]
    hi60 = max(r["h"] for r in w60)
    lo60 = min(r["l"] for r in w60)
    prev = [r for r in ser2 if r["d"] == "20261116"]
    prev_hi = prev[0]["h"] if prev else None
    prev_lo = prev[0]["l"] if prev else None
    lv = LEVELS.get(name, [])
    lvs = ", ".join(f"{x}" for x in lv if isinstance(x, float))
    print(f"  {name}({st['code']}) 现{s['close']:.2f} {s['pct']:+.2f}% "
          f"开{s['open']:.2f} 高{s['high']:.2f} 低{s['low']:.2f} | 昨H{prev_hi} 昨L{prev_lo} | "
          f"60日高{hi60:.2f} 低{lo60:.2f} | 关键位 {lvs}")
    for x in lv:
        if isinstance(x, float):
            print(f"      位 {x}: 最高{s['high']:.2f} {'触达+'+str(round(s['high']-x,2)) if s['high']>=x else '未触(差'+str(round(x-s['high'],2))+')'} | "
                  f"最低{s['low']:.2f} {'跌破'+str(round(x-s['low'],2)) if s['low']<=x else '未破(差'+str(round(s['low']-x,2))+')'}")
