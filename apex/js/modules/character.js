/* Apex module: Code & Ownership. The character traits research ties to top performers
 * (conscientiousness, self-control, grit, integrity) trained as a daily practice.
 */
(function () {
  const { h, card } = Apex.ui;
  const ID = 'character';
  const DEFAULTS = {
    ownWrong: '', ownFix: '',
    hard: '', hardLevel: null,
    word: null, wordNote: '',
    noComplain: false, complaints: 0,
    cold: false, coldSec: null,
    temptation: '',
    values: [],
    grit: null, // [1-5 x4] or null
  };
  const CONFIG = { values: ['Integrity', 'Discipline', 'Courage', 'Service', 'Excellence'] };

  // Paraphrased in the spirit of the Grit scale (not the published items).
  const GRIT = [
    'I finish what I start, even after it stops being exciting.',
    'A setback slows me down but does not knock me off the goal.',
    'I have stuck with the same big goal for months instead of chasing new ones.',
    'I keep putting in the work when progress is slow and nobody is watching.',
  ];

  const TIPS = [
    'Discipline equals freedom: the structure you choose today buys the options you want tomorrow.',
    'The 40% rule: when your mind says you are done, you have usually used only a fraction of what you have. Take one more step.',
    'Who is going to carry the boats? Stop waiting for someone else to step up. Pick up your end first.',
    'Leaders eat last: take care of your people before yourself, and they will follow you anywhere.',
    'Extreme ownership: no bad teams, only bad leaders. If it touched your mission, it is yours to fix.',
    'Callus the mind: do one hard thing on purpose every day so the hard things you do not choose feel familiar.',
    'Your word is a contract with yourself. Make fewer promises and keep every one of them.',
    'Complaining spends energy on the problem. Owning it spends energy on the solution.',
    'Default aggressive: when in doubt, take action. You can correct course once you are moving.',
  ];
  const tipFor = (date) => TIPS[Math.abs(Apex.date.diff(date, '2024-01-01')) % TIPS.length];

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const entry = (date) => Apex.store.get(ID, date, DEFAULTS);
  const has = (s) => typeof s === 'string' && s.trim().length > 0;

  /* ---------- scoring ---------- */
  function parts(d) {
    const own = has(d.ownWrong) && has(d.ownFix) ? 20 : has(d.ownWrong) || has(d.ownFix) ? 10 : 0;
    const hardDone = has(d.hard) || d.hardLevel != null;
    const lvl = d.hardLevel != null ? Math.max(1, Math.min(5, d.hardLevel)) : 1;
    const hard = hardDone ? 15 + (lvl - 1) * 2.5 : 0;
    const word = d.word === true ? 20 : 0;
    const complain = d.noComplain ? Math.max(0, 10 - 3 * (d.complaints || 0)) : 0;
    const cold = d.cold ? 10 : 0;
    const tempt = has(d.temptation) ? 10 : 0;
    const vals = (d.values || []).length ? 5 : 0;
    return { own, hard, word, complain, cold, tempt, vals };
  }
  const logged = (d) => has(d.ownWrong) || has(d.ownFix) || has(d.hard) || d.hardLevel != null || d.word != null
    || d.noComplain || (d.complaints || 0) > 0 || d.cold || has(d.temptation) || (d.values || []).length > 0;

  function computeScore(date) {
    if (!Apex.store.has(ID, date)) return null;
    const d = entry(date);
    if (!logged(d)) return null; // a grit check alone is not a scored day
    const p = parts(d);
    const s = p.own + p.hard + p.word + p.complain + p.cold + p.tempt + p.vals;
    return Math.max(0, Math.min(100, s));
  }

  const gritAvg = (g) => {
    if (!Array.isArray(g)) return null;
    const nums = g.filter((v) => typeof v === 'number');
    return nums.length === GRIT.length ? nums.reduce((a, b) => a + b, 0) / nums.length : null;
  };

  /* ---------- styles ---------- */
  const CSS = `
.module-character { --character-olive: #a3b35c; --character-olive-bg: rgba(163, 179, 92, .14); }
@media (prefers-color-scheme: light) { .module-character { --character-olive: #556b2f; --character-olive-bg: rgba(85, 107, 47, .1); } }
.module-character .card { border-top: 3px solid var(--character-olive); }
.module-character .card-title { text-transform: uppercase; letter-spacing: .14em; font-size: .78rem; font-weight: 800; color: var(--character-olive); }
.character-kicker { text-transform: uppercase; letter-spacing: .14em; font-size: .7rem; font-weight: 700; color: var(--muted); margin: 4px 0 6px; }
.character-hero { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.character-checks { flex: 1; min-width: 200px; display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 6px; }
.character-check { display: flex; justify-content: space-between; gap: 6px; font-size: .8rem; padding: 5px 8px; border-radius: 6px; background: var(--surface-2); border: 1px solid var(--border); }
.character-check.on { background: var(--character-olive-bg); border-color: var(--character-olive); }
.character-check b { font-variant-numeric: tabular-nums; }
.character-yn { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.character-yn .pill { text-transform: uppercase; letter-spacing: .08em; font-size: .8rem; font-weight: 700; }
.character-yn .pill.no.active { background: var(--bad); border-color: var(--bad); color: #fff; }
.character-yn .pill.yes.active { background: var(--character-olive); border-color: var(--character-olive); color: var(--bg); }
.character-counter { display: flex; align-items: center; gap: 10px; margin: 6px 0 4px; flex-wrap: wrap; }
.character-counter .character-count { font-size: 1.4rem; font-weight: 800; min-width: 2ch; text-align: center; font-variant-numeric: tabular-nums; }
.character-sub { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--border); }
.character-jar { list-style: none; margin: 0; padding: 0; max-height: 420px; overflow-y: auto; }
.character-jar li { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid var(--border); }
.character-jar li:last-child { border-bottom: 0; }
.character-jar-lvl { flex: none; min-width: 34px; text-align: center; font-size: .72rem; font-weight: 800; letter-spacing: .05em; padding: 2px 6px; border-radius: 4px; background: var(--character-olive); color: var(--bg); }
.character-jar-body { flex: 1; min-width: 0; overflow-wrap: anywhere; display: flex; flex-direction: column; }
.character-values { display: flex; flex-direction: column; }
.character-value { display: flex; align-items: center; gap: 10px; border-bottom: 1px solid var(--border); }
.character-value:last-child { border-bottom: 0; }
.character-value .toggle { flex: 1; min-width: 0; }
.character-value-count { font-size: .78rem; color: var(--muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
.character-value .progress { max-width: 80px; }
.character-grit-q { margin-bottom: 8px; }
.character-grit-q > p { margin: 0 0 4px; font-size: .88rem; }
.character-spark svg { width: 100%; height: 48px; }
.character-details summary { cursor: pointer; font-weight: 700; font-size: .88rem; padding: 4px 0; }
.character-edit { display: flex; flex-direction: column; gap: 4px; }
`;
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, CSS));
  }
  injectStyle();

  /** The last `limit` hard-thing entries on or before `end`, latest first. */
  function cookieJar(end, limit) {
    const out = [];
    const rows = Apex.store.range(ID, end, 730);
    for (let i = rows.length - 1; i >= 0 && out.length < limit; i--) {
      const r = rows[i].data;
      if (r && (has(r.hard) || r.hardLevel != null)) out.push({ date: rows[i].date, text: r.hard || '', level: r.hardLevel });
    }
    return out;
  }

  /** Monday of the week containing `date`. */
  const weekStart = (date) => Apex.date.add(date, -((Apex.date.weekday(date) + 6) % 7));

  Apex.registerModule({
    id: ID,
    name: 'Code & Ownership',
    icon: '🛡️',
    category: 'discipline',
    order: 3,
    weight: 1,
    description: 'Ownership, hard things, a kept word and self-control: character is the edge that compounds.',

    render(el, ctx) {
      injectStyle();
      const c = cfg();
      const d = entry(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const score = computeScore(ctx.date);
      const p = parts(d);

      /* --- overview --- */
      const chk = (label, pts, max) => h('div', { class: 'character-check' + (pts > 0 ? ' on' : '') }, h('span', null, label), h('b', null, `${Math.round(pts)}/${max}`));
      el.append(card('Today’s code',
        h('div', { class: 'character-hero' },
          Apex.ui.ring(score == null ? 0 : score, { size: 96, label: score == null ? 'no data' : 'score', color: 'var(--character-olive)' }),
          h('div', { class: 'character-checks' },
            chk('Ownership', p.own, 20), chk('Hard thing', p.hard, 25), chk('Word kept', p.word, 20),
            chk('No complaining', p.complain, 10), chk('Cold', p.cold, 10), chk('Temptation', p.tempt, 10), chk('Values', p.vals, 5)))));

      /* --- extreme ownership --- */
      el.append(card('Extreme ownership',
        h('p', { class: 'muted small' }, 'After Jocko Willink & Leif Babin: everything in your world is yours to own. No blaming, no excuses.'),
        Apex.ui.textarea({ label: 'What went wrong today that I own?', value: d.ownWrong, rows: 2, placeholder: 'I missed the deadline because I did not flag the risk early.',
          onChange: (v) => { d.ownWrong = v; save(); } }),
        Apex.ui.textarea({ label: 'What I will do about it', value: d.ownFix, rows: 2, placeholder: 'Flag risks in the Monday standup, in writing.',
          onChange: (v) => { d.ownFix = v; save(); } })));

      /* --- hard thing --- */
      el.append(card('Hard thing done',
        h('p', { class: 'muted small' }, 'Do the hardest or most uncomfortable thing on purpose, before anyone makes you.'),
        Apex.ui.text({ label: 'What I did', value: d.hard, placeholder: 'Made the call I was avoiding', onChange: (v) => { d.hard = v; save(); } }),
        Apex.ui.rating({ label: 'Difficulty', value: d.hardLevel, max: 5, onChange: (v) => { d.hardLevel = v; save(); } })));

      /* --- word, complaining, cold, temptation --- */
      const yn = (val, set) => h('div', { class: 'character-yn', role: 'radiogroup', 'aria-label': 'Word kept' },
        h('button', { type: 'button', class: 'pill yes' + (val === true ? ' active' : ''), role: 'radio', 'aria-checked': String(val === true), onClick: () => set(val === true ? null : true) }, 'Yes, kept'),
        h('button', { type: 'button', class: 'pill no' + (val === false ? ' active' : ''), role: 'radio', 'aria-checked': String(val === false), onClick: () => set(val === false ? null : false) }, 'No, broke one'));
      el.append(card('Self-control',
        h('div', { class: 'character-kicker' }, 'Word kept'),
        h('p', { class: 'small', style: { marginBottom: '6px' } }, 'Did I keep every promise I made today, to others and to myself?'),
        yn(d.word, (v) => { d.word = v; save(); }),
        Apex.ui.text({ label: 'Note', value: d.wordNote, placeholder: d.word === false ? 'Which one, and how I will make it right' : 'Optional', onChange: (v) => { d.wordNote = v; save(); } }),
        h('div', { class: 'character-sub' },
          h('div', { class: 'character-kicker' }, 'No complaining, no excuses'),
          Apex.ui.toggle({ label: 'I committed to zero complaints today', hint: 'Each complaint costs 3 of the 10 points.', checked: d.noComplain, onChange: (v) => { d.noComplain = v; save(); } }),
          h('div', { class: 'character-counter' },
            h('span', { class: 'small muted' }, 'Complaints'),
            h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'One fewer complaint', disabled: (d.complaints || 0) <= 0 ? true : null,
              onClick: () => { d.complaints = Math.max(0, (d.complaints || 0) - 1); save(); } }, '−'),
            h('span', { class: 'character-count', 'aria-live': 'polite' }, String(d.complaints || 0)),
            h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Log a complaint', onClick: () => { d.complaints = (d.complaints || 0) + 1; save(); } }, '+'))),
        h('div', { class: 'character-sub' },
          h('div', { class: 'character-kicker' }, 'Cold exposure'),
          Apex.ui.toggle({ label: 'Cold shower or plunge', checked: d.cold, onChange: (v) => { d.cold = v; save(); } }),
          d.cold ? Apex.ui.number({ label: 'Duration', value: d.coldSec, min: 0, step: 5, unit: 'sec', onChange: (v) => { d.coldSec = v == null ? null : Math.max(0, Math.round(v)); save(); } }) : null),
        h('div', { class: 'character-sub' },
          h('div', { class: 'character-kicker' }, 'Delayed gratification'),
          Apex.ui.text({ label: 'A temptation I resisted today', value: d.temptation, placeholder: 'Skipped the dessert / did not open the app', onChange: (v) => { d.temptation = v; save(); } }))));

      /* --- core values --- */
      const last30 = Apex.store.range(ID, ctx.date, 30);
      const valueCount = (name) => last30.filter((r) => r.data && (r.data.values || []).includes(name)).length;
      const values = c.values || [];
      el.append(card('Core values',
        h('p', { class: 'muted small' }, 'Tick each value you actually lived today. Counts are for the last 30 days.'),
        values.length ? h('div', { class: 'character-values' }, values.map((name) => {
          const n = valueCount(name);
          return h('div', { class: 'character-value' },
            Apex.ui.toggle({ label: name, checked: (d.values || []).includes(name), onChange: (v) => {
              d.values = (d.values || []).filter((x) => x !== name);
              if (v) d.values.push(name);
              save();
            } }),
            Apex.ui.progress(n, 30, 'var(--character-olive)'),
            h('span', { class: 'character-value-count' }, `${n}/30`));
        })) : Apex.ui.empty('No core values yet. Add one below.'),
        h('details', { class: 'character-details', style: { marginTop: '10px' } },
          h('summary', null, 'Edit values'),
          h('div', { class: 'character-edit' },
            Apex.ui.list(values, (v) => v, (i) => { const n = cfg(); n.values = values.filter((_, j) => j !== i); Apex.store.setConfig(ID, n); ctx.refresh(); }),
            Apex.ui.adder('New value (e.g. Humility)', (v) => {
              if (values.some((x) => x.toLowerCase() === v.toLowerCase())) { Apex.ui.toast('Already on the list'); return; }
              const n = cfg(); n.values = values.concat(v.slice(0, 40)); Apex.store.setConfig(ID, n); ctx.refresh();
            })))));

      /* --- grit check --- */
      const isSunday = Apex.date.weekday(ctx.date) === 0;
      const g = Array.isArray(d.grit) ? d.grit.slice() : [null, null, null, null];
      const weeks = Array.from({ length: 12 }, (_, i) => Apex.date.add(weekStart(ctx.date), -7 * (11 - i)));
      const history = Apex.store.range(ID, ctx.date, 7 * 12);
      const weekly = weeks.map((ws) => {
        const avgs = history.filter((r) => r.data && r.date >= ws && r.date < Apex.date.add(ws, 7)).map((r) => gritAvg(r.data.grit)).filter((v) => v != null);
        return avgs.length ? Math.round((avgs.reduce((a, b) => a + b, 0) / avgs.length) * 100) / 100 : null;
      });
      const todayGrit = gritAvg(d.grit);
      const gritBody = [
        h('p', { class: 'muted small' }, 'Rate each statement 1 (not like me) to 5 (very much like me). Be honest: this is not scored.'),
        GRIT.map((q, i) => h('div', { class: 'character-grit-q' }, h('p', null, q),
          Apex.ui.rating({ value: g[i], max: 5, onChange: (v) => { g[i] = v; d.grit = g.every((x) => x == null) ? null : g; save(); } }))),
        todayGrit != null ? h('p', { class: 'small' }, h('strong', null, `This check: ${todayGrit.toFixed(2)} / 5`)) : null,
      ];
      el.append(card('Grit check (weekly)',
        isSunday || d.grit ? h('div', null, gritBody)
          : h('details', { class: 'character-details' }, h('summary', null, 'Sunday is grit-check day. Take it now anyway'), gritBody),
        h('div', { class: 'character-kicker', style: { marginTop: '10px' } }, 'Weekly average · last 12 weeks'),
        weekly.filter((v) => v != null).length > 1
          ? h('div', { class: 'character-spark' }, Apex.ui.sparkline(weekly, { width: 320, height: 48, color: 'var(--character-olive)' }))
          : h('p', { class: 'muted small' }, 'Two weekly checks needed to show a trend.')));

      /* --- history + cookie jar --- */
      const days = Apex.date.lastN(ctx.date, 14);
      el.append(card('History',
        h('div', { class: 'character-kicker' }, 'Code score · last 14 days'),
        Apex.ui.bars(days.map((k) => { const s = computeScore(k); return s == null ? null : Math.round(s); }),
          { max: 100, color: 'var(--character-olive)', labels: days.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 80 })));

      const jar = cookieJar(ctx.date, 30);
      el.append(card('Cookie jar',
        h('p', { class: 'muted small' }, 'After David Goggins: a store of hard things you have already done. When you want to quit, reach in and remember who you are.'),
        jar.length ? h('ul', { class: 'character-jar' }, jar.map((x) => h('li', null,
          h('span', { class: 'character-jar-lvl', title: 'Difficulty' }, x.level != null ? `${x.level}/5` : '—'),
          h('div', { class: 'character-jar-body' },
            h('span', null, x.text || '(no description)'),
            h('span', { class: 'muted small' }, Apex.date.format(x.date, { weekday: 'short', month: 'short', day: 'numeric' }))))))
          : Apex.ui.empty('Empty jar. Do one hard thing today and log it above.')));

      el.append(card('Insight', h('p', { class: 'tip' }, tipFor(ctx.date))));
    },

    score(date) {
      return computeScore(date);
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = entry(date);
      if (!logged(d)) return '';
      const out = [];
      if (has(d.hard) || d.hardLevel != null) out.push(`Hard thing ${d.hardLevel != null ? d.hardLevel + '/5' : 'done'}`);
      if (d.word === true) out.push('word kept');
      else if (d.word === false) out.push('word broken');
      if (d.noComplain || (d.complaints || 0) > 0) out.push(`${d.complaints || 0} complaint${d.complaints === 1 ? '' : 's'}`);
      if (!out.length) {
        if (has(d.ownWrong)) out.push('ownership logged');
        if (d.cold) out.push('cold');
        if ((d.values || []).length) out.push(`${d.values.length} value${d.values.length === 1 ? '' : 's'} lived`);
      }
      return out.join(' · ');
    },
  });
})();
