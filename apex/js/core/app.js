/* Apex core: app shell. Handles routing, the header and date picker, nav,
 * the dashboard (which combines every module), and settings.
 * Loaded last, after every module has registered.
 */
(function () {
  const Apex = window.Apex;
  const { h, card, ring, bars, button, toggle, number } = Apex.ui;

  const state = { date: Apex.date.today() };

  const $ = (sel) => document.querySelector(sel);

  function route() {
    const hash = location.hash || '#/';
    const m = hash.match(/^#\/m\/([\w-]+)/);
    if (m) return { name: 'module', id: m[1] };
    if (hash.startsWith('#/settings')) return { name: 'settings' };
    if (hash.startsWith('#/library')) return { name: 'library' };
    return { name: 'dashboard' };
  }

  function ctx() {
    return {
      date: state.date,
      today: Apex.date.today(),
      refresh: () => render(),
      go: (hash) => { location.hash = hash; },
    };
  }

  // ---------- header ----------
  function renderHeader() {
    const today = Apex.date.today();
    const { score } = Apex.lifeScore(state.date);
    const tier = Apex.tier(score);
    const label = state.date === today ? 'Today' : Apex.date.format(state.date);
    const header = $('#header');
    header.replaceChildren(
      h('button', { class: 'icon-btn menu-btn', 'aria-label': 'Open menu', onClick: () => document.body.classList.toggle('nav-open') }, '☰'),
      h('div', { class: 'date-nav' },
        h('button', { class: 'icon-btn', 'aria-label': 'Previous day', onClick: () => shiftDate(-1) }, '‹'),
        h('label', { class: 'date-label' }, h('span', null, label),
          h('input', { type: 'date', value: state.date, max: today, 'aria-label': 'Pick date',
            onChange: (e) => { if (e.target.value) { state.date = e.target.value; render(); } } })),
        h('button', { class: 'icon-btn', 'aria-label': 'Next day', disabled: state.date >= today ? true : null, onClick: () => shiftDate(1) }, '›'),
        state.date !== today ? h('button', { class: 'btn btn-ghost small', onClick: () => { state.date = today; render(); } }, 'Today') : null),
      h('a', { class: 'header-score', href: '#/', title: 'Life Score' },
        h('span', { class: 'header-score-num' }, String(score)),
        h('span', { class: 'tag', style: { background: tier.color } }, tier.label)));
  }

  function shiftDate(n) {
    const next = Apex.date.add(state.date, n);
    if (next > Apex.date.today()) return;
    state.date = next;
    render();
  }

  // ---------- nav ----------
  function renderNav(r) {
    const byCat = {};
    Apex.modules.enabled().forEach((m) => (byCat[m.category] = byCat[m.category] || []).push(m));
    const lifeScore = Apex.lifeScore(state.date);
    const link = (href, icon, text, active, score) =>
      h('a', { href, class: 'nav-link' + (active ? ' active' : ''), onClick: () => document.body.classList.remove('nav-open') },
        h('span', { class: 'nav-icon', 'aria-hidden': 'true' }, icon), h('span', { class: 'nav-text' }, text),
        score != null ? h('span', { class: 'nav-score' }, String(score)) : null);
    $('#nav').replaceChildren(
      h('div', { class: 'brand' }, h('span', { class: 'brand-mark' }, '▲'), h('span', null, 'Apex'), h('small', null, 'Top 1% Life OS')),
      link('#/', '🏆', 'Dashboard', r.name === 'dashboard'),
      ...Object.keys(Apex.CATEGORIES).filter((c) => byCat[c]).map((c) => h('div', { class: 'nav-group' },
        h('div', { class: 'nav-group-title' }, Apex.CATEGORIES[c].name),
        byCat[c].map((m) => link('#/m/' + m.id, m.icon, m.name, r.name === 'module' && r.id === m.id, lifeScore.byModule[m.id])))),
      h('div', { class: 'nav-group' },
        link('#/library', '📖', 'Library', r.name === 'library'),
        link('#/settings', '⚙️', 'Settings', r.name === 'settings')));
  }

  // ---------- dashboard ----------
  function renderDashboard(el) {
    const date = state.date;
    const ls = Apex.lifeScore(date);
    const tier = Apex.tier(ls.score);
    const days = Apex.date.lastN(date, 14);
    const history = days.map((d) => Apex.lifeScore(d).score);
    const week = history.slice(-7);
    const weekAvg = Math.round(week.reduce((a, b) => a + b, 0) / week.length);
    const streak = Apex.streak(date, 70);
    const mods = Apex.modules.enabled();

    if (!mods.length) {
      el.append(card('No trackers enabled', h('p', null, 'Turn some on in ', h('a', { href: '#/settings' }, 'Settings'), '.')));
      return;
    }

    const weakest = mods
      .map((m) => ({ m, s: ls.byModule[m.id] }))
      .sort((a, b) => (a.s == null ? -1 : a.s) - (b.s == null ? -1 : b.s))
      .slice(0, 3);

    el.append(
      h('div', { class: 'hero card' },
        ring(ls.score, { size: 168, color: tier.color, label: 'Life Score' }),
        h('div', { class: 'hero-body' },
          h('div', { class: 'tag big', style: { background: tier.color } }, tier.label),
          h('h2', null, date === Apex.date.today() ? 'Today' : Apex.date.format(date, { weekday: 'long', month: 'long', day: 'numeric' })),
          h('p', { class: 'muted' }, `${ls.tracked} of ${ls.total} areas logged. Areas you skip count as 0, so log everything.`),
          h('div', { class: 'kpis' },
            Apex.ui.stat('7-day avg', String(weekAvg), Apex.tier(weekAvg).label),
            Apex.ui.stat('Streak ≥70', `${streak}d`, streak ? '🔥 keep it alive' : 'start today'),
            Apex.ui.stat('Best (14d)', String(Math.max(...history)))))),

      h('div', { class: 'grid grid-2' },
        card('Life Score · last 14 days', bars(history, { max: 100, labels: days.map((d) => Apex.date.format(d, { weekday: 'narrow' })), height: 110 })),
        card('Balance by area',
          h('div', { class: 'cat-list' }, Object.entries(Apex.CATEGORIES).filter(([k]) => ls.byCategory[k] != null).map(([k, c]) =>
            h('div', { class: 'cat-row' },
              h('span', { class: 'cat-name' }, `${c.icon} ${c.name}`),
              Apex.ui.progress(ls.byCategory[k], 100, c.color),
              h('strong', null, String(ls.byCategory[k]))))))),

      principleCard('Principle of the day', Apex.knowledge.daily(date, weakest.map((w) => w.m.id))),

      card('Focus next: your weakest areas',
        h('div', { class: 'focus-list' }, weakest.map(({ m, s }) =>
          h('a', { class: 'focus-item', href: '#/m/' + m.id },
            h('span', { class: 'nav-icon' }, m.icon),
            h('span', null, h('strong', null, m.name), h('small', { class: 'muted' }, s == null ? 'Not logged yet' : `Score ${s}`)),
            h('span', { class: 'chev' }, '→'))))),

      h('div', { class: 'tiles' }, mods.map((m) => {
        const s = ls.byModule[m.id];
        const cat = Apex.CATEGORIES[m.category];
        const hist = Apex.date.lastN(date, 7).map((d) => Apex.moduleScore(m, d));
        return h('a', { class: 'tile', href: '#/m/' + m.id, style: { '--tile-color': cat.color } },
          h('div', { class: 'tile-head' }, h('span', { class: 'tile-icon' }, m.icon), h('span', { class: 'tile-name' }, m.name),
            h('span', { class: 'tile-score' + (s == null ? ' muted' : '') }, s == null ? '—' : String(s))),
          Apex.ui.progress(s || 0, 100, cat.color),
          h('div', { class: 'tile-summary muted small' }, Apex.moduleSummary(m, date) || m.description),
          bars(hist, { max: 100, color: cat.color, height: 28 }));
      })));
  }

  // ---------- library ----------
  function principleCard(title, p) {
    if (!p) return null;
    return h('section', { class: 'card principle' },
      h('div', { class: 'principle-kicker' }, title),
      h('p', { class: 'principle-text' }, p.text),
      h('p', { class: 'principle-action' }, h('strong', null, 'Do today: '), p.action),
      h('div', { class: 'muted small' }, `📖 ${p.title} · ${p.author}`));
  }

  let libraryQuery = '';
  function renderLibrary(el) {
    const results = h('div', { class: 'library-list' });
    const draw = () => {
      const list = libraryQuery ? Apex.knowledge.search(libraryQuery) : Apex.knowledge.principles;
      results.replaceChildren(...(list.length ? list.map((p) => h('article', { class: 'card library-item' },
        h('p', { class: 'principle-text' }, p.text),
        h('p', { class: 'principle-action' }, h('strong', null, 'Do today: '), p.action),
        h('div', { class: 'row library-meta' },
          h('span', { class: 'muted small' }, `📖 ${p.title} · ${p.author}`),
          h('span', { class: 'spacer' }),
          p.modules.map((id) => {
            const m = Apex.modules.get(id);
            return m ? h('a', { class: 'pill small', href: '#/m/' + id }, `${m.icon} ${m.name}`) : null;
          })))) : [Apex.ui.empty('No principles match that search.')]));
    };
    const search = h('input', { type: 'search', placeholder: 'Search sleep, money, focus, Atomic Habits…', value: libraryQuery, 'aria-label': 'Search the library',
      onInput: (e) => { libraryQuery = e.target.value; draw(); } });
    el.append(
      h('h2', null, '📖 Library'),
      h('p', { class: 'muted' }, `${Apex.knowledge.principles.length} principles from ${Object.keys(Apex.knowledge.books).length} books, summarised and linked to your trackers.`),
      h('div', { class: 'field' }, search),
      results);
    draw();
  }

  // ---------- settings ----------
  function renderSettings(el) {
    const cfg = Apex.store.getConfig('_app', { disabled: [], weights: {} });
    const save = () => { Apex.store.setConfig('_app', cfg); render(); };

    el.append(
      h('h2', null, 'Settings'),
      card('Trackers & weights',
        h('p', { class: 'muted small' }, 'Turn areas on or off and choose how much each one counts toward your Life Score.'),
        h('div', { class: 'settings-list' }, Apex.modules.all().map((m) => h('div', { class: 'settings-row' },
          toggle({ label: `${m.icon} ${m.name}`, hint: m.description, checked: !cfg.disabled.includes(m.id),
            onChange: (on) => {
              cfg.disabled = on ? cfg.disabled.filter((x) => x !== m.id) : cfg.disabled.concat(m.id);
              save();
            } }),
          number({ label: 'Weight', value: Apex.modules.weight(m), min: 0, max: 5, step: 0.5,
            onChange: (v) => { cfg.weights[m.id] = v == null ? m.weight : v; save(); } }))))),
      card('Backup',
        h('p', { class: 'muted small' }, 'All data lives only on this device. Export a backup regularly.'),
        h('div', { class: 'row' },
          button('Export JSON', exportData, 'primary'),
          h('label', { class: 'btn' }, 'Import JSON', h('input', { type: 'file', accept: 'application/json', hidden: true, onChange: importData })),
          button('Erase everything', () => {
            if (confirm('Erase all Apex data on this device? This cannot be undone.')) { Apex.store.clearAll(); Apex.ui.toast('All data erased'); render(); }
          }, 'danger'))));
  }

  function exportData() {
    const blob = new Blob([JSON.stringify(Apex.store.exportAll(), null, 2)], { type: 'application/json' });
    const a = h('a', { href: URL.createObjectURL(blob), download: `apex-backup-${Apex.date.today()}.json` });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  function importData(e) {
    const file = e.target.files[0];
    if (!file) return;
    file.text().then((txt) => {
      try {
        Apex.store.importAll(JSON.parse(txt));
        Apex.ui.toast('Backup restored');
        render();
      } catch (err) {
        Apex.ui.toast('Import failed: ' + err.message);
      }
    });
  }

  // ---------- main render ----------
  // Removing a focused input fires blur/change, which can call refresh() mid-render.
  // Queue those instead of nesting renders.
  let rendering = false;
  let pending = false;
  function render() {
    if (rendering) { pending = true; return; }
    rendering = true;
    try {
      renderNow();
    } finally {
      rendering = false;
    }
    if (pending) { pending = false; render(); }
  }

  function renderNow() {
    const r = route();
    const main = $('#main');
    const scrollY = window.scrollY;
    const sameView = main.dataset.view === JSON.stringify(r) && main.dataset.date === state.date;
    main.replaceChildren();
    main.dataset.view = JSON.stringify(r);
    main.dataset.date = state.date;

    renderHeader();
    renderNav(r);

    if (r.name === 'module') {
      const m = Apex.modules.get(r.id);
      if (!m) {
        main.append(card('Not found', h('p', null, 'That tracker does not exist. ', h('a', { href: '#/' }, 'Back to dashboard'))));
      } else {
        const cat = Apex.CATEGORIES[m.category];
        const s = Apex.moduleScore(m, state.date);
        main.append(h('div', { class: 'module-head' },
          h('span', { class: 'module-icon', style: { background: cat.color } }, m.icon),
          h('div', null, h('h2', null, m.name), h('p', { class: 'muted small' }, m.description)),
          ring(s || 0, { size: 72, color: cat.color, label: s == null ? 'no data' : 'score' })));
        const body = h('div', { class: 'module-body module-' + m.id });
        main.append(body);
        try {
          m.render(body, ctx());
        } catch (err) {
          console.error(`[apex] ${m.id}.render failed`, err);
          body.append(card('Something broke', h('p', { class: 'muted' }, String(err.message || err))));
        }
        const related = Apex.knowledge.forModule(m.id);
        if (related.length) main.append(principleCard('From the library', Apex.knowledge.daily(state.date, [m.id])));
      }
    } else if (r.name === 'settings') {
      renderSettings(main);
    } else if (r.name === 'library') {
      renderLibrary(main);
    } else {
      renderDashboard(main);
    }
    document.title = (r.name === 'module' && Apex.modules.get(r.id) ? Apex.modules.get(r.id).name + ' · ' : '') + 'Apex';
    if (sameView) window.scrollTo(0, scrollY);
    else window.scrollTo(0, 0);
  }

  // Background saves (e.g. the focus timer finishing on another page) only need the
  // header and nav refreshed; re-rendering main would wipe whatever the user is typing.
  let chromeTimer = null;
  Apex.store.onChange(() => {
    clearTimeout(chromeTimer);
    chromeTimer = setTimeout(() => {
      if (rendering) return;
      renderHeader();
      renderNav(route());
    }, 50);
  });

  Apex.render = render;
  Apex.state = state;

  window.addEventListener('hashchange', render);
  document.addEventListener('DOMContentLoaded', () => {
    render();
    if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
      navigator.serviceWorker.register('sw.js').catch(() => {});
    }
  });
})();
