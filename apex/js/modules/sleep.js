/* Apex module: Sleep. Bedtime/wake, duration vs target, quality, energy, sleep hygiene, wake consistency. */
(function () {
  const { h, card } = Apex.ui;
  const ID = 'sleep';
  const DEFAULTS = { bed: null, wake: null, quality: null, energy: null, noScreens: false, noCaffeine: false, consistentWake: false };
  const CONFIG = { targetHours: 8 };
  const HYGIENE = [
    ['noScreens', 'No screens 1h before bed', 'Blue light and scrolling delay melatonin'],
    ['noCaffeine', 'No caffeine after 2pm', 'Caffeine half-life is 5–6 hours'],
    ['consistentWake', 'Consistent wake time', 'Within ~30 min of your usual time'],
  ];

  const CSS = `
.sleep-hero { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.sleep-hero-body { flex: 1; min-width: 180px; }
.sleep-big { font-size: 2rem; font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1.1; }
.sleep-times { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.sleep-times .field { margin-bottom: 6px; }
.sleep-legend { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 8px; }
.sleep-legend span:not(.sleep-legend-plain)::before { content: ''; display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; background: var(--sleep-c); vertical-align: -1px; }
.sleep-chart { position: relative; }
.sleep-labels { display: flex; gap: 4px; margin-top: 3px; }
.sleep-labels span { flex: 1; min-width: 0; text-align: center; font-size: .65rem; color: var(--muted); }
.sleep-target-line { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--muted); opacity: .6; pointer-events: none; }
`;
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, CSS));
  }
  injectStyle();

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const toMin = (t) => {
    if (!t || !/^\d{1,2}:\d{2}/.test(t)) return null;
    const [hh, mm] = t.split(':').map(Number);
    return hh * 60 + mm;
  };
  /** Minutes asleep, handling bedtimes before midnight. */
  function duration(d) {
    const b = toMin(d.bed);
    const w = toMin(d.wake);
    if (b == null || w == null) return null;
    const m = (w - b + 1440) % 1440;
    return m || null;
  }
  const fmtClock = (min) => {
    const hh = Math.floor(min / 60) % 24;
    const mm = Math.round(min % 60);
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
  };

  function durationScore(mins, targetHours) {
    const t = targetHours * 60;
    if (mins >= t) {
      const over = mins - t;
      return over <= 60 ? 100 : Math.max(60, 100 - ((over - 60) / 180) * 40); // oversleeping is mildly penalised
    }
    return Math.max(0, 100 - ((t - mins) / t) * 200); // 6h vs 8h → 50, 7h → 75
  }

  /** Weighted parts of the day's score; only logged parts count (hygiene always counts once anything is logged). */
  function parts(d, target) {
    const out = [];
    const dur = duration(d);
    if (dur != null) out.push({ w: 0.5, v: durationScore(dur, target) });
    if (d.quality != null) out.push({ w: 0.2, v: ((d.quality - 1) / 4) * 100 });
    if (d.energy != null) out.push({ w: 0.1, v: ((d.energy - 1) / 4) * 100 });
    const hyg = HYGIENE.filter(([k]) => d[k]).length;
    out.push({ w: 0.2, v: (hyg / HYGIENE.length) * 100 });
    return out;
  }
  const logged = (d) => duration(d) != null || d.quality != null || d.energy != null || HYGIENE.some(([k]) => d[k]);

  function computeScore(date) {
    if (!Apex.store.has(ID, date)) return null;
    const d = Apex.store.get(ID, date, DEFAULTS);
    if (!logged(d)) return null;
    const ps = parts(d, cfg().targetHours || 8);
    const w = ps.reduce((a, p) => a + p.w, 0);
    return ps.reduce((a, p) => a + p.v * p.w, 0) / w;
  }

  /** Std-dev (minutes) of wake time across the last 7 days ending `date`; null with fewer than 3 logs. */
  function wakeSpread(date) {
    const mins = Apex.store.range(ID, date, 7)
      .map((r) => (r.data ? toMin(r.data.wake) : null))
      .filter((v) => v != null);
    if (mins.length < 3) return { sd: null, n: mins.length, mean: null };
    const mean = mins.reduce((a, b) => a + b, 0) / mins.length;
    const sd = Math.sqrt(mins.reduce((a, b) => a + (b - mean) ** 2, 0) / mins.length);
    return { sd, n: mins.length, mean };
  }

  function insight(d, dur, target, spread) {
    if (dur != null && dur < target * 60 - 45) return 'Sleep debt compounds: each hour lost cuts next-day focus and willpower. Move bedtime 15 minutes earlier each night until you hit target, rather than trying to "catch up" on weekends.';
    if (spread.sd != null && spread.sd > 30) return 'Your wake time swings by more than 30 minutes. Top performers anchor one fixed wake time, 7 days a week, and get outdoor light within 30 minutes of waking. Bedtime then settles on its own.';
    if (!d.noScreens) return 'The last hour before bed decides the night. Put the phone outside the bedroom, dim the lights, and read paper. It is the highest-leverage sleep habit most people skip.';
    if (!d.noCaffeine) return 'Caffeine at 3pm is still a quarter-strength coffee at 9pm. A hard 2pm cutoff often adds deep sleep you can feel the next morning.';
    return 'Elite sleepers treat sleep like training: cool dark room (~18°C), same wake time daily, and a wind-down ritual. Protect it like a meeting you can’t move.';
  }

  function historyChart(date, target) {
    const days = Apex.store.range(ID, date, 14);
    const vals = days.map((r) => {
      const m = r.data ? duration(Object.assign({}, DEFAULTS, r.data)) : null;
      return m == null ? null : Math.round((m / 60) * 10) / 10;
    });
    const labels = days.map((r) => String(Apex.date.parse(r.date).getDate()));
    const max = Math.max(target + 2, ...vals.map((v) => v || 0));
    const height = 90;
    const chart = Apex.ui.bars(vals, { max, height });
    chart.querySelectorAll('.bar').forEach((b, i) => {
      const v = vals[i];
      if (v == null) return;
      b.style.background = v >= target ? 'var(--good)' : v >= target - 1 ? 'var(--accent)' : 'var(--bad)';
    });
    const wrap = h('div', { class: 'sleep-chart' }, chart,
      h('div', { class: 'sleep-target-line', style: { top: (height - (target / max) * height) + 'px' }, title: `Target ${target}h` }));
    return h('div', null, wrap,
      h('div', { class: 'sleep-labels' }, labels.map((l) => h('span', null, l))),
      h('div', { class: 'sleep-legend small muted' },
        h('span', { style: '--sleep-c: var(--good)' }, 'On target'),
        h('span', { style: '--sleep-c: var(--accent)' }, 'Within 1h'),
        h('span', { style: '--sleep-c: var(--bad)' }, 'Short'),
        h('span', { class: 'sleep-legend-plain' }, `Dashed line: ${target}h target`)));
  }

  Apex.registerModule({
    id: ID,
    name: 'Sleep',
    icon: '😴',
    category: 'body',
    order: 10,
    weight: 1,
    description: 'Sleep is the multiplier on everything else: focus, mood, training and willpower.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const target = c.targetHours || 8;
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const dur = duration(d);
      const score = computeScore(ctx.date);
      const spread = wakeSpread(ctx.date);

      // Overview
      el.append(card('Last night',
        h('div', { class: 'sleep-hero' },
          Apex.ui.ring(score == null ? 0 : score, { size: 96, label: 'score', color: 'var(--good)' }),
          h('div', { class: 'sleep-hero-body' },
            h('div', { class: 'sleep-big' }, dur == null ? '—' : Apex.ui.fmtMinutes(dur)),
            h('div', { class: 'muted small' }, dur == null ? 'Enter bedtime and wake time' : `${Math.round((dur / (target * 60)) * 100)}% of your ${target}h target`),
            h('div', { style: { marginTop: '8px' } }, Apex.ui.progress(dur || 0, target * 60, dur != null && dur >= target * 60 ? 'var(--good)' : null))))));

      // Inputs
      el.append(card('Log sleep',
        h('div', { class: 'sleep-times' },
          Apex.ui.text({ label: 'Bedtime', type: 'time', value: d.bed, onChange: (v) => { d.bed = v || null; save(); } }),
          Apex.ui.text({ label: 'Wake time', type: 'time', value: d.wake, onChange: (v) => { d.wake = v || null; save(); } })),
        Apex.ui.rating({ label: 'Sleep quality', value: d.quality, max: 5, onChange: (v) => { d.quality = v; save(); } }),
        Apex.ui.rating({ label: 'Energy on waking', value: d.energy, max: 5, icons: ['😵', '🥱', '😐', '🙂', '⚡'], onChange: (v) => { d.energy = v; save(); } })));

      el.append(card('Sleep hygiene',
        HYGIENE.map(([k, label, hint]) => Apex.ui.toggle({ label, hint, checked: d[k], onChange: (v) => { d[k] = v; save(); } }))));

      // Progress + consistency
      const sdText = spread.sd == null ? '—' : `±${Math.round(spread.sd)}m`;
      const sdSub = spread.sd == null ? `need 3+ wake times (${spread.n}/7)` : spread.sd <= 15 ? 'elite consistency' : spread.sd <= 30 ? 'good' : 'inconsistent';
      const week = Apex.store.range(ID, ctx.date, 7).map((r) => (r.data ? duration(Object.assign({}, DEFAULTS, r.data)) : null)).filter((v) => v != null);
      const avg = week.length ? week.reduce((a, b) => a + b, 0) / week.length : null;
      const debt = week.reduce((a, m) => a + Math.max(0, target * 60 - m), 0);
      el.append(card('Consistency · last 7 days',
        h('div', { class: 'kpis' },
          Apex.ui.stat('Wake-time spread', sdText, sdSub),
          Apex.ui.stat('Avg wake', spread.mean == null ? '—' : fmtClock(spread.mean), `${spread.n} logged`),
          Apex.ui.stat('Avg sleep', avg == null ? '—' : Apex.ui.fmtMinutes(avg), `${week.length} nights`),
          Apex.ui.stat('Sleep debt', week.length ? Apex.ui.fmtMinutes(debt) : '—', 'vs target'))));

      el.append(card('Duration · 14 days', historyChart(ctx.date, target)));

      el.append(card('Top 1% insight', h('p', { class: 'tip', style: { margin: 0 } }, insight(d, dur, target, spread))));

      el.append(card('Targets',
        Apex.ui.number({ label: 'Sleep target', value: target, min: 4, max: 12, step: 0.25, unit: 'hours',
          onChange: (v) => {
            const next = cfg();
            next.targetHours = v == null || v < 4 || v > 12 ? CONFIG.targetHours : v;
            Apex.store.setConfig(ID, next);
            ctx.refresh();
          } }),
        h('p', { class: 'muted small' }, 'Most adults do best on 7–9 hours. Score: 50% duration vs target, 20% quality, 10% waking energy, 20% hygiene.')));
    },

    score(date) {
      return computeScore(date);
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = Apex.store.get(ID, date, DEFAULTS);
      if (!logged(d)) return '';
      const out = [];
      const dur = duration(d);
      if (dur != null) out.push(Apex.ui.fmtMinutes(dur));
      if (d.quality != null) out.push(`quality ${d.quality}/5`);
      out.push(`hygiene ${HYGIENE.filter(([k]) => d[k]).length}/3`);
      return out.join(' · ');
    },
  });
})();
