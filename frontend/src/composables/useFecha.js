// Centraliza todo el formateo de fechas/horas y las clases CSS
// de resultado de asistencia, que se repiten en Historial, Asistencia y MarcarView.

import { computed } from 'vue'

export function useFecha() {

  // Fecha y hora actual formateada — usada en MarcarView (confirmación)
  const fechaHoraActual = computed(() =>
    new Date().toLocaleString('es-PE', {
      weekday: 'long', year: 'numeric', month: 'long',
      day: 'numeric', hour: '2-digit', minute: '2-digit',
    })
  )

  // Fecha larga con día de semana — usada en Historial
  // Ejemplo: "lun., 21/04/2025"
  function formatearFecha(fecha) {
    return new Date(fecha).toLocaleDateString('es-PE', {
      weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit',
    })
  }

  // Solo hora y minutos — usada en Historial
  // Ejemplo: "08:05"
  function formatearHora(fecha) {
    return new Date(fecha).toLocaleTimeString('es-PE', {
      hour: '2-digit', minute: '2-digit',
    })
  }

  // Fecha corta desde string YYYY-MM-DD — usada en Asistencia
  // Ejemplo: "21/04/2025"
  function formatearFechaCorta(fechaStr) {
    const [y, m, d] = fechaStr.split('-')
    return `${d}/${m}/${y}`
  }

  // Clase CSS según resultado de asistencia — usada en Asistencia
  // Valores posibles del backend:
  // 'ASISTIÓ' | 'TARDANZA' | 'FALTA' | 'INCOMPLETO' | 'PENDIENTE' | 'NO_LABORABLE'
  function claseResultado(resultado) {
    const clases = {
      'ASISTIÓ':      'res-asistio',
      'TARDANZA':     'res-tardanza',
      'FALTA':        'res-falta',
      'INCOMPLETO':   'res-incompleto',
      'PENDIENTE':    'res-pendiente',
      'NO_LABORABLE': 'res-no-laborable',
    }
    return clases[resultado] || 'res-falta'
  }

  return {
    fechaHoraActual,
    formatearFecha,
    formatearHora,
    formatearFechaCorta,
    claseResultado,
  }
}