/* Apex module: PT Test. A military-style fitness test every few weeks, plus a daily
 * PT drill prescribed from your last test. Fitness logs general training; this is the
 * test-and-drill layer on top of it.
 */
(function () {
  const { h, card } = Apex.ui;
  const ID = 'pt';
  const DEFAULTS = { test: null, drill: null };
  const CONFIG = { age: 25, sex: 'x', core: 'situps', run: '2mile', interval: 21 };

  /* ---------- standards (approximate, adapted from the classic APFT tables) ----------
   * Each bracket gives [value for 60 points, value for 100 points]. Linear in between,
   * extrapolated below 60, capped at 100. Run times are in seconds (lower is better).
   */
  const BRACKETS = [[17, 21], [22, 26], [27, 31], [32, 36], [37, 41], [42, 46], [47, 51], [52, 200]];
  const STD = {
    push: {
      m: [[42, 71], [40, 75], [39, 77], [36, 75], [34, 73], [30, 66], [25, 59], [20, 56]],
      f: [[19, 42], [17, 46], [17, 50], [15, 45], [13, 40], [12, 37], [10, 34], [9, 31]],
    },
    situps: {
      m: [[53, 78], [50, 82], [45, 76], [42, 76], [38, 76], [32, 72], [30, 66], [28, 66]],
      f: [[53, 78], [50, 82], [45, 76], [42, 76], [38, 76], [32, 72], [30, 66], [28, 66]],
    },
    plank: {
      m: [[90, 220], [88, 215], [85, 210], [80, 205], [75, 200], [72, 195], [70, 190], [65, 185]],
      f: [[90, 220], [88, 215], [85, 210], [80, 205], [75, 200], [72, 195], [70, 190], [65, 185]],
    },
    run2mile: {
      m: [[954, 780], [996, 780], [1020, 798], [1062, 798], [1098, 816], [1122, 846], [1170, 864], [1188, 882]],
      f: [[1134, 936], [1176, 936], [1230, 948], [1302, 954], [1362, 1020], [1386, 1044], [1440, 1056], [1464, 1140]],
    },
  };
  const PULL_MAX = { m: 20, f: 8 };
  const PULL_AGE = [1, 1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7];
  const KM_2MILE = 3.2187;
  const RIEGEL_3K = Math.pow(3 / KM_2MILE, 1.06); // 3 km time ≈ 2-mile time × this

  const bracketIndex = (age) => {
    const a = Number(age) || 25;
    const i = BRACKETS.findIndex(([lo, hi]) => a >= lo && a <= hi);
    return i < 0 ? (a < 17 ? 0 : BRACKETS.length - 1) : i;
  };
  const bracketLabel = (age) => {
    const [lo, hi] = BRACKETS[bracketIndex(age)];
    return hi >= 200 ? `${lo}+` : `${lo}–${hi}`;
  };
  const bySex = (table, sex, bi) => {
    if (sex === 'm' || sex === 'f') return table[sex][bi];
    const a = table.m[bi];
    const b = table.f[bi];
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  };

  /** [value for 60 pts, value for 100 pts] for an event under a settings snapshot. */
  function standard(event, s) {
    const bi = bracketIndex(s.age);
    if (event === 'push') return bySex(STD.push, s.sex, bi);
    if (event === 'core') return bySex(s.core === 'plank' ? STD.plank : STD.situps, s.sex, bi);
    if (event === 'pull') {
      const base = s.sex === 'm' || s.sex === 'f' ? PULL_MAX[s.sex] : (PULL_MAX.m + PULL_MAX.f) / 2;
      return [1, Math.max(2, Math.round(base * PULL_AGE[bi]))];
    }
    if (event === 'run') {
      const r = bySex(STD.run2mile, s.sex, bi);
      return s.run === '3k' ? [Math.round(r[0] * RIEGEL_3K), Math.round(r[1] * RIEGEL_3K)] : r;
    }
    return [0, 1];
  }

  function eventPoints(event, value, s) {
    if (value == null || !isFinite(value)) return null;
    if (event !== 'run' && value <= 0) return 0;
    if (event === 'run' && value <= 0) return null;
    const [lo, hi] = standard(event, s);
    const pts = 60 + ((value - lo) / (hi - lo)) * 40;
    return Math.round(Math.max(0, Math.min(100, pts)));
  }

  const EVENTS = ['push', 'core', 'pull', 'run'];
  function testResult(t) {
    if (!t) return null;
    const pts = {};
    let total = 0;
    let n = 0;
    EVENTS.forEach((e) => {
      pts[e] = eventPoints(e, t[e], t);
      if (pts[e] != null) { total += pts[e]; n++; }
    });
    if (!n) return null;
    return { pts, total, complete: n === 4, count: n };
  }

  function rating(total) {
    if (total >= 360) return { label: 'Elite / Special Ops ready', color: '#b45309' };
    if (total >= 300) return { label: 'Excellent', color: '#4d7c0f' };
    if (total >= 270) return { label: 'Passing+', color: '#2563eb' };
    if (total >= 180) return { label: 'Pass', color: '#64748b' };
    return { label: 'Fail', color: '#dc2626' };
  }

  /* ---------- helpers ---------- */
  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const entry = (date) => Apex.store.get(ID, date, DEFAULTS);
  const fmtTime = (sec) => {
    if (sec == null || !isFinite(sec)) return '—';
    const s = Math.round(sec);
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  };
  const parseTime = (str) => {
    const v = String(str || '').trim();
    if (!v) return null;
    let m = v.match(/^(\d{1,3}):([0-5]?\d)$/);
    if (m) return Number(m[1]) * 60 + Number(m[2]);
    m = v.match(/^(\d+(?:\.\d+)?)$/);
    if (m) return Math.round(Number(m[1]) * 60); // plain minutes
    return NaN;
  };
  const runLabel = (mode) => (mode === '3k' ? '3 km run' : '2-mile run');
  const coreLabel = (mode) => (mode === 'plank' ? 'Plank hold' : 'Sit-ups (2 min)');
  const EVENT_NAMES = (s) => ({ push: 'Push-ups (2 min)', core: coreLabel(s.core), pull: 'Pull-ups', run: runLabel(s.run) });
  const fmtEvent = (e, v, s) => {
    if (v == null) return '—';
    if (e === 'run') return fmtTime(v);
    if (e === 'core' && s.core === 'plank') return fmtTime(v);
    return String(v);
  };

  /** Tests found in the `days` days ending at `end`, oldest first: [{date, test, res}]. */
  function testsUpTo(end, days) {
    return Apex.store.range(ID, end, days || 366)
      .filter((r) => r.data && r.data.test)
      .map((r) => ({ date: r.date, test: r.data.test, res: testResult(r.data.test) }))
      .filter((r) => r.res && r.res.complete);
  }
  function lastTest(end) {
    const all = testsUpTo(end, 366);
    return all.length ? all[all.length - 1] : null;
  }

  /* ---------- daily drill prescription (deterministic by weekday) ---------- */
  const BASELINE = { push: 10, core: 20, plankSec: 30, pull: 0, pace: 450 }; // pace = s per km
  function maxesFrom(t) {
    if (!t) return Object.assign({ baseline: true }, BASELINE);
    const km = t.run === '3k' ? 3 : KM_2MILE;
    return {
      baseline: false,
      push: t.push || 0,
      core: t.core === 'plank' ? null : t.core || 0,
      plankSec: t.core === 'plank' ? t.core || 0 : null,
      pull: t.pull || 0,
      pace: t.run ? t.run / km : BASELINE.pace,
    };
  }
  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));

  function pullItem(mx, pct, sets) {
    if (mx.pull <= 1) return { id: 'pull', label: `${sets} × negative pull-ups`, detail: 'Jump to the top, lower yourself over 5 s. Builds your first clean rep.' };
    const reps = Math.max(1, Math.round(mx.pull * pct));
    return { id: 'pull', label: `${sets} × ${reps} pull-ups`, detail: `≈${Math.round(pct * 100)}% of your max (${mx.pull}). Full hang to chin over bar. 90 s rest.` };
  }
  function coreItems(mx, heavy) {
    const out = [];
    if (mx.plankSec != null && mx.core == null) {
      const s = clamp(Math.round(mx.plankSec * (heavy ? 0.7 : 0.6)), 20, 240);
      out.push({ id: 'plank', label: `3 × ${fmtTime(s)} plank hold`, detail: `≈${heavy ? 70 : 60}% of your max hold. 45 s rest.` });
      out.push({ id: 'situp', label: '3 × 20 sit-ups or crunches', detail: 'Controlled tempo, no yanking the neck.' });
    } else {
      const reps = Math.max(8, Math.round((mx.core || BASELINE.core) * (heavy ? 0.6 : 0.5)));
      out.push({ id: 'situp', label: `3 × ${reps} sit-ups`, detail: `≈${heavy ? 60 : 50}% of your 2-min max. 45 s rest.` });
      out.push({ id: 'plank', label: `3 × ${heavy ? '1:00' : '0:45'} plank hold`, detail: 'Squeeze glutes, ribs down, straight line.' });
    }
    out.push({ id: 'flutter', label: `3 × ${heavy ? 40 : 30} flutter kicks (4-count)`, detail: 'Lower back pressed to the deck.' });
    out.push({ id: 'side', label: `3 × ${heavy ? '0:40' : '0:30'} side plank each side`, detail: 'Hips high.' });
    return out;
  }

  function prescribe(date, t) {
    const mx = maxesFrom(t);
    const wd = Apex.date.weekday(date);
    const warm = { id: 'warm', label: 'Warm-up: 5 min easy jog + dynamic stretch', detail: 'Arm circles, leg swings, 10 inchworms.' };
    const cool = { id: 'cool', label: 'Cool-down: 5 min walk + stretch', detail: 'Chest, lats, hips, hamstrings.' };
    if (wd === 1) {
      const reps = Math.max(3, Math.round(mx.push * 0.55));
      return { title: 'Upper body: push-up sets', items: [warm,
        { id: 'push', label: `5 × ${reps} push-ups`, detail: `≈55% of your max (${mx.push}). 60 s rest. Perfect form, chest to fist.` },
        pullItem(mx, 0.5, 5), cool] };
    }
    if (wd === 4) {
      const peak = clamp(Math.round(mx.push / 6), 3, 12);
      return { title: 'Upper body: push-up pyramid', items: [warm,
        { id: 'push', label: `Push-up pyramid 1 → ${peak} → 1`, detail: `${peak * peak} reps total. Rest as many seconds as the reps you just did.` },
        pullItem(mx, 0.6, 4), cool] };
    }
    if (wd === 2) {
      const goal = mx.pace * 0.95;
      return { title: 'Run: intervals', items: [
        { id: 'warm', label: 'Warm-up: 10 min easy jog', detail: 'Conversational pace, then 4 × 20 s strides.' },
        { id: 'int', label: `6 × 400 m in ${fmtTime(goal * 0.4)}`, detail: `Goal pace ${fmtTime(goal)}/km (5% faster than your test). 90 s walk/jog between.` },
        { id: 'cool', label: 'Cool-down: 10 min easy jog + stretch', detail: 'Calves, quads, hip flexors.' }] };
    }
    if (wd === 5) {
      return { title: 'Run: tempo', items: [
        { id: 'warm', label: 'Warm-up: 10 min easy jog', detail: 'Build gradually.' },
        { id: 'tempo', label: `20 min tempo at ${fmtTime(mx.pace + 20)}/km`, detail: 'Comfortably hard: you can speak a few words, not sentences.' },
        { id: 'strides', label: '4 × 20 s strides', detail: 'Fast and relaxed, full recovery between.' },
        { id: 'cool', label: 'Cool-down: 5 min walk + stretch', detail: '' }] };
    }
    if (wd === 3 || wd === 6) {
      const heavy = wd === 6;
      return { title: heavy ? 'Core circuit + ruck' : 'Core circuit + walk', items: coreItems(mx, heavy).concat(heavy
        ? { id: 'ruck', label: 'Ruck 45–60 min', detail: 'Pack at 10–15% of bodyweight, or a brisk walk if you have no pack. Build load slowly.' }
        : { id: 'ruck', label: 'Brisk walk or light ruck, 30 min', detail: 'Easy aerobic volume. Nose-breathing pace.' }) };
    }
    return { title: 'Active recovery (still an order)', items: [
      { id: 'mob', label: 'Mobility flow, 10 min', detail: 'Hips, hamstrings, thoracic spine, ankles.' },
      { id: 'walk', label: 'Easy walk, 20–30 min', detail: 'Outside if you can. No intensity.' },
      { id: 'roll', label: 'Foam roll / stretch, 10 min', detail: 'Calves, quads, upper back.' },
      { id: 'prep', label: 'Prep for the week', detail: 'Kit laid out, training times in the calendar.' }] };
  }

  /* ---------- scoring ---------- */
  const checkedCount = (dr) => Object.keys((dr && dr.checked) || {}).filter((k) => dr.checked[k]).length;

  function computeScore(date) {
    if (!Apex.store.has(ID, date)) return null;
    const d = entry(date);
    const res = testResult(d.test);
    if (res) return res.total / 4; // missing events count as 0
    const dr = d.drill;
    if (!dr) return null;
    if (dr.pain) return 70; // injury: stand down without penalty
    const done = checkedCount(dr);
    if (!done && dr.rpe == null) return null;
    const total = dr.total || 1;
    return Math.min(1, done / total) * 100;
  }

  const TIPS = [
    'Grease the groove: several easy sets of pull-ups or push-ups spread through the day (never to failure) teach your nervous system the movement fast.',
    'Progressive overload: add one rep, one set or a few seconds each week. Small, boring increases add up to big numbers.',
    'Consistency beats intensity. The soldier who trains 5 days every week beats the one who destroys himself twice and then gets hurt.',
    'Sleep is when you get stronger. Training is only the stimulus; adaptation happens during recovery.',
    'Test day is not training day. Rest the day before, warm up well, and pace the run: even splits beat a heroic first lap.',
    'Most run improvement comes from easy miles. Keep easy days truly easy so the intervals can be truly hard.',
    'Pain is information. Muscle burn is normal; sharp, joint or nerve pain is a stop order.',
  ];
  const tipFor = (date) => TIPS[Math.abs(Apex.date.diff(date, '2024-01-01')) % TIPS.length];

  /* ---------- styles ---------- */
  const CSS = `
.module-pt { --pt-olive: #a3b35c; --pt-olive-bg: rgba(163, 179, 92, .14); }
@media (prefers-color-scheme: light) { .module-pt { --pt-olive: #556b2f; --pt-olive-bg: rgba(85, 107, 47, .1); } }
.module-pt .card { border-top: 3px solid var(--pt-olive); }
.module-pt .card-title { text-transform: uppercase; letter-spacing: .14em; font-size: .78rem; font-weight: 800; color: var(--pt-olive); }
.pt-hero { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.pt-hero-body { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 6px; }
.pt-total { font-size: 2rem; font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1; }
.pt-total small { font-size: .9rem; color: var(--muted); font-weight: 600; }
.pt-kicker { text-transform: uppercase; letter-spacing: .14em; font-size: .7rem; font-weight: 700; color: var(--muted); }
.pt-rating { align-self: flex-start; text-transform: uppercase; letter-spacing: .08em; }
.pt-events { display: flex; flex-direction: column; gap: 12px; margin-top: 14px; }
.pt-ev-head { display: flex; justify-content: space-between; gap: 8px; font-size: .85rem; margin-bottom: 4px; }
.pt-ev-head strong { font-variant-numeric: tabular-nums; white-space: nowrap; }
.pt-ev-std { font-size: .72rem; color: var(--muted); margin-top: 3px; }
.pt-form { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12px; }
@media (max-width: 420px) { .pt-form { grid-template-columns: 1fr; } }
.pt-note { font-size: .78rem; color: var(--muted); border-left: 2px solid var(--pt-olive); padding-left: 8px; margin: 4px 0 0; }
.pt-order { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.pt-order-day { text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; font-weight: 800; background: var(--pt-olive); color: #fff; padding: 3px 9px; border-radius: 4px; }
.pt-order-title { font-weight: 800; text-transform: uppercase; letter-spacing: .06em; font-size: .92rem; }
.pt-banner { background: var(--pt-olive-bg); border: 1px dashed var(--pt-olive); border-radius: var(--radius-sm); padding: 8px 12px; font-size: .85rem; margin-bottom: 10px; }
.pt-items { border-top: 1px solid var(--border); margin-top: 4px; }
.pt-item { border-bottom: 1px solid var(--border); padding: 4px 0; }
.pt-item .toggle-label small { font-size: .78rem; }
.pt-item.skipped { opacity: .55; display: flex; gap: 10px; align-items: center; padding: 10px 0; }
.pt-item.skipped .pt-skip { font-size: .66rem; font-weight: 800; letter-spacing: .1em; border: 1px solid var(--border); border-radius: 4px; padding: 1px 6px; flex: none; }
.pt-alert { border: 2px solid var(--bad); border-radius: var(--radius-sm); padding: 10px 12px; margin: 8px 0; font-size: .88rem; }
.pt-alert strong { color: var(--bad); text-transform: uppercase; letter-spacing: .08em; display: block; margin-bottom: 2px; }
.pt-log .list-body { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pt-log-total { font-weight: 800; font-variant-numeric: tabular-nums; }
.pt-spark svg { width: 100%; height: 48px; }
.pt-due { font-weight: 700; }
.pt-due.over { color: var(--bad); }
.pt-settings { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0 12px; }
`;
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, CSS));
  }
  injectStyle();

  const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  Apex.registerModule({
    id: ID,
    name: 'PT Test',
    icon: '🏃',
    category: 'discipline',
    order: 2,
    weight: 1,
    description: 'Military-style fitness test every few weeks, and a daily PT order built from your results.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = entry(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const last = lastTest(ctx.date);
      const lastRes = last ? last.res : null;

      /* --- status --- */
      const due = (() => {
        if (!last) return h('span', { class: 'pt-due over' }, 'No test on record: take your baseline test.');
        const since = Apex.date.diff(ctx.date, last.date);
        const left = (c.interval || 21) - since;
        const txt = `${since} day${since === 1 ? '' : 's'} since last test · ` + (left > 0 ? `Next test due in ${left} day${left === 1 ? '' : 's'}` : left === 0 ? 'Test due today' : `Test overdue by ${-left} day${left === -1 ? '' : 's'}`);
        return h('span', { class: 'pt-due' + (left < 0 ? ' over' : '') }, txt);
      })();
      if (lastRes) {
        const r = rating(lastRes.total);
        el.append(card('Last test',
          h('div', { class: 'pt-hero' },
            Apex.ui.ring(lastRes.total / 4, { size: 96, label: 'avg', color: 'var(--pt-olive)' }),
            h('div', { class: 'pt-hero-body' },
              h('span', { class: 'pt-kicker' }, Apex.date.format(last.date, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })),
              h('div', { class: 'pt-total' }, String(lastRes.total), h('small', null, ' / 400')),
              h('span', { class: 'tag pt-rating', style: { background: r.color } }, r.label),
              h('span', { class: 'small' }, due))),
          eventBars(last.test, lastRes)));
      } else {
        el.append(card('Status', h('p', { class: 'small' }, due)));
      }

      /* --- daily drill --- */
      const plan = prescribe(ctx.date, last ? last.test : null);
      const dr = d.drill || { checked: {}, rpe: null, pain: false, total: plan.items.length };
      dr.checked = dr.checked || {};
      const saveDrill = () => { dr.total = plan.items.length; d.drill = dr; save(); };
      const done = plan.items.filter((it) => dr.checked[it.id]).length;
      const items = h('div', { class: 'pt-items' }, plan.items.map((it) => {
        if (dr.pain && !dr.checked[it.id]) {
          return h('div', { class: 'pt-item skipped' }, h('span', { class: 'pt-skip' }, 'SKIPPED'), h('span', null, it.label));
        }
        return h('div', { class: 'pt-item' }, Apex.ui.toggle({
          label: it.label, hint: it.detail || null, checked: !!dr.checked[it.id],
          onChange: (v) => { if (v) dr.checked[it.id] = true; else delete dr.checked[it.id]; saveDrill(); },
        }));
      }));
      el.append(card("Today's PT order",
        h('div', { class: 'pt-order' },
          h('span', { class: 'pt-order-day' }, DAY_NAMES[Apex.date.weekday(ctx.date)]),
          h('span', { class: 'pt-order-title' }, plan.title),
          h('span', { class: 'spacer' }),
          h('strong', { class: 'small' }, dr.pain ? 'Stood down' : `${done}/${plan.items.length} done`)),
        !last ? h('div', { class: 'pt-banner' }, 'No PT test yet, so this is a beginner baseline. Take the test (below) on a fresh day to calibrate every drill to your numbers.') : null,
        Apex.ui.progress(dr.pain ? 0 : done, plan.items.length, 'var(--pt-olive)'),
        items,
        h('div', { style: { marginTop: '12px' } },
          Apex.ui.rating({ label: 'Effort (RPE 1–10)', value: dr.rpe, max: 10, onChange: (v) => { dr.rpe = v; saveDrill(); } })),
        Apex.ui.toggle({ label: 'Pain or injury today', hint: 'Remaining items are skipped with no penalty (scored as a rest day).', checked: !!dr.pain,
          onChange: (v) => { dr.pain = v; saveDrill(); } }),
        dr.pain ? h('div', { class: 'pt-alert', role: 'alert' }, h('strong', null, 'Stop. Rest.'),
          'Do not train through sharp, joint or nerve pain. Rest, ice/elevate if useful, and see a doctor or physiotherapist if it persists beyond a few days or gets worse.') : null));

      /* --- test entry --- */
      const t = d.test ? Object.assign({}, d.test) : null;
      const snap = t || { age: c.age, sex: c.sex, core: c.core, run: c.run };
      const setEv = (k, v) => {
        const next = Object.assign({ push: null, core: null, pull: null, run: null }, d.test || {}, { age: c.age, sex: c.sex, core: (d.test && d.test.core) || c.core, run: (d.test && d.test.run) || c.run });
        next[k] = v;
        if (EVENTS.every((e) => next[e] == null)) d.test = null; else d.test = next;
        save();
      };
      const coreIsPlank = snap.core === 'plank';
      const todayRes = testResult(t);
      el.append(card('Record PT test · ' + (ctx.date === ctx.today ? 'today' : Apex.date.format(ctx.date)),
        h('p', { class: 'muted small' }, `Scored for age ${bracketLabel(snap.age)} · ${snap.sex === 'm' ? 'male' : snap.sex === 'f' ? 'female' : 'average of male/female'} standards. Take it every ${c.interval || 21} days, rested and warmed up.`),
        h('div', { class: 'pt-form' },
          Apex.ui.number({ label: 'Push-ups (max in 2 min)', value: t ? t.push : null, min: 0, step: 1, unit: 'reps', onChange: (v) => setEv('push', v == null ? null : Math.max(0, Math.round(v))) }),
          coreIsPlank
            ? Apex.ui.text({ label: 'Plank hold (m:ss)', value: t && t.core != null ? fmtTime(t.core) : '', placeholder: '2:30',
              onChange: (v) => { const s = parseTime(v); if (Number.isNaN(s)) { Apex.ui.toast('Use m:ss, e.g. 2:30'); return; } setEv('core', s); } })
            : Apex.ui.number({ label: 'Sit-ups (max in 2 min)', value: t ? t.core : null, min: 0, step: 1, unit: 'reps', onChange: (v) => setEv('core', v == null ? null : Math.max(0, Math.round(v))) }),
          Apex.ui.number({ label: 'Pull-ups (max, dead hang)', value: t ? t.pull : null, min: 0, step: 1, unit: 'reps', onChange: (v) => setEv('pull', v == null ? null : Math.max(0, Math.round(v))) }),
          Apex.ui.text({ label: `${runLabel(snap.run)} time (mm:ss)`, value: t && t.run != null ? fmtTime(t.run) : '', placeholder: snap.run === '3k' ? '13:30' : '14:30',
            onChange: (v) => { const s = parseTime(v); if (Number.isNaN(s)) { Apex.ui.toast('Use mm:ss, e.g. 14:30'); return; } setEv('run', s); } })),
        todayRes ? h('div', null,
          h('div', { class: 'pt-order', style: { marginTop: '6px' } },
            h('span', { class: 'pt-total' }, String(todayRes.total), h('small', null, ' / 400')),
            todayRes.complete ? h('span', { class: 'tag pt-rating', style: { background: rating(todayRes.total).color } }, rating(todayRes.total).label)
              : h('span', { class: 'muted small' }, `Incomplete: ${todayRes.count}/4 events`)),
          eventBars(t, todayRes),
          h('div', { style: { marginTop: '10px' } }, Apex.ui.button('Clear this test', () => { d.test = null; save(); }, 'danger'))) : null,
        h('p', { class: 'pt-note' }, 'Standards are approximate, adapted from the classic US Army APFT tables (60 points = minimum, 100 = max for your age bracket). They are not official and are meant for self-tracking only.')));

      /* --- history --- */
      const days = Apex.date.lastN(ctx.date, 14);
      const tests = testsUpTo(ctx.date, 366);
      el.append(card('History',
        h('div', { class: 'pt-kicker' }, 'PT score · last 14 days'),
        Apex.ui.bars(days.map((k) => { const s = computeScore(k); return s == null ? null : Math.round(s); }),
          { max: 100, color: 'var(--pt-olive)', labels: days.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 80 }),
        h('div', { class: 'pt-kicker', style: { marginTop: '16px' } }, 'Test totals'),
        tests.length > 1 ? h('div', { class: 'pt-spark' }, Apex.ui.sparkline(tests.map((x) => x.res.total), { width: 320, height: 48, color: 'var(--pt-olive)' }))
          : h('p', { class: 'muted small' }, tests.length ? 'Take a second test to see your trend.' : 'No tests logged yet.'),
        tests.length ? h('div', { class: 'pt-log' }, Apex.ui.list(tests.slice().reverse().slice(0, 12), (x) => {
          const r = rating(x.res.total);
          return [h('span', { class: 'pt-log-total' }, `${x.res.total}/400`),
            h('span', { class: 'tag', style: { background: r.color } }, r.label),
            h('span', { class: 'muted small' }, Apex.date.format(x.date, { month: 'short', day: 'numeric', year: 'numeric' }))];
        })) : null));

      el.append(card('Insight', h('p', { class: 'tip' }, tipFor(ctx.date))));

      /* --- settings --- */
      const setCfg = (k, v) => { const n = cfg(); n[k] = v; Apex.store.setConfig(ID, n); ctx.refresh(); };
      el.append(card('Settings',
        h('div', { class: 'pt-settings' },
          Apex.ui.number({ label: 'Age', value: c.age, min: 14, max: 99, step: 1, onChange: (v) => setCfg('age', v == null ? CONFIG.age : clamp(Math.round(v), 14, 99)) }),
          Apex.ui.select({ label: 'Sex (for standards)', value: c.sex, onChange: (v) => setCfg('sex', v),
            options: [{ value: 'm', label: 'Male' }, { value: 'f', label: 'Female' }, { value: 'x', label: 'Prefer not to say' }] }),
          Apex.ui.select({ label: 'Core event', value: c.core, onChange: (v) => setCfg('core', v),
            options: [{ value: 'situps', label: 'Sit-ups (2 min)' }, { value: 'plank', label: 'Plank hold' }] }),
          Apex.ui.select({ label: 'Run event', value: c.run, onChange: (v) => setCfg('run', v),
            options: [{ value: '2mile', label: '2 miles' }, { value: '3k', label: '3 km' }] }),
          Apex.ui.number({ label: 'Test every', value: c.interval, min: 7, max: 60, step: 1, unit: 'days', onChange: (v) => setCfg('interval', v == null ? CONFIG.interval : clamp(Math.round(v), 7, 60)) })),
        h('p', { class: 'muted small' }, 'Each test keeps the settings it was scored with. Editing a test re-scores it with your current settings.')));
    },

    score(date) {
      return computeScore(date);
    },

    summary(date) {
      const d = entry(date);
      const parts = [];
      const res = testResult(d.test);
      if (res) parts.push(`Test today ${res.total}/400`);
      else if (d.drill && d.drill.pain) parts.push('Stood down (pain)');
      else if (d.drill && (checkedCount(d.drill) || d.drill.rpe != null)) parts.push(`Drill ${checkedCount(d.drill)}/${d.drill.total || '?'}`);
      const last = lastTest(date);
      if (last && !(res && last.date === date)) parts.push(`last test ${last.res.total}/400 (${rating(last.res.total).label})`);
      if (!last && !parts.length) return 'No PT test yet';
      return parts.join(' · ');
    },
  });

  function eventBars(t, res) {
    const names = EVENT_NAMES(t);
    return h('div', { class: 'pt-events' }, EVENTS.map((e) => {
      const p = res.pts[e];
      const [lo, hi] = standard(e, t);
      const fmtStd = (v) => (e === 'run' || (e === 'core' && t.core === 'plank') ? fmtTime(v) : String(Math.round(v)));
      return h('div', null,
        h('div', { class: 'pt-ev-head' }, h('span', null, names[e], h('span', { class: 'muted' }, ' · ' + fmtEvent(e, t[e], t))),
          h('strong', null, p == null ? '—' : `${p} pts`)),
        Apex.ui.progress(p || 0, 100, p == null ? null : p >= 60 ? 'var(--pt-olive)' : 'var(--bad)'),
        h('div', { class: 'pt-ev-std' }, `60 pts at ${fmtStd(lo)} · 100 pts at ${fmtStd(hi)}`));
    }));
  }

  // Exposed for tests / other discipline modules (read-only helpers).
  Apex.pt = { eventPoints, testResult, rating, prescribe, standard };
})();
