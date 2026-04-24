// auth.js — Store de autenticación con Pinia
// Cada pestaña tiene su propia sesión independiente via sessionStorage
// Esto permite que un admin y un trabajador estén logueados en pestañas distintas
// Las URLs del backend se leen desde VITE_API_URL (sin hardcodear)

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL

// Clave única por pestaña usando sessionStorage
// sessionStorage es por pestaña — no se comparte entre ellas
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

  // Cargar sesión existente de esta pestaña al iniciar
  const sesionGuardada = cargarSesion()

  const token = ref(sesionGuardada?.token || null)
  const refreshTokenValue = ref(sesionGuardada?.refreshToken || null)
  const usuario = ref(sesionGuardada?.usuario || null)

  // COMPUTED
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => usuario.value?.rol === 'ADMIN')
  const esTrabajador = computed(() => usuario.value?.rol === 'TRABAJADOR')
  const debeCambiarPassword = computed(() => usuario.value?.debe_cambiar_password)

  // LOGIN — llama al backend y guarda en memoria + sessionStorage de esta pestaña
  async function login(username, password) {
    const response = await axios.post(`${BASE_URL}/api/auth/login/`, {
      username,
      password
    })

    token.value = response.data.access
    refreshTokenValue.value = response.data.refresh
    usuario.value = {
      ...response.data.usuario,
      debe_cambiar_password: response.data.debe_cambiar_password
    }

    // Persistir en sessionStorage (solo esta pestaña)
    guardarSesion({
      token: token.value,
      refreshToken: refreshTokenValue.value,
      usuario: usuario.value
    })

    return response.data
  }

  // LOGOUT — limpia memoria y sessionStorage de esta pestaña
  async function logout() {
    try {
      if (refreshTokenValue.value) {
        await axios.post(`${BASE_URL}/api/auth/logout/`, {
          refresh: refreshTokenValue.value
        }, {
          headers: { Authorization: `Bearer ${token.value}` }
        })
      }
    } catch {}
    finally {
      token.value = null
      refreshTokenValue.value = null
      usuario.value = null
      limpiarSesion()
    }
  }

  // REFRESH TOKEN — renueva el access token y actualiza sessionStorage
  async function refreshToken() {
    const response = await axios.post(`${BASE_URL}/api/auth/token/refresh/`, {
      refresh: refreshTokenValue.value
    })
    token.value = response.data.access

    // Actualizar token en sessionStorage
    guardarSesion({
      token: token.value,
      refreshToken: refreshTokenValue.value,
      usuario: usuario.value
    })
  }

  return {
    token,
    usuario,
    isAuthenticated,
    isAdmin,
    esTrabajador,
    debeCambiarPassword,
    login,
    logout,
    refreshToken
  }
})