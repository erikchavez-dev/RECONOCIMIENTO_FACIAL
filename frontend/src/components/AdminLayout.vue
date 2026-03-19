<!-- AdminLayout.vue — Layout compartido del panel administrador -->
<!-- Sidebar izquierdo con menú de navegación -->
<!-- Header con logo y nombre del admin -->

<template>
  <div class="admin-layout">

    <!-- SIDEBAR -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <img src="/sgd_logo.webp" alt="Logo" class="logo" />
        <div>
          <p class="sistema">Sistema de Control de Asistencia</p>
        </div>
      </div>

      <nav class="menu">
      <p class="divid-menu">Operaciones</p><br>
        <router-link to="/admin/dashboard" class="menu-item">
          <img :src="iconoDashboard" alt="trabajadores" class="icono" /> Dashboard

        </router-link>
        <router-link to="/admin/trabajadores" class="menu-item">
          <img :src="iconoTrabajadores" alt="trabajadores" class="icono" /> Trabajadores
        </router-link>
        <router-link to="/admin/usuarios" class="menu-item">
          <img :src="iconoUsuarios" alt="trabajadores" class="icono" /> Usuarios
        </router-link>
        <router-link to="/admin/marcaciones" class="menu-item">
          <img :src="iconoMarcaciones" alt="trabajadores" class="icono" /> Marcaciones de hoy
        </router-link>
        <router-link to="/admin/reportes" class="menu-item">
          <img :src="iconoReportes" alt="trabajadores" class="icono" /> Reportes
        </router-link>
        <router-link to="/admin/auditoria" class="menu-item">
          <img :src="iconoAuditoria" alt="trabajadores" class="icono" /> Auditoría
        </router-link>
      <p class="divid-menu">Sistema</p><br>
        <router-link to="/admin/configuracion" class="menu-item">
          <img :src="iconoConfiguracion" alt="trabajadores" class="icono" /> Configuración
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="btn-logout">
          <span>⬅</span> Cerrar sesión
        </button>
      </div>
    </aside>

    <!-- CONTENIDO PRINCIPAL -->
    <div class="contenido">

      <!-- HEADER -->
      <header class="header">
        <h1 class="pagina-titulo">{{ titulo }}</h1>
        <span class="admin-nombre">Administrador: {{ auth.usuario?.nombre_completo }}</span>
      </header>

      <!-- SLOT — aquí va el contenido de cada vista -->
      <main class="main">
        <slot />
      </main>

    </div>
  </div>
</template>

<script setup>
import iconoDashboard from '@/assets/icon-casa-dashboard.svg'
import iconoTrabajadores from '@/assets/icon-usuario.svg'
import iconoUsuarios from '@/assets/icon-trabajadores.svg'
import iconoMarcaciones from '@/assets/icon-marcaciones.svg'
import iconoReportes from '@/assets/icon-reportes.svg'
import iconoConfiguracion from '@/assets/icon-configuracion.svg'
import iconoAuditoria from '@/assets/icon-auditoria.svg'

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  titulo: {
    type: String,
    default: 'Dashboard'
  }
})

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

/* SIDEBAR */
.sidebar {
  width: 260px;
  min-width: 260px;
  background-color: #2d6aa1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-header {
  display: table-column;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-header p {
  font-size: 1.3em;
  font-weight: 500;
}

.logo {
  width: 140px;
  height: 80px;
  object-fit: contain;
  flex-shrink: 0;
}

.sistema {
  color: white;
  font-size: 0.85rem;
  font-weight: bold;
  line-height: 1.2;
}

.municipalidad {
  color: #a0b4cc;
  font-size: 0.75rem;
}

/* MENÚ */
.menu {
  flex: 1;
  padding: 16px 0;
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 20px;
  color: #a0b4cc;
  text-decoration: none;
  font-size: 0.9em;
  font-weight: 500 !important;
  transition: all 0.2s;
}
/*separa el menu de las configuraciones*/
.divid-menu {
  display: flex;
  align-items: center;
  gap: 0px;
  padding: 2px 20px;
  color: #f4f4f5;
  text-decoration: none;
  font-size: 1.01rem;
  font-weight: 600;
  transition: all 0.2s;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
  color: #ff7300;
}


.menu-item:hover .icono {
  filter: invert(51%) sepia(85%) saturate(2338%)
  hue-rotate(360deg) brightness(101%) contrast(106%) !important;
}

.menu-item.router-link-active .icono {
  filter: invert(51%) sepia(85%) saturate(2338%) 
  hue-rotate(360deg) brightness(101%) contrast(106%) !important;
}



.menu-item.router-link-active {
  background: rgba(255,255,255,0.15);
  color: #ff7300;
  border-left: 3px solid white;
}


.icono {
  height: 19px;
  width: 19px;
}

/* FOOTER SIDEBAR */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #a0b4cc;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

/* CONTENIDO */
.contenido {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f0f4f8;
  overflow: auto;
}

.header {
  background: white;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.pagina-titulo {
  font-size: 1.2rem;
  color: #1a3a6b;
  font-weight: bold;
}

.admin-nombre {
  font-size: 0.85rem;
  color: #666;
}

.main {
  flex: 1;
  padding: 24px;
}
</style>