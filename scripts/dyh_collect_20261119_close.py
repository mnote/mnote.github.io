"""都业华 2026-11-19 高级班收评 · 数据采集（收盘版）

⛔ 用户 2026-11-11 禁令：只用日线级别数据，不调用 1/15 分钟 K 线、不调用 czsc。
⛔ 老师原文的缠论定性按「老师口径」引用，不声称我方复算过 15 分钟结构。

数据源：
  - Tushare 日线（个股前复权 + 指数日线）+ 全市场 daily（涨跌家数/成交额/涨跌停）
  - 新浪实时快照（收盘后为终值，用于篮子均值与交叉校验）
  - 东财 push2ex 涨停/跌停/炸板池

输出：reports/duyiehua-20261119/data_close_20261119.json
"""
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
RPT.mkdir(parents=True, exist_ok=True)
TD, PREV, D8 = "20261119", "20261118", "20261119"

pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN")
                 or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")

SINA_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
EM_UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}

IDX = {
    "000001.SH": "上证指数",
    "399001.SZ": "深证成指",
    "399006.SZ": "创业板指",
    "000300.SH": "沪深300",
    "000688.SH": "科创50",
}

# 老师收评点名的 8 只教学案例 + 3 只板块个股
STOCKS = {
    "603259.SH": "药明康德",
    "600150.SH": "中国船舶",
    "603893.SH": "瑞芯微",
    "600887.SH": "伊利股份",
    "688787.SH": "海天瑞声",
    "603986.SH": "兆易创新",
    "688629.SH": "华丰科技",
    "688981.SH": "中芯国际",
    "000158.SZ": "常山北明",
    "002261.SZ": "拓维信息",
    "600839.SH": "四川长虹",
}

BASKETS = {
    "国产算力": ["000158", "002261", "600839", "000034", "301236", "002642", "002197"],
    "算力租赁/IDC": ["300442", "300383", "603881", "300738", "300846", "603496"],
    "高股息红利": ["600900", "601088", "601006", "601398", "601288", "600028", "000895"],
    "半导体": ["603893", "603986", "688981", "688041", "002371", "688256"],
    "AI视频/传媒": ["300364", "300133", "300251", "601595", "300182", "300418"],
    "人形机器人": ["000700", "300115", "002050", "601689", "688017", "300124"],
    "银行": ["600036", "601398", "601939", "601288", "601166"],
    "电力": ["600900", "600025", "600886", "600674", "601985"],
    "饮料制造": ["605499", "000848", "300997", "603156", "605337"],
    "煤炭/石油": ["601088", "600028", "601857", "600938", "601808"],
}

NAMES = {c: n for c, n in STOCKS.items()}
ALL_CODES = set(STOCKS) | {f"{c}.{'SH' if c[0] == '6' else 'SZ'}" for c in
                           sum(BASKETS.values(), [])}


def log(*a):
    print(*a, flush=True)


def ts_call(fn, **kw):
    for i in range(4):
        try:
            return fn(**kw)
        except Exception as e:
            log(f"  retry {fn.__name__} {kw} {str(e)[:80]}")
            time.sleep(1.5 + i * 2)
    return None


def norm(rows, key="trade_date"):
    if rows is None:
        return []
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    return sorted(rows, key=lambda r: r[key])


def fwd_adj(daily, adj):
    """前复权：close × adj_factor(最新日) / adj_factor(当日)。adj 升序 → 最新日在末尾。"""
    if not adj:
        return list(daily)
    today = adj[-1]["adj_factor"]
    f = {r["trade_date"]: r["adj_factor"] for r in adj}
    out = []
    for d in daily:
        r = f.get(d["trade_date"])
        if r is None:
            continue
        k = today / r
        out.append({
            "d": d["trade_date"], "o": round(d["open"] * k, 2),
            "h": round(d["high"] * k, 2), "l": round(d["low"] * k, 2),
            "c": round(d["close"] * k, 2), "v": d["vol"], "amt": d["amount"],
            "pct": d.get("pct_chg"),
        })
    return out


def fetch_stock(ts_code):
    daily = norm(ts_call(pro.daily, ts_code=ts_code, start_date="20250801", end_date=TD))
    adj = norm(ts_call(pro.adj_factor, ts_code=ts_code, start_date="20250801", end_date=TD))
    return fwd_adj(daily, adj)


def fetch_index(ts_code):
    rows = norm(ts_call(pro.index_daily, ts_code=ts_code, start_date="20250801", end_date=TD))
    if not rows:
        rows = norm(ts_call(pro.daily, ts_code=ts_code, start_date="20250801", end_date=TD))
    out = []
    for r in rows:
        out.append({"d": r["trade_date"], "o": r["open"], "h": r["high"], "l": r["low"],
                    "c": r["close"], "v": r.get("vol"), "amt": r.get("amount"),
                    "pct": r.get("pct_chg")})
    return out


def summarize(rows):
    if not rows:
        return None
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else last
    w60, w20, w5 = rows[-60:], rows[-20:], rows[-5:]
    vols = [r["v"] for r in rows if r.get("v")]
    v5 = sum(r["v"] for r in w5) / 5 if w5 else None
    return {
        "date": last["d"], "open": last["o"], "high": last["h"], "low": last["l"],
        "close": last["c"], "prev_close": prev["c"],
        "pct": round((last["c"] / prev["c"] - 1) * 100, 2),
        "vol": last["v"], "amt": last["amt"],
        "hi60": round(max(r["h"] for r in w60), 2),
        "lo60": round(min(r["l"] for r in w60), 2),
        "vol_ma5": round(v5, 0) if v5 else None,
        "vol_ma20": round(sum(r["v"] for r in w20) / 20, 0),
        "amt_prev": prev.get("amt"), "amt_ma5": round(sum(r["amt"] for r in w5) / 5, 0) if w5 else None,
        "bars": len(rows),
    }


def sina_snapshot(symbols):
    out = {}
    for i in range(0, len(symbols), 40):
        chunk = symbols[i:i + 40]
        url = "https://hq.sinajs.cn/list=" + ",".join(chunk)
        for t in range(3):
            try:
                raw = urllib.request.urlopen(
                    urllib.request.Request(url, headers=SINA_UA), timeout=20).read()
                for line in raw.decode("gbk", "ignore").strip().split("\n"):
                    m = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
                    if not m:
                        continue
                    sym, f = m.group(1), m.group(2).split(",")
                    if len(f) < 32 or not f[0]:
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
        time.sleep(0.3)
    return out


def sina_sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


def em_pool(kind, sort, date=D8):
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool?"
           "ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0&pagesize=300"
           f"&sort={sort}&date={date}")
    cmd = ["curl", "-s", "--max-time", "25", "-H", "User-Agent: Mozilla/5.0",
           "-H", "Referer: https://quote.eastmoney.com/", url]
    for i in range(3):
        try:
            raw = subprocess.run(cmd, capture_output=True).stdout
            if raw and raw.strip():
                d = json.loads(raw.decode("utf-8", "ignore")).get("data") or {}
                return {"tc": d.get("tc", 0), "pool": d.get("pool") or []}
        except Exception as e:
            log(f"  retry em {kind} {str(e)[:60]}")
        time.sleep(1.2)
    return {"tc": 0, "pool": []}


def limit_price(code, pre_close):
    if code.startswith("30") or code.startswith("688"):
        return round(pre_close * 1.2, 2)
    if code.startswith("8") or code.startswith("4") or code.startswith("92"):
        return round(pre_close * 1.3, 2)
    return round(pre_close * 1.1, 2)


def main():
    res = {"date": "2026-11-19", "snapshot_time": "15:00", "index": {}, "stocks": {},
           "series": {}, "baskets": {}, "snapshot": {}, "pools": {}}

    # ---------- 全市场 daily：涨跌家数 / 成交额 / 涨跌停 ----------
    all_day = norm(ts_call(pro.daily, trade_date=TD))
    all_prev = norm(ts_call(pro.daily, trade_date=PREV))
    log(f"[all] {TD} {len(all_day)} 只 / {PREV} {len(all_prev)} 只")
    try:
        nm = {r["ts_code"]: r["name"] for r in ts_call(
            pro.stock_basic, exchange="", list_status="L",
            fields="ts_code,name").to_dict("records")}
    except Exception as e:
        nm = {}
        log("[name] 失败", e)
    prev_map = {r["ts_code"]: r for r in all_prev}
    up = down = flat = 0
    zt, dt, ztb = [], [], []
    for r in all_day:
        r["name"] = nm.get(r["ts_code"], "")
        p = r.get("pct_chg") or 0
        if p > 0:
            up += 1
        elif p < 0:
            down += 1
        else:
            flat += 1
        pc = prev_map.get(r["ts_code"], {}).get("close")
        if pc is None or "ST" in r["name"]:
            continue
        code = r["ts_code"].split(".")[0]
        lp, dp = limit_price(code, pc), round(pc * 0.9, 2)
        if r["high"] and abs(r["high"] - lp) < 0.011 and r["close"] >= lp - 0.011:
            zt.append({"code": r["ts_code"], "name": r["name"], "pct": round(p, 2)})
            if r["high"] > lp + 0.011:
                ztb.append({"code": r["ts_code"], "name": r["name"], "pct": round(p, 2)})
        if r["low"] and abs(r["low"] - dp) < 0.011 and r["close"] <= dp + 0.011:
            dt.append({"code": r["ts_code"], "name": r["name"], "pct": round(p, 2)})
    amt_today = sum((r.get("amount") or 0) for r in all_day) / 1e5
    amt_prev = sum((r.get("amount") or 0) for r in all_prev) / 1e5
    res["breadth"] = {
        "n": len(all_day), "up": up, "down": down, "flat": flat,
        "amount_yi": round(amt_today, 0), "amount_prev_yi": round(amt_prev, 0),
        "amount_delta_yi": round(amt_today - amt_prev, 0),
        "amount_delta_pct": round((amt_today / amt_prev - 1) * 100, 2),
        "zt": len(zt), "dt": len(dt), "ztb": len(ztb),
        "zt_list": zt, "dt_list": dt,
        "down_5": sum(1 for r in all_day if (r.get("pct_chg") or 0) <= -5),
        "down_9": sum(1 for r in all_day if (r.get("pct_chg") or 0) <= -9),
    }
    log(f"[breadth] {amt_today:.0f}亿 (前 {amt_prev:.0f}, {(amt_today/amt_prev-1)*100:+.2f}%) "
        f"涨{up} 跌{down} 平{flat} 涨停{len(zt)} 跌停{len(dt)} 炸板{len(ztb)}")

    # ---------- 指数 ----------
    for code, name in IDX.items():
        rows = fetch_index(code)
        res["series"][name] = rows
        s = summarize(rows)
        s["code"] = code
        s["gap_3623"] = round(s["close"] - 3623.12, 2)
        s["hi_3623_gap"] = round(s["high"] - 3623.12, 2)
        res["index"][name] = s
        log(f"[idx] {name} 收 {s['close']} {s['pct']:+}% H{s['high']} L{s['low']} "
            f"60低 {s['lo60']} 60高 {s['hi60']}")

    # ---------- 个股 ----------
    for code, name in STOCKS.items():
        rows = fetch_stock(code)
        res["series"][name] = rows
        s = summarize(rows)
        s["code"] = code.split(".")[0]
        res["stocks"][name] = s
        log(f"[stk] {name} {code} 收 {s['close']} {s['pct']:+}% H{s['high']} L{s['low']} "
            f"额{s['amt']/1e8:.1f}亿 前日额{s['amt_prev']/1e8:.1f}亿")

    # ---------- 新浪快照（篮子均值 + 交叉校验） ----------
    syms = sorted({sina_sym(c.split(".")[0]) for c in ALL_CODES})
    snaps = sina_snapshot(syms)
    res["snapshot_raw"] = snaps
    log(f"[snap] {len(snaps)}/{len(syms)}")

    for code, name in STOCKS.items():
        s = snaps.get(sina_sym(code.split(".")[0]))
        if not s:
            continue
        snap = {"open": s["open"], "high": s["high"], "low": s["low"], "close": s["price"],
                "prev_close": s["prev"], "pct": round((s["price"] / s["prev"] - 1) * 100, 2),
                "vol": s["vol"], "amt": s["amount"], "time": s["time"], "date": s["date"]}
        st = res["stocks"][name]
        st["snap"] = snap
        diff = round(snap["close"] - st["close"], 2)
        st["sina_diff"] = diff
        if abs(diff) > 0.02:
            log(f"  [!] {name} tushare {st['close']} vs sina {snap['close']} 差 {diff}")

    for bname, ids in BASKETS.items():
        mem = []
        for code in ids:
            s = snaps.get(sina_sym(code))
            if not s or not s["prev"]:
                continue
            mem.append({"code": code, "name": s["name"],
                        "pct": round((s["price"] / s["prev"] - 1) * 100, 2),
                        "close": s["price"], "low": s["low"], "high": s["high"],
                        "amount_yi": round(s["amount"] / 1e8, 2),
                        "vol": s["vol"]})
        if not mem:
            continue
        pcts = [m["pct"] for m in mem]
        res["baskets"][bname] = {
            "avg_pct": round(sum(pcts) / len(pcts), 2), "n": len(mem),
            "up": sum(1 for p in pcts if p > 0), "down": sum(1 for p in pcts if p < 0),
            "amount_yi": round(sum(m["amount_yi"] for m in mem), 1),
            "members": mem,
        }
        log(f"[bkt] {bname} {res['baskets'][bname]['avg_pct']:+.2f}% "
            f"{res['baskets'][bname]['up']}/{res['baskets'][bname]['down']}")

    # ---------- 涨跌停池 + 前期强势股补跌 ----------
    zt_today = em_pool("ZT", "fbt:asc")
    dt_today = em_pool("DT", "fund:asc")
    zb_today = em_pool("ZB", "fbt:asc")
    zt_prev = em_pool("ZT", "fbt:asc", PREV)
    res["pools"] = {"zt": zt_today, "dt": dt_today, "zb": zb_today, "zt_prev": zt_prev}
    log(f"[pool] 涨停 {zt_today['tc']} 跌停 {dt_today['tc']} 炸板 {zb_today['tc']} "
        f"（昨涨停 {zt_prev['tc']}）")

    day_map = {r["ts_code"]: r for r in all_day}
    cont = []
    for p in zt_prev.get("pool") or []:
        c = p.get("c")
        if not c:
            continue
        full = (c + ".SZ") if c[0] in "03" else (c + ".SH")
        r = day_map.get(full)
        if not r:
            continue
        cont.append({"code": full, "name": p.get("n"), "pct": round(r.get("pct_chg") or 0, 2),
                     "close": r.get("close")})
    res["prev_zt_follow"] = {
        "n": len(cont),
        "down": sum(1 for c in cont if c["pct"] < 0),
        "down5": sum(1 for c in cont if c["pct"] <= -5),
        "up": sum(1 for c in cont if c["pct"] > 0),
        "items": sorted(cont, key=lambda x: x["pct"])[:12],
    }
    log(f"[续板跟踪] 昨日涨停 {len(cont)} 只 → 今日跌 "
        f"{res['prev_zt_follow']['down']} 只（跌超5% {res['prev_zt_follow']['down5']}）")

    (RPT / "data_close_20261119.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    log("saved", RPT / "data_close_20261119.json")


if __name__ == "__main__":
    main()
