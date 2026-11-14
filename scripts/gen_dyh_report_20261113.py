"""都业华 2026-11-13 收评纪要 HTML（白底 · 收盘版）
篇幅：正文 ≤2000 字 / 表格 ≤4 张（K 线图不计）
输出：html/duyiehua-20261113.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261113"
D = json.loads((RPT / "data_20261113.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
BR = json.loads((REPO / "charts/_breadth_20261113.json").read_text())
POOL = json.loads((REPO / "charts/_em_pools_20261113.json").read_text())
T, Y = BR["20261113"], BR["20261112"]

TITLE = "DYH 收评 - 2026-11-13（周五 缩量阴跌，跌停 33 家）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--panel2:#f1f3f6;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;--neutral:#d97706;--neutbg:#fef3c7;
    --none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
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
  th{background:var(--panel2);font-weight:600;color:var(--muted);font-size:11.5px}
  tr:hover{background:var(--panel)}td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
  .tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:10.5px;font-weight:500;white-space:nowrap}
  .tag-bull{background:var(--bullbg);color:var(--bull)}.tag-bear{background:var(--bearbg);color:var(--bear)}
  .tag-neutral{background:var(--neutbg);color:var(--neutral)}.tag-none{background:var(--nonebg);color:var(--none)}
  .chart{width:100%;height:auto;display:block;margin:8px 0 2px;border:1px solid var(--border);border-radius:6px;background:#fff}
  .up{color:var(--up);font-weight:600}.down{color:var(--down);font-weight:600}
  .kn{color:var(--key);font-weight:700;font-variant-numeric:tabular-nums}
  .box{border-radius:8px;padding:8px 12px;margin:8px 0;font-size:13.5px}
  .box-r{background:var(--bearbg)}.box-a{background:var(--accentbg)}.box-g{background:var(--bullbg)}
  .foot{margin-top:30px;padding-top:12px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
  .vol{color:var(--neutral);font-weight:600}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "")


def px(name):
    s = ST[name]
    return f'<span class="{cls(s["pct"])}">{s["close"]:.2f} ({s["pct"]:+.2f}%)</span>'


def bkinline(name):
    b = BK[name]
    return f'<span class="{cls(b["avg_pct"])}">{b["avg_pct"]:+.2f}%</span>'


sh = IX["上证指数"]
cy = IX["创业板指"]
kc = IX["科创50"]
amt, amt_prev = T["amount_yi"], Y["amount_yi"]
amt_chg = (amt / amt_prev - 1) * 100

ROWS = [
    ("药明康德", "大医药", "无买点 · 窄幅震荡 · 等充分震荡后破 157.8 出 15 分钟三买",
     "157.8", f'最高 {ST["药明康德"]["high"]:.2f}，差 {157.8-ST["药明康德"]["high"]:.2f}（{157.8/ST["药明康德"]["high"]*100-100:.1f}%）', "等"),
    ("中国船舶", "防御", "无买点 · 15 分钟下跌中枢延伸 · 未止跌，等翻压力后类二买共振",
     "—", "最低 33.80 再破 11/12 低 33.92，结构未修", "观察"),
    ("瑞芯微", "端侧AI", "无买点 · 日线前高顶在上沿不追 · 激进等中枢下沿止跌＋日线有力底分型",
     "前高 237.37", f'最高 {ST["瑞芯微"]["high"]:.2f}，差 {237.37-ST["瑞芯微"]["high"]:.2f}，未破前高', "不追"),
    ("伊利股份", "大消费", "无买点 · 逆势创新高但位置不一定拿得住，不建议追涨",
     "60日高 31.75", f'最高 {ST["伊利股份"]["high"]:.2f} = 60 日新高，量 1.35 倍', "不追"),
    ("中文在线", "AI视频", "无买点 · 复杂震荡不抓回调 · 稳健等破 30.38 出三买",
     "30.38", f'最高 {ST["中文在线"]["high"]:.2f}，差 {30.38-ST["中文在线"]["high"]:.2f}', "等"),
    ("海天瑞声", "机器人", "无买点 · 月线中枢略跌破 · 热度好＋个股止跌再谈",
     "—", f'最低 {ST["海天瑞声"]["low"]:.2f}，破 11/12 低 121.31', "等"),
    ("奥普特", "机器视觉", "无买点 · 日线顶分型回调至下沿附近 · 破 186.8 三买",
     "186.8 / 下沿 140", f'最低 {ST["奥普特"]["low"]:.2f}，距 140 还差 {ST["奥普特"]["low"]/140*100-100:.1f}%', "等"),
    ("柯力传感", "六维传感器", "无买点 · 短线调整缩量 · 等止跌＋日线有力底分型",
     "53", f'最低 {ST["柯力传感"]["low"]:.2f}，未破 53', "等"),
    ("兆易创新", "存储芯片", "无买点 · 短线下跌延续 · 观察创新低后底背驰",
     "前低 237.28", f'最低 {ST["兆易创新"]["low"]:.2f}，差 {ST["兆易创新"]["low"]-237.28:.2f} 未创新低', "等"),
    ("云铝股份", "非热点", "走势略破位 · <b>老师直接剔除跟踪</b>",
     "—", f'最低 {ST["云铝股份"]["low"]:.2f} = 60 日新低', "剔除"),
    ("模塑科技", "人形机器人", "无买点 · 盘中涨停不追 · 等回调 14.95 止跌或破 17.69 三买",
     "14.95 / 17.69", f'最高 {ST["模塑科技"]["high"]:.2f} = 涨停价（触板未封），量 1.36 倍', "不追"),
    ("长盈精密", "人形机器人", "无买点 · 类二买雏形 · 稳健等破 32.08 出三买",
     "32.08", f'最高 {ST["长盈精密"]["high"]:.2f}，差 {32.08-ST["长盈精密"]["high"]:.2f}', "等"),
]

BKROWS = [
    ("银行", "老师：今日创出新高，适度关注", "+1.23%，5 只样本全红；<b>个股最高价均未破 60 日高</b>（工行 8.86 vs 8.88）"),
    ("电力/高股息", "老师：类似电力方向也可观察", "+0.95%，5 只样本全红，与银行同步，红利是当日唯一成体系的方向"),
    ("人形机器人", "老师：二类热点，内部个股分化", "-0.12%，3 涨 6 跌；模塑触板 +6.54%，鸣志 -1.97%、兆威 -2.69%"),
    ("AI视频/传媒", "老师：能否存活待观察", "-0.17%，2 涨 5 跌；光线 +5.31% 创 60 日新高，中文在线 +2.21%，上海电影 -2.25%"),
    ("半导体", "老师：回落不意外，上方压力没消化", "-1.23%，2 涨 4 跌；兆易 -4.96% 领跌，寒武纪 +0.60%、海光 +0.46%"),
    ("算力/CPO", "老师本期<b>未提</b>", "-9.04%，0 涨 5 跌；沪电 -10.00%、胜宏 -10.57% 双跌停，当日最大杀跌源"),
    ("玄学链·东方字样", "老师：跌幅较大，掉下热点榜、走势垮掉", "-1.49%，2 涨 4 跌；<b>东方中科涨停 +9.98%</b>，东方通信 -7.39%、东方创业 -7.37%"),
]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收盘版 · 日线数据截至 2026-11-13 收盘</div>
  <p class="stance"><b>结论：弱势延续，不动为上。</b>上证 <b>{sh['close']:.2f}（{sh['pct']:+.2f}%）</b>，盘中新低 <b>{sh['low']:.2f}</b> 破 11/12 低 3647.44，3750 仍差 {(3750/sh['high']-1)*100:.1f}% 未触；创业板 <span class="down">{cy['pct']:+.2f}%</span>、科创50 <span class="down">{kc['pct']:+.2f}%</span>。成交 <span class="vol">{amt:,.0f} 亿</span>（同比 <span class="down">{amt_chg:+.1f}%</span>），<span class="down">{T['down']}</span> 家下跌、跌停 {POOL['dt']['tc']} 家（昨 5）。温度 25 度，一类无、二类仅人形机器人。<b>总仓 ≤4 成、不追涨；12 只标的依旧全无买点，亮的只有银行、电力。</b></p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3750 未触</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 新低 {sh['low']:.2f}</div></div>
  <div class="kpi"><div class="label">两市成交额 · 环比</div><div class="val vol">{amt:,.0f} 亿</div><div class="sub down">{amt_chg:+.1f}%（昨 {amt_prev:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{T['up']}</span> / <span class="down">{T['down']}</span></div><div class="sub">平 {T['flat']} · 共 {T['n']}</div></div>
  <div class="kpi"><div class="label">涨停 / 跌停（东财池）</div><div class="val">{POOL['zt']['tc']} / <span class="down">{POOL['dt']['tc']}</span></div><div class="sub">炸板 {POOL['zb']['tc']} · 跌超 9.9% 共 {T['limit_down']} 家</div></div>
</div>

<h2>一、指数：新低已出，等底背驰</h2>
<p>老师说 15 分钟下跌中枢延伸、方向未选：<b>向上要破 <span class="kn">3750</span> 后回抽确认三买，向下要创新低出底背驰</b>。按日线触达口径——<b>向上</b>今日最高 {sh['high']:.2f}，距 3750 差 {3750-sh['high']:.2f} 点（{(3750/sh['high']-1)*100:.1f}%），门槛根本没摸到；<b>向下</b>最低 {sh['low']:.2f} 已破 11/12 低 3647.44、11/11 低 3650.31，<b>「创新低」条件成立</b>，接下来只看底背驰是否出现。</p>
<p>高开 {sh['open']:.2f} 一路走低收 {sh['close']:.2f}，收在全天低位区；创业板 <span class="down">{cy['pct']:+.2f}%</span> 收 {cy['close']:.2f}，距 60 日低 {cy['lo60']:.2f} 只剩 {(cy['close']/cy['lo60']-1)*100:.1f}%。<b>缩量 {amt_chg:+.1f}% 却砸出 {POOL['dt']['tc']} 家跌停、{T['limit_down']} 家跌超 9.9%</b> —— 这不是「沉闷」，是杀跌，人气差的定性成立且更重。</p>
<img class="chart" src="../charts/000001_SH_DY_20261113.png">
<img class="chart" src="../charts/399006_SZ_DY_20261113.png">

<h2>二、板块：只有红利在涨</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值、涨跌家数、内部）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① 红的只有银行、电力，且是缩量下的防守抱团 —— 老师「高股息适度关注、不追买、结合回调找止跌」的分寸正好；② <b>算力/CPO -9.04% 是当日真正的杀跌源</b>（沪电、胜宏双跌停），老师仅说半导体回落、没点算力，这是遗漏；③ 人形机器人 -0.12% 的均值掩盖了分化：模塑触板、鸣志兆威下跌，正对应老师「板块内个股分化、别着急追买」。</p>

<h2>三、12 只标的：全无买点，关键位一个没触发</h2>
<table>
  <tr><th>标的 / 题材</th><th>收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a in ("不追","剔除") else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_20261113.png">
<img class="chart" src="../charts/600150_SH_DY_20261113.png">
<img class="chart" src="../charts/603893_SH_DY_20261113.png">
<img class="chart" src="../charts/600887_SH_DY_20261113.png">
<img class="chart" src="../charts/300364_SZ_DY_20261113.png">
<img class="chart" src="../charts/688787_SH_DY_20261113.png">
<img class="chart" src="../charts/688686_SH_DY_20261113.png">
<img class="chart" src="../charts/603662_SH_DY_20261113.png">
<img class="chart" src="../charts/603986_SH_DY_20261113.png">
<img class="chart" src="../charts/000807_SZ_DY_20261113.png">
<img class="chart" src="../charts/000700_SZ_DY_20261113.png">
<img class="chart" src="../charts/300115_SZ_DY_20261113.png">

<h2>四、明日盯什么</h2>
<div class="box box-g">
① 上证 {sh['low']:.2f} 新低后<b>底背驰是否出现</b>；向上唯一门槛仍是 <span class="kn">3750</span>。<br>
② 跌停能否从 {POOL['dt']['tc']} 家收敛（&lt;10 家 = 杀跌减弱），跌超 9.9% 家数同步看。<br>
③ 算力/CPO 单日 -9% 后是否续跌：沪电、胜宏两个跌停决定成长端方向。<br>
④ 红利（银行/电力）续强说明风险偏好仍低，是「不动」的又一票。<br>
⑤ 挂单线：药明 157.8、中文在线 30.38、奥普特 186.8、模塑 14.95/17.69、长盈 32.08、兆易 237.28，触达才动。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  <tr><td>「银行板块今日创出新高」</td><td>5 只成分最高价均未破 60 日高，工行 8.86 vs 8.88（差 0.02）</td><td><span class="tag tag-none">个股价无法复现</span></td></tr>
  <tr><td>「玄学链走势垮掉」</td><td>样本 2 涨 4 跌、均值 -1.49%，但<b>东方中科涨停 +9.98%</b></td><td><span class="tag tag-neutral">方向对、内部分化</span></td></tr>
  <tr><td>板块只提半导体回落、未提算力</td><td>算力/CPO -9.04%（0/5），沪电、胜宏双跌停</td><td><span class="tag tag-bear">遗漏最大跌幅源</span></td></tr>
  <tr><td>「市场运行沉闷」</td><td>缩量 {amt_chg:+.1f}% 成立，但跌停 {POOL['dt']['tc']} 家（昨 5）</td><td><span class="tag tag-bear">是杀跌非横盘</span></td></tr>
  <tr><td>「15 分钟下跌中枢延伸」</td><td>无分钟级数据（用户禁令），不做复算</td><td><span class="tag tag-none">按老师口径引用</span></td></tr>
</table>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-13 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>东财日线（前复权）＋ Tushare 全 A 快照；板块为自建篮子均值（成分股逐一在表内列出）；涨跌停用东财池（不含 ST／北交所），「跌超 9.9%」为 Tushare 全 A 统计；缠论定性按老师口径，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""
out = REPO / "html/duyiehua-20261113.html"
# 表格移动端适配（横向滚动 + 首列粘滞 + 溢出提示）：统一由 fix_mobile_tables 注入
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
