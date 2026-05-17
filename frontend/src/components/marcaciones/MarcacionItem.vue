// Renderiza una fila del historial de marcaciones.
// Encapsula la lógica de tipos (ENTRADA_VALIDA, SALIDA_VALIDA, FUERA_HORARIO,
// SOLO_VERIFICACION)

<template>
  <div class="marcacion-item">
    <div :class="['item-icono', claseIcono]">
      {{ icono }}
    </div>
    <div class="item-fecha">
      <span class="fecha-txt">{{ formatearFecha(marcacion.fecha) }}</span>
      <span class="hora-txt">{{ formatearHora(marcacion.fecha) }}</span>
    </div>
    <div class="item-badges">
      <span :class="['badge', claseBadge]">
        {{ etiqueta }}
      </span>
      <span
        v-if="marcacion.estado"
        :class="['badge', marcacion.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']"
      >
        {{ marcacion.estado }}
      </span>
    </div>
  </div>
</template>

<script setup>

import { computed } from 'vue'
import { useFecha } from '@/composables/useFecha'

const props = defineProps({
  marcacion: {
    type: Object,
    required: true,
  },
})

const { formatearFecha, formatearHora } = useFecha()

const TIPOS_ENTRADA = ['ENTRADA_VALIDA', 'ENTRADA']
const TIPOS_SALIDA  = ['SALIDA_VALIDA',  'SALIDA']


const ETIQUETAS = {
  ENTRADA_VALIDA:    'ENTRADA',
  SALIDA_VALIDA:     'SALIDA',
  ENTRADA:           'ENTRADA',
  SALIDA:            'SALIDA',
  FUERA_HORARIO:     'FUERA DE HORARIO',
  SOLO_VERIFICACION: 'VERIFICACION',
}

const claseIcono = computed(() => {
  if (TIPOS_ENTRADA.includes(props.marcacion.tipo)) return 'icono-entrada'
  if (TIPOS_SALIDA.includes(props.marcacion.tipo))  return 'icono-salida'
  return 'icono-fuera'
})

const icono = computed(() => {
  if (TIPOS_ENTRADA.includes(props.marcacion.tipo)) return '↗'
  if (TIPOS_SALIDA.includes(props.marcacion.tipo))  return '↙'
  return '○'
})

const claseBadge = computed(() => {
  if (TIPOS_ENTRADA.includes(props.marcacion.tipo)) return 'badge-entrada'
  if (TIPOS_SALIDA.includes(props.marcacion.tipo))  return 'badge-salida'
  return 'badge-fuera'
})

const etiqueta = computed(() =>
  ETIQUETAS[props.marcacion.tipo] || props.marcacion.tipo
)
</script>

<style scoped>
/* ── ITEM DE MARCACIÓN ── */
.marcacion-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.marcacion-item:hover {
  transform: translateX(5px);
  border-color: var(--accent);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
}

:global(.panel.light) .marcacion-item {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:global(.panel.light) .marcacion-item:hover {
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

/* ── ÍCONO LATERAL ── */
.item-icono {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 800;
  flex-shrink: 0;
}

.icono-entrada {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}

.icono-salida {
  background: rgba(148, 163, 184, 0.12);
  color: var(--text-soft);
  border: 1px solid var(--border-color);
}

.icono-fuera {
  background: #f8f2f2;
  color: #ffae27;
  border: 1px solid rgba(251, 191, 36, 0.25);
}

:global(.panel.light) .icono-entrada {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #bfdbfe;
}

:global(.panel.light) .icono-salida {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

:global(.panel.light) .icono-fuera {
  background: #fef9c3;
  color: #b45309;
  border-color: #fde68a;
}

/* ── FECHA Y HORA ── */
.item-fecha {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.fecha-txt {
  font-size: 1.03em;
  color: var(--text-main);
  font-weight: 600;
}

.hora-txt {
  font-size: 1rem;
  font-weight: 700;
  color: #07d854;
  letter-spacing: 0.5px;
}

/* ── BADGES ── */
.item-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.badge {
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.73rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* oscuro */
.badge-entrada {
  background: #f8f2f2;
  padding: 10px;
  border-radius: 7px;
  color: #1a3a6b;
}

.badge-salida {
  background: #f8f2f2;
  color: #1a3a6b;
}

.badge-puntual {
  background: #f8f2f2;
  padding: 10px;
  border-radius: 7px;
  color: #4ade80;

}

.badge-tardanza {

  background: rgba(251, 191, 36, 0.18);
  color: #fbbf24;
}

.badge-fuera {
  background: #f8f2f2;
  padding: 10px;
  border-radius: 7px;
  color: #ffae00;
}

/* claro */
:global(.panel.light) .badge-entrada {
  background: #dbeafe;
  color: #1d4ed8;
}

:global(.panel.light) .badge-salida {
  background: #f3f4f6;
  color: #513737;
}

:global(.panel.light) .badge-puntual {
  background: #dcfce7;
  color: #16a34a;
}

:global(.panel.light) .badge-tardanza {
  background: #fef9c3;
  color: #ca8a04;
}

:global(.panel.light) .badge-fuera {
  background: #fef9c3;
  color: #b45309;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .marcacion-item {
    padding: 12px 14px;
    gap: 12px;
    border-radius: 12px;
  }

  .marcacion-item:hover {
    transform: none;
  }

  .item-icono {
    width: 36px;
    height: 36px;
    font-size: 0.95rem;
    border-radius: 10px;
  }

  .fecha-txt {
    font-size: 0.82rem;
  }

  .hora-txt {
    font-size: 0.88rem;
  }

  .badge {
    font-size: 0.65rem;
    padding: 4px 10px;
  }

  .item-badges {
    gap: 6px;
  }
}
</style>