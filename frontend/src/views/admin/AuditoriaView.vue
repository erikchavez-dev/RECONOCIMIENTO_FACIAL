<!-- AuditoriaView.vue — Registro de auditoría del sistema -->
<!-- Tabla con usuario, acción, descripción, fecha e IP -->

<template>
  <AdminLayout titulo="Auditoría">

    <div class="toolbar">
      <h3>Registro de Auditoría</h3>
      <button @click="cargarAuditoria" class="btn-actualizar">🔄 Actualizar</button>
    </div>

    <div class="tabla-container">
      <div v-if="cargando" class="cargando">Cargando...</div>

      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Acción</th>
            <th>Descripción</th>
            <th>Fecha</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="auditorias.length === 0">
            <td colspan="5" class="vacio">No hay registros de auditoría</td>
          </tr>
          <tr v-for="a in auditorias" :key="a.id">
            <td>{{ a.usuario_nombre }}</td>
            <td>
              <span :class="['badge', getBadgeClass(a.accion)]">
                {{ a.accion }}
              </span>
            </td>
            <td class="descripcion">{{ a.descripcion }}</td>
            <td>{{ formatearFecha(a.fecha) }}</td>
            <td>{{ a.ip }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const auditorias = ref([])
const cargando = ref(true)

onMounted(async () => {
  await cargarAuditoria()
})

async function cargarAuditoria() {
  cargando.value = true
  try {
    const response = await api.get('/api/auditoria/')
    auditorias.value = response.data
  } catch (e) {
    console.error('Error cargando auditoría:', e)
  } finally {
    cargando.value = false
  }
}

function formatearFecha(fecha) {
  return new Date(fecha).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function getBadgeClass(accion) {
  if (accion.includes('LOGIN_EXITOSO')) return 'badge-verde'
  if (accion.includes('LOGIN_FALLIDO')) return 'badge-rojo'
  if (accion.includes('LOGOUT')) return 'badge-gris'
  if (accion.includes('MARCACION')) return 'badge-azul'
  if (accion.includes('VERIFICACION_FALLIDA')) return 'badge-naranja'
  if (accion.includes('CREAR') || accion.includes('REGISTRAR')) return 'badge-verde'
  if (accion.includes('ELIMINAR')) return 'badge-rojo'
  if (accion.includes('CAMBIO') || accion.includes('CONFIGURACION')) return 'badge-amarillo'
  if (accion.includes('BLOQUEAR') || accion.includes('DESBLOQUEAR')) return 'badge-naranja'
  return 'badge-gris'
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

.descripcion {
  max-width: 300px;
  font-size: 0.82rem;
  color: #555;
}

.vacio {
  text-align: center;
  color: #666;
  padding: 40px !important;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-verde { background: #dcfce7; color: #16a34a; }
.badge-rojo { background: #fee2e2; color: #dc2626; }
.badge-azul { background: #dbeafe; color: #1d4ed8; }
.badge-naranja { background: #ffedd5; color: #ea580c; }
.badge-amarillo { background: #fef9c3; color: #ca8a04; }
.badge-gris { background: #f3f4f6; color: #6b7280; }

.cargando {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>