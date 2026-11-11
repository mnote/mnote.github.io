"""11/11 盘中市场统计：涨停/跌停池、全 A 涨跌家数与成交额。

用法： python3 scripts/collect_market_20261111.py
"""
import json
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}
DATE = "20261111"


def get(u):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url=u, headers=UA), timeout=25).read())


def pool(kind):
    u = (f"https://push2ex.eastmoney.com/getTopic{kind}Pool"
         "?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt"
         f"&pageindex=0&pagesize=300&sort=fbt:asc&date={DATE}")
    try:
        d = get(u).get("data")
    except Exception as e:
        print(f"  [ERR] {kind}: {e}")
        return []
    return (d or {}).get("pool") or []


def all_a():
    """全 A 快照（翻页）。"""
    out = []
    for pn in range(1, 80):
        u = ("https://push2.eastmoney.com/api/qt/clist/get?"
             f"pn={pn}&pz=100&po=1&np=1&fltt=2&invt=2&fid=f3&"
             "fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&"
             "fields=f3,f6,f12,f14")
        try:
            d = get(u).get("data")
        except Exception as e:
            print(f"  [ERR] all_a pn={pn}: {e}")
            break
        if not d or not d.get("diff"):
            break
        out += d["diff"]
        time.sleep(0.1)
    return out


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}

    zt = pool("ZT")
    dt = pool("DT")
    print(f"=== 涨停 {len(zt)} 家 / 跌停 {len(dt)} 家 ===")
    multi = [x for x in zt if (x.get("lbc") or 1) >= 2]
    print(f"连板 >=2：{len(multi)} 只")
    for x in sorted(multi, key=lambda r: -(r.get("lbc") or 1)):
        print(f"   {x.get('lbc')}板 {x.get('n')}({x.get('c')}) "
              f"{x.get('zdp'):+.2f}% 封单 {(x.get('fund') or 0)/1e8:.2f}亿 "
              f"换手{x.get('hs'):.1f}% 行业 {x.get('hybk')}")
    res["zt"] = [{k: x.get(k) for k in ("c", "n", "lbc", "zdp", "fund",
                                        "hybk", "amount", "fbt", "hs", "p")} for x in zt]
    res["dt"] = [{k: x.get(k) for k in ("c", "n", "lbc", "zdp", "fund")} for x in dt]

    rows = all_a()
    up = sum(1 for x in rows if isinstance(x.get("f3"), (int, float)) and x["f3"] > 0)
    dn = sum(1 for x in rows if isinstance(x.get("f3"), (int, float)) and x["f3"] < 0)
    fl = len(rows) - up - dn
    amt = sum(x.get("f6") or 0 for x in rows if isinstance(x.get("f6"), (int, float)))
    print(f"\n=== 全 A {len(rows)} 只：涨 {up} / 跌 {dn} / 平 {fl} ===")
    print(f"盘中累计成交额 {amt/1e8:.0f} 亿（{amt/1e12:.3f} 万亿）")
    res["all_a"] = {"total": len(rows), "up": up, "down": dn, "flat": fl,
                    "amount_yi": round(amt / 1e8, 0)}

    (out_dir / "_market_20261111.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {out_dir / '_market_20261111.json'}")
