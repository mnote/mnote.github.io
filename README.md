## mnote.github.io

个人静态站点：**投研报告归档**（wu2198 投资日报 / 都业华《高级班》收评纪要）+ 几个工具页（AI 编程词典、Claude Code Architect）。

### 站点结构（已去 Jekyll，2026-11-13）

仓库根目录**就是发布根目录**，GitHub Pages 通过根目录的 `.nojekyll` 原样发布静态文件，不再跑 Jekyll 构建。

```
index.html            首页（纯静态 HTML，无 front matter / 无 Liquid）
2/ 3/ 4/              往期归档分页（每页 10 条）
<日期>-<来源>-*.html   报告页，文件名即线上 URL
charts/               K 线图 PNG
reports/              数据留痕（CSV 等）
assets/css/style.css  站点样式（原本由 Jekyll 从 theme 编译，现已落地到仓库）
scripts/              报告生成与校验脚本
```

约定与发布流程见 `AGENTS.md`（本地文件，不发布）。

### 加一页报告

1. 生成 HTML 放**仓库根目录**，文件名即线上 URL，例如 `2026-11-13-wu2198-investment-report.html`
2. 图片用相对路径 `charts/xxx.png`
3. 首页插卡：

```bash
python3 scripts/update_index.py latest \
    --url /2026-11-13-wu2198-investment-report.html \
    --title "wu2198 投资日报 - 2026-11-13（周五 ……）"
```

4. 交付时另存一份单文件内嵌版（图片 base64）：

```bash
python3 scripts/make_standalone_report.py 2026-11-13-wu2198-investment-report.html
```

### 本地预览

```bash
python3 -m http.server 8765   # 然后开 http://127.0.0.1:8765/
```
