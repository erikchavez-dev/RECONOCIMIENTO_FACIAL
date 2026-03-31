<template>
  <div class="admin-layout">

    <!-- SIDEBAR fijo -->
    <aside class="sidebar">
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
        <router-link to="/admin/asistencia"   class="menu-item"><img :src="iconoMarcaciones"  class="icono" /> Asistencia</router-link>
        <router-link to="/admin/reportes"     class="menu-item"><img :src="iconoReportes"     class="icono" /> Reportes</router-link>
        <router-link to="/admin/auditoria"    class="menu-item"><img :src="iconoAuditoria"    class="icono" /> Auditoría</router-link>
        <p class="divid-menu">Sistema</p>
        <router-link to="/admin/configuracion" class="menu-item"><img :src="iconoConfiguracion" class="icono" /> Configuración</router-link>
      </nav>

      <div class="sidebar-footer">
        <!-- TOGGLE TEMA -->
        <button @click="theme.toggle()" class="btn-tema" :title="theme.oscuro ? 'Cambiar a claro' : 'Cambiar a oscuro'">
          {{ theme.oscuro ? '☀️ Tema claro' : '🌙 Tema oscuro' }}
        </button>
        <button @click="handleLogout" class="btn-logout">⬅ Cerrar sesión</button>
      </div>
    </aside>

    <!-- CONTENIDO: header fijo + main con scroll propio -->
    <div class="contenido">
      <header class="header">
        <h1 class="pagina-titulo">{{ titulo }}</h1>
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
  background: var(--bg-sidebar);
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
  font-size: 0.85rem;
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
  color: rgba(255,255,255,0.5);
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
  color: #a0b4cc;
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.2s;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1);
  color: #ff7300;
}

.menu-item:hover .icono {
  filter: invert(51%) sepia(85%) saturate(2338%) hue-rotate(360deg) brightness(101%) contrast(106%);
}

.menu-item.router-link-active {
  background: rgba(255,255,255,0.15);
  color: #ff7300;
  border-left: 3px solid white;
}

.menu-item.router-link-active .icono {
  filter: invert(51%) sepia(85%) saturate(2338%) hue-rotate(360deg) brightness(101%) contrast(106%);
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

.btn-tema {
  width: 100%;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2);
  color: #c8d8e8;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.82rem;
  text-align: left;
  transition: all 0.2s;
}
.btn-tema:hover { background: rgba(255,255,255,0.15); color: white; }

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
.btn-logout:hover { background: rgba(255,255,255,0.1); color: white; }

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
</style>