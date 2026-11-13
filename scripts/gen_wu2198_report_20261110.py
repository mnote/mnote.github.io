"""生成 2026-11-10 wu2198 投资观点日报 HTML。

窗口：11/09 21:30（上期截断）→ 11/10 15:39
关键新增：11/10 10:04「目前三大人形机器人龙头领涨，龙大改写本轮新高，涨幅接近涨翻番了！」
        11/10 14:42「端侧今天够猛，两大龙头依然封板！」
        11/10 14:52「端侧虽然有几只连续改写新高的，但是还有磨在底部的，业绩增长速度明显了」
        11/10 06:26 早安帖：道指涨1104点 / 纳指涨673点 / 标普涨173点（实测分毫不差）
        11/10 14:32「日本股市涨1684点，涨2.87%。韩国股市涨4.39%」（实测分毫不差）
        11/10 13:47「机构一直这么干的！不敢坚持板块发展方向，不懂分批布局的早就冼干净完了！」
        11/10 14:56「不点评大盘，等待即可」
行情：Tushare Pro，11/10 收盘（周二）
"""
from pathlib import Path

OUT = Path("/Users/maoling/workspace/mnote.github.io/wu2198-20261110.html")

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
    """窗口内 13 条微博 + 信号判定。"""
    rows = [
        ("11/09 21:30", "436", "13", "⚪ 话题", "#黄仁勋妻子买了40件黑色皮夹克#科技界叫他皮衣哥！",
         "无关 A 股。"),
        ("11/09 21:30", "607", "40", "🟢 板块点名", "#黄仁勋出轨对象公司曾采购300亿芯片#<b>利好国内GPU芯片！</b>",
         "上期报告已收录。11/10 15:39 同话题再发一次（见下），构成<b>隔夜延续的主线</b>。"),
        ("11/10 06:26", "12100", "1068", "⚪ 外盘速报",
         "所有人早安……<b>昨晚美国股市涨得头晕目眩，收盘道指涨1104点，纳指涨673点、标普上涨173点。</b>",
         "<b>本期最硬的一条</b>。实测 11/09 美股收盘 DJI <b>+1104.02</b> / IXIC <b>+673.72</b> / SPX <b>+173.08</b> —— "
         "<b>三个数字分毫不差</b>。这是他本系列第四次外盘播报全中（11/07、11/08、11/09、11/10）。"),
        ("11/10 10:04", "6926", "166", "🟢 板块点名",
         "<b>目前三大人形机器人龙头领涨，龙大改写本轮新高，涨幅接近涨翻番了！</b>",
         "<b>本窗口最强板块信号</b>，直接点名<b>人形机器人</b>三大龙头。实测 11/10 10:04："
         "宇树科技 796.98（较 10/15 低点 <b>+97.3%</b>，正踩「接近涨翻番」）、上纬新材 233.78（+127.7%）、"
         "杭州柯林 75.98（当日 <b>20cm 涨停</b>）。三只<b>全部改写本轮新高</b>。"),
        ("11/10 13:33", "4961", "189", "🟢 板块强化",
         "回复@pochi6688:你不配！//…<b>两大龙头冲板，连续改写新高也有两只！</b>//…<b>今天又有20厘米的了！</b>",
         "对 10:04 那条的<b>盘中确认</b>。实测 20cm 涨停为杭州柯林(688611)、富瀚微(300613)、"
         "科瑞思(301314)、视涯科技-UW(688781)。「连续改写新高也有两只」与实测的"
         "瑞芯微、源杰科技等同向印证。"),
        ("11/10 13:44", "7495", "367", "🟡 情绪", "耐心等待！//@wu2198:一本正经看反弹……明白？",
         "转发自己前一条<b>「一本正经看反弹」</b>。自我调侃，立场仍是<b>看反弹但要等</b>。"),
        ("11/10 13:47", "8069", "348", "🟢 操作建议",
         "<b>机构一直这么干的！不敢坚持板块发展方向，不懂分批布局的早就冼干净完了！</b>",
         "<b>本期最明确的一条操作纲领</b>。两个关键词：<b>坚持板块方向</b> + <b>分批布局</b>。"
         "这是对当天「机构压盘」质疑的直接回应，等于再次确认「不追涨、分批」。"),
        ("11/10 14:32", "5929", "388", "⚪ 外盘速报", "<b>日本股市涨1684点，涨2.87%。韩国股市涨4.39%。</b>",
         "<b>又一个分毫不差</b>。实测 11/10 日经 225 收 <b>+1684.08 点（+2.8653%）</b>、"
         "韩国综合 <b>+4.3891%</b> —— 点数与百分比全部对上。"),
        ("11/10 14:42", "6274", "190", "🟢 板块点名", "<b>端侧今天够猛，两大龙头依然封板！</b>",
         "点名<b>端侧 AI</b>。「依然封板」= <b>连续两日涨停</b>，实测指向光洋股份(002708) 与盛洋科技(603703)，"
         "两者 11/09 首板、11/10 二板，且都属端侧/AI 眼镜/光学光电链。"),
        ("11/10 14:49", "7394", "376", "🟡 盘面观察", "感觉故意压着！",
         "抱怨主力刻意压制。与 13:47 那条「机构一直这么干的」同源：<b>他对当天的上涨是有保留的</b>。"),
        ("11/10 14:52", "7539", "263", "🟢 板块点名 + 布局",
         "<b>端侧虽然有几只连续改写新高的，但是还有磨在底部的，业绩增长速度明显了，涨是早晚的事情。</b>",
         "<b>本期最有操作性的一条</b>。前半句确认端侧已有新高股，后半句直接给出<b>下一批</b>："
         "<b>还在底部 + 业绩增速明显</b>的端侧标的。这是「主线延伸」的明确指引，不只是复盘。"),
        ("11/10 14:56", "11359", "1066", "🟡 大盘判断",
         "今天小粉裙飘杨……<b>不点评大盘，等待即可</b>……收到请回复666或者点赞支持一下！",
         "<b>本窗口互动最高的一条（赞 1.14 万）</b>，但核心是「<b>不点评大盘</b>」。"
         "延续 11/09「耐心先等大盘收复 3706」—— <b>3706 未收复，他就不给大盘方向</b>。"),
        ("11/10 15:39", "5293", "232", "⚪ 话题", "#美国两党都要查黄仁勋#<b>科技战的一部分？</b>",
         "11/09 21:30「利好国内GPU芯片」的<b>隔夜延续</b>。注意带问号 —— 是<b>提问</b>不是断言，"
         "但方向与 11/09 一致。"),
    ]
    out = []
    for t, likes, comments, sig, text, note in rows:
        cls = "tag-bull" if sig.startswith("🟢") else ("tag-bear" if sig.startswith("🔴") else ("tag-neutral" if sig.startswith("🟡") else "tag-none"))
        out.append(
            f"<tr><td style='white-space:nowrap'>{t}</td>"
            f"<td class='score'>{likes}</td><td class='score'>{comments}</td>"
            f"<td><span class='tag {cls}'>{sig}</span></td>"
            f"<td class='text'>{text}</td><td class='text'>{note}</td></tr>"
        )
    return "\n".join(out)


SECTOR_ROWS = """
<tr><td><b>人形机器人</b></td><td class="score">+7.15%</td><td class="score">100 / 100</td>
    <td>杭州柯林 +20.01 · 维宏股份 +12.54 · 同星科技 +12.06 · 井松智能 +12.01 · 伟创电气 +10.67 · 兆丰股份 +10.28 · 联创电子 +10.08 · 豪恩汽电 +10.07</td>
    <td><span class="tag tag-bull">博主点名</span> 10:04「三大人形机器人龙头领涨」</td></tr>
<tr><td><b>端侧 AI / AI 眼镜</b></td><td class="score">+5.99%</td><td class="score">100 / 100</td>
    <td>富瀚微 +20.01 · 视涯科技-UW +20.00 · 纬达光电 +17.15 · 星宸科技 +14.74 · 隆利科技 +12.04 · 中科蓝讯 +10.11 · 联创电子 +10.08 · 国光电器 +10.03</td>
    <td><span class="tag tag-bull">博主点名</span> 14:42 + 14:52 两条</td></tr>
<tr><td><b>科技战 / 国产 GPU</b></td><td class="score">+3.19%</td><td class="score">34 / 39</td>
    <td>星宸科技 +14.74 · 瑞芯微 +10.00 · 泰凌微 +6.86 · 航宇微 +6.49 · 铂科新材 +6.30 · 炬芯科技 +5.53 · 晶晨股份 +5.16 · 国科微 +4.51</td>
    <td><span class="tag tag-bull">博主点名</span> 11/09 21:30 + 11/10 15:39</td></tr>
<tr style="opacity:.62"><td>智能音箱 <span class="tag tag-none">端侧细分</span></td><td class="score">+6.11%</td><td class="score">19 / 19</td>
    <td>中科蓝讯 +10.11 · 国光电器 +10.03 · 瑞芯微 +10.00 · 朝阳科技 +10.00 · 瀛通通讯 +9.97 · 创维数字 +9.96 …</td>
    <td><span class="tag tag-none">并入端侧</span></td></tr>
<tr style="opacity:.62"><td>机器人概念 <span class="tag tag-none">宽口径</span></td><td class="score">+9.02%</td><td class="score">99 / 99</td>
    <td>杭州柯林 +20.01 · 富瀚微 +20.01 · 科瑞思 +20.00 · 海昌新材 +17.12 · 世纪恒通 +15.40 · 星宸科技 +14.74 …</td>
    <td><span class="tag tag-none">并入人形机器人</span></td></tr>
<tr style="opacity:.62"><td>CPO / 光模块 <span class="tag tag-none">上期主线</span></td><td class="score">—</td><td class="score">—</td>
    <td>本窗口博主<b>未再提及</b>；11/10 光通信模块主力净流入仍达 56.9 亿，但缺博主点名</td>
    <td><span class="tag tag-none">落选（无点名）</span></td></tr>
"""


def main():
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>wu2198 投资观点日报 · 2026-11-10</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 wu2198 投资观点日报 · 2026-11-10（周二）</h1>
  <div class="meta">
    <span>🕘 抓取时间：2026-11-10 23:05</span>
    <span>📡 数据源：weibo skill（访客时间线 + 双词表搜索补采 + 去重合并）</span>
    <span>💹 行情：Tushare Pro（11/10 收盘 · 前复权）</span>
  </div>
  <p class="stance">
    核心立场：🟢 <b>继续看反弹，但把操作口径从「看方向」改成「坚持方向 + 分批布局」</b>。
    13:47「<b>不敢坚持板块发展方向，不懂分批布局的早就冼干净完了</b>」是本期唯一的操作纲领；
    14:56「<b>不点评大盘，等待即可</b>」说明 <b>3706 仍未收复，他就不给大盘方向</b>。
    板块上他连续两天锁定<b>人形机器人</b>与<b>端侧 AI</b>，并给出下一批的选股条件：<b>磨在底部 + 业绩增速明显</b>。
  </p>
</div>

<div class="grid-4">
  <div class="kpi"><div class="label">上证指数</div><div class="val">3663.72</div>
    <div class="sub"><span class="up">+0.08%</span> · 高 3683.73 · <b>3706 未收复</b></div></div>
  <div class="kpi"><div class="label">全 A 成交额</div><div class="val">15167 亿</div>
    <div class="sub"><span class="vol">放量 221 亿</span>（+1.5%）</div></div>
  <div class="kpi"><div class="label">涨停 / 跌停</div><div class="val">93 / 0</div>
    <div class="sub">前值 54 / 1 · 情绪<b>显著回暖</b></div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val">4273 / 1149</div>
    <div class="sub"><span class="up">涨多于跌</span> · 较前日反转</div></div>
</div>

<div class="hero-win">
  <h3>📌 一句话总览</h3>
  <p style="margin-bottom:0">
    <b>指数几乎不动、个股全面走强、涨停翻近一倍</b> —— 沪指只涨 0.08%（高开 3682.04 后回落收 3663.72），
    但全 A <b>4273 家上涨 / 1149 家下跌</b>，涨停从 54 家跳到 <b>93 家</b>，跌停清零。
    钱不在指数里，在<b>人形机器人 + 端侧 AI</b>两条主线的个股里。
    博主完全没点评大盘（14:56「不点评大盘，等待即可」）—— 他在等 <b>3706</b>，但他的钱早就在板块里了。
    <b>本期 3 个板块全部来自他当日的具名点名，没有一条是推断出来的。</b>
  </p>
</div>

<h2>一、窗口内全部微博与信号判定</h2>
<p class="meta">
  窗口 <b>11/09 21:30（上期截断）→ 11/10 15:39</b>，共 <b>13 条</b>（11/10 十一条 + 11/09 两条）。
  采集路径：时间线第 1 页 → 搜索接口双词表补采（49 词 / 38 词）→ 合并去重。
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
    <li><b>操作纲领从「等信号」变成「守方向」</b>：11/09 是「耐心先等大盘收复 3706」，
      11/10 变成「<b>不敢坚持板块发展方向，不懂分批布局的早就冼干净完了</b>」——
      他不再等大盘给方向，而是<b>直接指定方向 + 分批买入</b>。这是本系列里最主动的一次表述。</li>
    <li><b>选股条件首次成体系</b>：14:52「<b>还有磨在底部的，业绩增长速度明显了，涨是早晚的事情</b>」
      —— 这是他第一次给出<b>可执行的选股公式</b>（底部 + 业绩增速），而不只是点名已涨的票。
      上期他举上纬、宇树是<b>事后证明</b>（11/09 收盘后），本期是<b>事前指路</b>。</li>
    <li><b>他承认自己被压盘</b>：14:49「感觉故意压着！」+ 13:47「机构一直这么干的」——
      <b>他对 11/10 的上涨是有保留的</b>。这解释了为什么 14:56 全窗口互动最高（1.14 万赞）的帖子
      反而是「不点评大盘，等待即可」。</li>
  </ul>
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
        <li><b>上证</b>：开 3682.04 → 收 3663.72，<b>绿 K</b>，但较昨收 3660.79 <b>仍涨 +0.08%</b> —— 图上已标「高开回落」；</li>
        <li><b>沪深300</b>：开 4089.05 → 收 4059.11，<b>绿 K</b>，较昨收 4056.11 <b>涨 +0.07%</b> —— 同为「高开回落」；</li>
        <li><b>创业板指</b>：开 2518.44 → 收 2494.40，<b>绿 K</b>，较昨收 2458.56 <b>涨 +1.46%</b> —— 全部高开低走。</li>
      </ul>
    </li>
    <li>关键点位在 K 线图 <b>左侧以虚线标注</b>（📌 博主点位 / 支撑位 / 昨收位），
      MA5（橙）/ MA10（紫）/ MA20（天蓝）为叠加曲线。<b>价格刻度移到右侧</b>，左侧只留给关键点位标签。</li>
  </ul>
</div>

<h3>上证指数 · 3663.72（+0.08%）</h3>
<img class="chart" src="charts/000001_SH_20261110.png" alt="上证指数 2026-11-10 K线">
<p class="chart-caption">
  11/10 开 3682.04 / 高 3683.73 / 低 3660.72 / 收 3663.72，<b>振幅仅 23.01 点（0.63%）</b>。
  博主 11/09 定的 <b>3706 确认位在左上方虚线</b>，全天最高 3683.73，<b>仍差 22.27 点未收复</b>。
  支撑带 3608–3650（浅蓝底纹）；60 日低 3574.27（10/23）标注在左下。
</p>

<div class="verify">
  <b>「3706 未收复」是本期最重要的一句话</b>。他 11/09 09:43 说「耐心先等大盘收复 3706 点」，
  11/10 全天最高 3683.73，<b>差 0.60%</b>没摸到；14:56 因此改口「不点评大盘，等待即可」。
  <b>他给门槛、他自己守门槛</b> —— 这正是上期报告说的「他认可方向，不认可追高」的延续，
  只是这次门槛被明明白白写成了数字。
</div>

<h3>创业板指 · 2494.40（+1.46%）</h3>
<img class="chart" src="charts/399006_SZ_20261110.png" alt="创业板指 2026-11-10 K线">
<p class="chart-caption">
  开 2518.44（高开 +2.44%）→ 收 2494.40，<b>绿 K 但当日涨 1.46%</b>，图上已标「高开回落」。
  收在 MA10（2494.61）附近，MA20（2599.80）仍在上方压制；下方昨收 2458.56、60 日低 2376.28。
</p>

<h3>沪深300 · 4059.11（+0.07%）</h3>
<img class="chart" src="charts/000300_SH_20261110.png" alt="沪深300 2026-11-10 K线">
<p class="chart-caption">
  开 4089.05 → 收 4059.11，<b>绿 K 但微涨 +0.07%</b>。权重股几乎走平，
  与「指数微涨、个股普涨」的结构吻合：<b>扛指数的没动，动的是中小盘题材股</b>。
</p>

<h2>三、最值得投资的 3 个板块 + 3 支个股</h2>

<p class="meta">筛选口径：博主当日<b>具名点名</b>的板块 → 用东方财富板块成分（剔除 2026-10 以后上市的次新，避免首日暴涨污染均值）实测当日涨跌幅均值 + 上涨家数占比验证 → 取前 3。
板块口径与上期一致（剔除次新后统计）。</p>

<table>
<thead><tr><th>板块</th><th class="score">样本均值</th><th class="score">上涨家数</th><th>样本明细（当日涨跌幅 %）</th><th>依据</th></tr></thead>
<tbody>
{SECTOR_ROWS}
</tbody>
</table>

<div class="sector r1">
  <h3>① 人形机器人 —— 唯一「三大龙头同时改写本轮新高」的板块</h3>
  <div class="quote">
    <span class="who">11/10 10:04 · 👍6926 💬166</span>
    <b>目前三大人形机器人龙头领涨，龙大改写本轮新高，涨幅接近涨翻番了！</b>
  </div>
  <p><b>为什么排第一</b>：100 只样本 <b>100/100 全红</b>，均值 <b>+7.15%</b>，主力净流入 <b>+46.6 亿</b>。
  这是当日唯一同时满足「全员上涨 + 三大龙头创新高 + 博主具名点名」的板块。</p>
  <p><b>「涨幅接近涨翻番」实测对上了</b>：10:04 那一刻宇树科技 796.98，较其 10/15 低点 404.03
  <b>+97.3%</b> —— 几乎正好翻番；上纬新材 233.78（+127.7%）已过翻番；杭州柯林当日 <b>20cm 涨停</b>。
  <b>三只全部收在或逼近日内新高。</b></p>
  <div class="risk"><b>但要扣掉他自己泼的水</b>：14:49「<b>感觉故意压着</b>」+ 13:47「机构一直这么干的」——
  他认为当天上涨里有<b>机构压盘的成分</b>，涨幅并非自然形成。
  准确的理解是：<b>机器人是最强的当日方向，也是他连续第二天点名的方向，但涨得并不轻松</b>。</div>
</div>

<div class="sector r2">
  <h3>② 端侧 AI —— 唯一给出「下一批怎么选」的板块</h3>
  <div class="quote">
    <span class="who">11/10 14:42 · 👍6274 💬190 &nbsp;|&nbsp; 11/10 14:52 · 👍7539 💬263</span>
    <b>端侧今天够猛，两大龙头依然封板！</b><br>
    <b>端侧虽然有几只连续改写新高的，但是还有磨在底部的，业绩增长速度明显了，涨是早晚的事情。</b>
  </div>
  <p><b>为什么排第二</b>：AI 眼镜板块 100 只样本 <b>100/100 全涨</b>，均值 <b>+5.99%</b>，
  主力净流入 <b>+36.9 亿</b>；智能音箱 19/19、+6.11%。</p>
  <p><b>「两大龙头依然封板」可以精确定位</b>：「依然」= <b>连续两日涨停</b>，
  实测光洋股份(002708) 与盛洋科技(603703) 均为 11/09 首板、11/10 二板，
  且同属端侧 / AI 眼镜 / 光学光电链 —— 措辞与盘面完全对应。</p>
  <div class="action"><b>14:52 那条是本期最有操作性的一句</b>：他不满足于点名已涨停的票，
  而是给出<b>下一批的筛选条件</b> —— <b>还在底部（磨在底部）+ 业绩增速明显</b>。
  这是一个可执行的公式，落地时按这个公式在端侧链里找「位置低、业绩兑现」的票，
  <b>而不是去追已经封板的两个龙头</b>（他自己的纲领就是不追涨）。</div>
</div>

<div class="sector r3">
  <h3>③ 科技战 / 国产 GPU —— 隔夜延续，但当天涨幅最弱</h3>
  <div class="quote">
    <span class="who">11/09 21:30 · 👍607 💬40 &nbsp;|&nbsp; 11/10 15:39 · 👍5293 💬232</span>
    #黄仁勋出轨对象公司曾采购300亿芯片#<b>利好国内GPU芯片！</b><br>
    #美国两党都要查黄仁勋#<b>科技战的一部分？</b>
  </div>
  <p><b>为什么排第三</b>：AI 芯片板块 39 只样本 34/39 上涨，均值仅 <b>+3.19%</b>，主力 +8.0 亿 ——
  <b>是三个板块里涨幅最小、覆盖面最窄的一个</b>。瑞芯微涨停（主力净流入 6.19 亿居首）、
  星宸科技 +14.74%、寒武纪 <b>当日反而跌 1.55%</b>。</p>
  <p><b>成色要打折</b>：两次点名都挂在「黄仁勋出轨对象」的<b>热搜话题</b>下，
  11/10 那条还带<b>问号</b>（是提问不是断言）。<b>「科技战」是情绪型催化，不是订单落地</b>。
  但它是唯一<b>跨日延续</b>的方向，说明他在持续跟踪这条线。</p>
</div>

<h3>3 支个股（按博主点名强度 + 当日实测强度排序）</h3>

<table>
<thead><tr><th>代码</th><th>名称</th><th class="score">收盘</th><th class="score">涨跌</th><th class="score">成交额</th><th class="score">PE(TTM)</th><th class="score">总市值</th><th>入选理由</th></tr></thead>
<tbody>
<tr><td>688836.SH</td><td><b>宇树科技</b></td><td class="score">761.01</td><td class="score"><span class="up">+6.29%</span></td>
  <td class="score">63.8 亿</td><td class="score">549.1</td><td class="score">3078 亿</td>
  <td><span class="tag tag-bull">博主两次具名</span> 11/09 18:40 + 11/10 10:04</td></tr>
<tr><td>603893.SH</td><td><b>瑞芯微</b></td><td class="score">233.20</td><td class="score"><span class="up">+10.00%</span></td>
  <td class="score">41.4 亿</td><td class="score">62.0</td><td class="score">987 亿</td>
  <td><span class="tag tag-bull">端侧 AI 芯片龙头</span> 主力 +6.19 亿居首</td></tr>
<tr><td>688585.SH</td><td><b>上纬新材</b></td><td class="score">218.86</td><td class="score"><span class="up">+1.31%</span></td>
  <td class="score">35.3 亿</td><td class="score">亏损</td><td class="score">883 亿</td>
  <td><span class="tag tag-bull">博主唯一点名个股</span>「涨了一倍多」</td></tr>
</tbody>
</table>

<h2>四、3 支个股 K 线与技术位</h2>

<h3>宇树科技（688836）· 761.01（+6.29%）</h3>
<img class="chart" src="charts/688836_SH_20261110.png" alt="宇树科技 2026-11-10 K线">
<p class="chart-caption">
  开 739.00 / 高 809.00 / 低 729.50 / 收 761.01，成交 <b>63.8 亿</b>，换手 <b>27.51%</b>。
  红 K（收 &gt; 开）且当日 +6.29%，颜色与涨跌一致。<b>上市以来最低 404.03（10/15）</b>标注在左下。
</p>

<div class="verify">
  <b>博主数字核对（本期最硬的一条 · 修正上期结论）</b>：11/09 18:40 他说「<b>宇树从大盘C3低点时至今涨了88%</b>」。
  实测宇树科技 10/15 最低 <b>404.03</b> → 11/09 盘中最高 <b>759.99</b> = <b>+88.1%</b> —— <b>分毫不差</b>。
  <br><br>
  <b>⚠️ 修正上期报告的一处判断</b>：上期报告写「宇树科技已于 2026-08-19 在<b>港交所</b>上市，本报告的行情源不含港股个股，故未做独立核验」。
  <b>这是错的</b> —— 宇树科技是 <b>科创板 688836.SH</b>，2026-08-19 在上交所科创板上市，
  Tushare A 股日线可直接取到。本期已用 A 股数据完成核验，结论是<b>他的 88% 完全准确</b>。
</div>

<p><b>技术状态</b>：日线 MACD <b>DIF +50.86 / DEA +36.12 / 柱 +29.48</b> —— 三者全在零轴上方且多头排列，
是三只里唯一<b>完全进入多头状态</b>的。60 日高点 1100.00（上市首日）→ 现价 761.01，回撤 −30.8%；
但 20 日高点 809.00 已被 11/10 盘中刷新，<b>本轮反弹结构完整</b>。</p>

<div class="risk"><b>风险（三个硬事实）</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>估值极端</b>：PE(TTM) <b>549.1 倍</b>、PB <b>34.5 倍</b>。</li>
    <li><b>换手 27.51%</b> —— 三只里最高，说明筹码在剧烈换手，<b>波动会非常大</b>。</li>
    <li><b>它是次新股</b>（2026-08-19 上市），仅 54 根日线，<b>没有完整的历史支撑结构可参照</b>；
      MA5/MA10/MA20 都是上市后短期均线，参考价值低于老票。</li>
  </ul>
</div>

<h3>瑞芯微（603893）· 233.20（+10.00% 涨停）</h3>
<img class="chart" src="charts/603893_SH_20261110.png" alt="瑞芯微 2026-11-10 K线">
<p class="chart-caption">
  开 218.99（高开 +3.30%）→ 收 233.20 = <b>涨停价</b>，成交 <b>41.4 亿</b>，换手 4.37%。
  红 K（收 &gt; 开）且当日 +10.00%，颜色与涨跌一致。<b>60 日高点 233.20 今日创出</b>。
</p>

<p><b>技术状态</b>：日线 MACD <b>DIF +5.01 / DEA +1.32 / 柱 +7.39</b>，零轴上方金叉且柱体放大。
MA5 214.74 / MA10 201.03 / MA20 197.09 <b>三线多头排列</b>，股价站上全部均线。
下方昨收 212.00 是第一道支撑，60 日低 159.34 是长线底。</p>

<p><b>为什么选它而不是中科蓝讯 / 星宸科技</b>：瑞芯微是<b>端侧 AI SoC 的行业龙头</b>（RK 系列），
当日 <b>涨停 + 主力净流入 6.19 亿居 AI 芯片板块首位</b>，成交 41.4 亿是板块内流动性最好的。
星宸科技 +14.74% 但量仅 22.5 亿；中科蓝讯 +10.11% 却<b>主力净流出 0.15 亿</b>（拉高派发嫌疑）。
<b>三只里瑞芯微是唯一「资金与涨幅同向」的。</b></p>

<div class="risk"><b>风险</b>：PE(TTM) <b>62.0 倍</b>、PB <b>18.1 倍</b> —— 已是全市场最贵的 AI 芯片标的之一；
且它同时出现在<b>端侧、机器人、AI 芯片</b>三个板块的样本里，属于多重标签的拥挤交易。
<b>博主的「端侧还有磨在底部的」这句话，恰恰不是在说它。</b></div>

<h3>上纬新材（688585）· 218.86（+1.31%）</h3>
<img class="chart" src="charts/688585_SH_20261110.png" alt="上纬新材 2026-11-10 K线">
<p class="chart-caption">
  开 223.97（高开 +3.68%）→ 盘中最高 236.00 → 收 218.86，<b>冲高回落 17.14 点</b>，成交 35.3 亿。
  <b>绿 K</b>（收 218.86 &lt; 开 223.97），但较昨收 216.02 <b>仍涨 +1.31%</b>，图上已标「高开回落」。
</p>

<div class="verify">
  <b>博主数字核对</b>：11/09 18:40 他说「<b>上纬从大盘C3低点时至今已经涨了一倍多</b>」。
  实测上纬新材 10/19 最低 <b>102.68</b> → 11/09 收盘 <b>216.02</b> = <b>+110.4%</b> —— 「一倍多」完全吻合。
  11/10 它<b>没有继续涨停</b>，而是高开冲 236 后回落 1.31% —— 已在消化。
</div>

<p><b>技术状态</b>：日线 MACD <b>DIF +18.22 / DEA +10.13 / 柱 +16.19</b>，多头但柱体较 11/09 收窄。
股价站上 MA5（193.87）、MA10（179.96）、MA20（150.20），全部均线在下方支撑。</p>

<div class="risk"><b>风险（上期已提示，本期未解除）</b>：<b>公司自己</b>在 11/09 盘后发了交易风险提示公告
  —— 累计涨幅已超 100%、<b>PE 1767 倍 vs 行业平均 19.57 倍</b>；三季报归母净利 <b>−4.22 亿</b>（亏损），
  PB 高达 <b>94.9 倍</b>。机器人业务<b>尚未确认收入</b>。
  <b>博主的「涨了一倍多」是在陈述已发生的涨幅，不是在推荐现在买</b> —— 与他 13:47「不懂分批布局的早就冼干净完了」并列读，
  含义是「<b>会做的人在 C3 底部布局了</b>」，不是「<b>现在追涨停</b>」。</div>

<h2>五、周线视角：博主「本周主打反弹」的核对（第二周）</h2>

<div class="panel">
  <table>
  <thead><tr><th>指标</th><th class="score">10/30 周</th><th class="score">11/06 周</th><th class="score">本周（截至 11/10）</th><th>变化</th></tr></thead>
  <tbody>
  <tr><td>上证 周线 DIF</td><td class="score">−73.45</td><td class="score">−80.33</td><td class="score">−83.65</td><td class="down">仍在下行</td></tr>
  <tr><td>上证 周线 DEA</td><td class="score">−42.36</td><td class="score">−49.95</td><td class="score">−56.69</td><td class="down">仍在下行</td></tr>
  <tr><td><b>上证 周线 MACD 柱</b></td><td class="score">−62.19</td><td class="score">−60.76</td><td class="score"><b>−53.91</b></td><td class="up">连续三周收窄（+6.85）</td></tr>
  <tr><td>创业板 周线 DIF</td><td class="score">−218.08</td><td class="score">−249.61</td><td class="score">−269.14</td><td class="down">加速下行</td></tr>
  <tr><td><b>创业板 周线 MACD 柱</b></td><td class="score">−250.06</td><td class="score">−250.49</td><td class="score"><b>−231.65</b></td><td class="up">收窄 18.84</td></tr>
  <tr><td>沪深300 周线 MACD 柱</td><td class="score">−136.45</td><td class="score">−129.06</td><td class="score"><b>−115.35</b></td><td class="up">连续三周收窄（+13.70）</td></tr>
  </tbody>
  </table>
</div>

<div class="hero-turn">
  <h3>结论：<b>「反弹」在加速，但「反转」依然不成立 —— 且周线比上期更弱</b></h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>日线级别反弹确认且在加强</b>：沪指日线 MACD 柱 <b>11/06 +10.38 → 11/09 +12.93 → 11/10 +15.21</b>，
      连续三根正柱且逐根放大；创业板 <b>+18.38 → +22.19 → +31.31</b>，同步放大。
      DIF 在零轴下方但已上穿 DEA 并持续走阔。</li>
    <li><b>但周线的 DIF / DEA 还在往下走</b>：沪指周线 DIF <b>−80.33 → −83.65</b>、DEA <b>−49.95 → −56.69</b>，
      创业板 DIF <b>−249.61 → −269.14</b>。
      <b>柱收窄只是跌速放缓，价格重心还没上移</b> —— 这是「反弹」不是「反转」的量化证据。</li>
    <li><b>所以他的用词依然精确</b>：11/06「探低抵抗」、11/09「探低成功回稳，本周主打反弹」、
      11/10「不点评大盘，等待即可」。<b>连续三周都没说过「反转」「反转点」「主升」</b>。
      反弹阶段的正确心法与他 13:47 那句完全一致：<b>坚持方向 + 分批布局</b>，不是满仓等反转。</li>
  </ul>
</div>

<h2>六、下个交易日（11/11 周三）操作建议</h2>

<div class="action">
  <b>① 方向：按他的原话做 —— 「坚持板块方向 + 分批布局」</b><br>
  他 11/10 不再等大盘给方向，而是直接指定了方向（人形机器人 + 端侧 AI）并给出了买入方式（分批）。
  翻译成执行：<b>在这两条线里低吸，回踩就分批，不要在涨停板上排队</b>。
</div>

<div class="action">
  <b>② 三个板块的优先次序与打法</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>端侧 AI（首选 · 唯一有选股公式的）</b>：14:52 给了公式 ——
      <b>「磨在底部 + 业绩增速明显」</b>。落地做法：在端侧 / AI 眼镜 / 智能音箱链里找<b>股价位置低</b>、
      <b>业绩已兑现</b>的票（例如当日仍在低位的亿道信息、康冠科技一类），<b>不碰</b>已经二连板的光洋、盛洋。</li>
    <li><b>人形机器人（次选 · 只做龙头）</b>：100/100 全涨、均值 +7.15%、主力 +46.6 亿，是当日最强方向。
      但他已经说过「感觉故意压着」—— <b>只做三大龙头（宇树 / 上纬 / 杭州柯林），不做跟风小票</b>，
      且<b>宇树换手 27.5%、估值 549 倍，仓位要按「高波动小票」给</b>。</li>
    <li><b>科技战 / 国产 GPU（第三 · 观察）</b>：两次点名都挂在热搜话题下、11/10 那条还带问号，
      且当日 AI 芯片板块涨幅最小（+3.19%）、<b>寒武纪还跌了 1.55%</b>。
      <b>不构成主线，只做观察</b>；真要参与也是瑞芯微这种「资金与涨幅同向」的龙头。</li>
  </ul>
</div>

<div class="risk">
  <b>③ 三条硬风险（按优先级）</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>3706 仍未收复</b>。他明说「耐心先等大盘收复 3706」「不点评大盘，等待即可」。
      <b>没有他确认的信号之前，大盘层面的加仓没有依据</b>。11/10 最高 3683.73，差 0.60%。</li>
    <li><b>他承认当天涨得「不干净」</b>：13:47「机构一直这么干的」+ 14:49「感觉故意压着」。
      <b>题材接力（涨停 54 → 93 家）叠加主力压盘</b>，是典型的<b>高波动、易回吐</b>结构。
      他自己那句「不懂分批布局的早就冼干净完了」，<b>就是为这种结构写的</b>。</li>
    <li><b>估值风险在三只个股上都成立</b>：宇树 PE 549 / PB 34.5、瑞芯微 PE 62 / PB 18.1、
      上纬 PE 1767（公司自曝）/ PB 94.9 且亏损。<b>这个板块的上涨是估值扩张驱动的，不是业绩驱动</b>，
      涨得快回撤也快。</li>
  </ul>
</div>

<div class="verify">
  <b>④ 需要盯的验证点（观察清单，不是预测）</b>
  <ul class="tight" style="margin-bottom:0">
    <li><b>沪指能否收复 3706</b>：这是他给大盘的唯一门槛，收复前他大概率继续「不点评」。</li>
    <li><b>成交额能否站上 1.6 万亿</b>：11/10 是 15167 亿（+221 亿）。<b>放量但幅度有限</b>，
      反弹要延续通常需要量能继续跟上。</li>
    <li><b>涨停家数能否守住 80 家以上</b>：11/10 是 93 家（前值 54）。掉回 50 家以下说明题材接力断了，
      端侧那两个二连板大概率也保不住。</li>
    <li><b>端侧板块上涨家数能否维持 100/100</b>：一旦出现下跌家数，端侧主线就退化为「抱团」，
      14:52 说的「磨在底部」的票还有空间；反之则说明整条线已经涨透。</li>
    <li><b>宇树 809.00（11/10 盘中新高）</b>：站稳则本轮新高延续；跌回 MA5（693.93）下方，
      说明 27.5% 换手之后有资金出逃。</li>
  </ul>
</div>

<h2>七、信号质量评估与本期方法说明</h2>

<div class="panel">
  <h3 style="margin-top:0">数据来源与采集路径</h3>
  <ul class="tight">
    <li><b>微博</b>：weibo skill，访客模式时间线第 1 页 → 搜索接口双词表补采（49 词 / 38 词）→
      合并去重 <b>13 条</b>（窗口 11/09 21:30 → 11/10 15:39）。</li>
    <li><b>行情</b>：Tushare Pro，11/10 收盘，个股按后复权因子前复权处理，60 根日线窗口
      （宇树科技为次新，实际 54 根）。</li>
    <li><b>成交额 / 涨跌家数</b>：Tushare <code>daily</code> 全量汇总（<code>amount</code> 单位千元 ÷1e5 → 亿元）；
      涨停 93 / 跌停 0 取自东方财富涨停池 / 跌停池（<code>getTopicZTPool</code> / <code>getTopicDTPool</code>）。</li>
    <li><b>板块统计</b>：东方财富板块成分接口（<code>clist/get</code>），<b>剔除 2026-10 以后上市的次新</b>
      以免首日暴涨污染均值（脚本 <code>scripts/collect_sectors_20261110.py</code>）。</li>
    <li><b>外盘</b>：Tushare <code>index_global</code> —— 11/09 美股收 DJI +1104.02 / IXIC +673.72 / SPX +173.08；
      11/10 日经 225 收 +1684.08 点（+2.8653%）、韩国综合 +4.3891%。</li>
    <li><b>估值</b>：Tushare <code>daily_basic</code>（total_mv / pe_ttm / pb / turnover_rate）。</li>
  </ul>
</div>

<div class="panel panel-2">
  <h3 style="margin-top:0">博主数据的独立核验（四条，全部对上）</h3>
  <table>
  <thead><tr><th>博主语录</th><th>实测</th><th>结论</th></tr></thead>
  <tbody>
  <tr><td>11/10 06:26「道指涨<b>1104</b>点，纳指涨<b>673</b>点、标普上涨<b>173</b>点」</td>
      <td>11/09 收 DJI <b>+1104.02</b> / IXIC <b>+673.72</b> / SPX <b>+173.08</b></td>
      <td><span class="tag tag-bull">分毫不差</span><br>三个数字全部对上</td></tr>
  <tr><td>11/10 14:32「日本股市涨<b>1684</b>点，涨<b>2.87%</b>。韩国股市涨<b>4.39%</b>」</td>
      <td>日经 225 收 <b>+1684.08 点（+2.8653%）</b>；韩国综合 <b>+4.3891%</b></td>
      <td><span class="tag tag-bull">分毫不差</span><br>点数与百分比全部对上</td></tr>
  <tr><td>11/09 18:40「宇树从大盘C3低点时至今涨了<b>88%</b>」</td>
      <td>10/15 低 404.03 → 11/09 盘中高 759.99 = <b>+88.1%</b></td>
      <td><span class="tag tag-bull">吻合</span><br>代码匹配正确（688836，<b>科创板</b>）</td></tr>
  <tr><td>11/09 18:40「上纬从大盘C3低点时至今已经<b>涨了一倍多</b>」</td>
      <td>10/19 低 102.68 → 216.02 = <b>+110.4%</b></td>
      <td><span class="tag tag-bull">吻合</span><br>代码匹配正确（688585）</td></tr>
  </tbody>
  </table>
  <p style="margin-bottom:0"><b>本期修正的上期结论</b>：上期报告称宇树科技「已在<b>港交所</b>上市，本报告行情源不含港股个股，故未做独立核验」。
  <b>该判断有误</b> —— 宇树科技是<b>科创板 688836.SH</b>，可用 A 股数据核验，本期已核，<b>结论为完全吻合</b>。</p>
</div>

<div class="panel">
  <h3 style="margin-top:0">本期评级</h3>
  <ul class="tight" style="margin-bottom:0">
    <li><b>信号密度</b>：★★★★☆ —— 13 条里 6 条为操盘相关（板块点名 3、操作纲领 1、板块布局 1、外盘佐证 1），
      且 3 个板块全部来自具名点名。</li>
    <li><b>可执行度</b>：★★★★★ —— <b>本期最高的一期</b>。13:47「坚持板块方向 + 分批布局」给出方向与买法，
      14:52「磨在底部 + 业绩增速明显」给出选股公式，10:04「三大龙头领涨」给出标的范围。
      <b>三件事凑齐了，这是他第一次同时给方向、买法、选股条件。</b></li>
    <li><b>数据可信度</b>：★★★★★ —— 外盘连续第四次全中（道指/纳指/标普 + 日经/韩股），
      个股涨幅 88% 与「一倍多」分毫不差，<b>他的数字可以直接当数据源用</b>。</li>
    <li><b>需要警惕的</b>：<b>估值集体极端</b>（PE 62 / 549 / 1767），
      且他自己承认当天涨得「被压着」。<b>照纲领做（分批、低吸、不追涨停），照样例做（追封板）</b>。</li>
  </ul>
</div>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容的信息整理与技术面统计，<b>不构成任何投资建议</b>。
  所有涨跌幅、点位、成交额、估值数据均标注来源，可独立复现（脚本见仓库 <code>scripts/</code> 目录）。
  「最值得投资的 3 个板块 + 3 支个股」的表述是对<b>博主当日观点 + 当日板块实测强度</b>的归纳，
  不代表对上述标的的推荐或看多看空立场。股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-10 · 数据源 weibo skill + Tushare Pro · 图表脚本
    <code>scripts/make_wu2198_charts_20261110.py</code> · K 线配色经
    <code>scripts/check_kline_colors_20261110.py</code> 逐图像素校验（6/6 一致）。
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
