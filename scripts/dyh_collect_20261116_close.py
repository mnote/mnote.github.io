"""都业华 2026-11-16 收评（高级班）· 收盘数据采集

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。

数据源：
  - 同花顺公开接口（免登录）：日线 https://d.10jqka.com.cn/v6/line/{code}/01/last.js
  - 新浪批量快照（收盘）：https://hq.sinajs.cn/list=...
  - 新浪行业板块榜：https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php
  - 东财 push2ex 涨停/跌停/炸板池（收盘定格）

输出：reports/duyiehua-20261116/data_20261116_close.json
      reports/duyiehua-20261116/ind_20261116_close.json
"""
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
RPT.mkdir(parents=True, exist_ok=True)
DATE = "2026-11-16"
D8 = "20261116"

THS_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
SINA_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
EM_UA = ["User-Agent: Mozilla/5.0", "Referer: https://quote.eastmoney.com/"]

IDX = {
    "上证指数": "zs_1A0001",
    "深证成指": "zs_399001",
    "创业板指": "zs_399006",
    "沪深300": "zs_1B0300",
    "科创50": "zs_1B0688",
    "中证500": "zs_1B0905",
}

STOCKS = {
    "药明康德": "603259", "中国船舶": "600150", "瑞芯微": "603893",
    "伊利股份": "600887", "中文在线": "300364", "海天瑞声": "688787",
    "奥普特": "688686", "柯力传感": "603662", "兆易创新": "603986",
    "模塑科技": "000700", "长盈精密": "300115", "云铝股份": "000807",
}

# 自建篮子（成分逐一列出，报告内必须可核对）
BASKETS = {
    "银行": ["600036", "601398", "601939", "601288", "601166"],
    "电力/高股息": ["600900", "600025", "600886", "600674", "601985"],
    "煤炭/石油": ["601088", "600028", "601857", "600938", "601808"],
    "AI视频/传媒": ["300364", "300133", "300182", "300251", "603533",
                "300418", "601595"],
    "半导体": ["603893", "603986", "688256", "688041", "688981", "002371"],
    "算力/CPO": ["601138", "300308", "300502", "002463", "300476"],
    "人形机器人": ["000700", "300115", "002050", "601689", "688017",
               "603728", "003021", "603009", "300124"],
    # 本期新增：老师点名的证券 / 防守 / 玄学链
    "证券": ["600030", "601066", "601688", "600837", "601211", "000776", "601878"],
    "家电/小家电": ["000333", "000651", "002032", "002508", "603868"],
    "保险": ["601318", "601601", "601336", "601628"],
    "公路铁路": ["600350", "601006", "601333", "600377", "601816"],
    "白酒": ["600519", "000858", "000568", "600809", "603369"],
    "玄学链·东方系": ["603366", "600327", "600075", "603706", "002086",
                "000530", "002611", "000721"],
    "羊字辈": ["300532", "300740"],
}

# 新浪快照补充指数（老师原文口径用到）
SINA_IDX = {
    "上证指数": "sh000001", "深证成指": "sz399001", "创业板指": "sz399006",
    "沪深300": "sh000300", "科创50": "sh000688", "中证500": "sh000905",
    "科创综指": "sh000680", "证券公司": "sz399975", "深证综指": "sz399106",
}


def log(*a):
    print(*a, flush=True)


def ths_kline(code, tries=4):
    url = f"https://d.10jqka.com.cn/v6/line/{code}/01/last.js"
    for i in range(tries):
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers=THS_UA), timeout=25).read().decode()
            j = json.loads(re.search(r"\((.*)\)", raw, re.S).group(1))
            rows = []
            for line in j["data"].split(";"):
                f = line.split(",")
                if len(f) < 7:
                    continue
                rows.append({
                    "d": f[0], "o": float(f[1]), "h": float(f[2]), "l": float(f[3]),
                    "c": float(f[4]), "v": float(f[5]), "amt": float(f[6]),
                })
            return j.get("name", ""), rows
        except Exception as e:
            log(f"  retry ths {code} {str(e)[:60]}")
            time.sleep(1.0 + i)
    return "", []


def sina_snapshot(symbols, tries=3):
    out = {}
    for i in range(0, len(symbols), 40):
        chunk = symbols[i:i + 40]
        url = "https://hq.sinajs.cn/list=" + ",".join(chunk)
        for t in range(tries):
            try:
                raw = urllib.request.urlopen(
                    urllib.request.Request(url, headers=SINA_UA), timeout=20).read()
                txt = raw.decode("gbk", "ignore")
                for line in txt.strip().split("\n"):
                    m = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
                    if not m:
                        continue
                    sym, body = m.group(1), m.group(2)
                    f = body.split(",")
                    if len(f) < 10 or not f[0]:
                        continue
                    out[sym] = {
                        "name": f[0], "open": float(f[1] or 0), "prev": float(f[2] or 0),
                        "price": float(f[3] or 0), "high": float(f[4] or 0),
                        "low": float(f[5] or 0), "vol": float(f[8] or 0),
                        "amount": float(f[9] or 0), "date": f[30], "time": f[31],
                    }
                break
            except Exception as e:
                log(f"  retry sina {str(e)[:60]}")
                time.sleep(0.8 + t)
        time.sleep(0.35)
    return out


def sina_sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


def em_pool(kind, sort):
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool?"
           "ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=300"
           f"&sort={sort}&date={D8}")
    for i in range(4):
        cmd = ["curl", "-s", "--max-time", "25"] + sum([["-H", h] for h in EM_UA], []) + [url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout and r.stdout.strip():
            try:
                d = json.loads(r.stdout).get("data") or {}
                return {"tc": d.get("tc", 0), "pool": d.get("pool") or []}
            except Exception:
                pass
        time.sleep(1.0 + i)
    return {"tc": 0, "pool": []}


def sina_industry():
    """新浪行业板块榜：返回 [{name, pct, lead, lead_pct, count, amount_yi}]"""
    url = ("https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php")
    cmd = ["curl", "-s", "--max-time", "25", "-H", SINA_UA["User-Agent"],
           "-H", SINA_UA["Referer"], url]
    for i in range(4):
        r = subprocess.run(cmd, capture_output=True)
        txt = r.stdout.decode("gbk", "ignore")
        if "S_Finance_bankuai_sinaindustry" in txt:
            body = txt.split("=", 1)[1].strip().rstrip(";").strip()
            j = json.loads(body)
            rows = []
            for k, v in j.items():
                f = v.split(",")
                if len(f) < 13:
                    continue
                try:
                    rows.append({
                        "key": k, "name": f[1], "count": int(f[2]),
                        "pct": round(float(f[5]), 2),
                        "amount_yi": round(float(f[7]) / 1e8, 1),
                        "lead_code": f[8], "lead_name": f[12],
                    })
                except Exception:
                    continue
            return rows
        time.sleep(1.0 + i)
    return []


def summarize(rows):
    if not rows:
        return None
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else last
    w60, w20, w5 = rows[-60:], rows[-20:], rows[-5:]
    return {
        "date": last["d"], "open": last["o"], "high": last["h"], "low": last["l"],
        "close": last["c"], "prev_close": prev["c"],
        "pct": round((last["c"] / prev["c"] - 1) * 100, 2),
        "vol": last["v"], "amt": last["amt"],
        "hi60": max(r["h"] for r in w60), "lo60": min(r["l"] for r in w60),
        "vol_ma5": round(sum(r["v"] for r in w5) / 5, 0),
        "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0),
    }


res = {"date": DATE, "snapshot_time": "close", "index": {}, "stocks": {},
       "baskets": {}, "series": {}, "snapshot": {}, "prev_day": {}}

# 1) 日线（同花顺）—— 收盘后最后一根即 20261116
log("== 日线（同花顺）==")
for name, code in IDX.items():
    n, rows = ths_kline(code)
    res["series"][name] = rows
    if rows:
        res["index"][name] = summarize(rows)
        res["index"][name]["code"] = code
        log(f"  IDX {name} {n} bars={len(rows)} last={rows[-1]['d']} "
            f"C={rows[-1]['c']} pct={res['index'][name]['pct']:+.2f}%")
for name, code in STOCKS.items():
    n, rows = ths_kline("hs_" + code)
    res["series"][name] = rows
    if rows:
        res["stocks"][name] = summarize(rows)
        res["stocks"][name]["code"] = code
        res["stocks"][name]["em_name"] = n
        log(f"  STK {name} {n} bars={len(rows)} last={rows[-1]['d']} "
            f"C={rows[-1]['c']} pct={res['stocks'][name]['pct']:+.2f}%")

# 2) 新浪收盘快照
log("== 新浪收盘快照 ==")
syms = list(SINA_IDX.values())
syms += [sina_sym(c) for c in STOCKS.values()]
for b, ids in BASKETS.items():
    syms += [sina_sym(c) for c in ids]
syms = list(dict.fromkeys(syms))
snaps = sina_snapshot(syms)
log(f"  快照 {len(snaps)}/{len(syms)}")

for name, sym in SINA_IDX.items():
    s = snaps.get(sym)
    if not s:
        continue
    res["snapshot"][name] = s
    pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    res["index"].setdefault(name + "_sina", {}).update({
        "open": s["open"], "high": s["high"], "low": s["low"], "close": s["price"],
        "prev_close": s["prev"], "pct": pct, "amount_yi": round(s["amount"] / 1e8, 1),
        "time": s["time"]})
    log(f"  SINA {name} {s['price']:.2f} {pct:+.2f}% H{s['high']:.2f} L{s['low']:.2f}")

for name, code in STOCKS.items():
    s = snaps.get(sina_sym(code))
    if not s:
        continue
    pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    st = res["stocks"].setdefault(name, {})
    st["snap"] = {"open": s["open"], "high": s["high"], "low": s["low"],
                  "close": s["price"], "prev_close": s["prev"], "pct": pct,
                  "amount_yi": round(s["amount"] / 1e8, 2), "time": s["time"]}
    log(f"  SINA {name} {s['price']:.2f} {pct:+.2f}% H{s['high']:.2f} L{s['low']:.2f}")

# 3) 篮子（收盘快照算均值）
log("== 篮子 ==")
for bname, ids in BASKETS.items():
    mem = []
    for code in ids:
        s = snaps.get(sina_sym(code))
        if not s or not s["prev"]:
            continue
        pct = round((s["price"] / s["prev"] - 1) * 100, 2)
        mem.append({"code": code, "name": s["name"].replace(" ", ""), "pct": pct,
                    "close": s["price"], "high": s["high"], "low": s["low"],
                    "amount_yi": round(s["amount"] / 1e8, 2)})
    if not mem:
        continue
    res["baskets"][bname] = {
        "avg_pct": round(sum(m["pct"] for m in mem) / len(mem), 2),
        "n": len(mem),
        "up": sum(1 for m in mem if m["pct"] > 0),
        "down": sum(1 for m in mem if m["pct"] < 0),
        "amount_yi": round(sum(m["amount_yi"] for m in mem), 1),
        "members": mem,
    }
    log(f"  BKT {bname} {res['baskets'][bname]['avg_pct']:+.2f}% "
        f"{res['baskets'][bname]['up']}/{res['baskets'][bname]['down']}")

# 4) 涨跌停池 + 炸板池（收盘）
log("== 涨跌停池 ==")
res["pools"] = {"zt": em_pool("ZT", "fbt:asc"), "dt": em_pool("DT", "fund:asc"),
                "zb": em_pool("ZB", "fbt:asc")}
log(f"  涨停 {res['pools']['zt']['tc']} 跌停 {res['pools']['dt']['tc']} "
    f"炸板 {res['pools']['zb']['tc']}")

# 5) 两市成交额（同花顺日线口径：沪市=上证指数额，深市=深证成指额）
log("== 成交额 ==")
amt = {}
for nm in ("上证指数", "深证成指"):
    rows = res["series"].get(nm) or []
    today = [r for r in rows if r["d"] == D8]
    prev = [r for r in rows if r["d"] == "20261113"]
    if today:
        amt[nm] = round(today[-1]["amt"] / 1e8, 1)
    if prev:
        res["prev_day"][nm] = {"amt_yi": round(prev[-1]["amt"] / 1e8, 1),
                                "vol": prev[-1]["v"]}
res["amount"] = {
    "sh_yi": amt.get("上证指数"), "sz_yi": amt.get("深证成指"),
    "total_yi": round((amt.get("上证指数", 0) + amt.get("深证成指", 0)), 1),
    "scope": "全日（同花顺指数口径）",
}
if res["prev_day"]:
    pv = sum(v["amt_yi"] for v in res["prev_day"].values())
    res["amount"]["prev_total_yi"] = round(pv, 1)
    res["amount"]["growth_pct"] = round(
        (res["amount"]["total_yi"] / pv - 1) * 100, 1) if pv else None
log(f"  {res['amount']}")

# 6) 新浪行业板块榜（涨幅榜 + 老师点名的防守行业）
log("== 新浪行业榜 ==")
inds = sina_industry()
inds_sorted = sorted(inds, key=lambda x: -x["pct"])
res["industry_top"] = inds_sorted[:15]
res["industry_all"] = {i["name"]: i for i in inds}
(RPT / "ind_20261116_close.json").write_text(
    json.dumps({"top": res["industry_top"], "all": res["industry_all"]},
               ensure_ascii=False, indent=1), encoding="utf-8")
for i in res["industry_top"]:
    log(f"  IND {i['name']} {i['pct']:+.2f}% 领涨 {i['lead_name']}")

(RPT / "data_20261116_close.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
log("saved", RPT / "data_20261116_close.json")
