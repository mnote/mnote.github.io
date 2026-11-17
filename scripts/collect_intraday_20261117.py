"""11/17 盘中数据采集（Tushare Pro 日线底座 + 东财实时快照）。

口径：
  - 日线底座：charts/_daily_20261116.json（到 11/16 收盘，前复权）
  - 今日 K 线：东财 push2 实时快照（未完成 K 线，成交量/额为盘中累计）
  - 全市场宽度：东财 push2 clist 全 A 快照（涨跌家数、涨跌停、成交额）
  - 成交额同比：push2his trends2 ndays=5，按同一时点截断后逐日比

用法： python3 scripts/collect_intraday_20261117.py
产物： charts/_intraday_20261117.json
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")
UA = ["-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://quote.eastmoney.com/"]


def curl(url, timeout=30):
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout)] + UA + [url],
                       capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def _num(v):
    """东财部分字段返回 '-'（停牌/无数据）。"""
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def secid(code):
    """ts_code -> 东财 secid。沪市 1.，深/北 0.。"""
    num, mkt = code.split(".")
    if mkt == "SH":
        return f"1.{num}"
    if code.endswith(".BJ"):
        return f"0.{num}"
    if num.startswith(("000", "001", "002", "003", "300", "301")):
        return f"0.{num}"
    return f"0.{num}"


def em_ulist(codes):
    """批量实时快照 → {code: {...}}"""
    out = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i + 50]
        ids = ",".join(secid(c) for c in chunk)
        url = ("https://push2.eastmoney.com/api/qt/ulist.np/get?secids=" + ids +
               "&fields=f2,f3,f4,f5,f6,f12,f13,f14,f15,f16,f17,f18")
        raw = curl(url)
        try:
            data = json.loads(raw).get("data") or {}
        except Exception:
            print(f"  [ulist] 解析失败: {raw[:120]}")
            continue
        for d in (data.get("diff") or []):
            code = f"{d.get('f13')}.{d.get('f12')}"
            # ulist.np 未带 fltt=2 → f2/f3/f15~f18 均为 ×100 的整数
            out[code] = {
                "name": d.get("f14"), "price": _num(d.get("f2")) / 100,
                "pct": _num(d.get("f3")) / 100, "chg": _num(d.get("f4")) / 100,
                "vol_hand": d.get("f5"), "amount": d.get("f6"),
                "high": _num(d.get("f15")) / 100, "low": _num(d.get("f16")) / 100,
                "open": _num(d.get("f17")) / 100, "prev_close": _num(d.get("f18")) / 100,
            }
        time.sleep(0.25)
    return out


def em_clist_all():
    """全 A 快照（分页拉全量）→ 宽度 + 涨幅榜 + 成交额"""
    rows = []
    seen = set()
    pn = 1
    total = None
    while True:
        url = ("https://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=100&po=1&np=1"
               "&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
               "&fields=f2,f3,f5,f6,f12,f14" % pn)
        try:
            d = json.loads(curl(url, timeout=30)).get("data") or {}
        except Exception as e:
            print(f"  [clist p{pn}] {e}")
            break
        if total is None:
            total = d.get("total") or 0
        arr = d.get("diff") or []
        if not arr:
            break
        for x in arr:
            c = str(x.get("f12"))
            if c in seen:
                continue
            seen.add(c)
            p = x.get("f3")
            if p is None:
                continue
            try:
                p = float(p)
            except (TypeError, ValueError):
                continue
            rows.append({"code": c, "name": x.get("f14"), "price": x.get("f2"),
                         "pct": p, "amount": _num(x.get("f6"))})
        if len(seen) >= (total or 0):
            break
        if len(arr) < 100:
            time.sleep(0.8)
            try:
                arr2 = (json.loads(curl(url.replace(f"pn={pn}", f"pn={pn}"), timeout=30))
                        .get("data") or {}).get("diff") or []
            except Exception:
                arr2 = []
            if not arr2:
                break
            for x in arr2:
                c = str(x.get("f12"))
                if c in seen:
                    continue
                seen.add(c)
                p = x.get("f3")
                try:
                    p = float(p)
                except (TypeError, ValueError):
                    continue
                rows.append({"code": c, "name": x.get("f14"), "price": x.get("f2"),
                             "pct": p, "amount": _num(x.get("f6"))})
            if len(rows) >= (total or 0):
                break
        pn += 1
        time.sleep(0.12)
    up = dn = fl = lu = ld = 0
    amt = 0.0
    for r in rows:
        p = r["pct"]
        amt += r["amount"]
        if p > 0:
            up += 1
        elif p < 0:
            dn += 1
        else:
            fl += 1
        if p >= 9.9:
            lu += 1
        if p <= -9.9:
            ld += 1
    rows.sort(key=lambda r: -r["pct"])
    return {"n": len(rows), "up": up, "down": dn, "flat": fl,
            "limit_up": lu, "limit_down": ld,
            "amount_yi": round(amt / 1e8, 1),
            "top_gainers": rows[:30], "rows": rows}


def trends_amount(secid_, ndays=5, tries=4):
    """分时成交额累计：返回 {日期: {分钟: 累计额}}"""
    url = (f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={secid_}"
           "&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
           "&fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&ndays={ndays}")
    out = {}
    for i in range(tries):
        raw = curl(url, timeout=40)
        try:
            d = json.loads(raw).get("data") or {}
        except Exception:
            d = {}
        lines = d.get("trends") or []
        if not lines:
            print(f"  [trends {secid_}] 第 {i+1} 次空返回，{2.5*(i+1):.1f}s 后重试")
            time.sleep(2.5 * (i + 1))
            continue
        out = {}
        for line in lines:
            parts = line.split(",")
            if len(parts) < 7:
                continue
            ts = parts[0]
            try:
                amt = float(parts[6])
            except ValueError:
                continue
            out.setdefault(ts.split(" ")[0], {})[ts.split(" ")[1]] = amt
        return out, d.get("preClose")
    return out, None


def cum_at(day_map, hhmm):
    """截至指定时点（含）的累计成交额 —— trends2 的 amount 本身就是累计值，取最后一个 ≤ cutoff 的点。"""
    # trends2 的 amount 是「每分钟」成交额，不是累计 → 需按分钟求和
    return sum(v for k, v in day_map.items() if k <= hhmm)


if __name__ == "__main__":
    daily = json.loads((CH / "_daily_20261116.json").read_text(encoding="utf-8"))
    last = json.loads((CH / "_last_20261116.json").read_text(encoding="utf-8"))
    codes = list(daily.keys())
    print(f"[collect] 标的 {len(codes)} 只")

    now = datetime.now()
    stamp = now.strftime("%H:%M")
    print(f"[time] {now.strftime('%Y-%m-%d %H:%M')}（盘中快照）")

    print("[1/4] 实时快照 …", flush=True)
    snap = em_ulist(codes)
    print(f"  拿到 {len(snap)}/{len(codes)}")

    print("[2/4] 全 A 快照 …", flush=True)
    allq = em_clist_all()
    print(f"  全 A {allq['n']} 只  涨 {allq['up']} / 跌 {allq['down']} / 平 {allq['flat']}"
          f"  涨9.9+ {allq['limit_up']} 跌9.9- {allq['limit_down']}"
          f"  成交 {allq['amount_yi']:,.0f} 亿")

    print("[3/4] 分时成交额（沪+深，5 日，同时点截断）…", flush=True)
    sh_t, sh_pc = trends_amount("1.000001")
    time.sleep(1.5)
    sz_t, sz_pc = trends_amount("0.399001")
    days = sorted(set(sh_t) | set(sz_t))
    hhmm = stamp
    amt_by_day = {}
    for day in days:
        a = cum_at(sh_t.get(day, {}), hhmm) + cum_at(sz_t.get(day, {}), hhmm)
        amt_by_day[day] = round(a / 1e8, 1)
    print(f"  截至 {hhmm} 累计成交额：{amt_by_day}")

    print("[4/4] 涨停/炸板/跌停池 …", flush=True)
    pools = {}
    for kind, key in [("ZT", "zt"), ("ZB", "zb"), ("DT", "dt")]:
        url = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool"
               f"?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&pageindex=0"
               f"&pagesize=300&sort=fbt:asc&date=20261117")
        try:
            d = json.loads(curl(url)) or {}
        except Exception as e:
            print(f"  [em {kind}] {e}")
            continue
        dd = d.get("data") or {}
        arr = dd.get("pool") or []
        ind = {}
        for x in arr:
            ind[x.get("hybk", "未知")] = ind.get(x.get("hybk", "未知"), 0) + 1
        pools[key] = {"tc": dd.get("tc", 0), "n": len(arr),
                      "industry": dict(sorted(ind.items(), key=lambda kv: -kv[1])),
                      "members": [{"code": x.get("c"), "name": x.get("n"),
                                   "pct": x.get("zdp"), "lbc": x.get("lbc"),
                                   "ind": x.get("hybk")} for x in arr]}
        print(f"  {key}: {dd.get('tc', 0)} 只  {list(pools[key]['industry'].items())[:6]}")
        time.sleep(0.3)

    out = {"stamp": stamp, "date": now.strftime("%Y-%m-%d"),
           "snapshot": snap, "all": {k: v for k, v in allq.items() if k != "rows"},
           "amount_by_day": amt_by_day,
           "amount_cutoff": hhmm,
           "em_pools": pools,
           "top_gainers": allq["top_gainers"]}
    (CH / "_intraday_20261117.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[out] {CH/'_intraday_20261117.json'}")
