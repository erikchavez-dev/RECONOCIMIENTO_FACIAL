<!-- CambiarPasswordView.vue — Forzar cambio de contraseña -->
<!-- Se muestra cuando debe_cambiar_password = true -->
<!-- Al cambiar exitosamente redirige según el rol -->

<template>
  <div class="cambiar-page">
    <div class="cambiar-card">

      <img :src="IconoLogo" alt="Logo Municipalidad" class="logo" />
      <h2>Cambiar Contraseña</h2>
      <p class="subtitulo">Debe cambiar su contraseña antes de continuar</p>

      <div class="formulario">

        <div class="campo">
          <label>Contraseña actual</label>
          <input
            v-model="passwordActual"
            type="password"
            placeholder="Ingrese su contraseña actual"
          />
        </div>

        <div class="campo">
          <label>Nueva contraseña</label>
          <input
            v-model="passwordNueva"
            type="password"
            placeholder="Mínimo 6 caracteres"
          />
        </div>

        <div class="campo">
          <label>Confirmar nueva contraseña</label>
          <input
            v-model="passwordConfirmar"
            type="password"
            placeholder="Repita la nueva contraseña"
          />
        </div>

        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="exito" class="exito">{{ exito }}</div>

        <button @click="handleCambiar" :disabled="cargando" class="btn-cambiar">
          {{ cargando ? 'Cambiando...' : 'Cambiar contraseña' }}
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import IconoLogo from '/logo-3.webp' 
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'


const router = useRouter()
const auth = useAuthStore()

const passwordActual = ref('')
const passwordNueva = ref('')
const passwordConfirmar = ref('')
const error = ref('')
const exito = ref('')
const cargando = ref(false)

async function handleCambiar() {
  error.value = ''
  exito.value = ''

  if (!passwordActual.value || !passwordNueva.value || !passwordConfirmar.value) {
    error.value = 'Todos los campos son requeridos'
    return
  }

  if (passwordNueva.value.length < 6) {
    error.value = 'La nueva contraseña debe tener mínimo 6 caracteres'
    return
  }

  if (passwordNueva.value !== passwordConfirmar.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  cargando.value = true

  try {
    await api.post('/api/auth/cambiar-password/', {
      password_actual: passwordActual.value,
      password_nueva: passwordNueva.value
    })

    // Actualizar en el store
    auth.usuario.debe_cambiar_password = false
    exito.value = 'Contraseña cambiada correctamente. Redirigiendo...'

    setTimeout(() => {
      if (auth.isAdmin) {
        router.push('/admin/dashboard')
      } else {
        router.push('/trabajador/panel')
      }
    }, 1500)

  } catch (e) {
    error.value = e.response?.data?.error || 'Error al cambiar la contraseña'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped src="./style.css"></style>