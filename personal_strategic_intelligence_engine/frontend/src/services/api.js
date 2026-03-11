import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Profile API
export const profileApi = {
  get: () => api.get('/profile'),
  create: (data) => api.post('/profile', data),
  update: (id, data) => api.patch(`/profile/${id}`, data),
};

// Signals API
export const signalsApi = {
  list: (params) => api.get('/signals', { params }),
  get: (id) => api.get(`/signals/${id}`),
  create: (data) => api.post('/signals', data),
  summary: (hours) => api.get('/signals/summary', { params: { hours } }),
};

// Governance API
export const governanceApi = {
  goals: {
    list: (params) => api.get('/governance/goals', { params }),
    get: (id) => api.get(`/governance/goals/${id}`),
    create: (data) => api.post('/governance/goals', data),
    update: (id, data) => api.patch(`/governance/goals/${id}`, data),
    progress: (id, data) => api.post(`/governance/goals/${id}/progress`, data),
    complete: (id) => api.post(`/governance/goals/${id}/complete`),
  },
  plans: {
    list: (params) => api.get('/governance/plans', { params }),
    get: (id) => api.get(`/governance/plans/${id}`),
    create: (data) => api.post('/governance/plans', data),
    complete: (id) => api.post(`/governance/plans/${id}/complete`),
  },
  schedules: {
    list: () => api.get('/governance/schedules'),
  },
  triggers: {
    list: (params) => api.get('/governance/triggers', { params }),
    resolve: (id) => api.post(`/governance/triggers/${id}/resolve`),
  },
  reviews: {
    run: (type) => api.post(`/governance/reviews/${type}`),
  },
  dashboard: () => api.get('/governance/dashboard'),
};

// Intelligence API
export const intelligenceApi = {
  trends: (params) => api.get('/intelligence/trends', { params }),
  forecasts: {
    list: (params) => api.get('/intelligence/forecasts', { params }),
    generate: (days) => api.post('/intelligence/forecasts/generate', null, { params: { days_ahead: days } }),
  },
  risks: {
    list: (params) => api.get('/intelligence/risks', { params }),
    project: () => api.post('/intelligence/risks/project'),
  },
  goals: {
    probability: (params) => api.get('/intelligence/goals/probability', { params }),
    calculate: () => api.post('/intelligence/goals/probability/calculate'),
  },
  scenario: {
    run: (data) => api.post('/intelligence/scenario/run', data),
  },
  dashboard: () => api.get('/intelligence/dashboard'),
};

// Simulation API
export const simulationApi = {
  run: (params) => api.post('/simulation/run', null, { params }),
  list: () => api.get('/simulation/runs'),
  get: (id) => api.get(`/simulation/runs/${id}`),
  report: (id) => api.get(`/simulation/runs/${id}/report`),
  events: (id) => api.get(`/simulation/runs/${id}/events`),
};

// Execution API
export const executionApi = {
  pending: () => api.get('/execution/pending'),
  executing: () => api.get('/execution/executing'),
  history: (limit) => api.get('/execution/history', { params: { limit } }),
  create: (data) => api.post('/execution/create', null, { params: data }),
  get: (id) => api.get(`/execution/${id}`),
  approve: (id) => api.post(`/execution/${id}/approve`),
  reject: (id, reason) => api.post(`/execution/${id}/reject`, null, { params: { reason } }),
  run: (id) => api.post(`/execution/${id}/run`),
  connectors: () => api.get('/execution/connectors/status'),
};

// Debate API
export const debateApi = {
  sessions: () => api.get('/debate/sessions'),
  session: (id) => api.get(`/debate/sessions/${id}`),
  arguments: (id) => api.get(`/debate/sessions/${id}/arguments`),
  votes: (id) => api.get(`/debate/sessions/${id}/votes`),
  start: (data) => api.post('/debate/start', null, { params: data }),
};

// Decisions API
export const decisionsApi = {
  list: (params) => api.get('/decisions', { params }),
  get: (id) => api.get(`/decisions/${id}`),
  create: (data) => api.post('/decisions', data),
  update: (id, data) => api.patch(`/decisions/${id}`, data),
};

// Board API
export const boardApi = {
  meetings: {
    list: (params) => api.get('/board/meetings', { params }),
    get: (id) => api.get(`/board/meetings/${id}`),
    create: (data) => api.post('/board/meetings', data),
    run: (id) => api.post(`/board/meetings/${id}/run`),
  },
  agents: {
    list: () => api.get('/board/agents'),
  },
};

// Health API
export const healthApi = {
  check: () => api.get('/health'),
};

export default api;
