// auth.js — Store de autenticación con Pinia
// Guarda en memoria: token, datos del usuario y rol
// NO usa localStorage por seguridad en PWA
// Maneja login, logout y renovación de token

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {

  // ESTADO — datos en memoria
  const token = ref(null)          // access token JWT (8 horas)
  const refreshTokenValue = ref(null) // refresh token (1 día)
  const usuario = ref(null)        // datos del usuario logueado

  // COMPUTED — valores derivados del estado
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => usuario.value?.rol === 'ADMIN')
  const esTrabajador = computed(() => usuario.value?.rol === 'TRABAJADOR')
  const debeCambiarPassword = computed(() => usuario.value?.debe_cambiar_password)

  //PARA LA IP
  const BASE_URL = import.meta.env.VITE_API_URL

  // LOGIN — llama al backend y guarda los tokens en memoria
  async function login(username, password) {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
      username,
      password
    })

    token.value = response.data.access
    refreshTokenValue.value = response.data.refresh
    usuario.value = {
      ...response.data.usuario,
      debe_cambiar_password: response.data.debe_cambiar_password
    }

    return response.data
  }

  // LOGOUT — limpia todo de memoria y llama al backend
  async function logout() {
    try {
      if (refreshTokenValue.value) {
        await axios.post('http://127.0.0.1:8000/api/auth/logout/', {
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
    }
  }

  // REFRESH TOKEN — renueva el access token cuando expira
  async function refreshToken() {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/token/refresh/', {
      refresh: refreshTokenValue.value
    })
    token.value = response.data.access
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