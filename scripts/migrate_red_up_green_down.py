#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把报告页的涨跌配色从「绿涨红跌」改为「红涨绿跌」（A 股惯例）。

原则
  1. 只改「股价 / 涨跌幅」语义的颜色；`--bull` / `--bear` 状态色变量不动，
     tag-bull / tag-bear / pill 等警示标签配色不受影响。
  2. 新增 `--up`（红 #e63946）/ `--down`（绿 #2a9d8f）语义变量，与 K 线图
     MC_UP / MC_DOWN 完全一致。
  3. 立场标签、图例、命中计数、量能（成交额 / 放量 / 缩量）保持非涨跌语义；
     量能数字改中性色 `--neutral`。
  4. K 线图为静态 PNG，本身已是红涨绿跌，不动。

用法
  python3 scripts/migrate_red_up_green_down.py            # dry-run，只报告
  python3 scripts/migrate_red_up_green_down.py --apply     # 写盘
"""
import argparse
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UP_HEX = "#e63946"      # 涨（A 股红）
DOWN_HEX = "#2a9d8f"    # 跌（A 股绿）

# ------------------------------------------------------------------ 文件清单
# A 组：绿涨红跌体系（--bull 绿 / --bear 红），需新增 --up/--down 并改 .up/.down
GROUP_A = [
    "2026-09-26-wu2198-investment-report.html",
    "2026-09-27-wu2198-investment-report.html",
    "2026-09-28-wu2198-investment-report.html",
    "2026-09-29-wu2198-investment-report.html",
    "2026-09-30-wu2198-investment-report.html",
    "2026-10-01-wu2198-investment-report.html",
    "2026-10-02-wu2198-investment-report.html",
    "2026-10-03-wu2198-investment-report.html",
    "2026-10-04-wu2198-investment-report.html",
    "2026-10-06-wu2198-investment-report.html",
    "2026-10-07-wu2198-investment-report.html",
    "2026-10-08-wu2198-investment-report.html",
    "2026-10-09-wu2198-investment-report.html",
    "2026-10-10-wu2198-investment-report.html",
    "2026-10-11-wu2198-investment-report.html",
    "2026-10-12-wu2198-investment-report.html",
    "2026-10-13-wu2198-investment-report.html",
    "2026-10-14-wu2198-investment-report.html",
    "2026-11-04-wu2198-investment-report.html",
    "2026-11-05-wu2198-investment-report.html",
    "2026-11-06-wu2198-investment-report.html",
    "2026-11-08-wu2198-investment-report.html",
    "2026-11-09-wu2198-investment-report.html",
    "2026-11-10-wu2198-investment-report.html",
    "2026-11-11-wu2198-investment-report.html",
    "2026-11-12-wu2198-investment-report.html",
    "wu2198-investment-report-20260905.html",
    "wu2198-investment-report-20260912.html",
    "2026-11-09-都业华-高级班收评纪要.html",
    "2026-11-10-都业华-高级班收评纪要.html",
    "2026-11-11-都业华-高级班收评纪要.html",
    "2026-11-12-都业华-高级班收评纪要.html",
    "2026-11-12-都业华-高级班午评纪要.html",
    "_posts/2026-09-04-wu2198-investment-report.html",
    "_posts/2026-09-05-wu2198-investment-report.html",
    "_posts/2026-09-13-wu2198-investment-report.html",
    "_posts/2026-09-25-wu2198-investment-report.html",
    "_posts/2026-11-09-都业华-高级班收评纪要.html",
    "_posts/2026-11-10-都业华-高级班收评纪要.html",
    "_posts/2026-11-11-都业华-高级班收评纪要.html",
    "_posts/2026-11-12-都业华-高级班收评纪要.html",
    "_posts/2026-11-12-都业华-高级班午评纪要.html",
]

# B 组：已定义 --up/--down（红涨绿跌），但 .signal-up/.signal-down 仍指向 --bull/--bear
GROUP_B = [
    "wu2198-investment-report-20260829.html",
    "wu2198-investment-report-20260830.html",
    "wu2198-investment-report-20260831.html",
    "wu2198-investment-report-20260904.html",
]

ALL_FILES = GROUP_A + GROUP_B

# 生成脚本（模板内含同样的 CSS / 内联色，重跑不能回退成绿涨红跌）
SCRIPTS = [
    "scripts/gen_dyh_report.py",
    "scripts/gen_dyh_report_20261110.py",
    "scripts/gen_dyh_report_20261111.py",
    "scripts/gen_dyh_report_20261112.py",
    "scripts/gen_dyh_report_20261112_close.py",
    "scripts/gen_wu2198_report_20260912.py",
    "scripts/gen_wu2198_report_20260926.py",
    "scripts/gen_wu2198_report_20260927.py",
    "scripts/gen_wu2198_report_20261001.py",
    "scripts/gen_wu2198_report_20261006.py",
    "scripts/gen_wu2198_report_20261012.py",
    "scripts/gen_wu2198_report_20261108.py",
    "scripts/gen_wu2198_report_20261109.py",
    "scripts/gen_wu2198_report_20261110.py",
    "scripts/gen_wu2198_report_20261111.py",
    "scripts/gen_wu2198_report_20261111_close.py",
    "scripts/gen_wu2198_report_20261112.py",
    "scripts/gen_wu2198_report_20261111_slim.py",
]

# 脚本内裸价格的 Tushare 核实覆盖
SCRIPT_OVERRIDES = {
    "scripts/gen_wu2198_report_20261006.py": {
        "808.44 (—)": "down",   # 300308.SZ 20260930 pct_chg -0.56%
        "411.16 (—)": "up",     # 601869.SH 20260930 pct_chg +0.79%
    },
}

# ------------------------------------------------------------------ 内联判定
# 「圆点 emoji 开头」= 立场标签，文字颜色必须与 emoji 一致，保持原样
RE_DOT = re.compile(r"^[🟢🔴🟡⚪⚫🔵]\s")
RE_LEGEND = re.compile(r"阳线（红）|阴线（绿）|红\s*K$|绿\s*K$")
RE_RATIO = re.compile(r"^\d+\s*/\s*\d+$")
RE_PCT = re.compile(r"([+-]\s?\d+(?:\.\d+)?\s?%)")
RE_PCT_LEAD = re.compile(r"^\(?[+-]\s?\d+(?:\.\d+)?\s?%")
RE_BARE = re.compile(r"^[\d,]+(?:\.\d+)?$")
RE_TICK = re.compile(r"^[\d,]+(?:\.\d+)?\s*亿$")
RE_NEG_TICK = re.compile(r"^-[\d,]+(?:\.\d+)?\s*亿$")
RE_COUNT = re.compile(r"^[\d,]+\s*(?:只|条|家)$")

RE_PCT_UP = re.compile(r"\+")
RE_UP_KW = re.compile(
    r"突破|站上|新高|守在上方|仍在上方|反弹|金叉|柱状转正|柱转正|收窄|逆势|改写|刷新")
RE_DOWN_KW = re.compile(
    r"跌破|已破|失守|破位|逼近|冲高回落|继续下行|跌多于涨|净流出|净流入|"
    r"收全天最低|今日收盘即|跌破\s*MA|跌|🔻|距[^，。]{0,24}仅")

# 个别裸价格无涨跌幅可查，用 Tushare 核实后的方向覆盖（file → {文本: 方向}）
OVERRIDES = {
    "_posts/2026-09-13-wu2198-investment-report.html": {
        "3322.04": "down",      # 399006.SZ 20260911 pct_chg -0.49%
    },
    "2026-10-06-wu2198-investment-report.html": {
        "808.44 (—)": "down",   # 300308.SZ 20260930 pct_chg -0.56%
        "411.16 (—)": "up",     # 601869.SH 20260930 pct_chg +0.79%
    },
    "2026-10-07-wu2198-investment-report.html": {
        "808.44 (—)": "down",   # 300308.SZ 20260930 pct_chg -0.56%
    },
}

# 逐条手工修正（file → [(旧片段, 新片段)]）
SPECIAL_FIXES = {
    # 板块均值 -0.89% 原被误标为 .up（绿涨），数值本身为负 → 改为 .down（绿跌）
    "2026-11-08-wu2198-investment-report.html": [
        ('<b class="up">-0.89%</b>', '<b class="down">-0.89%</b>'),
    ],
    # 个股卡收盘价：默认跌绿；中国神华为 8 只标的中唯一强势 → 红
    "_posts/2026-09-13-wu2198-investment-report.html": [
        ('<div class="price">¥47.51</div>',
         '<div class="price" style="color:var(--up)">¥47.51</div>'),
    ],
}


def classify(text, ctx="", near_after="", near_before="", orig_var="bull", rel=""):
    """返回 up / down / vol / keep。

    keep = 该处不是「涨跌语义」（立场标签、图例、命中计数、引用），
           文字颜色必须与原有 emoji / 语义一致，因此保留原 var(--bull)/var(--bear)。
    """
    t = (text or "").strip()

    ov = OVERRIDES.get(rel, {}).get(t) or SCRIPT_OVERRIDES.get(rel, {}).get(t)
    if ov:
        return ov

    # ---------- 非涨跌语义：保留原色 ----------
    if RE_DOT.match(t):
        return "keep"
    if re.match(r"^\[[^\]]+\]\s*⚠", t):
        return "keep"
    if RE_LEGEND.search(t):
        return "keep"
    if RE_RATIO.match(t):
        return "keep"
    if RE_COUNT.match(t):
        if re.search(r"只$", t):
            return "down"          # 下跌家数
        return "keep"               # 条数
    if t == "[思考]":
        return "keep"
    if re.search(r"PSL|收盘补充|跟单警示|唯一隐含信号|就忘记了本质", t):
        return "keep"
    if re.search(r"银行\+固态电池|银行\+白酒", t):
        return "keep"

    # ---------- 量能：无涨跌含义 → 中性色 ----------
    if RE_TICK.match(t) and not t.startswith("-"):
        return "vol"
    if RE_NEG_TICK.match(t):
        return "down"              # 资金净流出
    if re.search(r"放量|缩量", t):
        return "vol"
    if re.search(r"量比", ctx) and RE_BARE.match(t):
        return "vol"

    # ---------- 涨跌语义 ----------
    # 1) 文本自带涨跌号
    m = RE_PCT_LEAD.search(t)
    if m:
        return "up" if RE_PCT_UP.search(m.group(0)) else "down"
    mp = RE_PCT.search(t)
    if mp:
        return "up" if RE_PCT_UP.search(mp.group(0)) else "down"

    # 2) 文本本身带方向
    if RE_DOWN_KW.search(t):
        return "down"
    if RE_UP_KW.search(t):
        return "up"

    # 3) 裸价格：就近涨跌幅 → 关键词 → 原色极性
    if RE_BARE.match(t) or RE_TICK.match(t):
        for zone in (near_after, near_before):
            mp = RE_PCT.search(zone)
            if mp:
                return "up" if RE_PCT_UP.search(mp.group(0)) else "down"
        for zone in (near_after, near_before):
            if RE_DOWN_KW.search(zone):
                return "down"
            if RE_UP_KW.search(zone):
                return "up"
        # 原色极性：旧约定下 var(--bull)=绿=涨、var(--bear)=红=跌
        return "up" if orig_var == "bull" else "down"

    # 4) 其余按原色极性处理
    return "up" if orig_var == "bull" else "down"


# ------------------------------------------------------------------ CSS 改造
def patch_css(css):
    css0 = css
    notes = []

    # 1) 注入 / 校正 --up / --down
    if re.search(r"--up\s*:", css):
        css = re.sub(r"--up\s*:\s*#[0-9a-fA-F]{3,8}", "--up:%s" % UP_HEX, css)
        css = re.sub(r"--down\s*:\s*#[0-9a-fA-F]{3,8}", "--down:%s" % DOWN_HEX, css)
    else:
        m = re.search(r"(:root|body)\s*\{", css)
        if m:
            end = css.find("}", m.start())
            block = css[m.start():end]
            new = block
            for pat in (r"--bull-bg\s*:\s*[^;]+;", r"--bullbg\s*:\s*[^;]+;",
                        r"--bull\s*:\s*[^;]+;"):
                new2 = re.sub(pat, lambda mm: mm.group(0) + "--up:%s;--down:%s;" % (UP_HEX, DOWN_HEX),
                              new, count=1)
                if new2 != new:
                    new = new2
                    break
            if new != block:
                css = css[:m.start()] + new + css[end:]
                notes.append("注入 --up/--down")

    # 2) .up / .down 颜色规则
    css, n1 = re.subn(r"(\.up\s*\{[^}]*?)var\(--bull\)", r"\1var(--up)", css)
    css, n2 = re.subn(r"(\.down\s*\{[^}]*?)var\(--bear\)", r"\1var(--down)", css)
    if n1:
        notes.append(".up→--up x%d" % n1)
    if n2:
        notes.append(".down→--down x%d" % n2)

    # 3) .signal-up / .signal-down
    css, n3 = re.subn(r"(\.signal-up\s*\{[^}]*?)var\(--bull\)", r"\1var(--up)", css)
    css, n4 = re.subn(r"(\.signal-down\s*\{[^}]*?)var\(--bear\)", r"\1var(--down)", css)
    if n3:
        notes.append(".signal-up→--up x%d" % n3)
    if n4:
        notes.append(".signal-down→--down x%d" % n4)

    # 4) .sector.up / .sector.down 背景与标题色
    css, n5 = re.subn(
        r"\.sector\.up\s*\{\s*background:\s*#f0fdf4;\s*border-color:\s*#bbf7d0;\s*\}",
        ".sector.up { background:#fef2f2; border-color:#fecaca; }", css)
    css, n6 = re.subn(
        r"\.sector\.down\s*\{\s*background:\s*#fef2f2;\s*border-color:\s*#fecaca;\s*\}",
        ".sector.down { background:#f0fdf4; border-color:#bbf7d0; }", css)
    css, n7 = re.subn(r"(\.sector\.up\s+h4\s*\{[^}]*?)var\(--bull\)", r"\1var(--up)", css)
    css, n8 = re.subn(r"(\.sector\.down\s+h4\s*\{[^}]*?)var\(--bear\)", r"\1var(--down)", css)
    if n5 or n6:
        notes.append(".sector 背景对调 x%d/%d" % (n5, n6))
    if n7 or n8:
        notes.append(".sector h4 x%d/%d" % (n7, n8))

    # 5) .up / .down 作为边框色（_posts/2026-09-13）
    css, n9 = re.subn(r"(\.up\s*\{[^}]*?)var\(--bull\)", r"\1var(--up)", css)
    css, n10 = re.subn(r"(\.down\s*\{[^}]*?)var\(--bear\)", r"\1var(--down)", css)
    if n9:
        notes.append(".up 边框→--up x%d" % n9)
    if n10:
        notes.append(".down 边框→--down x%d" % n10)

    # 6) .stock-card .price 默认色
    css, n11 = re.subn(r"(\.stock-card\s+\.price\s*\{[^}]*?)var\(--bear\)", r"\1var(--down)", css)
    if n11:
        notes.append(".stock-card .price→--down x%d" % n11)

    # 7) 量能中性色类（放在最后，确保覆盖 .up/.down）
    if ".vol{" not in css:
        css = css.rstrip() + "\n  .vol{color:var(--neutral);font-weight:600}\n"
        notes.append("追加 .vol 中性色")

    return css, notes


# ------------------------------------------------------------------ 内联改造
TAG_RE = re.compile(r"<[^>]*>")
INLINE_RE = re.compile(r'style="([^"]*?)color:\s*var\(--(bull|bear)\)\s*;?([^"]*?)"')


def strip_tags(s):
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", s))


def patch_inline(html, rel=""):
    out, pos = [], 0
    stats = {"up": 0, "down": 0, "vol": 0, "keep": 0}
    details = []
    for m in INLINE_RE.finditer(html):
        out.append(html[pos:m.start()])
        pos = m.end()
        pre, var, post = m.group(1), m.group(2), m.group(3)
        tag_end = html.find(">", m.start())
        after = html[tag_end + 1:]
        nt = TAG_RE.search(after)
        text = (after[:nt.start()] if nt else after[:120]).strip()
        ctx = strip_tags(html[max(0, m.start() - 220):m.start()] + " " +
                         html[m.end():m.end() + 260])
        near_after = strip_tags(html[m.end():m.end() + 120])
        near_before = strip_tags(html[max(0, m.start() - 120):m.start()])
        kind = classify(text, ctx, near_after, near_before, var, rel)
        if kind == "up":
            newvar, stats["up"] = "--up", stats["up"] + 1
        elif kind == "down":
            newvar, stats["down"] = "--down", stats["down"] + 1
        elif kind == "vol":
            newvar, stats["vol"] = "--neutral", stats["vol"] + 1
        else:
            newvar, stats["keep"] = "--" + var, stats["keep"] + 1
        details.append((var, newvar, text[:60], kind))
        out.append('style="%scolor:var(%s)%s"' % (pre, newvar, post))
    out.append(html[pos:])
    return "".join(out), stats, details


# ------------------------------------------------------------------ 量能类改造
CLS_RE = re.compile(r'class="([^"]*\b(?:up|down)\b[^"]*)"')
VOL_TEXT_RE = re.compile(r"^(?:[\d,\.]+|\{[^}]+\})\s*亿$")
VOL_WORD_RE = re.compile(r"放量|缩量")
VOL_PCT_RE = re.compile(r"同时点[^%]{0,14}[+−\-][\d.]+%|成交额[^%]{0,14}[+−\-][\d.]+%")


def patch_vol_classes(html):
    """把 .up/.down 类里表示「成交额 / 放量 / 缩量」的条目改为 .vol 中性色。"""
    n = 0
    out, pos = [], 0
    for m in CLS_RE.finditer(html):
        cls = m.group(1)
        tag_end = html.find(">", m.end())
        after = html[tag_end + 1:]
        nt = TAG_RE.search(after)
        text = (after[:nt.start()] if nt else after[:80]).strip()
        if not (VOL_TEXT_RE.match(text) or VOL_WORD_RE.search(text)
                or VOL_PCT_RE.search(text)):
            continue
        newcls = " ".join(w for w in cls.split() if w not in ("up", "down"))
        newcls = (newcls + " vol").strip()
        out.append(html[pos:m.start()])
        out.append('class="%s"' % newcls)
        pos = m.end()
        n += 1
    out.append(html[pos:])
    return "".join(out), n


def patch_script(path, rel):
    """对生成脚本模板做同样的改造：CSS 块 + 内联色 + 逻辑表达式。"""
    src = open(path, encoding="utf-8").read()
    orig = src

    # 1) 只对 <style>…</style> 区间做 CSS 改造
    m = re.search(r"<style[^>]*>(.*?)</style>", src, re.S)
    if m:
        css, notes = patch_css(m.group(1))
        if css != m.group(1):
            src = src[:m.start(1)] + css + src[m.end(1):]

    # 2) 内联色
    src, stats, details = patch_inline(src, rel)

    # 3) 量能类（成交额 / 放量 / 缩量）→ .vol 中性色
    src, nvol = patch_vol_classes(src)

    # 4) 逻辑表达式（正数=涨=红，负数=跌=绿）
    src = src.replace('color = "var(--bull)" if v >= 0 else "var(--bear)"',
                      'color = "var(--up)" if v >= 0 else "var(--down)"')

    return src, stats, orig != src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正写盘")
    ap.add_argument("--dry-run", action="store_true", help="只报告不写盘（默认）")
    ap.add_argument("--files", nargs="*", help="只处理指定文件（相对仓库根）")
    ap.add_argument("--scripts-only", action="store_true", help="只处理生成脚本")
    args = ap.parse_args()

    files = [] if args.scripts_only else (args.files or ALL_FILES)
    if args.scripts_only:
        scripts = args.files or SCRIPTS
    elif args.files:
        scripts = [f for f in args.files if f.startswith("scripts/")]
    else:
        scripts = SCRIPTS

    total = {"up": 0, "down": 0, "vol": 0, "keep": 0}
    voltotal = 0
    changed = []
    for rel in files:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("!! 缺失:", rel)
            continue
        html = open(path, encoding="utf-8").read()
        orig = html

        m = re.search(r"<style[^>]*>(.*?)</style>", html, re.S)
        if m:
            css, notes = patch_css(m.group(1))
            if css != m.group(1):
                html = html[:m.start(1)] + css + html[m.end(1):]

        html, stats, details = patch_inline(html, rel)
        html, nvol = patch_vol_classes(html)
        voltotal += nvol

        for old, new in SPECIAL_FIXES.get(rel, []):
            if old in html:
                html = html.replace(old, new)
            else:
                print("   !! 手工修正未命中:", rel, old[:50])

        for k in total:
            total[k] += stats[k]

        if html != orig:
            changed.append(rel)
            if args.apply:
                open(path, "w", encoding="utf-8").write(html)
            print("改 %-52s 内联 上行%-3d 下行%-3d 中性%-3d 保留%-3d | 量能类 %d" %
                  (rel, stats["up"], stats["down"], stats["vol"], stats["keep"], nvol))
        else:
            print("跳过 %-50s (无变化)" % rel)

    for rel in scripts:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("!! 缺失:", rel)
            continue
        src, stats, diff = patch_script(path, rel)
        for k in total:
            total[k] += stats[k]
        if diff:
            changed.append(rel)
            if args.apply:
                open(path, "w", encoding="utf-8").write(src)
            print("改 %-52s 内联 上行%-3d 下行%-3d 中性%-3d 保留%-3d" %
                  (rel, stats["up"], stats["down"], stats["vol"], stats["keep"]))
        else:
            print("跳过 %-50s (无变化)" % rel)

    print("\n内联合计: 上行→红 %d, 下行→绿 %d, 量能→中性 %d, 保留 %d" %
          (total["up"], total["down"], total["vol"], total["keep"]))
    print("量能类改中性: %d 处" % voltotal)
    print("变更文件 %d 个%s" % (len(changed), "（已写盘）" if args.apply else "（dry-run，未写盘）"))


if __name__ == "__main__":
    main()
