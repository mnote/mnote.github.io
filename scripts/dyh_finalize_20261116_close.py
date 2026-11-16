"""都业华 2026-11-16 收评 · 数据收尾（补今日K线 / 除权修正 / 成交额口径）

- 同花顺个股日线在收盘后仍停在 11/13，需用同花顺 realhead 快照补 11/16 那根
- 个别标的今日除权（如长盈精密），需按「新浪昨收 ÷ 同花顺 11/13 收盘」修正历史序列
- 两市成交额：沪=上证指数额、深=深证成指额（同花顺口径，与新浪完全一致）
  11/16 用 realhead 快照，11/13 用同花顺日线

输出：就地改写 reports/duyiehua-20261116/data_20261116_close.json
"""
import json
import re
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
DATE = "20261116"

STOCKS = {
    "药明康德": "603259", "中国船舶": "600150", "瑞芯微": "603893",
    "伊利股份": "600887", "中文在线": "300364", "海天瑞声": "688787",
    "奥普特": "688686", "柯力传感": "603662", "兆易创新": "603986",
    "模塑科技": "000700", "长盈精密": "300115", "云铝股份": "000807",
}
IDX = {"上证指数": "zs_1A0001", "深证成指": "zs_399001", "创业板指": "zs_399006",
       "沪深300": "zs_1B0300", "科创50": "zs_1B0688", "中证500": "zs_1B0905"}


def ths_realhead(code, tries=4):
    url = f"https://d.10jqka.com.cn/v6/realhead/{code}/last.js"
    for i in range(tries):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                         timeout=20).read().decode()
            return json.loads(re.search(r"\((.*)\)", raw, re.S).group(1))
        except Exception as e:
            print(f"  retry {code} {str(e)[:60]}")
            time.sleep(1.2 + i)
    return {"items": {}}


def norm(it):
    f = lambda k: float(it.get(k) or 0)
    return {"open": f("7"), "prev": f("6"), "price": f("10"), "high": f("8"),
            "low": f("9"), "vol": f("13"), "amount": f("19"),
            "time": it.get("updateTime", "")}


d = json.loads((RPT / "data_20261116_close.json").read_text(encoding="utf-8"))

# ---- 1) 指数：realhead 快照补今日 K 线 + 成交额 ----
print("== 指数 realhead ==")
for name, code in IDX.items():
    it = ths_realhead(code)["items"]
    if not it:
        continue
    s = norm(it)
    rows = d["series"].setdefault(name, [])
    bar = {"d": DATE, "o": s["open"], "h": s["high"], "l": s["low"],
           "c": s["price"], "v": s["vol"], "amt": s["amount"]}
    if rows and rows[-1]["d"] == DATE:
        rows[-1] = bar
    else:
        rows.append(bar)
    pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    d["index"].setdefault(name + "_sina", {}).update({
        "open": s["open"], "high": s["high"], "low": s["low"], "close": s["price"],
        "prev_close": s["prev"], "pct": pct, "amount_yi": round(s["amount"] / 1e8, 1),
        "vol_yi": round(s["vol"] / 1e8, 1), "time": s["time"]})
    print(f"  {name} {s['price']:.2f} {pct:+.2f}% amt={s['amount']/1e8:.0f}亿 "
          f"vol={s['vol']/1e8:.2f}亿股 t={s['time']}")

# ---- 2) 个股：realhead 补今日 K 线 + 除权修正 ----
print("== 个股 realhead ==")
for name, code in STOCKS.items():
    it = ths_realhead("hs_" + code)["items"]
    if not it:
        continue
    s = norm(it)
    rows = d["series"].setdefault(name, [])
    # 除权修正：新浪/同花顺快照的昨收（除权后参考价） vs 日线最后一根收盘（未复权）
    if rows and s["prev"]:
        ratio = s["prev"] / rows[-1]["c"] if rows[-1]["c"] else 1.0
        if abs(ratio - 1) > 0.002:
            for r in rows:
                for k in ("o", "h", "l", "c"):
                    r[k] = round(r[k] * ratio, 4)
                r["amt"] = round(r["amt"] * ratio, 2)
            d["stocks"][name]["ex_rights_factor"] = round(ratio, 6)
            print(f"  {name} 除权修正 factor={ratio:.4f} (11/13 收 {rows[-1]['c']/ratio:.2f})")
    bar = {"d": DATE, "o": s["open"], "h": s["high"], "l": s["low"],
           "c": s["price"], "v": s["vol"], "amt": s["amount"]}
    if rows and rows[-1]["d"] == DATE:
        rows[-1] = bar
    else:
        rows.append(bar)
    pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    d["stocks"][name]["snap"] = {"open": s["open"], "high": s["high"], "low": s["low"],
                                 "close": s["price"], "prev_close": s["prev"], "pct": pct,
                                 "vol": s["vol"], "amount_yi": round(s["amount"] / 1e8, 2),
                                 "time": s["time"]}
    print(f"  {name} {s['price']:.2f} {pct:+.2f}% H{s['high']:.2f} L{s['low']:.2f} "
          f"amt={s['amount']/1e8:.2f}亿 vol={s['vol']/1e8:.2f}亿股 t={s['time']}")

# ---- 3) 两市成交额 ----
sh = d["index"]["上证指数_sina"]["amount_yi"]
sz = d["index"]["深证成指_sina"]["amount_yi"]
prev = 0.0
for nm in ("上证指数", "深证成指"):
    rows = d["series"].get(nm) or []
    for r in rows:
        if r["d"] == "20261113":
            prev += r["amt"] / 1e8
total = round(sh + sz, 1)
d["amount"] = {"sh_yi": sh, "sz_yi": sz, "total_yi": total,
               "prev_total_yi": round(prev, 1),
               "growth_pct": round((total / prev - 1) * 100, 1),
               "scope": "全日（同花顺指数口径：沪市=上证指数额，深市=深证成指额；与新浪逐分一致）"}
print("== 成交额 ==", d["amount"])

# ---- 4) 日线重算摘要（指数/个股，含 60 日高低、均量）----
def summarize(rows):
    if not rows:
        return None
    last, prevr = rows[-1], rows[-2]
    w60, w20, w5 = rows[-60:], rows[-20:], rows[-5:]
    return {"date": last["d"], "open": last["o"], "high": last["h"], "low": last["l"],
            "close": last["c"], "prev_close": prevr["c"],
            "pct": round((last["c"] / prevr["c"] - 1) * 100, 2),
            "vol": last["v"], "amt": last["amt"],
            "hi60": max(r["h"] for r in w60), "lo60": min(r["l"] for r in w60),
            "vol_ma5": round(sum(r["v"] for r in w5) / 5, 0),
            "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0)}


for name in IDX:
    if name in d["series"]:
        s = summarize(d["series"][name])
        s["code"] = IDX[name]
        d["index"][name] = s
for name in STOCKS:
    if name in d["series"]:
        s = summarize(d["series"][name])
        s["code"] = STOCKS[name]
        d["stocks"][name].update(s)

# ---- 5) 涨跌停行业分布 ----
import collections
d["pool_hybk"] = {k: collections.Counter(x.get("hybk", "?")
                                        for x in d["pools"][k]["pool"]).most_common()
                  for k in ("zt", "dt", "zb")}

(RPT / "data_20261116_close.json").write_text(
    json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", RPT / "data_20261116_close.json")
