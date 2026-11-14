"""给报告页加「PC / 手机都友好」的表格适配。

做三件事（幂等，可重复跑）：
  1. <head> 里引入共享样式表 assets/css/report-table.css
  2. 每个 <table> 包进 <div class="twx"><div class="tw">…</div></div>
     —— .tw 是横向滚动容器，手机上不再把中文压成竖排单字
  3. </body> 前注入一段小 JS：表格确实溢出时才给外层加 .ov（显示「左右滑动」提示）

用法：
    python3 scripts/fix_mobile_tables.py            # 处理 html/ 下全部报告页
    python3 scripts/fix_mobile_tables.py --check    # 只看哪些页还没适配

生成脚本里也可直接复用：
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from fix_mobile_tables import patch_html
    out.write_text(patch_html(html), encoding="utf-8")
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HTML_DIR = REPO / "html"
CSS_REL = "../assets/css/report-table.css"
CSS_FILE = REPO / "assets/css/report-table.css"

LINK = f'<link rel="stylesheet" href="{CSS_REL}">'
JS = (
    '<script>(function(){var w=document.querySelectorAll(".tw");'
    'for(var i=0;i<w.length;i++){if(w[i].scrollWidth>w[i].clientWidth+2&&w[i].parentNode)'
    '{w[i].parentNode.classList.add("ov");}}})();</script>'
)

TABLE_RE = re.compile(r"<table(?:\s[^>]*)?>.*?</table>", re.S)
OPEN = '<div class="twx" data-tw="1"><div class="tw" data-tw="1">'
CLOSE = "</div><!--tw--></div>"


def wrap_tables(text: str) -> str:
    """把每个 table 包进滚动容器；已包过的先还原再重包，保证幂等。"""
    text = text.replace(OPEN, "").replace(CLOSE, "")

    def repl(m: re.Match) -> str:
        return f"{OPEN}{m.group(0)}{CLOSE}"

    return TABLE_RE.sub(repl, text)


def add_link(text: str) -> str:
    if "report-table.css" in text:
        return re.sub(
            r'<link rel="stylesheet" href="[^"]*report-table\.css">', LINK, text
        )
    return text.replace("</head>", f"{LINK}\n</head>", 1)


def add_js(text: str) -> str:
    if "twOverflowHint" in text:
        return text
    js = JS.replace("</script>", "/*twOverflowHint*/</script>", 1)
    return text.replace("</body>", f"{js}\n</body>", 1)


def patch_html(text: str) -> str:
    """一页 HTML → 加了表格适配的 HTML。"""
    return add_js(add_link(wrap_tables(text)))


def inline_css(html: str) -> str:
    """把外部 CSS 引用替换成 <style> 内联（单文件自包含版用）。"""
    css = CSS_FILE.read_text(encoding="utf-8")
    return re.sub(
        r'<link rel="stylesheet" href="[^"]*report-table\.css">',
        "<style>\n" + css + "\n</style>",
        html,
    )


def main() -> None:
    check_only = "--check" in sys.argv
    targets = sorted(HTML_DIR.glob("*.html"))
    if not targets:
        print("html/ 下没有报告页")
        return
    changed = []
    for f in targets:
        old = f.read_text(encoding="utf-8")
        new = patch_html(old)
        if new == old:
            print(f"  [skip] {f.name}")
            continue
        changed.append(f.name)
        if not check_only:
            f.write_text(new, encoding="utf-8")
        print(f"  [{'check' if check_only else 'patch'}] {f.name}")
    print(f"共 {len(changed)} / {len(targets)} 页需要适配")


if __name__ == "__main__":
    main()
