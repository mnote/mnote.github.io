"""11/11 盘中实时行情 + 分时快照（东财接口）。

用途：
  1) 核验博主盘中每条说法（三大CPO龙头领先 / 端侧龙头改写新高 / 指数红绿）
  2) 为 K 线图补 11/11 当日未完成 K 线（open/high/low/当前价/量）
  3) 输出 KPI JSON

用法： python3 scripts/collect_quotes_20261111.py
"""
import json
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}

QUOTE_FIELDS = "f43,f44,f45,f46,f47,f48,f57,f58,f60,f169,f170,f86,f168"


def get(u):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url=u, headers=UA), timeout=25).read())


IDX_SECID = {"000001": "1.000001", "399001": "0.399001", "399006": "0.399006",
             "000688": "1.000688", "000300": "1.000300"}


def secid(code: str) -> str:
    """指数走白名单；个股 60/68 开头为沪市，其余深市。"""
    if code in IDX_SECID:
        return IDX_SECID[code]
    if code.startswith(("60", "68", "51", "58", "11", "900", "5")):
        return f"1.{code}"
    return f"0.{code}"


def quote(code: str, name: str = "") -> dict:
    u = (f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid(code)}"
         f"&fltt=2&invt=2&fields={QUOTE_FIELDS}")
    try:
        d = get(u).get("data")
    except Exception as e:
        return {"code": code, "error": str(e)}
    if not d:
        return {"code": code, "error": "no data"}
    return {
        "code": code, "name": d.get("f58") or name,
        "price": d.get("f43"), "high": d.get("f44"), "low": d.get("f45"),
        "open": d.get("f46"), "vol": d.get("f47"), "amount": d.get("f48"),
        "prev_close": d.get("f60"), "chg": d.get("f169"), "pct": d.get("f170"),
        "ts": d.get("f86"),
    }


def trends(code: str) -> list:
    """返回 [{'t':'09:30','c':..,'h':..,'l':..}, ...] 当日分时。"""
    u = ("https://push2his.eastmoney.com/api/qt/stock/trends2/get?"
         f"secid={secid(code)}&fields1=f1,f2,f3,f4,f5,f6&"
         "fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&ndays=1")
    try:
        d = get(u).get("data")
    except Exception:
        return []
    if not d or not d.get("trends"):
        return []
    out = []
    for s in d["trends"]:
        p = s.split(",")
        out.append({"t": p[0][-5:], "o": float(p[1]), "c": float(p[2]),
                    "h": float(p[3]), "l": float(p[4])})
    return out


def at(tr: list, hhmm: str):
    """取 hhmm 时点及之前最后一根分时的 close。"""
    r = [x for x in tr if x["t"] <= hhmm]
    return r[-1] if r else None


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out_dir.mkdir(parents=True, exist_ok=True)

    IDX = [("000001", "上证指数"), ("399001", "深成指"), ("399006", "创业板指"),
           ("000688", "科创50"), ("000300", "沪深300")]

    STOCKS = [
        ("300308", "中际旭创"), ("300502", "新易盛"), ("300394", "天孚通信"),
        ("603986", "兆易创新"), ("301308", "江波龙"), ("001309", "德明利"),
        ("688525", "佰维存储"), ("300475", "香农芯创"),
        ("603893", "瑞芯微"), ("301536", "星宸科技"), ("688332", "中科蓝讯"),
        ("688836", "宇树科技"), ("688585", "上纬新材"), ("688256", "寒武纪"),
        ("002708", "光洋股份"), ("300602", "飞荣达"),
        ("688498", "源杰科技"), ("603083", "剑桥科技"), ("300570", "太辰光"),
        ("301517", "陕西华达"),
    ]

    res = {"index": {}, "stock": {}, "trends": {}}

    print("=== 指数 ===")
    for c, n in IDX:
        q = quote(c, n)
        res["index"][c] = q
        print(f"  {q.get('name', n):8s} {q.get('price')} "
              f"{q.get('pct'):+.2f}%  开{q.get('open')} 高{q.get('high')} "
              f"低{q.get('low')} 昨收{q.get('prev_close')}")
        res["trends"][c] = trends(c)
        time.sleep(0.15)

    print("\n=== 个股 ===")
    for c, n in STOCKS:
        q = quote(c, n)
        res["stock"][c] = q
        print(f"  {q.get('name', n):10s} {q.get('price')} {q.get('pct'):+.2f}% "
              f"开{q.get('open')} 高{q.get('high')} 低{q.get('low')} "
              f"昨收{q.get('prev_close')} 额{(q.get('amount') or 0)/1e8:.1f}亿")
        time.sleep(0.12)

    # 博主发帖时点核对所需分时
    print("\n=== 分时核对 ===")
    for c in ["000001", "399001", "399006", "300308", "300502", "300394",
              "603986", "301308", "603893", "301536", "688332", "688836",
              "002708", "300475", "688525", "001309", "688256", "688585"]:
        tr = trends(c)
        res["trends"][c] = tr
        if not tr:
            print(f"  {c}: no trends")
            continue
        marks = ["09:30", "10:17", "10:20", "10:29", "10:41", "10:58", "11:11",
                 "11:17", "11:52", "13:00"]
        seg = " ".join(f"{m}={at(tr, m)['c'] if at(tr, m) else '-'}" for m in marks)
        print(f"  {c}: {seg}")
        time.sleep(0.12)

    p = out_dir / "_quote_20261111.json"
    p.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {p}")
