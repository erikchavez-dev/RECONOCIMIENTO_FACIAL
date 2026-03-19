<!-- DashboardView.vue — Panel principal del administrador -->
<!-- Muestra estadísticas del día y mes actual -->
<!-- Gráfico de dona con puntualidad del mes -->

<template>
  <AdminLayout titulo="Dashboard">

    <!-- TARJETAS DE ESTADÍSTICAS -->
    <div v-if="cargando" class="cargando">Cargando estadísticas...</div>

    <div v-else>
      <div class="tarjetas">

        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            TRABAJADORES TOTALES
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconoTrabajadores" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.trabajadores?.total_activos }}</span>
              <span class="tarjeta-label">Trabajadores activos</span>
            </div>
          </div>
        </div>

        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            EMBEDDINGS  
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconoCheck" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.trabajadores?.con_embedding }}</span>
              <span class="tarjeta-label">Embeddings registrados</span>
            </div>
          </div>
        </div>

        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            ENTRADAS   
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconoEntrada" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.hoy?.entradas }}</span>
              <span class="tarjeta-label">Entradas de hoy</span>
            </div>
          </div>
        </div>

        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            TARDANZAS 
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconoTardanza" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.hoy?.tardanzas }}</span>
              <span class="tarjeta-label">Tardanzas de hoy</span>
            </div>
          </div>
        </div>

        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            SIN MARCAR 
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconoSinMarcar" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.hoy?.sin_marcar }}</span>
              <span class="tarjeta-label">Sin marcar hoy</span>
            </div>
          </div>
        </div>
        
        <div class="tarjeta-contenedor">
          <div class="tarjeta-titulo">
            PORCENTAJE
          </div>
          <div class="tarjeta-cuerpo">
            <img :src="iconPuntualidad" alt="trabajadores" class="tarjeta-icono" />
            <div class="tarjeta-info">
              <span class="tarjeta-valor">{{ stats.mes_actual?.porcentaje_puntualidad }}%</span>
              <span class="tarjeta-label">Puntualidad del mes</span>
            </div>
          </div>
        </div>

      </div>

      <!-- GRÁFICO DONA -->
      <div class="grafico-seccion">
        <h3>Puntualidad del Mes — {{ stats.mes_actual?.mes }}</h3>
        <div class="grafico-container">
          <svg viewBox="0 0 200 200" class="dona">
            <!-- Fondo gris -->
            <circle cx="100" cy="100" r="70" fill="none" stroke="#e5e7eb" stroke-width="30"/>
            <!-- Porcentaje puntual (verde) -->
            <circle
              cx="100" cy="100" r="70"
              fill="none"
              stroke="#22c55e"
              stroke-width="30"
              stroke-dasharray="439.82"
              :stroke-dashoffset="439.82 - (439.82 * (stats.mes_actual?.porcentaje_puntualidad || 0) / 100)"
              stroke-linecap="round"
              transform="rotate(-90 100 100)"
            />
            <!-- Texto central -->
            <text x="100" y="95" text-anchor="middle" font-size="28" font-weight="bold" fill="#1a3a6b">
              {{ stats.mes_actual?.porcentaje_puntualidad }}%
            </text>
            <text x="100" y="118" text-anchor="middle" font-size="11" fill="#666">
              Puntual
            </text>
          </svg>

          <div class="leyenda">
            <div class="leyenda-item">
              <span class="leyenda-color" style="background:#22c55e"></span>
              <span>Puntual {{ stats.mes_actual?.puntuales }}</span>
            </div>
            <div class="leyenda-item">
              <span class="leyenda-color" style="background:#f59e0b"></span>
              <span>Tardanza {{ stats.mes_actual?.tardanzas }}</span>
            </div>
            <div class="leyenda-item">
              <span class="leyenda-color" style="background:#e5e7eb"></span>
              <span>Total entradas {{ stats.mes_actual?.total_entradas }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>

  </AdminLayout>
</template>

<script setup>
import iconoTrabajadores from '@/assets/icono-trabajadores.svg'
import iconoCheck from '@/assets/icon-check.svg'
import iconoEntrada from '@/assets/icon-entrada.svg'
import iconoTardanza from '@/assets/icon-tarde.svg'
import iconoSinMarcar from '@/assets/icon-sin-marcar.svg'
import iconPuntualidad from '@/assets/icon-puntualidad.svg'
import { ref, onMounted } from 'vue'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

const stats = ref({})
const cargando = ref(true)

onMounted(async () => {
  try {
    const response = await api.get('/api/marcaciones/estadisticas/')
    stats.value = response.data
  } catch (e) {
    console.error('Error cargando estadísticas:', e)
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.cargando {
  text-align: center;
  color: #666;
  padding: 40px;
}

.tarjetas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.tarjeta {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tarjeta-icono {
  height: 28px;
  width: 28px;
  
}

.tarjeta-info {
  display: flex;
  flex-direction: column;
}

.tarjeta-valor {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1a3a6b;
  line-height: 1;
}

.tarjeta-label {
  font-size: 0.78rem;
  color: #666;
  margin-top: 4px;
}

/* GRÁFICO */
.grafico-seccion {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.grafico-seccion h3 {
  font-size: 1rem;
  color: #1a3a6b;
  margin-bottom: 20px;
}

.grafico-container {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.dona {
  width: 180px;
  height: 180px;
}

.leyenda {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.leyenda-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #444;
}

.leyenda-color {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  flex-shrink: 0;
}

/* Contenedor principal con bordes redondeados */
.tarjeta-contenedor {
  background: white;
  border-radius: 8px;
  overflow: hidden; /* Corta el fondo del título para que respete el radio */
  border: 1px solid #e5e7eb;
  box-shadow: 5px 5px 5px 5px hwb(90 45% 55% / 0.1); 
  transition: transform 0.2s ease;
}

.tarjeta-contenedor:hover {
  box-shadow: 0 8px 20px 0 rgba(17, 24, 39, 0.15);
  transform: translateY(-8px);
}

/* Línea del título (Negro o Azul oscuro) */
.tarjeta-titulo {
  background: #1a3a6b; /* Negro azulado muy elegante */
  color: white;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* Espaciado para tu contenido original */
.tarjeta-cuerpo {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Ajustes a tus clases originales para que se vean bien */
.tarjeta-valor {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #111827;
}

.tarjeta-label {
  font-size: 13px;
  color: #6b7280;
}

.tarjeta-icono {
  width: 40px;
  height: 40px;
}


</style>