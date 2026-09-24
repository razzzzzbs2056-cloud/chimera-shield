/* Apex module: Relationships. Meaningful interactions, people who matter, kindness. */
(function () {
  const { h, card, row, stat, number, select, rating, toggle, button, progress, bars, list, adder } = Apex.ui;
  const ID = 'social';
  const DEFAULTS = { interactions: [], helped: false, compliment: false };
  const CONFIG = { target: 2, people: [] };
  const TYPES = [
    { value: 'in-person', label: 'In person' },
    { value: 'call', label: 'Call' },
    { value: 'message', label: 'Message' },
    { value: 'date', label: 'Date' },
    { value: 'family', label: 'Family time' },
  ];
  const typeLabel = (v) => (TYPES.find((t) => t.value === v) || { label: v }).label;
  const LOOKBACK = 90;

  const draft = { person: '', type: 'in-person', minutes: null, quality: null };

  if (!document.getElementById('apex-style-' + ID)) {
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.social-ix { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; }
.social-ix strong { overflow-wrap: anywhere; }
.social-person { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.social-person-name { flex: 1 1 120px; min-width: 0; overflow-wrap: anywhere; }
.social-person .field { width: 110px; flex: none; margin: 0; }
.social-overdue { display: flex; flex-direction: column; gap: 8px; }
.social-overdue-item { display: flex; justify-content: space-between; gap: 8px; padding: 8px 12px; border-radius: var(--radius-sm); background: var(--surface-2); flex-wrap: wrap; }
.social-overdue-item.social-late { box-shadow: inset 3px 0 0 var(--bad); }
.social-overdue-item.social-ok { box-shadow: inset 3px 0 0 var(--good); }
.social-person-input { width: 100%; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const norm = (s) => String(s || '').trim().toLowerCase();

  function isLogged(d) {
    return !!d && (((d.interactions || []).length > 0) || !!d.helped || !!d.compliment);
  }

  /** Days since last contact with each person (scanning back LOOKBACK days), null if none. */
  function lastContacts(date) {
    const out = {};
    const days = Apex.store.range(ID, date, LOOKBACK);
    for (let i = days.length - 1; i >= 0; i--) {
      const { date: dk, data } = days[i];
      if (!data || !data.interactions) continue;
      data.interactions.forEach((x) => {
        const k = norm(x.person);
        if (k && !(k in out)) out[k] = Apex.date.diff(date, dk);
      });
    }
    return out;
  }

  Apex.registerModule({
    id: ID,
    name: 'Relationships',
    icon: '🤝',
    category: 'life',
    order: 110,
    weight: 1,
    description: 'The strongest predictor of a long, happy life is the quality of your relationships. Invest in them daily.',

    render(el, ctx) {
      const c = cfg();
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const saveCfg = () => { Apex.store.setConfig(ID, c); ctx.refresh(); };
      const ix = d.interactions || [];
      const target = Math.max(1, Number(c.target) || 1);
      const mins = ix.reduce((a, x) => a + (Number(x.minutes) || 0), 0);
      const rated = ix.filter((x) => x.quality);
      const avgQ = rated.length ? rated.reduce((a, x) => a + x.quality, 0) / rated.length : null;

      // ---- today ----
      const dlId = 'social-people-list';
      const personInput = h('input', {
        type: 'text', class: 'social-person-input', list: dlId, value: draft.person, placeholder: 'Who?',
        onChange: (e) => { draft.person = e.target.value; },
      });
      const add = () => {
        draft.person = personInput.value;
        const p = (draft.person || '').trim();
        if (!p) { Apex.ui.toast('Who did you connect with?'); return; }
        d.interactions = ix.concat({ person: p, type: draft.type, minutes: draft.minutes, quality: draft.quality });
        draft.person = '';
        draft.minutes = null;
        draft.quality = null;
        save();
      };

      el.append(card('Today',
        h('div', { class: 'kpis' },
          stat('Interactions', `${ix.length}/${target}`),
          stat('Time together', Apex.ui.fmtMinutes(mins)),
          stat('Avg quality', avgQ == null ? '—' : avgQ.toFixed(1) + '/5')),
        h('div', { style: { margin: '12px 0' } }, progress(ix.length, target, 'var(--good)')),
        toggle({ label: 'Helped someone', hint: 'A favour, an intro, advice, your time.', checked: !!d.helped,
          onChange: (v) => { d.helped = v; save(); } }),
        toggle({ label: 'Gave a genuine compliment', hint: 'Specific and sincere.', checked: !!d.compliment,
          onChange: (v) => { d.compliment = v; save(); } })));

      el.append(card('Log an interaction',
        h('label', { class: 'field' }, h('span', null, 'Person'), personInput,
          h('datalist', { id: dlId }, (c.people || []).map((p) => h('option', { value: p.name })))),
        row(
          select({ label: 'Type', value: draft.type, options: TYPES, onChange: (v) => { draft.type = v; } }),
          number({ label: 'Minutes', value: draft.minutes, min: 0, step: 5, onChange: (v) => { draft.minutes = v; } })),
        rating({ label: 'Quality (how present and meaningful?)', value: draft.quality, max: 5,
          onChange: (v) => { draft.person = personInput.value; draft.quality = v; ctx.refresh(); } }),
        button('Add interaction', add, 'primary'),
        h('div', { style: { marginTop: '12px' } },
          list(ix, (x) => h('div', { class: 'social-ix' },
            h('strong', null, x.person),
            h('span', { class: 'tag' }, typeLabel(x.type)),
            x.minutes ? h('span', { class: 'muted small' }, Apex.ui.fmtMinutes(x.minutes)) : null,
            x.quality ? h('span', { class: 'muted small' }, '★'.repeat(x.quality)) : null),
          (i) => { d.interactions.splice(i, 1); save(); }))));

      // ---- people who matter ----
      const last = lastContacts(ctx.date);
      const people = (c.people || []).map((p) => {
        const since = norm(p.name) in last ? last[norm(p.name)] : null;
        const every = Math.max(1, Number(p.every) || 7);
        return { p, since, every, overdue: since == null || since > every };
      }).sort((a, b) => (b.overdue - a.overdue) || ((b.since == null ? 999 : b.since - b.every) - (a.since == null ? 999 : a.since - a.every)));
      const overdueN = people.filter((x) => x.overdue).length;
      el.append(card('People who matter',
        people.length
          ? h('div', null,
            h('p', { class: 'muted small' }, overdueN ? `You're overdue to reach out to ${overdueN} ${overdueN === 1 ? 'person' : 'people'}.` : 'You are in touch with everyone on your list. 👏'),
            h('div', { class: 'social-overdue' }, people.map(({ p, since, every, overdue }) =>
              h('div', { class: 'social-overdue-item ' + (overdue ? 'social-late' : 'social-ok') },
                h('strong', { class: 'social-person-name' }, p.name),
                h('span', { class: 'small ' + (overdue ? '' : 'muted') },
                  since == null ? `no contact in ${LOOKBACK}d · every ${every}d`
                    : since === 0 ? 'today'
                      : `${since}d ago · every ${every}d` + (overdue ? ` · ${since - every}d overdue` : ''))))))
          : h('p', { class: 'muted small' }, 'Add the people you want to stay close to in the settings below.')));

      // ---- history ----
      const days = Apex.date.lastN(ctx.date, 14);
      const hist = Apex.store.range(ID, ctx.date, 14).map(({ data }) => (isLogged(data) ? (data.interactions || []).length : null));
      const kind = Apex.store.range(ID, ctx.date, 14).filter(({ data }) => data && (data.helped || data.compliment)).length;
      el.append(card('Interactions · last 14 days',
        bars(hist, { labels: days.map((x) => Apex.date.format(x, { weekday: 'narrow' })), height: 80, color: '#f43f5e' }),
        h('p', { class: 'muted small', style: { marginTop: '8px' } }, `Acts of kindness on ${kind} of the last 14 days.`)));

      // ---- settings ----
      el.append(card('Settings',
        number({ label: 'Daily target (meaningful interactions)', value: c.target, min: 1, max: 20, step: 1,
          onChange: (v) => { c.target = v == null ? 2 : v; saveCfg(); } }),
        h('h4', { class: 'small muted', style: { margin: '8px 0' } }, 'People who matter · contact every N days'),
        list(c.people || [], (p, i) => h('div', { class: 'social-person' },
          h('span', { class: 'social-person-name' }, p.name),
          number({ label: 'Every', value: p.every, min: 1, step: 1, unit: 'd',
            onChange: (v) => { c.people[i].every = v == null ? 7 : v; saveCfg(); } })),
          (i) => { c.people.splice(i, 1); saveCfg(); }),
        adder('Add a person (e.g. Mom)', (name) => {
          c.people = c.people || [];
          if (c.people.some((p) => norm(p.name) === norm(name))) { Apex.ui.toast('Already on your list'); return; }
          c.people.push({ name, every: 7 });
          saveCfg();
        })));

      el.append(h('p', { class: 'tip' },
        'The Harvard Study of Adult Development (85+ years) found close relationships predict health and happiness better than wealth or IQ. Schedule the people who matter the way you schedule meetings, and be fully present: phone away.'));
    },

    score(date) {
      const d = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(d)) return null;
      const target = Math.max(1, Number(cfg().target) || 1);
      const ix = d.interactions || [];
      let s = Math.min(1, ix.length / target) * 50; // connection volume
      const rated = ix.filter((x) => x.quality);
      if (rated.length) s += (rated.reduce((a, x) => a + x.quality, 0) / rated.length / 5) * 25; // depth
      else if (ix.length) s += 10; // unrated: some credit
      if (d.helped) s += 12.5;
      if (d.compliment) s += 12.5;
      return Math.round(s);
    },

    summary(date) {
      const d = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(d)) return '';
      const ix = d.interactions || [];
      const parts = ix.length ? [`${ix.length} interaction${ix.length === 1 ? '' : 's'}`] : [];
      const uniq = [...new Set(ix.map((x) => x.person))];
      if (uniq.length && parts.length) parts[0] += ` (${uniq.slice(0, 2).join(', ')}${uniq.length > 2 ? '…' : ''})`;
      if (d.helped) parts.push('helped someone');
      if (d.compliment) parts.push('complimented');
      return parts.join(' · ');
    },
  });
})();
