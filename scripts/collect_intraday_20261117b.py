"""11/17 盘中补充：全 A 涨跌家数（分页重试）+ 沪深同时点成交额（trends2 重试）。

用法： python3 scripts/collect_intraday_20261117b.py
"""
import json
import subprocess
import time
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")
UA = ["-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://quote.eastmoney.com/"]


def curl(url, timeout=30):
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout)] + UA + [url],
                       capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def clist_page(pn, tries=4):
    url = ("https://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=100&po=1&np=1"
           "&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
           "&fields=f2,f3,f6,f12,f14" % pn)
    for i in range(tries):
        try:
            d = json.loads(curl(url)).get("data") or {}
            arr = d.get("diff") or []
            if arr:
                return arr, d.get("total") or 0
        except Exception:
            pass
        time.sleep(1.2 * (i + 1))
    return [], 0


def trends(secid_, tries=6):
    url = (f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={secid_}"
           "&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
           "&fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&ndays=5")
    for i in range(tries):
        try:
            d = json.loads(curl(url, timeout=40)).get("data") or {}
            lines = d.get("trends") or []
            if lines:
                out = {}
                for line in lines:
                    p = line.split(",")
                    if len(p) < 7:
                        continue
                    try:
                        amt = float(p[6])
                    except ValueError:
                        continue
                    out.setdefault(p[0].split(" ")[0], {})[p[0].split(" ")[1]] = amt
                return out
        except Exception:
            pass
        time.sleep(3.0 * (i + 1))
    return {}


if __name__ == "__main__":
    intr = json.loads((CH / "_intraday_20261117.json").read_text(encoding="utf-8"))
    cutoff = intr["amount_cutoff"]

    print("[1/2] 全 A 分页 …", flush=True)
    rows, seen, total = [], set(), 0
    for pn in range(1, 62):
        arr, t = clist_page(pn)
        if not arr:
            print(f"  p{pn} 空页，停")
            break
        total = total or t
        for x in arr:
            c = str(x.get("f12"))
            if c in seen:
                continue
            seen.add(c)
            try:
                p = float(x.get("f3"))
            except (TypeError, ValueError):
                continue
            rows.append({"code": c, "name": x.get("f14"), "price": x.get("f2"),
                         "pct": p, "amount": _num(x.get("f6"))})
        if pn % 10 == 0:
            print(f"  p{pn} 累计 {len(rows)}/{total}")
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
    print(f"  全 A {len(rows)} 只（total {total}）  涨 {up} / 跌 {dn} / 平 {fl}"
          f"  涨9.9+ {lu} 跌9.9- {ld}  成交 {amt:,.0f} 亿")
    print("  涨幅 TOP10：", [(r['name'], r['pct']) for r in rows[:10]])

    print("[2/2] 沪深同时点成交额 …", flush=True)
    sh = trends("1.000001")
    time.sleep(2.0)
    sz = trends("0.399001")
    days = sorted(set(sh) | set(sz))
    by_day = {}
    for d in days:
        a = 0.0
        for src in (sh, sz):
            m = src.get(d, {})
            a += sum(v for k, v in m.items() if k <= cutoff)
        by_day[d] = round(a / 1e8, 1)
    print(f"  截至 {cutoff} 沪深累计成交额：{by_day}")

    intr["all"] = {"n": len(rows), "up": up, "down": dn, "flat": fl,
                   "limit_up": lu, "limit_down": ld,
                   "amount_yi": round(amt, 1)}
    intr["top_gainers"] = rows[:30]
    intr["amount_by_day"] = by_day
    intr["amount_cutoff"] = cutoff
    intr["breadth_note"] = "东财 clist 全 A 快照（盘中累计成交额）"
    (CH / "_intraday_20261117.json").write_text(
        json.dumps(intr, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[out] _intraday_20261117.json 已更新")
