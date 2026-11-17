"""都业华 2026-11-17 收评（高级班）· 纪要 HTML（白底 · 收盘版）

⛔ 用户 2026-11-11 禁令：只用日线 + 收盘快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261117.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261117"
D = json.loads((RPT / "data_20261117_close.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261117_close.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261117C"

TITLE = "DYH 收评 - 2026-11-17（周二 微破新低，底背驰未成形）"

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


sh, cy, kc, sz, hs = (IX["上证指数_snap"], IX["创业板指_snap"], IX["科创50_snap"],
                      IX["深证成指_snap"], IX["沪深300_snap"])
amt = D["amount"]
prev_amt = (D["prev_day"]["上证指数"]["20261116"]["amt_yi"]
            + D["prev_day"]["深证成指"]["20261116"]["amt_yi"])
amt_g = (amt["total_yi"] / prev_amt - 1) * 100

# 关键位核对（日线触达判据）
NEW_LOW_GAP = 3586.57 - sh["low"]          # 相对 11/16 低点的破位幅度（点）
TO3623 = 3623.12 - sh["high"]              # 距见底确认位
CY_GAP = (2263.74 / 2308.90 - 1) * 100     # 创业板相对 11/16 低点


def c(v):
    return "up" if v > 0 else ("down" if v < 0 else "")


def bkv(name):
    v = BK[name]["avg_pct"]
    return '<span class="' + c(v) + '">' + format(v, "+.2f") + '%</span>'


BKROWS = [
    ("半导体", "有点动作，上方压力没突破，横盘震荡；1 分钟底背驰导致的反弹，结构没止跌",
     f'{bkv("半导体")}，3 涨 3 跌；中芯 +6.59%、北方华创 +4.09%，'
     f'但海光 -3.93%、兆易 -3.88%、瑞芯微 -1.74%'),
    ("算力/CPO", "前期强势股补跌",
     f'<b>{bkv("算力/CPO")}，0 涨 5 跌</b>；新易盛 -4.08%、中际旭创 -3.90%、胜宏 -1.96%'),
    ("AI视频/传媒", "走势垮掉，板块重新洗牌",
     f'<b>{bkv("AI视频/传媒")}，0 涨 7 跌</b>；华策 -13.34%、中文在线 -9.89%、'
     f'捷成 -8.23%、上海电影 -7.83%；<b>跌停池影视院线 5 家</b>'),
    ("人形机器人", "走势垮掉",
     f'<b>{bkv("人形机器人")}，0 涨 9 跌</b>；兆威跌停 -10.00%、长盈 -9.30%、'
     f'北特 -6.45%、绿的谐波 -4.24%'),
    ("银行", "高股息红利可持续跟踪，不建议追涨",
     f'{bkv("银行")}，<b>5 涨 0 跌</b>；建行 +0.33%、兴业 +0.30%、农行 +0.26%'),
    ("电力/高股息", "同上",
     f'{bkv("电力/高股息")}，4 涨 1 跌；川投 +0.98%、长电 +0.36%、中国核电 -0.61%'),
    ("煤炭/石油", "同上（板块内部分化）",
     f'{bkv("煤炭/石油")}，1 涨 4 跌；石化 +0.86%，中海油 -2.91%、中石油 -0.56%'),
]

ROWS = [
    ("药明康德", "大医药", "中线", "无买点 · 等突破 157.8 出 15 分钟三买；或日线底分型 + 收盘站上 148",
     "157.8 / 148", f'最高 146.80，距 157.8 差 10.99、距 148 差 1.20；逆势 +1.15%，池内最抗跌', "等"),
    ("中国船舶", "防御", "中线", "无买点 · 等翻过 36.75 后出 15 分钟底分型回抽",
     "36.75", f'最高 34.31，距 36.75 差 2.44；低 33.38 破昨低，未止跌', "等"),
    ("瑞芯微", "端侧AI", "中线", "无买点 · 激进等站住 220.7；稳健等下上下共振中枢",
     "220.7", f'最高 212.38，距 220.7 差 8.32；低 201.67 破昨低、略破位', "等"),
    ("伊利股份", "大消费", "中线", "无买点 · 与指数节奏相反，不追涨；持仓看顶背驰",
     "—", f'最高 32.44 <b>创 60 日新高</b>，收 32.41（+0.65%）', "不追"),
    ("中文在线", "AI视频", "剔除", "无买点 · 板块热度降、震荡复杂 → <b>中线剔除</b>",
     "—", f'收 23.68（<b>-9.89%</b>），低 23.40 <b>跌破 11/09 低 25.65</b>', "剔除"),
    ("海天瑞声", "机器人", "中线", "无买点 · 等止跌 + 15 分钟二买；或小级别共振中枢",
     "—", f'收 93.35（<b>-12.06%</b>），低 91.99，对称震荡已破位', "等"),
    ("奥普特", "机器视觉", "剔除", "补跌、结构破位 → <b>中线剔除</b>",
     "—", f'收 129.73（<b>-8.62%</b>），低 127.52 <b>破中枢下沿 140 达 12.48 元</b>', "剔除"),
    ("柯力传感", "六维传感器", "剔除", "转弱防二卖 → <b>中线剔除</b>",
     "—", f'收 49.27（<b>-6.19%</b>），低 48.72 破 53 支撑 4.28 元', "剔除"),
    ("兆易创新", "存储", "短线", "无买点 · 233 未收复，等日线有力度底分型",
     "233", f'最高 224.60，距 233 差 8.40；<b>低 212.00 创 60 日新低</b>', "等"),
    ("模塑科技", "机器人", "短线", "无买点 · 卡 14.95 没止跌，守不住不再跟",
     "14.95", f'低 14.67 <b>破 14.95 共 0.28 元</b>，收 14.90（-1.91%）', "等"),
    ("长盈精密", "机器人", "短线", "无买点 · 看明日能否守住，守住再等日线底分型",
     "—", f'收 24.18（<b>-9.30%</b>），低 23.86 <b>已破 11/02 低 24.57</b>', "等"),
]

DEVS = [
    ("「半导体今日有点动作，但上方压力没有突破」",
     f'篮子 {bkv("半导体")}（3 涨 3 跌）；内部极端分化 —— 中芯 +6.59%、北方华创 +4.09% vs 海光 -3.93%、兆易 -3.88%',
     "一致，但分化远大于「有点动作」"),
    ("「考虑跌破下沿幅度不大，因此底背驰没形成」",
     f'仅对上证成立：低 {sh["low"]:.2f} 只破 11/16 低 {NEW_LOW_GAP:.2f} 点（-0.59%）；'
     f'创业板低 2263.74 破前低 <b>{CY_GAP:+.2f}%</b>、深成指与沪深300 同样创 60 日新低',
     "上证口径窄"),
    ("「长盈精密短线延续下跌，还没有破位」",
     f'低 23.86 <b>已破 11/02 低 24.57</b>、破 11/16 低 26.43 达 9.7%，创 20 日新低',
     "偏乐观"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收评版 · 数据截至 2026-11-17 收盘</div>
  <p class="stance"><b>结论：新低破了但幅度不够，底背驰没形成，走势仍定性为下跌中枢震荡。仓位上限 4 成，轻仓、降频、不追涨。</b>
  上证 <span class="down">{sh['pct']:+.2f}%</span> 收 {sh['close']:.2f}，最低 <b>{sh['low']:.2f} 创 60 日新低</b>，但只比 11/16 低点多破 {NEW_LOW_GAP:.2f} 点（-0.59%），
  「跌破下沿幅度不大」成立 → 不能判底背驰。<b>市场温度 20 度，一类/二类热点双双为空</b>，
  人形机器人 <span class="down">{BK['人形机器人']['avg_pct']:+.2f}%</span>、AI视频传媒 <span class="down">{BK['AI视频/传媒']['avg_pct']:+.2f}%</span> 全线垮掉，
  板块重新洗牌。<b>11 只标的全部无买点</b>；中文在线、奥普特、柯力传感三只<b>中线剔除</b>，跟踪池 11 → 8 只。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3623 未到</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f} 创 60 日新低</div></div>
  <div class="kpi"><div class="label">科创50 / 创业板指</div><div class="val"><span class="up">{kc['pct']:+.2f}%</span> / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">深成 {sz['pct']:+.2f}% · 沪深300 {hs['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额</div><div class="val vol">{amt['total_yi']:,.0f} 亿</div><div class="sub down">{amt_g:+.2f}%（11/16 {prev_amt:,.0f} 亿）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 跌超 5% {BR['down_5']}</div></div>
</div>

<h2>一、指数：新低成立，但没走出底背驰</h2>
<p>三个判据逐条对：① <b>向下创新低成立</b> —— 最低 {sh['low']:.2f}，破 11/16 低 3586.57 共 {NEW_LOW_GAP:.2f} 点（<b>-0.59%</b>），同时是 60 日低；
② <b>「幅度不大」也成立</b> —— 只擦破一层皮，按老师判据这不足以构成底背驰，所以今天只能定性为<b>下跌中枢震荡</b>，不是见底；
③ <b>向上差得远</b> —— 最高 3604.98，距见底确认位 3623.12 差 {TO3623:.2f} 点（+1.07%），3750 差 4.62%，「突破后回抽确认」一步都没走。</p>
<p>剧本只有两条：<b>震荡后再向下破结实 → 抓底背驰的止跌机会；直接拉上去 → 因跌幅大，动态观察后小仓位尝试</b>，都不是现在动手。
结构上两条腿不同步：科创50 <span class="up">{kc['pct']:+.2f}%</span> 逆势翻红（中芯 +6.59%），创业板 <span class="down">{cy['pct']:+.2f}%</span> 且低 2263.74 同创 60 日新低。
明早开盘英伟达业绩会，可能扰动科技方向，<b>等实际走势给反应再判断</b>。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：热度 20 度，一类二类全空</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 家数 · 代表股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三件要记的：</b>① 「热点榜无板块上榜」成立 —— 新浪 49 个行业第一只有 +0.30%（开发区），前六全是防守；
② 旧热点全灭（机器人 0涨9跌、传媒 0涨7跌、算力 0涨5跌），<b>跌停 {POOL['dt']['tc']} 家里影视院线 5、汽车零部 4</b>，
涨停仅 {POOL['zt']['tc']} 家且散在 IT服务/环保设备/电子化学，<b>新主线没冒头</b>；
③ 半导体只是「有点动作」：中芯 +6.59%、北方华创 +4.09% 撑着，海光 -3.93%、兆易 -3.88% 拆台，篮子 {BK['半导体']['avg_pct']:+.2f}% 基本平 ——
这波反弹是 1 分钟底背驰，<b>结构没止跌，不追涨</b>。高股息可跟踪但不追，<b>指数一旦止跌反而要防它下跌</b>。</p>

<h2>三、8 只中线 + 3 只短线：全部无买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>类别</th><th>收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td><span class="tag {"tag-none" if t2=="剔除" else "tag-neutral"}">{t2}</span></td><td class="num">{sp(n)["close"]:.2f} <span class="{c(sp(n)["pct"])}">{sp(n)["pct"]:+.2f}%</span></td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="剔除" else ("tag-bull" if a=="不追" else "tag-neutral")}">{a}</span></td></tr>' for n, t, t2, d, k, e, a in ROWS)}
</table>
<p><b>两只单独说：</b>药明康德池内最强（+1.15%），但离 157.8 差 10.99、连 148 都没站上，<b>抗跌 ≠ 买点</b>；
兆易最低 212.00 创 60 日新低、无底背驰。<b>池子 11 → 8 只</b>（-中文在线、奥普特、柯力传感），剔除是把注意力收回来，不是换股信号。</p>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300364_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/688686_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603662_SH_DY_{SUF}.png">

<h2>四、纪律与被套处理（老师原话，可直接执行）</h2>
<div class="box box-g">
① <b>总仓上限 4 成</b>，轻仓、控制出手频率、不追涨，<b>不要放大仓位去抢低点</b>；
② <b>仓位轻被套</b>：手不要软，可结合走势反弹用部分仓位 <b>高抛低吸倒差价</b>；
③ <b>仓位重被套</b>：<b>不硬顶、不额外加仓</b>，心态压力大可酌情主动降低部分仓；
④ 中线分仓 3–5 只，<b>试探性第一笔 = 该股仓位的 5%</b>，跟踪的中线案例没必要个个都操作；
⑤ 别担心踏空 —— 我们无法创造行情，只能跟随：<b>市场弱时做好风控、少动多看</b>。
</div>

<h2>五、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 {sh['low']:.2f} 是否被「破结实」</b>：再破且放量 = 底背驰窗口打开，才是抓止跌的时机；站上 3623.12 才算反抽有效。<br>
② <b>半导体能否连续第二日不回落</b>（中芯、北方华创）：只涨一天是 1 分钟底背驰的反弹，两日站稳才谈结构修复。<br>
③ <b>跌停能否收敛</b>（今日 {POOL['dt']['tc']} 家、影视院线 5）：收敛前不接任何旧热点。<br>
④ <b>长盈精密 23.86 一线</b>：已跌破 11/02 低点，若继续下破就直接放弃关注；守住也要等日线底分型。<br>
⑤ <b>英伟达业绩会</b>（明早开盘前）：科技方向开盘跳空向上冲不过 = 弱势震荡，跳空向下 = 下跌没结束。
</div>

<h2>六、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-bear" if t in ("偏乐观","上证口径窄") else "tag-none"}">{t}</span></td></tr>' for a, b, t in DEVS)}
</table>
<p class="meta">「跌破下沿幅度不大」「创新低」「题材垮掉」「热点榜无板块」「高股息不追涨」「8 只中线全部无买点」等其余判据与实测一致，不再逐条列出；缠论定性（下跌中枢震荡、1 分钟底背驰）按老师口径引用，我方未复算分钟结构。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-17 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！历史案例不代表未来收益。</b></p>
  <p><b>口径：</b>同花顺日线 140 根（今日那根用收盘快照补齐）+ 新浪收盘快照；成交额＝上证指数额＋深证成指额；涨跌家数取新浪 {BR['n']} 只；涨跌停用东财池；板块为自建篮子均值。关键位一律用<b>日线触达判据</b>（当日最高/最低 vs 关键位）。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261117.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
