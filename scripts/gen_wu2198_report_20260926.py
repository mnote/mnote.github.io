"""
wu2198 投资日报 — 2026-09-26 (周六 21:00 · 中秋节)
- 最近 24 小时 0 条操盘贴(博主节日休息 9/25-9/26)
- 数据截至: 9/24 节前最后交易日(9/25-9/27 中秋休市)
- 核心立场: ⚪ 中性偏空 · 沿用博主 8/4 关键位体系
- 板块: PCB/覆铜板 + 光模块/CPO + 创新药
- 6 个股: 沪电股份 / 生益科技 / 中际旭创 / 天孚通信 / 恒瑞医药 / 深南电路
"""
from pathlib import Path
from datetime import datetime

OUT_HTML = Path("/Users/maoling/workspace/mnote.github.io/2026-09-26-wu2198-investment-report.html")
INDEX_HTML = Path("/Users/maoling/workspace/mnote.github.io/index.html")

TODAY = "2026-09-26 (周六 21:00 · 中秋节)"
LAST_TRADING = "2026-09-24 (周三 · 节前最后交易日)"
SH_INDEX = "3888.37 (-1.22%)"  # 9/24 实际收盘

# ── 抓取的微博(全部为节日祝福/社会新闻/晚安,无操盘信号) ───
POSTS = [
    {
        "time": "09-26 20:48", "score": 225, "rep": 0, "com": 27, "like": 198,
        "signal": "—", "topic": "社会新闻", "emoji": "⚪", "dir": "无关",
        "text": "#乒乓球混双决赛#你看了么?",
    },
    {
        "time": "09-26 20:07", "score": 947, "rep": 2, "com": 100, "like": 845,
        "signal": "—", "topic": "节日祝福", "emoji": "⚪", "dir": "无关",
        "text": "西大的月饼,久违了!",
    },
    {
        "time": "09-26 19:37", "score": 1602, "rep": 6, "com": 196, "like": 1406,
        "signal": "—", "topic": "鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "秋风一吹又长一岁,很多老铁也老了!",
    },
    {
        "time": "09-26 18:49", "score": 1133, "rep": 3, "com": 47, "like": 1084,
        "signal": "—", "topic": "社会新闻", "emoji": "⚪", "dir": "无关",
        "text": "#比尔盖茨发出严厉警告#资本不怕这事!",
    },
    {
        "time": "09-26 16:44", "score": 1717, "rep": 5, "com": 81, "like": 1631,
        "signal": "—", "topic": "娱乐", "emoji": "⚪", "dir": "无关",
        "text": "曲子《从头再来》。",
    },
    {
        "time": "09-26 11:31", "score": 2531, "rep": 3, "com": 99, "like": 2432,
        "signal": "—", "topic": "社会新闻", "emoji": "⚪", "dir": "无关",
        "text": "#游本昌临终遗言#济公!",
    },
    {
        "time": "09-26 10:34", "score": 3773, "rep": 39, "com": 330, "like": 3474,
        "signal": "—", "topic": "社会新闻", "emoji": "⚪", "dir": "无关",
        "text": "#刘欢去世#歌声长存……愿一路走好。",
    },
    {
        "time": "09-26 10:17", "score": 2594, "rep": 1, "com": 165, "like": 2429,
        "signal": "—", "topic": "娱乐", "emoji": "⚪", "dir": "无关",
        "text": "昨晚上确定没磨指甲?",
    },
    {
        "time": "09-26 09:17", "score": 4297, "rep": 65, "com": 296, "like": 4003,
        "signal": "—", "topic": "鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "心坚能破万重难,心稳可掌百事顺!",
    },
    {
        "time": "09-25 23:04", "score": 4648, "rep": 11, "com": 367, "like": 4270,
        "signal": "—", "topic": "鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "月亮不睡,我先睡了……大家晚安!",
    },
]

# ── 关键位定义(沿用博主 8/4 体系) ─────
SH_LEVELS = [
    ("4256", "8/15 前顶"),
    ("3996", "8/29 周高"),
    ("3926", "8/26 上沿"),
    ("3900", "整数"),
    ("3886", "B 浪位"),
    ("3856", "8/4 支撑"),
    ("3824", "多空线"),
    ("3767", "8/4 底"),
    ("3741", "B 反起"),
]
CYB_LEVELS = [
    ("3686", "8/15 前顶"),
    ("3590", "目标位"),
    ("3486", "B 反位"),
    ("3370", "反抽"),
    ("3286", "试破位"),
    ("3220", "支撑"),
    ("3160", "A 杀位"),
]

# ── 3 大板块 + 6 支个股(沿用 9/25 报告框架) ─────
SECTORS = [
    {
        "name": "🟢 PCB / 覆铜板(博主 8/4 关注方向)",
        "summary": "博主 8/4 当日连发 2 条关键速报:'覆铜板、电子布冲板了' + 'CPO、光纤有冲板效应',奠定 9 月以来 AI 算力产业链的主线地位。<b>9/24 节前最后交易日</b>两大龙头全部下跌(沪电 -3.16% / 生益 -4.34% / 深南 -4.89%),但这是<b>节前资金避险情绪</b>而非基本面恶化(AI 服务器/光通信/CPO 中期逻辑未变)。9/28 节后开盘是检验主线成色的关键窗口。",
        "stocks": [
            {"code": "002463.SZ", "name": "沪电股份", "emoji": "🟡",
             "close": "124.05", "chg": "-3.16%",
             "logic": "AI 服务器 PCB 全球龙头,博主 8/4 'PCB 板块冲板效应'直接对应品种。9/24 节前跌 3.16% 收 124.05,股价从 60D 高 158.20 回调至 60D 低 94.73 上方 124 一线,处于中枢震荡下沿。AI 服务器主板高多层 PCB/Mini-LED IC 载板三方向需求景气,中期逻辑未变。",
             "key": "60D低 94.73 / 支撑 115 / 9/24收 124.05 / 压力 140 / 60D高 158.20"},
            {"code": "600183.SH", "name": "生益科技", "emoji": "🟡",
             "close": "137.33", "chg": "-4.34%",
             "logic": "覆铜板(CCL)全球第二大/国内龙头,博主 8/4 直接点名'覆铜板、电子布冲板了'。9/24 节前跌 4.34% 收 137.33,股价从 60D 高 191.88 回调至 60D 低 97.51 上方 137 一线。<b>高速 CCL(M6/M7/M8)</b>用于 800G/1.6T 光模块/AI 服务器,景气周期延续。",
             "key": "60D低 97.51 / 支撑 130 / 9/24收 137.33 / 压力 170 / 60D高 191.88"},
        ],
    },
    {
        "name": "🟢 光模块 / CPO(博主 8/4 关注方向)",
        "summary": "博主 8/4 'CPO、光纤有冲板效应' + 8/14 转发英伟达 200G/lane Spectrum-6 ASIC 102.4Tb/s 量产 + 9/2 14:05 '算力租赁龙头 12 日 87.26→137.50'(=利通电子 603629)三剑客涨停潮,共同构成光模块/CPO 主线的多头逻辑。<b>9/24 节前</b>中际旭创 -2.89% / 天孚通信 -2.71% 同步走弱,但板块中期景气未变(1.6T 光模块/800G/AI 算力)。",
        "stocks": [
            {"code": "300308.SZ", "name": "中际旭创", "emoji": "🟡",
             "close": "895.86", "chg": "-2.89%",
             "logic": "1.6T 光模块全球龙头,博主 8/14 转发英伟达 200G/lane 量产 + 8/22 业绩 +241% 验证。9/24 节前跌 2.89% 收 895.86,股价从 60D 高 1382.33 回调至 60D 低 793.03 上方 895 一线。距 60D 低 793 仅 102 元(11%),是 CPO 主线中基本面最强、估值合理的核心标的。",
             "key": "60D低 793.03 / 支撑 820 / 9/24收 895.86 / 压力 1000 / 60D高 1382.33"},
            {"code": "300394.SZ", "name": "天孚通信", "emoji": "🟡",
             "close": "267.93", "chg": "-2.71%",
             "logic": "光器件平台型公司(无源+有源+封装),中际旭创核心供应商。9/24 节前跌 2.71% 收 267.93,与中际旭创同步走弱,体现光模块产业链共振。60D 高 395 / 60D 低 220,股价回调至 267 一线接近支撑区。",
             "key": "支撑 220 / 9/24收 267.93 / 压力 300 / 60D高 395"},
        ],
    },
    {
        "name": "🟢 创新药(博主 8/4 关注方向)",
        "summary": "博主 8/4 18:46 '创新药龙头涨停 36.36 元'(=恒瑞医药 600276) + 8/27 转发风华高科 +74% 业绩 + 8/31 博主长期持有优质银行股。每年拿分红更划算(5722 赞),共同构成'业绩兑现 + 防御红利'双逻辑。<b>9/24 节前</b>恒瑞跌 1.58% 收 44.86(8/4 涨停价 36.36 上方 +23%),深南电路跌 4.89% 收 394.50。",
        "stocks": [
            {"code": "600276.SH", "name": "恒瑞医药", "emoji": "🟡",
             "close": "44.86", "chg": "-1.58%",
             "logic": "创新药出海标杆(PD-1/ADC 双轮驱动),博主 8/4 18:46 '创新药龙头涨停 36.36 元'直接对应品种。9/24 节前跌 1.58% 收 44.86,从 8/4 低 36.36 反弹至 44.86(+23.4%),趋势延续。出海逻辑+集采压力缓解+多款新药放量,中期逻辑清晰。",
             "key": "8/4底 36.36 / 9/24收 44.86 / 压力 50 / 60D高 60"},
            {"code": "002916.SZ", "name": "深南电路", "emoji": "🟡",
             "close": "394.50", "chg": "-4.89%",
             "logic": "PCB + 封装基板(国产替代)双轮,博主 8/4 'PCB 冲板效应'关注方向。9/24 节前跌 4.89% 收 394.50,是<b>8 个观察标的中跌幅最大</b>。封装基板(ABF/BT)用于 CPU/GPU/AI 芯片,IC 载板国产替代加速,中期景气未变。",
             "key": "支撑 280 / 9/24收 394.50 / 压力 440 / 60D高 540"},
        ],
    },
]

# ── 风险点 ──────────────────
RISKS = [
    ("⚠️", "博主 9/24-9/26 中秋节休息 12 条微博全部节日祝福/社会新闻/晚安,0 条操盘贴 — 9/28 节后开盘博主是否发新观点是关键"),
    ("🔴", "大盘 3888.37 已失守博主 8/4 'B 浪位' 3886 (跌穿 2.37 点),距博主 8/4 关键支撑 3856 仅 32 点 — 第四大浪 ABC 调整结构未完立场得到市场印证"),
    ("🔴", "创业板 3288.95 已跌穿博主 8/4 '试破不收破'位 3286 (跌穿 2.95 点),距博主 8/4 'A 杀完成位' 3160 仅 129 点 — B 反失败风险加大"),
    ("⚠️", "博主 8/4 关键位体系部分失效:大盘 3886 失守 / 创业板 3286 失守,需重新评估博主'B 反结构明朗'判断"),
    ("⚠️", "9/24 节前 8 个观察标的 6 个跌幅超 2%,深南电路 -4.89% 最大,生益科技 -4.34% 次之,沪电股份 -3.16% 第三 — 节前避险情绪集中"),
    ("⚠️", "博主 6/8 撤离本金+去年盈利一半,预测偏多但实际行动防御 — 实际比预测更看空"),
    ("⚠️", "博主长期风控底线:不举债/不杠杆/只用闲钱/无技术不参与短线"),
    ("⚠️", "9/25-9/27 中秋节 A 股休市,9/28 周一恢复交易 — 节后首日开盘表现是验证主线的关键"),
]

# ── HTML 模板 ──────────────────
HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>wu2198 投资观点日报 · 2026-09-26</title>
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
    background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 28px;
  }}
  .hero h1 {{ color: #991b1b; }}
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
    <h1>📈 wu2198 投资观点日报 · 2026-09-26</h1>
    <div class="meta">
      <span>📅 <b>{TODAY}</b></span>
      <span>🏛️ 沪指(9/24 收) <b>{SH_INDEX}</b></span>
      <span>📊 数据源:weibo-watcher + tushare</span>
      <span>🎯 最近交易日:<b>{LAST_TRADING}</b></span>
      <span>🌕 A 股:9/25-9/27 中秋休市 · 9/28 周一恢复</span>
    </div>
    <div class="stance">
      <span class="emoji">⚪</span><b>博主最近一天核心立场</b>:
      <b>中性偏空 · 沿用 8/4 关键位体系</b>。
      最近 24 小时 <span class="tag tag-none">0 条操盘贴</span> (博主中秋节+周末休息,12 条微博全部为节日祝福/社会新闻/晚安);
      数据截止 <b>9/24 节前最后交易日</b>,
      关键位印证:大盘 <span class="tag tag-bear">3888.37 失守 B 浪位 3886</span>,
      创业板 <span class="tag tag-bear">3288.95 跌穿试破位 3286</span>,
      博主 8/4 'B 反结构'判断需要重估。
    </div>
  </div>

  <h2>📊 核心数据卡片</h2>
  <div class="grid-3">
    <div class="kpi">
      <div class="label">博主核心立场</div>
      <div class="val" style="color: var(--none);">⚪ 中性偏空</div>
      <div class="sub">0 条新贴 · 沿用 8/4 体系</div>
    </div>
    <div class="kpi">
      <div class="label">沪指 9/24 收</div>
      <div class="val" style="color: var(--bear);">{SH_INDEX}</div>
      <div class="sub">失守 B 浪位 3886 距 3856 仅 32 点</div>
    </div>
    <div class="kpi">
      <div class="label">创业板 9/24 收</div>
      <div class="val" style="color: var(--bear);">3288.95</div>
      <div class="sub">-2.68% 跌穿试破位 3286 距 3160 仅 129 点</div>
    </div>
    <div class="kpi">
      <div class="label">最近交易日</div>
      <div class="val">9/24 (周三)</div>
      <div class="sub">9/25-9/27 中秋休市</div>
    </div>
    <div class="kpi">
      <div class="label">抓取微博</div>
      <div class="val">10 条</div>
      <div class="sub">过滤 2 置顶 · 全部节日祝福</div>
    </div>
    <div class="kpi">
      <div class="label">操盘信号</div>
      <div class="val" style="color: var(--none);">0 条</div>
      <div class="sub">博主中秋休息 · 等 9/28</div>
    </div>
  </div>

  <h2>📋 完整微博列表(10 条,按时间倒序)</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 32px;">#</th>
        <th style="width: 100px;">时间</th>
        <th style="width: 50px;">方向</th>
        <th>信号 / 话题</th>
        <th>内容摘要</th>
        <th style="width: 90px;">互动(转/评/赞)</th>
        <th style="width: 60px;">综合分</th>
      </tr>
    </thead>
    <tbody>
{POSTS_TABLE}
    </tbody>
  </table>

  <h2>🚦 核心操盘信号(LLM 二次摘要)</h2>

  <div class="panel">
    <h3>⚪ 信号 0 — 最近 24 小时 0 条操盘贴 (中秋节 + 周末休息)</h3>
    <p>博主 9/24(中秋节前最后交易日)17:41 转发 <span class="tag tag-bear">"反弹几天,就忘记了本质!"</span> 之后,<b>9/24-9/26 共 3 天 12 条微博全部为节日祝福/社会新闻/晚安/鸡汤,0 条操盘贴</b>。</p>
    <ul>
      <li><b>9/24 17:41</b>(中秋节前最后一贴)转发 <b>"反弹几天,就忘记了本质!"</b> — <span class="tag tag-bear">🔴 看空</span> <span class="tag tag-neutral">置信度 中</span>。这是博主节前唯一隐含看空信号。</li>
      <li><b>9/25 23:04</b>「月亮不睡,我先睡了……大家晚安!」— 4270 赞</li>
      <li><b>9/26 09:17</b>「心坚能破万重难,心稳可掌百事顺!」— 4003 赞(中秋节早安)</li>
      <li><b>9/26 10:34</b>「#刘欢去世#歌声长存……愿一路走好。」— 3474 赞(悼念)</li>
      <li><b>9/26 11:31</b>「#游本昌临终遗言#济公!」— 2432 赞</li>
      <li><b>9/26 18:49</b>「#比尔盖茨发出严厉警告#资本不怕这事!」— 1084 赞</li>
    </ul>
    <p><b>LLM 解读</b>:博主 9/24 17:41 在节前最后一个交易日收盘后转发"反弹几天就忘记了本质",这是博主 8/4 体系下的"第四大浪 ABC 调整未完"立场的延续 — 警惕节前小 V 反弹后的二次下探。中秋节期间博主休息,9/28 节后开盘是否发新观点是关键(<span class="tag tag-neutral">中性偏空</span> <span class="tag tag-neutral">置信度 中</span>,样本极少)。</p>
  </div>

  <h2>📉 9/24 节前最后交易日 关键位印证</h2>

  <div class="grid-2">
    <div class="panel" style="border-left: 4px solid var(--bear);">
      <h3>🔴 大盘 沪指 3888.37 -1.22%</h3>
      <p><b>关键位印证</b>:9/24 收 <b>3888.37</b>(跌 1.22%),<b>已失守博主 8/4 'B 浪位' 3886</b>(跌穿 2.37 点)。</p>
      <ul>
        <li><b>距博主 8/4 关键支撑 3856 仅 32 点</b>(再跌 0.82% 即失守)</li>
        <li>距 8/4 关键位 3824 (多空线) 64 点</li>
        <li>距 8/4 关键位 3767 (8/4 底) 121 点</li>
        <li>距 8/14 B 反起 3741 147 点</li>
      </ul>
      <p><b>结论</b>:博主 8/4 'B 反结构'判断需要重估 — B 浪位 3886 已失守,关键支撑 3856 岌岌可危。</p>
    </div>

    <div class="panel" style="border-left: 4px solid var(--bear);">
      <h3>🔴 创业板 3288.95 -2.68%</h3>
      <p><b>关键位印证</b>:9/24 收 <b>3288.95</b>(跌 2.68%),<b>已跌穿博主 8/4 '试破不收破'位 3286</b>(跌穿 2.95 点)。</p>
      <ul>
        <li><b>距博主 8/4 'A 杀完成位' 3160 仅 129 点</b>(再跌 3.9% 即触及)</li>
        <li><b>MA20 3430.98 / MA50 3532.61 / MA60 3647.62 全部失守</b></li>
        <li>距 8/4 关键位 3220 (支撑) 69 点</li>
      </ul>
      <p><b>结论</b>:博主 8/4 给出 3286 '试破不收破'判断,9/24 直接跌穿 — 创业板是 9/24 最弱指数,博主'第四大浪未完'判断被强化。</p>
    </div>
  </div>

  <h2>💼 3 大板块 + 6 支个股</h2>

{SECTORS_HTML}

  <h2>📉 K 线图(关键位居左虚线标注)</h2>

  <h3>1. 上证指数 (000001.SH) · 9/24 收 3888.37 (-1.22%)</h3>
  <img class="chart" src="charts/000001_SH_20260926.png" alt="上证指数 K线图" />
  <div class="chart-caption">沪指 9 个关键位(沿用博主 8/4 体系):4256(8/15 前顶)/ 3996(8/29 周高)/ 3926(8/26 上沿)/ 3900(整数)/ 3886(B 浪位)/ 3888.37(9/24 收)/ 3856(8/4 支撑)/ 3824(多空线)/ 3767(8/4 底)/ 3741(B 反起)。9/24 收盘 3888.37 已失守 B 浪位 3886(跌穿 2.37 点),距关键支撑 3856 仅 32 点。</div>

  <h3>2. 创业板指 (399006.SZ) · 9/24 收 3288.95 (-2.68%)</h3>
  <img class="chart" src="charts/399006_SZ_20260926.png" alt="创业板指 K线图" />
  <div class="chart-caption">创业板 10 个关键位(沿用博主 8/4 体系):3686(8/15 前顶)/ 3590(目标位)/ 3486(B 反位)/ 3370(反抽)/ 3289.95(9/24 收)/ 3286(试破位)/ 3220(支撑)/ 3160(A 杀位)。9/24 收盘 3288.95 已跌穿试破位 3286(跌穿 2.95 点),距 A 杀位 3160 仅 129 点 — 创业板是 9/24 最弱指数。</div>

  <h3>3. 🟡 沪电股份 (002463.SZ) · AI PCB 龙头 · 9/24 收 124.05 (-3.16%)</h3>
  <img class="chart" src="charts/002463_SZ_20260926.png" alt="沪电股份 K线图" />
  <div class="chart-caption">博主 8/4 'PCB 板块冲板效应'直接对应品种。5 个关键位:60D低 94.73 / 支撑 115 / 9/24 收 124.05 / 压力 140 / 60D高 158.20。</div>

  <h3>4. 🟡 生益科技 (600183.SH) · 覆铜板龙头 · 9/24 收 137.33 (-4.34%)</h3>
  <img class="chart" src="charts/600183_SH_20260926.png" alt="生益科技 K线图" />
  <div class="chart-caption">博主 8/4 直接点名'覆铜板、电子布冲板了'。5 个关键位:60D低 97.51 / 支撑 130 / 9/24 收 137.33 / 压力 170 / 60D高 191.88。</div>

  <h3>5. 🟡 中际旭创 (300308.SZ) · 1.6T 光模块龙头 · 9/24 收 895.86 (-2.89%)</h3>
  <img class="chart" src="charts/300308_SZ_20260926.png" alt="中际旭创 K线图" />
  <div class="chart-caption">博主 8/14 转发英伟达 200G/lane 量产 + 8/22 业绩 +241%。5 个关键位:60D低 793.03 / 支撑 820 / 9/24 收 895.86 / 压力 1000 / 60D高 1382.33。</div>

  <h3>6. 🟡 天孚通信 (300394.SZ) · 光器件平台型 · 9/24 收 267.93 (-2.71%)</h3>
  <img class="chart" src="charts/300394_SZ_20260926.png" alt="天孚通信 K线图" />
  <div class="chart-caption">光器件平台型公司,中际旭创核心供应商。4 个关键位:支撑 220 / 9/24 收 267.93 / 压力 300 / 60D高 395。</div>

  <h3>7. 🟡 恒瑞医药 (600276.SH) · 创新药出海标杆 · 9/24 收 44.86 (-1.58%)</h3>
  <img class="chart" src="charts/600276_SH_20260926.png" alt="恒瑞医药 K线图" />
  <div class="chart-caption">博主 8/4 18:46 '创新药龙头涨停 36.36 元'直接对应品种。4 个关键位:8/4底 36.36 / 9/24 收 44.86 / 压力 50 / 60D高 60。</div>

  <h3>8. 🟡 深南电路 (002916.SZ) · PCB/封装基板 · 9/24 收 394.50 (-4.89%)</h3>
  <img class="chart" src="charts/002916_SZ_20260926.png" alt="深南电路 K线图" />
  <div class="chart-caption">博主 8/4 'PCB 冲板效应'关注方向。4 个关键位:支撑 280 / 9/24 收 394.50 / 压力 440 / 60D高 540。<b>9/24 节前 8 个观察标的中跌幅最大 (-4.89%)</b>。</div>

  <h2>⚠️ 风险提示</h2>
  <div class="panel" style="border-left: 4px solid var(--bear);">
    <ul>
{RISKS_HTML}
    </ul>
  </div>

  <h2>🎯 操作建议汇总</h2>

  <div class="panel panel-2">
    <h3>📌 大盘</h3>
    <p><b>短期(节后 1-2 周)</b>:<b>🟡 中性偏空</b>。9/24 节前最后交易日大盘 3888 已失守博主 8/4 B 浪位 3886,<b>距关键支撑 3856 仅 32 点</b>。9/28 节后开盘是关键窗口 —</p>
    <ul>
      <li><b>乐观情景</b>:9/28 反弹收复 3886,重回 3900-3926 区间震荡,板块快速轮动(沿用 9/4 防御 + 9/11 进攻组合)</li>
      <li><b>悲观情景</b>:9/28 跌破 3856,触发博主 8/4 '关键支撑'破位,下看 3824 多空线 → 3767 8/4 底 → 3741 B 反起</li>
      <li><b>创业板 3286 已跌穿</b>:距 A 杀位 3160 仅 129 点 — 创业板是节后最弱环节,警惕</li>
    </ul>
  </div>

  <div class="panel panel-2">
    <h3>📌 板块策略</h3>
    <ul>
      <li><b>🟢 中线布局(节后回调买入):PCB/覆铜板 + 光模块/CPO + 创新药</b> — 博主 8/4 关注方向 + AI 算力/创新药中期逻辑未变。9/24 节前避险情绪集中释放后,9/28-30 是分批建仓窗口。</li>
      <li><b>🟡 短期防御:银行/红利</b> — 博主 8/31 '长期持有优质银行股,每年拿分红更划算' (5722 赞) 持续底仓逻辑。在主线回调时银行股是抗跌品种。</li>
      <li><b>⚠️ 规避:高位消费白马</b> — 博主 8/15 警示白酒/贵州茅台的逻辑仍未解除,'中央汇金证金集体清仓贵州茅台' 警示消费白马。</li>
    </ul>
  </div>

  <div class="panel panel-2">
    <h3>📌 关键位监控(节后 9/28 开盘首日)</h3>
    <table>
      <thead>
        <tr><th>标的</th><th>支撑位</th><th>9/24 收</th><th>压力位</th><th>监控动作</th></tr>
      </thead>
      <tbody>
        <tr><td>沪指</td><td>3856 / 3824</td><td>3888.37</td><td>3900 / 3926</td><td>收复 3886 → 偏多;失守 3856 → 减仓</td></tr>
        <tr><td>创业板</td><td>3220 / 3160</td><td>3288.95</td><td>3370 / 3486</td><td>收复 3286 → 偏多;失守 3220 → 警示 A 杀</td></tr>
        <tr><td>沪电股份</td><td>115 / 94.73</td><td>124.05</td><td>140 / 158</td><td>回踩 115 加仓;反弹 140 减仓</td></tr>
        <tr><td>生益科技</td><td>130 / 97.51</td><td>137.33</td><td>170 / 192</td><td>回踩 130 加仓;反弹 170 减仓</td></tr>
        <tr><td>中际旭创</td><td>820 / 793</td><td>895.86</td><td>1000 / 1382</td><td>触 793 加仓(博主 9/4 已触底反弹)</td></tr>
        <tr><td>天孚通信</td><td>220</td><td>267.93</td><td>300 / 395</td><td>回踩 220 加仓;反弹 300 减仓</td></tr>
        <tr><td>恒瑞医药</td><td>36.36 (8/4底)</td><td>44.86</td><td>50 / 60</td><td>持有不操作;回踩 40 加仓</td></tr>
        <tr><td>深南电路</td><td>280</td><td>394.50</td><td>440 / 540</td><td>9/24 节前跌幅最大 -4.89% — 回踩 350 加仓</td></tr>
      </tbody>
    </table>
  </div>

  <div class="footer">
    <p>报告生成时间:{ts} · 数据源:weibo-watcher skill (UID 1216826604) + tushare Pro · 8 张 K 线图(关键位 📌 红色虚线 居左标注,沿用博主 8/4 关键位体系)</p>
    <p>博主最近一天核心立场:<b>⚪ 中性偏空 · 沿用 8/4 关键位体系</b> · 0 条新操盘贴 · 数据截至 9/24 节前最后交易日 · 板块:<b>🟢 PCB/覆铜板 · 🟢 光模块/CPO · 🟢 创新药</b> · 风险:<b>🔴 大盘失守 3886 / 创业板跌穿 3286 / 节后 9/28 开盘是关键</b></p>
  </div>

</div>
</body>
</html>
"""

# 渲染微博表格
def render_posts_table():
    rows = []
    for i, p in enumerate(POSTS, 1):
        emoji = p["emoji"]
        dir_cls = {"看多": "tag-bull", "看空": "tag-bear", "中性": "tag-neutral", "无关": "tag-none"}.get(p["dir"], "tag-none")
        rows.append(f"""      <tr>
        <td>{i}</td>
        <td>{p['time']}</td>
        <td class="emoji">{emoji}</td>
        <td><span class="tag {dir_cls}">{p['signal']}</span><br/><span class="tag tag-accent">{p['topic']}</span></td>
        <td class="text">{p['text']}</td>
        <td class="score">{p['rep']} / {p['com']} / {p['like']}</td>
        <td class="score">{p['score']:,}</td>
      </tr>""")
    return "\n".join(rows)

# 渲染板块
def render_sectors():
    out = []
    for s in SECTORS:
        cards = []
        for st in s["stocks"]:
            bull_cls = "bull" if "🟢" in st["emoji"] else ("bear" if "🔴" in st["emoji"] else "neutral")
            cards.append(f"""    <div class="stock-card {bull_cls}">
      <h4>{st['emoji']} {st['name']} ({st['code']}) · 9/24 收 {st['close']} {st['chg']}</h4>
      <div class="logic">{st['logic']}</div>
      <div class="key">关键位:{st['key']}</div>
    </div>""")
        out.append(f"""  <div class="panel">
    <h3>{s['name']}</h3>
    <p>{s['summary']}</p>
{chr(10).join(cards)}
  </div>""")
    return "\n".join(out)

# 渲染风险
def render_risks():
    return "\n".join([f"      <li><b>{e}</b> {t}</li>" for e, t in RISKS])


# 拼装 HTML
posts_table = render_posts_table()
sectors_html = render_sectors()
risks_html = render_risks()

html = HTML.format(
    TODAY=TODAY,
    SH_INDEX=SH_INDEX,
    LAST_TRADING=LAST_TRADING,
    POSTS_TABLE=posts_table,
    SECTORS_HTML=sectors_html,
    RISKS_HTML=risks_html,
    ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)

OUT_HTML.write_text(html, encoding="utf-8")
print(f"[ok] wrote {OUT_HTML} ({len(html):,} bytes)")
