// composables/useGeolocalizacion.js
// Encapsula toda la lógica de geolocalización del navegador.
// Expone latitud, longitud, estado (ok/denegado/obteniendo/no-soportado)
// y los computed de texto y clase CSS para el indicador visual.

import { ref, computed } from 'vue'

export function useGeolocalizacion() {
  const geoLatitud  = ref(null)
  const geoLongitud = ref(null)
  const geoEstado   = ref('obteniendo')

  const geoTexto = computed(() => ({
    obteniendo:      'Obteniendo ubicación...',
    ok:              'Ubicación obtenida',
    denegado:        'Permiso de ubicación denegado (opcional)',
    'no-soportado':  'Geolocalización no disponible en este dispositivo',
  }[geoEstado.value] || ''))

  const geoClase = computed(() => ({
    'geo-ok':       geoEstado.value === 'ok',
    'geo-denegado': geoEstado.value === 'denegado',
    'geo-cargando': geoEstado.value === 'obteniendo',
  }))

  function pedirGeolocalizacion() {
    if (!navigator.geolocation) {
      geoEstado.value = 'no-soportado'
      return
    }
    geoEstado.value = 'obteniendo'
    navigator.geolocation.getCurrentPosition(
      pos => {
        geoLatitud.value  = pos.coords.latitude
        geoLongitud.value = pos.coords.longitude
        geoEstado.value   = 'ok'
      },
      () => { geoEstado.value = 'denegado' },
      { timeout: 8000, maximumAge: 60000 }
    )
  }

  return {
    geoLatitud,
    geoLongitud,
    geoEstado,
    geoTexto,
    geoClase,
    pedirGeolocalizacion,
  }
}