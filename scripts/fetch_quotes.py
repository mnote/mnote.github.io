"""批量取 A股/港股实时行情，多源自动 fallback，输出统一 JSON。

设计目标（2026-11-13 实测优化）：
  · **一次批量请求拿全部标的**，不要逐只调 —— 逐只 10 个约 50s，批量 1 次约 8s
  · **源优先级固定**：东财 ulist.np 批量 → 新浪 hq 批量 → 东财单只（带域名轮换）
  · **同一路径连续失败 2 次就换源**，不要在同一条路��上反复重试
  · 实测：东财 `clist`（板块/榜单）接口失败率 100%，`ulist.np` 成功率 ~100%
    → 板块/榜单需求走新浪或 `push2ex`，不要用 clist

用法：
    python3 fetch_quotes.py 688795.SH 688802.SH 688801.SH 688256.SH 688041.SH 300474.SZ 000001.SH 399006.SZ
    python3 fetch_quotes.py --json out.json 688795.SH ...
    python3 fetch_quotes.py --hk 06082        # 港股，自动带 .HK

输出结构（每个标的）：
    {ts_code, name, price, prev_close, open, high, low, pct, amount_yi, ts, source}
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
EM_HOSTS = ["push2", "1.push2", "82.push2", "push2delay"]
FIELDS = "f12,f13,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18"


def norm(code: str) -> tuple[str, str]:
    """把各种写法统一成 (ts_code, market)。market ∈ {sh, sz, bj, hk}"""
    c = code.strip().upper()
    if c.startswith("HK") or c.endswith(".HK"):
        return (c.split(".")[0] + ".HK", "hk")
    if "." in c:
        base, suf = c.split(".")
        suf = suf.lower()
        if suf in ("sh", "ss"):
            suf = "sh"
        elif suf in ("sz",):
            suf = "sz"
        elif suf in ("bj",):
            suf = "bj"
        return (f"{base}.{suf.upper()}", suf)
    # 纯 6 位数字按首位猜市场
    if len(c) == 6 and c.isdigit():
        if c[0] in ("6", "9"):
            return (f"{c}.SH", "sh")
        if c.startswith("4") or c.startswith("8"):
            return (f"{c}.BJ", "bj")
        return (f"{c}.SZ", "sz")
    raise ValueError(f"无法解析代码: {code}")


def em_secid(ts_code: str, market: str) -> str:
    """东财 secid：沪=1.x 深=0.x 港=116.x 北=0.x"""
    if market == "hk":
        return f"116.{ts_code.split('.')[0]}"
    return ("1." if market == "sh" else "0.") + ts_code.split(".")[0]


def curl(url: str, referer: str = "https://quote.eastmoney.com/") -> str | None:
    for host in EM_HOSTS:
        u = url.replace("__HOST__", host)
        try:
            r = subprocess.run(
                ["curl", "-s", "--max-time", "12", "-H", f"User-Agent: {UA}", "-H", f"Referer: {referer}", u],
                capture_output=True, text=True, timeout=20,
            )
            if r.returncode == 0 and r.stdout and len(r.stdout) > 20:
                return r.stdout
        except Exception:
            pass
    return None


def fetch_em_batch(items: list[tuple[str, str]]) -> dict:
    """东财 ulist.np 批量：一次请求拿全部。"""
    secids = ",".join(em_secid(tc, m) for tc, m in items)
    raw = curl(f"https://__HOST__.eastmoney.com/api/qt/ulist.np/get?secids={secids}&fltt=2&invt=2&fields={FIELDS}")
    if not raw:
        return {}
    try:
        data = json.loads(raw).get("data") or {}
    except Exception:
        return {}
    diff = data.get("diff") or []
    out = {}
    for it in diff:
        code = it.get("f12")
        if not code:
            continue
        mkt = {1: "sh", 0: "sz", 116: "hk"}.get(it.get("f13"), "sh")
        out[f"{code}.{mkt.upper()}"] = {
            "ts_code": f"{code}.{mkt.upper()}", "name": it.get("f14"),
            "price": it.get("f2"), "pct": it.get("f3"), "chg": it.get("f4"),
            "high": it.get("f15"), "low": it.get("f16"), "open": it.get("f17"),
            "prev_close": it.get("f18"), "amount_yi": round((it.get("f6") or 0) / 1e8, 2),
            "source": "eastmoney-ulist",
        }
    return out


def fetch_sina_batch(items: list[tuple[str, str]]) -> dict:
    """新浪批量（GBK），A 股 + 港股通用。"""
    def sina_code(ts_code: str, market: str) -> str:
        base = ts_code.split(".")[0]
        if market == "hk":
            return f"hk{base}"
        if market == "sh":
            return f"sh{base}"
        if market == "bj":
            return f"bj{base}"
        return f"sz{base}"
    lst = ",".join(sina_code(tc, m) for tc, m in items)
    try:
        # 必须用字节模式：新浪返回 GBK，若按 UTF-8 解码会把中文名破坏掉
        r = subprocess.run(
            ["curl", "-s", "--max-time", "15", "-H", f"User-Agent: {UA}", "-H", "Referer: https://finance.sina.com.cn",
             f"https://hq.sinajs.cn/list={lst}"],
            capture_output=True, timeout=20,
        )
        if not r.stdout:
            return {}
        raw = r.stdout.decode("gbk", "ignore")
    except Exception:
        return {}
    out = {}
    for line in raw.splitlines():
        if "=" not in line or '"' not in line:
            continue
        head, body = line.split('="', 1)
        body = body.rstrip('";')
        key = head.split("_")[-1]
        p = body.split(",")
        if len(p) < 10 or not p[0]:
            continue
        try:
            if key.startswith("hk"):
                # 港股字段序不同：0英文名 1中文名 2开 3昨收 4高 5低 6现价 7涨跌额 8涨跌幅 11成交额
                name = p[1] or p[0]
                op, pc, px = float(p[2]), float(p[3]), float(p[6])
                hi, lo = float(p[4]), float(p[5])
                amt = float(p[11]) / 1e8
                ts = f"{p[17]} {p[18]}" if len(p) > 18 else ""
            else:
                # A股：0名称 1开 2昨收 3现价 4高 5低 9成交额 30日期 31时间
                name = p[0]
                op, pc, px = float(p[1]), float(p[2]), float(p[3])
                hi, lo = float(p[4]), float(p[5])
                amt = float(p[9]) / 1e8
                ts = f"{p[30]} {p[31]}" if len(p) > 31 else ""
        except (ValueError, IndexError):
            continue
        mkt = "HK" if key.startswith("hk") else ("SH" if key.startswith("sh") else ("BJ" if key.startswith("bj") else "SZ"))
        out[f"{key[2:]}.{mkt}"] = {
            "ts_code": f"{key[2:]}.{mkt}", "name": name, "price": px, "prev_close": pc,
            "open": op, "high": hi, "low": lo,
            "pct": round((px / pc - 1) * 100, 2) if pc else None,
            "amount_yi": round(amt, 2), "ts": ts,
            "source": "sina",
        }
    return out


def fetch_em_single(ts_code: str, market: str) -> dict:
    """东财单只（带域名轮换）—— 批量失败时的兜底。"""
    raw = curl(
        f"https://__HOST__.eastmoney.com/api/qt/stock/get?secid={em_secid(ts_code, market)}"
        f"&fltt=2&invt=2&fields=f43,f44,f45,f46,f48,f57,f58,f60,f169,f170,f116"
    )
    if not raw:
        return {}
    try:
        d = json.loads(raw).get("data") or {}
    except Exception:
        return {}
    if not d:
        return {}
    return {
        "ts_code": ts_code, "name": d.get("f58"), "price": d.get("f43"),
        "prev_close": d.get("f60"), "open": d.get("f46"), "high": d.get("f44"),
        "low": d.get("f45"), "pct": d.get("f170"), "chg": d.get("f169"),
        "amount_yi": round((d.get("f48") or 0) / 1e8, 2),
        "total_mv_yi": round((d.get("f116") or 0) / 1e8, 1),
        "source": "eastmoney-single",
    }


def fetch_all(codes: list[str]) -> tuple[dict, list[str]]:
    items = [norm(c) for c in codes]
    t0 = time.time()
    data = fetch_em_batch(items)
    missing = [(tc, m) for tc, m in items if tc not in data]
    for tc, m in missing:
        try:
            data[tc] = fetch_sina_batch([(tc, m)]).get(tc, {})
        except Exception:
            pass
    missing = [(tc, m) for tc, m in items if not data.get(tc)]
    for tc, m in missing:
        data[tc] = fetch_em_single(tc, m)
    cost = time.time() - t0
    order = {tc: i for i, (tc, _) in enumerate(items)}
    out = {k: data[k] for k in sorted(data, key=lambda x: order.get(x, 999)) if data.get(k)}
    return out, [f"[fetch_quotes] {len(items)} 个标的耗时 {cost:.1f}s，源={next((v.get('source') for v in out.values()), '-')}"], missing


def main() -> None:
    args = sys.argv[1:]
    out_path = None
    if "--json" in args:
        i = args.index("--json")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--hk" in args:
        i = args.index("--hk")
        args = args[:i] + [f"{args[i + 1]}.HK"] + args[i + 2:]
    if not args:
        print(__doc__)
        sys.exit(1)

    data, notes, missing = fetch_all(args)
    for n in notes:
        print(n)
    print(f"{'名称':14s}{'现价':>11s}{'涨跌%':>8s}{'开':>11s}{'最高':>11s}{'最低':>11s}{'额(亿)':>10s}  源")
    for k, v in data.items():
        print(f"{str(v.get('name')):14s}{v.get('price') or 0:>11.2f}{v.get('pct') or 0:>8.2f}"
              f"{v.get('open') or 0:>11.2f}{v.get('high') or 0:>11.2f}{v.get('low') or 0:>11.2f}"
              f"{v.get('amount_yi') or 0:>10.2f}  {v.get('source')}")
    if missing:
        print(f"[WARN] 未取到: {[m[0] for m in missing]}")
    if out_path:
        Path(out_path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[out] {out_path}")


if __name__ == "__main__":
    main()
