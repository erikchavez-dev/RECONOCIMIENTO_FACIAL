// Lógica de paginación reutilizable — funciona en dos modos:
// MODO CLIENTE: le pasas el array completo y él calcula las páginas
//   const { paginaActual, paginasVisibles, itemsPagina, totalPaginas, irA } = usePaginacion(lista, 20)
// MODO SERVIDOR: tú manejas la carga, solo usas paginaActual/paginasVisibles/irA
//   const { paginaActual, paginasVisibles, totalPaginas, setTotal, irA } = usePaginacion(null, 20)
//   // Después de cargar: setTotal(response.data.total_paginas)

import { ref, computed } from 'vue'

export function usePaginacion(listaRef = null, porPagina = 20) {
  const paginaActual  = ref(1)
  const totalPaginas  = ref(1)

  // Para modo servidor — llamar con el total que devuelve el backend
  function setTotal(total) {
    totalPaginas.value = total || 1
  }

  // Para modo cliente — slice del array completo según página actual
  const itemsPagina = listaRef
    ? computed(() => {
        const inicio = (paginaActual.value - 1) * porPagina
        const fin    = inicio + porPagina
        // Calcular totalPaginas automáticamente desde el array
        totalPaginas.value = Math.max(1, Math.ceil((listaRef.value?.length || 0) / porPagina))
        return listaRef.value?.slice(inicio, fin) || []
      })
    : null

  // Números de página visibles — máximo 5, centrados en la actual
  const paginasVisibles = computed(() => {
    const total  = totalPaginas.value
    const actual = paginaActual.value
    const rango  = 2   // páginas a cada lado de la actual

    let inicio = Math.max(1, actual - rango)
    let fin    = Math.min(total, actual + rango)

    // Ajustar si estamos cerca del inicio o del final
    if (actual <= rango)        fin   = Math.min(total, rango * 2 + 1)
    if (actual >= total - rango) inicio = Math.max(1, total - rango * 2)

    const paginas = []
    for (let i = inicio; i <= fin; i++) paginas.push(i)
    return paginas
  })

  function irA(pagina) {
    if (pagina < 1 || pagina > totalPaginas.value) return
    paginaActual.value = pagina
  }

  function resetear() {
    paginaActual.value = 1
  }

  return {
    paginaActual,
    totalPaginas,
    paginasVisibles,
    itemsPagina,
    setTotal,
    irA,
    resetear,
  }
}