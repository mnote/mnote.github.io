"""都业华 2026-11-16 收评（高级班）· 纪要 HTML（白底 · 收盘版）

⛔ 用户 2026-11-11 禁令：只用日线 + 收盘快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261116.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
D = json.loads((RPT / "data_20261116_close.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261116_close.json").read_text(encoding="utf-8"))
XY = json.loads((RPT / "xyuan_20261116_close.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261116C"

TITLE = "DYH 收评 - 2026-11-16（周一 缩量杀跌创新低，池内无买点）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;
    --neutral:#d97706;--neutbg:#fef3c7;--none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
  .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
  h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
  p{margin:6px 0}a{color:var(--accent);text-decoration:none}
  .meta{color:var(--muted);font-size:12px}
  .hero{background:linear-gradient(135deg,#fff7ed,#fffdf7);border:1px solid #fdba74;border-radius:12px;padding:18px 22px;margin-bottom:14px}
  .hero h1{color:#9a3412}.hero .stance{font-size:14.5px;margin:7px 0 0}
  .grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
  @media(max-width:900px){.grid4{grid-template-columns:1fr 1fr}}@media(max-width:700px){.grid4{grid-template-columns:1fr}}
  .kpi{background:#fff;border:1px solid var(--border);border-radius:8px;padding:10px 12px;text-align:center}
  .kpi .label{font-size:11.5px;color:var(--muted)}.kpi .val{font-size:18px;font-weight:600;margin:2px 0}
  .kpi .sub{font-size:11px;color:var(--muted)}
  table{width:100%;border-collapse:collapse;margin:9px 0;font-size:13px}
  th,td{padding:6px 8px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
  th{background:var(--panel);font-weight:600;white-space:nowrap}
  .up{color:var(--up)}.down{color:var(--down)}.vol{color:var(--neutral);font-weight:600}
  .num{font-variant-numeric:tabular-nums;white-space:nowrap}
  .kn{color:var(--key);font-weight:600}
  .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11.5px;white-space:nowrap}
  .tag-bear{background:var(--bearbg);color:var(--bear)}
  .tag-bull{background:var(--bullbg);color:var(--bull)}
  .tag-neutral{background:var(--neutbg);color:var(--neutral)}
  .tag-none{background:var(--nonebg);color:var(--none)}
  .box{background:var(--panel);border-left:4px solid var(--accent);border-radius:6px;padding:11px 14px;margin:9px 0}
  .box-g{background:var(--bullbg);border-left-color:var(--bull)}
  .box-r{background:var(--bearbg);border-left-color:var(--bear)}
  .box-a{background:var(--accentbg);border-left-color:var(--accent)}
  img.chart{width:100%;max-width:100%;display:block;margin:10px 0 4px;border:1px solid var(--border);border-radius:8px;background:#fff}
  .cap{color:var(--muted);font-size:12px;margin:0 0 14px}
  .foot{margin-top:30px;padding-top:12px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
</style>"""


def sp(n):
    return ST[n]["snap"]


def ix(n):
    return IX[n + "_sina"]


sh, cy, kc, zz, hs300 = (ix("上证指数"), ix("创业板指"), ix("科创50"),
                         ix("中证500"), ix("沪深300"))
kcz = ix("科创综指")
amt = D["amount"]
BK_ = BK


def c(v):
    return "up" if v > 0 else ("down" if v < 0 else "")


# ---------------- 板块表 ----------------
BKROWS = [
    ("算力/CPO", "老师：科技方向受英伟达业绩会扰动",
     f'<b>{BK_["算力/CPO"]["avg_pct"]:+.2f}%，0 涨 {BK_["算力/CPO"]["down"]} 跌</b>；'
     f'中际旭创 -12.28%、胜宏 -11.54%、沪电 -10.00%、工业富联 -9.68%'),
    ("半导体", "老师：端侧/存储同步走弱",
     f'{BK_["半导体"]["avg_pct"]:+.2f}%，0 涨 {BK_["半导体"]["down"]} 跌；'
     f'兆易 -9.27%、寒武纪 -8.27%、海光 -6.54%、中芯 -3.67%'),
    ("AI视频/传媒", "老师：二类热点（传媒）",
     f'<b>{BK_["AI视频/传媒"]["avg_pct"]:+.2f}%，0 涨 {BK_["AI视频/传媒"]["down"]} 跌</b>；'
     f'上海电影 -8.57%、昆仑万维 -5.58%、光线 -5.50%、中文在线 -5.23%'),
    ("人形机器人", "老师：今日下热点榜，先观察能否止跌",
     f'{BK_["人形机器人"]["avg_pct"]:+.2f}%，0 涨 {BK_["人形机器人"]["down"]} 跌；'
     f'模塑 -8.55%、绿的谐波 -5.87%、长盈 -5.93%、三花 -3.56%'),
    ("玄学链·东方系", "老师：补跌风险还没有结束",
     f'<b>{BK_["玄学链·东方系"]["avg_pct"]:+.2f}%，1 涨 {BK_["玄学链·东方系"]["down"]} 跌</b>；'
     f'大东方 -10.06%、日出东方 -10.00%、东方环宇 -9.98%、东方海洋 -9.96%（羊字辈：三羊马 -6.15%、水羊 -2.08%）'),
    ("防守（银行/家电/公路/保险/白酒/煤炭）", "老师：与市场节奏相反的防守方向",
     f'全部红盘：家电 {BK_["家电/小家电"]["avg_pct"]:+.2f}%、公路铁路 {BK_["公路铁路"]["avg_pct"]:+.2f}%、'
     f'银行 {BK_["银行"]["avg_pct"]:+.2f}%、电力 {BK_["电力/高股息"]["avg_pct"]:+.2f}%、'
     f'保险 {BK_["保险"]["avg_pct"]:+.2f}%、煤炭石油 {BK_["煤炭/石油"]["avg_pct"]:+.2f}%、白酒 {BK_["白酒"]["avg_pct"]:+.2f}%'),
    ("证券", "老师：有异动，但结构不行",
     f'{BK_["证券"]["avg_pct"]:+.2f}%，6 涨 0 跌；国证证券指数 {ix("证券公司")["close"]:.2f} '
     f'({ix("证券公司")["pct"]:+.2f}%)，逆势翻红但没突破压力'),
]

# ---------------- 个股表 ----------------
ROWS = [
    ("药明康德", "大医药", "等突破前高 157.8 出 15 分钟底分型三买",
     "157.8", f'最高 {sp("药明康德")["high"]:.2f}，差 <b>11.08</b> 未触；低 {sp("药明康德")["low"]:.2f}', "等"),
    ("中国船舶", "防御", "月线扎实、等翻过压力做类二买共振",
     "—", f'收 {sp("中国船舶")["close"]:.2f}（{sp("中国船舶")["pct"]:+.2f}%），<b>池内最抗跌</b>，但低 {sp("中国船舶")["low"]:.2f} 未止跌', "等"),
    ("瑞芯微", "端侧AI", "激进：回调到 208 附近出止跌信号 + 日线有力度底分型过第三根 K 线高点",
     "208", f'<b>最低 {sp("瑞芯微")["low"]:.2f}，已跌破 208（差 1.11）</b>，收 {sp("瑞芯微")["close"]:.2f}；底分型未出', "等"),
    ("伊利股份", "大消费", "结构延续创新高，不追涨",
     "30.46", f'<b>最高 {sp("伊利股份")["high"]:.2f} 创 60 日新高</b>，收 {sp("伊利股份")["close"]:.2f}（{sp("伊利股份")["pct"]:+.2f}%），池内唯一红盘', "不追"),
    ("中文在线", "AI视频", "等突破压力高点 30.38 出底分型三买",
     "30.38", f'最高 {sp("中文在线")["high"]:.2f}，差 2.54；低 {sp("中文在线")["low"]:.2f} 回到 11/09 低点 25.65 附近', "等"),
    ("海天瑞声", "机器人", "对称震荡有破位迹象，观察能否收复修复",
     "—", f'低 {sp("海天瑞声")["low"]:.2f}（{sp("海天瑞声")["pct"]:+.2f}%）继续破位，未收复', "等"),
    ("奥普特", "机器视觉", "激进等回调到中枢下沿止跌；稳健等突破 186.8 出日线底分型三买",
     "140", f'<b>最低 {sp("奥普特")["low"]:.2f} 触及 140 下沿</b>（差 0.20），收 {sp("奥普特")["close"]:.2f}；底分型未出', "等"),
    ("柯力传感", "六维传感器", "等中枢共振或突破高点压力后出三买",
     "53", f'低 {sp("柯力传感")["low"]:.2f}，<b>已跌破 53 支撑 1.90 元</b>，收 {sp("柯力传感")["close"]:.2f}', "等"),
    ("兆易创新", "存储", "继续创新低，无法判断底背驰，等日线有力度底分型",
     "237.28", f'<b>盘中触及跌停 221.42</b>，收 {sp("兆易创新")["close"]:.2f}（{sp("兆易创新")["pct"]:+.2f}%），深跌破 11/09 前低 15.86 元', "等"),
    ("模塑科技", "人形机器人", "顶分型今日出现，回调到 14.95 附近但还没止跌",
     "14.95", f'低 {sp("模塑科技")["low"]:.2f}，<b>距 14.95 仅 0.11 元</b>（14.95 恰是今日跌停价），收 {sp("模塑科技")["close"]:.2f}', "等"),
    ("长盈精密", "人形机器人", "等回调到左边低点支撑做中枢震荡止跌",
     "32.08", f'低 {sp("长盈精密")["low"]:.2f}，距 32.08 门槛 3.82 元，未止跌', "等"),
]

# ---------------- 偏差记录 ----------------
DEVS = [
    ("「倾向走势直接大幅下破的概率较小」",
     f'上证最低 {sh["low"]:.2f} 破 11/13 低 3623.84、距 60 日低 3574.27 只剩 0.34%；创业板指最低 {cy["low"]:.2f} <b>恰是 60 日新低</b>',
     "偏乐观"),
    ("「人形机器人板块内部走势分化」",
     f'篮子均值 {BK_["人形机器人"]["avg_pct"]:+.2f}%，<b>0 涨 9 跌</b>，是普跌不是分化',
     "实为普跌"),
    ("「二类热点：传媒」",
     f'传媒篮子 {BK_["AI视频/传媒"]["avg_pct"]:+.2f}%、0 涨 7 跌，上海电影 -8.57%、中文在线 -5.23%',
     "标签与当日强度不符"),
    ("「证券上方压力 1380 点附近无法突破消化」",
     f'本机唯一可核口径（国证证券指数 399975）收 {ix("证券公司")["close"]:.2f}，量纲不同',
     "无法核验"),
]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<link rel="stylesheet" href="../assets/css/report-table.css">
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收评版 · 数据截至 2026-11-16 收盘</div>
  <p class="stance"><b>结论：今天就是「市场运行很差」的一天，池内 11 只全部无买点，仓位与频率都要压到最低。</b>
  上证 <span class="down">{sh["pct"]:+.2f}%</span>、创业板指 <span class="down">{cy["pct"]:+.2f}%</span>、
  科创综指 <span class="down">{kcz["pct"]:+.2f}%</span>（老师给的四个跌幅<b>逐一对上</b>），
  {BR["down"]} 家下跌、跌停 {POOL["dt"]["tc"]} 家，两市缩量到 <span class="vol">{amt["total_yi"]:,.0f} 亿</span>
  （<span class="down">{amt["growth_pct"]:+.1f}%</span>）——<b>缩量杀跌，不是放量出清</b>。
  上证最低 {sh["low"]:.2f} <b>创新低</b>、距 60 日低 3574.27 只剩 0.34%，3750 差 4.1% 没摸到。
  纪律照抄：<b>总仓上限 4 成、轻仓、降频、不追涨</b>；瑞芯微跌到 208 下方、奥普特触到 140 下沿，
  只是<b>条件到位</b>，不是买点。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3750 未触</div><div class="val down">{sh["pct"]:+.2f}%</div><div class="sub">{sh["close"]:.2f} · 低 {sh["low"]:.2f} 创新低</div></div>
  <div class="kpi"><div class="label">创业板指 / 科创综指 / 中证500</div><div class="val down">{cy["pct"]:+.2f}% / {kcz["pct"]:+.2f}%</div><div class="sub">中证500 {zz["pct"]:+.2f}% · 科创50 {kc["pct"]:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额 · 较 11/13</div><div class="val vol">{amt["total_yi"]:,.0f} 亿</div><div class="sub down">{amt["growth_pct"]:+.1f}%（昨 {amt["prev_total_yi"]:,.0f} 亿）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数 · 跌停</div><div class="val"><span class="up">{BR["up"]}</span> / <span class="down">{BR["down"]}</span></div><div class="sub">跌超 5% {BR["down_5"]} 家 · 跌停 {POOL["dt"]["tc"]} 家</div></div>
</div>

<h2>一、指数：创新低成立，3750 依旧够不着</h2>
<p>老师给的四个跌幅<b>全部对上</b>（上证 -0.87%、创业板 -4.37%、科创综指 -5.41%、中证500 -2.6%）。方向上，
<b>向下条件已触发</b>：上证最低 {sh["low"]:.2f}，破 11/13 低 3623.84 与 11/12 低 3647.44，距 60 日低 3574.27 只剩 0.34%；
创业板指最低 {cy["low"]:.2f} <b>恰好是 60 日新低</b>。向上仍是空谈——3750 一根都没摸到（差 4.1%），
「突破后回抽确认三买」无从谈起。老师口径的「15 分钟弱势下跌中枢震荡、性质没变」与「创新低出底背驰低点」
今天同时成立；<b>但「倾向直接大幅下破的概率较小」这句偏乐观</b>：今天恰恰是继续下破，且量能同步萎缩
（{amt["total_yi"]:,.0f} 亿，{amt["growth_pct"]:+.1f}%），属于缩量阴跌而非放量砸出底部。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：防守与科技彻底分家</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 家数 · 代表股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三件要记的：</b>① 老师「涨幅榜靠前主要是防守」成立——新浪行业榜前六：开发区 +2.91%、公路桥梁 +2.00%、
金融 +1.19%、家电 +1.18%、酿酒 +1.05%、煤炭 +0.54%；② <b>跌停 {POOL["dt"]["tc"]} 家集中在
通用设备 5、汽车零部 4、元件 4、光伏设备 4</b>，杀跌主力是机器人与科技权重，不是指数权重；
③ 涨停仅 {POOL["zt"]["tc"]} 家且极散（一般零售 3、电池 3、游戏 2…），<b>没有主线</b>。
防守只当参照物，<b>不要追红盘</b>。</p>

<h2>三、11 只标的：全部无买点，只有条件到位</h2>
<table>
  <tr><th>标的 / 题材</th><th>收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{sp(n)["close"]:.2f} <span class="{c(sp(n)["pct"])}">{sp(n)["pct"]:+.2f}%</span></td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="不追" else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<p><b>最接近触发的两个：</b>瑞芯微最低 206.89 已跌破 208、奥普特最低 140.20 触到中枢下沿 140，
但第二条件「日线有力度底分型」都没出——<b>条件到位 ≠ 买点</b>；兆易盘中触跌停、模塑距 14.95 差 0.11 元，
都是「还没止跌」。老师给的潜在强势案例<b>只给筛选逻辑不给标的</b>，不推荐直接买入，仍要等方法买点。</p>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/300364_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688686_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603662_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">

<h2>四、被套怎么办（老师原话，可直接执行）</h2>
<div class="box box-g">
① <b>仓位轻、被套</b>：手不要软，可结合反弹用部分仓位<b>高抛低吸倒差价</b>；
② <b>仓位重、被套</b>：<b>不硬顶、也不额外加仓</b>，心态压力大可酌情主动降低部分仓——交易心态不要消极，理清思路；
③ 整体<b>不要着急、不用担心踏空</b>，养成按方法规则操作的习惯；市场弱时做好风控、少动多看，市场强时再找机会。
</div>

<h2>五、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 {sh["low"]:.2f} 是否被二次跌破</b>：跌破 3574.27（60 日低）= 底背驰窗口打开；站回 3623.12 之上才算反抽有效；3750 是远门槛。<br>
② <b>瑞芯微</b>：208 已破，只看<b>日线有力度底分型</b>是否出现并过掉第三根 K 线高点——池内最接近触发的一个。<br>
③ <b>奥普特</b>：140 下沿已触（140.20），同样只等日线底分型。<br>
④ <b>模塑科技</b>：距 14.95 仅 0.11 元，触到且出止跌信号才谈得上方法买点。<br>
⑤ <b>18 日开盘英伟达业绩会</b>：科技（算力/半导体/端侧）开盘怎么走直接决定要不要等回抽；同时提醒——<b>市场一旦止跌，防守方向反而会面临回调</b>，今天红盘的银行家电不要追。
</div>

<h2>六、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-bear" if t in ("偏乐观","实为普跌") else "tag-none"}">{t}</span></td></tr>' for a, b, t in DEVS)}
</table>
<p class="meta">指数跌幅、板块强弱、玄学链补跌、传媒回调位置等其余判据<b>与实测一致</b>，不再逐条列出。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-16 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>同花顺日线 140 根（今日那根用收盘快照补齐）+ 新浪收盘快照；两市成交额＝沪市上证指数额＋深市深证成指额（同花顺口径，与新浪逐分一致）；全 A 涨跌家数取新浪 5578 只收盘；涨停/跌停用东财池；板块为自建篮子均值。缠论定性按老师口径引用，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261116.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
