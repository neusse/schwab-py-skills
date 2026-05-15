const scenarios = {
  base: {
    last: 298.21,
    change: "+1.18%",
    decision: "Bullish continuation, wait for confirmation",
    body:
      "Price is above VWAP with rising relative volume, but the nearest option chain shows crowded 300 call activity. Codex recommends a conditional plan, not a market chase.",
    confidence: "78%",
    risk: "Medium",
    window: "18m",
    color: "#1a8f68",
    data: [291.8, 292.4, 293.1, 292.7, 294.6, 296.2, 295.8, 297.1, 298.4, 297.9, 298.21],
    plan: {
      title: "Conditional bracket, no live mutation",
      text:
        "Codex builds the order JSON, previews risk, and stops before live placement unless the explicit confirmation flag is provided.",
      json: {
        workflow: "dry_run_first",
        symbol: "AAPL",
        trigger: "break above 299.20 with volume confirmation",
        entry: { type: "LIMIT", side: "BUY", quantity: 1, max_price: 299.35 },
        exits: {
          profit_target: 311.25,
          stop_loss: 292.75,
          risk_reward: "1 : 1.8",
        },
        safety: "requires --confirm-live-order for placement",
      },
    },
  },
  breakout: {
    last: 301.06,
    change: "+2.14%",
    decision: "Breakout confirmed, scale risk slowly",
    body:
      "The 300 strike turned from resistance into support while breadth improved. Codex favors a smaller starter position with a tight invalidation point.",
    confidence: "84%",
    risk: "Medium",
    window: "11m",
    color: "#1a8f68",
    data: [291.8, 293.4, 294.2, 295.1, 296.8, 298.2, 299.4, 300.1, 301.7, 300.8, 301.06],
    plan: {
      title: "Starter bracket after retest",
      text:
        "The plan waits for a retest instead of buying the first spike, then uses a bracket exit to keep live risk bounded.",
      json: {
        workflow: "preview_then_decide",
        symbol: "AAPL",
        trigger: "hold 300.00 for two 1-minute bars",
        entry: { type: "LIMIT", side: "BUY", quantity: 1, max_price: 300.65 },
        exits: {
          profit_target: 312.90,
          stop_loss: 296.80,
          risk_reward: "1 : 2.1",
        },
        safety: "dry-run JSON only",
      },
    },
  },
  fade: {
    last: 294.38,
    change: "-0.47%",
    decision: "Momentum faded, preserve capital",
    body:
      "Price lost VWAP while put deltas firmed near 295. Codex downgrades the setup and recommends alerts only until structure improves.",
    confidence: "71%",
    risk: "High",
    window: "34m",
    color: "#b94a48",
    data: [298.9, 298.4, 297.5, 298.1, 296.7, 296.1, 295.8, 294.9, 295.3, 294.7, 294.38],
    plan: {
      title: "No trade, alert-only posture",
      text:
        "The decision engine suppresses order generation because the setup no longer matches the bullish continuation thesis.",
      json: {
        workflow: "alert_only",
        symbol: "AAPL",
        trigger: "recover VWAP and reclaim 297.50",
        action: "watchlist alert",
        suppressed_order_reason: "risk expanded while confidence declined",
        safety: "no live mutation path generated",
      },
    },
  },
};

const alerts = [
  {
    level: "high",
    title: "VWAP reclaim with volume expansion",
    meta: "AAPL moved above VWAP while 5-minute volume ran 1.8x the prior window.",
    confidence: "86%",
  },
  {
    level: "medium",
    title: "300 call wall detected",
    meta: "Near-money chain shows heavy 300 call volume. Treat as magnet or resistance.",
    confidence: "79%",
  },
  {
    level: "medium",
    title: "Portfolio exposure check",
    meta: "Existing tech beta is elevated. Position size should stay below the normal unit.",
    confidence: "74%",
  },
  {
    level: "watch",
    title: "Refresh token horizon",
    meta: "Auth is healthy, but the refresh token lifecycle should be visible before long sessions.",
    confidence: "92%",
  },
];

const options = [
  { strike: 295, call: "4.55 d .69", put: "1.33 d -.31" },
  { strike: 297.5, call: "3.04 d .55", put: "2.19 d -.45" },
  { strike: 300, call: "1.90 d .40", put: "3.68 d -.60" },
  { strike: 302.5, call: "1.07 d .27", put: "5.32 d -.73" },
  { strike: 305, call: "0.60 d .17", put: "7.75 d -.83" },
];

const tape = [
  ["AAPL", "+1.18", "up"],
  ["MSFT", "-0.22", "down"],
  ["NVDA", "+2.41", "up"],
  ["SPY", "+0.38", "up"],
  ["QQQ", "+0.71", "up"],
];

const reasoning = [
  "Read Schwab quote and price-history shaped data, then normalized the intraday series against VWAP.",
  "Compared the latest price to near-money option strikes to identify pressure around 300.",
  "Scored alerts by actionability, confidence, and whether the user would need to act immediately.",
  "Checked order safety rules from schwab-py-skills and produced only dry-run order intent.",
  "Generated repeatable Codex prompts so the same analysis can be rerun against live data.",
];

const els = {
  clock: document.querySelector("#clock"),
  chart: document.querySelector("#priceChart"),
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

let activeScenario = "base";
let animationPhase = 0;

function formatPrice(value) {
  return `$${value.toFixed(2)}`;
}

function drawChart() {
  const canvas = els.chart;
  const ctx = canvas.getContext("2d");
  const scenario = scenarios[activeScenario];
  const width = canvas.width;
  const height = canvas.height;
  const padding = 34;
  const values = scenario.data;
  const min = Math.min(...values) - 1.2;
  const max = Math.max(...values) + 1.2;
  const progress = Math.min(1, animationPhase / 45);

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

  const xFor = (index) => padding + (index / (values.length - 1)) * (width - padding * 2);
  const yFor = (value) => height - padding - ((value - min) / (max - min)) * (height - padding * 2);
  const visible = Math.max(2, Math.floor(values.length * progress));

  const vwap = values.reduce((sum, value) => sum + value, 0) / values.length;
  const alert = activeScenario === "fade" ? 297.5 : 300;
  const stop = activeScenario === "fade" ? 293.5 : 292.75;
  [
    [vwap, "#1a8f68"],
    [alert, "#c9891e"],
    [stop, "#b94a48"],
  ].forEach(([value, color]) => {
    ctx.strokeStyle = color;
    ctx.setLineDash([7, 8]);
    ctx.beginPath();
    ctx.moveTo(padding, yFor(value));
    ctx.lineTo(width - padding, yFor(value));
    ctx.stroke();
  });
  ctx.setLineDash([]);

  ctx.strokeStyle = scenario.color;
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
  ctx.fillStyle = scenario.color;
  ctx.beginPath();
  ctx.arc(lastX, lastY, 8 + Math.sin(animationPhase / 6) * 1.8, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#151515";
  ctx.font = "700 22px Inter, sans-serif";
  ctx.fillText(formatPrice(values[lastIndex]), Math.min(lastX + 14, width - 150), Math.max(30, lastY - 14));

  animationPhase += 1;
  requestAnimationFrame(drawChart);
}

function renderScenario(name) {
  activeScenario = name;
  animationPhase = 0;
  const scenario = scenarios[name];
  els.lastPrice.textContent = formatPrice(scenario.last);
  els.priceChange.textContent = scenario.change;
  els.priceChange.style.color = scenario.color;
  els.title.textContent = scenario.decision;
  els.body.textContent = scenario.body;
  els.confidence.textContent = scenario.confidence;
  els.risk.textContent = scenario.risk;
  els.window.textContent = scenario.window;
  els.planTitle.textContent = scenario.plan.title;
  els.planText.textContent = scenario.plan.text;
  els.orderPlan.textContent = JSON.stringify(scenario.plan.json, null, 2);
}

function renderAlerts() {
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

function renderOptions() {
  els.options.innerHTML = `
    <div class="optionRow header">
      <span>Strike</span><span>Call</span><span>Put</span>
    </div>
    ${options
      .map(
        (row) => `
          <div class="optionRow">
            <strong>${row.strike}</strong>
            <span class="optionCell"><strong>${row.call}</strong><span class="optionMeta">bid/ask context available from Schwab</span></span>
            <span class="optionCell"><strong>${row.put}</strong><span class="optionMeta">delta read into risk engine</span></span>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderTape() {
  els.tape.innerHTML = tape
    .map(
      ([symbol, move, direction], index) => `
        <div class="tapeItem ${direction}" style="animation-delay:${index * 70}ms">
          <strong>${symbol}</strong>
          <span>${move}%</span>
        </div>
      `,
    )
    .join("");
}

function renderReasoning() {
  els.reasoning.innerHTML = reasoning.map((item) => `<li>${item}</li>`).join("");
}

function updateClock() {
  els.clock.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

document.querySelectorAll(".segment").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".segment").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderScenario(button.dataset.scenario);
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

renderScenario("base");
renderAlerts();
renderOptions();
renderTape();
renderReasoning();
updateClock();
setInterval(updateClock, 1000);
drawChart();
