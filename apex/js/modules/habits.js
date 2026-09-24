/* Apex module: Habits. Custom habit builder, daily checklist, streaks, 12-week heatmap. */
(function () {
  const { h, card, text, select, toggle, button, progress, bars, stat } = Apex.ui;
  const ID = 'habits';
  const DEFAULTS = { done: {} };
  const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const CFG = {
    habits: [
      { id: 'bed', name: 'Make bed', emoji: '🛏️', days: null, type: 'good' },
      { id: 'cold', name: 'Cold shower', emoji: '🚿', days: null, type: 'good' },
      { id: 'read', name: 'Read 10 pages', emoji: '📖', days: null, type: 'good' },
      { id: 'plan', name: 'Plan tomorrow', emoji: '🗒️', days: [0, 1, 2, 3, 4], type: 'good' },
      { id: 'junk', name: 'No junk food', emoji: '🍔', days: null, type: 'bad' },
      { id: 'phone', name: 'No phone first hour', emoji: '📵', days: null, type: 'bad' },
    ],
  };

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.habits-check { display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--border); padding: 4px 0; }
.habits-check:last-child { border-bottom: 0; }
.habits-check .toggle { flex: 1; min-width: 0; }
.habits-check .toggle-label { overflow-wrap: anywhere; }
.habits-streak { font-size: .8rem; font-variant-numeric: tabular-nums; white-space: nowrap; color: var(--muted); }
.habits-streak.hot { color: var(--accent); font-weight: 700; }
.habits-bad { font-size: .68rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: var(--bad); margin-left: 6px; }
.habits-heat { display: grid; grid-template-rows: repeat(7, auto); grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); gap: 3px; max-width: 460px; }
.habits-heat-day { font-size: .6rem; color: var(--muted); line-height: 1; align-self: center; padding-right: 4px; }
.habits-cell { aspect-ratio: 1; border-radius: 3px; background: var(--surface-2); min-width: 0; }
.habits-cell.l0 { background: var(--border); }
.habits-cell.l1 { background: color-mix(in srgb, var(--good) 30%, var(--surface-2)); }
.habits-cell.l2 { background: color-mix(in srgb, var(--good) 55%, var(--surface-2)); }
.habits-cell.l3 { background: color-mix(in srgb, var(--good) 80%, var(--surface-2)); }
.habits-cell.l4 { background: var(--good); }
.habits-cell.future { background: transparent; }
.habits-cell.sel { outline: 2px solid var(--accent); outline-offset: 1px; }
.habits-legend { display: flex; align-items: center; gap: 4px; margin-top: 8px; font-size: .72rem; color: var(--muted); }
.habits-legend .habits-cell { width: 11px; }
.habits-edit { border-bottom: 1px solid var(--border); padding: 10px 0; }
.habits-edit:last-child { border-bottom: 0; }
.habits-edit-top { display: flex; gap: 8px; align-items: flex-end; }
.habits-edit-top .field { margin: 0; }
.habits-edit-top .habits-emoji { width: 58px; flex: none; }
.habits-edit-top .habits-name { flex: 1; min-width: 0; }
.habits-edit-top .habits-type { width: 100px; flex: none; }
.habits-days { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.habits-days .pill { min-width: 0; padding: 4px 9px; font-size: .78rem; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CFG);
  const saveCfg = (c) => Apex.store.setConfig(ID, c);
  const isScheduled = (hb, date) => !Array.isArray(hb.days) || hb.days.includes(Apex.date.weekday(date));
  const scheduledFor = (habits, date) => habits.filter((hb) => isScheduled(hb, date));
  const newId = () => 'h' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);

  /** Completion ratio 0..1 for a date, or null when nothing is logged / nothing scheduled. */
  function ratio(date, habits) {
    const sched = scheduledFor(habits, date);
    if (!sched.length || !Apex.store.has(ID, date)) return null;
    const d = Apex.store.get(ID, date, DEFAULTS);
    return sched.filter((hb) => d.done && d.done[hb.id]).length / sched.length;
  }

  /** Consecutive scheduled days done, ending at `date` (today can still be pending). */
  function streak(hb, date) {
    let n = 0;
    let k = date;
    for (let i = 0; i < 730; i++, k = Apex.date.add(k, -1)) {
      if (!isScheduled(hb, k)) continue;
      const done = Apex.store.has(ID, k) && !!Apex.store.get(ID, k, DEFAULTS).done[hb.id];
      if (done) n++;
      else if (k === date) continue;
      else break;
    }
    return n;
  }

  function scheduleText(hb) {
    if (!Array.isArray(hb.days) || hb.days.length === 7) return 'every day';
    const s = hb.days.slice().sort();
    if (s.join() === '1,2,3,4,5') return 'weekdays';
    if (s.join() === '0,6') return 'weekends';
    return s.map((i) => DAY_NAMES[i]).join(' ');
  }

  function heatmap(date, habits) {
    const today = Apex.date.today();
    const end = Apex.date.add(date, 6 - Apex.date.weekday(date)); // Saturday of the selected week
    const start = Apex.date.add(end, -83);
    const grid = h('div', { class: 'habits-heat', role: 'img', 'aria-label': 'Habit completion, last 12 weeks' });
    // first column: weekday labels
    DAY_NAMES.forEach((n, i) => grid.appendChild(h('span', { class: 'habits-heat-day' }, i % 2 ? n.slice(0, 1) : '')));
    for (let i = 0; i < 84; i++) {
      const k = Apex.date.add(start, i);
      let cls = 'habits-cell';
      let title = Apex.date.format(k);
      if (k > today) cls += ' future';
      else {
        const r = ratio(k, habits);
        if (r == null) title += ': nothing logged';
        else {
          cls += ' l' + (r === 0 ? 0 : r < 0.34 ? 1 : r < 0.67 ? 2 : r < 1 ? 3 : 4);
          title += `: ${Math.round(r * 100)}%`;
        }
      }
      if (k === date) cls += ' sel';
      grid.appendChild(h('div', { class: cls, title }));
    }
    return h('div', null, grid,
      h('div', { class: 'habits-legend' }, 'Less',
        ['', ' l0', ' l1', ' l2', ' l3', ' l4'].map((l) => h('span', { class: 'habits-cell' + l })), 'More'));
  }

  function editor(hb, ctx) {
    const update = (fn) => { const c = cfg(); const x = c.habits.find((y) => y.id === hb.id); if (!x) return; fn(x, c); saveCfg(c); ctx.refresh(); };
    const days = Array.isArray(hb.days) ? hb.days : [0, 1, 2, 3, 4, 5, 6];
    const emoji = text({ label: 'Icon', value: hb.emoji, onChange: (v) => update((x) => { x.emoji = v.trim() || '⭐'; }) });
    emoji.classList.add('habits-emoji');
    const name = text({ label: 'Habit', value: hb.name, onChange: (v) => update((x) => { x.name = v.trim() || x.name; }) });
    name.classList.add('habits-name');
    const type = select({ label: 'Type', value: hb.type, options: [{ value: 'good', label: 'Build' }, { value: 'bad', label: 'Avoid' }],
      onChange: (v) => update((x) => { x.type = v; }) });
    type.classList.add('habits-type');
    return h('div', { class: 'habits-edit' },
      h('div', { class: 'habits-edit-top' }, emoji, name, type,
        h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Delete habit ' + hb.name, onClick: () => {
          if (!confirm(`Delete habit "${hb.name}"? Past check-ins stay in your history.`)) return;
          const c = cfg(); c.habits = c.habits.filter((y) => y.id !== hb.id); saveCfg(c); ctx.refresh();
        } }, '✕')),
      h('div', { class: 'habits-days', role: 'group', 'aria-label': 'Schedule' },
        DAY_NAMES.map((n, i) => h('button', {
          type: 'button', class: 'pill' + (days.includes(i) ? ' active' : ''), 'aria-pressed': days.includes(i) ? 'true' : 'false',
          onClick: () => update((x) => {
            const cur = Array.isArray(x.days) ? x.days.slice() : [0, 1, 2, 3, 4, 5, 6];
            const next = cur.includes(i) ? cur.filter((dd) => dd !== i) : cur.concat(i).sort();
            if (!next.length) { Apex.ui.toast('A habit needs at least one day'); return; }
            x.days = next.length === 7 ? null : next;
          }),
        }, n))));
  }

  Apex.registerModule({
    id: ID,
    name: 'Habits',
    icon: '✅',
    category: 'life',
    order: 90,
    weight: 1,
    description: 'Small daily wins that compound. You do not rise to your goals, you fall to your systems.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      d.done = d.done || {};
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const sched = scheduledFor(c.habits, ctx.date);
      const doneN = sched.filter((hb) => d.done[hb.id]).length;
      const streaks = {};
      c.habits.forEach((hb) => { streaks[hb.id] = streak(hb, ctx.date); });

      // --- checklist ---
      const checklist = card(`Checklist · ${ctx.date === ctx.today ? 'today' : Apex.date.format(ctx.date)}`,
        sched.length
          ? sched.map((hb) => h('div', { class: 'habits-check' },
            toggle({
              label: h('span', null, `${hb.emoji || '⭐'} ${hb.name}`, hb.type === 'bad' ? h('span', { class: 'habits-bad' }, 'avoid') : null),
              hint: hb.type === 'bad' ? 'Check if you stayed clean today' : null,
              checked: !!d.done[hb.id],
              onChange: (v) => { d.done[hb.id] = v; save(); },
            }),
            h('span', { class: 'habits-streak' + (streaks[hb.id] >= 3 ? ' hot' : ''), title: 'Current streak' },
              streaks[hb.id] ? `🔥 ${streaks[hb.id]}d` : '—')))
          : Apex.ui.empty(c.habits.length ? 'Nothing scheduled for this day. Rest is part of the system.' : 'No habits yet. Add one below.'));

      // --- progress ---
      const pct = sched.length ? Math.round((doneN / sched.length) * 100) : 0;
      const best = c.habits.reduce((a, hb) => (streaks[hb.id] > a.n ? { n: streaks[hb.id], hb } : a), { n: 0, hb: null });
      const r30 = Apex.date.lastN(ctx.date, 30).map((k) => ratio(k, c.habits)).filter((v) => v != null);
      const avg30 = r30.length ? Math.round((r30.reduce((a, b) => a + b, 0) / r30.length) * 100) : null;
      const progressCard = card('Progress',
        h('div', { class: 'kpis' },
          stat('Done', `${doneN}/${sched.length}`, `${pct}%`),
          stat('Best streak', best.n ? `${best.n}d` : '—', best.hb ? best.hb.name : null),
          stat('30-day avg', avg30 == null ? '—' : avg30 + '%', r30.length ? `${r30.length} day${r30.length === 1 ? '' : 's'} logged` : null)),
        h('div', { style: { marginTop: '12px' } }, progress(doneN, sched.length || 1, doneN === sched.length && sched.length ? 'var(--good)' : '')),
        h('p', { class: 'muted small', style: { marginTop: '6px' } },
          !sched.length ? 'No habits scheduled.' : doneN === sched.length ? 'Perfect day. Never miss twice.' : `${sched.length - doneN} left today.`));

      // --- history ---
      const days14 = Apex.date.lastN(ctx.date, 14);
      const hist14 = days14.map((k) => { const r = ratio(k, c.habits); return r == null ? null : Math.round(r * 100); });
      const historyCard = card('Last 12 weeks',
        heatmap(ctx.date, c.habits),
        h('h4', { class: 'small muted', style: { margin: '16px 0 6px' } }, 'Completion % · last 14 days'),
        bars(hist14, { max: 100, color: 'var(--good)', labels: days14.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 70 }));

      // --- builder ---
      const builder = card('Your habits',
        h('p', { class: 'muted small' }, 'Build = do it. Avoid = check it when you stayed clean. Tap days to set the schedule.'),
        c.habits.length ? c.habits.map((hb) => editor(hb, ctx)) : Apex.ui.empty('No habits yet.'),
        Apex.ui.adder('New habit, e.g. "Meditate 10 min"', (v) => {
          const cc = cfg();
          const bad = /^(no|stop|quit|avoid|don'?t)\b/i.test(v);
          cc.habits = cc.habits.concat({ id: newId(), name: v, emoji: bad ? '🚫' : '⭐', days: null, type: bad ? 'bad' : 'good' });
          saveCfg(cc);
          ctx.refresh();
        }),
        c.habits.length ? null : button('Restore default habits', () => { const cc = cfg(); cc.habits = CFG.habits.map((x) => Object.assign({}, x)); saveCfg(cc); ctx.refresh(); }, 'ghost'));

      el.append(
        h('div', { class: 'grid grid-2' }, checklist, progressCard),
        historyCard,
        builder,
        h('p', { class: 'tip' }, insight(c, d, sched, streaks, ctx)));
    },

    score(date) {
      const r = ratio(date, Apex.store.getConfig(ID, CFG).habits);
      return r == null ? null : r * 100;
    },

    summary(date) {
      const c = cfg();
      const sched = scheduledFor(c.habits, date);
      if (!sched.length) return c.habits.length ? 'Rest day: nothing scheduled' : '';
      const d = Apex.store.get(ID, date, DEFAULTS);
      const n = sched.filter((hb) => d.done && d.done[hb.id]).length;
      const best = Math.max(0, ...c.habits.map((hb) => streak(hb, date)));
      return `${n}/${sched.length} habits` + (best ? ` · best streak ${best}d` : '');
    },
  });

  function insight(c, d, sched, streaks, ctx) {
    if (!c.habits.length) return 'Start with one habit so small you cannot fail: two minutes. Consistency first, intensity later.';
    // Habit missed yesterday and not yet done today: the "never miss twice" rule.
    const y = Apex.date.add(ctx.date, -1);
    const yd = Apex.store.get(ID, y, DEFAULTS);
    const atRisk = sched.find((hb) => !d.done[hb.id] && isScheduled(hb, y) && Apex.store.has(ID, y) && !yd.done[hb.id]);
    if (atRisk) return `You missed "${atRisk.name}" yesterday. Never miss twice: one miss is an accident, two is the start of a new habit.`;
    const long = sched.filter((hb) => streaks[hb.id] >= 7).sort((a, b) => streaks[b.id] - streaks[a.id])[0];
    if (long && !d.done[long.id]) return `"${long.name}" is on a ${streaks[long.id]}-day streak. Protect it today, even with a minimum version.`;
    if (c.habits.length > 8) return 'More than 8 habits spreads willpower thin. The top 1% master a few keystone habits, then add more.';
    return 'Stack new habits onto existing ones: "After I pour my coffee, I will read 10 pages." Cues beat motivation.';
  }
})();
