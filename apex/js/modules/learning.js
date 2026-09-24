/* Apex module: Learning — reading, books in progress, skill practice, daily lesson. */
(function () {
  const { h, card, stat } = Apex.ui;
  const ID = 'learning';
  const DEFAULTS = { readMin: null, pages: null, sessions: [], note: '' };
  const CONFIG = { readGoal: 30, skillGoal: 15, booksGoal: 20, books: [], skills: [] };
  const TIPS = [
    'Warren Buffett reads ~500 pages a day. You don\'t need that, but 30 minutes daily is 20+ books a year.',
    'Deliberate practice beats mileage: work at the edge of your ability, get fast feedback, repeat.',
    'Write down one thing you learned every day. Retrieval, not re-reading, is what makes knowledge stick.',
    'Finish or quit. Top learners abandon a weak book after 50 pages without guilt, and move on.',
    'Teach it to learn it: explain today\'s lesson in two sentences as if to a 12-year-old (the Feynman technique).',
    'Stack learning onto dead time: audiobooks on commutes, flashcards in queues.',
  ];

  injectStyle();

  const cfg = () => {
    const c = Apex.store.getConfig(ID, CONFIG);
    if (!Array.isArray(c.books)) c.books = [];
    if (!Array.isArray(c.skills)) c.skills = [];
    return c;
  };
  const num = (v, dflt) => (typeof v === 'number' && v > 0 ? v : dflt);
  const dailyGoal = (c) => num(c.readGoal, 30) + num(c.skillGoal, 15);

  function load(date) {
    const d = Apex.store.get(ID, date, DEFAULTS);
    if (!Array.isArray(d.sessions)) d.sessions = [];
    return d;
  }
  const filled = (s) => typeof s === 'string' && s.trim().length > 0;
  const skillMin = (d) => d.sessions.reduce((a, s) => a + (Number(s.minutes) || 0), 0);
  const totalMin = (d) => (d.readMin || 0) + skillMin(d);
  const isLogged = (d) => (d.readMin || 0) > 0 || (d.pages || 0) > 0 || d.sessions.length > 0 || filled(d.note);

  function tipFor(date) {
    return TIPS[Math.abs(Apex.date.diff(date, '2024-01-01')) % TIPS.length];
  }

  const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

  Apex.registerModule({
    id: ID,
    name: 'Learning',
    icon: '📚',
    category: 'mind',
    order: 50,
    weight: 1,
    description: 'Reading and deliberate skill practice compound faster than anything else you can do with an hour.',

    render(el, ctx) {
      const c = cfg();
      const goal = dailyGoal(c);
      const d = load(ctx.date);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const saveCfg = () => { Apex.store.setConfig(ID, c); ctx.refresh(); };
      const total = totalMin(d);
      const readGoal = num(c.readGoal, 30);
      const year = ctx.date.slice(0, 4);

      // --- Today
      const today = card('Today',
        h('div', { class: 'row' },
          Apex.ui.number({ label: 'Reading', value: d.readMin, min: 0, step: 1, unit: 'min', onChange: (v) => { d.readMin = v == null ? null : Math.max(0, v); save(); } }),
          Apex.ui.number({ label: 'Pages', value: d.pages, min: 0, step: 1, unit: 'pp', onChange: (v) => { d.pages = v == null ? null : Math.max(0, v); save(); } })),
        h('div', { class: 'learning-line' }, h('span', { class: 'small' }, 'Reading'),
          Apex.ui.progress(d.readMin || 0, readGoal, (d.readMin || 0) >= readGoal ? 'var(--good)' : ''),
          h('span', { class: 'small muted learning-num' }, `${d.readMin || 0}/${readGoal}m`)),
        h('div', { class: 'learning-line' }, h('span', { class: 'small' }, 'Total'),
          Apex.ui.progress(total, goal, total >= goal ? 'var(--good)' : ''),
          h('span', { class: 'small muted learning-num' }, `${total}/${goal}m`)),
        Apex.ui.textarea({ label: '💡 One thing I learned today', value: d.note, rows: 3, placeholder: 'Write it in your own words…',
          onChange: (v) => { d.note = v; save(); } }));

      // --- Skill practice
      let pickSkill = c.skills[0] || '';
      let pickMin = null;
      const practice = card(`Skill practice · ${Apex.ui.fmtMinutes(skillMin(d))}`,
        c.skills.length
          ? h('div', { class: 'learning-add' },
            Apex.ui.select({ label: 'Skill', value: pickSkill, options: c.skills, onChange: (v) => { pickSkill = v; } }),
            Apex.ui.number({ label: 'Minutes', value: null, min: 1, step: 1, onChange: (v) => { pickMin = v; } }),
            Apex.ui.button('Log', () => {
              if (!pickSkill || !(pickMin > 0)) { Apex.ui.toast('Pick a skill and minutes'); return; }
              d.sessions.push({ skill: pickSkill, minutes: pickMin });
              save();
            }, 'primary'))
          : h('p', { class: 'muted small' }, 'Add the skills you\'re building in Targets below (e.g. Spanish, Piano, Coding).'),
        Apex.ui.list(d.sessions, (s) => h('span', null, h('strong', null, s.skill), ' · ', Apex.ui.fmtMinutes(Number(s.minutes) || 0)),
          (i) => { d.sessions.splice(i, 1); save(); }));

      // --- Books
      const reading = c.books.filter((b) => !b.finished);
      const finishedYear = c.books.filter((b) => b.finished && String(b.finished).startsWith(year));
      const booksGoal = num(c.booksGoal, 20);
      const dayOfYear = Apex.date.diff(ctx.date, `${year}-01-01`) + 1;
      const pace = (booksGoal * dayOfYear) / 365;
      const books = card('Currently reading',
        reading.length ? h('div', { class: 'learning-books' }, reading.map((b) => {
          const tot = num(b.total, 0);
          const cur = Math.max(0, Number(b.current) || 0);
          return h('div', { class: 'learning-book' },
            h('div', { class: 'learning-book-head' },
              h('strong', { class: 'learning-title' }, b.title),
              h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Remove book', onClick: () => {
                c.books = c.books.filter((x) => x.id !== b.id); saveCfg();
              } }, '✕')),
            h('div', { class: 'learning-line' },
              Apex.ui.progress(cur, tot || 1),
              h('span', { class: 'small muted learning-num' }, tot ? `${Math.round(Math.min(100, (cur / tot) * 100))}%` : '—')),
            h('div', { class: 'row learning-book-row' },
              Apex.ui.number({ label: 'Page', value: cur, min: 0, step: 1, unit: tot ? `/ ${tot}` : '',
                onChange: (v) => { b.current = v == null ? 0 : Math.max(0, v); if (tot && b.current >= tot) b.current = tot; saveCfg(); } }),
              Apex.ui.button('✓ Finished', () => { b.finished = ctx.date; b.current = tot || b.current; saveCfg(); Apex.ui.toast(`Finished "${b.title}" 🎉`); })));
        })) : h('p', { class: 'muted small' }, 'No books in progress.'),
        bookAdder(c, saveCfg));

      const yearCard = card(`Books in ${year}`,
        h('div', { class: 'kpis' },
          stat('Finished', `${finishedYear.length}/${booksGoal}`, finishedYear.length >= Math.floor(pace) ? 'on pace ✓' : `pace: ${Math.floor(pace)} by now`),
          stat('In progress', String(reading.length), 'books')),
        h('div', { class: 'learning-line learning-gap' },
          Apex.ui.progress(finishedYear.length, booksGoal, finishedYear.length >= booksGoal ? 'var(--good)' : '#a855f7'),
          h('span', { class: 'small muted learning-num' }, `${Math.round(Math.min(100, (finishedYear.length / booksGoal) * 100))}%`)),
        finishedYear.length
          ? h('ul', { class: 'learning-done small' }, finishedYear.map((b) => h('li', null, '✓ ', b.title, h('span', { class: 'muted' }, ` · ${Apex.date.format(b.finished, { month: 'short', day: 'numeric' })}`))))
          : null);

      // --- History
      const days = Apex.store.range(ID, ctx.date, 14);
      const mins = days.map((x) => (x.data ? totalMin(load(x.date)) : null));
      const logged = mins.filter((v) => v != null);
      const hitDays = mins.filter((v) => v != null && v >= goal).length;
      const history = card('Last 14 days',
        Apex.ui.bars(mins, { max: Math.max(goal, ...logged, 1), color: '#a855f7', height: 80,
          labels: days.map((x) => Apex.date.format(x.date, { weekday: 'narrow' })) }),
        h('div', { class: 'kpis learning-gap' },
          stat('Total', Apex.ui.fmtMinutes(logged.reduce((a, b) => a + b, 0)), '14 days'),
          stat('Goal hit', `${hitDays}/14`, `≥ ${goal}m`),
          stat('Pages', String(days.reduce((a, x) => a + ((x.data && x.data.pages) || 0), 0)), '14 days')));

      // --- Settings
      const setNum = (k, dflt) => (v) => { c[k] = v && v > 0 ? v : dflt; saveCfg(); };
      const settings = card('Targets',
        h('div', { class: 'row' },
          Apex.ui.number({ label: 'Reading / day', value: readGoal, min: 1, step: 1, unit: 'min', onChange: setNum('readGoal', 30) }),
          Apex.ui.number({ label: 'Skill practice / day', value: num(c.skillGoal, 15), min: 1, step: 1, unit: 'min', onChange: setNum('skillGoal', 15) }),
          Apex.ui.number({ label: 'Books / year', value: booksGoal, min: 1, step: 1, onChange: setNum('booksGoal', 20) })),
        h('div', { class: 'small muted' }, 'Skills'),
        Apex.ui.list(c.skills, (s) => s, (i) => { c.skills.splice(i, 1); saveCfg(); }),
        Apex.ui.adder('Add a skill (e.g. Spanish)', (v) => { if (!c.skills.includes(v)) c.skills.push(v); saveCfg(); }));

      el.append(
        h('div', { class: 'grid grid-2' }, today, practice),
        h('div', { class: 'grid grid-2' }, books, yearCard),
        history,
        h('div', { class: 'grid grid-2' }, settings, card('Top 1% insight', h('p', { class: 'tip' }, tipFor(ctx.date)))));
    },

    /** 80 pts for total learning minutes vs daily goal, 20 for writing down what you learned. */
    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = load(date);
      if (!isLogged(d)) return null;
      const s = Math.min(1, totalMin(d) / dailyGoal(cfg())) * 80 + (filled(d.note) ? 20 : 0);
      return Math.round(s);
    },

    summary(date) {
      if (!Apex.store.has(ID, date)) return '';
      const d = load(date);
      if (!isLogged(d)) return '';
      const parts = [`${Apex.ui.fmtMinutes(totalMin(d))}/${dailyGoal(cfg())}m learning`];
      if (d.pages) parts.push(`${d.pages} pages`);
      if (d.sessions.length) parts.push(`${d.sessions.length} practice`);
      if (filled(d.note)) parts.push('lesson noted');
      return parts.join(' · ');
    },
  });

  function bookAdder(c, saveCfg) {
    const title = h('input', { type: 'text', placeholder: 'Book title', 'aria-label': 'Book title' });
    const pages = h('input', { type: 'text', inputmode: 'numeric', placeholder: 'Pages', 'aria-label': 'Total pages', class: 'learning-pages' });
    return h('form', { class: 'adder learning-adder', onSubmit: (e) => {
      e.preventDefault();
      const t = title.value.trim();
      if (!t) return;
      const p = parseInt(pages.value, 10);
      c.books.push({ id: uid(), title: t, total: p > 0 ? p : null, current: 0, finished: null });
      saveCfg();
    } }, title, pages, h('button', { type: 'submit', class: 'btn' }, 'Add'));
  }

  function injectStyle() {
    if (document.getElementById('apex-style-' + ID)) return;
    const css = `
      .learning-line { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
      .learning-line > .small:first-child { width: 58px; flex: none; }
      .learning-num { white-space: nowrap; font-variant-numeric: tabular-nums; min-width: 52px; text-align: right; }
      .learning-gap { margin-top: 12px; }
      .learning-add { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; }
      .learning-add > .field { flex: 1 1 120px; }
      .learning-add > .btn { margin-bottom: 10px; }
      .learning-books { display: flex; flex-direction: column; gap: 12px; }
      .learning-book { background: var(--surface-2); border-radius: var(--radius-sm); padding: 10px 12px; }
      .learning-book-head { display: flex; align-items: center; gap: 8px; }
      .learning-title { flex: 1; min-width: 0; overflow-wrap: anywhere; }
      .learning-book .progress { background: var(--border); }
      .learning-book-row { margin-top: 6px; }
      .learning-book-row > .btn { margin-bottom: 10px; }
      .learning-book input { background: var(--surface); }
      .learning-adder input { flex: 1; }
      .learning-adder .learning-pages { flex: 0 0 76px; }
      .learning-done { list-style: none; padding: 0; margin: 12px 0 0; display: flex; flex-direction: column; gap: 4px; overflow-wrap: anywhere; }
    `;
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, css));
  }
})();
