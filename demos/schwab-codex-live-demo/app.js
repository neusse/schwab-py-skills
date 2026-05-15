const els = {
  clock: document.querySelector("#clock"),
  chart: document.querySelector("#priceChart"),
  symbolName: document.querySelector("#symbolName"),
  lastPrice: document.querySelector("#lastPrice"),
  priceChange: document.querySelector("#priceChange"),
  title: document.querySelector("#decisionTitle"),
  body: document.querySelector("#decisionBody"),
  confidence: document.querySelector("#confidence"),
  risk: document.querySelector("#riskScore"),
  window: document.querySelector("#timeWindow"),
  planTitle: document.querySelector("#planTitle"),
  planText: document.querySelector("#planText"),
  orderPlan: document.querySelector("#orderPlan"),
  alerts: document.querySelector("#alerts"),
  options: document.querySelector("#optionsTable"),
  tape: document.querySelector("#tickerTape"),
  drawer: document.querySelector("#explainDrawer"),
  reasoning: document.querySelector("#reasoningList"),
  toast: document.querySelector("#toast"),
};

let activeData = null;
let animationPhase = 0;

function formatPrice(value) {
  return `$${Number(value).toFixed(2)}`;
}

function formatMove(value) {
  const number = Number(value || 0);
  return `${number >= 0 ? "+" : ""}${number.toFixed(2)}%`;
}

function compactVolume(value) {
  const number = Number(value || 0);
  if (number >= 1000000) return `${(number / 1000000).toFixed(1)}M`;
  if (number >= 1000) return `${(number / 1000).toFixed(1)}K`;
  return String(number);
}

function drawChart() {
  const canvas = els.chart;
  const ctx = canvas.getContext("2d");
  const points = activeData?.history?.chart || [];
  const width = canvas.width;
  const height = canvas.height;
  const padding = 34;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fffdf8";
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = "rgba(21, 21, 21, 0.09)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i += 1) {
    const y = padding + ((height - padding * 2) / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    ctx.stroke();
  }

  if (points.length < 2) {
    ctx.fillStyle = "#6e6a61";
    ctx.font = "700 22px Inter, sans-serif";
    ctx.fillText("Waiting for live Schwab data", padding, height / 2);
    requestAnimationFrame(drawChart);
    return;
  }

  const values = points.map((point) => Number(point.close));
  const min = Math.min(...values) - 1;
  const max = Math.max(...values) + 1;
  const color = Number(activeData.quote.net_pct) >= 0 ? "#1a8f68" : "#b94a48";
  const progress = Math.min(1, animationPhase / 45);
  const visible = Math.max(2, Math.floor(values.length * progress));
  const xFor = (index) => padding + (index / (values.length - 1)) * (width - padding * 2);
  const yFor = (value) => height - padding - ((value - min) / (max - min)) * (height - padding * 2);

  const pivot = activeData.decision.levels.pivot;
  const support = activeData.decision.levels.support[0];
  const resistance = activeData.decision.levels.resistance[0];
  [
    [pivot, "#c9891e"],
    [support, "#b94a48"],
    [resistance, "#1a8f68"],
  ].forEach(([value, lineColor]) => {
    ctx.strokeStyle = lineColor;
    ctx.setLineDash([7, 8]);
    ctx.beginPath();
    ctx.moveTo(padding, yFor(value));
    ctx.lineTo(width - padding, yFor(value));
    ctx.stroke();
  });
  ctx.setLineDash([]);

  ctx.strokeStyle = color;
  ctx.lineWidth = 5;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.beginPath();
  values.slice(0, visible).forEach((value, index) => {
    const x = xFor(index);
    const y = yFor(value);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  const lastIndex = visible - 1;
  const lastX = xFor(lastIndex);
  const lastY = yFor(values[lastIndex]);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(lastX, lastY, 8 + Math.sin(animationPhase / 6) * 1.8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#151515";
  ctx.font = "700 22px Inter, sans-serif";
  ctx.fillText(formatPrice(values[lastIndex]), Math.min(lastX + 14, width - 160), Math.max(30, lastY - 14));
  animationPhase += 1;
  requestAnimationFrame(drawChart);
}

function renderContext(data) {
  activeData = data;
  animationPhase = 0;
  const quote = data.quote;
  const decision = data.decision;
  const color = Number(quote.net_pct) >= 0 ? "#1a8f68" : "#b94a48";

  els.symbolName.textContent = quote.symbol;
  els.lastPrice.textContent = formatPrice(quote.last);
  els.priceChange.textContent = `${formatMove(quote.net_pct)} (${Number(quote.net || 0).toFixed(2)})`;
  els.priceChange.style.color = color;
  els.title.textContent = decision.title;
  els.body.textContent = decision.body;
  els.confidence.textContent = decision.confidence;
  els.risk.textContent = decision.risk;
  els.window.textContent = decision.stance;
  els.planTitle.textContent = decision.plan.title;
  els.planText.textContent = decision.plan.text;
  els.orderPlan.textContent = JSON.stringify(decision.plan.json, null, 2);
  renderAlerts(decision.alerts);
  renderOptions(data.options);
  renderTape(data);
  renderReasoning(decision.reasoning);
}

function renderAlerts(alerts) {
  els.alerts.innerHTML = alerts
    .map(
      (alert) => `
        <article class="alertRow">
          <span class="badge ${alert.level}">${alert.level}</span>
          <div>
            <div class="alertTitle">${alert.title}</div>
            <div class="alertMeta">${alert.meta}</div>
          </div>
          <div class="confidence">${alert.confidence}</div>
        </article>
      `,
    )
    .join("");
}

function optionText(option) {
  return `${option.bid ?? ""}/${option.ask ?? ""}/${option.last ?? ""} d ${option.delta ?? ""}`;
}

function renderOptions(options) {
  const expiration = options.expiration || "nearest";
  document.querySelector(".optionPane .sectionHeader span").textContent = expiration;
  els.options.innerHTML = `
    <div class="optionRow header">
      <span>Strike</span><span>Call</span><span>Put</span>
    </div>
    ${options.rows
      .map(
        (row) => `
          <div class="optionRow">
            <strong>${row.strike}</strong>
            <span class="optionCell"><strong>${optionText(row.call)}</strong><span class="optionMeta">gamma ${row.call.gamma ?? ""}, theta ${row.call.theta ?? ""}</span></span>
            <span class="optionCell"><strong>${optionText(row.put)}</strong><span class="optionMeta">gamma ${row.put.gamma ?? ""}, theta ${row.put.theta ?? ""}</span></span>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderTape(data) {
  const q = data.quote;
  const history = data.history;
  const tape = [
    [q.symbol, formatMove(q.net_pct), Number(q.net_pct) >= 0 ? "up" : "down"],
    ["BID", q.bid, "up"],
    ["ASK", q.ask, "up"],
    ["VOL", compactVolume(q.volume), "up"],
    ["5D", formatMove(history.period_change_pct), Number(history.period_change_pct) >= 0 ? "up" : "down"],
  ];
  els.tape.innerHTML = tape
    .map(
      ([label, value, direction], index) => `
        <div class="tapeItem ${direction}" style="animation-delay:${index * 70}ms">
          <strong>${label}</strong>
          <span>${value}</span>
        </div>
      `,
    )
    .join("");
}

function renderReasoning(reasoning) {
  els.reasoning.innerHTML = reasoning.map((item) => `<li>${item}</li>`).join("");
}

async function loadSymbol(symbol) {
  els.title.textContent = `Loading ${symbol} from Schwab...`;
  els.body.textContent = "Fetching quote, 5-day history, and option chain through schwab-py-skills.";
  const response = await fetch(`/api/context?symbol=${encodeURIComponent(symbol)}`);
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.error || `Request failed with ${response.status}`);
  }
  renderContext(data);
}

function updateClock() {
  els.clock.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

document.querySelectorAll(".segment").forEach((button) => {
  button.addEventListener("click", async () => {
    document.querySelectorAll(".segment").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    try {
      await loadSymbol(button.dataset.symbol);
    } catch (error) {
      els.title.textContent = "Live data request failed";
      els.body.textContent = error.message;
    }
  });
});

document.querySelector("#explainButton").addEventListener("click", () => {
  els.drawer.classList.add("open");
  els.drawer.setAttribute("aria-hidden", "false");
});

document.querySelector("#closeDrawer").addEventListener("click", () => {
  els.drawer.classList.remove("open");
  els.drawer.setAttribute("aria-hidden", "true");
});

document.querySelectorAll(".copyPrompt").forEach((button) => {
  button.addEventListener("click", async () => {
    const prompt = button.dataset.prompt;
    try {
      await navigator.clipboard.writeText(prompt);
    } catch {
      window.prompt("Copy this prompt", prompt);
    }
    els.toast.classList.add("show");
    setTimeout(() => els.toast.classList.remove("show"), 1200);
  });
});

document.querySelectorAll(".railButton").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".railButton").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    const target =
      button.dataset.view === "alerts"
        ? ".signalPane"
        : button.dataset.view === "options"
          ? ".optionPane"
          : button.dataset.view === "orders"
            ? ".planArea"
            : ".topbar";
    document.querySelector(target).scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

updateClock();
setInterval(updateClock, 1000);
drawChart();
loadSymbol("AAPL").catch((error) => {
  els.title.textContent = "Live data request failed";
  els.body.textContent = error.message;
});
