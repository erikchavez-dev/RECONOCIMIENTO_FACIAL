<!-- MarcacionesView.vue — Marcaciones del día actual -->
<!-- Tabla con todas las marcaciones de hoy -->

<template>
  <AdminLayout titulo="Marcaciones de hoy">

    <div class="toolbar">
      <div>
        <h3>Marcaciones de Hoy</h3>
        <p class="fecha">Fecha: {{ fechaHoy }}</p>
      </div>
      <button @click="cargarMarcaciones" class="btn-actualizar">Actualizar</button>
    </div>

    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando...</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Trabajador</th>
            <th>DNI</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Hora</th>
            <th>Dispositivo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="marcaciones.length === 0">
            <td colspan="6" class="vacio">No hay marcaciones hoy</td>
          </tr>
          <tr v-for="m in marcaciones" :key="m.id">
            <td>{{ m.trabajador_nombre }}</td>
            <td>{{ m.dni }}</td>
            <td>
              <span :class="['badge', m.tipo === 'ENTRADA' ? 'badge-entrada' : 'badge-salida']">
                {{ m.tipo }}
              </span>
            </td>
            <td>
              <span v-if="m.estado" :class="['badge', m.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']">
                {{ m.estado }}
              </span>
              <span v-else>—</span>
            </td>
            <td>{{ formatearHora(m.fecha) }}</td>
            <td>{{ m.dispositivo }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const marcaciones = ref([])
const cargando = ref(true)

const fechaHoy = computed(() => {
  return new Date().toLocaleDateString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  })
})

onMounted(async () => {
  await cargarMarcaciones()
})

async function cargarMarcaciones() {
  cargando.value = true
  try {
    const response = await api.get('/api/marcaciones/hoy/')
    marcaciones.value = response.data.marcaciones
  } catch (e) {
    console.error('Error cargando marcaciones:', e)
  } finally {
    cargando.value = false
  }
}

function formatearHora(fecha) {
  return new Date(fecha).toLocaleTimeString('es-PE', {
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar h3 {
  font-size: 1.1rem;
  color: #1a3a6b;
}

.fecha {
  font-size: 0.85rem;
  color: #666;
  margin-top: 4px;
}

.btn-actualizar {
  background: #1a3a6b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-actualizar:hover { background: #142d54; }

.tabla-container {
  background: white;
  border-radius: 12px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.tabla th {
  background: #1a3a6b;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.tabla td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.tabla tr:hover { background: #f8fafc; }

.vacio {
  text-align: center;
  color: #666;
  padding: 40px !important;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}

.badge-entrada { background: #dbeafe; color: #1d4ed8; }
.badge-salida { background: #f3f4f6; color: #374151; }
.badge-puntual { background: #dcfce7; color: #16a34a; }
.badge-tardanza { background: #fef9c3; color: #ca8a04; }

.cargando {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>