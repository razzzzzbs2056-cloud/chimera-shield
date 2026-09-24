/* Apex module: Deep Work. Focus timer (survives navigation), sessions, distractions, daily goal. */
(function () {
  const { h, card, number, text, rating, button, progress, bars, stat } = Apex.ui;
  const ID = 'focus';
  const DEFAULTS = { sessions: [], distractions: 0 };
  const CFG = { goal: 240, timerMinutes: 50, timer: null };

  // Draft for the manual entry form; module-level so it survives re-renders.
  const draft = { label: '', minutes: null, quality: null };

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.focus-clock { font-size: 3rem; font-weight: 800; font-variant-numeric: tabular-nums; letter-spacing: .02em; text-align: center; line-height: 1.1; margin: 4px 0 6px; }
.focus-clock-label { text-align: center; margin-bottom: 10px; overflow-wrap: anywhere; }
.focus-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.focus-presets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.focus-counter { display: flex; align-items: center; gap: 12px; }
.focus-counter strong { font-size: 1.8rem; font-variant-numeric: tabular-nums; min-width: 2ch; text-align: center; }
.focus-session { display: flex; flex-direction: column; gap: 4px; }
.focus-session-head { display: flex; gap: 8px; justify-content: space-between; flex-wrap: wrap; }
.focus-session .rating .pill { padding: 2px 8px; min-width: 30px; font-size: .8rem; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CFG);
  const minutesOf = (d) => (d.sessions || []).reduce((a, s) => a + (Number(s.minutes) || 0), 0);
  /** Minute-weighted avg quality; unrated sessions count as 3. */
  function avgQuality(d) {
    const ss = (d.sessions || []).filter((s) => s.minutes > 0);
    const mins = ss.reduce((a, s) => a + s.minutes, 0);
    if (!mins) return null;
    return ss.reduce((a, s) => a + (s.quality || 3) * s.minutes, 0) / mins;
  }
  const remainingMs = (t) => t.start + t.minutes * 60000 - Date.now();
  const fmtClock = (ms) => {
    const s = Math.max(0, Math.ceil(ms / 1000));
    const hh = Math.floor(s / 3600);
    const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const ss = String(s % 60).padStart(2, '0');
    return hh ? `${hh}:${mm}:${ss}` : `${mm}:${ss}`;
  };

  function addSession(date, session) {
    Apex.store.update(ID, date, (d) => {
      d.sessions = (d.sessions || []).concat(session);
    }, DEFAULTS);
  }

  function chime() {
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      const ac = new AC();
      const o = ac.createOscillator();
      const g = ac.createGain();
      o.frequency.value = 880;
      g.gain.setValueAtTime(0.15, ac.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 1.2);
      o.connect(g).connect(ac.destination);
      o.start();
      o.stop(ac.currentTime + 1.2);
    } catch (e) { /* audio is optional */ }
  }

  /** If the running timer has finished, log it and clear it. Returns true if it logged. */
  function finalizeIfDone() {
    const c = cfg();
    const t = c.timer;
    if (!t || remainingMs(t) > 0) return false;
    addSession(t.date, { label: t.label || 'Focus block', minutes: t.minutes, quality: null, timer: true });
    c.timer = null;
    Apex.store.setConfig(ID, c);
    Apex.ui.toast(`🎯 Focus block done: ${Apex.ui.fmtMinutes(t.minutes)} logged. Rate its quality.`);
    chime();
    return true;
  }

  /** Stop the timer early and log the minutes elapsed so far. */
  function finishEarly() {
    const c = cfg();
    const t = c.timer;
    if (!t) return;
    const mins = Math.round((Date.now() - t.start) / 60000);
    c.timer = null;
    Apex.store.setConfig(ID, c);
    if (mins >= 1) {
      addSession(t.date, { label: t.label || 'Focus block', minutes: mins, quality: null, timer: true });
      Apex.ui.toast(`Logged ${Apex.ui.fmtMinutes(mins)} of deep work`);
    } else {
      Apex.ui.toast('Under a minute: nothing logged');
    }
  }

  // Background watcher: completes the timer even while the user is on another page.
  // It only writes + toasts; it never re-renders, so it can't disturb other views.
  setInterval(() => {
    if (document.querySelector('.focus-clock')) return; // the visible clock handles it
    try { finalizeIfDone(); } catch (e) { /* ignore */ }
  }, 1000);

  function timerCard(ctx) {
    const c = cfg();
    const t = c.timer;
    if (t) {
      const clock = h('div', { class: 'focus-clock', role: 'timer', 'aria-live': 'off' }, fmtClock(remainingMs(t)));
      const bar = progress(t.minutes * 60000 - remainingMs(t), t.minutes * 60000);
      const fill = bar.firstChild;
      const iv = setInterval(() => {
        if (!clock.isConnected) { clearInterval(iv); return; }
        const cur = cfg().timer;
        if (!cur) { clearInterval(iv); ctx.refresh(); return; } // finished or cancelled elsewhere
        const left = remainingMs(cur);
        clock.textContent = fmtClock(left);
        fill.style.width = Math.min(100, (1 - left / (cur.minutes * 60000)) * 100) + '%';
        if (left <= 0) {
          clearInterval(iv);
          if (finalizeIfDone()) ctx.refresh();
        }
      }, 500);
      const otherDay = t.date !== ctx.date ? h('p', { class: 'muted small' }, `Logging to ${Apex.date.format(t.date)}`) : null;
      return card('Focus timer · running',
        clock,
        h('div', { class: 'focus-clock-label muted' }, `${t.label || 'Focus block'} · ${Apex.ui.fmtMinutes(t.minutes)}`),
        bar, otherDay,
        h('div', { class: 'focus-actions' },
          button('Finish now & log', () => { finishEarly(); ctx.refresh(); }, 'primary'),
          button('Cancel', () => {
            if (!confirm('Cancel this focus block without logging it?')) return;
            const cc = cfg(); cc.timer = null; Apex.store.setConfig(ID, cc); ctx.refresh();
          }, 'ghost')));
    }
    const setup = { label: draft.timerLabel || '' };
    return card('Focus timer',
      h('div', { class: 'focus-presets' }, [25, 50, 90].map((m) =>
        h('button', { type: 'button', class: 'btn small' + (c.timerMinutes === m ? ' btn-primary' : ''),
          onClick: () => { const cc = cfg(); cc.timerMinutes = m; Apex.store.setConfig(ID, cc); ctx.refresh(); } }, `${m} min`))),
      h('div', { class: 'row' },
        text({ label: 'What are you working on?', value: setup.label, placeholder: 'e.g. Write chapter 3',
          onChange: (v) => { draft.timerLabel = v; setup.label = v; } }),
        number({ label: 'Length', value: c.timerMinutes, min: 1, max: 480, step: 1, unit: 'min',
          onChange: (v) => { const cc = cfg(); cc.timerMinutes = v && v > 0 ? Math.round(v) : CFG.timerMinutes; Apex.store.setConfig(ID, cc); ctx.refresh(); } })),
      h('div', { class: 'focus-actions' },
        button('▶ Start focus block', () => {
          const cc = cfg();
          cc.timer = { start: Date.now(), minutes: cc.timerMinutes || CFG.timerMinutes, label: (draft.timerLabel || '').trim(), date: ctx.date };
          Apex.store.setConfig(ID, cc);
          draft.timerLabel = '';
          ctx.refresh();
        }, 'primary')),
      h('p', { class: 'muted small' }, 'Keeps running if you switch pages or close the tab. Phone on another room, one tab, one task.'));
  }

  Apex.registerModule({
    id: ID,
    name: 'Deep Work',
    icon: '🎯',
    category: 'work',
    order: 70,
    weight: 1,
    description: 'Hours of distraction-free focus on hard problems: the output multiplier of elite performers.',

    render(el, ctx) {
      injectStyle();
      finalizeIfDone();
      const c = cfg();
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const mins = minutesOf(d);
      const q = avgQuality(d);
      const s = this.score(ctx.date);

      // Today
      const todayCard = card(ctx.date === ctx.today ? 'Today' : Apex.date.format(ctx.date),
        h('div', { class: 'kpis' },
          stat('Deep work', Apex.ui.fmtMinutes(mins), `goal ${Apex.ui.fmtMinutes(c.goal)}`),
          stat('Sessions', String(d.sessions.length)),
          stat('Avg quality', q == null ? '—' : q.toFixed(1), 'out of 5'),
          stat('Score', s == null ? '—' : String(Math.round(s)))),
        h('div', { style: { marginTop: '12px' } }, progress(mins, c.goal, mins >= c.goal ? 'var(--good)' : '')),
        h('p', { class: 'muted small', style: { marginTop: '6px' } },
          mins >= c.goal ? 'Goal hit. Anything more is a bonus.' : `${Apex.ui.fmtMinutes(c.goal - mins)} to go.`));

      // Distractions
      const distractCard = card('Distractions',
        h('p', { class: 'muted small' }, 'Tap every time you break focus: phone, email, a tab you did not need.'),
        h('div', { class: 'focus-counter' },
          button('−', () => { d.distractions = Math.max(0, (d.distractions || 0) - 1); save(); }, 'ghost'),
          h('strong', null, String(d.distractions || 0)),
          button('+1 distraction', () => { d.distractions = (d.distractions || 0) + 1; save(); })));

      // Sessions list
      const sessionsCard = card('Sessions',
        Apex.ui.list(d.sessions, (se, i) => h('div', { class: 'focus-session' },
          h('div', { class: 'focus-session-head' },
            h('strong', null, se.label || 'Focus block'),
            h('span', { class: 'muted' }, Apex.ui.fmtMinutes(se.minutes) + (se.timer ? ' · ⏱' : ''))),
          rating({ value: se.quality, max: 5, onChange: (v) => { d.sessions[i].quality = v; save(); } }),
          se.quality == null ? h('small', { class: 'muted' }, 'Rate the depth: 1 = shallow, 5 = total flow') : null),
        (i) => { d.sessions.splice(i, 1); save(); }));

      // Manual entry
      const manualCard = card('Log a session manually',
        h('div', { class: 'row' },
          text({ label: 'Label', value: draft.label, placeholder: 'e.g. Code review', onChange: (v) => { draft.label = v; } }),
          number({ label: 'Minutes', value: draft.minutes, min: 1, max: 600, step: 1, unit: 'min', onChange: (v) => { draft.minutes = v; } })),
        rating({ label: 'Quality', value: draft.quality, max: 5, onChange: (v) => { draft.quality = v; ctx.refresh(); } }),
        button('Add session', () => {
          const m = Math.round(Number(draft.minutes) || 0);
          if (m <= 0) { Apex.ui.toast('Enter the minutes first'); return; }
          d.sessions.push({ label: (draft.label || '').trim() || 'Focus block', minutes: m, quality: draft.quality });
          draft.label = ''; draft.minutes = null; draft.quality = null;
          save();
        }, 'primary'));

      // History
      const days = Apex.date.lastN(ctx.date, 14);
      const hist = days.map((k) => {
        if (!Apex.store.has(ID, k)) return null;
        return minutesOf(Apex.store.get(ID, k, DEFAULTS));
      });
      const logged = hist.filter((v) => v != null);
      const avg = logged.length ? Math.round(logged.reduce((a, b) => a + b, 0) / logged.length) : 0;
      const hitDays = logged.filter((v) => v >= c.goal).length;
      const historyCard = card('Last 14 days',
        bars(hist, { max: Math.max(c.goal, ...logged), labels: days.map((k) => Apex.date.format(k, { weekday: 'narrow' })), height: 100,
          color: 'var(--accent)' }),
        h('p', { class: 'muted small', style: { marginTop: '8px' } },
          logged.length ? `Avg ${Apex.ui.fmtMinutes(avg)} on logged days · goal hit ${hitDays}/${logged.length} days` : 'No sessions yet.'));

      // Settings
      const settingsCard = card('Targets',
        h('div', { class: 'row' },
          number({ label: 'Daily deep-work goal', value: c.goal, min: 15, max: 720, step: 15, unit: 'min',
            onChange: (v) => { const cc = cfg(); cc.goal = v && v > 0 ? Math.round(v) : CFG.goal; Apex.store.setConfig(ID, cc); ctx.refresh(); } }),
          number({ label: 'Default block length', value: c.timerMinutes, min: 1, max: 480, step: 1, unit: 'min',
            onChange: (v) => { const cc = cfg(); cc.timerMinutes = v && v > 0 ? Math.round(v) : CFG.timerMinutes; Apex.store.setConfig(ID, cc); ctx.refresh(); } })),
        h('p', { class: 'muted small' }, 'Most people manage about 1 hour of real deep work a day. Four hours is the ceiling most elite researchers and writers report.'));

      el.append(
        h('div', { class: 'grid grid-2' }, timerCard(ctx), todayCard),
        h('div', { class: 'grid grid-2' }, sessionsCard, manualCard),
        h('div', { class: 'grid grid-2' }, distractCard, historyCard),
        settingsCard,
        h('p', { class: 'tip' }, insight(d, c, mins, q)));
    },

    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = Apex.store.get(ID, date, DEFAULTS);
      const mins = minutesOf(d);
      if (!mins && !(d.distractions > 0)) return null;
      const goal = Apex.store.getConfig(ID, CFG).goal || CFG.goal;
      const q = avgQuality(d);
      // Quality 5 = 1.1x, 3 = 0.9x, 1 = 0.7x. Each distraction costs 2 points (max 20).
      const factor = q == null ? 1 : 0.6 + 0.1 * q;
      const base = Math.min(1, mins / goal) * 100 * factor;
      return Math.max(0, Math.min(100, base - Math.min(20, 2 * (d.distractions || 0))));
    },

    summary(date) {
      const running = cfg().timer;
      const d = Apex.store.get(ID, date, DEFAULTS);
      const mins = minutesOf(d);
      const q = avgQuality(d);
      const parts = [];
      if (running && remainingMs(running) > 0) parts.push(`⏱ ${fmtClock(remainingMs(running))} left`);
      if (Apex.store.has(ID, date) && (mins || d.distractions)) {
        parts.push(`${Apex.ui.fmtMinutes(mins)} / ${Apex.ui.fmtMinutes(cfg().goal)}`);
        parts.push(`${d.sessions.length} session${d.sessions.length === 1 ? '' : 's'}`);
        if (q != null) parts.push(`q ${q.toFixed(1)}`);
        if (d.distractions) parts.push(`${d.distractions} distraction${d.distractions === 1 ? '' : 's'}`);
      }
      return parts.join(' · ');
    },
  });

  function insight(d, c, mins, q) {
    if (!d.sessions.length) return 'Schedule your first deep block for the morning, before email. Top performers protect 2 to 4 hours of focus before the world gets a vote.';
    if ((d.distractions || 0) >= 5) return 'Many distractions today. Next block: phone in another room, notifications off, one tab. Every switch costs about 20 minutes of warm-up.';
    if (q != null && q < 3) return 'Shallow sessions do not compound. Try fewer, longer blocks (90 min) with one clearly defined outcome written down first.';
    if (mins >= c.goal) return 'Goal hit. The top 1% stop at the edge of fatigue, so quality stays high tomorrow. Write down where to start the next block.';
    return 'Batch shallow work (email, chat) into two fixed windows so it cannot fragment your deep blocks.';
  }
})();
