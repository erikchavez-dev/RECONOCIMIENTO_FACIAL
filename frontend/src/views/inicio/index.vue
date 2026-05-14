<!-- InicioView.vue — Página de inicio pública -->
<!-- Muestra el logo, título, botón de inicio de sesión -->
<!-- y 4 tarjetas con características del sistema -->

<template>
  <div class="inicio">

    <!-- HERO — fondo con imagen de Cajamarca -->
    <div class="hero">
      <div class="hero-overlay">
        <img src="/logo-4.webp" alt="Logo Municipalidad" class="logo" />
        <h1>Sistema de Control de Asistencia Facial</h1>
        <p class="sub-titulo">Municipalidad Provincial de Cajamarca</p>
        <button @click="$router.push('/login')" class="btn-iniciar">
          Iniciar Sesión
        </button>
      </div>
    </div>

    <!-- CARACTERÍSTICAS -->
    <div class="caracteristicas">
      <div class="card">
        <img :src="iconoFacial" alt="Icono Reconocimiento Facial" class="icono" />
        <h3>Reconocimiento Facial</h3>
        <p>Verificación biométrica segura y rápida</p>
      </div>
      <div class="card">
        <img :src="iconoTiempo" alt="Icono Registro en Tiempo Real" class="icono" />
        <h3>Registro en Tiempo Real</h3>
        <p>Control de entrada y salida al instante</p>
      </div>
      <div class="card">
        <img :src="iconoReporte" alt="Icono Reportes PDF" class="icono" />
        <h3>Reportes PDF</h3>
        <p>Generación automática de reportes detallados</p>
      </div>
      <div class="card">
        <img :src="iconoDispositivo" alt="Icono Acceso Multiplataforma" class="icono" />
        <h3>Acceso Multiplataforma</h3>
        <p>Desde cualquier dispositivo con cámara</p>
      </div>
    </div>

    <!-- FOOTER -->
    <footer>
      © 2026 Municipalidad Provincial de Cajamarca. Todos los derechos reservados.
    </footer>

  </div>
</template>

<script setup>
import iconoFacial from '@/assets/icono-facial.png'
import iconoTiempo from '@/assets/icono-tiempo.png'
import iconoReporte from '@/assets/icono-reporte.png'
import iconoDispositivo from '@/assets/icono-dispositivo.png'
</script>

<style scoped src="./style.css"></style>