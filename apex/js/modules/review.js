/* Apex module: Daily Review. Morning routine + evening reflection + Life Score recap. */
(function () {
  const { h, card, stat, text, textarea, rating, toggle, progress, bars, list, adder } = Apex.ui;
  const ID = 'review';
  const DEFAULTS = { checks: {}, intention: '', predicted: null, actual: null, well: '', improve: '', firstTask: '' };
  const CONFIG = { checklist: ['Drink water', 'Get sunlight', 'Move your body', 'Plan the day'] };

  if (!document.getElementById('apex-style-' + ID)) {
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.review-rating .rating .pill { min-width: 34px; padding: 6px 8px; }
.review-carry { background: var(--surface-2); border-radius: var(--radius-sm); padding: 8px 12px; margin-bottom: 10px; font-size: .9rem; overflow-wrap: anywhere; }
.review-recap-head { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 12px; }
.review-recap-row { display: flex; align-items: center; gap: 10px; padding: 5px 0; color: var(--text); }
.review-recap-name { width: 130px; flex: none; font-size: .88rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.review-recap-row strong { width: 28px; text-align: right; font-variant-numeric: tabular-nums; flex: none; }
.review-gap { font-size: .85rem; margin-top: 8px; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const hasText = (s) => !!String(s || '').trim();

  function parts(d, checklist) {
    const done = checklist.filter((item) => d.checks && d.checks[item]).length;
    const morningPct = checklist.length ? done / checklist.length : 0;
    const eveningDone = d.actual != null && (hasText(d.well) || hasText(d.improve));
    return { done, total: checklist.length, morningPct, eveningDone };
  }

  function isLogged(d) {
    if (!d) return false;
    return Object.values(d.checks || {}).some(Boolean) || hasText(d.intention) || d.predicted != null ||
      d.actual != null || hasText(d.well) || hasText(d.improve) || hasText(d.firstTask);
  }

  Apex.registerModule({
    id: ID,
    name: 'Daily Review',
    icon: '📝',
    category: 'life',
    order: 120,
    weight: 1,
    description: 'Win the morning, review the evening. Daily reflection turns experience into compounding improvement.',

    render(el, ctx) {
      const c = cfg();
      const checklist = c.checklist || [];
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      d.checks = d.checks || {};
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const saveCfg = () => { Apex.store.setConfig(ID, c); ctx.refresh(); };
      const p = parts(d, checklist);

      // ---- morning ----
      const yesterday = Apex.store.get(ID, Apex.date.add(ctx.date, -1), DEFAULTS);
      el.append(card('☀️ Morning',
        hasText(yesterday.firstTask) ? h('div', { class: 'review-carry' }, h('span', { class: 'muted' }, "Yesterday's plan for your first task: "), h('strong', null, yesterday.firstTask)) : null,
        h('div', { class: 'row', style: { alignItems: 'center', marginBottom: '8px' } },
          h('span', { class: 'small muted' }, `Wake-up routine ${p.done}/${p.total}`), progress(p.done, p.total || 1, 'var(--good)')),
        checklist.length
          ? checklist.map((item) => toggle({ label: item, checked: !!d.checks[item], onChange: (v) => { d.checks[item] = v; save(); } }))
          : h('p', { class: 'muted small' }, 'Add routine steps in the settings below.'),
        h('div', { style: { marginTop: '10px' } },
          text({ label: 'Intention · the ONE thing that would make today a win', value: d.intention, placeholder: 'e.g. Ship the pricing page',
            onChange: (v) => { d.intention = v; save(); } })),
        h('div', { class: 'review-rating' },
          rating({ label: 'How good will today be? (prediction, 1–10)', value: d.predicted, max: 10, onChange: (v) => { d.predicted = v; save(); } }))));

      // ---- evening ----
      const gap = d.predicted != null && d.actual != null ? d.actual - d.predicted : null;
      el.append(card('🌙 Evening review',
        h('div', { class: 'review-rating' },
          rating({ label: 'How good was today, really? (1–10)', value: d.actual, max: 10, onChange: (v) => { d.actual = v; save(); } })),
        gap != null ? h('p', { class: 'review-gap muted' },
          gap === 0 ? 'Exactly as predicted.' : gap > 0 ? `${gap} point${gap === 1 ? '' : 's'} better than you predicted.` : `${-gap} point${gap === -1 ? '' : 's'} below your prediction. What got in the way?`) : null,
        textarea({ label: 'What went well?', value: d.well, rows: 3, onChange: (v) => { d.well = v; save(); } }),
        textarea({ label: 'What will I do better?', value: d.improve, rows: 3, onChange: (v) => { d.improve = v; save(); } }),
        text({ label: "Tomorrow's first task", value: d.firstTask, placeholder: 'The first thing you will do tomorrow',
          onChange: (v) => { d.firstTask = v; save(); } }),
        h('p', { class: 'small ' + (p.eveningDone ? '' : 'muted') }, p.eveningDone ? '✓ Reflection complete' : 'Rate the day and write at least one reflection to complete it.')));

      // ---- life score recap (reads other modules; review.score never calls lifeScore) ----
      const ls = Apex.lifeScore(ctx.date);
      const tier = Apex.tier(ls.score);
      const others = Apex.modules.enabled().filter((m) => m.id !== ID)
        .map((m) => ({ m, s: Apex.moduleScore(m, ctx.date) }))
        .sort((a, b) => (b.s == null ? -1 : b.s) - (a.s == null ? -1 : a.s));
      const logged = others.filter((x) => x.s != null);
      const weakest = logged.length ? logged[logged.length - 1] : null;
      el.append(card('Life Score recap',
        h('div', { class: 'review-recap-head' },
          Apex.ui.ring(ls.score, { size: 84, color: tier.color, label: 'Life' }),
          h('div', null,
            h('span', { class: 'tag', style: { background: tier.color } }, tier.label),
            h('p', { class: 'muted small', style: { margin: '6px 0 0' } }, `${ls.tracked} of ${ls.total} areas logged.`),
            weakest && weakest.s < 70 ? h('p', { class: 'small', style: { margin: '4px 0 0' } }, `Lowest today: ${weakest.m.icon} ${weakest.m.name} (${weakest.s}).`) : null)),
        others.length
          ? others.map(({ m, s }) => h('a', { class: 'review-recap-row', href: '#/m/' + m.id },
            h('span', { class: 'review-recap-name' }, `${m.icon} ${m.name}`),
            progress(s || 0, 100, Apex.CATEGORIES[m.category].color),
            h('strong', { class: s == null ? 'muted' : '' }, s == null ? '—' : String(s))))
          : h('p', { class: 'muted small' }, 'No other trackers enabled.')));

      // ---- history ----
      const days = Apex.date.lastN(ctx.date, 14);
      const range = Apex.store.range(ID, ctx.date, 14);
      const actual = range.map(({ data }) => (data && data.actual != null ? data.actual : null));
      const rated = actual.filter((v) => v != null);
      const both = range.filter(({ data }) => data && data.actual != null && data.predicted != null);
      const bias = both.length ? both.reduce((a, { data }) => a + (data.actual - data.predicted), 0) / both.length : null;
      const reviewed = range.filter(({ data }) => data && parts(Object.assign({}, DEFAULTS, data), checklist).eveningDone).length;
      el.append(card('Day rating · last 14 days',
        bars(actual, { max: 10, labels: days.map((x) => Apex.date.format(x, { weekday: 'narrow' })), height: 80, color: '#f43f5e' }),
        h('div', { class: 'kpis', style: { marginTop: '12px' } },
          stat('Avg rating', rated.length ? (rated.reduce((a, b) => a + b, 0) / rated.length).toFixed(1) : '—', `${rated.length} days rated`),
          stat('Reviews done', `${reviewed}/14`),
          stat('Forecast bias', bias == null ? '—' : (bias > 0 ? '+' : '') + bias.toFixed(1), bias == null ? 'predict + rate' : bias < 0 ? 'you over-predict' : bias > 0 ? 'you under-predict' : 'spot on'))));

      // ---- settings ----
      el.append(card('Morning routine steps',
        list(checklist, (item) => h('span', null, item), (i) => { c.checklist.splice(i, 1); saveCfg(); }),
        adder('Add a step (e.g. Cold shower)', (item) => {
          c.checklist = c.checklist || [];
          if (c.checklist.includes(item)) { Apex.ui.toast('Already in your routine'); return; }
          c.checklist.push(item);
          saveCfg();
        })));

      el.append(h('p', { class: 'tip' },
        'Top performers close every day with a review: what worked, what to fix, and the first task for tomorrow. Deciding tonight removes friction in the morning, and comparing predicted vs actual ratings teaches you what really makes a great day.'));
    },

    /** Scores only this module's own data. Never call Apex.lifeScore here (it would recurse). */
    score(date) {
      const d = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(d)) return null;
      const p = parts(d, cfg().checklist || []);
      let s = p.morningPct * 35;                  // wake-up routine
      if (hasText(d.intention)) s += 10;          // one-thing intention
      if (d.predicted != null) s += 5;            // forecast
      if (d.actual != null) s += 10;              // honest rating
      if (hasText(d.well)) s += 12.5;             // reflection
      if (hasText(d.improve)) s += 12.5;
      if (hasText(d.firstTask)) s += 15;          // tomorrow planned
      return Math.round(s);
    },

    summary(date) {
      const d = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(d)) return '';
      const p = parts(d, cfg().checklist || []);
      const out = [`Routine ${p.done}/${p.total}`];
      if (d.actual != null) out.push(`day ${d.actual}/10`);
      else if (d.predicted != null) out.push(`predicted ${d.predicted}/10`);
      out.push(p.eveningDone ? 'reviewed ✓' : 'review pending');
      return out.join(' · ');
    },
  });
})();
