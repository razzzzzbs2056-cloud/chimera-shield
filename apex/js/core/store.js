/* Apex core: date utilities + persistent store (localStorage).
 * Every tracker module stores one JSON object per day, plus one config object.
 *   daily:  apex:v1:<moduleId>:<YYYY-MM-DD>
 *   config: apex:v1:<moduleId>:config
 */
(function () {
  const Apex = (window.Apex = window.Apex || {});
  const PREFIX = 'apex:v1:';

  const pad = (n) => String(n).padStart(2, '0');

  Apex.date = {
    toKey(d) {
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    },
    parse(key) {
      const [y, m, d] = key.split('-').map(Number);
      return new Date(y, m - 1, d);
    },
    today() {
      return Apex.date.toKey(new Date());
    },
    add(key, days) {
      const d = Apex.date.parse(key);
      d.setDate(d.getDate() + days);
      return Apex.date.toKey(d);
    },
    diff(a, b) {
      // whole days from b to a
      return Math.round((Apex.date.parse(a) - Apex.date.parse(b)) / 86400000);
    },
    format(key, opts) {
      return Apex.date.parse(key).toLocaleDateString(undefined, opts || { weekday: 'short', month: 'short', day: 'numeric' });
    },
    weekday(key) {
      return Apex.date.parse(key).getDay(); // 0 = Sunday
    },
    /** Array of date keys ending at `end` (inclusive), oldest first. */
    lastN(end, n) {
      const out = [];
      for (let i = n - 1; i >= 0; i--) out.push(Apex.date.add(end, -i));
      return out;
    },
  };

  let memory = {}; // fallback when localStorage is unavailable
  const backend = (() => {
    try {
      const t = PREFIX + '__test';
      localStorage.setItem(t, '1');
      localStorage.removeItem(t);
      return localStorage;
    } catch (e) {
      return {
        getItem: (k) => (k in memory ? memory[k] : null),
        setItem: (k, v) => { memory[k] = String(v); },
        removeItem: (k) => { delete memory[k]; },
        key: (i) => Object.keys(memory)[i] || null,
        get length() { return Object.keys(memory).length; },
      };
    }
  })();

  const listeners = new Set();
  const read = (k, fallback) => {
    try {
      const raw = backend.getItem(k);
      return raw == null ? fallback : JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  };
  const write = (k, v) => {
    backend.setItem(k, JSON.stringify(v));
    listeners.forEach((fn) => fn(k));
  };
  const clone = (v) => JSON.parse(JSON.stringify(v));

  Apex.store = {
    /** Day entry for a module. Returns a fresh copy of `defaults` merged with saved data. */
    get(moduleId, date, defaults) {
      const saved = read(`${PREFIX}${moduleId}:${date}`, null);
      return Object.assign(clone(defaults || {}), saved || {});
    },
    /** True if the module has saved anything for that day. */
    has(moduleId, date) {
      return backend.getItem(`${PREFIX}${moduleId}:${date}`) != null;
    },
    set(moduleId, date, data) {
      write(`${PREFIX}${moduleId}:${date}`, data);
    },
    /** Read-modify-write helper: fn receives the entry and may mutate or return a new one. */
    update(moduleId, date, fn, defaults) {
      const cur = Apex.store.get(moduleId, date, defaults);
      const next = fn(cur);
      Apex.store.set(moduleId, date, next === undefined ? cur : next);
      return next === undefined ? cur : next;
    },
    remove(moduleId, date) {
      backend.removeItem(`${PREFIX}${moduleId}:${date}`);
      listeners.forEach((fn) => fn(moduleId));
    },
    /** Non-dated module settings (targets, habit lists, goals...). */
    getConfig(moduleId, defaults) {
      return Object.assign(clone(defaults || {}), read(`${PREFIX}${moduleId}:config`, {}) || {});
    },
    setConfig(moduleId, cfg) {
      write(`${PREFIX}${moduleId}:config`, cfg);
    },
    /** [{date, data}] for the `days` days ending at `end`, oldest first. data is null when nothing saved. */
    range(moduleId, end, days) {
      return Apex.date.lastN(end, days).map((date) => ({
        date,
        data: read(`${PREFIX}${moduleId}:${date}`, null),
      }));
    },
    /** Everything Apex has stored, for backup. */
    exportAll() {
      const out = {};
      for (let i = 0; i < backend.length; i++) {
        const k = backend.key(i);
        if (k && k.startsWith(PREFIX)) out[k] = read(k, null);
      }
      return { app: 'apex', version: 1, exportedAt: new Date().toISOString(), data: out };
    },
    importAll(dump) {
      if (!dump || dump.app !== 'apex' || typeof dump.data !== 'object') throw new Error('Not an Apex backup file');
      Object.entries(dump.data).forEach(([k, v]) => {
        if (k.startsWith(PREFIX)) backend.setItem(k, JSON.stringify(v));
      });
      listeners.forEach((fn) => fn('*'));
    },
    clearAll() {
      const keys = [];
      for (let i = 0; i < backend.length; i++) {
        const k = backend.key(i);
        if (k && k.startsWith(PREFIX)) keys.push(k);
      }
      keys.forEach((k) => backend.removeItem(k));
      memory = {};
      listeners.forEach((fn) => fn('*'));
    },
    onChange(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
})();
