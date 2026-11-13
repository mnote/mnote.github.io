"""首页加 11/12 日报卡（原「🔥 最新」降级为「📅 往期」）。

锚定插入：绝不把新块拼到文件最前面（front matter 必须在最顶端）。
用法： ~/czsc/.venv/bin/python scripts/update_index_20261112.py
"""
from pathlib import Path

IDX = Path("/Users/maoling/workspace/mnote.github.io/index.html")

NEW_CARD = ('<div class="featured"><h2><span class="badge">🔥 最新</span> '
            '<a href="/2026-11-12-wu2198-investment-report.html">'
            'wu2198 投资日报 - 2026-11-12（周四 GPU逆势，双门槛未收复）</a></h2></div>\n\n')

OLD_CARD = ('<div class="featured"><h2><span class="badge">🔥 最新</span> '
            '<a href="/2026-11-11-wu2198-investment-report.html">'
            'wu2198 投资日报 - 2026-11-11（周三 主线切CPO，等收复3706）</a></h2></div>')

OLD_TO_HISTORY = OLD_CARD.replace('<span class="badge">🔥 最新</span>',
                                  '<span class="badge">📅 往期</span>')

if __name__ == "__main__":
    s = IDX.read_text(encoding="utf-8")
    assert s.lstrip().startswith("<!DOCTYPE html>"), "index.html 不是静态首页，停止"
    if "2026-11-12-wu2198-investment-report.html" in s:
        print("[skip] 首页已有 11/12 卡片")
    else:
        assert OLD_CARD in s, "找不到 11/11 的「🔥 最新」卡片锚点"
        s = s.replace(OLD_CARD, NEW_CARD + OLD_TO_HISTORY, 1)
        IDX.write_text(s, encoding="utf-8")
        print("[ok] 首页已插入 11/12 卡片，11/11 降级为「📅 往期」")

    # 校验
    head = IDX.read_text(encoding="utf-8").splitlines()[:3]
    print("[首行]", head[0])
    body = IDX.read_text(encoding="utf-8")
    print("[卡片数]", body.count('class="featured"'))
    print("[Liquid 泄漏]", body.count("{%"))
