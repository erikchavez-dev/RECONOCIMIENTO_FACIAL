// auth.js — Store de autenticación con Pinia
// Cada pestaña tiene su propia sesión independiente via sessionStorage
// Esto permite que un admin y un trabajador estén logueados en pestañas distintas
// Las URLs del backend se leen desde VITE_API_URL (sin hardcodear)
// stores/auth.js — Store de autenticación con Pinia
// Cada pestaña tiene su propia sesión independiente via sessionStorage

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL

function cargarSesion() {
  try {
    const raw = sessionStorage.getItem('auth_session')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function guardarSesion(data) {
  try {
    sessionStorage.setItem('auth_session', JSON.stringify(data))
  } catch {}
}

function limpiarSesion() {
  try {
    sessionStorage.removeItem('auth_session')
  } catch {}
}

export const useAuthStore = defineStore('auth', () => {

  const sesionGuardada = cargarSesion()

  const token              = ref(sesionGuardada?.token        || null)
  const refreshTokenValue  = ref(sesionGuardada?.refreshToken || null)
  const usuario            = ref(sesionGuardada?.usuario      || null)

  // ── Computed de rol ──────────────────────────────────────────────────────
  const isAuthenticated   = computed(() => !!token.value)
  const rolActual         = computed(() => usuario.value?.rol || null)

  const esSuperAdmin      = computed(() => rolActual.value === 'SUPERADMIN')
  const esAdmin           = computed(() => rolActual.value === 'ADMIN')
  const esAdminOSuperAdmin = computed(() => ['ADMIN', 'SUPERADMIN'].includes(rolActual.value))
  const esTrabajador      = computed(() => rolActual.value === 'TRABAJADOR')

  // Alias para compatibilidad con código existente
  const isAdmin           = esAdminOSuperAdmin

  const debeCambiarPassword = computed(() => usuario.value?.debe_cambiar_password)

  // ── LOGIN ────────────────────────────────────────────────────────────────
  async function login(username, password) {
    const response = await axios.post(`${BASE_URL}/api/auth/login/`, { username, password })

    token.value             = response.data.access
    refreshTokenValue.value = response.data.refresh
    usuario.value           = {
      ...response.data.usuario,
      debe_cambiar_password: response.data.debe_cambiar_password,
    }

    guardarSesion({
      token:        token.value,
      refreshToken: refreshTokenValue.value,
      usuario:      usuario.value,
    })

    return response.data
  }

  // ── LOGOUT ───────────────────────────────────────────────────────────────
  async function logout() {
    try {
      if (refreshTokenValue.value) {
        await axios.post(`${BASE_URL}/api/auth/logout/`, {
          refresh: refreshTokenValue.value,
        }, {
          headers: { Authorization: `Bearer ${token.value}` },
        })
      }
    } catch {}
    finally {
      token.value             = null
      refreshTokenValue.value = null
      usuario.value           = null
      limpiarSesion()
    }
  }

  // ── REFRESH TOKEN ────────────────────────────────────────────────────────
  async function refreshToken() {
    const response = await axios.post(`${BASE_URL}/api/auth/token/refresh/`, {
      refresh: refreshTokenValue.value,
    })
    token.value = response.data.access
    guardarSesion({
      token:        token.value,
      refreshToken: refreshTokenValue.value,
      usuario:      usuario.value,
    })
  }

  return {
    token,
    usuario,
    rolActual,
    isAuthenticated,
    isAdmin,
    esSuperAdmin,
    esAdmin,
    esAdminOSuperAdmin,
    esTrabajador,
    debeCambiarPassword,
    login,
    logout,
    refreshToken,
  }
})