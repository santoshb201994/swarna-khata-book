import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token & Tenant header to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const tenant = localStorage.getItem('tenant_schema') || 'demo'
  config.headers['X-Tenant'] = tenant
  return config
})

// Deduplicated async refresh token promise queue
// Prevents race conditions and multiple refresh calls when concurrent requests return 401
let refreshPromise: Promise<string> | null = null

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh_token')

      if (refresh) {
        try {
          if (!refreshPromise) {
            refreshPromise = (async () => {
              try {
                const currentTenant = localStorage.getItem('tenant_schema') || 'demo'
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
