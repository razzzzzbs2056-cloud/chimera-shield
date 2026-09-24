/* Apex module: Goals. Long-term goals with milestones + a daily Top 3. */
(function () {
  const { h, card, text, textarea, select, toggle, button, progress, bars, stat } = Apex.ui;
  const ID = 'goals';
  const blankPriorities = () => [{ text: '', done: false }, { text: '', done: false }, { text: '', done: false }];
  const DEFAULTS = { priorities: blankPriorities(), advanced: '' };
  const CFG = { goals: [], advanceBonus: 15 };

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.goals-prio { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.goals-prio .toggle { padding: 0; flex: none; }
.goals-prio .field { flex: 1; margin: 0; }
.goals-prio .toggle-label { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.goals-prio.done input[type=text] { text-decoration: line-through; color: var(--muted); }
.goals-num { width: 1.4em; text-align: center; font-weight: 800; color: var(--muted); flex: none; }
.goals-goal { border-top: 1px solid var(--border); padding-top: 14px; margin-top: 14px; }
.goals-goal:first-of-type { border-top: 0; margin-top: 0; padding-top: 0; }
.goals-goal-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.goals-goal-head strong { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.goals-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.goals-meta .progress { flex: 1; }
.goals-why { font-style: italic; overflow-wrap: anywhere; }
.goals-due-late { color: var(--bad); font-weight: 700; }
.goals-edit summary { cursor: pointer; color: var(--muted); font-size: .85rem; margin: 6px 0; }
.goals-ms .toggle { padding: 0; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CFG);
  const saveCfg = (c) => Apex.store.setConfig(ID, c);
  const newId = () => 'g' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  const goalPct = (g) => {
    const ms = g.milestones || [];
    return ms.length ? Math.round((ms.filter((m) => m.done).length / ms.length) * 100) : 0;
  };
  const areaOf = (g) => Apex.CATEGORIES[g.area] || Apex.CATEGORIES.work;

  function normalize(d) {
    const p = Array.isArray(d.priorities) ? d.priorities.slice(0, 3) : [];
    while (p.length < 3) p.push({ text: '', done: false });
    d.priorities = p;
    return d;
  }
  const filled = (d) => d.priorities.filter((p) => (p.text || '').trim());
  const doneCount = (d) => filled(d).filter((p) => p.done).length;

  function dueLabel(g, today) {
    if (!g.deadline) return h('span', { class: 'muted small' }, 'No deadline');
    const n = Apex.date.diff(g.deadline, today);
    if (n < 0) return h('span', { class: 'small goals-due-late' }, `${-n}d overdue`);
    if (n === 0) return h('span', { class: 'small goals-due-late' }, 'Due today');
    return h('span', { class: 'small muted' }, `${n}d left · ${Apex.date.format(g.deadline, { month: 'short', day: 'numeric', year: 'numeric' })}`);
  }

  function goalBlock(g, idx, ctx, momentum) {
    const update = (fn) => { const c = cfg(); const gg = c.goals.find((x) => x.id === g.id); if (!gg) return; fn(gg, c); saveCfg(c); ctx.refresh(); };
    const area = areaOf(g);
    const pct = goalPct(g);
    const ms = g.milestones || [];
    return h('div', { class: 'goals-goal' },
      h('div', { class: 'goals-goal-head' },
        h('span', { class: 'tag', style: { background: area.color } }, `${area.icon} ${area.name}`),
        h('strong', null, g.title || 'Untitled goal'),
        dueLabel(g, ctx.today)),
      h('div', { class: 'goals-meta' }, progress(pct, 100, area.color), h('strong', { class: 'small' }, pct + '%')),
      g.why ? h('p', { class: 'goals-why muted small' }, `Why: ${g.why}`) : null,
      h('p', { class: 'muted small' }, `Moved forward ${momentum} of the last 30 days · ${ms.filter((m) => m.done).length}/${ms.length} milestones`),
      h('div', { class: 'goals-ms' },
        Apex.ui.list(ms, (m, i) => toggle({ label: m.text, checked: m.done,
          onChange: (v) => update((gg) => { gg.milestones[i].done = v; }) }),
        (i) => update((gg) => { gg.milestones.splice(i, 1); })),
        Apex.ui.adder('Add a milestone', (v) => update((gg) => { gg.milestones = (gg.milestones || []).concat({ text: v, done: false }); }))),
      h('details', { class: 'goals-edit' },
        h('summary', null, 'Edit goal'),
        text({ label: 'Title', value: g.title, onChange: (v) => update((gg) => { gg.title = v.trim() || gg.title; }) }),
        h('div', { class: 'row' },
          select({ label: 'Area', value: g.area, options: Object.entries(Apex.CATEGORIES).map(([k, c]) => ({ value: k, label: `${c.icon} ${c.name}` })),
            onChange: (v) => update((gg) => { gg.area = v; }) }),
          text({ label: 'Deadline', type: 'date', value: g.deadline, onChange: (v) => update((gg) => { gg.deadline = v; }) })),
        textarea({ label: 'Why it matters', value: g.why, rows: 2, placeholder: 'The reason that keeps you going on bad days',
          onChange: (v) => update((gg) => { gg.why = v; }) }),
        h('div', { class: 'row' },
          button('Move up', () => update((gg, c) => { const i = c.goals.indexOf(gg); if (i > 0) c.goals.splice(i - 1, 0, c.goals.splice(i, 1)[0]); }), 'ghost'),
          button('Delete goal', () => {
            if (!confirm(`Delete goal "${g.title}"?`)) return;
            const c = cfg(); c.goals = c.goals.filter((x) => x.id !== g.id); saveCfg(c); ctx.refresh();
          }, 'danger'))));
  }

  Apex.registerModule({
    id: ID,
    name: 'Goals',
    icon: '🏔️',
    category: 'work',
    order: 80,
    weight: 1,
    description: 'Clear long-term goals and three daily priorities that move them: how the top 1% turn years into results.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = normalize(Apex.store.get(ID, ctx.date, DEFAULTS));
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const s = this.score(ctx.date);

      // --- Top 3 ---
      const prioCard = card(`Top 3 priorities · ${ctx.date === ctx.today ? 'today' : Apex.date.format(ctx.date)}`,
        h('p', { class: 'muted small' }, 'The three things that would make today a win. Hardest first.'),
        d.priorities.map((p, i) => h('div', { class: 'goals-prio' + (p.done && (p.text || '').trim() ? ' done' : '') },
          h('span', { class: 'goals-num' }, String(i + 1)),
          text({ value: p.text, placeholder: ['Most important task', 'Second priority', 'Third priority'][i],
            onChange: (v) => { d.priorities[i].text = v; save(); } }),
          toggle({ label: `Priority ${i + 1} done`, checked: p.done, onChange: (v) => { d.priorities[i].done = v; save(); } }))),
        c.goals.length
          ? select({ label: 'Which goal did today move forward?', value: d.advanced || '',
            options: [{ value: '', label: '— none yet —' }].concat(c.goals.map((g) => ({ value: g.id, label: g.title }))),
            onChange: (v) => { d.advanced = v; save(); } })
          : h('p', { class: 'muted small' }, 'Add a long-term goal below to link your days to it.'));

      // --- Progress ---
      const done = doneCount(d);
      const nFilled = filled(d).length;
      const overall = c.goals.length ? Math.round(c.goals.reduce((a, g) => a + goalPct(g), 0) / c.goals.length) : 0;
      const advancedGoal = c.goals.find((g) => g.id === d.advanced);
      const progressCard = card('Progress',
        h('div', { class: 'kpis' },
          stat('Top 3 done', `${done}/3`, nFilled < 3 ? `${3 - nFilled} not set` : null),
          stat('Score', s == null ? '—' : String(Math.round(s))),
          stat('Goals', String(c.goals.length), c.goals.length ? `${overall}% overall` : 'none yet')),
        h('div', { style: { marginTop: '12px' } }, progress(done, 3, done === 3 ? 'var(--good)' : '')),
        h('p', { class: 'muted small', style: { marginTop: '6px' } },
          advancedGoal ? `Moved forward: ${advancedGoal.title} (+${c.advanceBonus} bonus)` : 'Moving a long-term goal forward earns a bonus.'));

      // --- History ---
      const days = Apex.date.lastN(ctx.date, 14);
      const hist = days.map((k) => (Apex.store.has(ID, k) ? doneCount(normalize(Apex.store.get(ID, k, DEFAULTS))) : null));
      const logged = hist.filter((v) => v != null);
      const perfect = logged.filter((v) => v === 3).length;
      const historyCard = card('Top 3 completed · last 14 days',
        bars(hist, { max: 3, labels: days.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 90 }),
        h('p', { class: 'muted small', style: { marginTop: '8px' } },
          logged.length ? `3/3 on ${perfect} of ${logged.length} logged days` : 'No days logged yet.'));

      // --- Goals ---
      const last30 = Apex.date.lastN(ctx.date, 30);
      const momentum = {};
      last30.forEach((k) => {
        if (!Apex.store.has(ID, k)) return;
        const a = Apex.store.get(ID, k, DEFAULTS).advanced;
        if (a) momentum[a] = (momentum[a] || 0) + 1;
      });
      const goalsCard = card('Long-term goals',
        c.goals.length ? c.goals.map((g, i) => goalBlock(g, i, ctx, momentum[g.id] || 0))
          : Apex.ui.empty('No goals yet. Add 1 to 3 big ones: fewer goals, more focus.'),
        h('div', { style: { marginTop: '14px' } },
          Apex.ui.adder('New goal, e.g. "Run a sub-4h marathon"', (v) => {
            const cc = cfg();
            cc.goals = cc.goals.concat({ id: newId(), title: v, area: 'work', deadline: Apex.date.add(ctx.today, 90), milestones: [], why: '' });
            saveCfg(cc);
            ctx.refresh();
          })));

      const settingsCard = card('Scoring',
        Apex.ui.number({ label: 'Bonus for moving a goal forward', value: c.advanceBonus, min: 0, max: 50, step: 5, unit: 'pts',
          onChange: (v) => { const cc = cfg(); cc.advanceBonus = v == null ? CFG.advanceBonus : Math.max(0, Math.min(50, v)); saveCfg(cc); ctx.refresh(); } }),
        h('p', { class: 'muted small' }, 'Daily score = priorities done out of 3, plus the bonus, capped at 100.'));

      el.append(
        h('div', { class: 'grid grid-2' }, prioCard, progressCard),
        goalsCard,
        h('div', { class: 'grid grid-2' }, historyCard, settingsCard),
        h('p', { class: 'tip' }, insight(c, d, momentum, ctx)));
    },

    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = normalize(Apex.store.get(ID, date, DEFAULTS));
      const c = Apex.store.getConfig(ID, CFG);
      const advanced = !!d.advanced && c.goals.some((g) => g.id === d.advanced);
      if (!filled(d).length && !advanced) return null;
      return Math.min(100, (doneCount(d) / 3) * 100 + (advanced ? c.advanceBonus : 0));
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) {
        const n = cfg().goals.length;
        return n ? `${n} goal${n === 1 ? '' : 's'} · set today's Top 3` : '';
      }
      const d = normalize(Apex.store.get(ID, date, DEFAULTS));
      const g = cfg().goals.find((x) => x.id === d.advanced);
      if (!filled(d).length && !g) return 'Set today\'s Top 3';
      return `${doneCount(d)}/3 priorities done` + (g ? ` · moved "${g.title}"` : '');
    },
  });

  function insight(c, d, momentum, ctx) {
    if (!c.goals.length) return 'Write your goals down. People who write specific goals and review them weekly are far more likely to hit them than people who only think about them.';
    const stale = c.goals.find((g) => !momentum[g.id] && goalPct(g) < 100);
    if (stale) return `"${stale.title}" has not moved in 30 days. Put one small step toward it in tomorrow's Top 3, or drop the goal on purpose.`;
    const noMs = c.goals.find((g) => !(g.milestones || []).length);
    if (noMs) return `Break "${noMs.title}" into 3 to 7 milestones. A goal without a next step is only a wish.`;
    const soon = c.goals.filter((g) => g.deadline && goalPct(g) < 100).map((g) => ({ g, n: Apex.date.diff(g.deadline, ctx.today) })).filter((x) => x.n >= 0 && x.n <= 14)[0];
    if (soon) return `"${soon.g.title}" is due in ${soon.n} days at ${goalPct(soon.g)}%. Make it priority #1 until it ships.`;
    if (!filled(d).length) return 'Set tomorrow\'s Top 3 tonight. You start the day executing instead of deciding.';
    return 'Put your hardest priority first, before messages. Win the morning and the day usually follows.';
  }
})();
