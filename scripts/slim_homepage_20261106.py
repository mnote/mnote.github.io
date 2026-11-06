"""首页瘦身：只保留标题链接，去掉摘要(<p>)与元信息(.meta-row)，标题小一号字。

背景（2026-11-06）：
  首页 57 张卡片每张都带几百字摘要 + 一整行元信息，首页没法扫读。
  本脚本把每张卡片压成「一行标题链接」，并把标题字号 18px → 16px。

实现要点：用 div 深度扫描定位每张 featured 卡的真实边界（正则会被卡片内的
<div class="meta-row"> 干扰），徽章并进 <h2> 以便同行显示。
只动 featured 区块（<ul class="entries"> 之前），分页列表不动。
"""
import re
from pathlib import Path

INDEX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

OLD_STYLE = """<style>
  .featured {
    background: linear-gradient(135deg, #eef4ff 0%, #fff7e0 100%);
    border: 1px solid #c7d8f7;
    border-left: 4px solid #1f6feb;
    border-radius: 8px;
    padding: 18px 22px;
    margin: 0 0 28px;
  }
  .featured .badge {
    display: inline-block; background: #1f6feb; color: #fff;
    padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
    margin-right: 8px; vertical-align: middle;
  }
  .featured h2 {
    margin: 6px 0; font-size: 18px; border: 0; padding: 0;
  }
  .featured h2 a { color: #1f6feb; text-decoration: none; }
  .featured h2 a:hover { text-decoration: underline; }
  .featured p { margin: 6px 0 0; color: #444; font-size: 14px; line-height: 1.6; }
  .featured .meta-row { color: #6e6e73; font-size: 12px; margin-top: 8px; }
</style>"""

NEW_STYLE = """<style>
  .featured {
    background: linear-gradient(135deg, #eef4ff 0%, #fff7e0 100%);
    border: 1px solid #c7d8f7;
    border-left: 4px solid #1f6feb;
    border-radius: 8px;
    padding: 7px 16px;
    margin: 0 0 5px;
  }
  .featured h2 {
    margin: 0; font-size: 16px; line-height: 1.5; border: 0; padding: 0;
  }
  .featured h2 .badge {
    display: inline-block; background: #1f6feb; color: #fff;
    padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600;
    margin-right: 8px; vertical-align: 2px;
  }
  .featured h2 a { color: #1f6feb; text-decoration: none; }
  .featured h2 a:hover { text-decoration: underline; }
</style>"""

P_RE = re.compile(r"[ \t]*<p>.*?</p>\s*", re.S)
META_RE = re.compile(r'[ \t]*<div class="meta-row">.*?</div>\s*', re.S)
BADGE_RE = re.compile(r'<span class="badge"[^>]*>(.*?)</span>', re.S)
H2_RE = re.compile(r"<h2([^>]*)>(.*?)</h2>", re.S)
DIV_OPEN_RE = re.compile(r"<div\b[^>]*>", re.I)
DIV_CLOSE_RE = re.compile(r"</div\s*>", re.I)


def find_card_end(s: str, start: int) -> int:
    """从 <div class="featured" 的起始位置起，找到其配对的 </div> 的结束下标。"""
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


def slim_card(inner: str) -> str:
    inner = P_RE.sub("", inner)
    inner = META_RE.sub("", inner)

    badge_html = ""
    bm = BADGE_RE.search(inner)
    if bm:
        label = bm.group(1).strip()
        # 「📅 往期」55 个完全相同，纯噪音 → 丢弃；「🔥 最新」「📚 词典 / 工具」保留
        if "往期" not in label:
            badge_html = f"{bm.group(0)} "   # 保留原 span（含内联样式）
        inner = inner[:bm.start()] + inner[bm.end():]

    def fix_h2(m):
        nonlocal badge_html
        attrs, body = m.group(1), m.group(2)
        attrs = attrs.replace("margin-top:14px", "margin-top:6px")
        # 徽章只在卡片的第一条标题前出现一次（词典卡有 3 条标题）
        pre, badge_html = badge_html, ""
        return f"<h2{attrs}>{pre}{body}</h2>"

    inner = H2_RE.sub(fix_h2, inner)
    inner = re.sub(r"\n\s*\n+", "\n", inner)
    return inner.strip()


def main():
    h = INDEX.read_text(encoding="utf-8")

    assert OLD_STYLE in h, "style block 未匹配，脚本需更新"
    h = h.replace(OLD_STYLE, NEW_STYLE)

    marker = '<ul class="entries">'
    assert marker in h, "未找到 entries 列表"
    head, tail = h.split(marker, 1)

    out, pos, n = [], 0, 0
    while True:
        m = re.search(r'<div class="featured"', head[pos:])
        if not m:
            out.append(head[pos:])
            break
        s = pos + m.start()
        out.append(head[pos:s])
        end = find_card_end(head, s)
        whole = head[s:end]
        open_tag = whole[:whole.index(">") + 1]
        inner = whole[len(open_tag):whole.rindex("</div>")]
        out.append(open_tag + slim_card(inner) + "</div>")
        n += 1
        pos = end

    head = "".join(out)
    print(f"[ok] 处理 featured 卡片 {n} 块")
    print(f"[ok] featured 区剩余 <p>: {head.count('<p>')}  剩余 meta-row: {head.count('meta-row')}")

    h = head + marker + tail
    INDEX.write_text(h, encoding="utf-8")
    print(f"[ok] index.html 已更新 ({len(h)} bytes)")


if __name__ == "__main__":
    main()
