"""wu2198 投资日报 2026-11-12（周四 · 收盘版 · 精简版）— 线上产物生成器

用法： ~/czsc/.venv/bin/python scripts/gen_wu2198_report_20261112.py
产物： 2026-11-12-wu2198-investment-report.html（仓库根目录）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张（用户 2026-11-12 硬约束）
"""
import json
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpi_20261112.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_sectors_20261112.json").read_text(encoding="utf-8"))
BR = json.loads((CH / "_breadth_20261112.json").read_text(encoding="utf-8"))

SH = KPI["000001.SH"]
CY = KPI["399006.SZ"]
b12, b11 = BR["20261112"], BR["20261111"]
mil = SEC["sw_mil"]
p_st, p_cpo, p_rob = SEC["pools"]["存储/半导体/GPU"], SEC["pools"]["CPO/光通信"], SEC["pools"]["人形机器人/端侧"]

TITLE = "wu2198 投资日报 - 2026-11-12（周四 GPU逆势，双门槛未收复）"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<style>
  :root {{
    --bg: #ffffff; --panel: #f8f9fb; --panel-2: #f1f3f6;
    --border: #e5e7eb; --border-strong: #d1d5db;
    --text: #1f2937; --muted: #6b7280;
    --bull: #16a34a; --bull-bg: #dcfce7;
    --bear: #dc2626; --bear-bg: #fee2e2;
    --neutral: #d97706; --neutral-bg: #fef3c7;
    --none: #6b7280; --none-bg: #f3f4f6;
    --accent: #2563eb; --accent-bg: #dbeafe;
    --key: #7c3aed;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px;
  }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1, h2, h3 {{ font-weight: 600; line-height: 1.3; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 17px; margin: 24px 0 10px; }}
  p {{ margin: 8px 0; }}
  a {{ color: var(--accent); text-decoration: none; }}
  .meta {{ color: var(--muted); font-size: 13px; }}
  .meta span {{ margin-right: 14px; }}

  .hero {{ background: linear-gradient(135deg, #eff6ff 0%, #f7fbff 100%); border: 1px solid #93c5fd; border-radius: 12px; padding: 24px 28px; margin-bottom: 28px; }}
  .hero h1 {{ color: #1e3a8a; }}
  .hero .stance {{ font-size: 16px; margin: 8px 0 0; }}

  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px 22px; margin: 16px 0; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
  @media (max-width: 900px) {{ .grid-4 {{ grid-template-columns: 1fr 1fr; }} }}
  @media (max-width: 620px) {{ .grid-4 {{ grid-template-columns: 1fr; }} }}

  .kpi {{ background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; text-align: center; }}
  .kpi .label {{ font-size: 12px; color: var(--muted); letter-spacing: 0.5px; }}
  .kpi .val {{ font-size: 20px; font-weight: 600; margin: 4px 0; }}
  .kpi .sub {{ font-size: 12px; color: var(--muted); }}

  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: var(--panel-2); font-weight: 600; color: var(--muted); font-size: 12px; }}
  tr:hover {{ background: var(--panel); }}
  td.text {{ max-width: 420px; }}
  td.score {{ font-variant-numeric: tabular-nums; text-align: right; }}

  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; margin: 0 2px; }}
  .tag-bull {{ background: var(--bull-bg); color: var(--bull); }}
  .tag-bear {{ background: var(--bear-bg); color: var(--bear); }}
  .tag-neutral {{ background: var(--neutral-bg); color: var(--neutral); }}
  .tag-accent {{ background: var(--accent-bg); color: var(--accent); }}

  .chart {{ width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; background: #fff; }}
  .chart-caption {{ font-size: 12px; color: var(--muted); margin: -4px 0 16px; }}

  .quote {{ background: var(--panel-2); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; border-left: 3px solid var(--border-strong); }}
  .risk {{ background: var(--bear-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .action {{ background: var(--bull-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .verify {{ background: var(--accent-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .up {{ color: var(--bull); font-weight: 600; }}
  .down {{ color: var(--bear); font-weight: 600; }}
  .key-num {{ color: var(--key); font-weight: 700; font-variant-numeric: tabular-nums; }}
  .foot {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }}
  ul.tight {{ margin: 8px 0; padding-left: 22px; }}
  ul.tight li {{ margin: 4px 0; }}
</style>
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta">
    <span>🕘 截稿 2026-11-12 22:05（收盘版）</span>
    <span>📡 weibo skill（时间线 + 两轮搜索词表补采，15 条）</span>
    <span>💹 Tushare Pro 11/12 收盘（前复权）</span>
  </div>
  <p class="stance">
    <b>🟡 门槛不变、方向不改。</b>今天等沪指收复 <b>3706</b> + 创业板 <b>2626</b>，
    双双未果（试 <b>3699.58</b> / <b>2620</b> 后回落），他定性为
    「<b>短线突破前的回洗</b>……构筑反弹的基础还在」。
    唯一异动是 <b>GPU 逆势</b> —— 英伟达盘后利空被他当成「借利空低吸的机会」。
    <b>仓位维持、不加码</b>；人形机器人/端侧 10 只全跌，他的警示当天兑现。
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 距 <b>3706</b> 差 50.17 点</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 距 <b>2626</b> 差 116.57 点</div></div>
  <div class="kpi"><div class="label">全 A 成交额</div><div class="val">{b12['amount_yi']:,.0f} 亿</div>
    <div class="sub"><span class="up">放量 2572 亿（+15.2%）</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{b12['up']} / {b12['down']}</div>
    <div class="sub">涨停 46（昨 113）· 跌停 19（昨 5）</div></div>
</div>

<h2>一、博主说了什么（只列能触发动作的 10 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>09:45</b></td><td>🟢 GPU</td><td class="text">英伟达或罢免皮衣哥，盘后跌9%……这是主力借利空低吸的机会。同时利好国内GPU股！</td><td class="text"><b>全期最准一条</b>：英伟达盘后一度 −9%（证券时报/澎湃）；11/11 费半 +5.66%。当日 <b>寒武纪 +8.11%</b>、海光 +3.07%，<b>科创50 是唯一收涨指数（+0.73%）</b>。</td></tr>
<tr><td><b>09:55</b></td><td>🟡 板块+门槛</td><td class="text">目前看GPU、存储芯片、半导体、CPO等领先科技股反弹。等待创业板指数收复2626点</td><td class="text">存储池均值 <b>+1.04%</b>、GPU 逆势；<b>CPO 池 −2.09%</b>（中际旭创 −6.11%）当日即证伪。门槛与 11/11 一致。</td></tr>
<tr><td><b>10:29</b></td><td>🟡 波浪</td><td class="text">前面杀到低点时，第一时间给出了分析的！第四浪的底部位置</td><td class="text">重复 11/11 的底部定位。<b>底部成立、反转未确认</b>：日线 DIF/DEA 仍双双在零轴下方。</td></tr>
<tr><td><b>13:09</b></td><td>⚪ 情绪</td><td class="text">郁闷，压下来干嘛？</td><td class="text">非信号帖（对应午后开盘回落），不计入操作判断。</td></tr>
<tr><td><b>13:33</b></td><td>🟢 回洗定性</td><td class="text">短线突破前的回洗（大盘3706点和创业板指数2626点），会清理掉一批浮动筹码。</td><td class="text">当日成交额放大至 <b>1.95 万亿（+15.2%）</b>、跌家数 4635、涨停 113→46、跌停 5→19 —— <b>放量换手 + 浮筹出清</b>，与定性一致。</td></tr>
<tr><td><b>13:55</b></td><td>🟡 板块点名</td><td class="text">军工板块出现拉起，有五六只冲板！</td><td class="text"><b>收盘口径未兑现</b>：申万军工 150 只全天触板仅 <b>2 只</b>（长城军工封板 +10.02%、ST亚光 +4.94%），均值 <b>−0.79%</b>、跌 109 家。</td></tr>
<tr><td><b>14:54</b></td><td>🔴 警示</td><td class="text">人形植物人涨了一倍之后，今天领跌！</td><td class="text"><b>当天兑现</b>：机器人/端侧池 <b>10 只全跌</b>、均值 <b>−4.57%</b>，宇树 −8.38%、瑞芯微 −6.08%。</td></tr>
<tr><td><b>14:57</b></td><td>🟡 门槛</td><td class="text">属于第二次收复2626点未果！</td><td class="text">创业板最高 <b>2620.25</b>，差 <b>5.75 点（0.22%）</b> —— 今天离门槛最近的一次。</td></tr>
<tr><td><b>15:05</b></td><td>🟡 收盘定稿</td><td class="text">收复3706点未果（试了3699.58点）回落，收在3655点；创业板收复2626点未果（试了2620点）回落，收在2509点……构筑反弹的基础还在，已经布局的需要有耐心</td><td class="text"><b>四个数字与实测分毫不差</b>（3699.58 / 3655.83 / 2620.25 / 2509.43）。<b>方向不变，只是还没到买点。</b></td></tr>
<tr><td><b>20:36</b></td><td>⚪ 外盘</td><td class="text">德国股市改写了历史新高，报27001点！</td><td class="text">11/11 DAX 已收 <b>26662.77</b> 创历史新高；<b>27001 是欧洲盘中价（未收盘）</b>，「新高」成立、点位待收盘确认。</td></tr>
</tbody>
</table>
<div class="action" style="margin-bottom:0">
  <b>09:45 那条是本期最值钱的信息</b>：他把英伟达利空直接翻译成「利好国内 GPU 股」。
  验证下来当天 GPU 是唯一逆势方向 —— <b>这是他给出的可执行方向，不是泛泛的「科技股反弹」</b>。
  19:09 的「77 万亿存款到期」无对应市场数据，不作判断。
</div>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">
  K 线<b>红涨绿跌</b>（按收 vs 开着色，与「日涨跌幅」口径不同）；关键位在图<b>左侧虚线</b>。
</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="charts/000001_SH_20261112.png" alt="上证指数 2026-11-12 K线">
<p class="chart-caption">开 3673.06 / 高 <b>3699.58</b> / 低 3647.44 / 收 {SH['close']:.2f}。
<b>3706 差 50.17 点（1.37%）</b>，日内最高只差 6.42 点（0.17%）；收盘失守 MA20 {SH['ma20']:.2f}。
日线 MACD 柱 <b>+{SH['macd_bar']:.2f}</b>（仍在零轴下方）。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="charts/399006_SZ_20261112.png" alt="创业板指 2026-11-12 K线">
<p class="chart-caption">高 <b>2620.25</b> / 低 2508.29 / 收 {CY['close']:.2f}。
<b>2626 差 5.75 点（0.22%）—— 今天离门槛最近的一次</b>，但收盘仍跌破 MA20 {CY['ma20']:.2f}。
日线 MACD 柱 <b>+{CY['macd_bar']:.2f}</b>。</p>

<div class="risk">
  <b>⚠️ 放量下跌才是今天的主信息。</b>全 A 成交 <b>{b12['amount_yi']:,.0f} 亿</b>（比昨日多 2572 亿、<b>+15.2%</b>），
  但<b>跌家数 4635 家（占 83%）</b>、涨停从 113 家降到 <b>46</b> 家、跌停从 5 家增到 <b>19</b> 家。
  这不是缩量回调，是<b>放量换手 + 杀跌</b> —— 与他 13:33「突破前的回洗清浮筹」方向一致，
  但也说明<b>门槛没到之前不能加仓</b>。
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/12 收盘实测</th><th>博主态度 / 明日打法</th></tr></thead>
<tbody>
<tr><td><b>① GPU / 国产算力</b><br><span class="tag tag-bull">首选 · 唯一逆势</span></td>
    <td>寒武纪 <b>+8.11%</b>、海光 +3.07%、星网锐捷 +4.13%（触板）；<b>科创50 +0.73%</b> 是 5 大指数唯一上涨</td>
    <td>09:45「利好国内 GPU 股」。<b>只做龙头，回踩不追高</b>；寒武纪距 60 日高 1170 还有 16.8%，MA20 890.79 是防守位。</td></tr>
<tr><td><b>② 存储芯片</b><br><span class="tag tag-neutral">次选 · 位置最低</span></td>
    <td>核心池 8 只均值 <b>+1.04%</b>（涨 4 / 跌 4），成交 634 亿；兆易创新 −0.30%、佰维 +1.49%</td>
    <td>09:55 点名。<b>内部分化，只能分批低吸</b>：兆易创新距 60 日低 237.28 仅 +9.1%、PE 14.8 / PB 2.24，是三只里估值最低。</td></tr>
<tr><td><b>③ 军工</b><br><span class="tag tag-neutral">观察 · 不追</span></td>
    <td>申万国防军工 150 只均值 <b>−0.79%</b>（涨 41 / 跌 109），<b>全天触板仅 2 只</b>；长城军工 +10.02%、北方长龙 +11.45%</td>
    <td>13:55 盘中新点名。<b>收盘口径没兑现「五六只冲板」</b>，明日看触板数能否 ≥5 只再决定。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避两个</b>：CPO/光通信 8 只均值 <b>−2.09%</b>（11/11 的主线一天退潮）、人形机器人/端侧 10 只<b>全跌</b>、均值 <b>−4.57%</b>（他 14:54 已警示）。
  口径：核心标的池 + 申万一级成分（东财 push2 全程限流），<b>与 11/10「东财全板块」口径不可跨期比较</b>。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>688256</b> 寒武纪</td><td class="score">973.00</td><td class="score"><span class="up">+8.11%</span></td>
    <td class="score">201.7 亿</td><td>MA20 <b>890.79</b> · 60 日高 <b>1170</b></td>
    <td class="text">日线 MACD 柱 <b>+24.22</b>、量能 159%；距 60 日低 750.01 已 +29.7%，<b>不追高，等回踩 MA20</b>。</td></tr>
<tr><td><b>603986</b> 兆易创新</td><td class="score">258.85</td><td class="score"><span class="down">−0.30%</span></td>
    <td class="score">128.7 亿</td><td>MA20 <b>268.20</b> · 60 日低 <b>237.28</b></td>
    <td class="text">逆势抗跌、MACD 柱 <b>+4.74</b>；<b>PE 14.8 / PB 2.24</b> 三只里最低。<b>回踩 250 附近可分批</b>。</td></tr>
<tr><td><b>600760</b> 中航沈飞</td><td class="score">47.66</td><td class="score"><span class="up">+2.23%</span></td>
    <td class="score">7.5 亿</td><td>MA20 <b>47.69</b> · 60 日高 <b>49.80</b></td>
    <td class="text">跑赢申万军工均值 <b>3.0 个百分点</b>；MACD 柱 −0.34 仍微负，<b>60 日高 49.80 就在头顶 4.3%，不追</b>。</td></tr>
</tbody>
</table>

<h3>寒武纪（688256）· 973.00（+8.11%）</h3>
<img class="chart" src="charts/688256_SH_20261112.png" alt="寒武纪 2026-11-12 K线">
<p class="chart-caption">高 1020.00 / 低 915.00 / 收 973.00。红 K 放量 159%，站上 MA20 890.79；60 日低 750.01 在左下，60 日高 1170 在左上。</p>

<h3>兆易创新（603986）· 258.85（−0.30%）</h3>
<img class="chart" src="charts/603986_SH_20261112.png" alt="兆易创新 2026-11-12 K线">
<p class="chart-caption">开 260.00 / 高 273.68 / 低 257.78 / 收 258.85。60 日低 <b>237.28</b> 在左下（仅 +9.1%），60 日高 455.81 在左上。<b>MA20 268.20 尚未收复</b>，MACD 柱 +4.74 仍正。</p>

<h3>中航沈飞（600760）· 47.66（+2.23%）</h3>
<img class="chart" src="charts/600760_SH_20261112.png" alt="中航沈飞 2026-11-12 K线">
<p class="chart-caption">高 48.14 / 低 46.47 / 收 47.66，紧贴 MA20 47.69；60 日高 <b>49.80</b> 是上方压制，60 日低 41.94 在左下。</p>

<h2>五、11/13（周五）盯什么（5 条可验证条件）</h2>
<ul class="tight">
  <li><b>沪指收盘站上 3706 + 创业板站上 2626</b> —— 分别差 50.17 / 116.57 点；两个都到才从「等」转「买回」，<b>只到沪指不算</b>。</li>
  <li><b>创业板 2508.29 的当日低点不能破</b> —— 破了就说明「回洗」定性失效，转为新一轮下跌。</li>
  <li><b>寒武纪回踩 MA20 890.79 不破、且科创50 继续收红</b> —— GPU 主线续不续的直接读数。</li>
  <li><b>申万国防军工触板家数 ≥5 只</b> —— 今天只有 2 只；不到 5 只说明 13:55「五六只冲板」只是盘中小作文，军工不参与。</li>
  <li><b>CPO 池 8 只均值转正 + 跌家数降到 3000 以下</b> —— 11/11 主线死没死、今天是不是纯杀跌。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>13:55 军工<br><span class="tag tag-bear">未兑现</span></td><td class="text">军工板块出现拉起，有五六只冲板！</td>
    <td class="text">收盘口径全天触板 <b>仅 2 只</b>（长城军工封板、ST亚光触及），申万军工均值 −0.79%、跌 109 家。<b>盘中口径无法用日线核实。</b></td></tr>
<tr><td>09:55 点名含 CPO<br><span class="tag tag-bear">当日证伪</span></td><td class="text">GPU、存储芯片、半导体、CPO 等领先科技股反弹</td>
    <td class="text">CPO 核心池 8 只均值 <b>−2.09%</b>、中际旭创 −6.11%；<b>他全天未再提 CPO</b>。</td></tr>
<tr><td>主线切换未明说<br><span class="tag tag-neutral">状态变化</span></td><td class="text">09:55 列举 GPU/存储/半导体/CPO</td>
    <td class="text">实际强度 <b>GPU +8.11% ≫ 存储 +1.04% ≫ CPO −2.09%</b> —— 11/11 的 CPO+存储双主线，<b>今天实际切到 GPU</b>，博主未用一句话说破。</td></tr>
<tr><td>19:09 存款<br><span class="tag tag-neutral">无法核验</span></td><td class="text">77 万亿存款到期，有 20% 流入大A市场就可以了</td>
    <td class="text">无对应可核验的公开市场数据，<b>仅作情绪指标，不作判断</b>。</td></tr>
<tr><td>20:36 德国<br><span class="tag tag-neutral">盘中口径</span></td><td class="text">德国股市改写了历史新高，报27001点！</td>
    <td class="text">「新高」成立（11/11 DAX 收 26662.77 已破前高）；<b>27001 为欧洲盘中价</b>（北京时间 20:36 未收盘），待收盘确认。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>5 条命中</b>：09:45 英伟达盘后利空（实测一度 −9%）、10:29 第四浪底部、13:33 回洗定性、
  14:54 人形机器人领跌、15:05 收盘长文的 <b>3699.58 / 3655 / 2620 / 2509</b> 四个数字分毫不差。
  采集：时间线第 1 页 + 两轮搜索词表补采 → 15 条（09:45–20:36）；行情：Tushare Pro 11/12 收盘前复权，
  外盘用 index_global，涨停/炸板/跌停池用东财 push2ex。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容的信息整理与技术面统计，<b>不构成任何投资建议</b>。
  「3 个板块 + 3 支个股」是对博主当日观点 + 当日实测强度的归纳，不代表推荐。
  股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-12（收盘版 · 精简版）· 数据源 weibo skill + Tushare Pro + 东方财富 ·
    图表脚本 <code>scripts/make_wu2198_charts_20261112.py</code> ·
    报告生成器 <code>scripts/gen_wu2198_report_20261112.py</code> ·
    采集脚本 <code>scripts/collect_daily_20261112.py</code> / <code>scripts/collect_sectors_20261112.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    out = ROOT / "2026-11-12-wu2198-investment-report.html"
    out.write_text(HTML, encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
