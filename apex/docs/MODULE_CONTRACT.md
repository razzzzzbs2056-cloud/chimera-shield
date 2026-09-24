# Apex module contract

Every life area in Apex (sleep, fitness, money…) is a **module**: one self-contained
file in `js/modules/<id>.js`. It's a plain script (no bundler, no imports). Each module
registers itself with the core, and the core connects it to the dashboard, the
Life Score, navigation, streaks, and backup.

```js
(function () {
  const { h, card } = Apex.ui;          // DOM helpers (see js/core/ui.js)
  const ID = 'sleep';
  const DEFAULTS = { hours: null, quality: null };

  Apex.registerModule({
    id: ID,                      // unique, lowercase, also used in the URL: #/m/sleep
    name: 'Sleep',
    icon: '😴',                  // one emoji
    category: 'body',            // body | mind | work | wealth | life
    order: 10,                   // position in nav (lower = earlier)
    weight: 1,                   // default weight in the Life Score (user can change)
    description: 'One line explaining why this matters for the top 1%.',

    /** Draw the tracker UI for `ctx.date` into `el` (already emptied). */
    render(el, ctx) {
      const d = Apex.store.get(ID, ctx.date, DEFAULTS);
      const save = () => { Apex.store.set(ID, ctx.date, d); ctx.refresh(); };
      el.append(card('Last night', Apex.ui.number({ label: 'Hours', value: d.hours,
        onChange: (v) => { d.hours = v; save(); } })));
    },

    /** 0–100 for that day, or null if nothing was logged. Must be pure and fast. */
    score(date) {
      if (!Apex.store.has(ID, date)) return null;
      const d = Apex.store.get(ID, date, DEFAULTS);
      return Math.min(100, (d.hours || 0) / 8 * 100);
    },

    /** Short one-line status for dashboard tiles, e.g. "7h 20m · quality 4/5". */
    summary(date) { return ''; },
  });
})();
```

## Rules

1. **Storage only through `Apex.store`.** Use `get / set / update / has / range` for per-day data
   and `getConfig / setConfig` for settings such as targets, habit lists, and goals. Never touch
   `localStorage` directly: backup and restore depend on this.
2. **Always write a date key.** Use `ctx.date` (the date the user picked in the header), not
   today's date. Date keys are `YYYY-MM-DD`. Use `Apex.date.add(key, n)` and `Apex.date.lastN(key, n)`.
3. **After saving, call `ctx.refresh()`.** It re-renders the header score and your view.
   Only call it from event handlers, never during render. When a text field is being typed into,
   save on `change` (the helpers already do this), so re-rendering doesn't steal focus.
4. **Scoring must be honest.** 100 means "a top-1% performer's day in this area". Return `null` when
   nothing is logged. Keep `score()` pure: no DOM work and no writes.
5. **Build UI with `Apex.ui` helpers and the CSS classes in `css/styles.css`.** Never use `innerHTML`
   with user data. Use your own class names prefixed with the module id (`.sleep-…`) if you need
   extra CSS. Put that CSS in a `<style>` element that you inject once, from your module file.
6. **Every module should show:** (a) today's inputs, (b) progress toward a target,
   (c) a 7- or 30-day history using `Apex.ui.bars` or `Apex.ui.sparkline`, and (d) one
   "top 1% insight" or tip.
7. **No network and no external libraries.** The app must work offline.

## ctx

| field       | meaning                                         |
|-------------|-------------------------------------------------|
| `ctx.date`  | selected day key `YYYY-MM-DD`                   |
| `ctx.today` | real today key                                   |
| `ctx.refresh()` | re-render after a save                      |
| `ctx.go(hash)`  | navigate, e.g. `ctx.go('#/m/habits')`       |

## UI helpers (`Apex.ui`)

`h(tag, attrs, ...children)`, `svg`, `card(title, ...)`, `row(...)`, `grid(...)`, `stat(label, value, sub)`,
`number({label,value,onChange,min,max,step,unit})`, `text({...})`, `textarea({...})`,
`select({label,value,options,onChange})`, `rating({label,value,max,onChange,icons})`,
`toggle({label,checked,onChange,hint})`, `button(label,onClick,variant)` (variants: `primary`, `ghost`, `danger`),
`progress(value,max,color)`, `ring(score,{size,color,label})`, `bars(values,{max,color,labels,height})`,
`sparkline(values,{width,height,color})`, `list(items,render,onRemove)`, `adder(placeholder,onAdd)`,
`empty(text)`, `toast(msg)`, `fmtMinutes(min)`.

CSS utility classes: `.card .row .grid .stat .muted .small .pill .tag .btn .list .progress .kpis .tip .spacer`.
