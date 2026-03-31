<template>
  <div class="asistencia">

    <!-- HEADER -->
    <header class="header">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-usuario">
          <img :src="iconoPerfil" class="icono-perfil" />
          {{ auth.usuario?.nombre_completo }}
        </span>
        <button @click="theme.toggle()" class="btn-tema" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">{{ theme.oscuro ? '☀️' : '🌙' }}</button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="main">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Asistencia</h2>
      </div>

      <!-- FILTROS -->
      <div class="filtros-card">
        <div class="filtros">
          <div class="campo">
            <label>Desde</label>
            <input v-model="fechaInicio" type="date" />
          </div>
          <div class="campo">
            <label>Hasta</label>
            <input v-model="fechaFin" type="date" />
          </div>
          <button @click="cargar" :disabled="cargando" class="btn-buscar">
            {{ cargando ? 'Cargando...' : 'Buscar' }}
          </button>
        </div>
      </div>

      <!-- RESUMEN -->
      <div v-if="datos" class="resumen-grid">
        <div class="resumen-card verde">
          <span class="res-valor">{{ datos.resumen.asistencias }}</span>
          <span class="res-label">Asistencias</span>
        </div>
        <div class="resumen-card amarillo">
          <span class="res-valor">{{ datos.resumen.tardanzas }}</span>
          <span class="res-label">Tardanzas</span>
        </div>
        <div class="resumen-card rojo">
          <span class="res-valor">{{ datos.resumen.faltas }}</span>
          <span class="res-label">Faltas</span>
        </div>
        <div class="resumen-card azul">
          <span class="res-valor">{{ datos.resumen.total_dias }}</span>
          <span class="res-label">Días registrados</span>
        </div>
      </div>

      <!-- TABLA -->
      <div v-if="datos" class="tabla-card">
        <div v-if="datos.dias.length === 0" class="vacio">
          No hay registros en este período
        </div>

        <table v-else class="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Entrada</th>
              <th>Salida</th>
              <th>Tiempo trabajado</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dia in datos.dias" :key="dia.fecha">
              <!-- FECHA -->
              <td class="celda-fecha">
                <span class="dia-semana">{{ dia.dia_semana }}</span>
                <span class="dia-fecha">{{ formatearFechaCorta(dia.fecha) }}</span>
              </td>

              <!-- ENTRADA -->
              <td>
                <div v-if="dia.entrada_hora" class="celda-marcacion">
                  <span :class="['chip', dia.entrada_estado === 'PUNTUAL' ? 'chip-p' : 'chip-t']">
                    {{ dia.entrada_estado === 'PUNTUAL' ? 'P' : 'T' }}
                  </span>
                  <span class="hora-texto">{{ dia.entrada_hora }}</span>
                </div>
                <span v-else class="sin-dato">—</span>
              </td>

              <!-- SALIDA -->
              <td>
                <div v-if="dia.salida_hora" class="celda-marcacion">
                  <span class="chip chip-s">S</span>
                  <span class="hora-texto">{{ dia.salida_hora }}</span>
                </div>
                <span v-else class="sin-dato">—</span>
              </td>

              <!-- TIEMPO TRABAJADO -->
              <td>
                <span v-if="dia.tiempo_trabajado" class="tiempo-trabajado">
                  {{ dia.tiempo_trabajado }}
                </span>
                <span v-else class="sin-dato">—</span>
              </td>

              <!-- RESULTADO -->
              <td>
                <span :class="['resultado-chip', claseResultado(dia.resultado)]">
                  {{ dia.resultado }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="cargando" class="cargando">Cargando...</div>

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

const datos = ref(null)
const cargando = ref(false)

// Fechas por defecto: mes actual
const hoy = new Date()
const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
const fechaInicio = ref(primerDia.toISOString().split('T')[0])
const fechaFin = ref(hoy.toISOString().split('T')[0])

onMounted(() => cargar())

async function cargar() {
  cargando.value = true
  try {
    const response = await api.get('/api/marcaciones/asistencia/', {
      params: { fecha_inicio: fechaInicio.value, fecha_fin: fechaFin.value }
    })
    datos.value = response.data
  } catch (e) {
    console.error('Error cargando asistencia:', e)
  } finally {
    cargando.value = false
  }
}

function formatearFechaCorta(fechaStr) {
  const [y, m, d] = fechaStr.split('-')
  return `${d}/${m}/${y}`
}

function claseResultado(resultado) {
  if (resultado === 'ASISTIÓ') return 'res-asistio'
  if (resultado === 'TARDANZA') return 'res-tardanza'
  if (resultado === 'SIN SALIDA') return 'res-sin-salida'
  return 'res-falta'
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.asistencia {
  min-height: 100vh;
  background: #f0f4f8;
  display: flex;
  flex-direction: column;
}

/* HEADER */
.header {
  background: #1a3a6b;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.header-right { display: flex; align-items: center; gap: 16px; }
.logo { width: 180px; height: 60px; object-fit: contain; }
.sistema-nombre { color: white; font-weight: bold; font-size: 1.1em; }
.nombre-usuario { color: white; font-size: 0.9rem; display: flex; align-items: center; gap: 6px; }
.icono-perfil { width: 20px; height: 20px; }
.btn-logout {
  background: transparent; border: 1px solid white; color: white;
  padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.85rem;
}
.btn-logout:hover { background: white; color: #1a3a6b; }

/* MAIN */
.main {
  flex: 1;
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.titulo-seccion {
  display: flex; align-items: center; gap: 16px; margin-bottom: 20px;
}
.btn-volver {
  background: none; border: none; color: #1a3a6b;
  font-size: 1rem; cursor: pointer; font-weight: 600;
}
h2 { font-size: 1.3rem; color: #1a3a6b; }

/* FILTROS */
.filtros-card {
  background: white; border-radius: 10px; padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 20px;
}
.filtros { display: flex; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.campo { display: flex; flex-direction: column; gap: 4px; }
.campo label { font-size: 0.78rem; font-weight: 600; color: #1a3a6b; }
.campo input {
  padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px;
  font-size: 0.88rem;
}
.campo input:focus { outline: none; border-color: #1a3a6b; }
.btn-buscar {
  padding: 8px 20px; background: #1a3a6b; color: white;
  border: none; border-radius: 6px; cursor: pointer; font-size: 0.88rem;
}
.btn-buscar:disabled { opacity: 0.6; cursor: not-allowed; }

/* RESUMEN */
.resumen-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 12px; margin-bottom: 20px;
}
@media (max-width: 600px) { .resumen-grid { grid-template-columns: repeat(2, 1fr); } }

.resumen-card {
  border-radius: 10px; padding: 16px; text-align: center;
  display: flex; flex-direction: column; gap: 4px;
  border-left: 4px solid transparent;
}
.resumen-card.verde   { background: #f0fdf4; border-left-color: #22c55e; }
.resumen-card.amarillo{ background: #fefce8; border-left-color: #f59e0b; }
.resumen-card.rojo    { background: #fef2f2; border-left-color: #ef4444; }
.resumen-card.azul    { background: #eff6ff; border-left-color: #3b82f6; }

.res-valor { font-size: 1.8rem; font-weight: 800; color: #111827; }
.res-label { font-size: 0.75rem; color: #6b7280; font-weight: 500; }

/* TABLA */
.tabla-card {
  background: white; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07); overflow: auto;
}
.tabla { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.tabla th {
  background: #1a3a6b; color: white;
  padding: 12px 16px; text-align: left; font-weight: 600;
}
.tabla td {
  padding: 12px 16px; border-bottom: 1px solid #f0f4f8; color: #333;
}
.tabla tr:hover { background: #f8fafc; }

/* CELDA FECHA */
.celda-fecha { display: flex; flex-direction: column; gap: 2px; }
.dia-semana { font-weight: 700; color: #1a3a6b; font-size: 0.82rem; }
.dia-fecha  { font-size: 0.82rem; color: #6b7280; }

/* CELDA MARCACION */
.celda-marcacion { display: flex; align-items: center; gap: 8px; }

/* CHIPS de P / T / S */
.chip {
  width: 24px; height: 24px; border-radius: 6px;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.75rem; flex-shrink: 0;
}
.chip-p { background: #dcfce7; color: #16a34a; }  /* Puntual - verde */
.chip-t { background: #fef9c3; color: #b45309; }  /* Tardanza - amarillo */
.chip-s { background: #dbeafe; color: #1d4ed8; }  /* Salida - azul */

.hora-texto { font-size: 0.82rem; color: #374151; font-weight: 500; }

/* TIEMPO TRABAJADO */
.tiempo-trabajado {
  font-family: monospace; font-size: 0.88rem;
  color: #1a3a6b; font-weight: 600;
}

/* RESULTADO */
.resultado-chip {
  padding: 3px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 700;
}
.res-asistio   { background: #dcfce7; color: #16a34a; }
.res-tardanza  { background: #fef9c3; color: #b45309; }
.res-sin-salida{ background: #dbeafe; color: #1d4ed8; }
.res-falta     { background: #fee2e2; color: #dc2626; }

.sin-dato { color: #d1d5db; font-size: 0.85rem; }
.vacio    { text-align: center; padding: 40px; color: #9ca3af; }
.cargando { text-align: center; padding: 40px; color: #9ca3af; }
</style>