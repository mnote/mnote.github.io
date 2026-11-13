"""生成 2026-11-12 都业华《高级班》午评纪要 HTML（白底 · 盘中版）

⛔ 2026-11-11 禁令：只用日线 + 实时快照，不调用 1/15 分钟 K 线、不调用 czsc。
📏 2026-11-12 篇幅硬约束：正文 ≤ 2000 字、表格 ≤ 4 张，K 线图保留不计字数。
数据：reports/duyiehua-20261112/data_20261112.json
输出：~/workspace/mnote.github.io/2026-11-12-都业华-高级班午评纪要.html
"""
import json
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261112"
D = json.loads((RPT / "data_20261112.json").read_text(encoding="utf-8"))

IDX, MKT, BASKET, QUOTES = D["index"], D["prev_market"], D["basket"], D["quotes"]
ZT = D.get("zt_pool", {})
SNAP_HM = D["snapshot_time"][-5:]

OUT = REPO / "2026-11-12-都业华-高级班午评纪要.html"
TITLE_SUMMARY = "算力放量临近压力，热点杂乱"
TITLE_FULL = f"DYH 午评 - 2026-11-12（周四 {TITLE_SUMMARY}）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--panel2:#f1f3f6;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;--neutral:#d97706;--neutbg:#fef3c7;
    --none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
  .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
  h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:28px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
  p{margin:6px 0}a{color:var(--accent);text-decoration:none}
  .meta{color:var(--muted);font-size:12px}.meta span{margin-right:12px}
  .hero{background:linear-gradient(135deg,#f0f9ff,#f8fbff);border:1px solid #7dd3fc;border-radius:12px;padding:18px 22px;margin-bottom:14px}
  .hero h1{color:#0c4a6e}.hero .stance{font-size:14.5px;margin:7px 0 0}
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
  .tag-accent{background:var(--accentbg);color:var(--accent)}
  .chart{width:100%;height:auto;display:block;margin:8px 0 2px;border:1px solid var(--border);border-radius:6px;background:#fff}
  .up{color:var(--up);font-weight:600}.down{color:var(--down);font-weight:600}
  .kn{color:var(--key);font-weight:700;font-variant-numeric:tabular-nums}
  .box{border-radius:8px;padding:8px 12px;margin:8px 0;font-size:13.5px}
  .box-r{background:var(--bearbg)}.box-a{background:var(--accentbg)}.box-g{background:var(--bullbg)}
  .foot{margin-top:32px;padding-top:14px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
  .vol{color:var(--neutral);font-weight:600}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "flat")


def pct(v):
    return f"{v:+.2f}%"


def q(n):
    for r in QUOTES:
        if r["名称"] == n:
            return r
    return {}


def sp(n):
    r = q(n)
    if not r:
        return "—"
    return f'<span class="{cls(r["涨跌幅%"])}">{r["现价"]:.2f} ({pct(r["涨跌幅%"])})</span>'


sh, sz, cy, kc = IDX["上证指数"], IDX["深证成指"], IDX["创业板指"], IDX["科创50"]
amt_now = round(sh["amount_yi"] + sz["amount_yi"], 1)
amt_prev = round(MKT["sh_amount_yi"] + MKT["sz_amount_yi"], 1)
amt_ratio = round(amt_now / amt_prev * 100, 1)
B = BASKET

bask_rows = "".join(
    f'<tr><td>{k}</td><td class="num {cls(v["avg_pct"])}">{v["avg_pct"]:+.2f}%</td>'
    f'<td class="num">{v["up"]}/{v["n"]}</td></tr>'
    for k, v in B.items())

ROWS = [
    ("药明康德", "对称震荡，等共振",
     f'振幅大；凯莱英 {pct(q("凯莱英")["涨跌幅%"])} 同步',
     '<span class="tag tag-none">观望</span>'),
    ("中国船舶", "高开，仍没止跌",
     f'高开 {q("中国船舶")["开盘"]:.2f}，未破昨收，无买点',
     '<span class="tag tag-none">不操作</span>'),
    ("瑞芯微", "倾向拉回小中枢震荡",
     f'下午续跌至 {q("瑞芯微")["现价"]:.2f}，未拉回',
     '<span class="tag tag-neutral">等拉回</span>'),
    ("伊利股份", "倾向破 30.46 再拉回",
     f'最低 {q("伊利股份")["最低"]:.2f}，<b>差 0.04 未破</b>；无有力度底分型',
     '<span class="tag tag-none">等条件</span>'),
    ("中文在线", "等破 30.38 出三买",
     f'最高 {q("中文在线")["最高"]:.2f}，离 30.38 更远',
     '<span class="tag tag-none">等突破</span>'),
    ("海天瑞声", "等对称震荡形成",
     f'{pct(q("海天瑞声")["涨跌幅%"])}，最低 {q("海天瑞声")["最低"]:.2f}，远未形成',
     '<span class="tag tag-bear">不追</span>'),
    ("奥普特", "等破 186.8 或回调 140",
     f'最高 {q("奥普特")["最高"]:.2f} 未触；最低 {q("奥普特")["最低"]:.2f}，距 140 还有 '
     f'{round((140 / q("奥普特")["最低"] - 1) * 100, 1)}%',
     '<span class="tag tag-accent">新增观察</span>'),
    ("柯力传感", "等顶分型调整充分（53）",
     f'最低 {q("柯力传感")["最低"]:.2f}，<b>未到 53</b>',
     '<span class="tag tag-accent">新增观察</span>'),
    ("兆易创新", "分型确认中，临近压力",
     f'冲高 {q("兆易创新")["最高"]:.2f} 回落；量达昨日 {q("兆易创新")["昨日量比(今累计/昨全天)"]:.0f}%',
     '<span class="tag tag-none">不追</span>'),
    ("云铝股份", "不满足方法条件",
     f'缩量，仅昨日 {q("云铝股份")["昨日量比(今累计/昨全天)"]:.0f}%',
     '<span class="tag tag-none">不操作</span>'),
    ("模塑科技", "等顶分型形成",
     f'最高 {q("模塑科技")["最高"]:.2f} &lt; 昨收，<b>确未新高</b>',
     '<span class="tag tag-none">等形成</span>'),
    ("汉威科技", "顶分型已出，下午留意",
     f'<b>下午 {pct(q("汉威科技")["涨跌幅%"])}，最低 {q("汉威科技")["最低"]:.2f}</b> → 兑现',
     '<span class="tag tag-bear">警示中</span>'),
    ("长盈精密", "等破 32.08",
     f'最高 {q("长盈精密")["最高"]:.2f}，离 32.08 尚远',
     '<span class="tag tag-none">等突破</span>'),
]
body_rows = ""
for nm, stance, meas, act in ROWS:
    body_rows += (f'<tr><td><b>{nm}</b></td><td class="num">{sp(nm)}</td>'
                  f'<td>{stance}</td><td>{meas}</td><td>{act}</td></tr>')

CHARTS = "".join(f'<img class="chart" src="charts/{c}_DY_20261112.png">' for c in
                 ["000001_SH", "399006_SZ", "603259_SH", "600150_SH", "603893_SH", "600887_SH",
                  "300364_SZ", "688787_SH", "688686_SH", "603662_SH", "603986_SH", "300007_SZ",
                  "300115_SZ"])

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE_FULL}</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE_FULL}</h1>
  <div class="meta"><span>⏱ 盘中版 · 数据截至 {SNAP_HM}</span><span>📡 都业华 11/12 午评 + Tushare 日线 + 新浪快照</span></div>
  <p class="stance"><b>结论：</b>偏弱震荡，<b>上证 {sh['price']:.2f}（{pct(sh['pct'])}）、创业板 {pct(cy['pct'])}、科创50 {pct(kc['pct'])}</b>，<b>3750 未破仍弱势</b>，两市放量至昨日全天 {amt_ratio}%。<b>核心警示：半导体今日量已赶上昨日全天，临近压力，不追</b>。<b>算力硬件 {B['算力硬件']['avg_pct']:+.2f}% 仍强，人形机器人 {B['人形机器人']['avg_pct']:+.2f}%、AI 视频 {B['AI视频/传媒']['avg_pct']:+.2f}% 调整</b>。<b>总仓 ≤4 成；13 只标的全无买点。</b></p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数</div><div class="val down">{pct(sh['pct'])}</div><div class="sub">{sh['price']:.2f} · 3750 未破</div></div>
  <div class="kpi"><div class="label">创业板 / 科创50</div><div class="val"><span class="down">{pct(cy['pct'])}</span> / <span class="up">{pct(kc['pct'])}</span></div><div class="sub">创业板冲高回落</div></div>
  <div class="kpi"><div class="label">两市成交额（{SNAP_HM}）</div><div class="val vol">{amt_now} 亿</div><div class="sub">昨日全天 {amt_ratio}% · 放量</div></div>
  <div class="kpi"><div class="label">盘中涨停 / 热点</div><div class="val">{ZT.get('n', '—')} 只</div><div class="sub">散落十余行业</div></div>
</div>

<h2>一、指数：偏弱震荡，3750 未破</h2>
<p>上证 {sh['price']:.2f}（高 {sh['high']:.2f} 低 {sh['low']:.2f}），<b>3750 未破，老师「仍看成弱势」成立</b>。分化在成长端内部：<b>科创50 {pct(kc['pct'])}</b>（半导体带动），但<b>创业板 {pct(cy['pct'])}</b>——最高 {cy['high']:.2f} 回落至 {cy['price']:.2f}（<b>-{((cy['high']-cy['price'])/cy['high']*100):.1f}%</b>）。两市成交额 {amt_now} 亿 = 昨日全天 {amt_prev} 亿的 {amt_ratio}%，<b>放量确认</b>。</p>
<img class="chart" src="charts/000001_SH_DY_20261112.png">
<img class="chart" src="charts/399006_SZ_DY_20261112.png">

<h2>二、板块：算力仍强，机器人与 AI 视频退潮</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>均值</th><th>涨/样本</th></tr>
  {bask_rows}
</table>
<div class="box box-a"><b>老师描述逐条成立：</b>① 算力硬件 {B['算力硬件']['avg_pct']:+.2f}%、半导体 {B['半导体']['avg_pct']:+.2f}%、CPO {B['CPO/光模块']['avg_pct']:+.2f}% →「仍较强」；② 防守/消费 {B['防守/消费']['avg_pct']:+.2f}%（7/10 涨）→「防守也有动作」；③ <b>人形机器人 {B['人形机器人']['avg_pct']:+.2f}%（18 只 0 涨）、AI 视频 {B['AI视频/传媒']['avg_pct']:+.2f}%</b> →「调整」。涨停 {ZT.get('n', '—')} 只散落十余行业 →<b>「热点杂乱」成立</b>。</div>
<div class="box box-r"><b>「半导体上午放量赶上昨日全天」成立：</b>8 只样本今日 {SNAP_HM} 累计 <b>302.3 亿</b> vs 昨日全天 <b>289.1 亿</b> = <b>104.6%</b>（中芯 130.6%、北方华创 120.2% 已单独超昨日全天）；此为 {SNAP_HM} 累计值，上午只会更低。<b>放量上冲 + 临近压力 = 冲不过即短期高点，不追。</b></div>

<h2>三、中线 8 + 短线 5：全部无买点</h2>
<table>
  <tr><th>标的</th><th>现价</th><th>老师定性</th><th>实测印证（日线）</th><th>动作</th></tr>
  {body_rows}
</table>
<img class="chart" src="charts/603259_SH_DY_20261112.png"><img class="chart" src="charts/600150_SH_DY_20261112.png">
<img class="chart" src="charts/603893_SH_DY_20261112.png"><img class="chart" src="charts/600887_SH_DY_20261112.png">
<img class="chart" src="charts/300364_SZ_DY_20261112.png"><img class="chart" src="charts/688787_SH_DY_20261112.png">
<img class="chart" src="charts/688686_SH_DY_20261112.png"><img class="chart" src="charts/603662_SH_DY_20261112.png">
<img class="chart" src="charts/603986_SH_DY_20261112.png"><img class="chart" src="charts/300007_SZ_DY_20261112.png">
<img class="chart" src="charts/300115_SZ_DY_20261112.png">

<h2>四、下午盯什么（4 条可验证条件）</h2>
<div class="box box-g">
① <b>半导体能否消化压力</b>：量超昨日全天 4.6%，下午缩量滞涨 → 短期高点，不追。<br>
② <b>3750 与全A 顶背驰</b>：3750 未破仍弱势；全A 顶背驰本机无数据源，需看老师系统。<br>
③ <b>算力硬件能否延续</b>：+{B['算力硬件']['avg_pct']:.2f}% 但 11 只仅 6 涨，强度与扩散度不匹配，掉头则短期高点。<br>
④ <b>汉威科技下午方向</b>：顶分型已出且 {pct(q('汉威科技')['涨跌幅%'])}，继续往下 → 短期出高点；模塑科技顶分型未形成。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>项目 / 老师原文</th><th>实测</th><th>判定</th></tr>
  <tr><td>乐鑫科技「容易拉回」</td><td>{sp('乐鑫科技')} 续跌</td><td><span class="tag tag-bear">相反</span></td></tr>
  <tr><td>海天瑞声 / 奥普特「等结构」</td><td>{sp('海天瑞声')}、{sp('奥普特')}；奥普特距 140 还有 {round((140 / q('奥普特')['最低'] - 1) * 100, 1)}%</td><td><span class="tag tag-neutral">偏弱</span></td></tr>
  <tr><td>瑞芯微「倾向拉回」</td><td>下午续跌 {pct(q('瑞芯微')['涨跌幅%'])}</td><td><span class="tag tag-neutral">待观察</span></td></tr>
  <tr><td>全A 顶背驰「下午跟踪」</td><td>本机无 881001 数据源，<b>无法核验</b></td><td><span class="tag tag-none">无法核验</span></td></tr>
</table>

<div class="foot">
  <p>原文来源：都业华《高级班》2026-11-12 午评，执业编号 A0400626100004。<b>以上内容仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b>本纪要为原文整理 + 独立数据核验，不构成投资建议。<b>口径：</b>{SNAP_HM} 实时快照，末根 K 线未完成、成交量为盘中累计；板块为自建篮子测算；缠论定性按「老师口径」引用，不做分钟级复算。</p>
</div>

</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print("written:", OUT, len(HTML), "bytes")
