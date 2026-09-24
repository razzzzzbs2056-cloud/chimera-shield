/* Apex module: Digital Discipline — screen time, social media, pickups, phone boundaries. */
(function () {
  const { h, card, stat } = Apex.ui;
  const ID = 'digital';
  const DEFAULTS = { screen: null, social: null, pickups: null, firstHour: false, noBedroom: false, detox: false };
  const CONFIG = { screenLimit: 120, socialLimit: 30, pickupLimit: 50 };
  const TIPS = [
    'The average person picks up their phone 90+ times a day. Top performers batch-check at set times instead.',
    'Guard the first hour: no phone until you\'ve moved, planned and done one piece of deep work.',
    'Charge your phone outside the bedroom. Buy a $10 alarm clock; it\'s the best sleep investment you\'ll make.',
    'Turn your phone to grayscale. Colorless apps are dramatically less compelling.',
    'Delete social apps from your phone and use them only on desktop. Friction is the strongest discipline.',
    'Every notification is someone else\'s priority. Turn off all but calls and messages from real people.',
  ];

  injectStyle();

  const num = (v, dflt) => (typeof v === 'number' && v > 0 ? v : dflt);
  const cfg = () => {
    const c = Apex.store.getConfig(ID, CONFIG);
    return { screenLimit: num(c.screenLimit, 120), socialLimit: num(c.socialLimit, 30), pickupLimit: num(c.pickupLimit, 50) };
  };
  const load = (date) => Apex.store.get(ID, date, DEFAULTS);
  const isLogged = (d) => d.screen != null || d.social != null || d.pickups != null || d.firstHour || d.noBedroom || d.detox;

  /** 1.0 at or under half the limit, 0.8 exactly at the limit, 0 at double the limit. Unlogged = 0. */
  function under(value, limit) {
    if (value == null) return 0;
    const r = value / limit;
    if (r <= 0.5) return 1;
    if (r <= 1) return 1 - (r - 0.5) * 0.4;
    return Math.max(0, 0.8 - (r - 1) * 0.8);
  }

  function computeScore(d, c) {
    const s = under(d.screen, c.screenLimit) * 40 +
      under(d.social, c.socialLimit) * 25 +
      under(d.pickups, c.pickupLimit) * 10 +
      (d.firstHour ? 10 : 0) + (d.noBedroom ? 10 : 0) + (d.detox ? 5 : 0);
    return Math.round(Math.min(100, s));
  }

  /** Bar with a limit marker; fill turns red past the limit. */
  function limitBar(label, value, limit, fmt) {
    const v = value || 0;
    const scale = Math.max(limit, v) * 1.05;
    const over = v > limit;
    return h('div', { class: 'digital-limit' + (over ? ' digital-over' : '') },
      h('div', { class: 'digital-limit-head' },
        h('span', null, label),
        h('span', { class: 'digital-limit-val' }, value == null ? 'not logged' : `${fmt(v)} / ${fmt(limit)}`,
          over ? ` · +${fmt(v - limit)} over` : '')),
      h('div', { class: 'digital-track', role: 'progressbar', 'aria-label': label, 'aria-valuenow': v, 'aria-valuemax': limit },
        h('div', { class: 'digital-fill', style: { width: (v / scale) * 100 + '%' } }),
        h('div', { class: 'digital-mark', style: { left: (limit / scale) * 100 + '%' }, title: 'limit' })));
  }

  function streak(end, key) {
    let d = end;
    const ok = (k) => Apex.store.has(ID, k) && !!load(k)[key];
    if (!ok(d)) d = Apex.date.add(d, -1);
    let n = 0;
    while (n < 3650 && ok(d)) { n++; d = Apex.date.add(d, -1); }
    return n;
  }

  const tipFor = (date) => TIPS[Math.abs(Apex.date.diff(date, '2024-01-01')) % TIPS.length];
  const fmtM = (m) => Apex.ui.fmtMinutes(m);
  const fmtN = (n) => String(Math.round(n));

  Apex.registerModule({
    id: ID,
    name: 'Digital Discipline',
    icon: '📵',
    category: 'mind',
    order: 60,
    weight: 1,
    description: 'Your attention is your most valuable asset. The top 1% own their phone; the phone doesn\'t own them.',

    render(el, ctx) {
      const c = cfg();
      const d = load(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const setN = (k) => (v) => { d[k] = v == null ? null : Math.max(0, v); save(); };

      const inputs = card('Today',
        h('div', { class: 'row' },
          Apex.ui.number({ label: 'Total screen time', value: d.screen, min: 0, step: 1, unit: 'min', onChange: setN('screen') }),
          Apex.ui.number({ label: 'Social media', value: d.social, min: 0, step: 1, unit: 'min', onChange: setN('social') }),
          Apex.ui.number({ label: 'Phone pickups', value: d.pickups, min: 0, step: 1, onChange: setN('pickups') })),
        h('p', { class: 'muted small' }, 'Copy these from Screen Time (iOS) or Digital Wellbeing (Android) at the end of the day.'));

      const limits = card('Limits',
        limitBar('📱 Screen time', d.screen, c.screenLimit, fmtM),
        limitBar('📸 Social media', d.social, c.socialLimit, fmtM),
        limitBar('👆 Pickups', d.pickups, c.pickupLimit, fmtN));

      const fh = streak(ctx.date, 'firstHour');
      const nb = streak(ctx.date, 'noBedroom');
      const rules = card('Boundaries',
        Apex.ui.toggle({ label: 'First hour without phone', hint: fh ? `${fh}-day streak` : 'Own your morning', checked: d.firstHour, onChange: (v) => { d.firstHour = v; save(); } }),
        Apex.ui.toggle({ label: 'No phone in bedroom', hint: nb ? `${nb}-day streak` : 'Charge it elsewhere', checked: d.noBedroom, onChange: (v) => { d.noBedroom = v; save(); } }),
        Apex.ui.toggle({ label: 'Dopamine detox', hint: 'No social, games, or binge content today', checked: d.detox, onChange: (v) => { d.detox = v; save(); } }));

      // --- History
      const days = Apex.store.range(ID, ctx.date, 14);
      const screen = days.map((x) => (x.data && x.data.screen != null ? x.data.screen : null));
      const logged = screen.filter((v) => v != null);
      const chart = Apex.ui.bars(screen, {
        max: Math.max(c.screenLimit, ...logged) * 1.05, color: 'var(--good)', height: 90,
        labels: days.map((x) => Apex.date.format(x.date, { weekday: 'narrow' })),
      });
      chart.querySelectorAll('.bar').forEach((b, i) => { if (screen[i] != null && screen[i] > c.screenLimit) b.style.background = 'var(--bad)'; });
      const topPct = Math.min(100, (c.screenLimit / (Math.max(c.screenLimit, ...logged) * 1.05)) * 100);
      const underDays = logged.filter((v) => v <= c.screenLimit).length;
      const avg = logged.length ? logged.reduce((a, b) => a + b, 0) / logged.length : null;
      const social = days.map((x) => (x.data && x.data.social != null ? x.data.social : null)).filter((v) => v != null);
      const history = card('Last 14 days · screen time',
        h('div', { class: 'digital-chart' }, chart,
          h('div', { class: 'digital-chart-limit', style: { bottom: `calc(${topPct}% * (90 - 17) / 90 + 17px)` }, title: 'limit' })),
        h('div', { class: 'kpis digital-kpis' },
          stat('Avg screen', avg == null ? '—' : fmtM(avg), `limit ${fmtM(c.screenLimit)}`),
          stat('Under limit', `${underDays}/${logged.length || 0}`, 'logged days'),
          stat('Avg social', social.length ? fmtM(social.reduce((a, b) => a + b, 0) / social.length) : '—', `limit ${fmtM(c.socialLimit)}`)));

      const setC = (k, dflt) => (v) => { const n = Apex.store.getConfig(ID, CONFIG); n[k] = v && v > 0 ? v : dflt; Apex.store.setConfig(ID, n); ctx.refresh(); };
      const settings = card('Targets',
        h('div', { class: 'row' },
          Apex.ui.number({ label: 'Screen time limit', value: c.screenLimit, min: 1, step: 5, unit: 'min', onChange: setC('screenLimit', 120) }),
          Apex.ui.number({ label: 'Social media limit', value: c.socialLimit, min: 1, step: 5, unit: 'min', onChange: setC('socialLimit', 30) }),
          Apex.ui.number({ label: 'Pickup limit', value: c.pickupLimit, min: 1, step: 1, onChange: setC('pickupLimit', 50) })));

      el.append(
        h('div', { class: 'grid grid-2' }, inputs, limits),
        h('div', { class: 'grid grid-2' }, rules, history),
        h('div', { class: 'grid grid-2' }, settings, card('Top 1% insight', h('p', { class: 'tip' }, tipFor(ctx.date)))));
    },

    /** Staying under limits: screen 40, social 25, pickups 10. Boundaries: first hour 10, bedroom 10, detox 5. */
    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = load(date);
      if (!isLogged(d)) return null;
      return computeScore(d, cfg());
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = load(date);
      if (!isLogged(d)) return '';
      const c = cfg();
      const parts = [];
      if (d.screen != null) parts.push(`${fmtM(d.screen)} screen${d.screen > c.screenLimit ? ' ⚠️' : ''}`);
      if (d.social != null) parts.push(`${fmtM(d.social)}/${fmtM(c.socialLimit)} social`);
      if (d.pickups != null) parts.push(`${d.pickups} pickups`);
      const rules = [d.firstHour, d.noBedroom, d.detox].filter(Boolean).length;
      if (rules) parts.push(`${rules}/3 boundaries`);
      return parts.join(' · ');
    },
  });

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    const css = `
      .digital-limit { margin-bottom: 14px; }
      .digital-limit-head { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; font-size: .88rem; margin-bottom: 5px; }
      .digital-limit-val { color: var(--muted); font-variant-numeric: tabular-nums; }
      .digital-over .digital-limit-val { color: var(--bad); font-weight: 700; }
      .digital-track { position: relative; height: 10px; background: var(--surface-2); border-radius: 999px; }
      .digital-fill { height: 100%; background: var(--good); border-radius: 999px; transition: width .3s ease; }
      .digital-over .digital-fill { background: var(--bad); }
      .digital-mark { position: absolute; top: -3px; bottom: -3px; width: 2px; margin-left: -1px; background: var(--text); opacity: .7; border-radius: 1px; }
      .digital-chart { position: relative; }
      .digital-chart-limit { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--bad); opacity: .7; pointer-events: none; }
      .digital-kpis { margin-top: 12px; }
    `;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, css));
  }
})();
