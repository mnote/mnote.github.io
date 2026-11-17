"""都业华 2026-11-17 午评（高级班·午盘）· 数据采集（盘中版）

⛔ 遵守用户 2026-11-11 禁令：只用日线 + 实时快照，不调用任何 1/15 分钟 K 线、不调用 czsc。

数据源：
  - 同花顺公开接口（免登录）：日线 https://d.10jqka.com.cn/v6/line/{code}/01/last.js
                            实时快照 https://d.10jqka.com.cn/v6/realhead/{code}/last.js
  - 新浪批量快照：https://hq.sinajs.cn/list=...
  - 新浪行业榜：https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php
  - 东财 push2ex 涨停/跌停/炸板池
  - 腾讯 5 日分时（仅用于两市同时点成交额同比，不是 K 线）

输出：reports/duyiehua-20261117/data_20261117.json
"""
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261117"
RPT.mkdir(parents=True, exist_ok=True)
DATE = "2026-11-17"
D8 = "20261117"
from datetime import datetime
SNAP_TIME = datetime.now().strftime("%H:%M")

THS_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://stockpage.10jqka.com.cn/"}
SINA_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
EM_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}

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
    "模塑科技": "000700", "长盈精密": "300115",
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


def fetch_curl(url, headers_cmd, tries=3, timeout=25):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    for h in headers_cmd:
        cmd += ["-H", h]
    cmd.append(url)
    for i in range(tries):
        try:
            r = subprocess.run(cmd, capture_output=True)
            if r.stdout and r.stdout.strip():
                return r.stdout
        except Exception as e:
            log(f"  retry-curl {url[:70]} {str(e)[:60]}")
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
                try:
                    rows.append({
                        "d": f[0], "o": float(f[1]), "h": float(f[2]), "l": float(f[3]),
                        "c": float(f[4]), "v": float(f[5]), "amt": float(f[6]),
                    })
                except ValueError:
                    continue  # 空值行（如停牌/未收盘占位）跳过
            return j.get("name", ""), rows
        except Exception as e:
            log(f"  retry ths {code} {str(e)[:60]}")
            time.sleep(1.0 + i)
    return "", []


def sina_snapshot(symbols, tries=3):
    """新浪批量快照"""
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
    # 补抓：分块失败的代码单独重试
    missing = [s for s in symbols if s not in out]
    if missing:
        log(f"  补抓 {len(missing)} 个代码: {missing[:8]}")
        for s in missing:
            url = "https://hq.sinajs.cn/list=" + s
            for t in range(tries):
                try:
                    raw = urllib.request.urlopen(
                        urllib.request.Request(url, headers=SINA_UA), timeout=15).read()
                    txt = raw.decode("gbk", "ignore")
                    m = re.search(r'var hq_str_(\w+)="([^"]*)"', txt)
                    if not m:
                        continue
                    f = m.group(2).split(",")
                    if len(f) < 10 or not f[0]:
                        continue
                    out[m.group(1)] = {
                        "name": f[0],
                        "open": float(f[1] or 0), "prev": float(f[2] or 0),
                        "price": float(f[3] or 0), "high": float(f[4] or 0),
                        "low": float(f[5] or 0),
                        "vol": float(f[8] or 0), "amount": float(f[9] or 0),
                        "date": f[30], "time": f[31],
                    }
                    break
                except Exception:
                    time.sleep(0.6 + t)
            time.sleep(0.2)
    return out


def em_pool(kind, sort, date=D8):
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool?"
           "ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=300"
           f"&sort={sort}&date={date}")
    raw = fetch_curl(url, ["User-Agent: Mozilla/5.0", "Referer: https://quote.eastmoney.com/"])
    if not raw:
        return {"tc": 0, "pool": []}
    try:
        txt = raw.decode("utf-8", "ignore")
        d = json.loads(txt).get("data") or {}
        return {"tc": d.get("tc", 0), "pool": d.get("pool") or []}
    except Exception:
        return {"tc": 0, "pool": []}


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


def merge_today(rows, snap, vol_scale=1):
    """把今日快照拼到日线序列末尾（未完成 K 线）

    ⚠️ 量纲：同花顺指数日线 vol 单位=股；新浪快照里沪市指数（sh*）vol 单位=手（需 ×100），
       深证成指/创业板指（sz399001/sz399006）vol 单位=股（不变）。
    """
    if not snap or not snap.get("price"):
        return rows
    v = snap["vol"] * vol_scale
    if rows and rows[-1]["d"] == D8:
        rows[-1].update({"o": snap["open"], "h": snap["high"], "l": snap["low"],
                         "c": snap["price"], "v": v, "amt": snap["amount"]})
    else:
        rows.append({"d": D8, "o": snap["open"], "h": snap["high"], "l": snap["low"],
                     "c": snap["price"], "v": v, "amt": snap["amount"]})
    return rows


def sina_sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


def tx_minute_amount(code):
    """腾讯 5 日分时：返回 {date: {'1130': 累计额(元), '1300':..., 'last':...}}"""
    url = f"https://web.ifzq.gtimg.cn/appstock/app/day/query?code={code}"
    raw = fetch_curl(url, ["User-Agent: Mozilla/5.0", "Referer: "], tries=3)
    if not raw:
        return {}
    try:
        j = json.loads(raw.decode("utf-8", "ignore"))
        data = j["data"][code]["data"]
    except Exception:
        return {}
    out = {}
    for day in data:
        d = day.get("date", "")
        rows = day.get("data") or []
        amt1130 = None
        amt1300 = None
        last_amt = None
        for r in rows:
            try:
                parts = r.split() if isinstance(r, str) else r
                t = str(parts[0])
                a = float(parts[3])
            except Exception:
                continue
            last_amt = a
            if t == "1130":
                amt1130 = a
            if t == "1300":
                amt1300 = a
        out[d] = {"amt_1130": amt1130, "amt_1300": amt1300,
                  "amt_last": last_amt, "rows": len(rows)}
    return out


def sina_industries():
    """新浪行业榜（49 个行业，GBK）：字段 code,name,家数,均价,平均涨跌幅(小数),涨跌幅%,量,额,领涨股..."""
    raw = fetch_curl("https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php",
                      ["User-Agent: Mozilla/5.0", "Referer: https://finance.sina.com.cn"], tries=3)
    if not raw:
        return []
    txt = raw.decode("gbk", "ignore")
    rows = []
    for m in re.finditer(r'"([a-z_]+)":"([a-z_]+),([^,]*),(\d+),([\d.]+),([-\d.eE]+),([-\d.eE]+),(\d+),(\d+),([^"]*)"', txt):
        rows.append({"name": m.group(3), "pct": round(float(m.group(6)), 2),
                     "n": int(m.group(4)), "amount_yi": round(int(m.group(8)) / 1e8, 1),
                     "leader": m.group(9)})
    rows.sort(key=lambda x: -x["pct"])
    return rows


# ---------------- 采集 ----------------
res = {"date": DATE, "snapshot_time": SNAP_TIME, "index": {}, "stocks": {},
       "baskets": {}, "series": {}, "snapshot": {}, "prev_day": {}}

log("== 日线（同花顺）==")
for name, code in IDX.items():
    n, rows = ths_kline(code)
    res["series"][name] = rows
    if rows:
        res["index"][name] = summarize(rows[:-1] if rows[-1]["d"] == D8 else rows)
    log(f"  IDX {name} {n} bars={len(rows)} last={rows[-1]['d'] if rows else '-'}")
for name, code in STOCKS.items():
    n, rows = ths_kline("hs_" + code)
    res["series"][name] = rows
    if rows:
        res["stocks"][name] = summarize(rows[:-1] if rows[-1]["d"] == D8 else rows)
        res["stocks"][name]["code"] = code
        res["stocks"][name]["em_name"] = n
    log(f"  STK {name} {n} bars={len(rows)}")

log("== 新浪快照 ==")
syms = ["sh000001", "sz399001", "sz399006", "sh000300", "sh000688", "sz399106",
        "sh000680", "sh000905"]
syms += [sina_sym(c) for c in STOCKS.values()]
for b, ids in BASKETS.items():
    syms += [sina_sym(c) for c in ids]
snaps = sina_snapshot(syms)
res["snapshot_raw"] = snaps
log(f"  快照 {len(snaps)}/{len(syms)}")

IDX_SINA = {"上证指数": "sh000001", "深证成指": "sz399001", "创业板指": "sz399006",
            "沪深300": "sh000300", "科创50": "sh000688"}
for name, sym in IDX_SINA.items():
    s = snaps.get(sym)
    if not s:
        continue
    res["snapshot"][name] = s
    rows = res["series"].get(name) or []
    res["series"][name] = merge_today(list(rows), s, vol_scale=(100 if sym.startswith("sh") else 1))
    snap_pct = round((s["price"] / s["prev"] - 1) * 100, 2) if s["prev"] else 0
    res["index"][name + "_snap"] = {
        "open": s["open"], "high": s["high"], "low": s["low"], "close": s["price"],
        "prev_close": s["prev"], "pct": snap_pct,
        "vol": s["vol"] * (100 if sym.startswith("sh") else 1), "amt": s["amount"], "time": s["time"],
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

log("== 篮子 ==")
for bname, ids in BASKETS.items():
    mem = []
    for code in ids:
        s = snaps.get(sina_sym(code))
        if not s or not s["prev"]:
            continue
        pct = round((s["price"] / s["prev"] - 1) * 100, 2)
        mem.append({"code": code, "name": s["name"], "pct": pct,
                    "close": s["price"], "low": s["low"], "high": s["high"],
                    "amount_yi": round(s["amount"] / 1e8, 2)})
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

log("== 涨跌停池 ==")
zt = em_pool("ZT", "fbt:asc")
dt = em_pool("DT", "fund:asc")
zb = em_pool("ZB", "fbt:asc")
res["pools"] = {"zt": zt, "dt": dt, "zb": zb}
log(f"  涨停 {zt['tc']} 跌停 {dt['tc']} 炸板 {zb['tc']}")

log("== 新浪行业榜 ==")
inds = sina_industries()
res["industries"] = inds
log(f"  {[(i['name'], i['pct']) for i in inds[:12]]}")

log("== 两市成交额（同时点同比：腾讯 5 日分时）==")
tx_sh = tx_minute_amount("sh000001")
tx_sz = tx_minute_amount("sz399001")
res["tx_amount"] = {"sh": tx_sh, "sz": tx_sz}
for k, v in tx_sh.items():
    log(f"  SH {k} 1130={v.get('amt_1130')}")

sh_amt = snaps.get("sh000001", {}).get("amount", 0)
sz_amt = snaps.get("sz399106", {}).get("amount", 0)
res["amount"] = {"sh_yi": round(sh_amt / 1e8, 1), "sz_yi": round(sz_amt / 1e8, 1),
                 "total_yi": round((sh_amt + sz_amt) / 1e8, 1)}
log(f"  两市累计成交 {res['amount']}")

# 11/16 同时点与全天成交额（同花顺日线）
for nm, code in (("上证指数", "zs_1A0001"), ("深证成指", "zs_399001")):
    rows = res["series"].get(nm) or []
    for d in ("20261116",):
        rr = [r for r in rows if r["d"] == d]
        if rr:
            res.setdefault("prev_day", {}).setdefault(nm, {})[d] = {
                "amt_yi": round(rr[0]["amt"] / 1e8, 1), "vol": rr[0]["v"]}

(RPT / "data_20261117.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
log("saved", RPT / "data_20261117.json")
