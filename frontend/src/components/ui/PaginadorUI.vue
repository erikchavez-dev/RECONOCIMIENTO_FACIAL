<template>
  <div class="paginacion" v-if="totalPaginas > 1">
    <!-- Primera página -->
    <button
      class="btn-pagina btn-extremo"
      :disabled="paginaActual === 1"
      @click="$emit('ir', 1)"
      title="Primera página"
    >«</button>

    <!-- Anterior -->
    <button
      class="btn-pagina"
      :disabled="paginaActual === 1"
      @click="$emit('ir', paginaActual - 1)"
    >‹ Anterior</button>

    <!-- Números -->
    <div class="paginas-numeros">
      <button
        v-for="p in paginasVisibles"
        :key="p"
        :class="['btn-num', p === paginaActual ? 'activo' : '']"
        @click="$emit('ir', p)"
      >{{ p }}</button>
    </div>

    <!-- Siguiente -->
    <button
      class="btn-pagina"
      :disabled="paginaActual === totalPaginas"
      @click="$emit('ir', paginaActual + 1)"
    >Siguiente ›</button>

    <!-- Última página -->
    <button
      class="btn-pagina btn-extremo"
      :disabled="paginaActual === totalPaginas"
      @click="$emit('ir', totalPaginas)"
      title="Última página"
    >»</button>
  </div>

  <!-- Info: "Página X de Y" cuando hay más de 1 -->
  <div class="pagina-info" v-if="totalPaginas > 1">
    Página {{ paginaActual }} de {{ totalPaginas }}
  </div>
</template>

<script setup>
// PaginadorUI.vue
// Botones de paginación reutilizables.
// Emite @ir(numeroPagina) — la vista decide qué hacer con ese número.
// Combinar con usePaginacion() para la lógica.

defineProps({
  paginaActual:   { type: Number, required: true },
  totalPaginas:   { type: Number, required: true },
  paginasVisibles:{ type: Array,  required: true },
})

defineEmits(['ir'])
</script>

<style scoped>
.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 6px;
  flex-wrap: wrap;
}

.pagina-info {
  text-align: center;
  font-size: 0.78rem;
  color: #9ca3af;
  margin-top: 6px;
}

.btn-pagina {
  background: #026d5f;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}
.btn-pagina:hover:not(:disabled) { background: #01c5ab; }
.btn-pagina:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-extremo { padding: 8px 10px; }

.paginas-numeros { display: flex; gap: 4px; }

.btn-num {
  background: #026d5f;
  color: white;
  border: none;
  padding: 7px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.2s;
}
.btn-num:hover  { background: #01c5ab; }
.btn-num.activo { background: #00f483; color: #0a3a2e; font-weight: 700; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .paginacion {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 10px;
    justify-content: flex-start;
  }
  .paginas-numeros { gap: 6px; }
  .btn-pagina, .btn-num { flex-shrink: 0; padding: 5px 8px; font-size: 0.8rem; }
  .btn-extremo { display: none; }
}
</style>