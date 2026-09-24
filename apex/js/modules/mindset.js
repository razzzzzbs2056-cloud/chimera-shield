/* Apex module: Mindset — mood, stress, meditation, gratitude, journal, win of the day. */
(function () {
  const { h, card, stat } = Apex.ui;
  const ID = 'mindset';
  const DEFAULTS = { mood: null, stress: null, meditation: null, gratitude: ['', '', ''], journal: '', win: '' };
  const CONFIG = { meditationGoal: 10 };
  const MOOD_ICONS = ['😞', '😕', '😐', '🙂', '😄'];
  const STRESS_ICONS = ['😌', '🙂', '😐', '😣', '🤯'];
  const TIPS = [
    'Top performers treat the mind like a muscle: 10 minutes of daily meditation beats a 1-hour session once a week.',
    'Write gratitude specifically ("my sister called to check on me"), not generically ("family"). Specificity is what rewires attention.',
    'A bad mood day where you still meditated and journaled is a win. Consistency of practice, not the feeling, compounds.',
    'Name your win of the day before bed. Ending on progress primes tomorrow\'s motivation (the "progress principle").',
    'High stress? Try a physiological sigh: two inhales through the nose, one long exhale. Repeat 3 times.',
    'Journal for clarity, not perfection: three honest sentences beat a blank page.',
  ];

  injectStyle();

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const goalOf = (c) => (c.meditationGoal > 0 ? c.meditationGoal : 10);

  function load(date) {
    const d = Apex.store.get(ID, date, DEFAULTS);
    if (!Array.isArray(d.gratitude)) d.gratitude = [];
    while (d.gratitude.length < 3) d.gratitude.push('');
    d.gratitude = d.gratitude.slice(0, 3);
    return d;
  }

  const filled = (s) => typeof s === 'string' && s.trim().length > 0;
  const gratCount = (d) => d.gratitude.filter(filled).length;

  function isLogged(d) {
    return d.mood != null || d.stress != null || (d.meditation || 0) > 0 ||
      gratCount(d) > 0 || filled(d.journal) || filled(d.win);
  }

  /** Practice is 85 points; mood/stress check-in only 15 so a hard day isn't punished. */
  function computeScore(d, goal) {
    let s = 0;
    s += Math.min(1, (d.meditation || 0) / goal) * 35;
    s += (gratCount(d) / 3) * 25;
    if (filled(d.journal)) s += d.journal.trim().length >= 40 ? 15 : 10;
    if (filled(d.win)) s += 10;
    if (d.mood != null) s += 4 + ((d.mood - 1) / 4) * 4;
    if (d.stress != null) s += 3.5 + ((5 - d.stress) / 4) * 3.5;
    return Math.round(Math.min(100, s));
  }

  function medStreak(end) {
    let d = end;
    const med = (k) => (Apex.store.has(ID, k) ? load(k).meditation || 0 : 0);
    if (med(d) <= 0) d = Apex.date.add(d, -1);
    let n = 0;
    while (n < 3650 && med(d) > 0) { n++; d = Apex.date.add(d, -1); }
    return n;
  }

  function tipFor(date) {
    const n = Math.abs(Apex.date.diff(date, '2024-01-01'));
    return TIPS[n % TIPS.length];
  }

  Apex.registerModule({
    id: ID,
    name: 'Mindset',
    icon: '🧘',
    category: 'mind',
    order: 40,
    weight: 1,
    description: 'Meditation, gratitude and reflection: the daily practice behind calm, clear, resilient high performers.',

    render(el, ctx) {
      const c = cfg();
      const goal = goalOf(c);
      const d = load(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };

      // --- Check-in
      const checkIn = card('Check-in',
        Apex.ui.rating({ label: 'Mood', value: d.mood, icons: MOOD_ICONS, onChange: (v) => { d.mood = v; save(); } }),
        Apex.ui.rating({ label: 'Stress (1 calm · 5 overwhelmed)', value: d.stress, icons: STRESS_ICONS, onChange: (v) => { d.stress = v; save(); } }),
        h('p', { class: 'muted small' }, 'Mood and stress are just data. They count lightly; your practice counts most.'));

      // --- Meditation
      const med = d.meditation || 0;
      const streak = medStreak(ctx.date);
      const meditation = card('Meditation',
        Apex.ui.number({ label: 'Minutes today', value: d.meditation, min: 0, step: 1, unit: 'min',
          onChange: (v) => { d.meditation = v == null ? null : Math.max(0, v); save(); } }),
        h('div', { class: 'mindset-prog' },
          Apex.ui.progress(med, goal, med >= goal ? 'var(--good)' : ''),
          h('span', { class: 'small muted' }, `${med}/${goal} min`)),
        h('div', { class: 'kpis mindset-kpis' },
          stat('Streak', `${streak}d`, streak ? 'days meditating' : 'start today'),
          stat('Goal', `${goal}m`, med >= goal ? 'done ✓' : `${Math.max(0, goal - med)}m to go`)));

      // --- Gratitude
      const gc = gratCount(d);
      const gratitude = card(`Gratitude · ${gc}/3`,
        d.gratitude.map((g, i) => Apex.ui.text({ label: null, value: g, placeholder: `${i + 1}. I'm grateful for…`,
          onChange: (v) => { d.gratitude[i] = v; save(); } })),
        Apex.ui.progress(gc, 3, gc === 3 ? 'var(--good)' : ''));

      // --- Journal + win
      const journal = card('Reflection',
        Apex.ui.text({ label: '🏆 Win of the day', value: d.win, placeholder: 'One thing that went well…',
          onChange: (v) => { d.win = v; save(); } }),
        Apex.ui.textarea({ label: 'Journal', value: d.journal, rows: 5, placeholder: 'What happened, what you felt, what you\'ll do differently…',
          onChange: (v) => { d.journal = v; save(); } }),
        h('p', { class: 'muted small' }, filled(d.journal) ? `${d.journal.trim().split(/\s+/).length} words` : 'A few honest sentences is enough.'));

      // --- History
      const days = Apex.store.range(ID, ctx.date, 30);
      const moods = days.map((x) => (x.data && x.data.mood != null ? x.data.mood : null));
      const moodVals = moods.filter((v) => v != null);
      const avg = moodVals.length ? moodVals.reduce((a, b) => a + b, 0) / moodVals.length : null;
      const medDays = days.filter((x) => x.data && (x.data.meditation || 0) > 0).length;
      const last14 = days.slice(-14);
      const history = card('Last 30 days',
        h('div', { class: 'mindset-spark' },
          h('div', { class: 'small muted' }, 'Mood trend'),
          moods.filter((v) => v != null).length >= 2
            ? Apex.ui.sparkline(moods, { width: 320, height: 48, color: '#a855f7' })
            : h('p', { class: 'muted small' }, 'Check in on 2+ days to see your mood trend.')),
        h('div', { class: 'kpis mindset-kpis' },
          stat('Avg mood', avg == null ? '—' : `${MOOD_ICONS[Math.round(avg) - 1]} ${avg.toFixed(1)}`, `${moodVals.length} check-ins`),
          stat('Meditated', `${medDays}/30`, 'days')),
        h('div', { class: 'small muted mindset-sub' }, 'Meditation minutes · 14 days'),
        Apex.ui.bars(last14.map((x) => (x.data ? x.data.meditation || 0 : null)), {
          max: Math.max(goal, ...last14.map((x) => (x.data && x.data.meditation) || 0)),
          color: '#a855f7',
          labels: last14.map((x) => Apex.date.format(x.date, { weekday: 'narrow' })),
          height: 70,
        }));

      // --- Settings
      const settings = card('Targets',
        Apex.ui.number({ label: 'Daily meditation goal', value: goal, min: 1, step: 1, unit: 'min',
          onChange: (v) => { const n = cfg(); n.meditationGoal = v && v > 0 ? v : 10; Apex.store.setConfig(ID, n); ctx.refresh(); } }));

      el.append(
        h('div', { class: 'grid grid-2' }, checkIn, meditation),
        h('div', { class: 'grid grid-2' }, gratitude, journal),
        history,
        h('div', { class: 'grid grid-2' }, settings,
          card('Top 1% insight', h('p', { class: 'tip' }, tipFor(ctx.date)))));
    },

    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = load(date);
      if (!isLogged(d)) return null;
      return computeScore(d, goalOf(cfg()));
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = load(date);
      if (!isLogged(d)) return '';
      const parts = [];
      if (d.mood != null) parts.push(`${MOOD_ICONS[d.mood - 1]} mood ${d.mood}/5`);
      parts.push(`${d.meditation || 0}/${goalOf(cfg())}m meditated`);
      parts.push(`${gratCount(d)}/3 gratitude`);
      if (filled(d.journal)) parts.push('journaled');
      return parts.join(' · ');
    },
  });

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    const css = `
      .mindset-prog { display: flex; align-items: center; gap: 10px; margin: 4px 0 12px; }
      .mindset-prog .small { white-space: nowrap; font-variant-numeric: tabular-nums; }
      .mindset-kpis { margin: 10px 0; }
      .mindset-spark { display: flex; flex-direction: column; gap: 4px; }
      .mindset-spark svg { width: 100%; height: 48px; }
      .mindset-sub { margin: 6px 0; }
      .module-mindset .rating .pill { font-size: 1.15rem; padding: 4px 10px; }
    `;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, css));
  }
})();
