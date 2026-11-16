"""都业华 2026-11-16 午评（高级班·午盘）· 数据采集（盘中版）

⛔ 遵守用户 2026-11-11 禁令：只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。

数据源：
  - 同花顺公开接口（免登录）：日线 https://d.10jqka.com.cn/v6/line/{code}/01/last.js
                            实时快照 https://d.10jqka.com.cn/v6/realhead/{code}/last.js
  - 新浪批量快照（11:30 上午收盘）：https://hq.sinajs.cn/list=...
  - 东财 push2ex 涨停/跌停池（盘中可用）
  - 东财 push2 clist 全 A 宽度（限流时降级）

输出：reports/duyiehua-20261116/data_20261116.json
"""
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
RPT.mkdir(parents=True, exist_ok=True)
DATE = "2026-11-16"
SNAP_TIME = "11:30"

THS_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
SINA_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
EM_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}

# 同花顺代码：个股 hs_{code}，沪指 zs_1A0001，深成 zs_399001，创业板 zs_399006
IDX = {
    "上证指数": "zs_1A0001",
    "深证成指": "zs_399001",
    "创业板指": "zs_399006",
    "沪深300": "zs_1B0300",
    "科创50": "zs_1B0688",
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
}


def log(*a):
    print(*a, flush=True)


def fetch(url, headers, tries=4, timeout=25):
    for i in range(tries):
        try:
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=timeout).read()
            return raw
        except Exception as e:
            log(f"  retry {url[:60]} {str(e)[:60]}")
            time.sleep(1.0 + i * 1.2)
    return None


def fetch_curl(url, headers_cmd, tries=4, timeout=25):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    for h in headers_cmd:
        cmd += ["-H", h]
    cmd.append(url)
    for i in range(tries):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.stdout and r.stdout.strip():
                return r.stdout
        except Exception as e:
            log(f"  retry-curl {url[:60]} {str(e)[:60]}")
        time.sleep(1.0 + i * 1.2)
    return None


def ths_kline(code, tries=4):
    """同花顺日线：返回 {name, rows:[{d,o,h,l,c,v,amt}]}"""
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
    """新浪批量快照：{symbol: {name,open,prev,price,high,low,vol,amount,date,time}}"""
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
                        "name": f[0],
                        "open": float(f[1] or 0), "prev": float(f[2] or 0),
                        "price": float(f[3] or 0), "high": float(f[4] or 0),
                        "low": float(f[5] or 0),
                        "vol": float(f[8] or 0), "amount": float(f[9] or 0),
                        "date": f[30], "time": f[31],
                    }
                break
            except Exception as e:
                log(f"  retry sina {str(e)[:60]}")
                time.sleep(0.8 + t)
        time.sleep(0.35)
    return out


def em_pool(kind, sort):
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool?"
           "ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=300"
           f"&sort={sort}&date=20261116")
    txt = fetch_curl(url, ["User-Agent: Mozilla/5.0", "Referer: https://quote.eastmoney.com/"])
    if not txt:
        return {"tc": 0, "pool": []}
    try:
        d = json.loads(txt).get("data") or {}
        return {"tc": d.get("tc", 0), "pool": d.get("pool") or []}
    except Exception:
        return {"tc": 0, "pool": []}


def em_breadth():
    """东财 clist 全 A 涨跌家数；限流时返回 None"""
    fs = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
    up = down = flat = 0
    lim_up = lim_dn = 0
    n = 0
    for pn in range(1, 65):
        url = ("https://push2.eastmoney.com/api/qt/clist/get?"
               f"pn={pn}&pz=100&po=0&np=1&fltt=2&invt=2&fid=f3&fs={fs}&fields=f2,f3,f12,f14")
        txt = fetch_curl(url, ["User-Agent: Mozilla/5.0", "Referer: https://quote.eastmoney.com/"], tries=2)
        if not txt:
            break
        try:
            d = json.loads(txt).get("data")
        except Exception:
            break
        if not d or not d.get("diff"):
            break
        diff = d["diff"]
        for it in diff:
            p = it.get("f3")
            n += 1
            if p is None:
                continue
            if p > 0:
                up += 1
            elif p < 0:
                down += 1
            else:
                flat += 1
            if p >= 9.8:
                lim_up += 1
            if p <= -9.8:
                lim_dn += 1
        if len(diff) < 100:
            break
        time.sleep(0.12)
    if n == 0:
        return None
    return {"n": n, "up": up, "down": down, "flat": flat,
            "lim_up_9_8": lim_up, "lim_dn_9_8": lim_dn}


def summarize(rows):
    if not rows:
        return None
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else last
    w60 = rows[-60:]
    w20 = rows[-20:]
    w5 = rows[-5:]
    return {
        "date": last["d"], "open": last["o"], "high": last["h"], "low": last["l"],
        "close": last["c"], "prev_close": prev["c"],
        "pct": round((last["c"] / prev["c"] - 1) * 100, 2),
        "vol": last["v"], "amt": last["amt"],
        "hi60": max(r["h"] for r in w60), "lo60": min(r["l"] for r in w60),
        "vol_ma5": round(sum(r["v"] for r in w5) / 5, 0),
        "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0),
    }


def merge_today(rows, snap):
    """把今日 11:30 快照拼到日线序列末尾（未完成 K 线）"""
    if not snap or not snap.get("price"):
        return rows
    d = DATE.replace("-", "")
    if rows and rows[-1]["d"] == d:
        rows[-1].update({"o": snap["open"], "h": snap["high"], "l": snap["low"],
                         "c": snap["price"], "v": snap["vol"], "amt": snap["amount"]})
    else:
        rows.append({"d": d, "o": snap["open"], "h": snap["high"], "l": snap["low"],
                     "c": snap["price"], "v": snap["vol"], "amt": snap["amount"]})
    return rows


def sina_sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


# ---------------- 采集 ----------------
res = {"date": DATE, "snapshot_time": SNAP_TIME, "index": {}, "stocks": {},
       "baskets": {}, "series": {}, "snapshot": {}, "prev_day": {}}

# 1) 日线（同花顺）
log("== 日线（同花顺）==")
for name, code in IDX.items():
    n, rows = ths_kline(code)
    res["series"][name] = rows
    if rows:
        res["index"][name] = summarize(rows[:-1] if rows[-1]["d"] == DATE.replace("-", "") else rows)
    log(f"  IDX {name} {n} bars={len(rows)} last={rows[-1]['d'] if rows else '-'}")
for name, code in STOCKS.items():
    n, rows = ths_kline("hs_" + code)
    res["series"][name] = rows
    if rows:
        res["stocks"][name] = summarize(rows[:-1] if rows[-1]["d"] == DATE.replace("-", "") else rows)
        res["stocks"][name]["code"] = code
        res["stocks"][name]["em_name"] = n
    log(f"  STK {name} {n} bars={len(rows)}")

# 2) 新浪快照（11:30 上午收盘）
log("== 新浪快照 ==")
syms = ["sh000001", "sz399001", "sz399006", "sh000300", "sh000688", "sz399106"]
syms += [sina_sym(c) for c in STOCKS.values()]
for b, ids in BASKETS.items():
    syms += [sina_sym(c) for c in ids]
snaps = sina_snapshot(syms)
log(f"  快照 {len(snaps)}/{len(syms)}")

IDX_SINA = {"上证指数": "sh000001", "深证成指": "sz399001", "创业板指": "sz399006",
            "沪深300": "sh000300", "科创50": "sh000688"}
for name, sym in IDX_SINA.items():
    s = snaps.get(sym)
    if not s:
        continue
    res["snapshot"][name] = s
    rows = res["series"].get(name) or []
    res["series"][name] = merge_today(list(rows), s)
    snap_pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    res["index"][name + "_snap"] = {
        "open": s["open"], "high": s["high"], "low": s["low"], "close": s["price"],
        "prev_close": s["prev"], "pct": snap_pct,
        "vol": s["vol"], "amt": s["amount"], "time": s["time"],
    }
    log(f"  IDX {name} {s['price']:.2f} {snap_pct:+.2f}% H{s['high']:.2f} L{s['low']:.2f}")

for name, code in STOCKS.items():
    s = snaps.get(sina_sym(code))
    if not s:
        continue
    res["snapshot"][name] = s
    rows = res["series"].get(name) or []
    res["series"][name] = merge_today(list(rows), s)
    snap_pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    st = res["stocks"].setdefault(name, {})
    st["snap"] = {"open": s["open"], "high": s["high"], "low": s["low"],
                  "close": s["price"], "prev_close": s["prev"], "pct": snap_pct,
                  "vol": s["vol"], "amt": s["amount"], "time": s["time"]}
    log(f"  STK {name} {s['price']:.2f} {snap_pct:+.2f}% H{s['high']:.2f} L{s['low']:.2f}")

# 3) 篮子（用快照算均值）
log("== 篮子 ==")
for bname, ids in BASKETS.items():
    mem = []
    for code in ids:
        s = snaps.get(sina_sym(code))
        if not s or not s["prev"]:
            continue
        pct = round((s["price"] / s["prev"] - 1) * 100, 2)
        mem.append({"code": code, "name": s["name"], "pct": pct,
                    "close": s["price"], "amount_yi": round(s["amount"] / 1e8, 2)})
    if not mem:
        continue
    avg = round(sum(m["pct"] for m in mem) / len(mem), 2)
    res["baskets"][bname] = {
        "avg_pct": avg, "n": len(mem),
        "up": sum(1 for m in mem if m["pct"] > 0),
        "down": sum(1 for m in mem if m["pct"] < 0),
        "amount_yi": round(sum(m["amount_yi"] for m in mem), 1),
        "members": mem,
    }
    log(f"  BKT {bname} {avg:+.2f}% {res['baskets'][bname]['up']}/{res['baskets'][bname]['down']}")

# 4) 涨跌停池 + 全 A 宽度
log("== 涨跌停池 ==")
zt = em_pool("ZT", "fbt:asc")
dt = em_pool("DT", "fund:asc")
zb = em_pool("ZB", "fbt:asc")
res["pools"] = {"zt": zt, "dt": dt, "zb": zb}
log(f"  涨停 {zt['tc']} 跌停 {dt['tc']} 炸板 {zb['tc']}")

log("== 全 A 宽度 ==")
br = em_breadth()
res["breadth"] = br
log(f"  {br}")

# 5) 两市成交额（上午累计，新浪指数口径：沪=sh000001 全市场，深=sz399106 全市场）
sh_amt = snaps.get("sh000001", {}).get("amount", 0)
sz_amt = snaps.get("sz399106", {}).get("amount", 0)
res["amount"] = {"sh_yi": round(sh_amt / 1e8, 1), "sz_yi": round(sz_amt / 1e8, 1),
                 "total_yi": round((sh_amt + sz_amt) / 1e8, 1)}
log(f"  两市上午成交 {res['amount']}")

# 6) 昨日（11/13）全市场成交额对照：同花顺 11/13 沪/深指数成交额
for nm, code in (("上证指数", "zs_1A0001"), ("深证成指", "zs_399001")):
    rows = res["series"].get(nm) or []
    prev_rows = [r for r in rows if r["d"] == "20261113"]
    if prev_rows:
        res.setdefault("prev_day", {})[nm] = {"amt_yi": round(prev_rows[0]["amt"] / 1e8, 1),
                                              "vol": prev_rows[0]["v"]}

(RPT / "data_20261116.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
log("saved", RPT / "data_20261116.json")
