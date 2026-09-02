const CONFIG = {
  repoUrl: 'https://github.com/Carlping/recruiter-review-tw',
  formUrl: 'https://github.com/Carlping/recruiter-review-tw#參與方式', // 換成 Google Form 連結
};

const DIMS = ['responsiveness', 'transparency', 'professionalism', 'respect', 'closure'];
const state = { reviews: [], recruiters: [], tax: null, view: 'reviews' };
const $ = (id) => document.getElementById(id);

async function load() {
  const [idx, tax, recs] = await Promise.all([
    fetch('data/index.json').then((r) => r.json()),
    fetch('data/taxonomy.json').then((r) => r.json()),
    fetch('data/recruiters.json').then((r) => r.json()),
  ]);
  state.reviews = idx.reviews;
  state.recruiters = recs;
  state.tax = tax;
  $('repo-link').href = CONFIG.repoUrl;
  $('form-link').href = CONFIG.formUrl;
  fillSelect('industry', tax.industries);
  fillSelect('region', tax.regions);
  fillSelect('recruiter_type', tax.recruiter_type);
  ['q', 'industry', 'region', 'recruiter_type', 'sort'].forEach((id) => $(id).addEventListener('input', render));
  document.querySelectorAll('.tabs button').forEach((b) =>
    b.addEventListener('click', () => {
      state.view = b.dataset.view;
      document.querySelectorAll('.tabs button').forEach((x) => x.classList.toggle('active', x === b));
      render();
    })
  );
  render();
}

function fillSelect(id, map) {
  const sel = $(id);
  Object.entries(map).forEach(([k, label]) => {
    const o = document.createElement('option');
    o.value = k;
    o.textContent = label;
    sel.appendChild(o);
  });
}

function label(group, key) {
  return (state.tax[group] && state.tax[group][key]) || key || '';
}

function matches(r) {
  const q = $('q').value.trim().toLowerCase();
  if ($('industry').value && r.industry !== $('industry').value) return false;
  if ($('region').value && r.region !== $('region').value) return false;
  if ($('recruiter_type').value && r.recruiter_type !== $('recruiter_type').value) return false;
  if (!q) return true;
  const hay = [r.recruiter_name, r.recruiter_company, r.hiring_company, r.summary, label('industries', r.industry), label('regions', r.region)]
    .filter(Boolean).join(' ').toLowerCase();
  return hay.includes(q);
}

function sortReviews(list) {
  const mode = $('sort').value;
  return list.sort((a, b) => {
    if (mode === 'low') return a.score_avg - b.score_avg;
    if (mode === 'high') return b.score_avg - a.score_avg;
    return (b.period + b.submitted_at).localeCompare(a.period + a.submitted_at);
  });
}

function scoreClass(v) {
  return v <= 2 ? 'low' : v >= 4 ? 'high' : '';
}

function scoresHtml(get) {
  return `<div class="scores">${DIMS.map((d) => {
    const v = get(d);
    return `<div class="score ${scoreClass(v)}">${esc(label('score_dimensions', d))}<b>${fmt(v)}</b></div>`;
  }).join('')}</div>`;
}

function reviewCard(r) {
  const tags = [
    label('recruiter_type', r.recruiter_type),
    label('industries', r.industry),
    label('regions', r.region),
    label('role_families', r.role_family),
    label('seniority', r.seniority),
    label('channel', r.channel),
    label('stage_reached', r.stage_reached),
  ].map((t) => `<span class="tag">${esc(t)}</span>`);
  if (r.ghosted) tags.push('<span class="tag warn">無聲卡</span>');
  if (!r.salary_disclosed_upfront) tags.push('<span class="tag warn">未事前揭露薪資</span>');
  if (r.would_engage_again) tags.push('<span class="tag">願意再次接觸</span>');
  const hiring = r.hiring_company ? ` · 應徵 ${esc(r.hiring_company)}` : '';
  return `<article class="card">
    <span class="overall">${fmt(r.score_avg)}<small> / 5</small></span>
    <h3>${esc(r.recruiter_name)} <span class="sub">@ ${esc(r.recruiter_company)}</span></h3>
    <div class="sub">${esc(r.period)}${hiring}</div>
    <div class="tags">${tags.join('')}</div>
    ${scoresHtml((d) => r['score_' + d])}
    <p class="summary">${esc(r.summary)}</p>
  </article>`;
}

function recruiterCard(x) {
  return `<article class="card">
    <span class="overall">${fmt(x.avg_overall)}<small> / 5 · ${x.review_count} 筆</small></span>
    <h3>${esc(x.name)} <span class="sub">@ ${esc(x.company)}</span></h3>
    <div class="tags">
      <span class="tag">${esc(label('recruiter_type', x.type))}</span>
      <span class="tag ${x.ghosted_rate > 0 ? 'warn' : ''}">無聲卡率 ${Math.round(x.ghosted_rate * 100)}%</span>
      <span class="tag">最近 ${esc(x.latest_period)}</span>
    </div>
    ${scoresHtml((d) => x.avg[d])}
  </article>`;
}

function render() {
  const out = $('results');
  if (state.view === 'reviews') {
    const list = sortReviews(state.reviews.filter(matches));
    $('count').textContent = `${list.length} / ${state.reviews.length} 筆評價`;
    out.innerHTML = list.length ? list.map(reviewCard).join('') : '<div class="empty">沒有符合的紀錄</div>';
    return;
  }
  const keys = new Set(state.reviews.filter(matches).map((r) => r.recruiter_key));
  const mode = $('sort').value;
  const list = state.recruiters.filter((x) => keys.has(x.recruiter_key)).sort((a, b) => {
    if (mode === 'low') return a.avg_overall - b.avg_overall;
    if (mode === 'high') return b.avg_overall - a.avg_overall;
    return b.latest_period.localeCompare(a.latest_period);
  });
  $('count').textContent = `${list.length} 位 recruiter`;
  out.innerHTML = list.length ? list.map(recruiterCard).join('') : '<div class="empty">沒有符合的紀錄</div>';
}

function fmt(v) {
  return v === undefined || v === null ? '–' : Number(v).toFixed(1);
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

load().catch((e) => {
  $('results').innerHTML = `<div class="empty">載入資料失敗：${esc(e.message)}</div>`;
});
