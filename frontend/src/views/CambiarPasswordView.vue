<!-- CambiarPasswordView.vue — Forzar cambio de contraseña -->
<!-- Se muestra cuando debe_cambiar_password = true -->
<!-- Al cambiar exitosamente redirige según el rol -->

<template>
  <div class="cambiar-page">
    <div class="cambiar-card">

      <img src="/logo-2.webp" alt="Logo Municipalidad" class="logo" />
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

<style scoped>
.cambiar-page {
  min-height: 100vh;
  background-color: #1a3a6b;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.cambiar-card {
  background: white;
  border-radius: 12px;
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
  font-size: 1.2rem;
  color: #1a3a6b;
  font-weight: bold;
}

.subtitulo {
  font-size: 0.85rem;
  color: #666;
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
  font-size: 0.85rem;
  font-weight: 600;
  color: #1a3a6b;
  margin-bottom: 6px;
}

.campo input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  box-sizing: border-box;
}

.campo input:focus {
  border-color: #1a3a6b;
}

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  border: 1px solid #fecaca;
}

.exito {
  background: #f0fdf4;
  color: #16a34a;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  border: 1px solid #bbf7d0;
}

.btn-cambiar {
  width: 100%;
  padding: 12px;
  background-color: #1a3a6b;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cambiar:hover:not(:disabled) {
  background-color: #142d54;
}

.btn-cambiar:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>