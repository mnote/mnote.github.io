"""首页两处调整（2026-11-06）：

1. 「📚 词典 / 工具」卡（3 个链接）从列表末尾移到最前面置顶。
2. 分页列表（<ul class="entries">）里每条上方的英文日期行（"Sep 25, 2026"）去掉，
   只保留与首页卡片同款格式的标题链接；并给 .entries 补样式，让它渲染成
   与 featured 卡一致的紧凑行（16px、无项目符号）。
"""
import re
from pathlib import Path

INDEX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

DIV_OPEN_RE = re.compile(r"<div\b[^>]*>", re.I)
DIV_CLOSE_RE = re.compile(r"</div\s*>", re.I)

OLD_ENTRIES = """<ul class="entries">
{% for post in paginator.posts %}
\t<li class="entry group">
\t\t<div class="entry-date">
\t\t\t<time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%b %-d, %Y" }}</time>
\t\t</div>
\t\t<div class="entry-title">
\t\t\t<h2>
\t\t\t<a class="post-link" href="{{ post.url }}">{{ post.title }}</a>
\t\t\t</h2>
\t\t</div>
\t</li>
{% endfor %}
</ul>"""

NEW_ENTRIES = """<ul class="entries">
{% for post in paginator.posts %}
\t<li class="entry group">
\t\t<div class="entry-title">
\t\t\t<h2>
\t\t\t<a class="post-link" href="{{ post.url }}">{{ post.title }}</a>
\t\t\t</h2>
\t\t</div>
\t</li>
{% endfor %}
</ul>"""

EXTRA_CSS = """  .entries {
    list-style: none; margin: 22px 0 0; padding: 0;
  }
  .entries .entry {
    margin: 0 0 5px; padding: 7px 16px;
    background: #fff; border: 1px solid #e5e7eb;
    border-left: 4px solid #1f6feb; border-radius: 8px;
  }
  .post .entries h2 {
    margin: 0; font-size: 16px; line-height: 1.5; border: 0; padding: 0;
  }
  .entries .post-link { color: #1f6feb; text-decoration: none; }
  .entries .post-link:hover { text-decoration: underline; }
</style>"""


def find_card_end(s: str, start: int) -> int:
    """从 <div class="featured" 起找配对的 </div> 结束下标。"""
    depth = 0
    i = start
    while i < len(s):
        mo = DIV_OPEN_RE.search(s, i)
        mc = DIV_CLOSE_RE.search(s, i)
        if mc is None:
            break
        if mo is not None and mo.start() < mc.start():
            depth += 1
            i = mo.end()
            continue
        depth -= 1
        if depth == 0:
            return mc.end()
        i = mc.end()
    raise ValueError("未找到配对的 </div>")


def main():
    h = INDEX.read_text(encoding="utf-8")

    # ── 1. 词典卡置顶 ────────────────────────────────────────────────
    anchor = h.find("词典 / 工具")
    assert anchor > 0, "未找到词典卡"
    card_start = h.rfind('<div class="featured"', 0, anchor)
    card_end = find_card_end(h, card_start)
    card = h[card_start:card_end]
    assert card.count("dictionary-of-ai-coding-zh") == 1 and card.count("dictionary-of-ai-coding-ddd") == 1 \
        and card.count("claude-code-architect") == 1, "词典卡内容异常"
    h = h[:card_start] + h[card_end:]
    h = h.lstrip("\n")  # 清掉删卡留下的空行

    # ── 1b. 把 <style> 块也移到最前（原本夹在卡片列表中段）────────────
    st_start = h.find("<style>")
    st_end = h.find("</style>", st_start)
    assert 0 <= st_start < st_end, "未找到 style 块"
    style_block = h[st_start:st_end + len("</style>")]
    h = h[:st_start] + h[st_end + len("</style>"):]
    h = re.sub(r"\n{3,}", "\n\n", h)

    # ── 1c. style 块之后 = 第一张卡片；词典卡插到它前面（真正置顶）────
    first_card = h.find('<div class="featured"')
    assert first_card > 0, "未找到第一张卡片"
    h = h[:first_card] + style_block + "\n\n" + card + "\n\n" + h[first_card:]
    print("[ok] style 块已移到顶部，词典卡已置顶（3 个链接）")

    # ── 2. entries 列表去掉英文日期行 ───────────────────────────────
    assert OLD_ENTRIES in h, "entries 模板未匹配，脚本需更新"
    h = h.replace(OLD_ENTRIES, NEW_ENTRIES)
    print("[ok] entries 列表已去掉英文日期行")

    # ── 3. entries 样式 ─────────────────────────────────────────────
    assert h.count("</style>") >= 1
    h = h.replace("</style>", EXTRA_CSS, 1)
    print("[ok] 已补 .entries 紧凑样式")

    INDEX.write_text(h, encoding="utf-8")
    print(f"[ok] index.html 已更新 ({len(h)} bytes)")


if __name__ == "__main__":
    main()
