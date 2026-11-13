#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点去 Jekyll 迁移（幂等，可重复运行）。

背景：仓库原来靠 Jekyll（`_config.yml` + `_layouts/default.html` + `_posts/`）构建，
GitHub Pages 每次 push 跑一次 Jekyll 构建。去掉 Jekyll 后靠仓库根目录的 `.nojekyll`
让 GitHub Pages 原样发布静态文件。

本脚本做四件事：

1. `_posts/*.html` → 仓库根目录静态文件
   - 文件名 = 原 permalink（`/duyiehua-report-20261112.html` → `duyiehua-report-20261112.html`）
   - 剥掉 YAML front matter
   - 图片路径 `../charts/` → `charts/`（从子目录移到根目录，相对路径要跟着改）
2. `index.html` → 纯静态（去 front matter、去 Liquid）
   - 68 张「🔥 最新 / 📅 往期 / 🧭 高级班」卡片原样保留
   - 底部分页列表改为写死的静态 HTML，并生成 `/2/` `/3/` `/4/` 归档页（URL 不破）
3. 落地 `assets/css/style.css`（原来由 Jekyll 从 jekyll-theme-cayman 编译）
4. 写 `.nojekyll`（空文件，告诉 GitHub Pages 不要跑 Jekyll）

用法：
    python3 scripts/migrate_off_jekyll.py

可选环境变量：
    THEME_CSS_SRC   主题 CSS 来源文件（默认 /tmp/live_style.css）
    RENDERED_MD     已渲染好的 markdown 页面来源（默认 /tmp/live_2018.html）
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
MANIFEST = ROOT / "scripts" / "site_posts.json"
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)

THEME_CSS_SRC = Path(os.environ.get("THEME_CSS_SRC", "/tmp/live_style.css"))
RENDERED_MD = Path(os.environ.get("RENDERED_MD", "/tmp/live_2018.html"))

PAGE_SIZE = 10
SITE_TITLE = "mnote"
# 2026-11-13：原副标题 “I tried to change the world, but I couldn't find the source code”
# （GitHub Pages 主题默认文案）已从 banner 删除；这里只留 meta description 用。
SITE_DESC = "wu2198 投资日报 · 都业华《高级班》收评纪要 · 投研报告归档"
PAGE_TITLE = "mnote · wu2198 投资日报"

# 同一日期内的排序：收评 → 午评 → 日报
KIND_ORDER = {"duyiehua-report": 0, "duyiehua-noon": 1, "wu2198": 2}


def parse_fm(text):
    """拆 YAML front matter，返回 (dict, 正文)。"""
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def kind_of(url):
    for k in KIND_ORDER:
        if k in url:
            return k
    return "wu2198"


def convert_posts():
    """_posts/*.html → 根目录静态文件。返回 post 清单。"""
    posts = []
    for f in sorted(POSTS_DIR.glob("*.html")):
        fm, body = parse_fm(f.read_text(encoding="utf-8"))
        url = fm.get("permalink") or f"/{f.stem}.html"
        title = fm.get("title") or f.stem
        date = f.name[:10]
        body = body.replace('src="../', 'src="')
        target = ROOT / url.lstrip("/")
        if target.exists():
            old = target.read_text(encoding="utf-8")
            if old.strip() == body.strip():
                print(f"  [skip] {target.name} 已存在且内容一致")
            else:
                print(f"  [warn] {target.name} 已存在但内容不同 —— 保留原文件，未覆盖")
        else:
            target.write_text(body, encoding="utf-8")
            print(f"  [ok]   {f.name} → {target.name}")
        posts.append({"date": date, "title": title, "url": url})
    return posts


def convert_md():
    """_posts/*.md → 根目录静态 HTML（用线上已渲染版本兜底）。"""
    out = []
    for f in sorted(POSTS_DIR.glob("*.md")):
        fm, _ = parse_fm(f.read_text(encoding="utf-8"))
        title = fm.get("title") or f.stem
        url = f"/{f.stem}.html"
        date = f.name[:10]
        if not RENDERED_MD.exists():
            print(f"  [skip] {f.name}：找不到已渲染版本 {RENDERED_MD}")
            continue
        target = ROOT / url.lstrip("/")
        target.write_text(RENDERED_MD.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  [ok]   {f.name} → {target.name}")
        out.append({"date": date, "title": title, "url": url})
    return out


def entry_html(posts):
    items = []
    for p in posts:
        items.append(
            '\t<li class="entry group">\n'
            '\t\t<div class="entry-title">\n'
            '\t\t\t<h2>\n'
            f'\t\t\t<a class="post-link" href="{p["url"]}">{p["title"]}</a>\n'
            '\t\t\t</h2>\n'
            '\t\t</div>\n'
            '\t</li>\n'
        )
    return "\n".join(items)


def pagination_html(page, total):
    # 第 2 页的「Prev」指回首页 /（不是 /1/）
    prev_href = "/" if page == 2 else f"/{page - 1}/"
    prev_link = (f'\t<a href="{prev_href}" class="previous">\n\t\tPrev\n\t</a>\n'
                 if page > 1 else '\t<span class="previous">Prev</span>\n')
    next_link = (f'\t<a href="/{page + 1}/" class="next">Next</a>\n'
                 if page < total else '\t<span class="next ">Next</span>\n')
    return ('<div class="pagination">\n'
            f'{prev_link}\t\n'
            '\t<span class="page_number ">\n'
            f'    {page} of {total}\n'
            '  </span>\n'
            f'\t\n{next_link}\t\n'
            '</div>\n')


def page_document(body, page, total, canonical, next_url=None, prev_url=None):
    head_extra = ""
    if next_url:
        head_extra += f'<link rel="next" href="https://mnote.github.io{next_url}" />\n'
    if prev_url:
        head_extra += f'<link rel="prev" href="https://mnote.github.io{prev_url}" />\n'
    doc_title = PAGE_TITLE if page == 1 else f"往期归档 · 第 {page} 页"
    # 2026-11-13：首页不再显示绿色大标题「mnote · wu2198 投资日报」（用户要求删掉），
    # <title> 保留。归档页仍保留自己的标题。
    post_header = "" if page == 1 else (
        '            <header class="post-header">\n'
        f'                <h1 class="post-title">往期归档 · 第 {page} 页</h1>\n'
        '            </header>\n'
    )
    return f"""<!DOCTYPE html>
<html lang="en_US">
  <head>

    <meta charset="UTF-8">

<title>{doc_title} | {SITE_TITLE}</title>
<meta name="description" content="{SITE_DESC}" />
<meta property="og:title" content="{doc_title}" />
<meta property="og:locale" content="en_US" />
<meta property="og:description" content="{SITE_DESC}" />
<link rel="canonical" href="https://mnote.github.io{canonical}" />
<meta property="og:url" content="https://mnote.github.io{canonical}" />
<meta property="og:site_name" content="{SITE_TITLE}" />
<meta property="og:type" content="website" />
{head_extra}<meta name="twitter:card" content="summary" />
<meta property="twitter:title" content="{doc_title}" />
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebSite","description":"{SITE_DESC}","headline":"{SITE_TITLE}","name":"{SITE_TITLE}","url":"https://mnote.github.io/"}}</script>


    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#157878">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="stylesheet" href="/assets/css/style.css">
  </head>
  <body>

    <header class="page-header" role="banner">
      <h1 class="project-name">{SITE_TITLE}</h1>
    </header>

    <main id="content" class="main-content" role="main">

        <article class="post">
{post_header}            <section>
{body}
            </section>
        </article>

    </main>
  </body>
</html>
"""


def build_index(posts):
    """index.html → 纯静态首页 + /2 /3 /4 归档页。"""
    idx_path = ROOT / "index.html"
    _, content = parse_fm(idx_path.read_text(encoding="utf-8"))
    start = content.index("<style>")
    end = content.index('<ul class="entries">')
    cards = content[start:end].rstrip() + "\n\n"

    posts = sorted(posts, key=lambda p: (p["date"], -KIND_ORDER.get(kind_of(p["url"]), 9)),
                   reverse=True)
    total_pages = max(1, (len(posts) + PAGE_SIZE - 1) // PAGE_SIZE)

    for page in range(1, total_pages + 1):
        chunk = posts[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]
        body = (cards if page == 1 else "") + \
            '<ul class="entries">\n' + entry_html(chunk) + '</ul>\n\n' + \
            '<article>\n' + pagination_html(page, total_pages) + '\n</article>\n'
        nxt = f"/{page + 1}/" if page < total_pages else None
        prv = "/" if page > 1 else None
        doc = page_document(body, page, total_pages,
                            "/" if page == 1 else f"/{page}/", nxt, prv)
        if page == 1:
            idx_path.write_text(doc, encoding="utf-8")
            print(f"  [ok]   index.html（{len(chunk)} 条 / 共 {total_pages} 页）")
        else:
            d = ROOT / str(page)
            d.mkdir(exist_ok=True)
            (d / "index.html").write_text(doc, encoding="utf-8")
            print(f"  [ok]   {page}/index.html（{len(chunk)} 条）")

    # 清掉多余的分页目录（条目变少后页数会缩，旧的 N/ 目录要删，否则留着死页）
    for d in ROOT.iterdir():
        if d.is_dir() and d.name.isdigit() and int(d.name) > total_pages:
            shutil.rmtree(d)
            print(f"  [rm]   {d.name}/ 超出总页数，已删")
    return total_pages


def drop_jekyll():
    """写 .nojekyll + 本地化主题 CSS。"""
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("  [ok]   .nojekyll")
    css_dst = ROOT / "assets" / "css" / "style.css"
    if css_dst.exists():
        print("  [skip] assets/css/style.css 已存在")
    elif THEME_CSS_SRC.exists():
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(THEME_CSS_SRC, css_dst)
        print(f"  [ok]   assets/css/style.css ← {THEME_CSS_SRC}（{css_dst.stat().st_size} bytes）")
    else:
        print(f"  [warn] 找不到主题 CSS：{THEME_CSS_SRC}")


def main():
    if POSTS_DIR.exists():
        print("[1] _posts/*.html → 根目录静态文件")
        posts = convert_posts()
        print("[2] _posts/*.md → 根目录静态 HTML")
        posts += convert_md()
        MANIFEST.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [ok]   清单写入 {MANIFEST.relative_to(ROOT)}")
    else:
        if not MANIFEST.exists():
            print(f"[ERR] {_posts} 已删除且没有清单 {MANIFEST.name}，无法重建首页 —— 停止")
            return 1
        posts = json.loads(MANIFEST.read_text(encoding="utf-8"))
        print(f"[1-2] _posts 已删除，改用清单 {MANIFEST.relative_to(ROOT)}（{len(posts)} 篇）")
    print("[3] index.html 静态化")
    build_index(posts)
    print("[4] .nojekyll + 主题 CSS")
    drop_jekyll()
    print(f"\n完成：{len(posts)} 篇报告已静态化")
    return 0


if __name__ == "__main__":
    sys.exit(main())
