<!-- LoginView.vue — Pantalla de login -->
<!-- Formulario centrado con logo, campos DNI y contraseña -->
<!-- Al hacer login redirige según el rol del usuario -->

<template>
  <div class="login-image">
    <div class="login-card">

      <!-- LOGO -->
      <img src="/logo-3.webp" alt="Logo Municipalidad" class="logo" />
      <h2>Sistema de Control de Asistencia</h2>
      <p class="subtitulo">Municipalidad Provincial de Cajamarca</p>

      <!-- FORMULARIO -->
      <div class="formulario">

        <div class="campo">
          <label>Usuario (DNI)</label>
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

<style scoped>
.login-image {
  background-image: url('@/assets/login.webp');
  animation: gradient 15s ease infinite;
  overflow: hidden;
  background-size: 110% 110%;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

@keyframes gradient {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-card {
  backdrop-filter: blur(15px);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  z-index: 10;
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 12px;
}

h2 {
  font-size: 1.4rem;
  color: #000000;
  font-weight: bold;
}

.subtitulo {
  font-size: 0.9rem;
  color: #3b3b3b;
  margin-bottom: 24px;
}

.formulario {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.campo label {
  display: block;
  font-size: 1.05rem;
  font-weight: 600;
  color: #000000;
  margin-bottom: 0px;
}

.campo input {
  width: 100%;
  padding: 10px 12px;
  padding-right: 44px; /* espacio para el botón del ojo */
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border 0.2s;
  box-sizing: border-box;
}

.campo input:focus {
  border-color: #1a3a6b;
}

/* --- PASSWORD WRAPPER --- */
.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  
}

.password-wrapper input {
  flex: 1;
  padding-right: 44px; /* evita que el texto quede debajo del ícono */
}

.toggle-password {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  border-radius: 0 6px 6px 0;
}

.toggle-password:focus {
  outline: none;
}

.toggle-password img {
  width: 20px;
  height: 20px;
  display: block;
  pointer-events: none; /* evita que el click lo absorba la imagen */
}

/* --- ERROR --- */
.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  border: 1px solid #fecaca;
}

/* --- BOTONES --- */
.btn-ingresar {
  width: 100%;
  padding: 12px;
  background-color: #0b1af1;
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-ingresar:hover:not(:disabled) {
  background-color: #0004ff;
}

.btn-ingresar:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-inicio {
  width: 100%;
  padding: 12px;
  background-color: #0be5ec;
  color: rgb(3, 3, 3);
  font-weight: 600;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-inicio:hover:not(:disabled) {
  background-color: #00ffff;
}

.btn-inicio:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  width: 100%;
  padding-left: 15px; /* espacio para el ícono */
  box-sizing: border-box;
  justify-content: space-between;
}

.icono-input {
  position: absolute;
  right: 10px;
  width: 18px;
  height: 18px;
  pointer-events: none; /* no interfiere con el input */
}

</style>