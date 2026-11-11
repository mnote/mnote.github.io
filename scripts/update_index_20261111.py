"""在 mnote.github.io 首页插入 2026-11-11 wu2198 投资日报入口，
并把原「🔥 最新」(11-10) 标记降级为「📅 往期」。

⚠️ 必须在 front matter 之后插入！Jekyll 靠 front matter 识别页面并解析 Liquid；
   把新块拼到文件最前面会把 front matter 顶掉，首页分页直接失效
   （2026-09-25 踩过这个坑，2026-11-06 才修好）。
   本脚本插入位置在「🧭 高级班」卡之后、「📅 往期 11-10」卡之前，
   front matter 保持在文件最顶端不变。

⚠️ 首页卡片只保留链接标题，不放摘要与 meta-row（用户 2026-11-10 明确要求）。
"""
from pathlib import Path

INDEX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

TITLE = "wu2198 投资日报 - 2026-11-11（周三 主线切CPO存储，等反弹）"

NEW_BLOCK = (
    '<div class="featured"><h2><span class="badge">🔥 最新</span> '
    f'<a href="/2026-11-11-wu2198-investment-report.html">{TITLE}</a></h2></div>\n\n'
)

html = INDEX.read_text(encoding="utf-8")

if "2026-11-11-wu2198-investment-report.html" in html:
    print("[skip] 首页已存在 11-11 入口")
else:
    # ① 原「🔥 最新」卡（11-10）降级为「📅 往期」
    old_latest = (
        '<div class="featured"><h2><span class="badge">🔥 最新</span> '
        '<a href="/2026-11-10-wu2198-investment-report.html">'
    )
    if old_latest not in html:
        raise SystemExit("[ERR] 未找到预期的 11-10「🔥 最新」卡，请检查 index.html 结构")
    html = html.replace(
        old_latest,
        '<div class="featured"><h2><span class="badge">📅 往期</span> '
        '<a href="/2026-11-10-wu2198-investment-report.html">',
        1,
    )

    # ② 插入新卡 —— 锚定「📅 往期 11-10」卡的起始位置，不动 front matter
    anchor = ('</h2></div>\n\n<div class="featured"><h2><span class="badge">📅 往期</span> '
              '<a href="/2026-11-10-wu2198-investment-report.html">')
    if anchor not in html:
        raise SystemExit("[ERR] 未找到插入锚点，请检查 index.html 结构")
    html = html.replace(anchor, '</h2></div>\n\n' + NEW_BLOCK + anchor[12:], 1)

    INDEX.write_text(html, encoding="utf-8")
    print("[ok] 已插入 11-11 入口（11-10 降级为往期）")
