import api from './client'

export interface Recommendation {
  id: number
  type: string
  suggestion: string
  status: string
  created_at: string
}

export interface Audit {
  id: number
  url: string
  title: string | null
  meta_description: string | null
  h1: string | null
  h2: string[] | null
  word_count: number
  images_count: number
  links_count: number
  load_time: number | null
  seo_score: number
  geo_score: number
  created_at: string
  recommendations: Recommendation[]
}

export interface Keyword {
  id: number
  keyword: string
  position: number | null
  previous_position: number | null
  volume: number | null
  created_at: string
}

export interface AgentResult {
  status: string
  audit_id: number
  current_seo_score: number
  current_geo_score: number
  actions: string[]
  generated_content?: Record<string, unknown>
}

export const authApi = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  register: (email: string, password: string) => api.post('/auth/register', { email, password }),
  me: () => api.get('/auth/me'),
  requestPasswordReset: (email: string) => api.post('/auth/password-reset-request', { email }),
  resetPassword: (token: string, newPassword: string) =>
    api.post('/auth/password-reset', { token, new_password: newPassword }),
}

export const auditsApi = {
  create: (url: string, model?: string) => api.post<Audit>('/audits/', { url, model }),
  list: () => api.get<Audit[]>('/audits/'),
  get: (id: number) => api.get<Audit>(`/audits/${id}`),
  remove: (id: number) => api.delete(`/audits/${id}`),
}

export const recommendationsApi = {
  apply: (id: number) => api.patch(`/recommendations/${id}/apply`),
  dismiss: (id: number) => api.patch(`/recommendations/${id}/dismiss`),
}

export const keywordsApi = {
  list: () => api.get<Keyword[]>('/keywords/'),
  create: (keyword: string, auditId?: number) => api.post<Keyword>('/keywords/', { keyword, audit_id: auditId }),
  refresh: (id: number) => api.post<Keyword>(`/keywords/${id}/refresh`),
  remove: (id: number) => api.delete(`/keywords/${id}`),
}

export const agentApi = {
  run: (url: string, targetScore: number, model?: string) =>
    api.post<AgentResult>('/agent/optimize', { url, target_score: targetScore, model }),
}

export const reportsApi = {
  emailAudit: (auditId: number) => api.post(`/reports/audit/${auditId}/email`),
}
