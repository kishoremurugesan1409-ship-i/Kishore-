// ---------- Setup ----------
const map = L.map('map', { zoomControl: false, attributionControl: false }).setView([11.0168, 76.9558], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

const pulseIcon = L.divIcon({ className: 'pulse-marker', iconSize: [16, 16] });
let marker = L.marker([11.0168, 76.9558], { icon: pulseIcon }).addTo(map);

const sparkCanvas = document.getElementById('sparkline');
const sparkCtx = sparkCanvas.getContext('2d');
let sparkHistory = [];
const SPARK_MAX_POINTS = 60;

function resizeCanvas() {
  sparkCanvas.width = sparkCanvas.clientWidth * devicePixelRatio;
  sparkCanvas.height = sparkCanvas.clientHeight * devicePixelRatio;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// ---------- Clock ----------
function tickClock() {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString();
}
setInterval(tickClock, 1000);
tickClock();

// ---------- Gauge ----------
const GAUGE_MAX_G = 15;
const GAUGE_DASH_TOTAL = 267;

function updateGauge(g) {
  const pct = Math.min(g / GAUGE_MAX_G, 1);
  const offset = GAUGE_DASH_TOTAL - pct * GAUGE_DASH_TOTAL;
  const fill = document.getElementById('gaugeFill');
  fill.style.strokeDashoffset = offset;

  let color = '#34d399'; // green
  if (g >= 4.0) color = '#ff4d5e';       // red - alert zone
  else if (g >= 2.0) color = '#ffb454';  // amber - elevated
  fill.style.stroke = color;

  document.getElementById('gForceValue').textContent = g.toFixed(2);
}

// ---------- Sparkline ----------
function drawSparkline() {
  const w = sparkCanvas.width, h = sparkCanvas.height;
  sparkCtx.clearRect(0, 0, w, h);
  if (sparkHistory.length < 2) return;

  const max = Math.max(GAUGE_MAX_G, ...sparkHistory);
  const step = w / (SPARK_MAX_POINTS - 1);

  sparkCtx.beginPath();
  sparkHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - (val / max) * h * 0.9 - h * 0.05;
    if (i === 0) sparkCtx.moveTo(x, y);
    else sparkCtx.lineTo(x, y);
  });
  sparkCtx.strokeStyle = '#ff4d5e';
  sparkCtx.lineWidth = 2 * devicePixelRatio;
  sparkCtx.stroke();

  // threshold line
  const thresholdY = h - (4.0 / max) * h * 0.9 - h * 0.05;
  sparkCtx.beginPath();
  sparkCtx.setLineDash([4, 4]);
  sparkCtx.moveTo(0, thresholdY);
  sparkCtx.lineTo(w, thresholdY);
  sparkCtx.strokeStyle = 'rgba(255,180,84,0.5)';
  sparkCtx.lineWidth = 1 * devicePixelRatio;
  sparkCtx.stroke();
  sparkCtx.setLineDash([]);
}

// ---------- Alert rendering ----------
function renderAlerts(alerts) {
  const list = document.getElementById('alertList');
  document.getElementById('alertCount').textContent = alerts.length;

  if (alerts.length === 0) {
    list.innerHTML = '<div class="alert-empty">No accidents detected. System nominal.</div>';
    return;
  }

  list.innerHTML = alerts.map(a => `
    <div class="alert-item">
      <div class="alert-item-head">
        <span>#${a.id}</span>
        <span>${a.time_readable}</span>
      </div>
      <div class="alert-item-body">
        <span class="label">Impact:</span> ${a.impact_g}g &nbsp;
        <span class="label">Speed:</span> ${a.speed_at_impact_kmph} km/h<br>
        <span class="label">Location:</span> ${a.location.lat}, ${a.location.lon}<br>
        <span class="label">Notified:</span> ${a.notified.join(', ')}
      </div>
    </div>
  `).join('');
}

function showBanner(alert) {
  const banner = document.getElementById('alertBanner');
  document.getElementById('bannerDetail').textContent =
    `Impact ${alert.impact_g}g at ${alert.location.lat}, ${alert.location.lon} — emergency contacts notified`;
  banner.classList.add('show');
  setTimeout(() => banner.classList.remove('show'), 4500);
}

// ---------- Polling ----------
let lastAlertCount = 0;

async function pollStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const reading = data.reading;

    updateGauge(reading.accel.magnitude);
    document.getElementById('speedValue').innerHTML = `${reading.speed_kmph}<small>km/h</small>`;
    document.getElementById('accelX').textContent = reading.accel.x.toFixed(3);
    document.getElementById('accelY').textContent = reading.accel.y.toFixed(3);
    document.getElementById('accelZ').textContent = reading.accel.z.toFixed(3);
    document.getElementById('thresholdValue').textContent = data.threshold_g.toFixed(1);
    document.getElementById('coordsReadout').textContent = `${reading.gps.lat}, ${reading.gps.lon}`;

    marker.setLatLng([reading.gps.lat, reading.gps.lon]);
    map.panTo([reading.gps.lat, reading.gps.lon]);

    sparkHistory.push(reading.accel.magnitude);
    if (sparkHistory.length > SPARK_MAX_POINTS) sparkHistory.shift();
    drawSparkline();

    const chip = document.getElementById('monitoringChip');
    if (data.monitoring_active) {
      chip.classList.remove('paused');
      chip.innerHTML = '<span class="dot dot-live"></span> MONITORING';
    } else {
      chip.classList.add('paused');
      chip.innerHTML = '<span class="dot"></span> PAUSED';
    }

    if (data.alert_count > lastAlertCount) {
      lastAlertCount = data.alert_count;
      fetchAlerts();
    }
  } catch (err) {
    console.error('status poll failed', err);
  }
}

async function fetchAlerts() {
  const res = await fetch('/api/alerts');
  const alerts = await res.json();
  renderAlerts(alerts);
  if (alerts.length > 0) showBanner(alerts[0]);
}

// ---------- Crash simulation button ----------
document.getElementById('crashBtn').addEventListener('click', async () => {
  const btn = document.getElementById('crashBtn');
  btn.classList.add('pulsing');
  setTimeout(() => btn.classList.remove('pulsing'), 900);

  const res = await fetch('/api/simulate-crash', { method: 'POST' });
  const data = await res.json();
  if (data.alert) {
    lastAlertCount = data.alert ? lastAlertCount + 1 : lastAlertCount;
    fetchAlerts();
  }
});

// ---------- Init ----------
setInterval(pollStatus, 1200);
pollStatus();
fetchAlerts();
