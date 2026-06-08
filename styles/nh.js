/* Caregos shared widget enhancer.
   Hand-written content stays in HTML; this only fills in tedious
   repetitive visuals (rating pips, sparklines, percentile fills). */
(function () {
  const RATE = ['', 'var(--rate-1)','var(--rate-2)','var(--rate-3)','var(--rate-4)','var(--rate-5)'];
  const ESC = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ESC[ch]);
  }

  function pips(host) {
    const r = Math.max(1, Math.min(5, Number(host.dataset.r) || 1));
    const lab = host.dataset.label || '';
    const showVal = host.dataset.val !== 'off';
    let html = '<span class="pips" aria-hidden="true">';
    for (let i = 1; i <= 5; i++) html += `<span class="pip${i <= r ? ' on' : ''}"></span>`;
    html += '</span>';
    if (showVal) html += `<span class="val">${r}.0</span>`;
    if (lab) html += `<span class="lab">${escapeHtml(lab)}</span>`;
    host.innerHTML = html;
    host.setAttribute('role', 'img');
    host.setAttribute('aria-label', `${lab ? lab + ': ' : ''}${r} out of 5 stars`);
  }

  /* tiny sparkline from comma list of star values, draws a stepped line */
  function spark(host) {
    const pts = host.dataset.points.split(',').map(Number).filter(Number.isFinite);
    if (pts.length < 2) return;
    const w = +host.dataset.w || 64, h = +host.dataset.h || 20, pad = 2;
    const min = 1, max = 5;
    const x = i => pad + (i / (pts.length - 1)) * (w - pad * 2);
    const y = v => pad + (1 - (v - min) / (max - min)) * (h - pad * 2);
    let d = '';
    pts.forEach((v, i) => { d += (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(v).toFixed(1) + ' '; });
    const last = pts[pts.length - 1], first = pts[0];
    const col = last < first ? 'var(--clay-dark)' : last > first ? 'var(--rate-5)' : 'var(--text-2)';
    host.innerHTML = `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true">
      <path d="${d}" fill="none" stroke="${col}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>
      <circle cx="${x(pts.length - 1).toFixed(1)}" cy="${y(last).toFixed(1)}" r="2.4" fill="${col}"/>
    </svg>`;
  }

  function pctile(host) {
    const p = Math.max(0, Math.min(100, Number(host.dataset.p) || 0));
    const fill = host.querySelector('.fill');
    if (fill) fill.style.width = p + '%';
  }

  function arrow(dir) {
    if (dir === 'down') return '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6.5 2v8M3 7l3.5 3.5L10 7"/></svg>';
    if (dir === 'up')   return '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6.5 11V3M3 6l3.5-3.5L10 6"/></svg>';
    return '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 6.5h9"/></svg>';
  }

  function enhance(root) {
    (root || document).querySelectorAll('.rating[data-r]').forEach(pips);
    (root || document).querySelectorAll('.spark[data-points]').forEach(spark);
    (root || document).querySelectorAll('.pctile[data-p]').forEach(pctile);
    (root || document).querySelectorAll('.trend[data-dir]').forEach(t => {
      const a = t.querySelector('.arr'); if (a) a.innerHTML = arrow(t.dataset.dir);
    });
  }

  document.addEventListener('DOMContentLoaded', () => { enhance(); setupMobileNav(); });
  window.NH = { enhance, arrow, escapeHtml };

  function setupMobileNav(){
    document.querySelectorAll('.topbar').forEach(bar=>{
      const wrap = bar.querySelector('.wrap'), nav = bar.querySelector('.nav');
      if(!wrap || !nav || bar.querySelector('.navtoggle')) return;
      if(!nav.id) nav.id = 'nav-' + Math.random().toString(36).slice(2,7);
      const btn = document.createElement('button');
      btn.className = 'navtoggle';
      btn.setAttribute('aria-label', 'Open menu');
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-controls', nav.id);
      btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h16M3 11h16M3 16h16"/></svg>';
      btn.addEventListener('click', ()=>{
        const open = bar.classList.toggle('nav-open');
        btn.setAttribute('aria-expanded', String(open));
        btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      });
      wrap.appendChild(btn);
    });
  }
})();

