<!-- PanelView.vue — Panel principal del trabajador -->
<!-- Muestra dos botones: Marcar Asistencia y Mi Historial -->
<!-- Header con logo, nombre del trabajador y cerrar sesión -->

<template>
  <div class="panel">

    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <img src="/logo-2.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-usuario">👤 {{ auth.usuario?.nombre_completo }}</span>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <!-- CONTENIDO PRINCIPAL -->
    <main class="main">
      <h2 class="bienvenida">Bienvenido, {{ primerNombre, apellido_paterno }}</h2>
      <p class="fecha">{{ fechaHoy }}</p>

      <div class="botones">

        <!-- MARCAR ASISTENCIA -->
        <div class="btn-card" @click="$router.push('/trabajador/marcar')">
          <div class="btn-icono">📷</div>
          <h3>Marcar Asistencia</h3>
          <p>Registrar entrada o salida</p>
        </div>

        <!-- MI HISTORIAL -->
        <div class="btn-card" @click="$router.push('/trabajador/historial')">
          <div class="btn-icono">📋</div>
          <h3>Mi Historial</h3>
          <p>Ver mis marcaciones</p>
        </div>

      </div>
    </main>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

// Solo el primer nombre
const primerNombre = computed(() => {
  return auth.usuario?.nombre_completo?.split(' ')[0] || ''
})

// Fecha actual en español
const fechaHoy = computed(() => {
  return new Date().toLocaleDateString('es-PE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.panel {
  min-height: 100vh;
  background-color: #f0f4f8;
  display: flex;
  flex-direction: column;
}

/* HEADER */
.header {
  background-color: #1a3a6b;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.sistema-nombre {
  color: white;
  font-weight: bold;
  font-size: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nombre-usuario {
  color: white;
  font-size: 0.9rem;
}

.btn-logout {
  background: transparent;
  border: 1px solid white;
  color: white;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: white;
  color: #1a3a6b;
}

/* MAIN */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.bienvenida {
  font-size: 1.5rem;
  color: #1a3a6b;
  margin-bottom: 6px;
}

.fecha {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 40px;
  text-transform: capitalize;
}

.botones {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-card {
  background: white;
  border-radius: 16px;
  padding: 40px 48px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transition: all 0.2s;
  min-width: 200px;
}

.btn-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(26,58,107,0.2);
}

.btn-icono {
  font-size: 3rem;
  margin-bottom: 16px;
}

.btn-card h3 {
  font-size: 1.1rem;
  color: #1a3a6b;
  margin-bottom: 6px;
}

.btn-card p {
  font-size: 0.85rem;
  color: #666;
}
</style>