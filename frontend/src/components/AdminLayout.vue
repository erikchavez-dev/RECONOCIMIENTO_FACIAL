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
        <router-link to="/admin/marcaciones"  class="menu-item"><img :src="iconoMarcaciones"  class="icono" /> Marcaciones</router-link>
        <router-link to="/admin/asistencia"   class="menu-item"><img :src="iconoAsistencia"   class="icono" /> Asistencia</router-link>
        <router-link to="/admin/reportes"     class="menu-item"><img :src="iconoReportes"     class="icono" /> Reportes</router-link>
        <router-link to="/admin/auditoria"    class="menu-item"><img :src="iconoAuditoria"    class="icono" /> Auditoría</router-link>

        <p class="divid-menu">Sistema</p>
        <router-link to="/admin/configuracion" class="menu-item"><img :src="iconoConfiguracion" class="icono" /> Configuración</router-link>

        <!-- Solo visible para SUPERADMIN -->
        <template v-if="auth.esSuperAdmin">
          <p class="divid-menu divid-superadmin">Super Admin</p>
          <router-link to="/superadmin/gestion-admins" class="menu-item menu-item-superadmin">
            <img :src="iconoAdmins" class="icono" /> Gestión de Admins
          </router-link>
        </template>
      </nav>

      <!-- Badge de rol en el footer -->
      <div class="sidebar-footer">
        
        <button @click="handleLogout" class="btn-logout">⬅ Cerrar sesión</button>
      </div>
    </aside>

    <div v-if="sidebarAbierto" class="overlay" @click="sidebarAbierto = false"></div>

    <!-- CONTENIDO -->
    <div class="contenido">
     <header class="header">
        <div class="header-left">
          <img :src="iconoBarra" class="btn-menu" @click="toggleSidebar" />
          <h1 class="pagina-titulo">{{ titulo }}</h1>
        </div>
        <div class="nom_and_rol">
          <span class="admin-nombre">{{ auth.usuario?.nombre_completo }}</span>
          <div class="rol-badge" :class="'rol-' + auth.rolActual?.toLowerCase()">
            - {{ auth.rolActual === 'SUPERADMIN' ? 'Super Admin' : 'Admin' }}
          </div>
        </div>
      </header>

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
import iconoAdmins from '@/assets/icons/people.svg'
import iconoMarcaciones  from '@/assets/icon-marcaciones.svg'
import iconoReportes     from '@/assets/icon-reportes.svg'
import iconoConfiguracion from '@/assets/icon-configuracion.svg'
import iconoAuditoria    from '@/assets/icon-auditoria.svg'
import iconoAsistencia   from '@/assets/icon-checking.svg'
import iconoBarra        from '@/assets/icon-off-canvas.svg'

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({ titulo: { type: String, default: 'Dashboard' } })

const router = useRouter()
const auth   = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

const sidebarAbierto = ref(false)
function toggleSidebar() {
  sidebarAbierto.value = !sidebarAbierto.value
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-app);
}

.sidebar {
  width: 240px;
  min-width: 240px;
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

.menu {
  flex: 1;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.divid-menu {
  padding: 6px 20px 2px;
  color: #fff;
  font-size: 0.95em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 8px;
}


.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 22px;
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

/* Ítem exclusivo SuperAdmin: borde dorado */

.menu-item-superadmin {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 22px;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.95em;
  font-weight: 500;
  transition: all 0.2s;
}
.menu-item-superadmin:hover {
  background: rgba(255,255,255,0.1);
  color: #00ff84;
}

.menu-item-superadmin.router-link-active {
  background: rgba(255,255,255,0.15);
  color: #00ff84;
  border-left: 4px solid white;
}

.icono { height: 19px; width: 19px; }

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Badge de rol */
.nom_and_rol {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 15px;
}

.admin-nombre {
  font-size: 1.07em;
  font-weight: 600;
  color: #000;
}

.rol-badge {
  text-transform: uppercase;
}

.rol-admin,
.rol-superadmin {
  color: #000;
  font-size: 0.9em;
  font-weight: 600;
}



.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ff0000;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.92rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background-color: #ad0404;
  color: #ffffff;
}

.contenido {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-app);
  overflow: hidden;
  transition: background 0.3s;
}

.header {
  background: var(--bg-panel);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow);
  flex-shrink: 0;
  transition: background 0.3s;
}

.pagina-titulo {
  font-size: 1.2rem;
  color: var(--text-accent);
  font-weight: bold;
}



.main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
}

.btn-menu {
  width: 24px;
  height: 24px;
  cursor: pointer;
  margin-right: 10px;
  display: none;
  filter: invert(48%) sepia(97%) saturate(2135%) hue-rotate(119deg) brightness(103%) contrast(112%);
}

.header-left {
  display: flex;
  align-items: center;
}

.overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  z-index: 900;
}

@media (max-width: 768px) {
  .btn-menu { display: block; }
  .sidebar {
    position: fixed;
    top: 0; left: 0;
    height: 100%;
    z-index: 1000;
    transform: translateX(-100%);
  }
  .sidebar-open { transform: translateX(0); }
  .contenido { width: 100%; }
  .admin-nombre { font-size: 0.7em; }
  .pagina-titulo { font-size: 1.06em; }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .btn-menu { display: block; width: 26px; height: 26px; }
  .sidebar {
    position: fixed;
    top: 0; left: 0;
    z-index: 1000;
    width: 270px; min-width: 270px;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.28s ease;
    box-shadow: 8px 0 30px rgba(0,0,0,0.25);
  }
  .sidebar-open { transform: translateX(0); }
  .contenido { width: 100%; }
  .header { padding: 16px 20px; gap: 12px; }
  .header-left { gap: 8px; min-width: 0; }
  .pagina-titulo { font-size: 1.1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .admin-nombre { font-size: 0.78rem; text-align: right; max-width: 240px; line-height: 1.3; }
  .main { padding: 20px; }
  .menu-item { padding: 10px 22px; font-size: 0.92rem; }
  .divid-menu { font-size: 0.82rem; padding: 10px 20px 4px; }
  .logo { width: 120px; height: 70px; }
  .sistema { font-size: 0.96rem; }
  .btn-logout { font-size: 0.85rem; padding: 10px 14px; }
}
</style>