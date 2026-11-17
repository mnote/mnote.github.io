"""指数日线改用东财口径（与 push2 实时 f5 同源同单位），保证盘中量柱可比。

用法： python3 scripts/fetch_idx_kline_20261117.py
产物： charts/_idxkline_20261117.json
"""
import json
import subprocess
import time
from pathlib import Path

CH = Path("/Users/maoling/workspace/mnote.github.io/charts")
UA = ["-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://quote.eastmoney.com/"]

IDX = {"000001.SH": "1.000001", "399006.SZ": "0.399006",
       "399001.SZ": "0.399001", "000300.SH": "1.000300", "000688.SH": "1.000688"}


def curl(url, timeout=30):
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout)] + UA + [url],
                       capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def kline(secid_, beg="20260901", end="20261117", tries=4):
    url = (f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid_}"
           f"&klt=101&fqt=1&beg={beg}&end={end}"
           f"&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57&lmt=70")
    for i in range(tries):
        try:
            d = json.loads(curl(url)).get("data") or {}
            kl = d.get("klines") or []
            if kl:
                return kl
        except Exception:
            pass
        time.sleep(1.5 * (i + 1))
    return []


if __name__ == "__main__":
    out = {}
    for code, sec in IDX.items():
        kl = kline(sec)
        rows = []
        for line in kl:
            p = line.split(",")
            if len(p) < 7:
                continue
            rows.append({"Date": p[0], "Open": float(p[1]), "Close": float(p[2]),
                         "High": float(p[3]), "Low": float(p[4]),
                         "Volume": float(p[5]), "Amount": float(p[6])})
        out[code] = rows
        print(f"  {code} {len(rows)} 根  最后 {rows[-1] if rows else None}")
        time.sleep(0.4)
    (CH / "_idxkline_20261117.json").write_text(
        json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"[out] {CH/'_idxkline_20261117.json'}")
