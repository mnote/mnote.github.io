"""把报告 HTML 里的相对图片路径内嵌成 base64 data URI，产出**单文件自包含版**。

用途：HTML 被下载/转发/存到别处后，相对路径 `charts/xxx.png` 会解析不到 → 全部裂图。
内嵌后无论在哪个目录、用什么方式打开都能正常显示图表。
共享样式表 `assets/css/report-table.css`（表格移动端适配）也一并内联。

用法：
    python3 make_standalone_report.py <报告.html> [-o 输出.html]
默认输出到 `~/workspace/mnote.github.io/_standalone/<原名>`（目录按需创建，不入库）。
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import inline_css

REPO = Path("/Users/maoling/workspace/mnote.github.io")
OUT_DIR = REPO / "_standalone"


def inline_images(html: str, base: Path) -> tuple[str, int, int]:
    """把 src="相对路径" 的 img 替换成 data URI。返回 (html, 内嵌数, 失败数)。"""
    refs = sorted(set(re.findall(r'src="(?!data:|https?:)([^"]+)"', html)))
    ok = fail = 0
    for rel in refs:
        f = base / rel
        if not f.exists():
            print(f"  [MISS] {rel}")
            fail += 1
            continue
        mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        data = base64.b64encode(f.read_bytes()).decode("ascii")
        html = html.replace(f'src="{rel}"', f'src="data:{mime};base64,{data}"')
        print(f"  [INLINE] {rel}  ({f.stat().st_size // 1024} KB)")
        ok += 1
    return html, ok, fail


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "html" / "wu2198-20261111.html"
    if not src.exists():
        print(f"[error] 找不到 {src}")
        sys.exit(1)

    out = None
    if "-o" in sys.argv:
        out = Path(sys.argv[sys.argv.index("-o") + 1])
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / src.name

    print(f"[src] {src}")
    html = src.read_text(encoding="utf-8")
    html, ok, fail = inline_images(html, src.parent)
    html = inline_css(html)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    kb = out.stat().st_size // 1024
    print(f"[out] {out}  ({kb} KB, 内嵌 {ok} 张, 失败 {fail} 张)")
    if fail:
        sys.exit(2)


if __name__ == "__main__":
    main()
