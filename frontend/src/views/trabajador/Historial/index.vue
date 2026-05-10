<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <AppHeader />

    <main class="content">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Historial de Marcaciones</h2>
        <span class="subtitulo">Mostrando últimos 50 registros</span>
      </div>

      <div v-if="cargando" class="estado-msg">
        <span class="estado-spinner"><img :src="relojArena" class="reloj-arena" alt="Reloj"/></span>
        Cargando historial...
      </div>

      <div v-else-if="error" class="error-box">{{ error }}</div>

      <div v-else-if="marcaciones.length > 0" class="tabla-wrapper">
        <table class="historia-tabla">
          <thead>
            <tr>
              <th>Fecha de Registro</th>
              <th>Hora Exacta</th>
              <th>Tipo</th>
              <th>Estado del Marcaje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in itemsPagina" :key="m.id">

              <td class="col-fecha">{{ formatearFecha(m.fecha) }}</td>

              <td class="col-hora">{{ formatearHora(m.fecha) }}</td>

              <td class="col-tipo">
                <span class="type-pill" :class="tipoPillClass(m.tipo)">
                  {{ formatearTipo(m.tipo) }}
                </span>
              </td>

              <td class="col-estado">
                <div class="status-indicator">
                  <span class="dot" :class="estadoDotClass(m.estado)"></span>
                  <span :class="estadoTextoClass(m.estado)">{{ m.estado || 'Fuera de Horario' }}</span>
                </div>
              </td>

            </tr>
          </tbody>
        </table>

        <div class="footer-tabla">
          <span class="info-pagina">Página {{ paginaActual }} de {{ totalPaginas }}</span>

          <div class="paginacion" v-if="totalPaginas > 1">
            <button @click="paginaActual = 1" :disabled="paginaActual === 1" class="btn-pagina btn-extremo">«</button>
            <button @click="paginaActual--" :disabled="paginaActual === 1" class="btn-pagina">‹ Anterior</button>
            <div class="paginas-numeros">
              <button
                v-for="p in paginasVisibles"
                :key="p"
                @click="paginaActual = p"
                :class="['btn-num', p === paginaActual ? 'activo' : '']"
              >{{ p }}</button>
            </div>
            <button @click="paginaActual++" :disabled="paginaActual === totalPaginas" class="btn-pagina">Siguiente ›</button>
            <button @click="paginaActual = totalPaginas" :disabled="paginaActual === totalPaginas" class="btn-pagina btn-extremo">»</button>
          </div>
        </div>
      </div>

      <div v-else class="estado-msg">
        <span class="estado-emoji">📋</span>
        <span>No hay marcaciones registradas</span>
      </div>
    </main>
  </div>
</template>

<script src="./script.js"></script>
<style scoped src="./style.css"></style>