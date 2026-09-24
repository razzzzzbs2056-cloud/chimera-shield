/* Apex module: Fitness. Steps, workouts, active minutes, rest days, body weight, weekly workout goal. */
(function () {
  const { h, card } = Apex.ui;
  const ID = 'fitness';
  const DEFAULTS = { steps: null, activeMin: null, workouts: [], rest: false, weight: null };
  const CONFIG = { stepGoal: 10000, activeGoal: 45, weeklyGoal: 4, weightUnit: 'kg' };
  const TYPES = [
    { value: 'strength', label: 'Strength', icon: '🏋️' },
    { value: 'cardio', label: 'Cardio', icon: '🏃' },
    { value: 'hiit', label: 'HIIT', icon: '🔥' },
    { value: 'mobility', label: 'Mobility', icon: '🧘' },
    { value: 'sport', label: 'Sport', icon: '⚽' },
  ];
  const typeOf = (v) => TYPES.find((t) => t.value === v) || TYPES[0];

  const CSS = `
.fitness-hero { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.fitness-hero-body { flex: 1; min-width: 180px; display: flex; flex-direction: column; gap: 10px; }
.fitness-meter { display: flex; flex-direction: column; gap: 4px; }
.fitness-meter-head { display: flex; justify-content: space-between; gap: 8px; font-size: .82rem; }
.fitness-meter .progress { flex: none; }
.fitness-meter-head strong { font-variant-numeric: tabular-nums; }
.fitness-add { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; align-items: end; }
.fitness-add .fitness-add-full { grid-column: 1 / -1; }
.fitness-w { display: flex; align-items: center; gap: 10px; min-width: 0; }
.fitness-w-icon { font-size: 1.2rem; flex: none; }
.fitness-w-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.fitness-dots { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0 10px; }
.fitness-dot { width: 28px; height: 28px; border-radius: 8px; display: grid; place-items: center; font-size: .72rem; background: var(--surface-2); border: 1px solid var(--border); color: var(--muted); }
.fitness-dot.on { background: var(--good); border-color: var(--good); color: #fff; font-weight: 700; }
.fitness-dot.rest { border-style: dashed; border-color: var(--accent); color: var(--accent); }
.fitness-dot.today { outline: 2px solid var(--accent); outline-offset: 1px; }
.fitness-labels { display: flex; gap: 4px; margin-top: 3px; }
.fitness-labels span { flex: 1; min-width: 0; text-align: center; font-size: .65rem; color: var(--muted); }
.fitness-spark { width: 100%; overflow: hidden; }
`;
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, CSS));
  }
  injectStyle();

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const entry = (date) => Apex.store.get(ID, date, DEFAULTS);
  const workoutMin = (d) => (d.workouts || []).reduce((a, w) => a + (w.min || 0), 0);
  const activeTotal = (d) => Math.max(d.activeMin || 0, workoutMin(d));
  const fmtInt = (n) => Math.round(n).toLocaleString();

  /** Monday-start week keys containing `date`. */
  function weekKeys(date) {
    const wd = (Apex.date.weekday(date) + 6) % 7; // 0 = Monday
    const start = Apex.date.add(date, -wd);
    return Array.from({ length: 7 }, (_, i) => Apex.date.add(start, i));
  }
  function weekSessions(date) {
    return weekKeys(date).filter((k) => k <= date).reduce((a, k) => a + ((Apex.store.range(ID, k, 1)[0].data || {}).workouts || []).length, 0);
  }

  const logged = (d) => d.steps != null || d.activeMin != null || (d.workouts || []).length > 0 || d.rest;

  function computeScore(date) {
    if (!Apex.store.has(ID, date)) return null;
    const d = entry(date);
    if (!logged(d)) return null;
    const c = cfg();
    const parts = [];
    if (d.steps != null) parts.push({ w: 0.35, v: Math.min(1, d.steps / (c.stepGoal || 10000)) * 100 });
    const act = activeTotal(d);
    if (d.activeMin != null || act > 0) parts.push({ w: 0.25, v: Math.min(1, act / (c.activeGoal || 45)) * 100 });

    let wv;
    const ws = d.workouts || [];
    if (ws.length) {
      const mins = workoutMin(d);
      const avgI = ws.reduce((a, w) => a + (w.intensity || 3), 0) / ws.length;
      wv = Math.min(100, 50 + (Math.min(mins, 60) / 60) * 35 + (avgI / 5) * 15);
    } else if (d.rest) {
      // Intentional rest is part of training. Full-ish credit if the week is on pace, less if resting too often.
      const keys = Apex.date.lastN(Apex.date.add(date, -1), 6);
      const restDays = keys.filter((k) => { const r = Apex.store.range(ID, k, 1)[0].data; return r && r.rest && !(r.workouts || []).length; }).length;
      const allowed = Math.max(1, 7 - (c.weeklyGoal || 4));
      wv = restDays < allowed ? 85 : 55;
    } else {
      wv = 0;
    }
    parts.push({ w: 0.4, v: wv });
    const tw = parts.reduce((a, p) => a + p.w, 0);
    return parts.reduce((a, p) => a + p.v * p.w, 0) / tw;
  }

  function insight(d, c, sessions) {
    if (d.steps != null && d.steps < c.stepGoal * 0.6) return 'Walking is the most underrated performance tool. A 10-minute walk after each meal adds ~3,000 steps and flattens blood-sugar spikes.';
    if (sessions < c.weeklyGoal && !(d.workouts || []).length && !d.rest) return 'The top 1% do not wait for motivation; the session is already in the calendar. Book tomorrow’s workout now, with a time and a place.';
    if ((d.workouts || []).some((w) => w.type === 'strength')) return 'Progressive overload is the whole game in strength training: log the weights and add a rep or a little load each week. Muscle mass is one of the strongest predictors of healthy longevity.';
    return 'Aim for about 80% easy Zone 2 cardio and 20% hard work. Base fitness (VO₂ max) is one of the strongest predictors of healthy longevity. Most people go too hard on easy days and too easy on hard days.';
  }

  function meter(label, value, goal, unitFmt) {
    return h('div', { class: 'fitness-meter' },
      h('div', { class: 'fitness-meter-head' }, h('span', { class: 'muted' }, label),
        h('strong', null, `${unitFmt(value || 0)} / ${unitFmt(goal)}`)),
      Apex.ui.progress(value || 0, goal, (value || 0) >= goal ? 'var(--good)' : null));
  }

  Apex.registerModule({
    id: ID,
    name: 'Fitness',
    icon: '🏋️',
    category: 'body',
    order: 20,
    weight: 1,
    description: 'Strength, cardio and daily movement: the foundation of energy and a long healthy life.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = entry(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const score = computeScore(ctx.date);
      const sessions = weekSessions(ctx.date);

      el.append(card('Today',
        h('div', { class: 'fitness-hero' },
          Apex.ui.ring(score == null ? 0 : score, { size: 96, label: 'score', color: 'var(--good)' }),
          h('div', { class: 'fitness-hero-body' },
            meter('Steps', d.steps, c.stepGoal, fmtInt),
            meter('Active minutes', activeTotal(d), c.activeGoal, (v) => `${Math.round(v)}m`),
            meter('Workouts this week', sessions, c.weeklyGoal, String)))));

      el.append(card('Movement',
        Apex.ui.row(
          Apex.ui.number({ label: 'Steps', value: d.steps, min: 0, step: 1, onChange: (v) => { d.steps = v == null ? null : Math.max(0, Math.round(v)); save(); } }),
          Apex.ui.number({ label: 'Active minutes', value: d.activeMin, min: 0, step: 1, unit: 'min', onChange: (v) => { d.activeMin = v == null ? null : Math.max(0, v); save(); } })),
        h('p', { class: 'muted small' }, 'Workout minutes count toward active minutes automatically.'),
        Apex.ui.toggle({ label: 'Planned rest day', hint: 'Recovery is training. Full credit if your week is on pace.', checked: d.rest, onChange: (v) => { d.rest = v; save(); } })));

      // Workout log with a local draft that doesn't re-render until "Add".
      const draft = { type: 'strength', min: 45, intensity: 3 };
      const ratingSlot = h('div', { class: 'fitness-add-full' });
      const drawRating = () => {
        ratingSlot.replaceChildren(Apex.ui.rating({ label: 'Intensity', value: draft.intensity, max: 5,
          onChange: (v) => { draft.intensity = v || 3; drawRating(); } }));
      };
      drawRating();
      el.append(card('Workouts',
        Apex.ui.list(d.workouts, (w) => h('div', { class: 'fitness-w' },
          h('span', { class: 'fitness-w-icon', 'aria-hidden': 'true' }, typeOf(w.type).icon),
          h('div', { class: 'fitness-w-body' },
            h('strong', null, typeOf(w.type).label),
            h('span', { class: 'muted small' }, `${Apex.ui.fmtMinutes(w.min || 0)} · intensity ${w.intensity || '—'}/5`))),
        (i) => { d.workouts.splice(i, 1); save(); }),
        h('div', { class: 'fitness-add', style: { marginTop: '12px' } },
          Apex.ui.select({ label: 'Type', value: draft.type, options: TYPES.map((t) => ({ value: t.value, label: `${t.icon} ${t.label}` })), onChange: (v) => { draft.type = v; } }),
          Apex.ui.number({ label: 'Minutes', value: draft.min, min: 1, step: 1, onChange: (v) => { draft.min = v; } }),
          ratingSlot,
          h('div', { class: 'fitness-add-full' }, Apex.ui.button('Add workout', () => {
            if (!draft.min || draft.min <= 0) { Apex.ui.toast('Enter the minutes first'); return; }
            d.workouts = (d.workouts || []).concat({ type: draft.type, min: Math.round(draft.min), intensity: draft.intensity });
            save();
          }, 'primary')))));

      // Week view
      const week = weekKeys(ctx.date);
      const letters = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
      el.append(card('This week',
        h('div', { class: 'fitness-dots' }, week.map((k, i) => {
          const r = Apex.store.range(ID, k, 1)[0].data;
          const n = r ? (r.workouts || []).length : 0;
          const cls = 'fitness-dot' + (n ? ' on' : r && r.rest ? ' rest' : '') + (k === ctx.date ? ' today' : '');
          return h('span', { class: cls, title: `${Apex.date.format(k)}: ${n ? n + ' workout(s)' : r && r.rest ? 'rest' : 'none'}` }, n ? String(n) : letters[i]);
        })),
        h('p', { class: 'muted small' }, sessions >= c.weeklyGoal ? `Weekly goal hit: ${sessions}/${c.weeklyGoal} sessions.` : `${sessions}/${c.weeklyGoal} sessions. ${c.weeklyGoal - sessions} to go this week.`)));

      // History
      const days = Apex.store.range(ID, ctx.date, 14);
      const stepVals = days.map((r) => (r.data && r.data.steps != null ? r.data.steps : null));
      const chart = Apex.ui.bars(stepVals, { max: Math.max(c.stepGoal * 1.2, ...stepVals.map((v) => v || 0)), height: 80 });
      chart.querySelectorAll('.bar').forEach((b, i) => { if (stepVals[i] != null) b.style.background = stepVals[i] >= c.stepGoal ? 'var(--good)' : 'var(--accent)'; });
      const logged7 = stepVals.slice(-7).filter((v) => v != null);
      el.append(card('Steps · 14 days', chart,
        h('div', { class: 'fitness-labels' }, days.map((r) => h('span', null, String(Apex.date.parse(r.date).getDate())))),
        h('p', { class: 'muted small', style: { marginTop: '8px', marginBottom: 0 } },
          logged7.length ? `7-day average: ${fmtInt(logged7.reduce((a, b) => a + b, 0) / logged7.length)} steps. Green = goal hit.` : 'Log steps to see your trend.')));

      // Body weight
      const w30 = Apex.store.range(ID, ctx.date, 30).map((r) => (r.data && r.data.weight != null ? r.data.weight : null));
      const wNums = w30.filter((v) => v != null);
      const change = wNums.length >= 2 ? wNums[wNums.length - 1] - wNums[0] : null;
      el.append(card('Body weight (optional)',
        Apex.ui.number({ label: 'Weight today', value: d.weight, min: 0, step: 0.1, unit: c.weightUnit, onChange: (v) => { d.weight = v; save(); } }),
        h('div', { class: 'fitness-spark' }, Apex.ui.sparkline(w30, { width: 320, height: 48, color: 'var(--good)' })),
        h('p', { class: 'muted small', style: { marginBottom: 0 } }, wNums.length
          ? `30 days: ${wNums.length} weigh-ins${change != null ? `, ${change > 0 ? '+' : ''}${change.toFixed(1)} ${c.weightUnit}` : ''}. Watch the trend, not the day.`
          : 'Weigh in first thing in the morning for a consistent trend.')));

      el.append(card('Top 1% insight', h('p', { class: 'tip', style: { margin: 0 } }, insight(d, c, sessions))));

      const setCfg = (k, v, fallback) => {
        const next = cfg();
        next[k] = v == null || !(v > 0) ? fallback : v;
        Apex.store.setConfig(ID, next);
        ctx.refresh();
      };
      el.append(card('Targets',
        Apex.ui.row(
          Apex.ui.number({ label: 'Daily steps goal', value: c.stepGoal, min: 1000, step: 500, onChange: (v) => setCfg('stepGoal', v && Math.round(v), CONFIG.stepGoal) }),
          Apex.ui.number({ label: 'Active minutes goal', value: c.activeGoal, min: 5, step: 5, unit: 'min', onChange: (v) => setCfg('activeGoal', v, CONFIG.activeGoal) })),
        Apex.ui.row(
          Apex.ui.number({ label: 'Workouts per week', value: c.weeklyGoal, min: 1, max: 14, step: 1, onChange: (v) => setCfg('weeklyGoal', v && Math.min(14, Math.round(v)), CONFIG.weeklyGoal) }),
          Apex.ui.select({ label: 'Weight unit', value: c.weightUnit, options: ['kg', 'lb'], onChange: (v) => { const n = cfg(); n.weightUnit = v; Apex.store.setConfig(ID, n); ctx.refresh(); } })),
        h('p', { class: 'muted small', style: { marginBottom: 0 } }, 'Score: 35% steps, 25% active minutes, 40% training (a workout, or a planned rest day while your week is on pace).')));
    },

    score(date) {
      return computeScore(date);
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = entry(date);
      const out = [];
      if (d.steps != null) out.push(`${fmtInt(d.steps)} steps`);
      const ws = d.workouts || [];
      if (ws.length) out.push(`${ws.length} workout${ws.length > 1 ? 's' : ''} (${Apex.ui.fmtMinutes(workoutMin(d))})`);
      else if (d.rest) out.push('rest day');
      else if (d.activeMin != null) out.push(`${Math.round(d.activeMin)}m active`);
      if (!out.length && d.weight != null) out.push(`${d.weight} ${cfg().weightUnit}`);
      return out.join(' · ');
    },
  });
})();
