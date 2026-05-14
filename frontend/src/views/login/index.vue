<!-- LoginView.vue — Pantalla de login -->
<!-- Formulario centrado con logo, campos DNI y contraseña -->
<!-- Al hacer login redirige según el rol del usuario -->

<template>
  <div class="login-image">
    <div class="login-card">

      <!-- LOGO -->
      <img src="/logo-4.webp" alt="Logo Municipalidad" class="logo" />
      <h2>Sistema de Control de Asistencia</h2>
      <p class="subtitulo">Municipalidad Provincial de Cajamarca</p>

      <!-- FORMULARIO -->
      <div class="formulario">

        <div class="campo">
          <label>Usuario</label>
          <div class="input-wrapper">
            <img :src="iconoUsuario" alt="usuario" class="icono-input" />
            <input
            v-model="username"
            type="text"
            placeholder="Ingrese su DNI"
            maxlength="8"
            autocomplete="username"
            name="username"
            @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <div class="campo">
          <label>Contraseña</label>
          <div class="password-wrapper">
            <input
              v-model="password"
              :type="mostrarPassword ? 'text' : 'password'"
              placeholder="Ingrese su contraseña"
              autocomplete="current-password"
              name="password"
              @keyup.enter="handleLogin"
            />
            <button
              class="toggle-password"
              @click.prevent="mostrarPassword = !mostrarPassword"
              type="button"
            >
              <!-- Uso v-if/v-else para forzar el cambio de icono -->
              <img v-if="mostrarPassword" :src="ojoAbierto" alt="Ocultar contraseña" />
              <img v-else :src="ojoCerrado" alt="Mostrar contraseña" />
            </button>
          </div>
        </div>

        <!-- ERROR -->
        <div v-if="error" class="error">
          {{ error }}
        </div>

        <!-- BOTÓN -->
        <button @click="handleLogin" :disabled="cargando" class="btn-ingresar">
          {{ cargando ? 'Ingresando...' : 'Ingresar' }}
        </button>
        <button @click="$router.push('/')" class="btn-inicio">
          Volver a Inicio
        </button>

      </div>
    </div>
  </div>
</template>

<script setup>
import ojoAbierto from '@/assets/ojo-abierto.svg'
import ojoCerrado from '@/assets/ojo-cerrado.svg'
import iconoUsuario from '@/assets/icono-usuario.svg'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)
const mostrarPassword = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Ingrese su usuario y contraseña'
    return
  }

  cargando.value = true
  error.value = ''

  try {
    const data = await auth.login(username.value, password.value)

    if (data.debe_cambiar_password) {
      router.push('/cambiar-password')
      return
    }

    if (data.usuario.rol === 'ADMIN') {
      router.push('/admin/dashboard')
    } else {
      router.push('/trabajador/panel')
    }

  } catch (e) {
    error.value = e.response?.data?.error || 'Error al iniciar sesión'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped src="./style.css"></style>