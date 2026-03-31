<!-- HistorialView.vue — Historial de marcaciones del trabajador -->
<!-- Lista vertical con fecha, hora, tipo y estado -->
<!-- Ordenado del más reciente al más antiguo -->

<template>
  <div class="historial">

    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-usuario"><img :src="iconoPerfil" class="icono-perfil" />{{ auth.usuario?.nombre_completo }}</span>
        <button @click="theme.toggle()" class="btn-tema" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">{{ theme.oscuro ? '☀️' : '🌙' }}</button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <!-- CONTENIDO -->
    <main class="main">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Historial de Marcaciones</h2>
      </div>

      <!-- CARGANDO -->
      <div v-if="cargando" class="cargando">Cargando...</div>

      <!-- ERROR -->
      <div v-else-if="error" class="error">{{ error }}</div>

      <!-- LISTA -->
      <div v-else-if="marcaciones.length > 0" class="lista">
        <div v-for="m in marcaciones" :key="m.id" class="marcacion-item">
          <div class="marcacion-fecha">
            <span class="fecha">{{ formatearFecha(m.fecha) }}</span>
            <span class="hora">{{ formatearHora(m.fecha) }}</span>
          </div>
          <div class="marcacion-badges">
            <span :class="['badge', m.tipo === 'ENTRADA' ? 'badge-entrada' : 'badge-salida']">
              {{ m.tipo }}
            </span>
            <span v-if="m.estado" :class="['badge', m.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']">
              {{ m.estado }}
            </span>
          </div>
        </div>
      </div>

      <!-- SIN MARCACIONES -->
      <div v-else class="vacio">
        No hay marcaciones registradas
      </div>

    </main>
  </div>
</template>

<script setup>
import iconoPerfil from '@/assets/icon-perfil.svg'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const marcaciones = ref([])
const cargando = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const trabajadorId = auth.usuario?.trabajador_id
    const response = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
    marcaciones.value = response.data
  } catch (e) {
    error.value = 'Error al cargar el historial'
  } finally {
    cargando.value = false
  }
})

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-PE', {
    year: 'numeric', month: '2-digit', day: '2-digit'
  })
}

function formatearHora(fecha) {
  return new Date(fecha).toLocaleTimeString('es-PE', {
    hour: '2-digit', minute: '2-digit'
  })
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>

.icono-perfil {
  width: 20px;
  height: 20px;
  margin-right: 6px;
}


.historial {
  min-height: 100vh;
  background-color: #f0f4f8;
  display: flex;
  flex-direction: column;
}

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
  width: 180px;
  height: 60px;
  object-fit: contain;
}

.sistema-nombre {
  color: white;
  font-weight: bold;
  font-size: 1.4em;
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

.main {
  flex: 1;
  padding: 32px 24px;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}

.titulo-seccion {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-volver {
  background: none;
  border: none;
  color: #1a3a6b;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
}

h2 {
  font-size: 1.3rem;
  color: #1a3a6b;
}

.lista {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.marcacion-item {
  background: white;
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.marcacion-fecha {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.fecha {
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}

.hora {
  font-size: 0.85rem;
  color: #666;
}

.marcacion-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}

.badge-entrada { background: #dbeafe; color: #1d4ed8; }
.badge-salida { background: #f3f4f6; color: #374151; }
.badge-puntual { background: #dcfce7; color: #16a34a; }
.badge-tardanza { background: #fef9c3; color: #ca8a04; }

.cargando, .vacio {
  text-align: center;
  color: #666;
  padding: 40px;
}

.error {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}
</style>