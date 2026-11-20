"""都业华 2026-11-20 午评 · 上午 11:30 口径的板块篮子（腾讯 5 日分时点位）

背景：13:1x 才开采集，新浪快照已是下午盘；老师原文讲的是「上午」板块异动，
     必须用 11:30 收点位重算篮子均值，否则会拿下午盘否定老师判断。

输入：reports/duyiehua-20261120/data_20261120.json（含新浪快照的昨收/名称）
输出：reports/duyiehua-20261120/morning_20261120.json
"""
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261120"
D = json.loads((RPT / "data_20261120.json").read_text(encoding="utf-8"))
SNAP = D["snapshot_raw"]
BASKETS = {
    "银行": ["600036", "601398", "601939", "601288", "601166"],
    "电力/高股息": ["600900", "600025", "600886", "600674", "601985"],
    "煤炭/石油": ["601088", "600028", "601857", "600938", "601808"],
    "家电": ["000333", "000651", "600690", "600060", "002508"],
    "公路": ["600377", "600350", "600012", "601107", "600548"],
    "饮料制造": ["605499", "000848", "300997", "603156", "605337"],
    "AI视频/传媒": ["300364", "300133", "300182", "300251", "603533",
                    "300418", "601595"],
    "半导体": ["603893", "603986", "688256", "688041", "688981", "002371"],
    "算力/CPO": ["601138", "300308", "300502", "002463", "300476"],
    "人形机器人": ["000700", "300115", "002050", "601689", "688017",
                   "603728", "003021", "603009", "300124"],
    "元件/PCB": ["002463", "300476", "600183", "002916", "603228",
                 "002384", "002938", "002815"],
    "国产算力": ["688981", "688041", "002261", "000158", "600839",
                 "301236", "603019"],
}


def sym(code):
    return ("sh" if code[0] == "6" else "sz") + code


def tx_day(code):
    """腾讯 5 日分时 → 取今日上午点位"""
    s = sym(code)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/day/query?code={s}"
    for i in range(3):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "20", "-H", "User-Agent: Mozilla/5.0", url],
                               capture_output=True)
            j = json.loads(r.stdout.decode("utf-8", "ignore"))
            data = j["data"][s]["data"]
            for day in data:
                d = str(day.get("date", ""))
                if d in ("20261120", "2026-11-20"):
                    rows = day.get("data") or []
                    am = []
                    amt1130 = None
                    for row in rows:
                        p = row.split() if isinstance(row, str) else row
                        try:
                            t = str(p[0])
                            px = float(p[1])
                            a = float(p[3])
                        except Exception:
                            continue
                        if t <= "1130":
                            am.append((t, px))
                            if t == "1130":
                                amt1130 = a
                    if not am:
                        continue
                    close1130 = [px for t, px in am if t == "1130"]
                    return {"o": am[0][1], "h": max(p for _, p in am),
                            "l": min(p for _, p in am),
                            "c": close1130[-1] if close1130 else am[-1][1],
                            "amt_1130": amt1130}
        except Exception:
            time.sleep(0.6 + i)
    return None


codes = sorted({c for ids in BASKETS.values() for c in ids})
with ThreadPoolExecutor(max_workers=10) as ex:
    results = dict(zip(codes, ex.map(tx_day, codes)))
print("fetched", sum(1 for v in results.values() if v), "/", len(codes))

out = {}
for bname, ids in BASKETS.items():
    mem = []
    for code in ids:
        m = results.get(code)
        sp = SNAP.get(sym(code))
        if not m or not sp or not sp.get("prev"):
            continue
        prev = sp["prev"]
        mem.append({
            "code": code, "name": sp["name"], "prev": prev,
            "am_open": m["o"], "am_high": m["h"], "am_low": m["l"], "am_close": m["c"],
            "pct": round((m["c"] / prev - 1) * 100, 2),
            "amt_yi": round((m["amt_1130"] or 0) / 1e8, 2),
            "now": sp["price"], "now_pct": round((sp["price"] / prev - 1) * 100, 2),
        })
    if not mem:
        continue
    out[bname] = {
        "avg_pct": round(sum(m["pct"] for m in mem) / len(mem), 2),
        "n": len(mem),
        "up": sum(1 for m in mem if m["pct"] > 0),
        "down": sum(1 for m in mem if m["pct"] < 0),
        "amt_yi": round(sum(m["amt_yi"] for m in mem), 1),
        "members": mem,
    }
    print(f"  {bname}: 上午均值 {out[bname]['avg_pct']:+.2f}% "
          f"({out[bname]['up']}/{out[bname]['down']}) 额 {out[bname]['amt_yi']} 亿")

(RPT / "morning_20261120.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", RPT / "morning_20261120.json")
