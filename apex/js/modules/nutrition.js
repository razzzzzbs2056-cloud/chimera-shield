/* Apex module: Nutrition. Water, protein, fruit & veg, meal quality, sugar/alcohol, eating window. */
(function () {
  const { h, card } = Apex.ui;
  const ID = 'nutrition';
  const DEFAULTS = { water: 0, protein: null, produce: null, meals: [], noSugar: false, noAlcohol: false, firstMeal: null, lastMeal: null };
  const CONFIG = { waterGoal: 8, proteinGoal: 120, produceGoal: 5, windowHours: 10 };
  const TAGS = {
    clean: { label: 'Clean', color: 'var(--good)', value: 100 },
    ok: { label: 'OK', color: 'var(--accent)', value: 60 },
    junk: { label: 'Junk', color: 'var(--bad)', value: 0 },
  };
  const TAG_ORDER = ['clean', 'ok', 'junk'];

  const CSS = `
.nutrition-hero { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.nutrition-hero-body { flex: 1; min-width: 180px; display: flex; flex-direction: column; gap: 10px; }
.nutrition-meter { display: flex; flex-direction: column; gap: 4px; }
.nutrition-meter-head { display: flex; justify-content: space-between; gap: 8px; font-size: .82rem; }
.nutrition-meter .progress { flex: none; }
.nutrition-meter-head strong { font-variant-numeric: tabular-nums; }
.nutrition-steppers { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 8px; }
.nutrition-stepper { background: var(--surface-2); border-radius: var(--radius-sm); padding: 10px 12px; }
.nutrition-stepper-label { font-size: .8rem; color: var(--muted); }
.nutrition-stepper-ctl { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 4px; }
.nutrition-stepper-ctl strong { font-size: 1.35rem; font-variant-numeric: tabular-nums; }
.nutrition-stepper-ctl .btn { width: 40px; height: 40px; padding: 0; font-size: 1.2rem; }
.nutrition-glasses { display: flex; flex-wrap: wrap; gap: 2px; margin-top: 6px; font-size: .9rem; letter-spacing: 1px; }
.nutrition-glasses span.off { opacity: .25; filter: grayscale(1); }
.nutrition-meal { display: flex; align-items: center; gap: 10px; min-width: 0; }
.nutrition-meal-name { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.nutrition-tag { cursor: pointer; border: 0; font: inherit; }
.nutrition-add { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; margin-top: 10px; }
.nutrition-add select { width: auto; }
.nutrition-times { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.nutrition-labels { display: flex; gap: 4px; margin-top: 3px; }
.nutrition-labels span { flex: 1; min-width: 0; text-align: center; font-size: .65rem; color: var(--muted); }
@media (max-width: 420px) { .nutrition-add { grid-template-columns: 1fr auto; } .nutrition-add input { grid-column: 1 / -1; } }
`;
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, CSS));
  }
  injectStyle();

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const entry = (date) => Apex.store.get(ID, date, DEFAULTS);
  const toMin = (t) => {
    if (!t || !/^\d{1,2}:\d{2}/.test(t)) return null;
    const [hh, mm] = t.split(':').map(Number);
    return hh * 60 + mm;
  };
  /** Eating window in minutes (first meal to last meal), null if either missing. */
  function windowMin(d) {
    const a = toMin(d.firstMeal);
    const b = toMin(d.lastMeal);
    if (a == null || b == null) return null;
    return (b - a + 1440) % 1440;
  }
  const mealScore = (meals) => (meals.length ? meals.reduce((s, m) => s + (TAGS[m.tag] || TAGS.ok).value, 0) / meals.length : null);

  const logged = (d) => (d.water || 0) > 0 || d.protein != null || d.produce != null || (d.meals || []).length > 0
    || d.noSugar || d.noAlcohol || windowMin(d) != null;

  function computeScore(date) {
    if (!Apex.store.has(ID, date)) return null;
    const d = entry(date);
    if (!logged(d)) return null;
    const c = cfg();
    const parts = [];
    parts.push({ w: 15, v: Math.min(1, (d.water || 0) / (c.waterGoal || 8)) * 100 });
    if (d.protein != null) parts.push({ w: 20, v: Math.min(1, d.protein / (c.proteinGoal || 120)) * 100 });
    if (d.produce != null) parts.push({ w: 20, v: Math.min(1, d.produce / (c.produceGoal || 5)) * 100 });
    const ms = mealScore(d.meals || []);
    if (ms != null) parts.push({ w: 20, v: ms });
    parts.push({ w: 10, v: d.noSugar ? 100 : 0 });
    parts.push({ w: 10, v: d.noAlcohol ? 100 : 0 });
    const win = windowMin(d);
    if (win != null) {
      const over = win / 60 - (c.windowHours || 10);
      parts.push({ w: 5, v: over <= 0 ? 100 : Math.max(0, 100 - over * 25) });
    }
    const tw = parts.reduce((a, p) => a + p.w, 0);
    return parts.reduce((a, p) => a + p.v * p.w, 0) / tw;
  }

  function insight(d, c) {
    if (d.protein != null && d.protein < c.proteinGoal * 0.7) return 'Build every meal around a palm-sized protein source first (eggs, Greek yogurt, fish, chicken, legumes), then add plants. Protein keeps you full and protects muscle.';
    if ((d.meals || []).some((m) => m.tag === 'junk')) return 'Don’t rely on willpower; change what’s around you. The top 1% keep junk food out of the house and keep a default clean meal they can make in 10 minutes.';
    if ((d.water || 0) < c.waterGoal / 2) return 'Even 2% dehydration measurably dulls focus. Drink a big glass of water before coffee, and keep a bottle within reach all day.';
    if (d.produce == null || d.produce < c.produceGoal) return 'Eat the rainbow: aim for 30 different plants a week. Fibre diversity feeds your gut microbiome, and that shows up in mood, energy and cravings.';
    return 'Consistency beats perfection: an 80/20 approach you can keep up for years is better than a perfect diet you drop in three weeks.';
  }

  function meter(label, value, goal, fmt) {
    return h('div', { class: 'nutrition-meter' },
      h('div', { class: 'nutrition-meter-head' }, h('span', { class: 'muted' }, label), h('strong', null, `${fmt(value || 0)} / ${fmt(goal)}`)),
      Apex.ui.progress(value || 0, goal, (value || 0) >= goal ? 'var(--good)' : null));
  }

  function stepper(label, value, goal, onSet, extra) {
    return h('div', { class: 'nutrition-stepper' },
      h('div', { class: 'nutrition-stepper-label' }, label),
      h('div', { class: 'nutrition-stepper-ctl' },
        h('button', { type: 'button', class: 'btn', 'aria-label': `Less ${label}`, disabled: value <= 0 ? true : null, onClick: () => onSet(Math.max(0, value - 1)) }, '−'),
        h('strong', null, `${value}`, h('span', { class: 'muted small' }, ` / ${goal}`)),
        h('button', { type: 'button', class: 'btn', 'aria-label': `More ${label}`, onClick: () => onSet(value + 1) }, '+')),
      extra || null);
  }

  Apex.registerModule({
    id: ID,
    name: 'Nutrition',
    icon: '🥗',
    category: 'body',
    order: 30,
    weight: 1,
    description: 'What you eat drives your energy, body composition and focus. Build the plate, and the rest follows.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = entry(ctx.date);
      d.meals = d.meals || [];
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const score = computeScore(ctx.date);

      el.append(card('Today',
        h('div', { class: 'nutrition-hero' },
          Apex.ui.ring(score == null ? 0 : score, { size: 96, label: 'score', color: 'var(--good)' }),
          h('div', { class: 'nutrition-hero-body' },
            meter('Water', d.water, c.waterGoal, (v) => `${v}`),
            meter('Protein', d.protein, c.proteinGoal, (v) => `${Math.round(v)}g`),
            meter('Fruit & veg', d.produce, c.produceGoal, (v) => `${v}`)))));

      const glasses = h('div', { class: 'nutrition-glasses', 'aria-hidden': 'true' },
        Array.from({ length: Math.max(c.waterGoal, d.water || 0) }, (_, i) => h('span', { class: i < (d.water || 0) ? '' : 'off' }, '💧')));
      el.append(card('Intake',
        h('div', { class: 'nutrition-steppers' },
          stepper('Water (glasses)', d.water || 0, c.waterGoal, (v) => { d.water = v; save(); }, glasses),
          stepper('Fruit & veg (servings)', d.produce || 0, c.produceGoal, (v) => { d.produce = v; save(); })),
        Apex.ui.number({ label: 'Protein', value: d.protein, min: 0, step: 1, unit: 'g', onChange: (v) => { d.protein = v == null ? null : Math.max(0, v); save(); } })));

      // Meals
      const nameIn = h('input', { type: 'text', placeholder: 'e.g. Salmon, rice, greens', 'aria-label': 'Meal name' });
      const tagSel = h('select', { 'aria-label': 'Meal quality' }, TAG_ORDER.map((k) => h('option', { value: k }, TAGS[k].label)));
      const addForm = h('form', { class: 'nutrition-add', onSubmit: (e) => {
        e.preventDefault();
        const name = nameIn.value.trim();
        if (!name) { Apex.ui.toast('Name the meal first'); return; }
        d.meals.push({ name, tag: tagSel.value });
        save();
      } }, nameIn, tagSel, h('button', { type: 'submit', class: 'btn btn-primary' }, 'Add'));
      const counts = TAG_ORDER.map((k) => `${d.meals.filter((m) => m.tag === k).length} ${TAGS[k].label.toLowerCase()}`).join(' · ');
      el.append(card('Meals',
        Apex.ui.list(d.meals, (m, i) => h('div', { class: 'nutrition-meal' },
          h('span', { class: 'nutrition-meal-name' }, m.name),
          h('button', { type: 'button', class: 'tag nutrition-tag', style: { background: (TAGS[m.tag] || TAGS.ok).color }, title: 'Tap to change quality',
            onClick: () => { d.meals[i].tag = TAG_ORDER[(TAG_ORDER.indexOf(m.tag) + 1) % TAG_ORDER.length]; save(); } }, (TAGS[m.tag] || TAGS.ok).label)),
        (i) => { d.meals.splice(i, 1); save(); }),
        addForm,
        d.meals.length ? h('p', { class: 'muted small', style: { marginTop: '8px', marginBottom: 0 } }, counts) : null));

      const win = windowMin(d);
      el.append(card('Discipline',
        Apex.ui.toggle({ label: 'No added sugar', hint: 'Sweets, soda, sweetened coffee', checked: d.noSugar, onChange: (v) => { d.noSugar = v; save(); } }),
        Apex.ui.toggle({ label: 'No alcohol', hint: 'Even 1–2 drinks hurt sleep quality', checked: d.noAlcohol, onChange: (v) => { d.noAlcohol = v; save(); } }),
        h('div', { class: 'nutrition-times', style: { marginTop: '10px' } },
          Apex.ui.text({ label: 'First meal', type: 'time', value: d.firstMeal, onChange: (v) => { d.firstMeal = v || null; save(); } }),
          Apex.ui.text({ label: 'Last meal', type: 'time', value: d.lastMeal, onChange: (v) => { d.lastMeal = v || null; save(); } })),
        h('p', { class: 'muted small', style: { marginBottom: 0 } }, win == null
          ? `Optional: eating window (target ≤ ${c.windowHours}h, and finish 3h before bed).`
          : `Eating window: ${Apex.ui.fmtMinutes(win)} (target ≤ ${c.windowHours}h)${win / 60 <= c.windowHours ? ' ✓' : ''}`)));

      // History: daily score, 14 days
      const days = Apex.date.lastN(ctx.date, 14);
      const vals = days.map((k) => { const s = computeScore(k); return s == null ? null : Math.round(s); });
      const chart = Apex.ui.bars(vals, { max: 100, height: 80 });
      chart.querySelectorAll('.bar').forEach((b, i) => { const v = vals[i]; if (v != null) b.style.background = v >= 80 ? 'var(--good)' : v >= 50 ? 'var(--accent)' : 'var(--bad)'; });
      const got = vals.filter((v) => v != null);
      el.append(card('Nutrition score · 14 days', chart,
        h('div', { class: 'nutrition-labels' }, days.map((k) => h('span', null, String(Apex.date.parse(k).getDate())))),
        h('p', { class: 'muted small', style: { marginTop: '8px', marginBottom: 0 } },
          got.length ? `Average ${Math.round(got.reduce((a, b) => a + b, 0) / got.length)} over ${got.length} logged day${got.length > 1 ? 's' : ''}.` : 'Log a few days to see your trend.')));

      el.append(card('Top 1% insight', h('p', { class: 'tip', style: { margin: 0 } }, insight(d, c))));

      const setCfg = (k, v, fallback) => {
        const next = cfg();
        next[k] = v == null || !(v > 0) ? fallback : v;
        Apex.store.setConfig(ID, next);
        ctx.refresh();
      };
      el.append(card('Targets',
        Apex.ui.row(
          Apex.ui.number({ label: 'Water goal', value: c.waterGoal, min: 1, max: 20, step: 1, unit: 'glasses', onChange: (v) => setCfg('waterGoal', v && Math.min(20, Math.round(v)), CONFIG.waterGoal) }),
          Apex.ui.number({ label: 'Protein goal', value: c.proteinGoal, min: 20, step: 5, unit: 'g', onChange: (v) => setCfg('proteinGoal', v && Math.round(v), CONFIG.proteinGoal) })),
        Apex.ui.row(
          Apex.ui.number({ label: 'Fruit & veg goal', value: c.produceGoal, min: 1, max: 15, step: 1, unit: 'servings', onChange: (v) => setCfg('produceGoal', v && Math.min(15, Math.round(v)), CONFIG.produceGoal) }),
          Apex.ui.number({ label: 'Max eating window', value: c.windowHours, min: 4, max: 16, step: 0.5, unit: 'h', onChange: (v) => setCfg('windowHours', v && Math.min(16, v), CONFIG.windowHours) })),
        h('p', { class: 'muted small', style: { marginBottom: 0 } }, 'Protein rule of thumb: about 1.6 g per kg of body weight. Score blends water, protein, fruit & veg, meal quality, no sugar, no alcohol and the eating window (when logged).')));
    },

    score(date) {
      return computeScore(date);
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = entry(date);
      if (!logged(d)) return '';
      const c = cfg();
      const out = [`💧 ${d.water || 0}/${c.waterGoal}`];
      if (d.protein != null) out.push(`${Math.round(d.protein)}g protein`);
      if (d.produce != null) out.push(`${d.produce}/${c.produceGoal} produce`);
      const ms = d.meals || [];
      if (ms.length) out.push(`${ms.filter((m) => m.tag === 'clean').length}/${ms.length} clean meals`);
      return out.join(' · ');
    },
  });
})();
