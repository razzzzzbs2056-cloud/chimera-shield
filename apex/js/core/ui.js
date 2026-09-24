/* Apex core: tiny DOM toolkit shared by all modules.
 * Everything uses textContent, never innerHTML, so user input is always safe.
 */
(function () {
  const Apex = (window.Apex = window.Apex || {});
  const SVG_NS = 'http://www.w3.org/2000/svg';

  /** h('div', {class: 'x', onClick: fn}, 'text', childEl, [more]) */
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    applyAttrs(el, attrs);
    append(el, children);
    return el;
  }

  function applyAttrs(el, attrs) {
    if (!attrs) return;
    Object.entries(attrs).forEach(([k, v]) => {
      if (v == null || v === false) return;
      if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2).toLowerCase(), v);
      else if (k === 'class') el.className = v;
      else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
      else if (k === 'value' && 'value' in el) el.value = v;
      else if (k === 'checked') el.checked = !!v;
      else el.setAttribute(k, v === true ? '' : v);
    });
  }

  function append(el, children) {
    children.flat(Infinity).forEach((c) => {
      if (c == null || c === false) return;
      el.appendChild(c instanceof Node ? c : document.createTextNode(String(c)));
    });
  }

  function svg(tag, attrs, ...children) {
    const el = document.createElementNS(SVG_NS, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => v != null && el.setAttribute(k, v));
    children.flat().forEach((c) => c && el.appendChild(c));
    return el;
  }

  let fieldId = 0;
  const nextId = () => `f${++fieldId}`;

  const ui = {
    h,
    svg,

    card(title, ...children) {
      return h('section', { class: 'card' }, title ? h('h3', { class: 'card-title' }, title) : null, ...children);
    },

    row(...children) {
      return h('div', { class: 'row' }, ...children);
    },

    grid(...children) {
      return h('div', { class: 'grid' }, ...children);
    },

    stat(label, value, sub) {
      return h('div', { class: 'stat' },
        h('div', { class: 'stat-value' }, value),
        h('div', { class: 'stat-label' }, label),
        sub ? h('div', { class: 'stat-sub' }, sub) : null);
    },

    number({ label, value, onChange, min, max, step, unit, placeholder }) {
      const id = nextId();
      const input = h('input', {
        id, type: 'number', inputmode: 'decimal', value: value == null ? '' : value,
        min, max, step: step || 'any', placeholder: placeholder || '',
        onChange: (e) => {
          const v = e.target.value === '' ? null : Number(e.target.value);
          onChange && onChange(v);
        },
      });
      return h('label', { class: 'field', for: id }, h('span', null, label),
        h('div', { class: 'field-input' }, input, unit ? h('span', { class: 'unit' }, unit) : null));
    },

    text({ label, value, onChange, placeholder, type }) {
      const id = nextId();
      return h('label', { class: 'field', for: id }, label ? h('span', null, label) : null,
        h('input', { id, type: type || 'text', value: value || '', placeholder: placeholder || '',
          onChange: (e) => onChange && onChange(e.target.value) }));
    },

    textarea({ label, value, onChange, placeholder, rows }) {
      const id = nextId();
      const ta = h('textarea', { id, rows: rows || 4, placeholder: placeholder || '',
        onChange: (e) => onChange && onChange(e.target.value) });
      ta.value = value || '';
      return h('label', { class: 'field', for: id }, label ? h('span', null, label) : null, ta);
    },

    select({ label, value, options, onChange }) {
      const id = nextId();
      const sel = h('select', { id, onChange: (e) => onChange && onChange(e.target.value) },
        options.map((o) => {
          const opt = typeof o === 'string' ? { value: o, label: o } : o;
          return h('option', { value: opt.value, selected: opt.value === value ? true : null }, opt.label);
        }));
      return h('label', { class: 'field', for: id }, label ? h('span', null, label) : null, sel);
    },

    /** 1..max rating as tappable pills (mood, energy, quality...). */
    rating({ label, value, max, onChange, icons }) {
      max = max || 5;
      const wrap = h('div', { class: 'rating', role: 'radiogroup', 'aria-label': label || 'rating' });
      for (let i = 1; i <= max; i++) {
        wrap.appendChild(h('button', {
          type: 'button', class: 'pill' + (value === i ? ' active' : ''), role: 'radio',
          'aria-checked': value === i ? 'true' : 'false',
          onClick: () => onChange && onChange(value === i ? null : i),
        }, icons ? icons[i - 1] : String(i)));
      }
      return h('div', { class: 'field' }, label ? h('span', null, label) : null, wrap);
    },

    toggle({ label, checked, onChange, hint, ariaLabel }) {
      const id = nextId();
      return h('label', { class: 'toggle', for: id },
        h('input', { id, type: 'checkbox', checked, 'aria-label': ariaLabel || null, onChange: (e) => onChange && onChange(e.target.checked) }),
        h('span', { class: 'toggle-box', 'aria-hidden': 'true' }),
        h('span', { class: 'toggle-label' }, label, hint ? h('small', null, hint) : null));
    },

    button(label, onClick, variant) {
      return h('button', { type: 'button', class: 'btn' + (variant ? ' btn-' + variant : ''), onClick }, label);
    },

    /** Horizontal bar. value/max, optional color. */
    progress(value, max, color) {
      const pct = max ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
      return h('div', { class: 'progress', role: 'progressbar', 'aria-valuenow': Math.round(pct), 'aria-valuemin': 0, 'aria-valuemax': 100 },
        h('div', { class: 'progress-fill', style: { width: pct + '%', background: color || '' } }));
    },

    /** Circular score gauge 0..100. */
    ring(score, { size, color, label } = {}) {
      size = size || 120;
      const r = size / 2 - 8;
      const c = 2 * Math.PI * r;
      const pct = Math.max(0, Math.min(100, score || 0)) / 100;
      return h('div', { class: 'ring', style: { width: size + 'px', height: size + 'px', fontSize: Math.max(9, size * 0.13) + 'px' } },
        svg('svg', { width: size, height: size, viewBox: `0 0 ${size} ${size}`, 'aria-hidden': 'true' },
          svg('circle', { cx: size / 2, cy: size / 2, r, class: 'ring-track', 'stroke-width': 8, fill: 'none' }),
          svg('circle', { cx: size / 2, cy: size / 2, r, fill: 'none', stroke: color || 'var(--accent)', 'stroke-width': 8,
            'stroke-linecap': 'round', 'stroke-dasharray': `${c * pct} ${c}`, transform: `rotate(-90 ${size / 2} ${size / 2})` })),
        h('div', { class: 'ring-center' }, h('strong', null, String(Math.round(score || 0))), label ? h('small', null, label) : null));
    },

    /** Mini bar chart. values: array of numbers or nulls; labels optional. */
    bars(values, { max, color, labels, height } = {}) {
      height = height || 64;
      const top = max || Math.max(1, ...values.map((v) => v || 0));
      return h('div', { class: 'bars', style: { height: height + 'px' } },
        values.map((v, i) => h('div', { class: 'bar-col', title: labels ? `${labels[i]}: ${v == null ? '—' : v}` : String(v == null ? '—' : v) },
          h('div', { class: 'bar-track' },
            h('div', { class: 'bar' + (v == null ? ' bar-empty' : ''), style: { height: (v == null ? 2 : Math.max(2, Math.min(100, (v / top) * 100))) + '%', background: v == null ? '' : color || '' } })),
          labels ? h('span', { class: 'bar-label' }, labels[i]) : null)));
    },

    /** Line sparkline, values may contain null. */
    sparkline(values, { width, height, color } = {}) {
      width = width || 160;
      height = height || 40;
      const nums = values.filter((v) => v != null);
      if (!nums.length) return h('div', { class: 'muted small' }, 'No data yet');
      const min = Math.min(...nums);
      const max = Math.max(...nums);
      const span = max - min || 1;
      const step = values.length > 1 ? width / (values.length - 1) : 0;
      const pts = values.map((v, i) => (v == null ? null : [i * step, height - 4 - ((v - min) / span) * (height - 8)])).filter(Boolean);
      return svg('svg', { class: 'sparkline', width, height, viewBox: `0 0 ${width} ${height}`, 'aria-hidden': 'true' },
        svg('polyline', { points: pts.map((p) => p.join(',')).join(' '), fill: 'none', stroke: color || 'var(--accent)', 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }));
    },

    /** Editable list of strings/objects. render(item, i) -> Node; onRemove(i). */
    list(items, render, onRemove) {
      if (!items.length) return h('p', { class: 'muted small' }, 'Nothing here yet.');
      return h('ul', { class: 'list' }, items.map((it, i) => h('li', null,
        h('div', { class: 'list-body' }, render(it, i)),
        onRemove ? h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Remove', onClick: () => onRemove(i) }, '✕') : null)));
    },

    /** Inline "add item" form: returns node; onAdd(value) called with trimmed string. */
    adder(placeholder, onAdd) {
      const input = h('input', { type: 'text', placeholder });
      const submit = (e) => {
        e.preventDefault();
        const v = input.value.trim();
        if (v) { onAdd(v); input.value = ''; }
      };
      return h('form', { class: 'adder', onSubmit: submit }, input, h('button', { type: 'submit', class: 'btn' }, 'Add'));
    },

    empty(text) {
      return h('p', { class: 'muted' }, text);
    },

    toast(msg) {
      let host = document.getElementById('toast-host');
      if (!host) {
        host = h('div', { id: 'toast-host', 'aria-live': 'polite' });
        document.body.appendChild(host);
      }
      const t = h('div', { class: 'toast' }, msg);
      host.appendChild(t);
      setTimeout(() => t.remove(), 2200);
    },

    fmtMinutes(min) {
      if (min == null) return '—';
      const hh = Math.floor(min / 60);
      const mm = Math.round(min % 60);
      return hh ? `${hh}h ${mm}m` : `${mm}m`;
    },
  };

  Apex.ui = ui;
})();
