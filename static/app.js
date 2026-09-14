const svg = document.getElementById('graph');
const edgesLayer = document.getElementById('edges');
const nodesLayer = document.getElementById('nodes');
const inspector = document.getElementById('inspector');
const notice = document.getElementById('notice');
const modeBadge = document.getElementById('mode-badge');

const positions = {
  households: [190, 345],
  firms: [550, 330],
  government: [530, 95],
  banks: [210, 585],
  retirement: [500, 600],
  'rest-world': [895, 335],
  'political-orgs': [825, 115],
  'media-vendors': [835, 560],
  'public-companies': [610, 505],
  'unresolved-firms': [690, 225]
};

const state = { graph: null, layer: 'all', mode: 'reported', selected: null };

const esc = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const humanize = (value) => value.replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());

function money(flow) {
  if (flow.amount == null) return 'Amount unavailable';
  const n = Number(flow.amount);
  if (n >= 1000) return `$${(n / 1000).toFixed(n % 1000 === 0 ? 0 : 3)}T / yr`;
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 1 })}B / yr`;
}

function filteredFlows() {
  if (!state.graph) return [];
  return state.layer === 'all'
    ? state.graph.flows
    : state.graph.flows.filter(flow => flow.layer === state.layer);
}

function makeSvg(tag, attrs = {}) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  return el;
}

function renderGraph() {
  edgesLayer.innerHTML = '';
  nodesLayer.innerHTML = '';
  const flows = filteredFlows();
  const connected = new Set(flows.flatMap(flow => [flow.source, flow.target]));
  const entities = state.layer === 'all'
    ? state.graph.entities
    : state.graph.entities.filter(entity => connected.has(entity.id));

  for (const flow of flows) {
    const a = positions[flow.source];
    const b = positions[flow.target];
    if (!a || !b) continue;
    const [x1, y1] = a;
    const [x2, y2] = b;
    const dx = x2 - x1;
    const dy = y2 - y1;
    const len = Math.hypot(dx, dy) || 1;
    const pad = 61;
    const sx = x1 + dx / len * pad;
    const sy = y1 + dy / len * pad;
    const tx = x2 - dx / len * pad;
    const ty = y2 - dy / len * pad;

    const line = makeSvg('line', {
      x1: sx, y1: sy, x2: tx, y2: ty,
      class: `edge ${flow.layer}`,
      'data-flow': flow.id
    });
    line.addEventListener('click', () => showFlow(flow));
    edgesLayer.appendChild(line);

    const label = makeSvg('text', {
      x: (sx + tx) / 2,
      y: (sy + ty) / 2 - 7,
      class: 'edge-label'
    });
    label.textContent = humanize(flow.type);
    edgesLayer.appendChild(label);
  }

  for (const entity of entities) {
    const pos = positions[entity.id];
    if (!pos) continue;
    const [x, y] = pos;
    const group = makeSvg('g', {
      class: `node${state.selected === entity.id ? ' selected' : ''}`,
      transform: `translate(${x}, ${y})`,
      tabindex: '0', role: 'button', 'aria-label': entity.name
    });
    group.appendChild(makeSvg('circle', { r: 58 }));
    const name = makeSvg('text', { class: 'name', y: -2 });
    const words = entity.name.split(' ');
    if (words.length > 2) {
      const first = makeSvg('tspan', { x: 0, dy: '-0.35em' });
      first.textContent = words.slice(0, Math.ceil(words.length / 2)).join(' ');
      const second = makeSvg('tspan', { x: 0, dy: '1.25em' });
      second.textContent = words.slice(Math.ceil(words.length / 2)).join(' ');
      name.append(first, second);
    } else name.textContent = entity.name;
    const kind = makeSvg('text', { class: 'kind', y: 31 });
    kind.textContent = entity.kind;
    group.append(name, kind);
    group.addEventListener('click', () => selectEntity(entity.id));
    group.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') selectEntity(entity.id);
    });
    nodesLayer.appendChild(group);
  }
}

function flowCard(flow, direction) {
  const entityMap = Object.fromEntries(state.graph.entities.map(e => [e.id, e]));
  const other = direction === 'in' ? entityMap[flow.source] : entityMap[flow.target];
  return `<div class="flow-card">
    <div class="title">${direction === 'in' ? '←' : '→'} ${esc(other?.name ?? 'Unknown')} · ${esc(humanize(flow.type))}</div>
    <div class="amount">${esc(money(flow))}</div>
    <div class="meta"><span class="badge layer">${esc(flow.layer)}</span><span class="badge ${esc(flow.status)}">${esc(flow.status)}</span>${flow.confidence != null ? `<span class="badge">confidence ${Math.round(flow.confidence * 100)}%</span>` : ''}</div>
    <p>${esc(flow.note)}</p>
  </div>`;
}

async function selectEntity(id) {
  state.selected = id;
  renderGraph();
  const response = await fetch(`/api/entities/${encodeURIComponent(id)}?mode=${state.mode}`);
  if (!response.ok) return;
  const detail = await response.json();
  const e = detail.entity;
  inspector.innerHTML = `<div class="kicker">${esc(e.sector)} · ${esc(e.kind)}</div>
    <h2>${esc(e.name)}</h2><p>${esc(e.description)}</p>
    ${detail.children.length ? `<h3>Drill down</h3><div class="children">${detail.children.map(child => `<button class="child-chip" data-id="${esc(child.id)}">${esc(child.name)}</button>`).join('')}</div>` : ''}
    <h3>Flows in</h3>${detail.incoming.length ? detail.incoming.map(flow => flowCard(flow, 'in')).join('') : '<p>No incoming flow is integrated in this data view.</p>'}
    <h3>Flows out</h3>${detail.outgoing.length ? detail.outgoing.map(flow => flowCard(flow, 'out')).join('') : '<p>No outgoing flow is integrated in this data view.</p>'}
    <h3>Provenance</h3>${detail.sources.length ? detail.sources.map(source => `<a class="source-link" href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.publisher)} · ${esc(source.name)}</a>`).join('') : '<p>No source attached.</p>'}`;
  inspector.querySelectorAll('.child-chip').forEach(btn => btn.addEventListener('click', () => selectEntity(btn.dataset.id)));
}

function showFlow(flow) {
  const entityMap = Object.fromEntries(state.graph.entities.map(e => [e.id, e]));
  const sources = state.graph.sources.filter(source => flow.source_ids.includes(source.id));
  inspector.innerHTML = `<div class="kicker">${esc(flow.layer)} flow · ${esc(flow.period)}</div>
    <h2>${esc(humanize(flow.type))}</h2>
    <p><strong>${esc(entityMap[flow.source]?.name)}</strong> → <strong>${esc(entityMap[flow.target]?.name)}</strong></p>
    <div class="amount">${esc(money(flow))}</div>
    <div class="meta"><span class="badge layer">${esc(flow.layer)}</span><span class="badge ${esc(flow.status)}">${esc(flow.status)}</span></div>
    <p>${esc(flow.note)}</p><h3>Provenance</h3>${sources.map(source => `<a class="source-link" href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.publisher)} · ${esc(source.name)}</a>`).join('') || '<p>No source attached.</p>'}`;
}

async function loadGraph() {
  const response = await fetch(`/api/graph?mode=${state.mode}`);
  if (!response.ok) throw new Error('Could not load graph');
  state.graph = await response.json();
  state.selected = null;
  state.layer = 'all';
  document.querySelectorAll('.layer-filter').forEach(button => button.classList.toggle('active', button.dataset.layer === 'all'));
  notice.textContent = state.graph.metadata.warning;
  modeBadge.textContent = state.mode === 'reported' ? 'Reported data' : 'Architecture demo';
  renderGraph();
}

async function init() {
  await loadGraph();
  document.querySelectorAll('.layer-filter').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.layer-filter').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      state.layer = button.dataset.layer;
      state.selected = null;
      renderGraph();
    });
  });
  document.querySelectorAll('.mode-filter').forEach(button => {
    button.addEventListener('click', async () => {
      document.querySelectorAll('.mode-filter').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      state.mode = button.dataset.mode;
      inspector.innerHTML = '<div class="inspector-empty"><span class="kicker">Inspect the circulation</span><h2>Select a node</h2><p>Click a sector or flow to inspect its amount, definition, evidence status, and source.</p></div>';
      await loadGraph();
    });
  });
}

init().catch(error => { notice.textContent = `OpenEconomy failed to load: ${error.message}`; });
