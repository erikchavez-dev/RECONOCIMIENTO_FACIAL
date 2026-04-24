<template>
  <div class="admin-layout">

    <!-- SIDEBAR fijo -->
    <aside :class="['sidebar', { 'sidebar-open': sidebarAbierto }]">
      <div class="sidebar-header">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <p class="sistema">Sistema de Control de Asistencia</p>
      </div>

      <nav class="menu">
        <p class="divid-menu">Operaciones</p>
        <router-link to="/admin/dashboard"    class="menu-item"><img :src="iconoDashboard"    class="icono" /> Dashboard</router-link>
        <router-link to="/admin/trabajadores" class="menu-item"><img :src="iconoTrabajadores" class="icono" /> Trabajadores</router-link>
        <router-link to="/admin/usuarios"     class="menu-item"><img :src="iconoUsuarios"     class="icono" /> Usuarios</router-link>
        <router-link to="/admin/marcaciones"  class="menu-item"><img :src="iconoMarcaciones"  class="icono" /> Marcaciones de hoy</router-link>
        <router-link to="/admin/asistencia"   class="menu-item"><img :src="iconoAsistencia"  class="icono" /> Asistencia</router-link>
        <router-link to="/admin/reportes"     class="menu-item"><img :src="iconoReportes"     class="icono" /> Reportes</router-link>
        <router-link to="/admin/auditoria"    class="menu-item"><img :src="iconoAuditoria"    class="icono" /> Auditoría</router-link>
        <p class="divid-menu">Sistema</p>
        <router-link to="/admin/configuracion" class="menu-item"><img :src="iconoConfiguracion" class="icono" /> Configuración</router-link>
      </nav>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="btn-logout">⬅ Cerrar sesión</button>
      </div>
    </aside>

   <div v-if="sidebarAbierto" class="overlay" @click="sidebarAbierto = false">
    </div>

    <!-- CONTENIDO: header fijo + main con scroll propio -->
    <div class="contenido">
      <header class="header">
        <div class="header-left">
          <img :src="iconoBarra" class="btn-menu" @click="toggleSidebar" />
          <h1 class="pagina-titulo">{{ titulo }}</h1>
        </div>
        <span class="admin-nombre">Administrador: {{ auth.usuario?.nombre_completo }}</span>
      </header>

      <!-- Solo este main hace scroll -->
      <main class="main">
        <slot />
      </main>
    </div>

  </div>
</template>

<script setup>
import iconoDashboard    from '@/assets/icon-casa-dashboard.svg'
import iconoTrabajadores from '@/assets/icon-usuario.svg'
import iconoUsuarios     from '@/assets/icon-trabajadores.svg'
import iconoMarcaciones  from '@/assets/icon-marcaciones.svg'
import iconoReportes     from '@/assets/icon-reportes.svg'
import iconoConfiguracion from '@/assets/icon-configuracion.svg'
import iconoAuditoria    from '@/assets/icon-auditoria.svg'
import iconoAsistencia from '@/assets/icon-checking.svg'
import iconoBarra from '@/assets/icon-off-canvas.svg'

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

defineProps({ titulo: { type: String, default: 'Dashboard' } })

const router = useRouter()
const auth   = useAuthStore()
const theme  = useThemeStore()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

//para el off-canvas
const sidebarAbierto = ref(false)

function toggleSidebar() {
  sidebarAbierto.value = !sidebarAbierto.value
}

</script>

<style scoped>
/* Layout raíz: ocupa toda la pantalla, sin scroll en este nivel */
.admin-layout {
  display: flex;
  height: 100vh;        /* altura fija = ventana */
  overflow: hidden;     /* nada desborda aquí */
  background: var(--bg-app);
}

/* SIDEBAR — fijo, no hace scroll */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: #1a3a6b;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  transition: background 0.3s;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo {
  width: 140px;
  height: 80px;
  object-fit: contain;
}

.sistema {
  color: white;
  font-size: 1.08em;
  font-weight: bold;
  line-height: 1.3;
  margin-top: 6px;
}

/* MENÚ — ocupa el espacio disponible, con scroll interno si necesita */
.menu {
  flex: 1;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.divid-menu {
  padding: 6px 20px 2px;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 20px;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.95em;
  font-weight: 500;
  transition: all 0.2s;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
  color: #00ff84;
}

.menu-item:hover .icono {
  filter: invert(48%) sepia(97%) saturate(2135%) hue-rotate(119deg) brightness(103%) contrast(112%);
}

.menu-item.router-link-active {
  background: rgba(255,255,255,0.15);
  color: #00ff84;
  border-left: 4px solid white;
}

.menu-item.router-link-active .icono {
  filter: invert(48%) sepia(97%) saturate(2135%) hue-rotate(119deg) brightness(103%) contrast(112%);
}

.icono { height: 19px; width: 19px; }

/* FOOTER SIDEBAR */
.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}


.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff1a;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.btn-logout:hover {
  background-color: #5a1818;
  color: #ffffff;
  border-color: 1px solid #ff0000;
}


/* CONTENIDO — columna derecha, tampoco hace scroll en este nivel */
.contenido {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-app);
  overflow: hidden;   /* importante: no dejar que este div scrollee */
  transition: background 0.3s;
}

/* HEADER fijo arriba del contenido */
.header {
  background: var(--bg-panel);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow);
  flex-shrink: 0;     /* no se encoge */
  transition: background 0.3s;
}

.pagina-titulo {
  font-size: 1.2rem;
  color: var(--text-accent);
  font-weight: bold;
}

.admin-nombre {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* MAIN — único elemento que hace scroll */
.main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;   /* solo aquí hay scroll */
  overflow-x: hidden;
}

/* para el off-canvas */
/* BOTÓN */
.btn-menu {
  width: 24px;
  height: 24px;
  cursor: pointer;
  margin-right: 10px;
  display: none;
}
.btn-menu {
  filter: invert(48%) sepia(97%) saturate(2135%) hue-rotate(119deg) brightness(103%) contrast(112%);
}
/* HEADER LEFT */
.header-left {
  display: flex;
  align-items: center;
}

/* OVERLAY */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 900;
}

/* MOBILE */
@media (max-width: 768px) {

  .btn-menu {
    display: block;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    z-index: 1000;

    /* oculto */
    transform: translateX(-100%);
  }

  .sidebar-open {
    transform: translateX(0);
  }

  .contenido {
    width: 100%;
  }
  .admin-nombre {
  font-size: 0.7em;
  color: var(--text-secondary);
  }
  .pagina-titulo {
  font-size: 1.06em;
  color: var(--text-accent);
  font-weight: bold;
  }
}

</style>