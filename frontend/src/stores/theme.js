// theme.js — Store de tema claro/oscuro
// Persiste en sessionStorage para mantener preferencia por pestaña

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const oscuro = ref(sessionStorage.getItem('tema') === 'oscuro')

  function aplicarTema() {
    if (oscuro.value) {
      document.documentElement.setAttribute('data-tema', 'oscuro')
    } else {
      document.documentElement.removeAttribute('data-tema')
    }
  }

  function toggle() {
    oscuro.value = !oscuro.value
    sessionStorage.setItem('tema', oscuro.value ? 'oscuro' : 'claro')
    aplicarTema()
  }

  // Aplicar al iniciar
  aplicarTema()

  return { oscuro, toggle }
})