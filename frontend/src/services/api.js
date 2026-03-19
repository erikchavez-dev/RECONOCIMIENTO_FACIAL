// api.js — Configuración central de Axios
// Todas las llamadas al backend pasan por aquí
// Agrega automáticamente el token JWT en cada request
// Si el token expira, intenta renovarlo automáticamente

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  //baseURL: 'http://127.0.0.1:8000',  // URL del backend Django
  //baseURL: 'http://10.38.154.121:8000',
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,                      // 10 segundos máximo por request
})

// INTERCEPTOR DE REQUEST
// Antes de cada llamada al backend, agrega el token JWT al header
api.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// INTERCEPTOR DE RESPONSE
// Si el backend responde 401 (token expirado), intenta renovar el token
// Si no puede renovar, cierra la sesión automáticamente
api.interceptors.response.use(
  response => response,
  async error => {
    const auth = useAuthStore()
    const original = error.config

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        await auth.refreshToken()
        original.headers.Authorization = `Bearer ${auth.token}`
        return api(original)
      } catch {
        // Solo redirigir al login si NO estamos en la vista de marcar
        if (!window.location.pathname.includes('/trabajador/marcar')) {
          auth.logout()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api