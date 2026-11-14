"""板块对比页生成器（半导体/GPU/算力/CPO/存储/端侧/人形机器人 各 Top8）。

输入： reports/sector-compare-20261113/data_20261113.json + charts.json
输出： html/sector-20261113.html
表格移动端适配由 fix_mobile_tables.patch_html 统一注入。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/sector-compare-20261113"
D = json.loads((RPT / "data_20261113.json").read_text(encoding="utf-8"))
CH = {c["name"]: c for c in json.loads((RPT / "charts.json").read_text(encoding="utf-8"))}

TITLE = "板块对比 - 2026-11-13（周五 七方向 Top8 对比）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--panel2:#f1f3f6;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;--neutral:#d97706;--neutbg:#fef3c7;
    --none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
  .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
  h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
  h3{font-size:15.5px;margin:20px 0 6px;color:#374151}
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
  .small{font-size:11.5px;color:var(--muted)}
  .rank{display:inline-block;width:18px;height:18px;line-height:18px;text-align:center;border-radius:50%;
    background:var(--panel2);color:var(--muted);font-size:11px;margin-right:5px}
</style>"""

# 每方向：标题 / 口径 / 一句结论 / K 线代表
SECTIONS = [
    ("半导体", "申万二级 801081",
     "市值前 8 有 3 只是 AI 芯片，半导体权重已被算力叙事主导；<b>长鑫 PE 19.5 且缩量</b>是唯一「便宜+回调未破位」的大票，华虹 PE 246 最贵又最弱。",
     "长鑫科技"),
    ("GPU", "AI 加速卡/图形 GPU 手工池",
     "全池均值 -0.21%，<b>唯一没被杀的方向</b>；能拿住的是有业绩的寒武纪、海光（换手 2.55%/1.22%），次新三兄弟换手 13%–22% 且亏损/PE 1171。",
     "寒武纪"),
    ("算力", "申万三级 851024+850703+850822",
     "PE 只有 18–31 却距 60 日高 -37%~-62%，<b>杀拥挤度不是杀业绩</b>；但量比仍 1.1–1.5 放量下跌，抛压没出完。",
     "中际旭创"),
    ("CPO", "光模块/光器件/光纤 手工池",
     "<b>21 只零红盘、均值 -7.0%，七个方向最惨</b>；光模块放量跌 8%–11.8%，光纤光缆缩量跌 4%，差别就在 AI 资本开支敞口。",
     "天孚通信"),
    ("存储", "存储设计+制造+模组 手工池",
     "模块厂 PE 仅 6.5–7.7 倍，是周期底部定价而非便宜就该买；<b>全池量比 0.67–0.95 普遍缩量</b>，抛压比 CPO 轻。",
     "江波龙"),
    ("端侧", "端侧 SoC/AIoT/终端 手工池",
     "均值仅 -1.85%，<b>不依赖北美资本开支，是本周避风港</b>；豪威当日红盘、距高 -5.8%、PE 34.9，位置估值都在线。",
     "瑞芯微"),
    ("机器人", "申万三级 850781 + 人形核心零部件",
     "均值 -1.10% 且<b>几乎全线缩量</b>（量比 0.51–0.93），是获利了结不是恐慌；但宇树 PE 502、绿的谐波 338 属故事定价。",
     "宇树科技"),
]


def pct_cell(v):
    cls = "up" if v > 0 else ("down" if v < 0 else "")
    return f'<td class="num {cls}">{v:+.2f}%</td>'


def pe_cell(v):
    if v is None:
        return '<td class="num" style="color:var(--muted)">亏损</td>'
    return f'<td class="num">{v:.1f}</td>'


def build_table(pool):
    rows = []
    for i, r in enumerate(D["tops"][pool], 1):
        h = D["hist"].get(r["ts_code"], {})
        name = r["name"]
        code = r["ts_code"].split(".")[0]
        px = (f'<span class="{"up" if r["pct_chg"] > 0 else "down" if r["pct_chg"] < 0 else ""}">'
              f'{r["close"]:.2f}</span>')
        rows.append(
            f'<tr><td><span class="rank">{i}</span><b>{name}</b> <span class="small">{code}</span>'
            f'<br><span class="small">成交 {r["amt_yi"]:.1f} 亿</span></td>'
            f'<td class="num">{px}</td>'
            f'{pct_cell(r["pct_chg"])}'
            f'<td class="num">{r["mv_yi"]:.0f} 亿</td>'
            f'{pe_cell(r.get("pe_ttm"))}'
            f'<td class="num">{h.get("from_hi", 0):.1f}%</td>'
            f'<td class="num">{h.get("chg20", 0):+.1f}%</td>'
            f'<td class="num">{h.get("vr20", 0):.2f}</td></tr>')
    return ('<table><tr><th>标的 / 代码</th><th>收盘</th><th>当日</th><th>总市值</th>'
            '<th>PE</th><th>距60日高</th><th>20日</th><th>量比20</th></tr>'
            + "".join(rows) + '</table>')


def main():
    order = ["半导体", "GPU", "算力", "CPO", "存储", "端侧", "机器人"]
    st = D["stats"]
    # 强弱总览表
    ov_rows = ""
    for i, k in enumerate(sorted(order, key=lambda x: -st[x]["avg_pct"]), 1):
        s = st[k]
        cls = "up" if s["avg_pct"] > 0 else "down"
        ov_rows += (f'<tr><td><span class="rank">{i}</span><b>{k}</b>'
                    f'<br><span class="small">{D["pools_meta"][k]}</span></td>'
                    f'<td class="num {cls}">{s["avg_pct"]:+.2f}%</td>'
                    f'<td class="num">{s["up"]}/{s["down"]}</td>'
                    f'<td class="num">{s["amount_yi"]:.0f} 亿</td>'
                    f'<td class="num">{s["n"]} 只</td>'
                    f'<td>{"、".join(s["best"][:2])}</td></tr>')

    sec_html = ""
    for idx, (pool, cal, concl, kline_name) in enumerate(SECTIONS, 1):
        c = CH.get(kline_name)
        img = (f'<img class="chart" src="../charts/{c["file"]}">' if c else "")
        sec_html += (f'<h3>{idx}. {pool}（Top8）</h3>'
                     f'<p class="small">口径：{cal}</p>'
                     f'{build_table(pool)}'
                     f'<p>{concl}</p>{img}')

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
  <h1>📊 {TITLE}</h1>
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>板块横向对比 · 数据截至 2026-11-13 收盘</div>
  <p class="stance"><b>结论：本周杀的是海外算力链，不是科技股。</b>七个方向均值排序 <b>GPU -0.21% ＞ 机器人 -1.10% ＞ 端侧 -1.85% ＞ 半导体 -3.35% ＞ 算力 -3.83% ＞ 存储 -4.49% ＞ CPO -7.00%</b>。CPO 21 只零红盘、光模块与光纤缩放分化；GPU 芯片端几乎没跌。<b>越贴北美云厂资本开支越惨，越贴国内算力供给与应用端越抗跌。</b>抄底先看缩量：机器人、端侧、存储量比已到 0.6–0.95，CPO 仍在放量下跌。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">最抗跌 · GPU</div><div class="val down">-0.21%</div><div class="sub">8 只 · 涨 5 跌 3</div></div>
  <div class="kpi"><div class="label">最惨 · CPO</div><div class="val down">-7.00%</div><div class="sub">21 只零红盘</div></div>
  <div class="kpi"><div class="label">全市场</div><div class="val down">4748 家下跌</div><div class="sub">成交 16671 亿</div></div>
  <div class="kpi"><div class="label">逆势红盘</div><div class="val up">豪威 +1.32%</div><div class="sub">端侧 CIS 龙头</div></div>
</div>

<h2>一、七个方向强弱排序</h2>
<img class="chart" src="../charts/{CH['上证指数']['file']}">
<p class="small">上证 3634.35（-0.59%），11/13 全市场 4748 家下跌、跌停 33 家；下方各方向的 K 线末根均为 11/13 收盘。</p>
<table>
  <tr><th>方向 / 口径</th><th>11/13 均值</th><th>涨/跌</th><th>池成交</th><th>样本</th><th>池内最强</th></tr>
  {ov_rows}
</table>
<p>规律：<b>同板块内部也在分化</b>——CPO 里光模块放量跌 8%–11.8%，光纤光缆缩量跌 4%；算力里海外链全杀，中兴 +0.11%、中科曙光 +1.76%、润泽 +2.70% 红盘。<b>今天被砍的是「卖给海外云厂」那一段，不是国内算力需求。</b></p>

<h2>二、三个常被混用的词</h2>
<p><b>半导体 = 行业</b>（材料→设备→设计→制造→封测→功率，申万二级有官方分类）；<b>GPU = 芯片的一个品类</b>（并行计算加速器，散在半导体与计算机行业，没有独立行业）；<b>算力 = 一种资源与产能</b>（芯片→服务器→光模块交换机→机房→电力→租赁运营，横跨电子/通信/计算机/电力，没有对应行业）。</p>
<p><b>关系：GPU ⊂ 半导体；算力硬件链 ⊃ GPU。</b>所以「买算力」和「买 GPU」不是一回事——本周两者差 3.6 个百分点（-3.83% vs -0.21%），混买等于承担最差那条链的波动。<b>端侧、机器人</b>则靠真实出货与产业订单，不在 AI 资本开支链上，因此抗跌。</p>

<h2>三、各方向 Top8</h2>
<p class="small">列：收盘 / 当日 / 总市值 / PE(TTM) / 距 60 日高 / 20 日涨跌 / 量比（当日额 ÷ 20 日均额）。Top8 一律按总市值；距高、20 日、量比按 60 交易日窗口。</p>
{sec_html}

<h2>四、怎么用这份对比</h2>
<div class="box box-g">
① <b>别把七个词混买</b>：本周区间 -0.21% 到 -7.00%，差 6.8 个百分点。<br>
② <b>抄底先等量能</b>：CPO/算力量比仍 1.1–1.5 放量下跌，抛压未出完；<b>连续两日量比 &lt;0.8</b> 才是入场信号。机器人、端侧、存储已在 0.6–0.95，条件更接近。<br>
③ <b>优先级</b>：机器人零部件（拓普 PE 35 距高 -4.2%、双环 PE 28 距高 -8.0%、三花 PE 38 红盘）→ 端侧（豪威 PE 35 距高 -5.8%、瑞芯微距高 -8.2%、歌尔量比 0.70 缩量）→ 存储权重长鑫（PE 19.5 量比 0.70）。<br>
④ <b>回避故事定价</b>：宇树 PE 502、绿的谐波 338、沐曦 1171、华虹 246、燧原/摩尔线程/景嘉微/芯原亏损——回撤弹性大于上涨弹性。<br>
⑤ <b>只碰有业绩的</b>：GPU 端仅寒武纪、海光换手 2.55%/1.22% 且有盈利支撑；次新 GPU 三兄弟换手 13%–22%，波动远大于涨幅。</div>

<div class="foot">
  <p><b>口径：</b>申万 2021 分类（二级 801081 / 三级 851024+850703+850822+850781）；GPU、CPO、存储、端侧为手工核心池；Top8 按总市值。行情与估值为 Tushare Pro 日线 + daily_basic（2026-11-13 收盘），距高/20 日/量比按 60 交易日窗口；燧原科技 2026-09-11 上市、宇树科技 2026-08-19 上市，样本不足 60 日。K 线为前复权日线，红涨绿跌。</p>
  <p>本页面为数据对比与结构梳理，不构成买卖建议；据此操作风险自担。投资有风险，入市需谨慎。</p>
</div>

</div>
</body>
</html>
"""
    out = REPO / "html/sector-20261113.html"
    out.write_text(patch_html(html), encoding="utf-8")
    print("saved", out, len(html))


if __name__ == "__main__":
    main()
