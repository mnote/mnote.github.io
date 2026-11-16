"""都业华 2026-11-16 午评 · 补充同花顺实时快照（统一量纲：个股/指数 vol 均为「股」）

把 realhead 的今日 OHLC + 量额写入 data_20261116.json 的 snapshot 字段，
并用同花顺口径替换新浪快照（新浪指数 vol 单位为手，与日线不同源）。
输出：仍为 reports/duyiehua-20261116/data_20261116.json
"""
import json
import re
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
DATE = "2026-11-16"

IDX = {"上证指数": "zs_1A0001", "深证成指": "zs_399001", "创业板指": "zs_399006",
       "沪深300": "zs_1B0300", "科创50": "zs_1B0688"}
STOCKS = {
    "药明康德": "603259", "中国船舶": "600150", "瑞芯微": "603893",
    "伊利股份": "600887", "中文在线": "300364", "海天瑞声": "688787",
    "奥普特": "688686", "柯力传感": "603662", "兆易创新": "603986",
    "模塑科技": "000700", "长盈精密": "300115", "云铝股份": "000807",
}


def ths(code, tries=4):
    url = f"https://d.10jqka.com.cn/v6/realhead/{code}/last.js"
    import time
    for i in range(tries):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read().decode()
            return json.loads(re.search(r"\((.*)\)", raw, re.S).group(1))
        except Exception as e:
            print(f"  retry {code} {str(e)[:50]}")
            time.sleep(1.2 + i)
    return {"items": {}}


def norm(it):
    """同花顺快照字段号：6 昨收 / 7 开 / 8 高 / 9 低 / 10 现价 / 13 量 / 19 额"""
    f = lambda k: float(it.get(k) or 0)
    return {
        "open": f("7"), "prev": f("6"), "price": f("10"),
        "high": f("8"), "low": f("9"),
        "vol": f("13"), "amount": f("19"),
        "time": it.get("updateTime", ""),
    }


d = json.loads((RPT / "data_20261116.json").read_text(encoding="utf-8"))

for name, code in IDX.items():
    it = ths(code)["items"]
    s = norm(it)
    s["name"] = it.get("name", "")
    s["pct"] = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    d["snapshot"][name] = s
    d["index"][name + "_snap"] = s
    # 用同花顺口径重写今日那根 K 线（vol=股）
    rows = d["series"].get(name) or []
    if rows:
        rows[-1].update({"o": s["open"], "h": s["high"], "l": s["low"],
                          "c": s["price"], "v": s["vol"], "amt": s["amount"]})
    print(f"IDX {name} {s['price']:.2f} {s['pct']:+.2f}% H{s['high']:.2f} L{s['low']:.2f} amt={s['amount']/1e8:.0f}亿")

for name, code in STOCKS.items():
    it = ths("hs_" + code)["items"]
    s = norm(it)
    s["name"] = it.get("name", "")
    s["pct"] = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    d["snapshot"][name] = s
    d["stocks"][name]["snap"] = s
    rows = d["series"].get(name) or []
    if rows:
        rows[-1].update({"o": s["open"], "h": s["high"], "l": s["low"],
                          "c": s["price"], "v": s["vol"], "amt": s["amount"]})
    print(f"STK {name} {s['price']:.2f} {s['pct']:+.2f}% H{s['high']:.2f} L{s['low']:.2f} amt={s['amount']/1e8:.2f}亿")

# 两市成交额：同花顺指数 amount（沪市全市场 + 深市全市场）
sh_amt = d["snapshot"]["上证指数"]["amount"]
sz_amt = d["snapshot"]["深证成指"]["amount"]
d["amount"] = {"sh_yi": round(sh_amt / 1e8, 1), "sz_yi": round(sz_amt / 1e8, 1),
               "total_yi": round((sh_amt + sz_amt) / 1e8, 1), "scope": "11:30 上午累计"}
print("两市上午成交", d["amount"])

(RPT / "data_20261116.json").write_text(
    json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved")
