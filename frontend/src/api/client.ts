import axios from 'axios'
import { logger } from '../utils/logger'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token & Tenant header to every request and record telemetry
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const tenant = localStorage.getItem('tenant_schema') || 'demo'
  config.headers['X-Tenant'] = tenant

  ;(config as unknown as { _startTime: number })._startTime = performance.now()
  logger.debug('api', `--> ${config.method?.toUpperCase()} ${config.url} [Tenant: ${tenant}]`)

  return config
})

// Deduplicated async refresh token promise queue
// Prevents race conditions and multiple refresh calls when concurrent requests return 401
let refreshPromise: Promise<string> | null = null

api.interceptors.response.use(
  (res) => {
    const startTime = (res.config as unknown as { _startTime?: number })._startTime
    const duration = startTime ? Math.round(performance.now() - startTime) : 0
    logger.info('api', `<-- ${res.config.method?.toUpperCase()} ${res.config.url} [${res.status}] (${duration}ms)`)
    return res
  },
  async (error) => {
    const originalRequest = error.config
    const startTime = (originalRequest as unknown as { _startTime?: number })?._startTime
    const duration = startTime ? Math.round(performance.now() - startTime) : 0
    const errText = error.response?.data?.error || error.response?.data?.detail || error.message || 'Unknown Error'

    logger.warn('api', `<-- ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url} [${error.response?.status || 'NET_ERR'}] (${duration}ms): ${errText}`)

    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh_token')

      if (refresh) {
        try {
          if (!refreshPromise) {
            refreshPromise = (async () => {
              try {
                const currentTenant = localStorage.getItem('tenant_schema') || 'demo'
                logger.info('auth', `Attempting access token refresh [Tenant: ${currentTenant}]`)
                const { data } = await axios.post('/api/auth/token/refresh/', { refresh }, {
                  headers: { 'X-Tenant': currentTenant }
                })
                localStorage.setItem('access_token', data.access)
                if (data.refresh) {
                  localStorage.setItem('refresh_token', data.refresh)
                }
                if (data.tenant_schema) {
                  localStorage.setItem('tenant_schema', data.tenant_schema)
                }
                logger.info('auth', 'Access token refreshed successfully')
                return data.access
              } finally {
                refreshPromise = null
              }
            })()
          }

          const newAccessToken = await refreshPromise
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api.request(originalRequest)
        } catch (refreshErr) {
          logger.error('auth', 'Session refresh failed; redirecting to login', refreshErr)
          refreshPromise = null
          localStorage.clear()
          window.location.href = '/login'
          return Promise.reject(refreshErr)
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
