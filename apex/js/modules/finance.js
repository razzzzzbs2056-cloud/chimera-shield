/* Apex module: Finance. Daily money log, budget, savings rate, net worth. */
(function () {
  const { h, card, row, stat, number, text, select, toggle, button, progress, bars, sparkline, list } = Apex.ui;
  const ID = 'finance';
  const DEFAULTS = { txns: [], noSpend: false };
  const CONFIG = { currency: '$', dailyBudget: 50, savingsGoal: 500, netWorth: [] };
  const TYPES = [
    { value: 'expense', label: 'Expense' },
    { value: 'income', label: 'Income' },
    { value: 'saving', label: 'Saving' },
    { value: 'investment', label: 'Investment' },
  ];
  const CATS = ['food', 'transport', 'housing', 'fun', 'health', 'education', 'other'];
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  // Draft for the "add transaction" form survives re-renders.
  const draft = { amount: null, type: 'expense', cat: 'food', note: '' };

  if (!document.getElementById('apex-style-' + ID)) {
    document.head.appendChild(h('style', { id: 'apex-style-' + ID }, `
.finance-kpis { margin-bottom: 12px; }
.finance-txn { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.finance-txn-amt { font-weight: 700; font-variant-numeric: tabular-nums; }
.finance-txn-amt.finance-in { color: var(--good); }
.finance-txn-amt.finance-out { color: var(--bad); }
.finance-txn-amt.finance-save { color: var(--accent); }
.finance-txn-note { flex-basis: 100%; }
.finance-cat-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.finance-cat-name { width: 84px; flex: none; font-size: .85rem; }
.finance-cat-amt { width: 84px; flex: none; text-align: right; font-size: .85rem; font-variant-numeric: tabular-nums; }
.finance-meter-label { display: flex; justify-content: space-between; gap: 8px; font-size: .85rem; margin: 10px 0 4px; flex-wrap: wrap; }
.finance-warn { color: var(--bad); }
.finance-nw { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
`));
  }

  const cfg = () => Apex.store.getConfig(ID, CONFIG);
  const num = (v) => (typeof v === 'number' && isFinite(v) ? v : 0);

  function money(n, sym) {
    const s = Math.abs(num(n)).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return (n < 0 ? '-' : '') + (sym == null ? cfg().currency : sym) + s;
  }

  function totals(data) {
    const t = { income: 0, expense: 0, saving: 0, investment: 0, count: 0, byCat: {} };
    ((data && data.txns) || []).forEach((x) => {
      const a = num(x.amount);
      if (!(x.type in t)) return;
      t[x.type] += a;
      t.count++;
      if (x.type === 'expense') t.byCat[x.cat || 'other'] = (t.byCat[x.cat || 'other'] || 0) + a;
    });
    return t;
  }

  /** Totals from the 1st of the month up to and including `date`. */
  function monthTotals(date) {
    const dom = Number(date.slice(8, 10));
    const m = { income: 0, expense: 0, saving: 0, investment: 0, count: 0, byCat: {}, days: dom, noSpendDays: 0 };
    Apex.store.range(ID, date, dom).forEach(({ data }) => {
      if (!data) return;
      const t = totals(data);
      ['income', 'expense', 'saving', 'investment', 'count'].forEach((k) => (m[k] += t[k]));
      Object.entries(t.byCat).forEach(([k, v]) => (m.byCat[k] = (m.byCat[k] || 0) + v));
      if (data.noSpend && t.expense === 0) m.noSpendDays++;
    });
    return m;
  }

  function isLogged(data) {
    return !!data && (((data.txns || []).length > 0) || !!data.noSpend);
  }

  Apex.registerModule({
    id: ID,
    name: 'Finance',
    icon: '💰',
    category: 'wealth',
    order: 100,
    weight: 1,
    description: 'The top 1% know where every dollar goes, spend below their means, and invest the gap.',

    render(el, ctx) {
      const c = cfg();
      const sym = c.currency;
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      const saveCfg = () => { Apex.store.setConfig(ID, c); ctx.refresh(); };
      const t = totals(d);
      const m = monthTotals(ctx.date);
      const budget = num(c.dailyBudget);
      const monthBudget = budget * m.days;
      const saved = m.saving + m.investment;
      const rate = m.income > 0 ? Math.round((saved / m.income) * 100) : null;

      // ---- today ----
      const addTxn = () => {
        if (!(num(draft.amount) > 0)) { Apex.ui.toast('Enter an amount above 0'); return; }
        d.txns = (d.txns || []).concat({ amount: num(draft.amount), type: draft.type, cat: draft.type === 'expense' ? draft.cat : null, note: (draft.note || '').trim() });
        if (draft.type === 'expense') d.noSpend = false;
        draft.amount = null;
        draft.note = '';
        save();
      };

      el.append(card('Today',
        h('div', { class: 'kpis finance-kpis' },
          stat('Spent', money(t.expense, sym), budget ? `budget ${money(budget, sym)}` : null),
          stat('Earned', money(t.income, sym)),
          stat('Saved + invested', money(t.saving + t.investment, sym))),
        budget ? h('div', null,
          h('div', { class: 'finance-meter-label' }, h('span', null, 'Daily budget used'),
            h('span', { class: t.expense > budget ? 'finance-warn' : 'muted' }, `${money(t.expense, sym)} / ${money(budget, sym)}`)),
          progress(t.expense, budget, t.expense > budget ? 'var(--bad)' : 'var(--good)')) : null,
        h('div', { style: { marginTop: '12px' } },
          toggle({ label: 'No-spend day', hint: 'Spent nothing today, on purpose.', checked: !!d.noSpend,
            onChange: (v) => { d.noSpend = v; save(); } }),
          d.noSpend && t.expense > 0 ? h('p', { class: 'small finance-warn' }, 'You marked a no-spend day but logged expenses.') : null)));

      el.append(card('Log a transaction',
        row(
          number({ label: `Amount (${sym})`, value: draft.amount, min: 0, step: 0.01, onChange: (v) => { draft.amount = v; } }),
          select({ label: 'Type', value: draft.type, options: TYPES, onChange: (v) => { draft.type = v; ctx.refresh(); } }),
          draft.type === 'expense'
            ? select({ label: 'Category', value: draft.cat, options: CATS.map((x) => ({ value: x, label: cap(x) })), onChange: (v) => { draft.cat = v; } })
            : null),
        text({ label: 'Note', value: draft.note, placeholder: 'What was it?', onChange: (v) => { draft.note = v; } }),
        button('Add', addTxn, 'primary'),
        h('div', { style: { marginTop: '12px' } },
          list(d.txns || [], (x) => h('div', { class: 'finance-txn' },
            h('span', { class: 'finance-txn-amt ' + (x.type === 'income' ? 'finance-in' : x.type === 'expense' ? 'finance-out' : 'finance-save') },
              (x.type === 'expense' ? '−' : '+') + money(x.amount, sym)),
            h('span', { class: 'tag' }, cap(x.type)),
            x.cat ? h('span', { class: 'muted small' }, cap(x.cat)) : null,
            x.note ? h('span', { class: 'muted small finance-txn-note' }, x.note) : null),
          (i) => { d.txns.splice(i, 1); save(); }))));

      // ---- month ----
      const catEntries = Object.entries(m.byCat).sort((a, b) => b[1] - a[1]).slice(0, 5);
      const catMax = catEntries.length ? catEntries[0][1] : 1;
      const goal = num(c.savingsGoal);
      el.append(card('This month',
        h('div', { class: 'kpis finance-kpis' },
          stat('Spent MTD', money(m.expense, sym), monthBudget ? `of ${money(monthBudget, sym)}` : null),
          stat('Savings rate', rate == null ? '—' : rate + '%', m.income > 0 ? `of ${money(m.income, sym)} income` : 'log income to see'),
          stat('No-spend days', String(m.noSpendDays), `${m.days} days so far`)),
        monthBudget ? h('div', null,
          h('div', { class: 'finance-meter-label' }, h('span', null, 'Spend vs budget (month to date)'),
            h('span', { class: m.expense > monthBudget ? 'finance-warn' : 'muted' }, `${Math.round((m.expense / monthBudget) * 100)}%`)),
          progress(m.expense, monthBudget, m.expense > monthBudget ? 'var(--bad)' : 'var(--good)')) : null,
        goal ? h('div', null,
          h('div', { class: 'finance-meter-label' }, h('span', null, 'Savings goal'),
            h('span', { class: 'muted' }, `${money(saved, sym)} / ${money(goal, sym)}`)),
          progress(saved, goal, 'var(--accent)')) : null,
        h('h4', { class: 'small muted', style: { margin: '14px 0 8px' } }, 'Top spending categories'),
        catEntries.length
          ? catEntries.map(([k, v]) => h('div', { class: 'finance-cat-row' },
            h('span', { class: 'finance-cat-name' }, cap(k)),
            progress(v, catMax),
            h('span', { class: 'finance-cat-amt' }, money(v, sym))))
          : h('p', { class: 'muted small' }, 'No expenses logged this month.')));

      // ---- history ----
      const days = Apex.date.lastN(ctx.date, 14);
      const hist = Apex.store.range(ID, ctx.date, 14).map(({ data }) => (isLogged(data) ? Math.round(totals(data).expense * 100) / 100 : null));
      const logged = hist.filter((v) => v != null);
      const under = budget ? logged.filter((v) => v <= budget).length : null;
      el.append(card('Spending · last 14 days',
        bars(hist, { labels: days.map((x) => Apex.date.format(x, { weekday: 'narrow' })), height: 90 }),
        h('p', { class: 'muted small', style: { marginTop: '8px' } },
          logged.length
            ? `Logged ${logged.length}/14 days` + (under != null ? ` · under budget on ${under}` : '') + ` · avg ${money(logged.reduce((a, b) => a + b, 0) / logged.length, sym)}/day`
            : 'No days logged yet.')));

      // ---- net worth ----
      const nw = (c.netWorth || []).slice().sort((a, b) => (a.date < b.date ? -1 : 1));
      let nwDraft = null;
      const latest = nw.length ? nw[nw.length - 1] : null;
      const first = nw.length ? nw[0] : null;
      el.append(card('Net worth',
        h('div', { class: 'finance-nw' },
          stat('Latest', latest ? money(latest.value, sym) : '—', latest ? Apex.date.format(latest.date) : 'add a snapshot'),
          nw.length > 1 ? stat('Change', money(latest.value - first.value, sym), `since ${Apex.date.format(first.date)}`) : null,
          sparkline(nw.map((x) => x.value), { width: 160, height: 44 })),
        row(
          number({ label: `Snapshot for ${Apex.date.format(ctx.date)} (${sym})`, value: null, step: 0.01, onChange: (v) => { nwDraft = v; } }),
          button('Save snapshot', () => {
            if (nwDraft == null) { Apex.ui.toast('Enter your net worth first'); return; }
            c.netWorth = (c.netWorth || []).filter((x) => x.date !== ctx.date).concat({ date: ctx.date, value: nwDraft });
            saveCfg();
          })),
        list(nw.slice().reverse().slice(0, 6), (x) => h('span', null, `${Apex.date.format(x.date)} · ${money(x.value, sym)}`),
          (i) => {
            const target = nw[nw.length - 1 - i];
            c.netWorth = (c.netWorth || []).filter((x) => x.date !== target.date);
            saveCfg();
          })));

      // ---- settings ----
      el.append(card('Targets',
        row(
          text({ label: 'Currency symbol', value: c.currency, onChange: (v) => { c.currency = (v || '').trim() || '$'; saveCfg(); } }),
          number({ label: 'Daily spend budget', value: c.dailyBudget, min: 0, step: 1, unit: sym, onChange: (v) => { c.dailyBudget = v; saveCfg(); } }),
          number({ label: 'Monthly savings goal', value: c.savingsGoal, min: 0, step: 1, unit: sym, onChange: (v) => { c.savingsGoal = v; saveCfg(); } }))));

      el.append(h('p', { class: 'tip' },
        'Pay yourself first: automate a transfer of 20%+ of income on payday. The top 1% track every expense and invest the gap between what they earn and what they spend, then let compounding do the work.'));
    },

    score(date) {
      const data = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(data)) return null;
      const c = cfg();
      const t = totals(data);
      const budget = num(c.dailyBudget);
      let s = 30; // tracking itself
      // Spending discipline (40)
      if (budget > 0) s += t.expense <= budget ? 40 : Math.max(0, 40 * (1 - (t.expense - budget) / budget));
      else s += t.expense === 0 ? 40 : 20;
      // Building wealth (30): saved/invested today, or month-to-date savings on pace.
      if (t.saving + t.investment > 0) s += 30;
      else {
        const goal = num(c.savingsGoal);
        if (goal > 0) {
          const m = monthTotals(date);
          const pace = goal * (m.days / 30);
          if (m.saving + m.investment >= pace) s += 20;
        }
      }
      return Math.round(s);
    },

    summary(date) {
      const data = Apex.store.has(ID, date) ? Apex.store.get(ID, date, DEFAULTS) : null;
      if (!isLogged(data)) return '';
      const c = cfg();
      const t = totals(data);
      const parts = [];
      parts.push(t.expense === 0 && data.noSpend ? 'No-spend day' : `Spent ${money(t.expense, c.currency)}`);
      if (num(c.dailyBudget) > 0 && t.expense > 0) parts.push(t.expense <= c.dailyBudget ? 'under budget' : 'over budget');
      if (t.saving + t.investment > 0) parts.push(`saved ${money(t.saving + t.investment, c.currency)}`);
      return parts.join(' · ');
    },
  });
})();
