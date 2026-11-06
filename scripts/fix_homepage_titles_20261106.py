"""统一 mnote.github.io 首页 wu2198 报告链接标题格式：

    wu2198 投资日报 - yyyy-MM-dd（周x {精简两句，每句 ≤10 字}）

同时补回 index.html 丢失的 YAML front matter —— 2026-09-25 那次提交
把 `---\nlayout: default\n---` 抹掉了，导致 Jekyll 把它当静态文件、
Liquid 标签原样输出（`{% for post in paginator.posts %}` 直接显示在首页）。
"""
import re
from datetime import date
from pathlib import Path

INDEX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

WEEK = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}

# href → (日期, 两句精简摘要)
TITLES = {
 "/2026-11-05-wu2198-investment-report.html": ("2026-11-05", "方向对了幅度差了点", "隔夜纳指暴跌"),
 "/2026-11-04-wu2198-investment-report.html": ("2026-11-04", "点位方向双双全中", "双底成支撑"),
 "/2026-10-14-wu2198-investment-report.html": ("2026-10-14", "点位全中方向判反", "C4当日失败"),
 "/2026-10-13-wu2198-investment-report.html": ("2026-10-13", "立场翻转为中性偏多", "六点位全中"),
 "/2026-10-12-wu2198-investment-report.html": ("2026-10-12", "全天定调偏软", "C4反弹未形成"),
 "/2026-10-11-wu2198-investment-report.html": ("2026-10-11", "周末休市", "固态主线待确认"),
 "/2026-10-10-wu2198-investment-report.html": ("2026-10-10", "周末仅一条弱信号", "主线沿用"),
 "/2026-10-09-wu2198-investment-report.html": ("2026-10-09", "收盘预测分毫不差", "C4在酝酿"),
 "/2026-10-08-wu2198-investment-report.html": ("2026-10-08", "开门黑跌穿3800", "暂不参与"),
 "/2026-10-07-wu2198-investment-report.html": ("2026-10-07", "假期无新信号", "等节后开盘"),
 "/2026-10-06-wu2198-investment-report.html": ("2026-10-06", "空心光纤催化光通信", "留住现金流"),
 "/2026-10-04-wu2198-investment-report.html": ("2026-10-04", "假期休整无信号", "沿用纳指新高"),
 "/2026-10-03-wu2198-investment-report.html": ("2026-10-03", "美股纳指创新高", "硬科技领先"),
 "/2026-10-02-wu2198-investment-report.html": ("2026-10-02", "港股暴跌668点", "开盘承压预警"),
 "/2026-10-01-wu2198-investment-report.html": ("2026-10-01", "国庆休整无操盘帖", "沿用节前主线"),
 "/2026-09-30-wu2198-investment-report.html": ("2026-09-30", "老登股局部上涨", "节前清仓观望"),
 "/2026-09-29-wu2198-investment-report.html": ("2026-09-29", "3800关卡多方抵抗", "无操作空间"),
 "/2026-09-28-wu2198-investment-report.html": ("2026-09-28", "C杀进行时", "等C5完成再干"),
 "/2026-09-27-wu2198-investment-report.html": ("2026-09-27", "中秋休市无新帖", "沿用节前主线"),
 "/2026-09-26-wu2198-investment-report.html": ("2026-09-26", "中秋休整无新帖", "沿用节前主线"),
 "/2026-09-25-wu2198-investment-report.html": ("2026-09-25", "失守3886关键位", "中秋休整"),
 "/2026-09-13-wu2198-investment-report.html": ("2026-09-13", "跌破3915支撑", "周末无新观点"),
 "/wu2198-investment-report-20260912.html":   ("2026-09-12", "沪指试3852反抽", "区间偏防御"),
 "/wu2198-investment-report-20260905.html":   ("2026-09-05", "第四大浪调整未完", "多看少动"),
 "/wu2198-investment-report-20260904.html":   ("2026-09-04", "沪指试3915守住", "偏防御观望"),
 "/wu2198-investment-report-20260902.html":   ("2026-09-02", "失守3980", "多看少动等支撑"),
 "/wu2198-investment-report-20260901.html":   ("2026-09-01", "权重护盘偏强", "3996基本符合"),
 "/wu2198-investment-report-20260831.html":   ("2026-08-31", "权重护盘收复3986", "多于预期"),
 "/wu2198-investment-report-20260830.html":   ("2026-08-30", "区间震荡偏防御", "多看少动"),
 "/wu2198-investment-report-20260829.html":   ("2026-08-29", "区间震荡偏软", "多看少动"),
 "/wu2198-investment-report-20260828.html":   ("2026-08-28", "区间震荡偏软", "3900关口反复"),
 "/wu2198-investment-report-20260827.html":   ("2026-08-27", "增量反弹B反持续", "创业板同步"),
 "/wu2198-investment-report-20260826.html":   ("2026-08-26", "B反延续", "可操作空间不大"),
 "/wu2198-investment-report-20260824.html":   ("2026-08-24", "资金流出放量", "短期偏防御"),
 "/wu2198-investment-report-20260822.html":   ("2026-08-22", "六股全数收涨", "业绩兑现主线"),
 "/wu2198-investment-report-20260817.html":   ("2026-08-16", "B反结构未坏", "注意节奏仓位"),
 "/wu2198-investment-report-20260815.html":   ("2026-08-15", "站上3900关口", "中性偏谨慎"),
 "/wu2198-investment-report-20260814.html":   ("2026-08-14", "站上3900关口", "中性偏谨慎"),
 "/wu2198-investment-report-20260813.html":   ("2026-08-13", "放量转跌风险增大", "偏防御"),
 "/wu2198-investment-report-20260812.html":   ("2026-08-12", "B反未坏", "MLCC龙头涨八成"),
 "/wu2198-investment-report-20260811.html":   ("2026-08-11", "四浪调整未完", "紧贴支撑位"),
 "/wu2198-investment-report-20260808.html":   ("2026-08-08", "看3956", "收复3590待确认"),
 "/wu2198-investment-report-20260810.html":   ("2026-08-10", "B反未变", "半导体设备领涨"),
 "/wu2198-investment-report-20260807.html":   ("2026-08-07", "收复3940", "生物制品获提示"),
 "/wu2198-investment-report-20260805.html":   ("2026-08-05", "B反继续", "电池成新重点"),
 "/wu2198-investment-report-20260804.html":   ("2026-08-04", "B反结构明朗", "算力光通信"),
 "/wu2198-investment-report-20260803.html":   ("2026-08-03", "半导体双驱动", "等收复3856"),
 "/wu2198-investment-report-20260731.html":   ("2026-07-31", "B浪如期兑现", "收手等C杀"),
 "/wu2198-investment-report-20260730.html":   ("2026-07-30", "A杀到位3158", "小仓搏B反"),
 "/wu2198-investment-report-20260729.html":   ("2026-07-29", "3786反击点成立", "盯3886"),
 "/wu2198-investment-report-20260727.html":   ("2026-07-27", "二次反击点成立", "盯3886"),
 "/wu2198-investment-report-20260725.html":   ("2026-07-25", "端侧存储封装三主线", "缩量震荡"),
 "/wu2198-investment-report-20260724.html":   ("2026-07-24", "等二次启动点", "半导体封装"),
 "/wu2198-investment-report-20260723.html":   ("2026-07-23", "缩量震荡", "三大主线看多"),
 "/wu2198-investment-report-20260722.html":   ("2026-07-22", "三针探底", "算力三主线"),
 "/wu2198-investment-report.html":             ("2026-07-21", "三针探底", "算力主线确立"),
}

FRONT_MATTER = "---\nlayout: default\ntitle: mnote · wu2198 投资日报\n---\n\n"


def weekday(d: str) -> str:
    y, m, dd = (int(x) for x in d.split("-"))
    return WEEK[date(y, m, dd).weekday()]


def main():
    h = INDEX.read_text(encoding="utf-8")

    # ── 1) 补回 front matter ────────────────────────────────────────────
    if h.lstrip().startswith("---"):
        print("[skip] front matter 已存在")
    else:
        h = FRONT_MATTER + h
        print("[ok] 已补回 front matter (layout: default)")

    # ── 2) 重写 wu2198 报告链接标题 ──────────────────────────────────────
    pat = re.compile(r'(<h2><a href=")([^"]+)(">)(.*?)(</a></h2>)', re.S)
    done, missed, other = 0, [], 0

    def repl(m):
        nonlocal done, other
        href = m.group(2)
        if href in TITLES:
            d, s1, s2 = TITLES[href]
            for s in (s1, s2):
                assert len(s) <= 10, f"{href} 句长 {len(s)} > 10: {s}"
            new = f"wu2198 投资日报 - {d}（{weekday(d)} {s1}，{s2}）"
            done += 1
            return f"{m.group(1)}{href}{m.group(3)}{new}{m.group(5)}"
        other += 1
        return m.group(0)

    h = pat.sub(repl, h)
    print(f"[ok] 重写标题 {done} 条；未改动的其它链接 {other} 条")
    if done != len(TITLES):
        missed = sorted(set(TITLES) - set(re.findall(r'<h2><a href="([^"]+)"', h)))
        print(f"[warn] 未匹配到 {len(TITLES) - done} 条:", missed)

    INDEX.write_text(h, encoding="utf-8")
    print(f"[ok] index.html 已更新 ({len(h)} bytes)")


if __name__ == "__main__":
    main()
