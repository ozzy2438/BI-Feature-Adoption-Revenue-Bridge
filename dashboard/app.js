// ═══════════════════════════════════════════════════════════
//  DATA: Embedded mart data from generated CSVs
// ═══════════════════════════════════════════════════════════

const FUNNEL_DATA = {
  months: ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09'],
  steps: ['Signup','First Invoice Created','First Payment Received','App Integration Connected','Plan Upgrade'],
  byMonth: {
    '2024-01': {users:[272,203,159,52,0], conv:[1.0,0.746,0.783,0.327,0.0], drop:[0,0.254,0.217,0.673,1.0]},
    '2024-02': {users:[317,245,188,100,7], conv:[1.0,0.773,0.767,0.532,0.07], drop:[0,0.227,0.233,0.468,0.93]},
    '2024-03': {users:[294,242,199,128,17], conv:[1.0,0.823,0.822,0.643,0.133], drop:[0,0.177,0.178,0.357,0.867]},
    '2024-04': {users:[258,182,148,98,28], conv:[1.0,0.705,0.813,0.662,0.286], drop:[0,0.295,0.187,0.338,0.714]},
    '2024-05': {users:[276,214,167,92,37], conv:[1.0,0.775,0.780,0.551,0.402], drop:[0,0.225,0.220,0.449,0.598]},
    '2024-06': {users:[265,204,168,107,24], conv:[1.0,0.770,0.824,0.637,0.224], drop:[0,0.230,0.177,0.363,0.776]},
    '2024-07': {users:[254,211,185,99,31], conv:[1.0,0.831,0.877,0.535,0.313], drop:[0,0.169,0.123,0.465,0.687]},
    '2024-08': {users:[285,218,188,119,21], conv:[1.0,0.765,0.862,0.633,0.177], drop:[0,0.235,0.138,0.367,0.824]},
    '2024-09': {users:[279,211,166,99,25], conv:[1.0,0.756,0.787,0.596,0.253], drop:[0,0.244,0.213,0.404,0.748]}
  }
};

const COHORT_DATA = {
  cohorts: ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10'],
  sizes: [159,188,199,148,167,168,185,188,166,37],
  retention: {
    '2024-01': [1.0,1.0,1.0,1.0,0.994,0.962,0.937,0.918,0.912,0.906,0.881,0.881,0.881],
    '2024-02': [1.0,1.0,1.0,1.0,0.984,0.957,0.947,0.926,0.910,0.883,0.878,0.878,0.878],
    '2024-03': [1.0,1.0,1.0,1.0,0.980,0.970,0.955,0.940,0.895,0.869,0.839],
    '2024-04': [1.0,1.0,1.0,1.0,0.980,0.953,0.932,0.899,0.892,0.865,0.824],
    '2024-05': [1.0,1.0,1.0,1.0,0.970,0.946,0.934,0.928,0.892,0.862,0.838],
    '2024-06': [1.0,1.0,1.0,1.0,0.994,0.970,0.946,0.911,0.899,0.869,0.839],
    '2024-07': [1.0,1.0,1.0,1.0,0.973,0.968,0.951,0.924,0.897,0.860,0.827],
    '2024-08': [1.0,1.0,1.0,1.0,0.957,0.936,0.888,0.888,0.872,0.872,0.856],
    '2024-09': [1.0,1.0,1.0,1.0,0.988,0.970,0.940,0.916,0.861,0.819],
    '2024-10': [1.0,1.0,1.0,1.0,1.0,0.973,0.946,0.919,0.892]
  }
};

const ADOPTION_DATA = {
  months: ['2024-01','2024-02','2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12','2025-01','2025-02','2025-03','2025-04','2025-05','2025-06'],
  bank_feed_sync: {
    rate: [0.050,0.184,0.244,0.274,0.290,0.294,0.306,0.306,0.311,0.337,0.346,0.348,0.346,0.345,0.345,0.344,0.343,0.342],
    eligible: [159,347,546,694,860,1020,1192,1370,1519,1541,1507,1486,1455,1425,1405,1385,1369,1358],
    adopted: [8,64,133,190,249,300,365,419,472,520,521,517,504,491,484,476,470,465]
  }
};

const BRIDGE_DATA = [
  {q:'2024 Q1', components:{'New Customers':27264, 'Plan Upgrade':1035, 'Feature Adoption Lift':1350, 'Other/Residual':0}},
  {q:'2024 Q2', components:{'New Customers':24207, 'Plan Upgrade':3895, 'Feature Adoption Lift':1920, 'Other/Residual':-2531}},
  {q:'2024 Q3', components:{'New Customers':26996, 'Plan Upgrade':3265, 'Feature Adoption Lift':2130, 'Other/Residual':-4525}},
  {q:'2024 Q4', components:{'New Customers':1968, 'Plan Upgrade':2950, 'Feature Adoption Lift':795, 'Other/Residual':-5835}}
];

const IMPACT_DATA = {
  bank_feed_sync: { adopted: {churnRate:0.014, avgMrr:59.4, contRate:0.063}, not_adopted: {churnRate:0.005, avgMrr:20.1, contRate:0.0} },
  feature_count: { '0': {churnRate:0.005, avgMrr:20.1, accounts:2040}, '1': {churnRate:0.014, avgMrr:59.4, accounts:460} }
};

// ═══════════════════════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════════════════════
function switchPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
  document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
}

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(148,163,184,0.1)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';

// ═══════════════════════════════════════════════════════════
//  PAGE 1: FUNNEL
// ═══════════════════════════════════════════════════════════
function renderFunnel(month) {
  const d = FUNNEL_DATA.byMonth[month]; if (!d) return;
  const maxUsers = d.users[0];
  FUNNEL_DATA.steps.forEach((step, i) => {
    const bar = document.getElementById(`funnel-bar-${i}`);
    const val = document.getElementById(`funnel-val-${i}`);
    const conv = document.getElementById(`funnel-conv-${i}`);
    if (bar) { const pct = maxUsers > 0 ? (d.users[i] / maxUsers * 100) : 0; bar.style.width = pct + '%'; val.textContent = d.users[i].toLocaleString(); conv.textContent = i === 0 ? '100%' : (d.conv[i] * 100).toFixed(1) + '%'; }
  });
  const tbody = document.getElementById('funnel-table-body'); tbody.innerHTML = '';
  FUNNEL_DATA.steps.forEach((step, i) => {
    const row = document.createElement('tr'); const convPct = (d.conv[i] * 100).toFixed(1); const dropPct = (d.drop[i] * 100).toFixed(1);
    row.innerHTML = `<td>${step}</td><td style="font-weight:600">${d.users[i].toLocaleString()}</td><td><span class="badge ${i === 0 ? 'badge-neutral' : parseFloat(convPct) > 70 ? 'badge-positive' : 'badge-negative'}">${convPct}%</span></td><td><span class="badge ${parseFloat(dropPct) > 30 ? 'badge-negative' : 'badge-positive'}">${dropPct}%</span></td>`;
    tbody.appendChild(row);
  });
  document.getElementById('kpi-signups').textContent = d.users[0].toLocaleString();
  document.getElementById('kpi-paid').textContent = d.users[2].toLocaleString();
  document.getElementById('kpi-overall-conv').textContent = (maxUsers > 0 ? (d.users[2] / maxUsers * 100).toFixed(1) : '0') + '%';
  const biggestDrop = d.drop.reduce((max, v, i) => v > max.v ? {v, i} : max, {v:0, i:0});
  document.getElementById('kpi-biggest-drop').textContent = FUNNEL_DATA.steps[biggestDrop.i];
}

let funnelTrendChart;
function renderFunnelTrend() {
  const ctx = document.getElementById('funnel-trend-chart').getContext('2d');
  const colors = ['#3b82f6','#8b5cf6','#06b6d4','#f59e0b','#f43f5e'];
  const datasets = FUNNEL_DATA.steps.map((step, i) => ({ label: step, data: FUNNEL_DATA.months.map(m => FUNNEL_DATA.byMonth[m].users[i]), borderColor: colors[i], backgroundColor: colors[i] + '20', borderWidth: 2, pointRadius: 3, pointHoverRadius: 6, tension: 0.4, fill: false }));
  funnelTrendChart = new Chart(ctx, { type: 'line', data: { labels: FUNNEL_DATA.months.map(m => m.substring(5)), datasets }, options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
}

// ═══════════════════════════════════════════════════════════
//  PAGE 2: COHORT RETENTION
// ═══════════════════════════════════════════════════════════
function renderCohortHeatmap() {
  const container = document.getElementById('cohort-heatmap');
  let html = '<table class="heatmap"><thead><tr><th>Cohort</th><th>Size</th>';
  for (let i = 0; i <= 12; i++) html += `<th>M+${i}</th>`;
  html += '</tr></thead><tbody>';
  let m6Rates = [];
  COHORT_DATA.cohorts.forEach((cohort, ci) => {
    const rates = COHORT_DATA.retention[cohort];
    html += `<tr><td class="label-cell">${cohort}</td><td class="label-cell">${COHORT_DATA.sizes[ci]}</td>`;
    for (let age = 0; age <= 12; age++) {
      if (age < rates.length) { const r = rates[age]; const pct = (r * 100).toFixed(0); const bg = retentionColor(r); html += `<td style="background:${bg};color:${r > 0.5 ? '#fff' : '#ddd'}" title="${cohort} M+${age}: ${pct}%">${pct}%</td>`; if (age === 6) m6Rates.push(r); }
      else { html += '<td style="background:rgba(30,38,64,0.3)">—</td>'; }
    }
    html += '</tr>';
  });
  html += '</tbody></table>'; container.innerHTML = html;
  const avgM6 = m6Rates.length > 0 ? (m6Rates.reduce((a,b)=>a+b,0)/m6Rates.length*100).toFixed(1) : 'N/A';
  document.getElementById('kpi-m6-retention').textContent = avgM6 + '%';
  document.getElementById('kpi-cohorts-count').textContent = COHORT_DATA.cohorts.length;
  document.getElementById('kpi-best-cohort').textContent = COHORT_DATA.cohorts[m6Rates.indexOf(Math.max(...m6Rates))];
  document.getElementById('kpi-worst-cohort').textContent = COHORT_DATA.cohorts[m6Rates.indexOf(Math.min(...m6Rates))];
}
function retentionColor(rate) { if (rate >= 0.95) return 'rgba(16,185,129,0.7)'; if (rate >= 0.90) return 'rgba(16,185,129,0.5)'; if (rate >= 0.85) return 'rgba(59,130,246,0.5)'; if (rate >= 0.80) return 'rgba(139,92,246,0.4)'; return 'rgba(244,63,94,0.4)'; }

let cohortLineChart;
function renderCohortCurves() {
  const ctx = document.getElementById('cohort-curve-chart').getContext('2d');
  const colors = ['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b','#f43f5e','#ec4899','#6366f1','#14b8a6','#a855f7'];
  const datasets = COHORT_DATA.cohorts.slice(0, 8).map((cohort, i) => ({ label: cohort, data: COHORT_DATA.retention[cohort].map(r => (r * 100).toFixed(1)), borderColor: colors[i], borderWidth: 2, pointRadius: 2, tension: 0.3, fill: false }));
  cohortLineChart = new Chart(ctx, { type: 'line', data: { labels: Array.from({length: 13}, (_, i) => `M+${i}`), datasets }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { size: 10 } } } }, scales: { y: { min: 75, max: 102, ticks: { callback: v => v + '%' }, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
}

// ═══════════════════════════════════════════════════════════
//  PAGE 3: FEATURE ADOPTION
// ═══════════════════════════════════════════════════════════
let adoptionLineChart, adoptionBarChart;
function renderAdoption() {
  const ctx1 = document.getElementById('adoption-trend-chart').getContext('2d');
  adoptionLineChart = new Chart(ctx1, { type: 'line', data: { labels: ADOPTION_DATA.months.map(m => m.substring(5)), datasets: [{ label: 'Bank Feed Sync', data: ADOPTION_DATA.bank_feed_sync.rate.map(r => (r * 100).toFixed(1)), borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', borderWidth: 3, pointRadius: 4, pointHoverRadius: 8, tension: 0.4, fill: true }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 40, ticks: { callback: v => v + '%' }, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
  const ctx2 = document.getElementById('adoption-bar-chart').getContext('2d');
  const lastIdx = ADOPTION_DATA.months.length - 1;
  adoptionBarChart = new Chart(ctx2, { type: 'bar', data: { labels: ['Eligible Accounts', 'Adopted Accounts'], datasets: [{ label: 'Bank Feed Sync', data: [ADOPTION_DATA.bank_feed_sync.eligible[lastIdx], ADOPTION_DATA.bank_feed_sync.adopted[lastIdx]], backgroundColor: ['rgba(59,130,246,0.6)', 'rgba(16,185,129,0.6)'], borderColor: ['#3b82f6', '#10b981'], borderWidth: 2, borderRadius: 8 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
  const latestRate = (ADOPTION_DATA.bank_feed_sync.rate[lastIdx] * 100).toFixed(1);
  document.getElementById('kpi-adoption-rate').textContent = latestRate + '%';
  document.getElementById('kpi-adopted-count').textContent = ADOPTION_DATA.bank_feed_sync.adopted[lastIdx].toLocaleString();
  document.getElementById('kpi-eligible-count').textContent = ADOPTION_DATA.bank_feed_sync.eligible[lastIdx].toLocaleString();
  document.getElementById('kpi-peak-adoption').textContent = (Math.max(...ADOPTION_DATA.bank_feed_sync.rate) * 100).toFixed(1) + '%';
}

// ═══════════════════════════════════════════════════════════
//  PAGE 4: REVENUE BRIDGE
// ═══════════════════════════════════════════════════════════
let bridgeChart;
function renderBridge(qIdx) {
  const q = BRIDGE_DATA[qIdx];
  const components = ['New Customers','Plan Upgrade','Feature Adoption Lift','Other/Residual'];
  const colors = ['#10b981','#3b82f6','#8b5cf6','#64748b'];
  const negColors = ['#10b981','#3b82f6','#8b5cf6','#f43f5e'];
  const vals = components.map(c => q.components[c] || 0);
  const total = vals.reduce((a, b) => a + b, 0);
  const maxAbs = Math.max(...vals.map(Math.abs));
  const waterfallContainer = document.getElementById('waterfall-bars'); waterfallContainer.innerHTML = '';
  components.forEach((comp, i) => {
    const amount = vals[i]; const isNeg = amount < 0; const pct = maxAbs > 0 ? (Math.abs(amount) / maxAbs * 100) : 0; const color = isNeg ? negColors[i] : colors[i];
    const bar = document.createElement('div'); bar.className = 'waterfall-bar';
    bar.innerHTML = `<div class="waterfall-label">${comp}</div><div class="waterfall-bar-track"><div class="waterfall-bar-fill" style="width:${pct}%;background:${color}">${pct > 15 ? '$' + Math.abs(amount).toLocaleString() : ''}</div></div><div class="waterfall-amount" style="color:${isNeg ? '#fb7185' : '#34d399'}">${isNeg ? '-' : '+'}$${Math.abs(amount).toLocaleString()}</div>`;
    waterfallContainer.appendChild(bar);
  });
  const netBar = document.createElement('div'); netBar.className = 'waterfall-bar'; netBar.style.borderTop = '2px solid rgba(148,163,184,0.2)'; netBar.style.paddingTop = '1rem';
  netBar.innerHTML = `<div class="waterfall-label" style="font-weight:700">Net MRR Delta</div><div class="waterfall-bar-track"><div class="waterfall-bar-fill" style="width:${maxAbs > 0 ? Math.abs(total)/maxAbs*100 : 0}%;background:${total >= 0 ? 'linear-gradient(135deg,#10b981,#06b6d4)' : 'linear-gradient(135deg,#f43f5e,#ec4899)'}">${'$' + Math.abs(total).toLocaleString()}</div></div><div class="waterfall-amount" style="color:${total >= 0 ? '#34d399' : '#fb7185'};font-size:1rem">${total >= 0 ? '+' : '-'}$${Math.abs(total).toLocaleString()}</div>`;
  waterfallContainer.appendChild(netBar);
  if (bridgeChart) bridgeChart.destroy();
  const ctx = document.getElementById('bridge-chart').getContext('2d');
  bridgeChart = new Chart(ctx, { type: 'bar', data: { labels: [...components, 'Net Delta'], datasets: [{ data: [...vals, total], backgroundColor: [...vals.map((v, i) => v < 0 ? '#f43f5e80' : colors[i] + '80'), total >= 0 ? '#10b98180' : '#f43f5e80'], borderColor: [...vals.map((v, i) => v < 0 ? '#f43f5e' : colors[i]), total >= 0 ? '#10b981' : '#f43f5e'], borderWidth: 2, borderRadius: 6 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(148,163,184,0.06)' }, ticks: { callback: v => '$' + v.toLocaleString() } }, x: { grid: { display: false } } } } });
  const positive = vals.filter(v => v > 0).reduce((a, b) => a + b, 0);
  document.getElementById('kpi-quarter-label').textContent = q.q;
  document.getElementById('kpi-positive-delta').textContent = '+$' + positive.toLocaleString();
  document.getElementById('kpi-net-delta').textContent = (total >= 0 ? '+$' : '-$') + Math.abs(total).toLocaleString();
  document.getElementById('kpi-lift-share').textContent = (positive > 0 ? ((q.components['Feature Adoption Lift'] || 0) / positive * 100).toFixed(1) : '0') + '%';
}

// ═══════════════════════════════════════════════════════════
//  PAGE 5: FEATURE IMPACT
// ═══════════════════════════════════════════════════════════
let impactChurnChart, impactMrrChart;
function renderImpact() {
  const ctx1 = document.getElementById('impact-churn-chart').getContext('2d');
  impactChurnChart = new Chart(ctx1, { type: 'bar', data: { labels: ['Bank Feed Sync'], datasets: [{ label: 'Adopted', data: [IMPACT_DATA.bank_feed_sync.adopted.churnRate * 100], backgroundColor: 'rgba(16,185,129,0.6)', borderColor: '#10b981', borderWidth: 2, borderRadius: 8 }, { label: 'Not Adopted', data: [IMPACT_DATA.bank_feed_sync.not_adopted.churnRate * 100], backgroundColor: 'rgba(244,63,94,0.6)', borderColor: '#f43f5e', borderWidth: 2, borderRadius: 8 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, ticks: { callback: v => v.toFixed(1) + '%' }, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
  const ctx2 = document.getElementById('impact-mrr-chart').getContext('2d');
  impactMrrChart = new Chart(ctx2, { type: 'bar', data: { labels: ['Bank Feed Sync'], datasets: [{ label: 'Adopted', data: [IMPACT_DATA.bank_feed_sync.adopted.avgMrr], backgroundColor: 'rgba(16,185,129,0.6)', borderColor: '#10b981', borderWidth: 2, borderRadius: 8 }, { label: 'Not Adopted', data: [IMPACT_DATA.bank_feed_sync.not_adopted.avgMrr], backgroundColor: 'rgba(244,63,94,0.6)', borderColor: '#f43f5e', borderWidth: 2, borderRadius: 8 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, ticks: { callback: v => '$' + v }, grid: { color: 'rgba(148,163,184,0.06)' } }, x: { grid: { display: false } } } } });
  const tbody = document.getElementById('impact-count-table'); tbody.innerHTML = '';
  ['0','1'].forEach(count => { const d = IMPACT_DATA.feature_count[count]; const row = document.createElement('tr'); row.innerHTML = `<td style="font-weight:600">${count} feature${count !== '1' ? 's' : ''}</td><td>${d.accounts.toLocaleString()}</td><td><span class="badge ${d.churnRate > 0.01 ? 'badge-negative' : 'badge-positive'}">${(d.churnRate*100).toFixed(2)}%</span></td><td style="font-weight:600;color:#34d399">$${d.avgMrr.toFixed(0)}</td>`; tbody.appendChild(row); });
  const mrrUplift = IMPACT_DATA.bank_feed_sync.adopted.avgMrr - IMPACT_DATA.bank_feed_sync.not_adopted.avgMrr;
  document.getElementById('kpi-mrr-uplift').textContent = '+$' + mrrUplift.toFixed(0);
  document.getElementById('kpi-churn-delta').textContent = ((IMPACT_DATA.bank_feed_sync.not_adopted.churnRate - IMPACT_DATA.bank_feed_sync.adopted.churnRate)*100).toFixed(2) + 'pp';
  document.getElementById('kpi-adopted-mrr').textContent = '$' + IMPACT_DATA.bank_feed_sync.adopted.avgMrr.toFixed(0);
  document.getElementById('kpi-nonadopt-mrr').textContent = '$' + IMPACT_DATA.bank_feed_sync.not_adopted.avgMrr.toFixed(0);
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('funnel-month-select');
  FUNNEL_DATA.months.forEach(m => { const opt = document.createElement('option'); opt.value = m; opt.textContent = m; select.appendChild(opt); });
  select.value = '2024-05'; select.addEventListener('change', () => renderFunnel(select.value));
  const qSelect = document.getElementById('bridge-quarter-select');
  BRIDGE_DATA.forEach((q, i) => { const opt = document.createElement('option'); opt.value = i; opt.textContent = q.q; qSelect.appendChild(opt); });
  qSelect.value = '2'; qSelect.addEventListener('change', () => renderBridge(parseInt(qSelect.value)));
  renderFunnel('2024-05'); renderFunnelTrend(); renderCohortHeatmap(); renderCohortCurves(); renderAdoption(); renderBridge(2); renderImpact();
  document.querySelectorAll('.nav-tab').forEach(tab => { tab.addEventListener('click', () => switchPage(tab.dataset.page)); });
});
