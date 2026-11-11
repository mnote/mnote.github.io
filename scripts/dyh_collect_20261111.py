"""都业华 2026-11-11 收评纪要 · 数据采集（探测 + 指数 + 市场宽度 + 板块 + 涨停池 + 中枢）
"""
import csv
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import pandas as pd
import tushare as ts

UA = {"User-Agent": "Mozilla/5.0"}
REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261111"
DATA = RPT / "data"
for p in (RPT, DATA):
    p.mkdir(parents=True, exist_ok=True)
CZ = os.path.expanduser("~/czsc/.venv/bin/czsc")
pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN", "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"))
DATE, PREV = "20261111", "20261110"


def fetch(url, tries=6):
    """东财限流较严（Remote end closed connection），失败要退避重试"""
    for i in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore"))
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url[:110], e)
                return None
            time.sleep(2 + 2 * i)


def em_kline(secid, klt=15, lmt=1000):
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}"
              f"&klt={klt}&fqt=1&lmt={lmt}&end=20500101"
              "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61")
    rows = []
    for kk in (d.get("data") or {}).get("klines", []):
        p = kk.split(",")
        rows.append({"dt": p[0], "o": float(p[1]), "c": float(p[2]), "h": float(p[3]),
                     "l": float(p[4]), "vol": float(p[5]), "amt": float(p[6]), "pct": float(p[8])})
    return rows


def zs_from_bi(bi):
    zss = []
    for i in range(len(bi) - 2):
        a, b, c = bi[i], bi[i + 1], bi[i + 2]
        lo = max(min(a["low"], a["high"]), min(b["low"], b["high"]), min(c["low"], c["high"]))
        hi = min(max(a["low"], a["high"]), max(b["low"], b["high"]), max(c["low"], c["high"]))
        if lo < hi:
            zss.append({"from": a["edt"], "to": c["edt"], "ZD": round(lo, 2), "ZG": round(hi, 2)})
    return zss


def czsc(rows, freq, tag):
    if len(rows) < 40:
        return None
    p = DATA / f"_tmp_{tag}.csv"
    with open(p, "w") as f:
        f.write("dt,symbol,open,close,high,low,vol,amount\n")
        for r in rows:
            f.write(f'{r["dt"]},{r["dt"]},{r["o"]},{r["c"]},{r["h"]},{r["l"]},{r["vol"]},{r["amt"]}\n')
    pr = subprocess.run([CZ, "analyze", str(p), "--freq", freq, "--json"], capture_output=True, text=True, timeout=240)
    try:
        ana = json.loads(pr.stdout)
    except Exception:
        return {"error": (pr.stdout or "")[-200:]}
    bl = ana.get("bi_list") or []
    bi = [{"edt": str(b.get("edt"))[:16], "dir": b.get("direction"), "high": b.get("high"),
           "low": b.get("low"), "power": b.get("power"), "length": b.get("length")} for b in bl]
    zss = zs_from_bi(bi)
    return {"bi": bi, "zs_all": zss, "zs_now": zss[-1] if zss else None, "last_bi": bi[-1] if bi else None}


# ═════════ 0. 探测同花顺全A ═════════
probe = {}
for sid in ["1.881001", "0.881001", "1.000985", "0.399006", "1.000001"]:
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={sid}"
              "&fields=f43,f44,f45,f46,f48,f57,f58,f60,f170")
    x = (d or {}).get("data") or {}
    if x.get("f58"):
        probe[sid] = {"name": x["f58"], "close": x["f43"] / 100, "pct": x["f170"] / 100,
                      "high": x["f44"] / 100, "low": x["f45"] / 100, "prev": x["f60"] / 100,
                      "amount_yi": round((x.get("f48") or 0) / 1e8, 1)}
    time.sleep(0.2)
print("探测:", json.dumps(probe, ensure_ascii=False))

# ═════════ 1. 指数 ═════════
idx_out = {}
IDXLIST = [("上证指数", "1.000001"), ("深证成指", "0.399001"), ("创业板指", "0.399006"),
           ("科创50", "1.000688"), ("沪深300", "1.000300"), ("同花顺全A", "1.881001")]
for nm, sid in IDXLIST:
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={sid}"
              "&fields=f43,f44,f45,f46,f48,f57,f58,f60,f170")
    x = (d or {}).get("data") or {}
    if not x.get("f58"):
        continue
    idx_out[nm] = {"code": x.get("f57"), "close": x["f43"] / 100, "open": x["f46"] / 100,
                    "high": x["f44"] / 100, "low": x["f45"] / 100, "prev": x["f60"] / 100,
                    "pct": x["f170"] / 100, "amount_yi": round((x.get("f48") or 0) / 1e8, 1)}
    time.sleep(0.4)

# 前日成交额（东财口径，用分时累计）
for nm, sid in [("上证指数", "1.000001"), ("深证成指", "0.399001")]:
    d = fetch(f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?secid={sid}&ndays=2"
              "&iscr=0&iscca=0&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
    for dt in [f"2026-11-{d_}" for d_ in ("10", "11")]:
        rows = [t for t in (d or {}).get("data", {}).get("trends", []) if t.startswith(dt)]
        if rows:
            idx_out[nm].setdefault("day_amount", {})[dt] = round(sum(float(t.split(",")[6]) for t in rows) / 1e8, 1)
(RPT / "index_20261111.json").write_text(json.dumps(idx_out, ensure_ascii=False, indent=1), encoding="utf-8")

# ═════════ 2. 市场宽度 + 涨停池 ═════════
market = {}
try:
    df = pro.daily(trade_date=DATE)
    pcts = df["pct_chg"].dropna()
    zt = fetch("https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989"
               f"&dpt=wz.ztzt&pageindex=0&pagesize=300&sort=fbt:asc&date={DATE}")
    dtp = fetch("https://push2ex.eastmoney.com/getTopicDTPool?ut=7eea3edcaed734bea9cbfc24409ed989"
                f"&dpt=wz.ztzt&pageindex=0&pagesize=1&sort=fbt:asc&date={DATE}")
    market["breadth"] = {"n": len(df), "up": int((pcts > 0).sum()), "down": int((pcts < 0).sum()),
                          "flat": int((pcts == 0).sum()), "median_pct": round(float(pcts.median()), 3),
                          "zt_em": (zt or {}).get("data", {}).get("tc"),
                          "dt_em": (dtp or {}).get("data", {}).get("tc")}
    market["total_amount_yi"] = round(df["amount"].sum() / 1e5, 1)
    if zt and zt.get("data"):
        pool = zt["data"]["pool"]
        market["zt_pool"] = [{"code": p["c"], "name": p["n"], "pct": round(float(p["zdp"]), 2),
                              "lbc": p["lbc"], "hy": p.get("hybk", "")} for p in pool]
        from collections import Counter
        market["zt_by_industry"] = dict(Counter(p.get("hybk", "") for p in pool).most_common())
except Exception as e:
    print("market fail", e)

# ═════════ 3. 板块 ═════════
IND_NAMES = ["光伏设备", "电力", "银行", "石油加工贸易", "公路铁路运输", "通用设备", "专用设备",
             "汽车零部件", "医疗器械", "食品饮料", "光学光电", "消费电子零部件及组装", "通信设备",
             "半导体", "元件", "自动化设备", "影视院线", "广告营销", "游戏", "数字媒体", "出版",
             "电子化学品", "仪器仪表", "工程机械"]
CON_NAMES = ["算力概念", "CPO概念", "液冷服务器", "数据中心", "AI应用", "AIGC概念", "ChatGPT概念",
             "AI视频", "AI语料", "短剧互动游戏", "影视概念", "传媒", "多模态AI", "人形机器人",
             "机器人概念", "机器人执行器", "AI眼镜", "AI手机", "AIPC", "智能穿戴", "智能音箱",
             "消费电子", "光通信模块", "虚拟数字人", "Kimi概念", "快手概念", "机器视觉", "传感器",
             "六维传感器", "减速器", "数据采集", "工业母机"]
boards = {}
for bs in ("m:90+t:2", "m:90+t:3"):
    for pn in range(1, 14):
        d = fetch(f"https://push2.eastmoney.com/api/qt/clist/get?fs={bs}&pn={pn}&pz=100"
                  "&po=1&np=1&fltt=2&invt=2&fid=f3&fields=f2,f3,f6,f12,f14,f62,f104,f105,f128,f140")
        if not d or not d.get("data") or not d["data"].get("diff"):
            break
        diff = d["data"]["diff"]
        if isinstance(diff, dict):
            diff = list(diff.values())
        for it in diff:
            boards[it["f12"]] = {"name": it["f14"], "code": it["f12"], "pct": it.get("f3"),
                                 "amount_yi": round((it.get("f6") or 0) / 1e8, 1),
                                 "up": it.get("f104"), "down": it.get("f105"),
                                 "main_net_yi": round((it.get("f62") or 0) / 1e8, 2)}
        if len(diff) < 100:
            break
        time.sleep(0.45)
IND, CON = {}, {}
for want, tgt in ((IND_NAMES, IND), (CON_NAMES, CON)):
    for b in boards.values():
        if b["name"] in want and b["name"] not in tgt:
            tgt[b["name"]] = b
(RPT / "sectors_20261111.json").write_text(json.dumps({"行业": IND, "概念": CON}, ensure_ascii=False, indent=1), encoding="utf-8")

# ═════════ 4. 标的：15 分钟中枢 + 月线 ═════════
TARGETS = {
    "上证指数": ("000001.SH", "1.000001"), "创业板指": ("399006.SZ", "0.399006"),
    "药明康德": ("603259.SH", "1.603259"), "中国船舶": ("600150.SH", "1.600150"),
    "瑞芯微": ("603893.SH", "1.603893"), "伊利股份": ("600887.SH", "1.600887"),
    "中文在线": ("300364.SZ", "0.300364"), "海天瑞声": ("688787.SH", "1.688787"),
    "奥普特": ("688686.SH", "1.688686"), "柯力传感": ("603662.SH", "1.603662"),
    "兆易创新": ("603986.SH", "1.603986"), "云铝股份": ("000807.SZ", "0.000807"),
    "凯莱英": ("002821.SZ", "0.002821"), "昭衍新药": ("603127.SH", "1.603127"),
}
czv = {}
for nm, (tsc, sid) in TARGETS.items():
    rows15 = em_kline(sid, 15, 1000)
    v15 = czsc(rows15, "15分钟", f"{nm}_15m")
    rowsM = em_kline(sid, 103, 300)      # 月线
    vM = czsc(rowsM, "月线", f"{nm}_M") if len(rowsM) >= 40 else None
    rowsW = em_kline(sid, 102, 300)      # 周线
    vW = czsc(rowsW, "周线", f"{nm}_W") if len(rowsW) >= 40 else None
    czv[nm] = {"m15": v15, "month": vM, "week": vW}
    for r in rows15:
        pass
    with open(DATA / f"m15_{nm}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dt", "symbol", "open", "close", "high", "low", "vol", "amount"])
        for r in rows15:
            w.writerow([r["dt"], r["dt"], r["o"], r["c"], r["h"], r["l"], r["vol"], r["amt"]])
    z = (v15 or {}).get("zs_now")
    zm = (vM or {}).get("zs_now")
    print(f"[czsc] {nm}: 15分钟中枢 {z['ZD'] if z else '—'}–{z['ZG'] if z else '—'} | 月线中枢 {zm['ZD'] if zm else '—'}–{zm['ZG'] if zm else '—'}")
    time.sleep(0.4)
(RPT / "czsc_verdict.json").write_text(json.dumps(czv, ensure_ascii=False, indent=1), encoding="utf-8")

# ═════════ 5. 个股行情 + 位置 ═════════
rows_out = []
for nm, (tsc, sid) in TARGETS.items():
    if tsc in ("000001.SH", "399006.SZ"):
        continue
    d = fetch(f"https://push2.eastmoney.com/api/qt/stock/get?secid={sid}"
              "&fields=f43,f44,f45,f46,f48,f57,f58,f60,f116,f170")
    x = (d or {}).get("data") or {}
    try:
        df = pro.daily(ts_code=tsc, start_date="20260601", end_date=DATE).sort_values("trade_date")
        hi60 = float(df["high"].tail(60).max()); lo60 = float(df["low"].tail(60).min())
        ret60 = round((float(df["close"].iloc[-1]) / float(df["close"].iloc[-60]) - 1) * 100, 1)
        df["ma20"] = df["close"].rolling(20).mean()
        ma20 = round(float(df["ma20"].iloc[-1]), 2)
        vol_ma5 = round(float(df["vol"].tail(5).mean()), 0)
        vol_ma20 = round(float(df["vol"].tail(20).mean()), 0)
        # 月线/周线收盘
        mclose = float(df["close"].iloc[-1])
        rows_out.append({"名称": nm, "代码": tsc, "收盘": x["f43"] / 100, "涨跌幅%": x["f170"] / 100,
                         "最高": x["f44"] / 100, "最低": x["f45"] / 100, "昨收": x["f60"] / 100,
                         "成交额亿": round((x.get("f48") or 0) / 1e8, 2),
                         "总市值亿": round((x.get("f116") or 0) / 1e8, 1),
                         "60日高": hi60, "60日低": lo60, "60日涨幅%": ret60, "MA20": ma20,
                         "量MA5": vol_ma5, "量MA20": vol_ma20,
                         "量空头排列": "是" if vol_ma5 < vol_ma20 else "否"})
    except Exception as e:
        print("quote fail", nm, e)
    time.sleep(0.15)
with open(DATA / "quotes_20261111.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    w.writeheader(); w.writerows(rows_out)

# ═════════ 6. 玄学链 ═════════
try:
    sb = pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,industry")
    nm_map = dict(zip(sb["ts_code"], sb["name"]))
    df = pro.daily(trade_date=DATE)
    df["name"] = df["ts_code"].map(nm_map)
    df = df[df["name"].str.contains("东方|羊", na=False)].sort_values("pct_chg", ascending=False)
    with open(DATA / "xuanxue_20261111.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["名称", "代码", "收盘", "涨跌幅%", "成交额亿"])
        for _, r in df.iterrows():
            w.writerow([r["name"], r["ts_code"], r["close"], round(r["pct_chg"], 2), round(r["amount"] / 1e5, 2)])
    market["xuanxue_zt"] = [r["name"] for _, r in df.iterrows() if r["pct_chg"] > 9.8]
except Exception as e:
    print("xuanxue fail", e)

(RPT / "market_20261111.json").write_text(json.dumps(market, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"index": idx_out, "breadth": market.get("breadth")}, ensure_ascii=False, indent=1))
