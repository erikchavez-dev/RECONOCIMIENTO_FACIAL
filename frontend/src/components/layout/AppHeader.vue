<template>
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
      <button
        @click="theme.toggle()"
        class="btn-sm"
        :title="theme.oscuro ? 'Tema claro' : 'Tema oscuro'"
      >
        <img :src="theme.oscuro ? iconoSol : iconoLuna" alt="Icono Tema" class="icono-btn" />
      </button>
      <button @click="handleLogout" class="btn-logout">
        <span class="txt-exit">Salir</span>
        <img :src="iconoLogout" alt="" class="icon-logout" />
      </button>
    </div>
  </header>
</template>

<script setup>
import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna from '@/assets/icons/half-moon.svg'
import iconoSol from '@/assets/icons/sun.svg'
import iconoLogout from '@/assets/icons/logout.svg'

import { useThemeStore } from '@/stores/theme'
import { useAuth }       from '@/composables/useAuth'

// Props: callback opcional para ejecutar antes del logout
// (ej: detener cámara en MarcarView)
const props = defineProps({
  antesDeLogout: {
    type: Function,
    default: null,
  },
})

const theme = useThemeStore()
const { auth, handleLogout } = useAuth({
  antesDeLogout: props.antesDeLogout ?? undefined,
})
</script>

<style scoped>
.header-bar {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 28px;
  border-bottom: 2px solid var(--accent);
  background: var(--bg-card);
}
.header-left { display: flex; align-items: center; gap: 10px; }
.header-right { display: flex; align-items: center; gap: 10px; }

.logo {
  width: 150px;
  height: 55px;
  object-fit: contain;

}

.sistema-nombre {
  color: #ffffff;
  font-weight: 600;
  font-size: 1.5em;
  font-weight: 600;
  opacity: 0.9;
}

.nombre-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #ffffff;
  font-size: 1.1em;
  font-weight: 600;
  margin-right: 50px;

}
.icono-perfil { width: 18px; height: 18px; }

.btn-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 22px;
  cursor: pointer;
  background: #e7e7e7;
  border: 0px solid var(--border-color);
  border-radius: 4px;
  transition: background 0.2s;
}
.btn-sm:hover {
  background: #00ff95;
}
.icono-btn {
  width: 18px;
  height: 18px;
  display: block;
}

.btn-logout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2px;
  background: #ff0000;
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #ffffff;
  padding: 9px 20px 9px 45px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
}
.icon-logout {
  width: 22px;
  height: 22px;
  margin-left: 5px;
}



.btn-logout:hover {
  background: #000000;
  color: #ff0000;
}

/* ── TEMA CLARO ── */
.panel.light .header-bar,
:global(.panel.light) .header-bar {
  background: #132941 !important;
  border-bottom: 1px solid var(--border-color);
}
:global(.panel.light) .btn-sm {
  background: var(--bg-soft);
  border-color: var(--border-color);
}
:global(.panel.light) .btn-sm:hover { background: var(--accent); }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .header-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 16px;
  }
  .header-right { width: 100%; justify-content: space-between; }
  .logo { width: 110px; height: auto; }
  .sistema-nombre { font-size: 0.8rem; }
  .nombre-chip { padding: 6px 10px; font-size: 0.75rem; }
  .btn-logout { padding: 6px 12px; font-size: 0.75rem; }
}
</style>