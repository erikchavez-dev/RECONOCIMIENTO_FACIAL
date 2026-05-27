// router/index.js — Incluye guardas de navegación para TRABAJADOR, ADMIN y SUPERADMIN

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // Públicas
  { path: '/',      component: () => import('@/views/inicio/index.vue') },
  { path: '/login', component: () => import('@/views/login/index.vue') },

  // Cambiar contraseña — cualquier usuario autenticado
  { path: '/cambiar-password', component: () => import('@/views/cambiarPassword/index.vue'), meta: { requiresAuth: true } },

  // ── Trabajador ───────────────────────────────────────────────────────────
  { path: '/trabajador/panel',      component: () => import('@/views/trabajador/Panel/index.vue'),      meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/historial',  component: () => import('@/views/trabajador/Historial/index.vue'),  meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/marcar',     component: () => import('@/views/trabajador/Marcacion/index.vue'),  meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/asistencia', component: () => import('@/views/trabajador/Asistencia/index.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },

  // ── Admin y SuperAdmin (mismas rutas, acceso compartido) ─────────────────
  { path: '/admin/dashboard',    component: () => import('@/views/admin/Dashboard/index.vue'),    meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/trabajadores', component: () => import('@/views/admin/Trabajadores/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/marcaciones',  component: () => import('@/views/admin/Marcaciones/index.vue'),  meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/reportes',     component: () => import('@/views/admin/Reportes/index.vue'),     meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/configuracion',component: () => import('@/views/admin/Configuracion/index.vue'),meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/auditoria',    component: () => import('@/views/admin/Auditoria/index.vue'),    meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/usuarios',     component: () => import('@/views/admin/Usuarios/index.vue'),     meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/asistencia',   component: () => import('@/views/admin/Asistencia/index.vue'),   meta: { requiresAuth: true, rol: 'ADMIN' } },

  // ── SuperAdmin exclusivo ─────────────────────────────────────────────────
  { path: '/superadmin/gestion-admins', component: () => import('@/views/admin/GestionAdmins/index.vue'), meta: { requiresAuth: true, rol: 'SUPERADMIN' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // 1. Ruta protegida sin sesión → login
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'

  // 2. Debe cambiar password primero
  if (auth.isAuthenticated && auth.debeCambiarPassword && to.path !== '/cambiar-password') {
    return '/cambiar-password'
  }

  // 3. Control de rol
  if (to.meta.rol) {
    const rol = auth.rolActual

    // SUPERADMIN puede ir a cualquier ruta de ADMIN también
    if (to.meta.rol === 'ADMIN' && (rol === 'ADMIN' || rol === 'SUPERADMIN')) return

    // Ruta exclusiva de SUPERADMIN
    if (to.meta.rol === 'SUPERADMIN' && rol === 'SUPERADMIN') return

    // Ruta de TRABAJADOR
    if (to.meta.rol === 'TRABAJADOR' && rol === 'TRABAJADOR') return

    // No tiene el rol correcto → redirigir según su rol
    if (rol === 'SUPERADMIN' || rol === 'ADMIN') return '/admin/dashboard'
    if (rol === 'TRABAJADOR') return '/trabajador/panel'
    return '/login'
  }
})

export default router