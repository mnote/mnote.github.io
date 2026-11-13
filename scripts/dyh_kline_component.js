/* 都业华收评纪要 · 交互式 K 线组件（ECharts 内嵌自包含）
 * 约定：A 股惯例红涨绿跌（收盘 ≥ 开盘 = 红）；关键位只画虚线，文字在 HTML 图例里，避免压 K 线；
 *       懒渲染（进入视口才 init），手机端与桌面端都可缩放/看十字光标。
 * 依赖：window.__KLINE__ = {series: {code: {name, levels:[{v,label,color}], bars:[...]}}}
 */
(function () {
  var UP = "#e63946", DOWN = "#2a9d8f";
  var MA_COLORS = { ma5: "#f59e0b", ma10: "#8b5cf6", ma20: "#0ea5e9" };
  var FONT = 'PingFang SC, Microsoft YaHei, Heiti SC, "Segoe UI", sans-serif';

  function fmt(v, n) {
    if (v === null || v === undefined || isNaN(v)) return "—";
    return Number(v).toFixed(n === undefined ? 2 : n);
  }

  function tooltipFormatter(params) {
    if (!params || !params.length) return "";
    var p0 = null;
    for (var pi = 0; pi < params.length; pi++) {
      if (params[pi].seriesId && params[pi].seriesId.indexOf("k_") === 0) { p0 = params[pi]; break; }
    }
    if (!p0) p0 = params[0];
    var code = (p0.seriesId || "").replace(/^k_/, "");
    var s = window.__KLINE__.series[code];
    if (!s) return "";
    var i = p0.dataIndex;
    var b = s.bars[i];
    if (!b) return "";
    var prev = i > 0 ? s.bars[i - 1].c : b.o;
    var chg = prev ? ((b.c - prev) / prev) * 100 : 0;
    var col = b.c >= b.o ? UP : DOWN;
    var html = '<div style="font-size:12px;line-height:1.7;min-width:172px">';
    html += '<b>' + b.d + '</b><br>';
    html += '开 <b>' + fmt(b.o) + '</b>　高 <b>' + fmt(b.h) + '</b><br>';
    html += '低 <b>' + fmt(b.l) + '</b>　收 <span style="color:' + col + ';font-weight:700">' + fmt(b.c) + "</span><br>";
    html += '涨跌 <span style="color:' + col + '">' + (chg >= 0 ? "+" : "") + fmt(chg) + "%</span><br>";
    html += '量 <b>' + fmt(b.v / 10000, 0) + " 万手</b><br>";
    html += 'MA5 ' + fmt(b.ma5) + "　MA10 " + fmt(b.ma10) + "<br>";
    html += "MA20 " + fmt(b.ma20) + "<br>";
    html += "MACD " + fmt(b.macd, 3) + "　DIF " + fmt(b.dif, 3) + "　DEA " + fmt(b.dea, 3);
    html += "</div>";
    return html;
  }

  function buildOption(code) {
    var s = window.__KLINE__.series[code];
    var bars = s.bars;
    var dates = bars.map(function (b) { return b.d; });
    var n = bars.length;

    var kData = bars.map(function (b) { return [b.o, b.c, b.l, b.h]; });
    var volData = bars.map(function (b, i) { return [i, b.v]; });
    var difData = bars.map(function (b) { return b.dif; });
    var deaData = bars.map(function (b) { return b.dea; });
    var macdData = bars.map(function (b) { return b.macd; });

    var markLines = s.levels.map(function (lv) {
      return {
        yAxis: lv.v,
        lineStyle: { color: lv.color, type: "dashed", width: 1.1, opacity: 0.9 },
        label: { show: false },
        silent: true
      };
    });

    function volColor(p) {
      var b = bars[p.dataIndex];
      return b && b.c >= b.o ? UP : DOWN;
    }
    function macdColor(p) {
      return p.value >= 0 ? UP : DOWN;
    }

    var maSeries = [];
    ["ma5", "ma10", "ma20"].forEach(function (k) {
      maSeries.push({
        name: k.toUpperCase(),
        type: "line",
        data: bars.map(function (b) { return b[k]; }),
        smooth: true,
        symbol: "none",
        lineStyle: { width: 0.9, color: MA_COLORS[k] },
        itemStyle: { color: MA_COLORS[k] },
        z: 3,
        emphasis: { disabled: true }
      });
    });

    return {
      animation: false,
      backgroundColor: "#fff",
      textStyle: { fontFamily: FONT, fontSize: 11 },
      grid: [
        { left: 12, right: 58, top: 16, height: "55%" },
        { left: 12, right: 58, top: "67%", height: "12%" },
        { left: 12, right: 58, top: "82%", height: "12%" }
      ],
      axisPointer: { link: [{ xAxisIndex: "all" }], label: { backgroundColor: "#334155" } },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross", crossStyle: { color: "#94a3b8" }, lineStyle: { color: "#94a3b8" } },
        confine: true,
        backgroundColor: "rgba(255,255,255,.96)",
        borderColor: "#e5e7eb",
        borderWidth: 1,
        textStyle: { color: "#1f2937", fontSize: 12 },
        formatter: tooltipFormatter
      },
      xAxis: [
        { type: "category", data: dates, gridIndex: 0, boundaryGap: true, axisLine: { lineStyle: { color: "#9ca3af" } }, axisTick: { show: false }, axisLabel: { show: false }, splitLine: { show: false } },
        { type: "category", data: dates, gridIndex: 1, axisLine: { lineStyle: { color: "#9ca3af" } }, axisTick: { show: false }, axisLabel: { show: false }, splitLine: { show: false } },
        { type: "category", data: dates, gridIndex: 2, axisLine: { lineStyle: { color: "#9ca3af" } }, axisTick: { show: false }, axisLabel: { fontSize: 10, color: "#6b7280", hideOverlap: true }, splitLine: { show: false } }
      ],
      yAxis: [
        { scale: true, gridIndex: 0, position: "right", axisLine: { show: false }, axisTick: { show: false }, axisLabel: { fontSize: 10, color: "#6b7280" }, splitLine: { lineStyle: { color: "#eef0f3" } } },
        { scale: true, gridIndex: 1, position: "right", splitNumber: 1, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { show: false }, splitLine: { show: false } },
        { scale: true, gridIndex: 2, position: "right", splitNumber: 1, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { fontSize: 9, color: "#6b7280", showMaxLabel: false, showMinLabel: false, formatter: function (v) { return Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(1); } }, splitLine: { lineStyle: { color: "#eef0f3" } } }
      ],
      dataZoom: [
        { type: "inside", xAxisIndex: [0, 1, 2], start: Math.max(0, 100 - (60 / n) * 100), end: 100, minValueSpan: 12 },
        { type: "slider", xAxisIndex: [0, 1, 2], start: Math.max(0, 100 - (60 / n) * 100), end: 100, bottom: 8, height: 20, borderColor: "#e5e7eb", fillerColor: "rgba(37,99,235,.10)", handleStyle: { color: "#94a3b8" }, dataBackground: { lineStyle: { color: "#cbd5e1" }, areaStyle: { color: "#f1f5f9" } }, selectedDataBackground: { lineStyle: { color: "#94a3b8" }, areaStyle: { color: "#e2e8f0" } }, textStyle: { fontSize: 9, color: "#6b7280" } }
      ],
      series: [
        {
          id: "k_" + code,
          name: s.name,
          type: "candlestick",
          data: kData,
          xAxisIndex: 0, yAxisIndex: 0,
          itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN, borderWidth: 1 },
          markLine: { symbol: "none", silent: true, data: markLines, animation: false },
          z: 2
        }
      ].concat(maSeries).concat([
        {
          name: "成交量", type: "bar", data: volData, xAxisIndex: 1, yAxisIndex: 1,
          itemStyle: { color: volColor }, barWidth: "58%", large: true
        },
        {
          name: "MACD", type: "bar", data: macdData, xAxisIndex: 2, yAxisIndex: 2,
          itemStyle: { color: macdColor }, barWidth: "58%"
        },
        {
          name: "DIF", type: "line", data: difData, xAxisIndex: 2, yAxisIndex: 2,
          symbol: "none", smooth: true, lineStyle: { width: 1, color: "#f59e0b" }, itemStyle: { color: "#f59e0b" }
        },
        {
          name: "DEA", type: "line", data: deaData, xAxisIndex: 2, yAxisIndex: 2,
          symbol: "none", smooth: true, lineStyle: { width: 1, color: "#1d4ed8" }, itemStyle: { color: "#1d4ed8" }
        }
      ])
    };
  }

  var charts = [];
  function initOne(el) {
    var code = el.getAttribute("data-code");
    if (!code || !window.__KLINE__ || !window.__KLINE__.series[code]) return;
    var chart = echarts.init(el, null, { renderer: "canvas" });
    chart.setOption(buildOption(code));
    charts.push(chart);
    el.setAttribute("data-ready", "1");
  }

  function boot() {
    var els = Array.prototype.slice.call(document.querySelectorAll(".kchart[data-code]"));
    if (!("IntersectionObserver" in window)) {
      els.forEach(initOne);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && en.target.getAttribute("data-ready") !== "1") {
          initOne(en.target);
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "300px 0px" });
    els.forEach(function (el) { io.observe(el); });
  }

  var rt;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { charts.forEach(function (c) { c.resize(); }); }, 160);
  });

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
