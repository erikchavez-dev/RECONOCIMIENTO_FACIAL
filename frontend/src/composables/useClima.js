// Obtiene el clima actual la api se llama Open Meteo API.

import { ref } from 'vue'
import iconMayorDespejado from '@/assets/icons/clima/mayorDespejado.svg'
import iconDiaSoleado from '@/assets/icons/clima/diaSoleado.svg'
import iconParcialNublado from '@/assets/icons/clima/parcial-nublado.svg'
import iconNublado from '@/assets/icons/clima/nublado.svg'
import iconLlovizna from '@/assets/icons/clima/llovizna.svg'
import iconLluvia from '@/assets/icons/clima/lluvia.svg'
import iconTormenta from '@/assets/icons/clima/tormenta.svg'

// Tabla de códigos meteorológicos WMO → descripción + ícono
const WMO = {
  0:  { d: 'Despejado',             i: iconDiaSoleado },
  1:  { d: 'Mayormente despejado',  i: iconMayorDespejado },
  2:  { d: 'Parcialmente nublado',  i: iconParcialNublado },
  3:  { d: 'Nublado',               i: iconNublado },
  45: { d: 'Neblina',               i: iconNublado },
  51: { d: 'Llovizna',              i: iconLlovizna },
  61: { d: 'Lluvia ligera',         i: iconLluvia },
  63: { d: 'Lluvia moderada',       i: iconLluvia },
  80: { d: 'Chubascos',             i: iconLlovizna },
  95: { d: 'Tormenta',              i: iconTormenta },
}

const CAMPOS = 'temperature_2m,relative_humidity_2m,weathercode,windspeed_10m,apparent_temperature,precipitation'
const CACHE_KEY  = 'weather_cache'
const CACHE_TIME = 10 * 60 * 1000  // 10 minutos

function parsearClima(current) {
  const w = WMO[current.weathercode] || { d: 'Variable', i: '🌡️' }
  return {
    temperatura: Math.round(current.temperature_2m),
    humedad:     current.relative_humidity_2m,
    viento:      Math.round(current.windspeed_10m),
    sensacion:   Math.round(current.apparent_temperature),
    lluvia:      current.precipitation ?? 0,
    descripcion: w.d,
    icono:       w.i,
  }
}

export function useClima() {
  const clima = ref(null)

  async function cargarClima() {
    // 1. Intentar desde caché
    try {
      const raw = localStorage.getItem(CACHE_KEY)
      if (raw) {
        const cache = JSON.parse(raw)
        if (Date.now() - cache.timestamp < CACHE_TIME) {
          clima.value = parsearClima(cache.data.current)
          return
        }
      }
    } catch { /* caché corrupto — continuar */ }

    // 2. Intentar con geolocalización real
    try {
      const pos = await new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 })
      )
      const { latitude: lat, longitude: lon } = pos.coords
      const url  = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=${CAMPOS}&timezone=auto`
      const data = await fetch(url).then(r => r.json())
      localStorage.setItem(CACHE_KEY, JSON.stringify({ data, timestamp: Date.now() }))
      clima.value = parsearClima(data.current)
      return
    } catch { /* geolocalización denegada o timeout — usar fallback */ }

    // 3. Fallback: coordenadas fijas de Cajamarca
    try {
      const url  = `https://api.open-meteo.com/v1/forecast?latitude=-7.1518&longitude=-78.5117&current=${CAMPOS}&timezone=America%2FLima`
      const data = await fetch(url).then(r => r.json())
      clima.value = parsearClima(data.current)
    } catch {
      clima.value = {
        temperatura: '--', humedad: '--', viento: '--',
        sensacion: '--', lluvia: 0, descripcion: 'Sin datos', icono: '🌡️',
      }
    }
  }

  return { clima, cargarClima }
}