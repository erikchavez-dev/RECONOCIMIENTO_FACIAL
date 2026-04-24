<template>
  <div class="panel" :class="{ light: !theme.oscuro }">

    <header class="header-bar">
      <div class="header-left">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <span class="sistema-nombre">Sistema de Control de Asistencia</span>
      </div>
      <div class="header-right">
        <span class="nombre-chip">
          <img :src="iconoPerfil" class="icono-perfil" />
          {{ auth.usuario?.nombre_completo }}
        </span>
        <button @click="theme.toggle()" class="btn-sm" :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'">
          <img :src="theme.oscuro ? iconoSol : iconoLuna" alt="Icono Tema" class="icono-btn" />
        </button>
        <button @click="handleLogout" class="btn-logout">⬅ Salir</button>
      </div>
    </header>

    <main class="content">
      <div class="titulo-seccion">
        <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
        <h2>Mi Historial de Marcaciones</h2>
      </div>

      <div v-if="cargando" class="estado-msg">
        <span class="estado-spinner"><img :src="relojArena" class="reloj-arena" alt="Reloj"/></span>
        Cargando historial...
      </div>

      <div v-else-if="error" class="error-box">{{ error }}</div>

      <div v-else-if="marcaciones.length > 0" class="lista">
        <div v-for="m in marcaciones" :key="m.id" class="marcacion-item">
          <div :class="['item-icono', m.tipo === 'ENTRADA' ? 'icono-entrada' : 'icono-salida']">
            {{ m.tipo === 'ENTRADA' ? '↗' : '↙' }}
          </div>
          <div class="item-fecha">
            <span class="fecha-txt">{{ formatearFecha(m.fecha) }}</span>
            <span class="hora-txt">{{ formatearHora(m.fecha) }}</span>
          </div>
          <div class="item-badges">
            <span :class="['badge', m.tipo === 'ENTRADA' ? 'badge-entrada' : 'badge-salida']">
              {{ m.tipo }}
            </span>
            <span v-if="m.estado" :class="['badge', m.estado === 'PUNTUAL' ? 'badge-puntual' : 'badge-tardanza']">
              {{ m.estado }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="estado-msg">
        <span class="estado-emoji"></span>
        <span>No hay marcaciones registradas</span>
      </div>
    </main>
  </div>
</template>

<script src="./script.js"></script>

<style scoped src="./style.css"></style>