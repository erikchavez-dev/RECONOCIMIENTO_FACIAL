// Maneja el mini-calendario del panel: mes/año reactivos, navegación
// entre meses y carga de feriados nacionales de Perú.
// la api que estoy usando se llama Nager Date API

import { ref, computed } from 'vue'

const MESES_ES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

// Caché en memoria — persiste durante la sesión sin volver a pedir la API
const feriadosCache = {}

export function useCalendario() {
  const mesCalendario  = ref(new Date().getMonth())
  const anioCalendario = ref(new Date().getFullYear())
  const feriadosSet    = ref({ set: new Set(), names: {} })

  const nombreMes = computed(() => MESES_ES[mesCalendario.value])

  async function cargarFeriados(anio) {
    if (feriadosCache[anio]) {
      feriadosSet.value = feriadosCache[anio]
      return
    }
    try {
      const res  = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${anio}/PE`)
      const data = await res.json()
      const set   = new Set()
      const names = {}
      data.forEach(f => { set.add(f.date); names[f.date] = f.localName })
      feriadosCache[anio] = { set, names }
      feriadosSet.value   = { set, names }
    } catch {
      feriadosSet.value = { set: new Set(), names: {} }
    }
  }

  const diasCalendario = computed(() => {
    const primer  = new Date(anioCalendario.value, mesCalendario.value, 1)
    const ultimo  = new Date(anioCalendario.value, mesCalendario.value + 1, 0)
    const inicio  = (primer.getDay() + 6) % 7   // lunes = 0
    const hoy     = new Date()
    const hoyStr  = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-${String(hoy.getDate()).padStart(2, '0')}`
    const dias    = []

    // Celdas vacías al principio para alinear con el día de la semana
    for (let i = 0; i < inicio; i++) dias.push({ vacio: true })

    for (let d = 1; d <= ultimo.getDate(); d++) {
      const mm        = String(mesCalendario.value + 1).padStart(2, '0')
      const dd        = String(d).padStart(2, '0')
      const fs        = `${anioCalendario.value}-${mm}-${dd}`
      const diaSemana = new Date(anioCalendario.value, mesCalendario.value, d).getDay()
      const esFeriado = feriadosSet.value?.set?.has(fs)
      dias.push({
        num:          d,
        vacio:        false,
        esHoy:        fs === hoyStr,
        feriado:      esFeriado,
        nombreFeriado: esFeriado ? (feriadosSet.value?.names?.[fs] || 'Feriado') : '',
        domingo:      diaSemana === 0,
      })
    }
    return dias
  })

  function mesAnterior() {
    if (mesCalendario.value === 0) { mesCalendario.value = 11; anioCalendario.value-- }
    else mesCalendario.value--
    cargarFeriados(anioCalendario.value)
  }

  function mesSiguiente() {
    if (mesCalendario.value === 11) { mesCalendario.value = 0; anioCalendario.value++ }
    else mesCalendario.value++
    cargarFeriados(anioCalendario.value)
  }

  return {
    mesCalendario,
    anioCalendario,
    nombreMes,
    diasCalendario,
    cargarFeriados,
    mesAnterior,
    mesSiguiente,
  }
}