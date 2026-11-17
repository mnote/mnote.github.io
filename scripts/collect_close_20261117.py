"""11/17 收盘数据（东财口径，单源一致：kline 日线 + ulist 收盘快照 + clist 全市场 + push2ex 三池）。

用法： python3 scripts/collect_close_20261117.py
产物： charts/_close_20261117.json
"""
import json
import subprocess
import time
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")
UA = ["-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://quote.eastmoney.com/"]
DAILY = json.loads((CH / "_daily_20261116.json").read_text(encoding="utf-8"))


def curl(url, timeout=35):
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout)] + UA + [url],
                       capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def secid(code):
    num, mkt = code.split(".")
    return f"{1 if mkt == 'SH' else 0}.{num}"


def kline(sec, beg="20260801", end="20261117", tries=4):
    url = (f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={sec}"
           f"&klt=101&fqt=1&beg={beg}&end={end}"
           f"&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&lmt=90")
    for i in range(tries):
        try:
            d = json.loads(curl(url)).get("data") or {}
            kl = d.get("klines") or []
            if kl:
                rows = []
                for line in kl:
                    p = line.split(",")
                    if len(p) < 7:
                        continue
                    rows.append({"Date": p[0], "Open": float(p[1]), "Close": float(p[2]),
                                 "High": float(p[3]), "Low": float(p[4]),
                                 "Volume": float(p[5]), "Amount": float(p[6])})
                return rows
        except Exception:
            pass
        time.sleep(1.5 * (i + 1))
    return []


def ulist(codes):
    out = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i + 50]
        ids = ",".join(secid(c) for c in chunk)
        url = ("https://push2.eastmoney.com/api/qt/ulist.np/get?secids=" + ids +
               "&fields=f2,f3,f4,f5,f6,f12,f13,f14,f15,f16,f17,f18")
        try:
            d = json.loads(curl(url)).get("data") or {}
        except Exception:
            continue
        for x in (d.get("diff") or []):
            out[f"{x.get('f13')}.{x.get('f12')}"] = {
                "name": x.get("f14"), "price": _num(x.get("f2")) / 100,
                "pct": _num(x.get("f3")) / 100, "chg": _num(x.get("f4")) / 100,
                "vol_hand": x.get("f5"), "amount": x.get("f6"),
                "high": _num(x.get("f15")) / 100, "low": _num(x.get("f16")) / 100,
                "open": _num(x.get("f17")) / 100, "prev_close": _num(x.get("f18")) / 100}
        time.sleep(0.25)
    return out


def clist_all():
    rows, seen, total = [], set(), 0
    for pn in range(1, 63):
        url = ("https://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=100&po=1&np=1"
               "&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
               "&fields=f2,f3,f6,f12,f14" % pn)
        arr = []
        for _ in range(3):
            try:
                d = json.loads(curl(url)).get("data") or {}
                arr = d.get("diff") or []
                total = total or (d.get("total") or 0)
                if arr:
                    break
            except Exception:
                pass
            time.sleep(1.0)
        if not arr:
            break
        for x in arr:
            c = str(x.get("f12"))
            if c in seen:
                continue
            seen.add(c)
            try:
                p = float(x.get("f3"))
            except (TypeError, ValueError):
                continue
            rows.append({"code": c, "name": x.get("f14"), "pct": p,
                         "price": x.get("f2"), "amount": _num(x.get("f6"))})
        if len(rows) >= total:
            break
        time.sleep(0.1)
    up = sum(1 for r in rows if r["pct"] > 0)
    dn = sum(1 for r in rows if r["pct"] < 0)
    fl = len(rows) - up - dn
    lu = sum(1 for r in rows if r["pct"] >= 9.9)
    ld = sum(1 for r in rows if r["pct"] <= -9.9)
    amt = sum(r["amount"] for r in rows) / 1e8
    rows.sort(key=lambda r: -r["pct"])
    return {"n": len(rows), "up": up, "down": dn, "flat": fl,
            "limit_up": lu, "limit_down": ld, "amount_yi": round(amt, 1),
            "top_gainers": rows[:30], "top_losers": rows[-30:]}


def em_pool(kind, date):
    url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool"
           f"?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0"
           f"&pagesize=300&sort=fbt:asc&date={date}")
    for _ in range(3):
        try:
            d = json.loads(curl(url)) or {}
            dd = d.get("data") or {}
            arr = dd.get("pool") or []
            ind = {}
            for x in arr:
                ind[x.get("hybk", "未知")] = ind.get(x.get("hybk", "未知"), 0) + 1
            return {"tc": dd.get("tc", 0), "n": len(arr),
                    "industry": dict(sorted(ind.items(), key=lambda kv: -kv[1])),
                    "members": [{"code": x.get("c"), "name": x.get("n"),
                                 "pct": x.get("zdp"), "lbc": x.get("lbc"),
                                 "ind": x.get("hybk")} for x in arr]}
        except Exception:
            pass
        time.sleep(1.2)
    return {}


if __name__ == "__main__":
    codes = list(DAILY.keys())
    print(f"[close] 标的 {len(codes)} 只")

    print("[1/4] 东财日 K（含今日收盘）…", flush=True)
    series = {}
    for c in codes:
        rows = kline(secid(c))
        if rows:
            series[c] = rows
        time.sleep(0.12)
    last_dates = {}
    for c, rows in series.items():
        last_dates[c] = rows[-1]["Date"]
    from collections import Counter
    print("  末根日期分布:", Counter(last_dates.values()).most_common())

    print("[2/4] 收盘快照 …", flush=True)
    snap = ulist(codes)
    print(f"  {len(snap)}/{len(codes)}")

    print("[3/4] 全 A 宽度 …", flush=True)
    allq = clist_all()
    print(f"  全 A {allq['n']} 只  涨 {allq['up']} / 跌 {allq['down']} / 平 {allq['flat']}"
          f"  涨9.9+ {allq['limit_up']} 跌9.9- {allq['limit_down']}  成交 {allq['amount_yi']:,.0f} 亿")

    print("[4/4] 涨停/炸板/跌停池 …", flush=True)
    pools = {}
    for kind, key in [("ZT", "zt"), ("ZB", "zb"), ("DT", "dt")]:
        pools[key] = em_pool(kind, "20261117")
        print(f"  {key}: {pools[key].get('tc', 0)} 只  {list(pools[key].get('industry', {}).items())[:8]}")

    out = {"date": "2026-11-17", "series": series, "snapshot": snap,
           "all": {k: v for k, v in allq.items() if k not in ("top_gainers", "top_losers")},
           "top_gainers": allq["top_gainers"], "top_losers": allq["top_losers"],
           "em_pools": pools}
    (CH / "_close_20261117.json").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"[out] {CH/'_close_20261117.json'}")
