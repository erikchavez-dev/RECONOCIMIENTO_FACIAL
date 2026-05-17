// Muestra el estado de la geolocalización: dot de color + texto descriptivo.
// Recibe los valores calculados desde useGeolocalizacion() vía props.

<template>
  <div class="geo-status" :class="geoClase">
    <span class="geo-dot"></span>
    <span class="geo-txt">{{ geoTexto }}</span>
  </div>
</template>

<script setup>


defineProps({
  geoTexto: {
    type: String,
    required: true,
  },
  geoClase: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.geo-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  padding: 5px 14px;
  border-radius: 20px;
  margin-bottom: 12px;
  background: var(--bg-soft);
  color: var(--text-soft);
  border: 1px solid var(--border-color);
}

.geo-ok       { background: rgba(24,196,64,0.1);  color: #18c440; border-color: rgba(24,196,64,0.3); }
.geo-denegado { background: rgba(251,191,36,0.1); color: #d97706; border-color: rgba(251,191,36,0.3); }
.geo-cargando { background: rgba(59,130,246,0.1); color: #3b82f6; border-color: rgba(59,130,246,0.3); }

.geo-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  background: currentColor;
  opacity: 0.8;
}
</style>