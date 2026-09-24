/* Apex module: Boot Camp HQ. Daily orders (manual + auto-linked), demerits, drill sergeant,
 * Operation Iron 75, the Big Four of mental toughness (box-breathing timer), After Action Review.
 */
(function () {
  const { h, card, text, textarea, select, toggle, number, button, progress, bars, stat } = Apex.ui;
  const ID = 'bootcamp';
  const ROUND_MS = 16000; // box breathing: 4 phases x 4 s
  const PHASES = ['Breathe in', 'Hold', 'Breathe out', 'Hold'];
  const IRON_DAYS = 75;

  const DEFAULT_ORDERS = [
    { id: 'reveille', time: '05:30', text: 'Reveille: out of bed, no snooze' },
    { id: 'rack', time: '05:35', text: 'Make your rack (bed)' },
    { id: 'hydrate', time: '05:45', text: 'Hydrate + sunlight' },
    { id: 'pt', time: '06:00', text: 'PT', link: 'pt', min: 60 },
    { id: 'plan', time: '07:00', text: 'Plan the mission: Top 3', link: 'goals', min: 34 },
    { id: 'deep', time: '08:00', text: 'Deep work block', link: 'focus', min: 50 },
    { id: 'junk', time: '12:00', text: 'No junk food', link: 'nutrition', min: 60 },
    { id: 'study', time: '18:00', text: 'Read / study', link: 'learning', min: 50 },
    { id: 'aar', time: '21:00', text: 'After Action Review' },
    { id: 'gear', time: '21:30', text: 'Gear ready for tomorrow' },
    { id: 'lights', time: '22:00', text: 'Lights out' },
  ];
  const CFG = {
    orders: DEFAULT_ORDERS,
    iron: { start: null, strict: true, attempts: 0, best: 0, prevAttempts: 0 },
    breathRounds: 4,
    breath: null, // running box-breathing timer: { start, rounds, date }
  };
  const AAR_BLANK = { planned: '', happened: '', why: '', sustain: '' };
  const DEFAULTS = { checks: {}, demerits: [], goals: [], visualized: false, visualNote: '', selfTalk: '', breath: 0, aar: AAR_BLANK, rest: false };
  const DEMERIT_REASONS = ['Snoozed', 'Complained', 'Broke a rule', 'Made an excuse', 'Skipped a rep', 'Phone in bed'];

  // ---------- drill sergeant ----------
  const LINES = {
    perfect: [
      'Every order executed. That is what squared away looks like. Do it again tomorrow.',
      'Clean sweep, recruit. No excuses, no gaps. You earned your rack tonight.',
      'Perfect day. Don\'t get cocky: standards don\'t take days off.',
      'Outstanding. You said you would and you did. That is the whole game.',
    ],
    ontrack: [
      'On schedule. Keep the tempo. Next order, move!',
      'So far so good, recruit. Good is the enemy of done. Finish the list.',
      'You\'re in formation. Stay there. The day isn\'t won until lights out.',
      'Solid work. Don\'t coast. Coasting only goes downhill.',
    ],
    behind: [
      'You\'re falling behind, maggot. Stop reading this and knock out the next order.',
      'Missed orders don\'t fix themselves. Pick the next one and execute. Now.',
      'This day is slipping. Good news: it isn\'t over. Get your ass moving.',
      'Behind schedule. No speeches, no excuses: one order at a time, starting now.',
    ],
    reveille: [
      'You lost the first battle of the day to a pillow. Win the next one.',
      'Reveille missed. Tomorrow the alarm goes off and your feet hit the deck. Today, recover the mission.',
      'The snooze button is not your commanding officer. Get up when the order says get up.',
      'Late out of the rack. Make up for it with every order that\'s left.',
    ],
    demerits: [
      'Demerits are stacking up, recruit. Every one is a choice. Choose better.',
      'That demerit sheet is getting long. Tighten up or it will write your whole week.',
      'Too many demerits. Own every one of them, then stop adding more.',
      'Excuses don\'t do push-ups. Squash the demerits and square yourself away.',
    ],
    comeback: [
      'Yesterday was ugly. Today you\'re back in formation. That is how winners respond.',
      'Nobody cares that you fell. They care that you got back up. Keep going.',
      'Bad day behind you, good start in front of you. Don\'t miss twice.',
      'That\'s a comeback, recruit. Stack another day on it.',
    ],
    rest: [
      'Rest day authorised. Recovery is part of training, not a vacation from it.',
      'Stand down the hard training. Orders still stand: sleep, hydrate, prep your gear.',
      'Rest hard today so you can hit hard tomorrow. Lights out on time.',
    ],
    early: [
      'Day hasn\'t started yet, recruit. Lay out your gear and hit the rack on time.',
      'Clean slate. Every order is still open. Take them one by one.',
      'New day, zero excuses on the board. Keep it that way.',
    ],
  };
  const SIT_LABEL = { perfect: 'Squared away', ontrack: 'On track', behind: 'Falling behind', reveille: 'Missed reveille', demerits: 'Demerits', comeback: 'Comeback', rest: 'Rest day', early: 'Stand by' };

  const TIPS = [
    'Make your bed first thing. One task done before breakfast, and small wins stack into big ones. (Adm. William McRaven)',
    'Extreme ownership: nobody else is to blame for how your day went. Own the mission and the outcome. (Jocko Willink)',
    'Discipline equals freedom. The schedule you keep today buys the options you want tomorrow. (Jocko Willink)',
    'The 40% rule: when your mind says you are done, you usually have more in the tank. Go one more controlled rep, not one reckless one.',
    'Slow is smooth, smooth is fast. Rushed work gets redone. Do it right the first time.',
    'Embrace the suck. The discomfort you choose makes the discomfort you don\'t choose smaller.',
    'Keep the plan simple: no plan survives first contact intact, so fewer moving parts win. Top 3, not top 30.',
    'Two is one, one is none. Lay out tomorrow\'s gear tonight and keep a backup.',
    'Don\'t ring the bell. Quitting is a decision; make the opposite decision one evolution at a time.',
    'Sleep is a weapon. Elite units schedule it like any other mission. Lights out is an order, not a suggestion.',
  ];

  // ---------- styles ----------
  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.module-bootcamp { --bc-olive: #8a9a4b; --bc-khaki: #c8b98a; --bc-olive-bg: color-mix(in srgb, #6b7a3a 16%, var(--surface)); }
@media (prefers-color-scheme: light) { .module-bootcamp { --bc-olive: #4d5a22; --bc-khaki: #7a6a3a; --bc-olive-bg: color-mix(in srgb, #6b7a3a 10%, var(--surface)); } }
.module-bootcamp .card { border-top: 3px solid var(--bc-olive); }
.module-bootcamp .card-title, .bootcamp-stencil { text-transform: uppercase; letter-spacing: .16em; font-weight: 800; font-family: 'Stencil', 'Stencil Std', Impact, 'Arial Narrow', var(--font); color: var(--bc-khaki); }
.bootcamp-sarge { background: linear-gradient(135deg, #3b4724, #262f17); color: #efe8d0; border-color: #4d5a2e; }
.module-bootcamp .bootcamp-sarge { border-top-color: #c8b98a; }
.bootcamp-sarge-kicker { font-size: .72rem; letter-spacing: .2em; text-transform: uppercase; color: #c8bf9f; font-weight: 700; display: flex; gap: 8px; flex-wrap: wrap; }
.bootcamp-sarge-msg { font-size: 1.2rem; font-weight: 800; line-height: 1.3; margin: 8px 0 12px; overflow-wrap: anywhere; }
.bootcamp-sarge .stat { background: rgba(0,0,0,.25); }
.bootcamp-sarge .stat-label, .bootcamp-sarge .stat-sub { color: #c8bf9f; }
.bootcamp-sarge .progress { background: rgba(0,0,0,.3); }
.bootcamp-timeline { list-style: none; margin: 0; padding: 0; position: relative; }
.bootcamp-timeline::before { content: ''; position: absolute; left: 25px; top: 6px; bottom: 6px; width: 2px; background: var(--border); }
.bootcamp-order { display: grid; grid-template-columns: 52px minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 8px 0; position: relative; }
.bootcamp-time { font-variant-numeric: tabular-nums; font-weight: 800; font-size: .82rem; text-align: center; background: var(--surface); border: 2px solid var(--border); border-radius: 6px; padding: 2px 0; position: relative; z-index: 1; letter-spacing: .04em; }
.bootcamp-order.done .bootcamp-time { border-color: var(--good); }
.bootcamp-order.late .bootcamp-time { border-color: var(--accent); }
.bootcamp-order.missed .bootcamp-time { border-color: var(--bad); }
.bootcamp-order-text { font-weight: 600; overflow-wrap: anywhere; }
.bootcamp-order.done .bootcamp-order-text, .bootcamp-order.late .bootcamp-order-text { opacity: .75; }
.bootcamp-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: .76rem; color: var(--muted); margin-top: 2px; }
.bootcamp-badge { display: inline-block; font-size: .64rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
.bootcamp-badge.done { background: var(--good); border-color: var(--good); color: #0b1a0f; }
.bootcamp-badge.late { background: var(--accent); border-color: var(--accent); color: #111; }
.bootcamp-badge.missed { background: var(--bad); border-color: var(--bad); color: #fff; }
.bootcamp-check { width: 38px; height: 38px; border-radius: 8px; border: 2px solid var(--border); background: var(--surface-2); color: var(--text); font: inherit; font-weight: 800; font-size: 1.1rem; cursor: pointer; display: grid; place-items: center; }
.bootcamp-check[aria-pressed="true"] { background: var(--good); border-color: var(--good); color: #0b1a0f; }
.bootcamp-check.auto { font-size: .9rem; text-decoration: none; }
.bootcamp-stats { margin-bottom: 12px; }
.bootcamp-reasons { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
.bootcamp-reasons .pill { min-width: 0; font-size: .8rem; padding: 5px 10px; }
.bootcamp-iron-grid { display: grid; grid-template-columns: repeat(15, minmax(0, 1fr)); gap: 3px; margin: 10px 0; max-width: 520px; }
.bootcamp-cell { aspect-ratio: 1; border-radius: 3px; background: var(--surface-2); border: 1px solid var(--border); min-width: 0; }
.bootcamp-cell.pass { background: var(--bc-olive); border-color: var(--bc-olive); }
.bootcamp-cell.fail { background: var(--bad); border-color: var(--bad); }
.bootcamp-cell.today { outline: 2px solid var(--accent); outline-offset: 1px; }
.bootcamp-iron-day { font-size: 2.2rem; font-weight: 900; font-variant-numeric: tabular-nums; letter-spacing: .06em; line-height: 1; }
.bootcamp-iron-day small { font-size: .9rem; color: var(--muted); letter-spacing: .1em; }
.bootcamp-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.bootcamp-big4 h4 { margin: 14px 0 6px; font-size: .78rem; text-transform: uppercase; letter-spacing: .14em; color: var(--bc-khaki); }
.bootcamp-big4 h4:first-child { margin-top: 0; }
.bootcamp-goal { display: flex; align-items: center; gap: 8px; }
.bootcamp-goal .toggle { flex: 1; min-width: 0; }
.bootcamp-goal .toggle-label { overflow-wrap: anywhere; }
.bootcamp-breath { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.bootcamp-box { position: relative; width: 120px; height: 120px; flex: none; border: 4px solid var(--border); border-radius: 6px; display: grid; place-items: center; text-align: center; background: var(--bc-olive-bg); }
.bootcamp-box[data-phase="0"] { border-left-color: var(--bc-olive); }
.bootcamp-box[data-phase="1"] { border-top-color: var(--bc-olive); }
.bootcamp-box[data-phase="2"] { border-right-color: var(--bc-olive); }
.bootcamp-box[data-phase="3"] { border-bottom-color: var(--bc-olive); }
.bootcamp-box-phase { font-weight: 800; text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; }
.bootcamp-box-count { font-size: 1.8rem; font-weight: 900; font-variant-numeric: tabular-nums; line-height: 1.1; }
.bootcamp-dot { position: absolute; width: 14px; height: 14px; border-radius: 50%; background: var(--accent); left: 0; top: 100%; transform: translate(-50%, -50%); box-shadow: 0 0 8px var(--accent); }
@media (prefers-reduced-motion: no-preference) { .bootcamp-dot { animation: bootcamp-trace 16s linear infinite; } }
@media (prefers-reduced-motion: reduce) { .bootcamp-dot { display: none; } }
@keyframes bootcamp-trace { 0% { left: 0; top: 100%; } 25% { left: 0; top: 0; } 50% { left: 100%; top: 0; } 75% { left: 100%; top: 100%; } 100% { left: 0; top: 100%; } }
.bootcamp-edit { display: grid; grid-template-columns: 136px minmax(0, 1fr) auto; gap: 8px; align-items: end; border-bottom: 1px solid var(--border); padding: 8px 0; }
.bootcamp-edit:last-of-type { border-bottom: 0; }
.bootcamp-edit .field { margin: 0; }
.bootcamp-edit-link { grid-column: 1 / -1; display: grid; grid-template-columns: minmax(0, 1fr) 110px; gap: 8px; }
.bootcamp-edit-link.manual { grid-template-columns: minmax(0, 1fr); }
.bootcamp-aar .field span { text-transform: uppercase; letter-spacing: .08em; font-size: .72rem; font-weight: 700; }
.module-bootcamp .tip::before { content: '🎖️ '; }
`));
  }

  // ---------- helpers ----------
  const pad = (n) => String(n).padStart(2, '0');
  const toMin = (t) => {
    const m = /^(\d{1,2}):(\d{2})/.exec(String(t || ''));
    return m ? Number(m[1]) * 60 + Number(m[2]) : 0;
  };
  const nowHHMM = () => { const d = new Date(); return `${pad(d.getHours())}:${pad(d.getMinutes())}`; };
  const hasText = (s) => !!String(s || '').trim();
  const newId = () => 'o' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  function hash(s) {
    let x = 0;
    for (let i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) | 0;
    return Math.abs(x);
  }

  function cfg() {
    const c = Apex.store.getConfig(ID, CFG);
    c.orders = Array.isArray(c.orders) ? c.orders : [];
    c.iron = Object.assign({}, CFG.iron, c.iron || {});
    return c;
  }
  const saveCfg = (c) => Apex.store.setConfig(ID, c);
  const sorted = (orders) => orders.slice().sort((a, b) => toMin(a.time) - toMin(b.time));

  function day(date) {
    const d = Apex.store.get(ID, date, DEFAULTS);
    d.checks = d.checks && typeof d.checks === 'object' ? d.checks : {};
    d.demerits = Array.isArray(d.demerits) ? d.demerits : [];
    d.goals = Array.isArray(d.goals) ? d.goals : [];
    d.aar = Object.assign({}, AAR_BLANK, d.aar || {});
    d.breath = Number(d.breath) || 0;
    return d;
  }
  const aarFull = (d) => Object.keys(AAR_BLANK).every((k) => hasText(d.aar[k]));
  const aarAny = (d) => Object.keys(AAR_BLANK).some((k) => hasText(d.aar[k]));

  /** The module an order is linked to, if it's valid and enabled; otherwise null (manual order). */
  function linkedModule(o, enabledIds) {
    if (!o.link || o.link === ID) return null;
    const m = Apex.modules.get(o.link);
    return m && enabledIds.has(m.id) ? m : null;
  }

  // Guard against a linked module whose score() ends up calling ours.
  let busy = false;

  /** Evaluate every order for a date. Real time only matters for PENDING vs MISSED on today. */
  function evalDay(date, c, d) {
    c = c || cfg();
    d = d || day(date);
    const today = Apex.date.today();
    const nowM = toMin(nowHHMM());
    const enabledIds = new Set(Apex.modules.enabled().map((m) => m.id));
    const rows = sorted(c.orders).map((o) => {
      const m = linkedModule(o, enabledIds);
      const r = { o, m, st: 'pending', auto: false, at: null, modScore: null };
      if (m) {
        r.modScore = Apex.moduleScore(m, date);
        if (r.modScore != null && r.modScore >= (Number(o.min) || 0)) { r.st = 'done'; r.auto = true; return r; }
      } else if (d.checks[o.id]) {
        r.at = d.checks[o.id].at || null;
        r.via = d.checks[o.id].via || null;
        r.st = r.at != null && toMin(r.at) > toMin(o.time) + 15 ? 'late' : 'done';
        return r;
      }
      if (date < today) r.st = 'missed';
      else if (date === today && nowM > toMin(o.time) + 60) r.st = 'missed';
      return r;
    });
    const count = (s) => rows.filter((r) => r.st === s).length;
    const done = count('done');
    const late = count('late');
    const missed = count('missed');
    const n = rows.length;
    const completion = n ? (done + late * 0.5) / n : 0;
    const manualChecks = rows.some((r) => !r.m && d.checks[r.o.id]);
    const autoDone = rows.some((r) => r.auto);
    const logged = manualChecks || autoDone || aarAny(d) || d.breath > 0 || d.demerits.length > 0;
    return {
      rows, n, done, late, missed, pending: count('pending'), completion,
      pct: Math.round(completion * 100),
      full: n > 0 && done + late === n,
      manualDem: d.demerits.length,
      demerits: missed + d.demerits.length,
      logged, d,
    };
  }

  function scoreOf(date) {
    const c = cfg();
    const d = day(date);
    const ev = evalDay(date, c, d);
    if (!ev.logged) return null;
    let s = 85 * ev.completion;
    if (aarFull(d)) s += 10;
    if (d.breath >= 4) s += 5;
    s -= 5 * d.demerits.length;
    return Math.max(0, Math.min(100, s));
  }

  /** Consecutive days at 100% (every order DONE on time) ending at `date`; today may still be in progress. */
  function streak(date, c) {
    let n = 0;
    let k = date;
    const today = Apex.date.today();
    for (let i = 0; i < 365; i++, k = Apex.date.add(k, -1)) {
      const ev = evalDay(k, c);
      if (ev.n && ev.pct === 100) n++;
      else if (k === date && k === today) continue;
      else break;
    }
    return n;
  }

  // ---------- Operation Iron 75 ----------
  const ironPass = (ev) => ev.full && ev.manualDem === 0;

  /** Scan from the start date. Strict mode: a failed day resets the counter; the next day is day 1. */
  function ironState(c) {
    const ir = c.iron;
    if (!ir.start) return null;
    const today = Apex.date.today();
    let runStart = ir.start;
    let attempts = 1;
    let run = 0;
    let best = 0;
    let completed = null;
    const result = {}; // date -> 'pass' | 'fail'
    let todayEv = null;
    for (let k = ir.start, i = 0; k <= today && i < 3000; k = Apex.date.add(k, 1), i++) {
      const ev = evalDay(k, c);
      const pass = ironPass(ev);
      if (k === today) {
        todayEv = ev;
        if (pass) { result[k] = 'pass'; run++; best = Math.max(best, run); }
        if (pass && Apex.date.diff(k, runStart) + 1 >= IRON_DAYS) completed = k;
        break;
      }
      if (pass) {
        result[k] = 'pass';
        run++;
        best = Math.max(best, run);
      } else {
        result[k] = 'fail';
        run = 0;
        if (ir.strict) { attempts++; runStart = Apex.date.add(k, 1); }
      }
      if (Apex.date.diff(k, runStart) + 1 >= IRON_DAYS) { completed = k; break; }
    }
    const dayNo = completed ? IRON_DAYS : Math.min(IRON_DAYS, Apex.date.diff(today, runStart) + 1);
    const passes = Object.keys(result).filter((k) => k >= runStart && result[k] === 'pass').length;
    return { runStart, attempts: attempts + (ir.prevAttempts || 0), best: Math.max(best, ir.best || 0), dayNo, completed, result, passes, todayEv, today };
  }

  // ---------- box breathing timer (state in config so it survives re-renders) ----------
  function addBreath(date, rounds) {
    if (rounds <= 0) return;
    Apex.store.update(ID, date, (d) => { d.breath = (Number(d.breath) || 0) + rounds; }, DEFAULTS);
  }
  function finalizeBreath() {
    const c = cfg();
    const t = c.breath;
    if (!t || Date.now() - t.start < t.rounds * ROUND_MS) return false;
    c.breath = null;
    saveCfg(c);
    addBreath(t.date, t.rounds);
    Apex.ui.toast(`🫁 Box breathing: ${plural(t.rounds, 'round')} logged. Calm is a weapon.`);
    return true;
  }
  function stopBreath() {
    const c = cfg();
    const t = c.breath;
    if (!t) return;
    const rounds = Math.min(t.rounds, Math.floor((Date.now() - t.start) / ROUND_MS));
    c.breath = null;
    saveCfg(c);
    addBreath(t.date, rounds);
    Apex.ui.toast(rounds ? `Logged ${plural(rounds, 'round')}` : 'Stopped before a full round: nothing logged');
  }
  // Finish the timer in the background while the user is on another page (writes only, never re-renders).
  setInterval(() => {
    if (document.querySelector('.bootcamp-box')) return;
    try { finalizeBreath(); } catch (e) { /* ignore */ }
  }, 1000);

  function breathCard(ctx, d) {
    const c = cfg();
    const t = c.breath;
    const logged = h('p', { class: 'muted small' }, `Logged ${ctx.date === ctx.today ? 'today' : 'this day'}: ${plural(d.breath, 'round')}${d.breath >= 4 ? ' ✓' : ' · 4+ rounds = +5 points'}`);
    if (!t) {
      return h('div', null,
        h('div', { class: 'bootcamp-breath' },
          h('div', { class: 'bootcamp-box', 'data-phase': '-1', 'aria-hidden': 'true' },
            h('div', null, h('div', { class: 'bootcamp-box-phase' }, '4 · 4 · 4 · 4'), h('div', { class: 'muted small' }, 'in · hold · out · hold'))),
          h('div', { style: { flex: '1', minWidth: '140px' } },
            number({ label: 'Rounds', value: c.breathRounds, min: 1, max: 30, step: 1,
              onChange: (v) => { const cc = cfg(); cc.breathRounds = v && v > 0 ? Math.min(30, Math.round(v)) : CFG.breathRounds; saveCfg(cc); ctx.refresh(); } }),
            button('▶ Start box breathing', () => {
              const cc = cfg();
              cc.breath = { start: Date.now(), rounds: cc.breathRounds || CFG.breathRounds, date: ctx.date };
              saveCfg(cc);
              ctx.refresh();
            }, 'primary'))),
        logged);
    }
    const elapsed = () => Math.max(0, Date.now() - t.start);
    const phaseEl = h('div', { class: 'bootcamp-box-phase', 'aria-live': 'polite' });
    const countEl = h('div', { class: 'bootcamp-box-count' });
    const roundEl = h('div', { class: 'bootcamp-stencil small' });
    const dot = h('span', { class: 'bootcamp-dot', style: { animationDelay: `-${elapsed() % ROUND_MS}ms` } });
    const box = h('div', { class: 'bootcamp-box', role: 'timer', 'aria-label': 'Box breathing guide' }, dot, h('div', null, phaseEl, countEl));
    let lastPhase = -1;
    const tick = () => {
      const e = elapsed();
      const p = Math.floor(e / 4000) % 4;
      box.dataset.phase = String(p);
      if (p !== lastPhase) { phaseEl.textContent = PHASES[p]; lastPhase = p; }
      countEl.textContent = String(4 - Math.floor((e % 4000) / 1000));
      roundEl.textContent = `Round ${Math.min(t.rounds, Math.floor(e / ROUND_MS) + 1)} / ${t.rounds}`;
    };
    tick();
    const iv = setInterval(() => {
      if (!box.isConnected) { clearInterval(iv); return; }
      const cur = cfg().breath;
      if (!cur || cur.start !== t.start) { clearInterval(iv); ctx.refresh(); return; }
      if (elapsed() >= t.rounds * ROUND_MS) {
        clearInterval(iv);
        if (finalizeBreath()) ctx.refresh();
        return;
      }
      tick();
    }, 200);
    return h('div', null,
      h('div', { class: 'bootcamp-breath' }, box,
        h('div', { style: { flex: '1', minWidth: '140px' } }, roundEl,
          t.date !== ctx.date ? h('p', { class: 'muted small' }, `Logging to ${Apex.date.format(t.date)}`) : null,
          h('div', { class: 'bootcamp-actions' }, button('■ Stop & log full rounds', () => { stopBreath(); ctx.refresh(); })))),
      logged);
  }

  // ---------- drill sergeant ----------
  function situation(ctx, ev, c) {
    const d = ev.d;
    if (ev.manualDem >= 2 || ev.demerits >= 3) return 'demerits';
    if (ev.full) return 'perfect';
    if (d.rest) return 'rest';
    const first = ev.rows.find((r) => /reveille/i.test(r.o.text)) || ev.rows[0];
    if (first && (first.st === 'missed' || first.st === 'late')) return 'reveille';
    if (!ev.missed) {
      const y = evalDay(Apex.date.add(ctx.date, -1), c);
      if (y.logged && y.pct < 50 && (ev.done + ev.late) > 0) return 'comeback';
    }
    if (ev.missed) return 'behind';
    if (ev.done + ev.late === 0) return 'early';
    return 'ontrack';
  }

  function sergeantCard(ctx, ev, c, st, iron) {
    const sit = situation(ctx, ev, c);
    const pool = LINES[sit];
    const line = pool[hash(ctx.date + ':' + sit) % pool.length];
    const isToday = ctx.date === ctx.today;
    const kicker = isToday ? `${nowHHMM().replace(':', '')} HRS` : `Debrief · ${Apex.date.format(ctx.date)}`;
    const extra = st >= 2 && (sit === 'perfect' || sit === 'ontrack') ? ` ${st} straight days at 100%. Protect the streak.` : '';
    return h('section', { class: 'card bootcamp-sarge' },
      h('div', { class: 'bootcamp-sarge-kicker' }, h('span', null, '🪖 Drill Sergeant'), h('span', null, '·'), h('span', null, kicker), h('span', null, '·'), h('span', null, SIT_LABEL[sit])),
      h('p', { class: 'bootcamp-sarge-msg' }, line + extra),
      h('div', { class: 'kpis' },
        stat('Orders', `${ev.done + ev.late}/${ev.n}`, `${ev.pct}% complete`),
        stat('Demerits', String(ev.demerits), ev.manualDem ? `${ev.manualDem} logged · ${ev.missed} missed` : `${ev.missed} missed`),
        stat('Streak', `${st}d`, '100% days'),
        stat('Iron 75', iron ? (iron.completed ? '✓ 75' : `Day ${iron.dayNo}`) : '—', iron ? `attempt ${iron.attempts}` : 'not enlisted')),
      h('div', { style: { marginTop: '12px' } }, progress(ev.completion * 100, 100, ev.full ? 'var(--good)' : '#c8b98a')));
  }

  // ---------- cards ----------
  function ordersCard(ctx, ev, d, save) {
    const isToday = ctx.date === ctx.today;
    const items = ev.rows.map((r) => {
      const o = r.o;
      const label = { done: 'Done', late: 'Late', pending: 'Pending', missed: 'Missed' }[r.st];
      const meta = [h('span', { class: 'bootcamp-badge ' + r.st }, label)];
      let action;
      if (r.m) {
        const href = '#/m/' + r.m.id;
        if (r.auto) meta.push(h('span', null, 'auto ✓ from ', h('a', { href }, `${r.m.icon} ${r.m.name}`), ` (${r.modScore})`));
        else meta.push(h('span', null, 'auto when ', h('a', { href }, `${r.m.icon} ${r.m.name}`), ` ≥ ${Number(o.min) || 0}`, r.modScore != null ? ` · now ${r.modScore}` : ' · not logged'));
        action = h('a', { class: 'bootcamp-check auto', href, 'aria-label': `Open ${r.m.name}` }, r.auto ? '✓' : '→');
      } else {
        const checked = !!d.checks[o.id];
        if (checked) {
          const when = r.at ? `at ${r.at}` : 'logged after the fact';
          meta.push(h('span', null, r.via === 'aar' ? `via AAR${r.at ? ' · ' + when : ''}` : when));
        }
        if (o.link) meta.push(h('span', null, '(link unavailable: manual)'));
        action = h('button', {
          type: 'button', class: 'bootcamp-check', 'aria-pressed': checked ? 'true' : 'false', 'aria-label': (checked ? 'Undo: ' : 'Check off: ') + o.text,
          onClick: () => {
            if (checked) delete d.checks[o.id];
            else d.checks[o.id] = { at: isToday ? nowHHMM() : null };
            save();
          },
        }, checked ? '✓' : '');
      }
      return h('li', { class: 'bootcamp-order ' + r.st },
        h('span', { class: 'bootcamp-time' }, o.time),
        h('div', { style: { minWidth: '0' } }, h('div', { class: 'bootcamp-order-text' }, o.text), h('div', { class: 'bootcamp-meta' }, meta)),
        action);
    });
    return card(`Daily orders · ${isToday ? 'today' : Apex.date.format(ctx.date)}`,
      h('div', { class: 'row bootcamp-stats', style: { alignItems: 'center' } },
        h('span', { class: 'small muted' }, `${ev.done + ev.late}/${ev.n} executed · ${ev.pct}%`), progress(ev.completion * 100, 100, ev.full ? 'var(--good)' : 'var(--bc-olive)')),
      ev.rows.length ? h('ol', { class: 'bootcamp-timeline' }, items) : Apex.ui.empty('No orders. Add some in the orders editor below.'),
      h('p', { class: 'muted small', style: { marginTop: '8px', marginBottom: '0' } },
        isToday ? 'Checked more than 15 min after the order time = LATE (half credit). Over 60 min past with nothing = MISSED.' : 'Past day: anything not done is MISSED. Check-offs here count as done after the fact.'));
  }

  function demeritsCard(ctx, ev, d, save, c) {
    const week = Apex.date.lastN(ctx.date, 7).reduce((a, k) => a + evalDay(k, c).demerits, 0);
    const add = (reason) => { d.demerits.push({ reason, at: ctx.date === ctx.today ? nowHHMM() : null }); save(); };
    return card('Demerits',
      h('div', { class: 'kpis bootcamp-stats' },
        stat('Today', String(ev.demerits), `${ev.missed} missed + ${ev.manualDem} logged`),
        stat('Last 7 days', String(week)),
        stat('Score hit', ev.manualDem ? `−${ev.manualDem * 5}` : '0', '−5 per logged demerit')),
      h('p', { class: 'muted small' }, 'Every missed order is 1 demerit automatically. Be honest and log the rest:'),
      h('div', { class: 'bootcamp-reasons' }, DEMERIT_REASONS.map((r) => h('button', { type: 'button', class: 'pill', onClick: () => add(r) }, '+ ' + r))),
      Apex.ui.adder('Other reason…', add),
      h('div', { style: { marginTop: '8px' } },
        Apex.ui.list(d.demerits, (x) => h('span', null, '⚠️ ', x.reason, x.at ? h('span', { class: 'muted small' }, ` · ${x.at}`) : null),
          (i) => { d.demerits.splice(i, 1); save(); })));
  }

  function ironCard(ctx, c, iron) {
    const ir = c.iron;
    const setIron = (fn) => { const cc = cfg(); fn(cc.iron, cc); saveCfg(cc); ctx.refresh(); };
    const strictToggle = toggle({ label: 'Strict mode', hint: 'A failed day sends you back to day 1', checked: ir.strict,
      onChange: (v) => setIron((x) => { x.strict = v; }) });
    const rules = h('p', { class: 'muted small' }, 'A day passes only when every order is DONE (LATE still passes) and you log zero demerits. 75 days. No days off.');
    if (!iron) {
      return card('Operation Iron 75', rules, strictToggle,
        ir.best ? h('p', { class: 'small' }, `Best run so far: ${ir.best} days over ${plural(ir.attempts, 'attempt')}.`) : null,
        h('div', { class: 'bootcamp-actions' }, button('🪖 Enlist today', () => setIron((x) => { x.start = ctx.today; }), 'primary')));
    }
    const cells = [];
    for (let i = 0; i < IRON_DAYS; i++) {
      const k = Apex.date.add(iron.runStart, i);
      const r = iron.result[k];
      let cls = 'bootcamp-cell';
      let title = `Day ${i + 1} · ${Apex.date.format(k)}`;
      if (r === 'pass') { cls += ' pass'; title += ': pass'; } else if (r === 'fail') { cls += ' fail'; title += ': fail'; }
      if (k === iron.today) { cls += ' today'; if (!r) title += ': in progress'; }
      cells.push(h('div', { class: cls, title }));
    }
    const tev = iron.todayEv;
    let todayLine = null;
    if (!iron.completed && tev) {
      todayLine = ironPass(tev) ? 'Today: passing. Hold the line until lights out.'
        : tev.manualDem ? 'Today: demerit logged. This day will fail.'
          : tev.missed ? `Today: ${plural(tev.missed, 'order')} missed. This day will fail unless you still check them off.`
            : `Today: ${ev2left(tev)} to go.`;
    }
    return card('Operation Iron 75',
      h('div', { class: 'row', style: { alignItems: 'baseline' } },
        h('div', { class: 'bootcamp-iron-day' }, iron.completed ? 'COMPLETE ' : `DAY ${iron.dayNo}`, h('small', null, iron.completed ? '75/75' : ` / ${IRON_DAYS}`)),
        h('span', { class: 'spacer' }),
        h('span', { class: 'small muted' }, `Attempt ${iron.attempts} · best run ${iron.best}d`)),
      h('div', { class: 'bootcamp-iron-grid', role: 'img', 'aria-label': `Iron 75 progress: day ${iron.dayNo} of 75` }, cells),
      iron.completed ? h('p', null, h('strong', null, 'Mission complete. '), 'Seventy-five days of kept promises. You are not the same recruit who enlisted.') : null,
      todayLine ? h('p', { class: 'small' }, todayLine) : null,
      rules, strictToggle,
      h('p', { class: 'muted small' }, `Enlisted ${Apex.date.format(ir.start)}${iron.runStart !== ir.start ? ` · current run since ${Apex.date.format(iron.runStart)}` : ''}.`),
      h('div', { class: 'bootcamp-actions' },
        button('Re-enlist (restart today)', () => {
          if (!confirm('Re-enlist? Your current run ends and day 1 starts today.')) return;
          setIron((x) => { x.prevAttempts = iron.attempts; x.best = iron.best; x.attempts = iron.attempts + 1; x.start = ctx.today; });
        }),
        button('Abort mission', () => {
          if (!confirm('Abort Operation Iron 75? Your best run is kept.')) return;
          setIron((x) => { x.prevAttempts = iron.attempts; x.best = iron.best; x.attempts = iron.attempts; x.start = null; });
        }, 'danger')));
  }
  const ev2left = (ev) => plural(ev.n - ev.done - ev.late, 'order');

  function bigFourCard(ctx, d, save) {
    return card('Mental toughness · the Big Four',
      h('div', { class: 'bootcamp-big4' },
        h('p', { class: 'muted small' }, 'The four skills from the Navy SEAL mental-toughness training developed with psychologist Eric Potterat.'),
        h('h4', null, '1 · Goal setting: micro-goals'),
        h('p', { class: 'muted small' }, 'Shrink the day to the next small target: make it to the next order, the next set, the next hour.'),
        d.goals.length ? d.goals.map((g, i) => h('div', { class: 'bootcamp-goal' },
          toggle({ label: g.text, checked: !!g.done, onChange: (v) => { d.goals[i].done = v; save(); } }),
          h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Remove micro-goal ' + g.text, onClick: () => { d.goals.splice(i, 1); save(); } }, '✕'))) : null,
        Apex.ui.adder('Micro-goal, e.g. "Finish set 3 with good form"', (v) => { d.goals.push({ text: v, done: false }); save(); }),
        h('h4', null, '2 · Visualization'),
        toggle({ label: 'Rehearsed today\'s hardest task in my head', hint: 'See it go right, see it go wrong, see yourself recover.', checked: !!d.visualized,
          onChange: (v) => { d.visualized = v; save(); } }),
        text({ label: 'What did you rehearse?', value: d.visualNote, placeholder: 'e.g. The tough conversation at 14:00',
          onChange: (v) => { d.visualNote = v; save(); } }),
        h('h4', null, '3 · Self-talk'),
        text({ label: 'Replace one negative thought with a command', value: d.selfTalk, placeholder: '"I can\'t" → "Next rep. Move."',
          onChange: (v) => { d.selfTalk = v; save(); } }),
        h('h4', null, '4 · Arousal control: box breathing'),
        breathCard(ctx, d)));
  }

  function aarCard(ctx, c, d, save) {
    const fields = [
      ['planned', 'What was planned?', 'The orders, the Top 3, the targets.'],
      ['happened', 'What actually happened?', 'Facts only. No excuses.'],
      ['why', 'Why was there a difference?', 'Root cause, not blame.'],
      ['sustain', 'What will we sustain / improve?', 'One thing to keep, one thing to fix tomorrow.'],
    ];
    const enabledIds = new Set(Apex.modules.enabled().map((m) => m.id));
    const onChange = (k, v) => {
      d.aar[k] = v;
      if (aarFull(d)) {
        const o = c.orders.find((x) => /after action review/i.test(x.text || '') && !linkedModule(x, enabledIds));
        if (o && !d.checks[o.id]) d.checks[o.id] = { at: ctx.date === ctx.today ? nowHHMM() : null, via: 'aar' };
      }
      save();
    };
    return card('After Action Review',
      h('p', { class: 'muted small' }, 'US Army format. Fill all four to complete it (+10 points) and check off the After Action Review order.'),
      h('div', { class: 'bootcamp-aar' }, fields.map(([k, label, ph]) => textarea({ label, value: d.aar[k], placeholder: ph, rows: 2, onChange: (v) => onChange(k, v) }))),
      aarFull(d) ? h('p', { class: 'small', style: { marginBottom: '0' } }, '✓ AAR complete. Carry the lesson into tomorrow.') : null);
  }

  function historyCard(ctx, c, st) {
    const days = Apex.date.lastN(ctx.date, 14);
    const vals = days.map((k) => { const ev = evalDay(k, c); return ev.logged ? ev.pct : null; });
    const logged = vals.filter((v) => v != null);
    const avg = logged.length ? Math.round(logged.reduce((a, b) => a + b, 0) / logged.length) : null;
    return card('Last 14 days · order completion',
      bars(vals, { max: 100, color: 'var(--bc-olive)', labels: days.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 100 }),
      h('p', { class: 'muted small', style: { marginTop: '8px', marginBottom: '0' } },
        `Streak of 100% days: ${st}d` + (avg != null ? ` · avg ${avg}% on ${plural(logged.length, 'logged day')}` : ' · nothing logged yet')));
  }

  function editorCard(ctx, c) {
    const update = (id, fn) => { const cc = cfg(); const o = cc.orders.find((x) => x.id === id); if (!o) return; fn(o); cc.orders = sorted(cc.orders); saveCfg(cc); ctx.refresh(); };
    const mods = Apex.modules.enabled().filter((m) => m.id !== ID);
    const rows = sorted(c.orders).map((o) => {
      const opts = [{ value: '', label: 'Manual check-off' }].concat(mods.map((m) => ({ value: m.id, label: `Auto: ${m.icon} ${m.name}` })));
      if (o.link && !mods.some((m) => m.id === o.link)) opts.push({ value: o.link, label: `${o.link} (unavailable: manual)` });
      const linkSel = select({ label: 'Completion', value: o.link || '', options: opts,
        onChange: (v) => update(o.id, (x) => {
          if (!v || v === ID) { delete x.link; delete x.min; } else { x.link = v; if (x.min == null) x.min = 50; }
        }) });
      return h('div', { class: 'bootcamp-edit' },
        text({ label: 'Time', type: 'time', value: o.time, onChange: (v) => update(o.id, (x) => { if (/^\d{2}:\d{2}$/.test(v)) x.time = v; }) }),
        text({ label: 'Order', value: o.text, onChange: (v) => update(o.id, (x) => { x.text = v.trim() || x.text; }) }),
        h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Delete order ' + o.text, onClick: () => {
          if (!confirm(`Delete order "${o.text}"?`)) return;
          const cc = cfg(); cc.orders = cc.orders.filter((x) => x.id !== o.id); saveCfg(cc); ctx.refresh();
        } }, '✕'),
        h('div', { class: 'bootcamp-edit-link' + (o.link ? '' : ' manual') }, linkSel,
          o.link ? number({ label: 'Min score', value: o.min, min: 0, max: 100, step: 1,
            onChange: (v) => update(o.id, (x) => { x.min = v == null ? 0 : Math.max(0, Math.min(100, Math.round(v))); }) }) : null));
    });
    return card('Orders editor',
      h('p', { class: 'muted small' }, 'Set the time and the order. Auto orders complete themselves when the linked tracker scores at least the minimum that day. Always sorted by time.'),
      rows.length ? rows : Apex.ui.empty('No orders.'),
      h('div', { class: 'bootcamp-actions' },
        button('+ Add order', () => { const cc = cfg(); cc.orders = sorted(cc.orders.concat({ id: newId(), time: '12:00', text: 'New order' })); saveCfg(cc); ctx.refresh(); }, 'primary'),
        button('Restore default orders', () => {
          if (!confirm('Replace your orders with the default schedule?')) return;
          const cc = cfg(); cc.orders = DEFAULT_ORDERS.map((x) => Object.assign({}, x)); saveCfg(cc); ctx.refresh();
        }, 'ghost')));
  }

  Apex.registerModule({
    id: ID,
    name: 'Boot Camp HQ',
    icon: '🪖',
    category: 'discipline',
    order: 1,
    weight: 1,
    description: 'Your orders for the day, recruit. Execute on time, own your demerits, and nobody has to drag you to the top.',

    render(el, ctx) {
      injectStyle();
      finalizeBreath();
      const c = cfg();
      const d = day(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const ev = evalDay(ctx.date, c, d);
      const st = streak(ctx.date, c);
      const iron = ironState(c);
      if (iron && (iron.attempts !== c.iron.attempts || iron.best !== c.iron.best)) {
        const cc = cfg(); cc.iron.attempts = iron.attempts; cc.iron.best = iron.best; saveCfg(cc); // record, no refresh
      }

      el.append(
        sergeantCard(ctx, ev, c, st, iron),
        ordersCard(ctx, ev, d, save),
        h('div', { class: 'grid grid-2' }, demeritsCard(ctx, ev, d, save, c), ironCard(ctx, c, iron)),
        h('div', { class: 'grid grid-2' }, bigFourCard(ctx, d, save), aarCard(ctx, c, d, save)),
        historyCard(ctx, c, st),
        card('Rest day',
          toggle({ label: 'Authorised rest day', hint: 'Changes the drill sergeant\'s brief only. Orders still stand.', checked: !!d.rest,
            onChange: (v) => { d.rest = v; save(); } })),
        editorCard(ctx, c),
        h('p', { class: 'tip' }, TIPS[hash('tip' + ctx.date) % TIPS.length]));
    },

    /** Pure: own data + linked modules' scores. Never calls Apex.lifeScore. */
    score(date) {
      if (busy) return null;
      busy = true;
      try {
        return scoreOf(date);
      } finally {
        busy = false;
      }
    },

    summary(date) {
      if (busy) return '';
      busy = true;
      try {
        const c = cfg();
        const ev = evalDay(date, c);
        const parts = [`${ev.done + ev.late}/${ev.n} orders`, plural(ev.demerits, 'demerit')];
        const iron = ironState(c);
        if (iron) parts.push(iron.completed ? 'Iron 75 complete' : `Iron 75 day ${iron.dayNo}`);
        return parts.join(' · ');
      } finally {
        busy = false;
      }
    },
  });
})();
