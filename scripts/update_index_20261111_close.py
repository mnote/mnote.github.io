"""更新 mnote.github.io 首页 2026-11-11 wu2198 卡片标题（盘中版 → 收盘版）。

⚠️ 只替换卡片标题字符串，不动 front matter、不动其他卡片。
   插卡规则见 AGENTS.md（锚定插入，绝不能拼到文件最前面）。
"""
from pathlib import Path

INDEX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

OLD_TITLE = "wu2198 投资日报 - 2026-11-11（周三 主线切CPO存储，等反弹）"
NEW_TITLE = "wu2198 投资日报 - 2026-11-11（周三 主线切CPO，等收复3706）"

html = INDEX.read_text(encoding="utf-8")

if NEW_TITLE in html:
    print("[skip] 首页标题已是收盘版")
elif OLD_TITLE in html:
    html = html.replace(OLD_TITLE, NEW_TITLE, 1)
    INDEX.write_text(html, encoding="utf-8")
    print("[ok] 首页 11-11 标题已更新为收盘版")
else:
    raise SystemExit("[ERR] 未找到预期的 11-11 卡片标题，请检查 index.html 结构")
