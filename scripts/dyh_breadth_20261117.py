"""都业华 2026-11-16 午评 · 全 A 宽度采集（新浪 Market_Center 分页，盘中 11:30 口径）

⛔ 只用实时快照与日线，不调用分钟级 K 线 / czsc。
输出：reports/duyiehua-20261117/breadth_20261117.json
"""
import json
import re
import subprocess
import time
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261117"
RPT.mkdir(parents=True, exist_ok=True)
HDR = ["User-Agent: Mozilla/5.0", "Referer: https://finance.sina.com.cn"]
NODE = "hs_a"


def page(pn, num=100):
    url = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
           f"Market_Center.getHQNodeData?page={pn}&num={num}&sort=symbol&asc=1&node={NODE}&symbol=&_s_r_a=page")
    for i in range(4):
        r = subprocess.run(["curl", "-s", "--max-time", "25", "-H", HDR[0], "-H", HDR[1], url],
                           capture_output=True, text=True)
        out = r.stdout.strip()
        if out and out.startswith("["):
            try:
                return json.loads(out)
            except Exception:
                pass
        time.sleep(1.0 + i)
    return None


up = down = flat = 0
n = 0
lim_up = lim_dn = 0
up5 = dn5 = dn9 = 0
amount = 0.0
pn = 1
t0 = time.time()
while True:
    d = page(pn)
    if not d:
        print("stop at page", pn)
        break
    if not d:
        break
    for it in d:
        n += 1
        p = it.get("changepercent")
        if p is None or p == "":
            continue
        try:
            p = float(p)
        except (TypeError, ValueError):
            continue
        amount += float(it.get("amount") or 0)
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
        if p >= 5:
            up5 += 1
        if p <= -5:
            dn5 += 1
        if p <= -9:
            dn9 += 1
    if len(d) < 100:
        break
    pn += 1
    if pn % 10 == 0:
        print(f"page {pn} n={n} {time.time()-t0:.0f}s", flush=True)

out = {"n": n, "up": up, "down": down, "flat": flat,
       "lim_up_9_8": lim_up, "lim_dn_9_8": lim_dn,
       "up_5": up5, "down_5": dn5, "down_9": dn9,
       "amount_yi": round(amount / 1e8, 1),
       "snapshot": "2026-11-17 13:25", "source": "新浪 Market_Center hs_a"}
print(json.dumps(out, ensure_ascii=False))
(RPT / "breadth_20261117.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
