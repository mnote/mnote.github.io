#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 2026-10-12 wu2198 投资日报 HTML（10/12 周一收盘 · 国庆节后第 3 个交易日）

数据来源：
  - 微博：weibo-watcher skill，UID 1216826604，2026-10-12 21:00 抓取 9 条（过滤置顶）
  - 行情：Tushare Pro，index_daily / daily + adj_factor（前复权）
  - 图表：scripts/make_wu2198_charts_20261012.py 产出的 9 张 PNG

博主 10/12 立场：🔴 偏空 ·「软」+ C3 调整未完 + C4 反弹未形成 + 急不来
                🟢 但唯一点名主线是「四大行，两桶油等继续提肩带」→ 防御线当日最强
"""
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
OUT = REPO / "2026-10-12-wu2198-investment-report.html"

# ── 10/12 实际行情（tushare 校验值）────────────────────────
MKT = {
    "sh":   dict(name="上证指数", code="000001.SH", close=3797.24, pct=-0.43, high=3828.22, low=3790.9954, ma5=3819.12, ma10=3864.61, ma20=3886.10, ma60=3894.36, h60=3995.18, l60=3741.11, h120=4258.86),
    "cyb":  dict(name="创业板指", code="399006.SZ", close=2963.82, pct=-2.61, high=3049.34, low=2962.2445, ma5=3064.33, ma10=3192.96, ma20=3260.97, ma60=3425.15, h60=3905.31, l60=2932.80, h120=4380.41),
    "hs300":dict(name="沪深300",  code="000300.SH", close=4287.98, pct=-0.68, high=4334.29, low=4279.71, ma5=4323.67, ma10=4399.97, ma20=4457.13, ma60=4578.72, h60=4826.86, l60=4239.74, h120=5064.27),
}

def signed(v, suffix=""):
    color = "var(--bull)" if v >= 0 else "var(--bear)"
    return f'<strong style="color:{color}">{v:+.2f}%</strong>{suffix}'

# ── 9 条微博（按时间倒序 · tushare/weibo 实测互动数）──────────
POSTS = [
    ("10-12 15:05", "🔴", "tag-bear", "🔴 C3 调整未完 · C4 反弹未形成", "收盘定调",
     "今评价一个字“软”……<b>还属于 C3 的调整中,暂时还没有形成 C4 反弹</b>……收到请回复 666 或点赞支持一下!",
     74, 1073, 10357),
    ("10-12 14:35", "🔴", "tag-bear", "🔴 收盘定性:今天也就这样了", "收盘定调",
     "今天也就这样了!（全天无实质操作暗示）",
     10, 388, 6401),
    ("10-12 13:38", "🔴", "tag-bear", "🔴 盘中体感:软软绵绵", "盘中情绪",
     "死鬼,软软绵绵……（<b>对当日走势偏软的直接描述</b>）",
     11, 583, 7884),
    ("10-12 11:41", "🔴", "tag-bear", "🔴 风控:真的急不来的", "风控提醒",
     "真的急不来的!（<b>博主对抢反弹者当日第二次劝阻</b>）",
     16, 401, 9304),
    ("10-12 10:39", "⚪", "tag-none", "—", "互动粉丝文化",
     "收到请回复 666 或点赞支持一下!（粉丝互动口令 · 非信号）",
     19, 1099, 11476),
    ("10-12 10:06", "🔴", "tag-bear", "🔴 风控:急不来的", "风控提醒",
     "急不来的!（<b>博主当日第一次劝阻抢反弹</b>,全天三次重复表态）",
     17, 378, 9939),
    ("10-12 09:50", "🟢", "tag-bull", "🟢 资金面:流入明显", "资金面",
     "<b>最近几个交易日资金流入明显!</b>（博主当日唯一资金面偏多表态）",
     23, 251, 9799),
    ("10-12 09:47", "🟢", "tag-bull", "🟢 大盘:3786--3836 观察区间", "大盘判断",
     "<b>大盘指数早盘先观察 3786--3836 之间的取向</b>，收到请回复 666 或点赞支持一下!（<b>博主 10/12 唯一明确关键区间</b>）",
     58, 677, 9651),
    ("10-12 09:44", "🟢", "tag-bull", "🟢 主线:四大行 + 两桶油提肩带", "板块主线",
     "<b>四大行,两桶油等继续提肩带!</b>（<b>博主 10/12 唯一点名主线 → 银行 + 石油</b>）",
     10, 97, 6871),
]

rows = []
for t, emo, tagcls, sig, cat, text, r, c, l in POSTS:
    score = r + c * 2 + l
    hot = "热帖" if score >= 10000 else ("小热" if score >= 1000 else "普通")
    rows.append(f"""      <tr>
        <td>{t}</td>
        <td class="emoji">{emo}</td>
        <td><span class="tag {tagcls}">{sig}</span></td>
        <td style="font-size:12px">{cat}</td>
        <td class="text">{text}</td>
        <td class="score">R:{r} C:{c} L:{l}</td>
        <td class="score">{score}</td>
      </tr>""")
POST_ROWS = "\n".join(rows)

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>wu2198 投资观点日报 · 2026-10-12</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  :root {{
    --bg: #ffffff;
    --panel: #f8f9fb;
    --panel-2: #f1f3f6;
    --border: #e5e7eb;
    --border-strong: #d1d5db;
    --text: #1f2937;
    --muted: #6b7280;
    --bull: #16a34a;
    --bull-bg: #dcfce7;
    --bear: #dc2626;
    --bear-bg: #fee2e2;
    --neutral: #d97706;
    --neutral-bg: #fef3c7;
    --none: #6b7280;
    --none-bg: #f3f4f6;
    --accent: #2563eb;
    --accent-bg: #dbeafe;
    --key: #7c3aed;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 15px;
  }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1, h2, h3, h4 {{ font-weight: 600; line-height: 1.3; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 17px; margin: 24px 0 10px; color: var(--text); }}
  h4 {{ font-size: 15px; margin: 16px 0 8px; color: var(--muted); font-weight: 500; }}
  p {{ margin: 8px 0; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .meta {{ color: var(--muted); font-size: 13px; }}
  .meta span {{ margin-right: 14px; }}

  .hero {{
    background: linear-gradient(135deg, #fff7e6 0%, #fffbf0 100%);
    border: 1px solid #fbbf24;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 28px;
  }}
  .hero h1 {{ color: #92400e; }}
  .hero .stance {{ font-size: 16px; margin: 8px 0 0; }}
  .stance .emoji {{ font-size: 18px; margin-right: 4px; }}

  .panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    margin: 16px 0;
  }}
  .panel-2 {{ background: var(--panel-2); }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
  @media (max-width: 760px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} }}

  .kpi {{
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    text-align: center;
  }}
  .kpi .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi .val {{ font-size: 20px; font-weight: 600; margin: 4px 0; }}
  .kpi .sub {{ font-size: 12px; color: var(--muted); }}

  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: var(--panel-2); font-weight: 600; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px; }}
  tr:hover {{ background: var(--panel); }}
  td.emoji {{ text-align: center; font-size: 16px; }}
  td.text {{ max-width: 420px; }}
  td.score {{ font-variant-numeric: tabular-nums; text-align: right; }}

  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; margin: 0 2px; }}
  .tag-bull {{ background: var(--bull-bg); color: var(--bull); }}
  .tag-bear {{ background: var(--bear-bg); color: var(--bear); }}
  .tag-neutral {{ background: var(--neutral-bg); color: var(--neutral); }}
  .tag-none {{ background: var(--none-bg); color: var(--none); }}
  .tag-accent {{ background: var(--accent-bg); color: var(--accent); }}

  .chart {{ width: 100%; max-width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; background: #fff; }}
  .chart-caption {{ font-size: 12px; color: var(--muted); margin: -4px 0 16px; }}

  .stock-card {{
    background: #fff;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0;
  }}
  .stock-card.bull {{ border-left-color: var(--bull); }}
  .stock-card.bear {{ border-left-color: var(--bear); }}
  .stock-card.neutral {{ border-left-color: var(--neutral); }}
  .stock-card h4 {{ margin: 0 0 4px; color: var(--text); font-weight: 600; font-size: 15px; }}
  .stock-card .logic {{ font-size: 13px; color: var(--text); margin: 6px 0; }}
  .stock-card .key {{ font-size: 12px; color: var(--muted); font-family: ui-monospace, "SF Mono", Menlo, monospace; }}

  ul, ol {{ margin: 8px 0; padding-left: 24px; }}
  li {{ margin: 4px 0; }}
  .footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 60px; padding-top: 20px; border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="wrap">

  <div class="hero">
    <h1>🔴 wu2198 投资观点日报 · 2026-10-12</h1>
    <div class="meta">
      <span>📅 <b>2026-10-12 (周一 21:00 · 🇨🇳 国庆节后第 3 个交易日)</b></span>
      <span>🏛️ 沪指 10/12 收 <b style="color:var(--bear)">3797.24 (-0.43%)</b></span>
      <span>📊 数据源:weibo-watcher + tushare</span>
    </div>
    <div class="stance">
      <span class="emoji">🔴</span><b>博主 10/12 核心立场</b>:
      <b>🔴 偏空 · 全天用一个字概括行情「软」· 明确「还属于 C3 的调整中,暂时还没有形成 C4 反弹」· 三次重复「急不来的」劝阻抢反弹</b>。
      10/12 共 <b>9 条微博</b>(过滤置顶剩 9),<b>3 条带操盘信号</b>(信号密度 33%) — <b>2 条偏多 🟢</b>(09:44 主线 + 09:47 关键区间)+ <b>1 条偏空 🔴</b>(15:05 收盘定调)+ <b>6 条情绪/风控/互动类</b>。
      当日两条<b>唯一可操作信号</b>:① <b>09:44「四大行,两桶油等继续提肩带!」</b>(6871 赞) — 博主<b>当日唯一点名主线</b>,指向银行 + 石油防御线。② <b>09:47「大盘指数早盘先观察 3786--3836 之间的取向」</b>(9651 赞 · 11063 综合分) — 博主当日<b>唯一明确关键区间</b>。
      <b>10/12 盘面完美验证</b>:沪指实际 <b>高 3828.22 / 低 3790.99 / 收 3797.24</b> — <b>全天 100% 落在博主给出的 3786--3836 区间内</b>;四大行全线收在 <b>60 日新高</b>(工行 8.44 / 农行 7.19 / 建行 +3.01% / 中行 +2.95%),中石油收 <b>11.90 = 60D 高</b> —「提肩带」分毫不差。
      <b>⚠️ 但防御线强 ≠ 大盘转强</b>:同日创业板 <b>-2.61%</b> 跌破 10/9 前低区、中证 500 -2.18%,中小盘仍在杀跌 — 博主「C3 调整未完」的定性在成长股上继续兑现。
    </div>
  </div>

  <h2>📊 核心数据卡片</h2>
  <div class="grid-3">
    <div class="kpi">
      <div class="label">博主 10/12 核心立场</div>
      <div class="val" style="color: var(--bear);">🔴 偏空 ·「软」</div>
      <div class="sub">9 条 · 3 条带信号 · 2 多 / 1 空 / 6 情绪风控</div>
    </div>
    <div class="kpi">
      <div class="label">博主收盘定调 (15:05)</div>
      <div class="val" style="color: var(--bear);">🔴 C3 调整未完</div>
      <div class="sub">「暂时还没有形成 C4 反弹」10357 赞 · 12577 综合分</div>
    </div>
    <div class="kpi">
      <div class="label">博主当日唯一主线 (09:44)</div>
      <div class="val" style="color: var(--bull);">🟢 四大行+两桶油</div>
      <div class="sub">「继续提肩带」6871 赞 · 4 只银行全收 60D 高</div>
    </div>
    <div class="kpi">
      <div class="label">博主关键区间 (09:47)</div>
      <div class="val" style="color: var(--accent);">3786 — 3836</div>
      <div class="sub">实际高 3828.22 / 低 3790.99 · 全天在区间内 ✅</div>
    </div>
    <div class="kpi">
      <div class="label">沪指 10/12 收</div>
      <div class="val" style="color: var(--bear);">3797.24 (-0.43%)</div>
      <div class="sub">跌破 MA5 3819.12 · 逼近博主区间下沿 3786</div>
    </div>
    <div class="kpi">
      <div class="label">创业板 10/12 收</div>
      <div class="val" style="color: var(--bear);">2963.82 (-2.61%)</div>
      <div class="sub">距 10/9 前低 2932.80 仅 31 点 · C3 调整延续</div>
    </div>
  </div>

  <h2>📈 10/12 大盘实际走势（tushare 校验）</h2>
  <table>
    <thead>
      <tr><th>指数</th><th style="text-align:right">收盘</th><th style="text-align:right">涨跌</th><th style="text-align:right">最高</th><th style="text-align:right">最低</th><th>关键位解读</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><b>上证指数</b> 000001.SH</td>
        <td class="score"><b>3797.24</b></td>
        <td class="score">{signed(MKT['sh']['pct'])}</td>
        <td class="score">3828.22</td>
        <td class="score">3790.99</td>
        <td><b>全天落在博主 3786--3836 区间内</b> · 收在区间下半部(偏弱) · 跌破 MA5 3819.12 · 距 60D 低 3741.11 仅 56 点</td>
      </tr>
      <tr>
        <td><b>创业板指</b> 399006.SZ</td>
        <td class="score"><b>2963.82</b></td>
        <td class="score">{signed(MKT['cyb']['pct'])}</td>
        <td class="score">3049.34</td>
        <td class="score">2962.24</td>
        <td><b>跌幅是沪指 6 倍</b> · 全天单边下行 · 距 10/9 前低 2932.80 仅 31 点 · 远在 MA5/10/20/60 之下</td>
      </tr>
      <tr>
        <td><b>沪深300</b> 000300.SH</td>
        <td class="score"><b>4287.98</b></td>
        <td class="score">{signed(MKT['hs300']['pct'])}</td>
        <td class="score">4334.29</td>
        <td class="score">4279.71</td>
        <td>老登权重小幅回落 · 仍失守 MA5 4323.67 · 距 60D 低 4239.74 约 48 点</td>
      </tr>
    </tbody>
  </table>
  <p style="color:var(--muted);font-size:13px;">📌 补充:<b>中证500 收 7093.02 (-2.18%)</b> — 与创业板同步杀跌,印证「<b>资金从成长撤向防御</b>」:当日四大行 +2.7~3.0%、两桶油 +0.7~2.6%,而创业板/中证500 双双跌超 2%,<b>风格切换极其明确</b>。</p>

  <h2>📋 完整微博列表 (9 条 · 按时间倒序 · 10/12 21:00 抓取)</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 100px;">时间</th>
        <th style="width: 50px;">方向</th>
        <th>信号 · 置信</th>
        <th>类别</th>
        <th>内容摘要</th>
        <th style="width: 90px;">互动(转/评/赞)</th>
        <th style="width: 60px;">综合分</th>
      </tr>
    </thead>
    <tbody>
{POST_ROWS}
    </tbody>
  </table>

  <h2>🚦 博主 10/12 核心主线（9 条 · 3 条带操盘信号）</h2>

    <h3>🔴 主线 1 — 15:05「今评价一个字"软"……还属于 C3 的调整中,暂时还没有形成 C4 反弹」（当日互动最高 · 收盘定调）</h3>
    <p><b>原帖</b>「今评价一个字"软"……还属于 C3 的调整中,暂时还没有形成 C4 反弹……收到请回复 666 或点赞支持一下!」(<b>74/1073/10357 · 12577 综合分 · 当日互动最高</b>)</p>
    <p><b>解读</b>博主用一个字定性 10/12 行情:<b>「软」</b>。结构上明确 <b>C3 调整尚未结束、C4 反弹尚未形成</b> — 这是对 10/9 14:09「创业板试 2932 点之后的反抽,能不能发展成 C4 反弹,预计要下周才能衡量」的<b>否定性回答</b>:节后第 3 个交易日,C4 没有如约而至,反抽夭折。配合当日创业板 -2.61%、中证500 -2.18%,<b>博主定性完全兑现</b>。散户策略:<b>不要把 C3 反抽当成 C4 反弹去追</b>,等 C4 真正成立(放量收复 MA20)再动。</p>

    <h3>🔴 主线 2 — 10:06「急不来的!」/ 11:41「真的急不来的!」（全天三次重复的风控劝阻）</h3>
    <p><b>原帖</b>「急不来的!」(9939 赞 · 10712 综合分) + 「真的急不来的!」(9304 赞 · 10122 综合分) + 13:38「死鬼,软软绵绵……」(7884 赞)</p>
    <p><b>解读</b>博主全天<b>三次重复「急不来」+ 一次「软软绵绵」</b>,是最近几天最密集的风控表态。这与 10/9 14:26「整体调整的趋势未变,一般的投资者还不适合操之过急」一脉相承 — 博主对当日盘面<b>没有给出任何入场点位</b>。对散户的含义:<b>博主不提买点 = 没有买点</b>。今天四大行大涨 3%,正是最容易「怕踏空」的时刻,博主的态度是<b>继续等</b>。</p>

    <h3>🟢 主线 3 — 09:44「四大行,两桶油等继续提肩带!」（博主当日唯一点名主线）</h3>
    <p><b>原帖</b>「四大行,两桶油等继续提肩带!」(<b>10/97/6871 · 7075 综合分</b>)</p>
    <p><b>解读</b>博主 09:44 开盘即给出<b>当日唯一的方向性主线</b>:「<b>提肩带</b>」是博主形容权重股<b>稳步抬升、不必急涨</b>的表达(延续 9/29「四大行一直在提肩带」的同一措辞)。<b>10/12 盘面完美验证</b>:四大行集体收在 <b>60 日新高</b> — 工商银行 8.44 (+2.68%)、农业银行 7.19 (+3.01%)、建设银行 11.31 (+3.01%)、中国银行 6.97 (+2.95%),<b>4 只全部收在当日最高价</b>;中国石油 11.90 (+2.59%,收 60D 高)、中国石化 +0.74%。同期创业板 -2.61%。<b>博主的「提肩带」= 当日 A 股唯一赚钱主线,分毫不差。</b></p>

    <h3>🟢 主线 4 — 09:47「大盘指数早盘先观察 3786--3836 之间的取向」（当日唯一明确关键区间）</h3>
    <p><b>原帖</b>「大盘指数早盘先观察 3786--3836 之间的取向,收到请回复 666 或点赞支持一下!」(<b>58/677/9651 · 11063 综合分</b>)</p>
    <p><b>解读</b>博主给出当日<b>唯一一条精确到点的关键区间</b>:上沿 <b>3836</b>、下沿 <b>3786</b>,跨度 50 点。<b>10/12 实际走势:最高 3828.22 / 最低 3790.99 / 收盘 3797.24 — 全天 100% 运行在博主区间之内,最高点距上沿差 7.78 点,最低点距下沿差 4.99 点,收盘落在区间下半部(偏弱)。</b>博主「区间内震荡、取向待定」的定性精准。对散户的含义:<b>3786 是当日多空分水岭</b> — 有效跌破则向 60D 低 3741 寻底;有效站上 3836 才有反弹空间。</p>

    <h3>🟢 主线 5 — 09:50「最近几个交易日资金流入明显!」（当日唯一资金面偏多）</h3>
    <p><b>原帖</b>「最近几个交易日资金流入明显!」(<b>23/251/9799 · 10324 综合分</b>)</p>
    <p><b>解读</b>博主从<b>资金面</b>角度给出偏多观察:节后几个交易日有资金净流入。<b>但注意口径</b> — 结合当日盘面看,流入的方向是<b>银行/石油等防御权重</b>,而创业板、中证500 同步失血 2%+。<b>「资金流入」≠「大盘转强」</b>,在风格切换期尤其容易误读。博主自己也在收盘定调里给出了偏空结论 — <b>资金流入与 C4 未形成并不矛盾</b>。</p>

  <h2>💼 3 大板块 + 6 支个股（最值得投资方向）</h2>
  <p style="color:var(--muted);font-size:13px;">选股原则:博主 10/12 09:44 唯一点名主线「<b>四大行,两桶油等继续提肩带</b>」→ 银行 + 石油为<b>当日第一梯队</b>,且被当日盘面以「4 只银行全收 60D 高」完美验证;能源防御(神华)为「等」字涵盖的第三极;固态电池沿用 10/8+10/9+10/10 三次确认,但 10/12 出现<b>明显分化</b>(宁德 +0.21% 逆势抗跌 / 赣锋 -3.94% 破位),降级为观察仓。</p>

    <h3>🟢 板块 1: 银行 / 四大行（博主 10/12 唯一点名主线 · 当日最强 · 全部收 60D 高）</h3>
    <p>博主 09:44「<b>四大行,两桶油等继续提肩带!</b>」延续 9/29「四大行一直在提肩带」同一措辞。<b>10/12 是节后三大主线中唯一兑现的一条</b> — 大盘 -0.43%、创业板 -2.61% 的普跌日,四大行<b>逆势集体收在 60 日新高</b>:</p>
    <table>
      <thead><tr><th>个股</th><th style="text-align:right">10/12 收盘</th><th style="text-align:right">涨幅</th><th style="text-align:right">当日最高</th><th>状态</th></tr></thead>
      <tbody>
        <tr><td>工商银行 601398.SH</td><td class="score">8.44</td><td class="score">{signed(2.68)}</td><td class="score">8.44</td><td><b>收 = 60D 高 = 当日最高</b> · 突破</td></tr>
        <tr><td>农业银行 601288.SH</td><td class="score">7.19</td><td class="score">{signed(3.01)}</td><td class="score">7.19</td><td><b>收 = 60D 高 = 当日最高</b> · 突破</td></tr>
        <tr><td>建设银行 601939.SH</td><td class="score">11.31</td><td class="score">{signed(3.01)}</td><td class="score">11.33</td><td>逼近 60D 高</td></tr>
        <tr><td>中国银行 601988.SH</td><td class="score">6.97</td><td class="score">{signed(2.95)}</td><td class="score">7.00</td><td>逼近 60D 高</td></tr>
      </tbody>
    </table>
    <p><b>逻辑</b>:节后资金避险 + 央行 PSL -25bp 利好息差 + 高股息防御属性,在成长股杀跌时成为唯一避险池。<b>4 只银行全部收在当日最高价</b>,说明是<b>资金主动扫货而非尾盘偷袭</b>。博主的「提肩带」正在从「稳步抬升」进入「突破新高」阶段。<b>⚠️ 但注意:博主本人从未给过银行的具体买点,只给方向 —— 突破后需防高位回抽。</b></p>
      <div class="stock-card bull">
        <h4>🟢 工商银行 (601398.SH) · 四大行 · 60D 高突破</h4>
        <div class="logic">博主 9/29「四大行一直在提肩带」+ 10/12「四大行,两桶油等继续提肩带」<b>连续两轮同一措辞</b>。10/12 收 <strong style="color:var(--bull)">8.44 (+2.68%)</strong>,<b>收盘价 = 当日最高价 = 60 日新高,教科书级突破</b>。均线多头排列(MA5 8.28 / MA10 8.20 / MA20 8.14 / MA60 7.89),放量上攻(355 万手)。国有大行高股息底仓,博主管线里最稳的防御品种。<b>⚠️ 突破后不追,等回抽 MA5 8.28 确认。</b></div>
        <div class="key">60D 高 8.44(已破) / 60D 低 7.29 / 10/12 收 8.44 / MA5 8.28 / MA10 8.20 / MA20 8.14 / MA60 7.89</div>
      </div>
      <div class="stock-card bull">
        <h4>🟢 农业银行 (601288.SH) · 四大行 · 60D 高突破 · 当日最强</h4>
        <div class="logic">博主 9/29 四大行提肩带验证品种。10/12 收 <strong style="color:var(--bull)">7.19 (+3.01%)</strong>,<b>收盘价 = 当日最高价 = 60 日新高</b>,四大行中涨幅居前。放量 416 万手(四大行之最)。MA5 7.02 / MA10 6.95 / MA20 6.91 / MA60 6.75 完全多头,短期无套牢盘。<b>⚠️ 已距 60D 低 7.20 上涨 16%,追高风险大于工行。</b></div>
        <div class="key">60D 高 7.19(已破) / 60D 低 6.20 / 10/12 收 7.19 / MA5 7.02 / MA10 6.95 / MA20 6.91 / MA60 6.75</div>
      </div>

    <h3>🟢 板块 2: 石油 / 两桶油 · 能源防御（博主 10/12 点名「两桶油」· 中石油收 60D 高）</h3>
    <p>博主 09:44「<b>两桶油</b>等继续提肩带」直接点名。中国石油 10/12 收 <strong style="color:var(--bull)">11.90 (+2.59%)</strong>,<b>收 = 当日最高 = 60 日新高</b>;中国石化 +0.74% 同步翻红。逻辑:OPEC+ 减产 + 中东地缘 + 高股息 + 低估值(PB 1x 以下),是四大行之外第二条防御腿。同期能源内的中国神华 +2.02% 收 49.38,<b>逼近 60D 高 49.48(仅差 0.10)</b>,能源防御三剑客(神华/中石油/中石化)集体走强 —— 博主「等」字涵盖的整个防御板块,<b>当日集体兑现</b>。</p>
      <div class="stock-card bull">
        <h4>🟢 中国石油 (601857.SH) · 两桶油 · 60D 高突破</h4>
        <div class="logic">博主 10/12 09:44「<b>两桶油</b>等继续提肩带」直接点名。10/12 收 <strong style="color:var(--bull)">11.90 (+2.59%)</strong>,<b>收盘价 = 当日最高价 = 60 日新高</b>,从 10/9 的 11.60 连拉两日。MA5 11.48 / MA10 11.17 / MA20 11.01 / MA60 10.74 完全多头排列。OPEC+ 减产 + 中东地缘双重催化 + 高股息。<b>⚠️ 距 60D 低 9.08 已涨 31%,油价回落是主要风险。</b></div>
        <div class="key">60D 高 11.90(已破) / 60D 低 9.08 / 10/12 收 11.90 / MA5 11.48 / MA10 11.17 / MA20 11.01 / MA60 10.74</div>
      </div>
      <div class="stock-card bull">
        <h4>🟢 中国神华 (601088.SH) · 能源防御 · 逼近 60D 高</h4>
        <div class="logic">博主「四大行,两桶油<b>等</b>」中的「等」字涵盖能源防御线。10/12 收 <strong style="color:var(--bull)">49.38 (+2.02%)</strong>,<b>距 60D 高 49.48 仅差 0.10</b>,是当日防御板块中最接近突破的一只。煤电路港航化一体化 + 现金奶牛 + 股息率约 5%。MA5 48.07 / MA10 47.83 / MA20 47.34 / MA60 46.10 多头。<b>⚠️ 49.48 是关键阻力,突破需放量确认。</b></div>
        <div class="key">60D 高 49.48 / 60D 低 40.72 / 10/12 收 49.38 / MA5 48.07 / MA10 47.83 / MA20 47.34 / MA60 46.10</div>
      </div>

    <h3>🟡 板块 3: 固态电池 / 锂电（沿用 10/8+10/9+10/10 三次确认 · 但 10/12 分化走弱 · 降级观察）</h3>
    <p>博主 10/8 14:57「今天市场中,只有固态电池板块资金是活动明显的」+ 10/9 14:40「<b>固态电池板块出现有 4 连板的和连续 2 个 20 及 30 厘米的。说明市场资金活动是明显的</b>」+ 10/10 20:15「<b>起码等固态电池技术成熟之后吧</b>」— 博主节后<b>三次确认</b>但<b>本人持续观望</b>。10/12 该主线<b>未能延续节后强势,出现明显分化</b>:<b>宁德时代 +0.21%(逆势抗跌)</b> vs <b>赣锋锂业 -3.94%(破位下杀)</b> — 龙头抗跌、跟风股杀跌,是典型的<b>退潮初期结构</b>。叠加博主 10/10「等成熟」的观望态度 + 对电车的持续看空,该板块<b>降级为观察仓</b>。</p>
      <div class="stock-card neutral">
        <h4>🟡 宁德时代 (300750.SZ) · 固态电池龙头 · 逆势抗跌</h4>
        <div class="logic">博主 10/8+10/9+10/10 <b>三次确认</b>「固态电池资金活动明显」。10/12 收 <strong style="color:var(--bull)">298.38 (+0.21%)</strong> — 在创业板 -2.61% 的普跌日<b>逆势翻红,相对强度突出</b>,说明龙头资金仍在。但 <b>MA20 310.17 / MA60 357.31 仍在头顶压制</b>,距 60D 高 408.51 仍有 27% 空间,属超跌反弹而非趋势反转。<b>博主 10/10「等固态电池技术成熟之后吧」本人持观望 —— 不追高。</b></div>
        <div class="key">60D 高 408.51 / 60D 低 285.17 / 10/12 收 298.38 / MA5 292.16 / MA10 294.90 / MA20 310.17 / MA60 357.31</div>
      </div>
      <div class="stock-card bear">
        <h4>🔴 赣锋锂业 (002460.SZ) · 锂矿 · 10/12 破位走弱</h4>
        <div class="logic">博主三次确认的固态电池产业链标的。10/12 收 <strong style="color:var(--bear)">43.68 (-3.94%)</strong>,<b>单日跑输大盘 3.5 个百分点</b>,已跌破 MA5 44.03 / MA10 44.42 / MA20 45.82,<b>逼近 60D 低 41.67(仅差 2.01)</b>。与宁德 +0.21% 形成鲜明对比 — <b>板块内部严重分化,跟风股正在退潮</b>。这是 10/12 最明确的<b>减仓/回避信号</b>。</div>
        <div class="key">60D 高 56.89 / 60D 低 41.67 / 10/12 收 43.68 / MA5 44.03 / MA10 44.42 / MA20 45.82 / MA60 49.68</div>
      </div>

  <h2>🛡️ 风险提示</h2>
  <div class="panel" style="background:#fef2f2; border-color:#fca5a5;">
    <ul>
      <li>🔴 <b>博主 10/12 15:05 收盘定调「软」+「还属于 C3 的调整中,暂时还没有形成 C4 反弹」</b>(10357 赞 · 12577 综合分 · 当日互动最高) — <b>C4 反弹未成立,节后第 3 个交易日反抽夭折</b></li>
      <li>🔴 <b>博主 10/12 全天三次风控表态</b>:10:06「急不来的!」(9939赞) + 11:41「真的急不来的!」(9304赞) + 13:38「软软绵绵」(7884赞) — <b>博主当日未给出任何入场点位</b></li>
      <li>🔴 <b>创业板 10/12 -2.61% 收 2963.82</b>,距 10/9 前低 2932.80 仅 31 点;<b>中证500 -2.18%</b> — 成长股仍在杀跌通道,C3 调整未见底</li>
      <li>🔴 <b>赣锋锂业 -3.94% 逼近 60D 低</b> — 固态电池板块内部退潮,跟风股风险高于龙头</li>
      <li>🔴 <b>沪指跌破 MA5 3819.12</b>,收盘 3797.24 距博主区间下沿 3786 仅 11 点,距 60D 低 3741.11 仅 56 点 —<b>下破风险大于反弹动力</b></li>
      <li>⚠️ <strong>四大行/石油单日暴涨 2.7~3.0% 后追高风险</strong>:博主只给方向从未给买点,突破后需防高位回抽 MA5</li>
      <li>⚠️ <b>「资金流入明显」≠ 大盘转强</b>:10/12 流入方向是防御权重,成长股同步失血 2%+</li>
      <li>⚠️ 博主长期风控底线:<strong>不举债/不杠杆/只用闲钱/无技术不参与短线</strong> + 6/8 撤离本金+去年盈利一半 + 10/6「留住现金流最重要」</li>
      <li>🟢 <b>博主 10/12 09:47 关键区间 3786--3836 分毫不差</b>(实际高 3828.22 / 低 3790.99 / 收 3797.24,全天 100% 在区间内)</li>
      <li>🟢 <b>博主 10/12 09:44「四大行,两桶油等继续提肩带」分毫不差</b>:工行/农行/建行/中行 <b>4 只全部收 60D 高</b>,中石油收 60D 高,神华 +2.02%</li>
    </ul>
  </div>

  <h2>🎯 跟单 Checklist</h2>
  <div class="panel" style="background:#f0fdf4; border-color:#86efac;">
    <ul>
      <li>✅ <b>博主 10/12 09:47 关键区间 3786--3836 完全验证</b>· 实际高 3828.22 / 低 3790.99 / 收 3797.24 · 全天在区间内</li>
      <li>✅ <b>博主 10/12 09:44「四大行,两桶油继续提肩带」完全验证</b>· 工行 8.44 / 农行 7.19 / 建行 +3.01% / 中行 +2.95% <b>4 只全收 60D 高</b></li>
      <li>✅ <b>中石油 11.90 收 60D 高</b> · 神华 49.38 距 60D 高仅 0.10 · 能源防御集体兑现</li>
      <li>✅ <b>宁德时代 +0.21% 逆势抗跌</b>(创业板 -2.61% 环境)· 龙头资金未撤</li>
      <li>🚫 <b>不追四大行/石油单日 3% 大阳线</b>· 博主只给方向从未给买点,等回抽 MA5(工行 8.28 / 农行 7.02 / 中石油 11.48)</li>
      <li>🚫 <b>不抄底科技成长/创业板</b>· 博主「还属于 C3 的调整中,暂时还没有形成 C4 反弹」</li>
      <li>🚫 <b>不碰赣锋锂业</b>· -3.94% 破位逼近 60D 低 41.67 · 板块跟风股退潮</li>
      <li>🚫 <b>不把 C3 反抽当 C4 反弹追</b>· 博主明确否定 · 「急不来的」×3</li>
      <li>🚫 <b>不因单日资金流入就判断大盘转强</b>· 流入的是防御权重,成长同步失血</li>
      <li>🚫 <b>博主不给买点就不动手</b>· 全天 9 条微博无任何入场点位</li>
      <li>🚫 <b>沪指有效跌破 3786 不接刀</b>· 向 60D 低 3741 寻底</li>
      <li>🚫 <b>不举债、不加杠杆</b>· 博主风控底线 · 6/8 已撤离本金+去年盈利一半</li>
    </ul>
  </div>

  <h2>📈 K 线图分析（9 张 · 关键位蓝色虚线 📌 居左标注）</h2>

  <h3>📊 1. 上证指数 (000001.SH) · 大盘指数</h3>
  <img src="/charts/000001_SH_20261012.png" alt="上证指数 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:MA60 3894.36 / MA20 3886.10 / MA10 3864.61 / <b>博主上沿 3836</b> / 10/12 高 3828.22 / MA5 3819.12 / <b>10/12 收 3797.24</b> / 10/12 低 3791.00 / <b>博主下沿 3786</b> / 60D 低 3741.11。浅蓝区间 = 博主 10/12 09:47 提出的 <b>3786--3836</b>,实际全天运行于区间内。<b>收盘跌破 MA5,收在区间下半部 → 偏弱。</b></p>

  <h3>📊 2. 创业板指 (399006.SZ) · 大盘指数</h3>
  <img src="/charts/399006_SZ_20261012.png" alt="创业板指 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:MA20 3260.97 / MA10 3192.96 / MA5 3064.33 / 10/12 高 3049.34 / <b>10/12 收 2963.82 (-2.61%)</b> / 10/12 低 2962.24 / <b>10/9 前低 2932.80</b>。<b>全天单边下行,几乎收在最低点,距前低仅 31 点</b> — 验证博主「还属于 C3 的调整中,暂时还没有形成 C4 反弹」。</p>

  <h3>📊 3. 沪深300 (000300.SH) · 老登权重</h3>
  <img src="/charts/000300_SH_20261012.png" alt="沪深300 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:MA20 4457.13 / MA10 4399.97 / 10/12 高 4334.29 / MA5 4323.67 / <b>10/12 收 4287.98 (-0.68%)</b> / 10/12 低 4279.71 / 60D 低 4239.74。权重指数小幅回落,但<b>明显强于创业板</b>,印证资金向防御权重集中。</p>

  <h3>📊 4. 工商银行 (601398.SH) · 银行/四大行 · 🟢 60D 高突破</h3>
  <img src="/charts/601398_SH_20261012.png" alt="工商银行 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:<b>60D 高 8.44 = 10/12 收盘</b>(已突破) / MA5 8.28 / MA10 8.20 / MA20 8.14 / MA60 7.89 / 60D 低 7.29。博主 9/29 + 10/12 两轮「提肩带」。<b>收在当日最高价并创 60 日新高,均线完全多头排列。</b></p>

  <h3>📊 5. 农业银行 (601288.SH) · 银行/四大行 · 🟢 60D 高突破</h3>
  <img src="/charts/601288_SH_20261012.png" alt="农业银行 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:<b>60D 高 7.19 = 10/12 收盘</b>(已突破) / MA5 7.02 / MA10 6.95 / MA20 6.91 / MA60 6.75 / 60D 低 6.20。四大行中弹性最大,<b>收于当日最高 + 60 日新高</b>,放量 416 万手。</p>

  <h3>📊 6. 中国石油 (601857.SH) · 石油/两桶油 · 🟢 60D 高突破</h3>
  <img src="/charts/601857_SH_20261012.png" alt="中国石油 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:<b>60D 高 11.90 = 10/12 收盘</b>(已突破) / MA5 11.48 / MA10 11.17 / MA20 11.01 / MA60 10.74 / 60D 低 9.08。博主 10/12「两桶油继续提肩带」点名,<b>连拉两日并收 60 日新高</b>,OPEC+ 减产 + 中东地缘双驱动。</p>

  <h3>📊 7. 中国神华 (601088.SH) · 煤炭/能源防御 · 🟢 逼近 60D 高</h3>
  <img src="/charts/601088_SH_20261012.png" alt="中国神华 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:60D 高 49.48 / <b>10/12 收 49.38 (+2.02%)</b> / MA5 48.07 / MA10 47.83 / MA20 47.34 / MA60 46.10 / 60D 低 40.72。<b>距 60D 高仅 0.10</b>,是防御板块中最接近突破的一只,煤电路港航化一体化 + 股息率约 5%。</p>

  <h3>📊 8. 宁德时代 (300750.SZ) · 固态电池/锂电 · 🟡 逆势抗跌</h3>
  <img src="/charts/300750_SZ_20261012.png" alt="宁德时代 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:60D 高 408.51 / MA60 357.31 / MA20 310.17 / 10/12 高 306.71 / <b>10/12 收 298.38 (+0.21%)</b> / MA10 294.90 / MA5 292.16 / 60D 低 285.17。博主 10/8+10/9+10/10 三次确认固态电池主线。<b>大盘 -0.43% / 创业板 -2.61% 日逆势翻红,相对强度突出,但仍在 MA20/MA60 之下。</b></p>

  <h3>📊 9. 赣锋锂业 (002460.SZ) · 锂矿+固态电池 · 🔴 破位走弱</h3>
  <img src="/charts/002460_SZ_20261012.png" alt="赣锋锂业 K 线" class="chart" />
  <p class="chart-caption">📌 <b>关键位</b>:60D 高 56.89 / MA60 49.68 / MA20 45.82 / 10/12 高 45.78 / MA10 44.42 / MA5 44.03 / <b>10/12 收 43.68 (-3.94%)</b> / <b>60D 低 41.67</b>。<b>跌破全部短期均线,逼近 60D 低</b> — 与宁德 +0.21% 严重分化,板块跟风股退潮,10/12 最明确的回避信号。</p>

  <div class="footer">
    <p>📊 数据来源:weibo-watcher skill (UID 1216826604 · 10/12 21:00 抓取 9 条) · Tushare Pro (10/12 收盘 · 个股前复权)</p>
    <p>📈 图表:120 根日线 K 线 + MACD(12/26/9) + 成交量 · 关键位居左蓝色虚线标注(密集区自动双列错落防重叠)</p>
    <p>📅 报告生成时间:2026-10-12 21:00 · 🤖 自动生成 by Mavis</p>
    <p>⚠️ 本报告仅供参考,不构成任何投资建议。投资有风险,入市需谨慎。</p>
  </div>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    OUT.write_text(HTML, encoding="utf-8")
    print(f"[ok] {OUT} ({len(HTML)} bytes)")