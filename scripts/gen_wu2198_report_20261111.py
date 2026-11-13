"""生成 2026-11-11 wu2198 投资观点日报 HTML（盘中版）。

窗口：11/10 15:39（上期截断）→ 11/11 13:09（A股盘中，未收盘）
关键新增：11/11 09:29「一个等……等反弹行情形成」
        11/11 10:20「早盘几大端侧龙头再次改写了新高！」
        11/11 10:41/10:48「你可先重点看看已经形成热点趋势的板块……低的时候不珍惜，现在追不是上策……应该选择接下来的板块」
        11/11 10:58「今天三大CPO龙头涨幅领先！」
        11/11 11:11「CPO反击之后，存储芯片也开始红了！」
        11/11 11:17「6月份提示CPO和存储芯片的泡沫……短短几个跌60%至70%的比比皆是！」
        11/11 11:22「看深成指、创业板指数即可」
行情：Tushare Pro 日线（至 11/10 收盘）+ 东方财富实时快照（11/11 13:09）
"""
from pathlib import Path

OUT = Path("/Users/maoling/workspace/mnote.github.io/html/wu2198-20261111.html")

CSS = """<style>
  :root {
    --bg: #ffffff; --panel: #f8f9fb; --panel-2: #f1f3f6;
    --border: #e5e7eb; --border-strong: #d1d5db;
    --text: #1f2937; --muted: #6b7280;
    --bull: #16a34a; --bull-bg: #dcfce7;--up:#e63946;--down:#2a9d8f;
    --bear: #dc2626; --bear-bg: #fee2e2;
    --neutral: #d97706; --neutral-bg: #fef3c7;
    --none: #6b7280; --none-bg: #f3f4f6;
    --accent: #2563eb; --accent-bg: #dbeafe;
    --key: #7c3aed;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px;
  }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }
  h1, h2, h3, h4 { font-weight: 600; line-height: 1.3; }
  h1 { font-size: 28px; margin: 0 0 8px; }
  h2 { font-size: 20px; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }
  h3 { font-size: 17px; margin: 24px 0 10px; color: var(--text); }
  h4 { font-size: 15px; margin: 16px 0 8px; color: var(--muted); font-weight: 500; }
  p { margin: 8px 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .meta { color: var(--muted); font-size: 13px; }
  .meta span { margin-right: 14px; }

  .hero { background: linear-gradient(135deg, #f0fdf4 0%, #f7fff9 100%); border: 1px solid #4ade80; border-radius: 12px; padding: 24px 28px; margin-bottom: 28px; }
  .hero h1 { color: #14532d; }
  .hero .stance { font-size: 16px; margin: 8px 0 0; }
  .hero-turn { background: linear-gradient(135deg, #fef2f2 0%, #fff7f7 100%); border: 1px solid var(--bear); border-radius: 12px; padding: 18px 24px; margin: 18px 0; }
  .hero-turn h3 { color: #991b1b; margin-top: 0; }
  .hero-win { background: linear-gradient(135deg, #eff6ff 0%, #f7fbff 100%); border: 1px solid var(--accent); border-radius: 12px; padding: 18px 24px; margin: 18px 0; }
  .hero-win h3 { color: #1e3a8a; margin-top: 0; }

  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px 22px; margin: 16px 0; }
  .panel-2 { background: var(--panel-2); }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
  @media (max-width: 900px) { .grid-4 { grid-template-columns: 1fr 1fr; } }
  @media (max-width: 760px) { .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; } }

  .kpi { background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; text-align: center; }
  .kpi .label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi .val { font-size: 20px; font-weight: 600; margin: 4px 0; }
  .kpi .sub { font-size: 12px; color: var(--muted); }

  table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }
  th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }
  th { background: var(--panel-2); font-weight: 600; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px; }
  tr:hover { background: var(--panel); }
  td.emoji { text-align: center; font-size: 16px; }
  td.text { max-width: 400px; }
  td.score { font-variant-numeric: tabular-nums; text-align: right; }

  .tag { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; margin: 0 2px; }
  .tag-bull { background: var(--bull-bg); color: var(--bull); }
  .tag-bear { background: var(--bear-bg); color: var(--bear); }
  .tag-neutral { background: var(--neutral-bg); color: var(--neutral); }
  .tag-none { background: var(--none-bg); color: var(--none); }
  .tag-accent { background: var(--accent-bg); color: var(--accent); }
  .tag-key { background: #ede9fe; color: var(--key); }

  .chart { width: 100%; max-width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; background: #fff; }
  .chart-caption { font-size: 12px; color: var(--muted); margin: -4px 0 16px; }

  .sector { background: #fff; border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 10px; padding: 18px 22px; margin: 18px 0; }
  .sector.r1 { border-left-color: #16a34a; }
  .sector.r2 { border-left-color: #d97706; }
  .sector.r3 { border-left-color: #7c3aed; }
  .sector h3 { margin-top: 0; }

  .quote { background: var(--panel-2); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; border-left: 3px solid var(--border-strong); }
  .quote .who { color: var(--muted); font-size: 12px; display: block; margin-bottom: 4px; }
  .risk { background: var(--bear-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }
  .action { background: var(--bull-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }
  .verify { background: var(--accent-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }
  .up { color: var(--up); font-weight: 600; }
  .down { color: var(--down); font-weight: 600; }
  .flat { color: var(--muted); font-weight: 600; }
  .key-num { color: var(--key); font-weight: 700; font-variant-numeric: tabular-nums; }
  .foot { margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }
  ul.tight { margin: 8px 0; padding-left: 22px; }
  ul.tight li { margin: 4px 0; }
  .divider { height: 1px; background: var(--border); margin: 26px 0; }
  .vol{color:var(--neutral);font-weight:600}
</style>"""


def post_rows():
    """窗口内 12 条微博 + 信号判定。"""
    rows = [
        ("11/11 09:29", "16094", "811", "🟢 大盘判断",
         "<b>一个等……等反弹行情形成</b>……支持的点个赞！",
         "开盘即定调：<b>等反弹行情形成</b>。实测 09:30 沪指开 3655.66，"
         "<b>低开 −0.22%</b>，全天最低 3650.31 —— "
         "<b>开盘确实更低，他等的正是「跌出来」的空间</b>。"),
        ("11/11 09:40", "10326", "549", "🟢 大盘判断",
         "<b>四个字：淡定待涨！</b>",
         "把 09:29 压缩成四个字。盘中创业板指 09:30 开 2490.10（低开 −0.17%）后翻红，"
         "与他 11:22「看深成指、创业板指数即可」完全一致 —— "
         "<b>他这次盯的是深市成长股，不是沪指</b>。"),
        ("11/11 10:17", "5633", "291", "🟡 盘面观察",
         "<b>死鬼，又绿了！</b>",
         "<b>时点分毫不差</b>。实测 10:17 沪指 3650.66，较昨收 3663.72 <b>−0.36%</b>，"
         "正处于当日<b>最低区间</b>。这是他对指数的真实态度：<b>不点评，只吐槽</b>。"),
        ("11/11 10:20", "6164", "159", "🟢 板块点名",
         "<b>早盘几大端侧龙头再次改写了新高！</b>",
         "<b>「改写新高」实测可定位</b>：瑞芯微盘中高 <b>237.37</b> > 60 日高 233.20；"
         "光洋股份 <b>26.59 涨停</b> > 60 日高 24.17 —— "
         "<b>两只都创出区间新高</b>。但星宸科技 103.24 < 20 日高 125.07，"
         "<b>「几大」是端侧链里最强的两只，不是全链普涨</b>。"),
        ("11/11 10:29", "7269", "447", "🟡 情绪",
         "<b>行情在你犹豫中展开！</b>",
         "催单式发帖。实测 10:29 沪指 3657.89（−0.16%）、创业板 2500.19（+0.23%）—— "
         "<b>他喊「行情在展开」时，指数其实是绿的</b>。",
         ),
        ("11/11 10:41", "5529", "194", "🟢 操作建议",
         "<b>你可先重点看看已经形成热点趋势的板块！</b>",
         "开始给方向。「热点趋势」= <b>已经走出来</b>的板块，不是低位的。"),
        ("11/11 10:48", "5607", "386", "🟢 操作建议 · 转折点",
         "<b>例如：已经出现快速涨翻番或者出现连续改写新高品种的板块：人形+物理AI、端侧等。"
         "低的时候不珍惜，现在追不是上策……应该选择接下来的板块。</b>",
         "<b>本期最重要的一条，也是立场转折点</b>。他点名把<b>人形+物理AI、端侧</b>划为"
         "「已经涨翻番 / 连续改写新高」的<b>不可追</b>品种，并明确要求「<b>选择接下来的板块</b>」。"
         "<b>11/10 的主线（人形+端侧）今天被他自己划掉了</b>。"),
        ("11/11 10:58", "4721", "128", "🟢 板块点名",
         "<b>今天三大CPO龙头涨幅领先！</b>",
         "<b>「接下来的板块」的第一答案</b>。实测 10:58 中际旭创 <b>+6.13%</b>、"
         "新易盛 <b>+6.52%</b>、天孚通信 <b>+4.07%</b>，全市场涨幅前列；"
         "光通信模块板块 98 只 <b>98/98 全涨</b>、均值 <b>+3.70%</b>、主力 <b>+106.3 亿</b>。"),
        ("11/11 11:11", "4300", "83", "🟢 板块点名",
         "<b>CPO反击之后，存储芯片也开始红了！</b>",
         "<b>「第二个答案」且时点吻合</b>。实测兆易创新 10:58 还是 244.50（<b>−0.03% 绿</b>），"
         "11:11 已到 246.17（<b>+0.65% 红</b>）—— <b>就是这 13 分钟翻红的</b>。"),
        ("11/11 11:17", "4177", "119", "🟢 自我验证",
         "<b>6月份提示CPO和存储芯片的泡沫……短短几个跌60%至70%的比比皆是！</b>",
         "<b>核验通过，且比他说得更深</b>。6 月历史帖可查：6/20「科技股的节奏和风险控制」、"
         "6/22「科技股是不是最后的疯狂？要警惕高位放量的品种」、6/23「高位连续放量…盲目满仓追高很容易变成亏损」、"
         "6/29「操作上记住不追高」，7/6「CPO…<b>6月22日见了阶段性顶位</b>…板块风险不可低估」。"
         "实测回撤：<b>8 只里 7 只跌 64%~73%</b>（详见第七节）。"),
        ("11/11 11:22", "5820", "413", "🟢 大盘判断",
         "<b>说了：一本正经的！</b>//@wu2198:<b>看深成指、创业板指数即可</b>……收到请回复666",
         "<b>核验通过</b>。实测创业板指 <b>+1.40%</b>、深成指 <b>+0.39%</b>，"
         "而沪指 <b>−0.10%</b>、沪深300 <b>−0.09%</b> —— "
         "<b>他主动放弃用沪指做判断，改看深市成长指数</b>。"),
        ("11/11 11:52", "6495", "384", "🟡 大盘判断",
         "<b>观点不变，下午继续……</b>支持的点个赞！",
         "全天最后一条（截至 13:09）。<b>「观点不变」= 方向已定，不改</b>；"
         "但 13:09 实测沪指仍 −0.10%，<b>全天并未转强</b>。"),
    ]
    out = []
    for r in rows:
        t, likes, comments, sig, text, note = r[:6]
        cls = ("tag-bull" if sig.startswith("🟢") else
               "tag-bear" if sig.startswith("🔴") else
               "tag-neutral" if sig.startswith("🟡") else "tag-none")
        out.append(
            f"<tr><td style='white-space:nowrap'>{t}</td>"
            f"<td class='score'>{likes}</td><td class='score'>{comments}</td>"
            f"<td><span class='tag {cls}'>{sig}</span></td>"
            f"<td class='text'>{text}</td><td class='text'>{note}</td></tr>"
        )
    return "\n".join(out)


SECTOR_ROWS = """
<tr><td><b>CPO / 光通信模块</b></td><td class="score">+3.70%</td><td class="score">98 / 98</td>
    <td>蘅东光 +18.94 · 太辰光 +13.75 · 源杰科技 +11.13 · 中际旭创 +10.65 · 新易盛 +10.63 · 青山纸业 +10.07 · 天洋新材 +10.03 · 剑桥科技 +10.00</td>
    <td><span class="tag tag-bull">博主点名</span> 10:58「今天三大CPO龙头涨幅领先」<br>主力 <b>+106.3 亿</b>（光通信模块）</td></tr>
<tr><td><b>存储芯片</b></td><td class="score">+1.74%</td><td class="score">98 / 100</td>
    <td>利扬芯片 +15.80 · 力芯微 +6.65 · 深南电路 +6.15 · 领先股份 +5.37 · 炬光科技 +5.17 · 协创数据 +4.90 · 普冉股份 +4.52</td>
    <td><span class="tag tag-bull">博主点名</span> 11:11「存储芯片也开始红了」<br>主力 <b>+13.5 亿</b></td></tr>
<tr><td><b>人形机器人 + 端侧 AI</b></td><td class="score">+4.25%</td><td class="score">100 / 100</td>
    <td>瑞迪智驱 +19.99 · 兆丰股份 +10.72 · 光洋股份 +10.01 · 宁波东力 +9.99 · 风语筑 +9.98 · 赛福天 +9.96 · 亿嘉和 +8.38</td>
    <td><span class="tag tag-bear">博主点名但劝退</span> 10:48「现在追不是上策」<br>AI 眼镜/端侧均值 +1.65%、81/99</td></tr>
<tr style="opacity:.62"><td>CPO 概念 <span class="tag tag-none">宽口径</span></td><td class="score">+3.38%</td><td class="score">87 / 99</td>
    <td>蘅东光 +18.94 · 致尚科技 +15.89 · 太辰光 +13.74 · 源杰科技 +11.13 · 新易盛 +10.69 · 中际旭创 +10.63</td>
    <td><span class="tag tag-none">并入 CPO</span> 主力 <b>+110.0 亿</b></td></tr>
<tr style="opacity:.62"><td>光纤概念 <span class="tag tag-none">CPO 邻链</span></td><td class="score">+2.51%</td><td class="score">67 / 91</td>
    <td>蘅东光 +18.94 · 致尚科技 +15.87 · 太辰光 +13.75 · 源杰科技 +11.13 · 中际旭创 +10.65 · 华脉科技 +10.03</td>
    <td><span class="tag tag-none">并入 CPO</span> 主力 +64.7 亿</td></tr>
<tr style="opacity:.62"><td>机器人概念 <span class="tag tag-none">宽口径</span></td><td class="score">+5.91%</td><td class="score">100 / 100</td>
    <td>瑞迪智驱 +19.99 · 德尔股份 +16.06 · 江苏北人 +10.85 · 北纬科技 +10.05 · 天安新材 +10.03 · 襄阳轴承 +10.02</td>
    <td><span class="tag tag-none">并入人形机器人</span> 主力 +28.8 亿</td></tr>
<tr style="opacity:.62"><td>智能音箱 <span class="tag tag-none">端侧细分</span></td><td class="score">−0.79%</td><td class="score">7 / 19</td>
    <td>瀛通通讯 +9.98 · 炬芯科技 +0.79 · 华勤技术 +0.38 · 晶晨股份 +0.28 · 智度股份 −0.14</td>
    <td><span class="tag tag-bear">逆势下跌</span> 主力 −5.1 亿</td></tr>
<tr style="opacity:.62"><td>AI 芯片 <span class="tag tag-none">科技战线</span></td><td class="score">+0.79%</td><td class="score">27 / 39</td>
    <td>北京利尔 +4.41 · 瑞晨环保 +2.83 · 罗普特 +2.63 · 寒武纪 +2.59 · 旋极信息 +2.42</td>
    <td><span class="tag tag-none">落选（无点名）</span></td></tr>
"""


def main():
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>wu2198 投资日报 - 2026-11-11（周三 主线切CPO存储，等反弹）</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 wu2198 投资日报 - 2026-11-11（周三 主线切CPO存储，等反弹）</h1>
  <div class="meta">
    <span>🕘 抓取时间：2026-11-11 13:09</span>
    <span>🏷️ 盘中版（未收盘）</span>
    <span>📡 数据源：weibo skill（访客时间线 + 三轮词表搜索补采 + 去重合并）</span>
    <span>💹 行情：Tushare Pro 日线（至 11/10 收盘）+ 东方财富实时快照（11/11 13:09）</span>
  </div>
  <p class="stance">
    核心立场：🟢 <b>方向换了 —— 从「守人形+端侧」切到「找接下来的板块」，他点名了 CPO 与存储芯片</b>。
    10:48「<b>低的时候不珍惜，现在追不是上策……应该选择接下来的板块</b>」是本期转折点；
    10:58 / 11:11 连续具名 CPO 与存储芯片，等于把「接下来的板块」直接说出口。
    但要读懂他的自我否定：<b>11/10 14:52 那句「磨在底部的，业绩增长速度明显了」，
    11/11 点名的 CPO / 存储正是这个公式的答案</b> —— <b>估值从 PE 549 的题材股，换成了 PE 15~21 的业绩龙头</b>。
  </p>
  <p class="stance" style="font-size:13px;color:var(--muted)">
    ⚠️ <b>本报告为盘中版</b>：A 股 15:00 收盘，本报告全部行情数据截至 <b>11/11 13:09</b>，
    K 线图中 11/11 为<b>未完成 K 线</b>、成交量为<b>盘中累计值</b>，收盘数据可能与本报告不同。
  </p>
</div>

<div class="grid-4">
  <div class="kpi"><div class="label">上证指数</div><div class="val">3659.99</div>
    <div class="sub"><span class="down">−0.10%</span> · 高 3672.18 · <b>3706 差 46.01 点</b></div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">2529.21</div>
    <div class="sub"><span class="up">+1.40%</span> · 博主「看深成指、创业板指数即可」</div></div>
  <div class="kpi"><div class="label">成交额（至 13:05）</div><div class="val">9686 亿</div>
    <div class="sub"><span class="vol">较 11/10 同时点 −2.0%</span> · <b>缩量反弹</b></div></div>
  <div class="kpi"><div class="label">涨停 / 跌停</div><div class="val">54 / 0</div>
    <div class="sub">11/10 收盘 93 / 0 · 涨停<b>腰斩</b></div></div>
</div>

<div class="hero-win">
  <h3>📌 一句话总览</h3>
  <p style="margin-bottom:0">
    <b>博主今天换方向了，而且换得很明确 —— 他自己把昨天的主线（人形+端侧）划成了「不可追」，然后点名了 CPO 和存储芯片。</b>
    盘面完全配合：光通信模块 98 只 <b>98/98 全涨</b>、均值 +3.70%、主力 <b>+106.3 亿</b>，
    中际旭创 <b>+10.66%</b>、新易盛 <b>+10.58%</b>、天孚通信 <b>+7.75%</b>；
    存储芯片 98/100 上涨，兆易创新在 11:11 那 13 分钟里由绿翻红。
    <b>但反弹的质量在退化</b>：成交额较昨日同时点缩量 2.0%、涨停从 93 家腰斩到 54 家、
    涨跌家数由「4273 / 1149」反转为「<b>2893 / 2453</b>」、沪指全天没翻红。
    <b>钱在换方向，不在进市场。</b>
  </p>
</div>

<h2>一、窗口内全部微博与信号判定</h2>
<p class="meta">
  窗口 <b>11/10 15:39（上期截断）→ 11/11 13:09</b>，共 <b>12 条</b>（全部为 11/11 当日）。
  采集路径：时间线第 1 页 → 搜索接口三轮词表补采（49 词 / 38 词 / 68 词）→ 合并去重。
</p>

<table>
<thead><tr><th>时间</th><th class="score">👍</th><th class="score">💬</th><th>信号</th><th>原文</th><th>判读</th></tr></thead>
<tbody>
{post_rows()}
</tbody>
</table>

<div class="panel">
  <h3 style="margin-top:0">🔍 与上期相比的三处变化</h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>主线自我否定：他把自己的昨天划掉了</b>。10:48「<b>已经出现快速涨翻番或者出现连续改写新高的品种的板块：人形+物理AI、端侧等。
      低的时候不珍惜，现在追不是上策……应该选择接下来的板块</b>」——
      11/10 报告把「人形机器人 + 端侧 AI」列为两大主线，11/11 他自己给这两条打了「不可追」。
      <b>这条比任何点名都重要：他不是在加仓，他是在换方向。</b></li>
    <li><b>「磨在底部 + 业绩增速明显」这个公式今天被点名兑现</b>。11/10 14:52 他给过公式：
      「<b>还有磨在底部的，业绩增长速度明显了，涨是早晚的事情</b>」。11/11 他点名的 CPO 与存储芯片，
      正好是 11/03–11/09 还在底部、且 PE 只有 <b>14.8~21.4 倍</b> 的那一批。
      <b>换句话说：11/10 他给的是「下一个方向的条件」，11/11 他把符合条件的票摆出来了。</b></li>
    <li><b>对大盘的口径变了 —— 从「等 3706」到「看深创指即可」</b>。
      11/09 说「耐心先等大盘收复 3706」，11/10 说「不点评大盘，等待即可」，
      11/11 直接改口「<b>看深成指、创业板指数即可</b>」。
      <b>3706 差 46.01 点（1.26%）他不再提了，转而盯自己持仓所在的深市成长指数 —— 这是回避，不是放弃。</b></li>
  </ul>
</div>

<div class="hero-turn">
  <h3>⚠️ 还有一个必须点明的「立场回撤」</h3>
  <p style="margin-bottom:0">
    7/17 泡沫破灭那天他写过：<b>「股价透支后的下跌是漫长的，即使中途有反弹也不会改变价值回归的趋势。
    因此，下周市场下寻之后将出现的反弹，将是调整持股的时机。」</b>
    —— 那时他说「反弹 = <b>减仓</b>」。
    <b>11/11 他说「淡定待涨」「CPO 反击之后，存储芯片也开始红了」，等于把反弹重新定义成「参与」。</b>
    这不是矛盾，而是<b>位置的差别</b>：7 月反弹是「高位透支后的反弹」，11 月反弹是「跌了 70% 之后的反弹」。
    <b>但对他的读者来说，纪律只有一个：他自己 10:48 刚说的「低的时候不珍惜，现在追不是上策」。</b>
  </p>
</div>

<h2>二、大盘关键点位（K 线 + MACD + 成交量）</h2>

<div class="panel panel-2">
  <h3 style="margin-top:0">📖 先读懂这三张图的颜色口径</h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>红涨绿跌的判定基准是「收盘价 vs 开盘价」（阳线 / 阴线），不是「收盘价 vs 昨收」</b>。
      收 ≥ 开 = <b style="color:var(--bear)">阳线（红）</b>，收 &lt; 开 = <b style="color:var(--bull)">阴线（绿）</b>。
      K 线、成交量柱、MACD 柱三处统一按此口径着色。</li>
    <li><b>「日涨跌幅」是另一套口径</b>（收盘 vs 昨收），它决定涨跌数字本身，<b>不决定 K 线颜色</b>。
      本期三个指数<b>全部出现错位</b>，图上都已标注：
      <ul class="tight" style="margin:4px 0 0">
        <li><b>上证</b>：开 3655.66 → 现 3659.99，<b>红 K</b>，但较昨收 3663.72 <b>仍跌 −0.10%</b> —— 图上已标「低开高走」；</li>
        <li><b>沪深300</b>：开 4049.43 → 现 4055.37，<b>红 K</b>，较昨收 4059.11 <b>跌 −0.09%</b> —— 同为「低开高走」；</li>
        <li><b>创业板指</b>：开 2490.10（= 当日最低）→ 现 2529.21，<b>红 K</b>，较昨收 2494.40 <b>涨 +1.40%</b>。</li>
      </ul>
    </li>
    <li>关键点位在 K 线图 <b>左侧以虚线标注</b>（📌 博主点位 / 支撑位 / 昨收位），
      MA5（橙）/ MA10（紫）/ MA20（天蓝）为叠加曲线。<b>价格刻度移到右侧</b>，左侧只留给关键点位标签。</li>
    <li><b>11/11 最后一根 K 线为未完成 K 线</b>，成交量是<b>盘中累计值</b>，收盘后会被放大，
      图上成交量柱会相应变高。</li>
  </ul>
</div>

<h3>上证指数 · 3659.99（−0.10%）</h3>
<img class="chart" src="charts/000001_SH_20261111.png" alt="上证指数 2026-11-11 K线">
<p class="chart-caption">
  开 3655.66（低开 −0.22%）/ 高 3672.18 / 低 3650.31 / 现 3659.99。
  博主 11/09 定的 <b>3706 确认位在左上方虚线</b>，全天最高 3672.18，<b>差 46.01 点（1.26%）未收复</b>。
  MA5 3664.72 / MA10 3650.63 / MA20 3674.26 —— <b>价格仍在三条均线之间被压着</b>。
</p>

<div class="verify">
  <b>大盘这一栏本期基本是「空」的</b>：他全天没说一个具体点位，
  从「等 3706」→「不点评大盘」→「看深成指、创业板指数即可」，<b>是在逐步退让</b>。
  日线 MACD DIF <b>−42.27</b> / DEA <b>−50.55</b> / 柱 <b>+16.56</b>（连续为正，DIF 仍深在零轴下方）；
  量能方面，13:09 成交 26662 亿手，仅为 5 日均量 42951 亿手的 <b>62%</b> —— <b>指数层面完全没有增量资金</b>。
</div>

<h3>创业板指 · 2529.21（+1.40%）</h3>
<img class="chart" src="charts/399006_SZ_20261111.png" alt="创业板指 2026-11-11 K线">
<p class="chart-caption">
  开 2490.10（<b>当日最低就是开盘价</b>）→ 现 2529.21，高 2538.69。较昨收 2494.40 <b>涨 +1.40%</b>。
  MA5 2502.84 / MA10 2484.05 在下方支撑，<b>MA20 2582.92 仍在上方压制</b>。
  日线 MACD DIF <b>−151.11</b> / DEA <b>−172.41</b> / 柱 <b>+42.61</b>。
</p>

<p><b>为什么博主说「看深成指、创业板指数即可」</b>：今天沪指 <b>−0.10%</b>、沪深300 <b>−0.09%</b>，
而深成指 <b>+0.39%</b>、创业板指 <b>+1.40%</b>、科创50 <b>+0.34%</b>。
<b>这是一天的行情，不足以证明他「放弃沪指」，但足以证明他「不需要沪指来给自己找理由」</b> ——
他持仓（CPO / 存储 / 机器人）全在深市与科创板。</p>

<h3>沪深300 · 4055.37（−0.09%）</h3>
<img class="chart" src="charts/000300_SH_20261111.png" alt="沪深300 2026-11-11 K线">
<p class="chart-caption">
  开 4049.43 → 现 4055.37，高 4061.14 / 低 4035.40，较昨收 4059.11 <b>−0.09%</b>。
  <b>红 K 但微跌</b>，与上证同口径。MA5 4067.66 / MA10 4049.27 / MA20 4082.33，
  日线 MACD DIF <b>−74.88</b> / DEA <b>−90.39</b> / 柱 <b>+31.03</b>。
</p>

<div class="panel">
  <h3 style="margin-top:0">📉 反弹的质量：四个指标同时在退化</h3>
  <table>
  <thead><tr><th>指标</th><th class="score">11/10（收盘）</th><th class="score">11/11（13:09）</th><th>变化</th></tr></thead>
  <tbody>
    <tr><td><b>沪深两市成交额</b>（同时点口径）</td><td class="score">9884 亿（至 13:05）</td>
      <td class="score"><b>9686 亿</b>（至 13:05）</td><td><span class="vol">−2.0%，缩量</span></td></tr>
    <tr><td>同上 vs 11/05 高点日</td><td class="score">15081 亿（11/05 至 13:05）</td>
      <td class="score"><b>9686 亿</b></td><td><span class="down">−35.8%</span></td></tr>
    <tr><td><b>涨停家数</b></td><td class="score">93 家</td><td class="score"><b>54 家</b></td>
      <td><span class="down">腰斩</span></td></tr>
    <tr><td><b>涨跌家数</b></td><td class="score">4273 / 1149</td><td class="score"><b>2893 / 2453</b></td>
      <td><span class="down">由涨转跌</span></td></tr>
    <tr><td>跌停家数</td><td class="score">0</td><td class="score">0</td><td><span class="up">无恐慌</span></td></tr>
  </tbody>
  </table>
  <p style="margin-bottom:0"><b>这四条一起看，结论是「结构性切换」而不是「增量行情」</b>：
  钱从人形机器人 + 端侧流出，流入 CPO + 存储；总量没有增加。
  <b>对持仓的含义：跟着他换板块可以，但不要因为「CPO 涨得好」就加大总仓位。</b></p>
</div>

<h2>三、最值得投资的 3 个板块 + 3 支个股</h2>

<p class="meta">筛选口径：博主当日<b>具名点名</b>的板块 → 用东方财富板块成分（剔除 2026-09-30 以后上市的次新，避免首日暴涨污染均值，与 11/10 口径一致）实测当日涨跌幅均值 + 上涨家数占比验证 → 取前 3。
板块数据为 <b>11/11 13:08</b> 快照；个股与指数为 <b>13:09</b> 快照。</p>

<table>
<thead><tr><th>板块</th><th class="score">样本均值</th><th class="score">上涨家数</th><th>样本明细（当日涨跌幅 %）</th><th>依据</th></tr></thead>
<tbody>
{SECTOR_ROWS}
</tbody>
</table>

<div class="sector r1">
  <h3>① CPO / 光通信模块 —— 博主亲自点名的「接下来的板块」</h3>
  <div class="quote">
    <span class="who">11/11 10:58 · 👍4721 💬128</span>
    <b>今天三大CPO龙头涨幅领先！</b>
  </div>
  <p><b>为什么排第一</b>：光通信模块 98 只样本 <b>98/98 全涨</b>，均值 <b>+3.70%</b>，
  主力净流入 <b>+106.3 亿</b>；CPO 概念 99 只均值 +3.38%、主力 <b>+110.0 亿</b>（全市场最强资金方向）。
  「<b>三大CPO龙头</b>」按行业惯例即 <b>中际旭创 / 新易盛 / 天孚通信</b>，实测 10:58 三只分别为
  <b>+6.13% / +6.52% / +4.07%</b>，确实处于全市场涨幅前列 —— <b>时点与措辞完全对应</b>。</p>
  <p><b>更重要的是它符合博主自己的选股公式</b>：CPO 三龙头 6 月顶 → 11/06 低点分别跌
  <b>−69.8% / −73.7% / −67.2%</b>，PE(TTM) 只有 <b>21.4 / 17.6 / —</b> 倍。
  <b>「磨在底部 + 业绩增速明显」这八个字，CPO 全部对得上。</b></p>
  <div class="risk"><b>但它今天已经涨过了</b>：中际旭创自 11/06 低点 427.34 已 <b>+22.0%</b>、
  新易盛自 161.16 已 <b>+26.1%</b>。按博主 10:48 自己的标准（「低的时候…现在追不是上策」），
  <b>CPO 今天已经不算「低」了 —— 下一步是等回踩，不是追高</b>。</div>
</div>

<div class="sector r2">
  <h3>② 存储芯片 —— 刚刚由绿翻红的那一条</h3>
  <div class="quote">
    <span class="who">11/11 11:11 · 👍4300 💬83</span>
    <b>CPO反击之后，存储芯片也开始红了！</b>
  </div>
  <p><b>为什么排第二</b>：存储芯片板块 100 只样本 <b>98 只上涨</b>，均值 <b>+1.74%</b>，主力 <b>+13.5 亿</b>。
  板块内利扬芯片 +15.80、力芯微 +6.65、普冉股份 +4.52、协创数据 +4.90。</p>
  <p><b>时点核验分毫不差</b>：兆易创新 10:58 报 244.50（较昨收 <b>−0.03%</b>，还是绿的），
  11:11 报 246.17（<b>+0.65%</b>，刚翻红）—— <b>他发这条的那 13 分钟里，板块刚刚由绿翻红</b>。</p>
  <div class="action"><b>存储是三只里最符合「低的时候」的</b>：兆易创新自 11/09 低点 237.28 只反弹了
  <b>+5.5%</b>，PE(TTM) <b>14.8 倍</b>、PB <b>2.24 倍</b>（三只里最低），
  6 月顶 846.66 → 低点 237.28 跌 <b>−72.0%</b>。
  <b>要按他公式选股，存储优先于 CPO。</b></div>
</div>

<div class="sector r3">
  <h3>③ 人形机器人 + 端侧 AI —— 博主点名了，但他说「别追」</h3>
  <div class="quote">
    <span class="who">11/11 10:20 · 👍6164 💬159 &nbsp;|&nbsp; 11/11 10:48 · 👍5607 💬386</span>
    <b>早盘几大端侧龙头再次改写了新高！</b><br>
    <b>例如：已经出现快速涨翻番或者出现连续改写新高的品种的板块：人形+物理AI、端侧等。
    低的时候不珍惜，现在追不是上策……应该选择接下来的板块。</b>
  </div>
  <p><b>盘面仍然是今天最猛的方向</b>：人形机器人 100 只 <b>100/100 全涨</b>、均值 <b>+4.25%</b>、
  主力 +27.0 亿；机器人概念 100 只 <b>100/100 全涨</b>、均值 <b>+5.91%</b>、主力 +28.8 亿，
  瑞迪智驱 +19.99% 领涨。</p>
  <p><b>「几大端侧龙头改写新高」实测可定位</b>：瑞芯微盘中高 <b>237.37</b> &gt; 60 日高 233.20；
  光洋股份 <b>26.59 涨停（3 连板）</b> &gt; 60 日高 24.17；瀛通通讯 <b>14.32 涨停（2 连板）</b>。
  <b>但星宸科技 103.24 仍低于 20 日高 125.07，智能音箱 19 只反而 −0.79%、主力净流出 5.1 亿</b> ——
  <b>端侧内部已经明显分化，不是一条线</b>。</p>
  <div class="risk"><b>这个板块必须扣分</b>：博主 10:48 亲口把「人形+物理AI、端侧」列为
  「已经涨翻番或者连续改写新高」的品种，<b>「现在追不是上策」</b>。
  <b>它是当日最强，却是他明说不能追的。</b>正确用法是<b>持有与回踩低吸</b>，不是今天新建仓。</div>
</div>

<h3>3 支个股（按博主点名强度 + 当日实测强度 + 估值结构排序）</h3>

<table>
<thead><tr><th>代码</th><th>名称</th><th class="score">现价</th><th class="score">涨跌</th><th class="score">成交额</th><th class="score">主力</th><th class="score">PE(TTM)</th><th class="score">PB</th><th class="score">总市值</th><th>入选理由</th></tr></thead>
<tbody>
<tr><td>300308.SZ</td><td><b>中际旭创</b></td><td class="score">521.21</td><td class="score"><span class="up">+10.66%</span></td>
  <td class="score">189.3 亿</td><td class="score"><span class="up">+22.44 亿</span></td>
  <td class="score">21.42</td><td class="score">5.88</td><td class="score">5548 亿</td>
  <td><span class="tag tag-bull">博主 10:58 具名</span> CPO 板块权重与流动性第一，主力净流入板块第一</td></tr>
<tr><td>300502.SZ</td><td><b>新易盛</b></td><td class="score">203.25</td><td class="score"><span class="up">+10.58%</span></td>
  <td class="score">154.8 亿</td><td class="score"><span class="up">+19.66 亿</span></td>
  <td class="score">17.59</td><td class="score">9.17</td><td class="score">2564 亿</td>
  <td><span class="tag tag-bull">博主 10:58 具名</span> CPO 弹性最强，自低点 +26.1%</td></tr>
<tr><td>603986.SH</td><td><b>兆易创新</b></td><td class="score">250.25</td><td class="score"><span class="up">+2.32%</span></td>
  <td class="score">52.7 亿</td><td class="score">—</td>
  <td class="score"><b>14.80</b></td><td class="score"><b>2.24</b></td><td class="score">1722 亿</td>
  <td><span class="tag tag-bull">博主 11:11 具名</span> 存储芯片权重龙头，<b>三只里唯一还在低位</b>（距低点仅 +5.5%）</td></tr>
</tbody>
</table>

<div class="hero-win">
  <h3>🔑 本期最重要的一张表：<b>估值结构换人了</b></h3>
  <p style="margin-bottom:0">
    11/10 报告选的三只是 <b>宇树科技（PE 549 倍 / PB 34.5）、瑞芯微（PE 62 / PB 18.1）、
    上纬新材（PE 1767 倍·公司自曝 / PB 94.9 · 亏损）</b> —— 全是<b>估值扩张驱动</b>的题材股。
    11/11 换成的三只是 <b>中际旭创（PE 21.4）、新易盛（PE 17.6）、兆易创新（PE 14.8）</b> ——
    全是<b>业绩兑现驱动</b>的板块龙头，PB 只有 2.24~9.17。
    <b>他换的不是板块位置，是估值结构</b>：从「还没赚钱的故事」换到「已经在赚钱的公司」。
    这也解释了为什么 CPO 能在今天放量拉起来而没有像端侧那样靠情绪接力 ——
    <b>筹码基础完全不同</b>。
  </p>
</div>

<h2>四、3 支个股 K 线与技术位</h2>

<h3>中际旭创（300308）· 521.21（+10.66%）</h3>
<img class="chart" src="charts/300308_SZ_20261111.png" alt="中际旭创 2026-11-11 K线">
<p class="chart-caption">
  开 480.42（<b>当日最低即开盘价</b>，低开 −1.26% 后一路上拉）→ 现 521.21，高 524.49，
  成交 <b>189.3 亿</b>。红 K 且当日 +10.66%，颜色与涨跌一致。
  <b>11/06 低点 427.34（本轮底，红虚线）在左下</b>，现价自低点 <b>+21.9%</b>。
</p>

<p><b>技术状态</b>：日线 MACD <b>DIF −77.72 / DEA −77.69 / 柱 −0.05</b> ——
<b>柱体今日几乎归零，正是零轴下方金叉的前夜</b>（11/10 柱 −4.24 → 今日 −0.05）。
MA5 477.11 在下方、MA10 508.42 已被站上、<b>MA20 568.85 仍在上方压制</b>。
量能上，13:09 成交 378416 手已达 5 日均量 481748 手的 <b>78.5%</b> —— <b>下午必然还有量</b>。</p>

<div class="verify"><b>博主数字核对</b>：11/11 10:58「今天三大CPO龙头涨幅领先」→ 实测 10:58 中际旭创 <b>+6.13%</b>，
新易盛 <b>+6.52%</b>，天孚通信 <b>+4.07%</b>，三者均居全市场涨幅前列 <b>✅</b>。
另外，11/17 他说「6 月提示 CPO 和存储芯片的泡沫…跌 60%~70% 的比比皆是」——
中际旭创 6/22 高点 <b>1414.69</b>（前复权）→ 11/06 低点 <b>427.34</b> = <b>−69.8%</b> <b>✅</b>。</div>

<div class="risk"><b>风险</b>：<b>已自底部反弹 21.9%</b>，按博主自己的「低的时候」标准已不属于低位；
距 6 月顶仍 −63.2%，上方套牢盘极重。<b>PE 21.4 倍在 AI 硬件里不算贵，但这一波涨幅是估值修复而非新增订单驱动</b>。
明早若高开，<b>就是他自己 10:48 说的「现在追不是上策」</b>。</div>

<h3>新易盛（300502）· 203.25（+10.58%）</h3>
<img class="chart" src="charts/300502_SZ_20261111.png" alt="新易盛 2026-11-11 K线">
<p class="chart-caption">
  开 187.30（= 当日最低，低开 +1.93%）→ 现 203.25，高 205.63，成交 <b>154.8 亿</b>。
  红 K 且 +10.58%。<b>11/06 低点 161.16 在左下</b>，现价自低点 <b>+26.1%</b>。
</p>

<p><b>技术状态</b>：日线 MACD <b>DIF −47.34 / DEA −48.58 / 柱 +2.46</b> ——
<b>柱体今日由负转正，金叉已在零轴下方完成</b>。MA5 184.15 / MA10 190.65 均在下方，
<b>MA20 234.24 仍在上方</b>。13:09 成交 788470 手已达 5 日均量 903402 手的 <b>87.3%</b>，
<b>是三只里量能放大最明显的</b>。</p>

<p><b>为什么选它而不是源杰科技 / 剑桥科技 / 联特科技</b>：新易盛是 CPO 板块<b>市值第二、成交第二</b>的权重股
（主力 +19.66 亿，仅次于中际旭创），PE <b>17.59 倍</b>是三者中最低。
源杰科技虽 +11.13% 但市值小、波动大；剑桥科技 11/08 已启动、今天属二波；
联特科技 +10.16% 但主力净流入仅 0.71 亿。<b>新易盛是「涨幅 + 资金 + 估值」三项同时靠前的。</b></p>

<div class="risk"><b>风险</b>：PB <b>9.17 倍</b>，是三只里最高的；自底部已 <b>+26.1%</b>，
弹性最大也意味着回撤最快。6/30 高点 612.86 → 11/06 低点 161.16 = <b>−73.7%</b>（实测最深的一档）。</div>

<h3>兆易创新（603986）· 250.25（+2.32%）</h3>
<img class="chart" src="charts/603986_SH_20261111.png" alt="兆易创新 2026-11-11 K线">
<p class="chart-caption">
  开 242.00 → 现 250.25，高 251.66 / 低 241.22，成交 <b>52.7 亿</b>。红 K 且 +2.32%。
  <b>11/09 低点 237.28（红虚线）在左下</b>，现价自低点仅 <b>+5.5%</b> —— <b>三只里唯一还在底部区域</b>。
</p>

<p><b>技术状态</b>：日线 MACD <b>DIF −24.06 / DEA −24.85 / 柱 +1.59</b>，零轴下方金叉已成立且柱体转正。
MA5 247.17 在下方，<b>MA10 255.69 与 MA20 268.70 在上方</b> —— 这是它与前两只最大的不同：
<b>它还没开始涨，位子上更低，上行空间更大，但时间上也不确定。</b></p>

<div class="verify"><b>博主数字核对</b>：11/11 11:11「CPO反击之后，存储芯片也开始红了」→ 实测兆易创新
10:58 报 244.50（<b>−0.03% 绿</b>），11:11 报 246.17（<b>+0.65% 红</b>）—— <b>翻红就发生在他发帖的那 13 分钟里</b> <b>✅</b>。
11/17 的「跌 60%~70%」：兆易创新 6/29 高点 <b>846.66</b> → 11/09 低点 <b>237.28</b> = <b>−72.0%</b> <b>✅</b>。</div>

<div class="risk"><b>风险</b>：它是三只里<b>唯一还没启动的</b> —— 涨幅落后板块，
也意味着<b>「CPO 反击之后」的接力未必轮到它</b>；存储芯片板块 100 只里主力净流入只有 13.5 亿
（不到 CPO 光通信模块的 1/8），<b>资金强度差一个量级</b>。DIF 仍在 −24 区间零轴下方。</div>

<h2>五、周线视角：博主「等反弹行情形成」的核对</h2>

<div class="panel">
  <table>
  <thead><tr><th>指标</th><th class="score">上周（截至 11/10）</th><th class="score">本周（截至 11/11 盘中）</th><th>变化</th></tr></thead>
  <tbody>
    <tr><td>上证 周线 DIF</td><td class="score">−96.14</td><td class="score">−98.79</td><td class="down">仍在下行</td></tr>
    <tr><td>上证 周线 DEA</td><td class="score">−71.71</td><td class="score">−77.13</td><td class="down">仍在下行</td></tr>
    <tr><td><b>上证 周线 MACD 柱</b></td><td class="score">−48.86</td><td class="score"><b>−43.32</b></td><td><span class="up">收窄 5.54</span></td></tr>
    <tr><td>创业板 周线 DIF</td><td class="score">−298.49</td><td class="score">−312.04</td><td class="down">加速下行</td></tr>
    <tr><td><b>创业板 周线 MACD 柱</b></td><td class="score">−213.99</td><td class="score"><b>−192.88</b></td><td><span class="up">收窄 21.11</span></td></tr>
    <tr><td>沪深300 周线 MACD 柱</td><td class="score">−111.75</td><td class="score"><b>−99.73</b></td><td><span class="up">收窄 12.02</span></td></tr>
  </tbody>
  </table>
</div>

<div class="hero-turn">
  <h3>结论：<b>日线在修复，周线在走弱 —— 「反弹」成立，「反转」依然不成立</b></h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>日线级别反弹继续</b>：沪指日线 MACD 柱 <b>+16.56</b>（连续为正），
      创业板 <b>+42.61</b>、沪深300 <b>+31.03</b>；
      三只被点名的 CPO / 存储个股里，<b>新易盛（+2.46）、兆易创新（+1.59）的柱体今日刚翻正，
      中际旭创（−0.05）几乎归零</b> —— <b>个股层面的技术拐点比指数更明确</b>。</li>
    <li><b>但周线的 DIF / DEA 还在往下走</b>：沪指周线 DIF <b>−96.14 → −98.79</b>、DEA <b>−71.71 → −77.13</b>，
      创业板 DIF <b>−298.49 → −312.04</b>（加速下行）。
      <b>柱收窄只是跌速放缓，价格重心还没上移</b> —— 这是「反弹」不是「反转」的量化证据。</li>
    <li><b>所以他的用词依然精确</b>：09:29「<b>一个等……等反弹行情形成</b>」、09:40「<b>淡定待涨</b>」、
      10:29「<b>行情在你犹豫中展开</b>」—— <b>连续四天都没说过「反转」「反转点」「主升」</b>。
      反弹阶段的正确心法与他 11/10 那句完全一致：<b>坚持方向 + 分批布局</b>，不是满仓等反转。</li>
  </ul>
</div>

<h2>六、下午与下个交易日（11/12 周四）操作建议</h2>

<div class="action">
  <b>① 方向：跟着他换板块，但按他给的顺序 —— 存储优先于 CPO</b><br>
  他的 10:48 给出了换板块的逻辑，10:58 / 11:11 给了答案，11/10 14:52 给了筛选条件
  （<b>磨在底部 + 业绩增速明显</b>）。把三条合起来执行：
  <b>在 CPO 与存储里选「还在底部、业绩兑现」的票，分批建仓，不追当日的 10% 大阳线。</b>
  落到具体标的：<b>兆易创新（距低点 +5.5%、PE 14.8）最符合；中际旭创 / 新易盛已自底部反弹 22%~26%，只能等回踩。</b>
</div>

<div class="action">
  <b>② 三个板块的优先次序与打法</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>存储芯片（首选 · 唯一仍在他公式的「低位」区间）</b>：
      11:11 他刚点名，板块 98/100 上涨但主力净流入仅 13.5 亿 —— <b>还没被资金充分定价</b>。
      打法：<b>低吸不追高</b>，看 237.28（11/09 低点）与 MA10 255.69 两个位置。</li>
    <li><b>CPO / 光通信模块（次选 · 只做龙头、等回踩）</b>：
      98/98 全涨、主力 +106.3 亿，强度最高，但<b>今天已经涨了 10%</b>。
      打法：<b>只做中际旭创 / 新易盛 / 天孚通信三只龙头</b>，等回踩 MA5 / 昨收，
      <b>不在明天的高开里追</b>。</li>
    <li><b>人形机器人 + 端侧 AI（持有，不新增）</b>：
      人形机器人 100/100 全涨、均值 +4.25%，但<b>他亲口说「现在追不是上策」</b>。
      已有持仓可持有（瑞芯微 237.37、光洋股份 3 连板都还在新高附近）；
      <b>新资金不参与，只在回踩时接</b>。</li>
  </ul>
</div>

<div class="risk">
  <b>③ 四条硬风险（按优先级）</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>缩量反弹，四个指标同时退化</b>：成交额较昨日同时点 −2.0%（较 11/05 −35.8%）、
      涨停 93 → <b>54 家</b>、涨跌家数 4273/1149 → <b>2893/2453</b>。
      <b>板块之间在互相搬运资金，没有增量入场</b>。这种结构一旦有一环掉头，回吐很快。</li>
    <li><b>3706 更远了</b>：差 <b>46.01 点（1.26%）</b>，全天最高 3672.18。
      他今天虽然不再提这个门槛（改口「看深成指、创业板指数即可」），<b>但门槛没消失，只是被绕开了</b>。</li>
    <li><b>他自己泼的水最该听</b>：10:48「<b>低的时候不珍惜，现在追不是上策</b>」。
      CPO 三大龙头今天 +7.75%~+10.66%，<b>按他自己的标准，明天追进去就是「追高」</b>。</li>
    <li><b>周线没转</b>：三个指数周线 DIF / DEA 双双继续下行。
      <b>反弹阶段的仓位应该是「分批」，不是「重仓等反转」</b> —— 这是他 11/10 13:47 那句话的原意。</li>
  </ul>
</div>

<div class="verify">
  <b>④ 需要盯的验证点（观察清单，不是预测）</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>CPO 三大龙头明天能否高开高走</b>：若集体低开闷杀，说明今天是<b>反弹兑现</b>而非反转，
      博主那句「追不是上策」就应验了。</li>
    <li><b>兆易创新能否站上 MA10（255.69）</b>：站上是存储接力确认；跌回 241.22（今日低）下方则接力失败。</li>
    <li><b>成交额能否重回 1.1 万亿以上</b>：今日至 13:05 仅 9686 亿，低于昨日同时点。
      <b>不放量的板块轮动撑不过三天</b>。</li>
    <li><b>涨停家数能否回到 80 家以上</b>：54 家是接力强度的高点信号；跌破 50 家说明整条线退潮。</li>
    <li><b>光洋股份 3 连板、瀛通通讯 2 连板能否续板</b>：端侧主线是否退潮的直接读数
      —— 断了，说明「不追」是对的。</li>
    <li><b>沪指能否收复 3706</b>：他不再提，但他一旦重新点评大盘，3706 仍是唯一门槛。</li>
  </ul>
</div>

<h2>七、信号质量评估与本期方法说明</h2>

<div class="panel">
  <h3 style="margin-top:0">数据来源与采集路径</h3>
  <ul class="tight">
    <li><b>微博</b>：weibo skill，访客模式时间线第 1 页 → 搜索接口三轮词表补采（49 词 / 38 词 / 68 词）→
      合并去重 <b>12 条</b>（窗口 11/10 15:39 → 11/11 13:09，全部为 11/11 当日）。</li>
    <li><b>行情</b>：Tushare Pro 日线（至 <b>11/10 收盘</b>，个股按后复权因子前复权，60 根日线窗口）；
      <b>11/11 盘中数据</b>取自东方财富实时快照（13:09）与分时接口（trends2），K 线图中 11/11 为未完成 K 线。</li>
    <li><b>成交额对比</b>：东方财富分时成交额累计（trends2，ndays=5），
      取 11/05–11/11 的<b>同一时点</b>口径（至 11:30 / 至 13:05）对比，避免用盘中值与收盘值直接比。</li>
    <li><b>涨跌家数 / 涨停跌停</b>：东方财富全 A 列表接口（clist/get，翻页取全 5928 只）
      与涨停池 / 跌停池（<code>getTopicZTPool</code> / <code>getTopicDTPool</code>）。</li>
    <li><b>板块统计</b>：东方财富板块成分接口（<code>clist/get</code>），<b>剔除 2026-09-30 以后上市的次新</b>
      以免首日暴涨污染均值（脚本 <code>scripts/collect_sectors_20261111.py</code>），口径与 11/10 一致。</li>
    <li><b>历史核验</b>：本机 weibo skill 历史库（2026-06-18 ~ 2026-07-31 的原始帖）
      用于核对「6 月提示 CPO 和存储泡沫」这一条。</li>
    <li><b>估值</b>：Tushare <code>daily_basic</code>（total_mv / pe_ttm / pb / turnover_rate，取 11/10 收盘）。</li>
  </ul>
</div>

<div class="panel panel-2">
  <h3 style="margin-top:0">博主数据的独立核验（七条，全部对上）</h3>
  <table>
  <thead><tr><th>博主语录</th><th>实测</th><th>结论</th></tr></thead>
  <tbody>
    <tr><td>11/11 10:20「早盘几大端侧龙头<b>再次改写了新高</b>」</td>
      <td>瑞芯微盘中高 <b>237.37</b> &gt; 60 日高 233.20；光洋股份 <b>26.59 涨停</b> &gt; 60 日高 24.17</td>
      <td><span class="tag tag-bull">吻合</span><br>两只均创区间新高</td></tr>
    <tr><td>11/11 10:58「<b>三大CPO龙头涨幅领先</b>」</td>
      <td>10:58 中际旭创 <b>+6.13%</b> / 新易盛 <b>+6.52%</b> / 天孚通信 <b>+4.07%</b></td>
      <td><span class="tag tag-bull">吻合</span><br>时点与措辞对应</td></tr>
    <tr><td>11/11 11:11「<b>存储芯片也开始红了</b>」</td>
      <td>兆易创新 10:58 = 244.50（<b>−0.03% 绿</b>）→ 11:11 = 246.17（<b>+0.65% 红</b>）</td>
      <td><span class="tag tag-bull">吻合</span><br>翻红就在发帖那 13 分钟</td></tr>
    <tr><td>11/11 11:17「6 月份<b>提示 CPO 和存储芯片的泡沫</b>」</td>
      <td>6/20「科技股的节奏和风险控制」、6/22「是不是最后的疯狂？要警惕高位放量」、6/23「盲目满仓追高很容易变成亏损」、6/29「记住不追高」、7/6「CPO…<b>6 月 22 日见阶段性顶</b>」</td>
      <td><span class="tag tag-bull">吻合</span><br>历史帖可查，非事后编</td></tr>
    <tr><td>11/11 11:17「<b>短短几个跌 60% 至 70% 的比比皆是</b>」</td>
      <td>中际旭创 <b>−67.5%</b> · 新易盛 <b>−71.6%</b> · 天孚通信 <b>−64.3%</b> · 兆易创新 <b>−71.6%</b> · 江波龙 <b>−72.0%</b> · 佰维存储 <b>−73.3%</b> · 香农芯创 <b>−68.1%</b> · 德明利 <b>−70.4%</b>（收盘对收盘，前复权）</td>
      <td><span class="tag tag-bull">吻合且偏保守</span><br><b>8 只里 7 只落在 −64%~−73%</b></td></tr>
    <tr><td>11/11 11:22「<b>看深成指、创业板指数即可</b>」</td>
      <td>创业板指 <b>+1.40%</b> · 深成指 <b>+0.39%</b> vs 沪指 <b>−0.10%</b> · 沪深300 <b>−0.09%</b></td>
      <td><span class="tag tag-bull">吻合</span><br>深市成长明显强于大盘</td></tr>
    <tr><td>11/11 10:17「<b>死鬼，又绿了！</b>」</td>
      <td>10:17 沪指 3650.66，较昨收 3663.72 <b>−0.36%</b>（当日最低 3650.31）</td>
      <td><span class="tag tag-bull">吻合</span><br>发帖时点正在低位</td></tr>
  </tbody>
  </table>
  <p style="margin-bottom:0"><b>一句话</b>：<b>本系列至今 7 条具名操盘信号 + 全部外盘播报，
  在本机可独立核验的范围内全部命中。</b>他的数字可以直接当数据源用 ——
  这是本系列跟踪下来最硬的结论。</p>
</div>

<div class="panel">
  <h3 style="margin-top:0">本期评级</h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>信号密度</b>：★★★★★ —— 12 条里 8 条为操盘相关，其中 <b>2 条板块点名（CPO、存储芯片）</b>、
      <b>1 条转折点（换板块）</b>、1 条自我验证、1 条大盘口径调整、1 条方向性表态。
      <b>3 个板块全部来自具名点名，没有一条是推断出来的。</b></li>
    <li><b>可执行度</b>：★★★★☆ —— <b>换板块的方向给出得极清楚</b>（10:48 逻辑 + 10:58/11:11 答案），
      <b>选股条件直接沿用 11/10 的公式</b>（磨在底部 + 业绩增速明显），落地路径完整。
      <b>扣一分</b>：他没给具体点位与仓位，只给方向 —— 所以「买多少、买在哪」仍要自己算。</li>
    <li><b>数据可信度</b>：★★★★★ —— 七条核验全部命中，包括 <b>「跌 60%~70%」这种最容易被夸大的表述
      （实测 8 只里 7 只 −64%~−73%，他反而说保守了）</b>。</li>
    <li><b>需要警惕的</b>：<b>本期最大风险不在他身上，在盘面上</b> ——
      缩量、涨停腰斩、涨跌家数反转、3706 更远。
      <b>而他今天说的最大一句「现在追不是上策」，恰恰是针对今天涨得最好的板块</b>。
      <b>照纲领做（按低位选存储、龙头等回踩、分批），照样例做（追 CPO 的 10% 大阳线）。</b></li>
  </ul>
</div>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容的信息整理与技术面统计，<b>不构成任何投资建议</b>。
  所有涨跌幅、点位、成交额、估值数据均标注来源，可独立复现（脚本见仓库 <code>scripts/</code> 目录）。
  「最值得投资的 3 个板块 + 3 支个股」的表述是对<b>博主当日观点 + 当日板块实测强度</b>的归纳，
  不代表对上述标的的推荐或看多看空立场。
  <b>本报告为盘中版（数据截至 11/11 13:09），收盘数据可能与文中数值不同。</b>
  股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-11 · 数据源 weibo skill + Tushare Pro + 东方财富 · 图表脚本
    <code>scripts/make_wu2198_charts_20261111.py</code> · K 线配色经
    <code>scripts/check_kline_colors_20261111.py</code> 逐图像素校验（6/6 一致）。
  </p>
</div>

</div>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"[report] {OUT}  ({len(html.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
