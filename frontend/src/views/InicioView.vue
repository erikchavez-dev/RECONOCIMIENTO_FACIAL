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
        <p>Municipalidad Provincial de Cajamarca</p>
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

<style scoped>
.inicio {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* HERO */
.hero {
  min-height: 80vh;
  background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/cajamarca-login.webp');
  background-size: cover;
  background-position: center;
  position: relative;

  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.hero-overlay {
  position: absolute;
  inset: 0;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
}

.logo {
  width: 280px;
  height: 108px;
  object-fit: contain;
  background-color: rgba(128, 128, 128, 0.5); 
  border-radius: 12px; /* Un toque redondeado para que se vea más profesional */
  padding: 10px;

}

h1 {
  font-size: 2.08rem;
  font-weight: bold;
  color: white;
}

p {
  font-size: 1.05rem;
  font-weight: 600;
  color: #ffffff ;
}


.btn-iniciar {
  margin-top: 16px;
  padding: 12px 36px; 
  background: linear-gradient(135deg, #0c9b2d 20%, #07551a 80%);
  color: white;
  border: none; 
  border-radius: 7px; 
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;

  box-shadow: 0 4px 15px rgba(24, 196, 64, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  z-index: 1;
}

/* El relleno que viene desde la izquierda */
.btn-iniciar::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: white; /* Color del relleno al hacer hover */
  transform: translateX(-100%); /* Lo mandamos fuera a la izquierda */
  transition: transform 0.4s ease; /* Controla la velocidad del barrido */
  z-index: -1; /* Se queda detrás del texto */
}

/* Efecto al pasar el mouse */
.btn-iniciar:hover {
  color: #000000; /* El texto cambia a azul cuando el fondo es blanco */
}

.btn-iniciar:hover::before {
  transform: translateX(0); /* El fondo blanco entra a su posición */
}

/* Pequeño efecto de pulsación al hacer click */
.btn-iniciar:active {
  transform: scale(0.98);
}

/* CARACTERÍSTICAS */
.caracteristicas {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 48px 24px;
  flex-wrap: wrap;
  background: white;
}

.card {
  text-align: center;
  max-width: 200px;
}

.icono {
  height: 43px;
  width: 43px;
}

.card h3 {
  margin: 12px 0 6px;
  font-size: 1rem;
  color: #1a3a6b;
}

.card p {
  font-size: 0.85rem;
  color: #666;
}

/* FOOTER */
footer {
  background-color: #1a3a6b;
  color: white;
  text-align: center;
  padding: 16px;
  font-size: 0.8rem;
  margin-top: auto;
}
</style>