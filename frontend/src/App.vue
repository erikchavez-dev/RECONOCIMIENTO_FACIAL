<!-- App.vue — Componente raíz de la aplicación -->
<!-- RouterView renderiza la vista según la ruta actual -->
<!-- Nada más aquí, cada vista maneja su propio layout -->

<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}
</style>