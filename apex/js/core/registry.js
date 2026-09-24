/* Apex core: module registry + Life Score engine.
 * Each tracker calls Apex.registerModule({...}). See docs/MODULE_CONTRACT.md.
 */
(function () {
  const Apex = (window.Apex = window.Apex || {});

  Apex.CATEGORIES = {
    body: { name: 'Body', icon: '💪', color: '#22c55e' },
    mind: { name: 'Mind', icon: '🧠', color: '#a855f7' },
    work: { name: 'Work', icon: '🎯', color: '#3b82f6' },
    wealth: { name: 'Wealth', icon: '💰', color: '#eab308' },
    life: { name: 'Life', icon: '❤️', color: '#f43f5e' },
  };

  const modules = [];
  const REQUIRED = ['id', 'name', 'icon', 'category', 'render', 'score'];

  Apex.registerModule = function (def) {
    const missing = REQUIRED.filter((k) => def[k] == null);
    if (missing.length) {
      console.error(`[apex] module ${def.id || '?'} missing: ${missing.join(', ')}`);
      return;
    }
    if (!Apex.CATEGORIES[def.category]) {
      console.error(`[apex] module ${def.id} has unknown category "${def.category}"`);
      return;
    }
    if (modules.some((m) => m.id === def.id)) {
      console.error(`[apex] duplicate module id ${def.id}`);
      return;
    }
    modules.push(Object.assign({ weight: 1, order: 100, description: '', summary: () => '' }, def));
    modules.sort((a, b) => a.order - b.order);
  };

  const settings = () => Apex.store.getConfig('_app', { disabled: [], weights: {} });

  Apex.modules = {
    all: () => modules.slice(),
    enabled: () => {
      const off = settings().disabled;
      return modules.filter((m) => !off.includes(m.id));
    },
    get: (id) => modules.find((m) => m.id === id),
    weight: (m) => {
      const w = settings().weights[m.id];
      return typeof w === 'number' ? w : m.weight;
    },
  };

  const clamp = (n) => Math.max(0, Math.min(100, n));

  /** Safe wrapper: a broken module must never break the dashboard. */
  Apex.moduleScore = function (m, date) {
    try {
      const s = m.score(date);
      return typeof s === 'number' && isFinite(s) ? Math.round(clamp(s)) : null;
    } catch (e) {
      console.error(`[apex] ${m.id}.score failed`, e);
      return null;
    }
  };

  Apex.moduleSummary = function (m, date) {
    try {
      return String(m.summary(date) || '');
    } catch (e) {
      return '';
    }
  };

  /** Weighted Life Score for a day. Modules with no data count as 0 so skipping days isn't rewarded. */
  Apex.lifeScore = function (date) {
    let total = 0;
    let weights = 0;
    const byCategory = {};
    const byModule = {};
    let tracked = 0;
    Apex.modules.enabled().forEach((m) => {
      const w = Apex.modules.weight(m);
      if (w <= 0) return;
      const s = Apex.moduleScore(m, date);
      byModule[m.id] = s;
      if (s != null) tracked++;
      const v = s == null ? 0 : s;
      total += v * w;
      weights += w;
      const c = (byCategory[m.category] = byCategory[m.category] || { total: 0, weights: 0 });
      c.total += v * w;
      c.weights += w;
    });
    Object.keys(byCategory).forEach((k) => {
      const c = byCategory[k];
      byCategory[k] = c.weights ? Math.round(c.total / c.weights) : 0;
    });
    return {
      score: weights ? Math.round(total / weights) : 0,
      byCategory,
      byModule,
      tracked,
      total: Apex.modules.enabled().length,
    };
  };

  Apex.tier = function (score) {
    if (score >= 90) return { label: 'Top 1%', color: '#f59e0b' };
    if (score >= 80) return { label: 'Top 5%', color: '#a855f7' };
    if (score >= 70) return { label: 'Top 10%', color: '#3b82f6' };
    if (score >= 50) return { label: 'Above average', color: '#22c55e' };
    if (score >= 25) return { label: 'Building', color: '#94a3b8' };
    return { label: 'Just starting', color: '#64748b' };
  };

  /** Consecutive days (ending today or yesterday) where the Life Score is >= threshold. */
  Apex.streak = function (end, threshold) {
    threshold = threshold == null ? 70 : threshold;
    let d = end;
    if (Apex.lifeScore(d).score < threshold) d = Apex.date.add(d, -1);
    let n = 0;
    while (n < 3650 && Apex.lifeScore(d).score >= threshold) {
      n++;
      d = Apex.date.add(d, -1);
    }
    return n;
  };
})();
