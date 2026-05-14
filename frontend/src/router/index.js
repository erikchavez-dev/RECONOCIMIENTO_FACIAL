// router/index.js — Configuración de rutas de la aplicación
// Incluye guardas de navegación que verifican:
// - Si el usuario está autenticado
// - Si tiene el rol correcto (ADMIN o TRABAJADOR)
// - Si debe cambiar su contraseña antes de continuar

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // Página de inicio pública
  { path: '/', component: () => import('@/views/inicio/index.vue') },
  
  // Login público
  { path: '/login', component: () => import('@/views/login/index.vue') },
  
  // Cambiar contraseña — solo usuarios autenticados
  { path: '/cambiar-password', component: () => import('@/views/cambiarPassword/index.vue'), meta: { requiresAuth: true } },

  // Panel del trabajador
  { path: '/trabajador/panel', component: () => import('@/views/trabajador/Panel/index.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path  : '/trabajador/historial', component: () => import('@/views/trabajador/Historial/index.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/marcar', component: () => import('@/views/trabajador/Marcacion/index.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/asistencia', component: () => import('@/views/trabajador/Asistencia/index.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },


  // Panel del administrador
  { path: '/admin/dashboard', component: () => import('@/views/admin/Dashboard/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/trabajadores', component: () => import('@/views/admin/Trabajadores/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/marcaciones', component: () => import('@/views/admin/Marcaciones/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/reportes', component: () => import('@/views/admin/Reportes/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/configuracion', component: () => import('@/views/admin/Configuracion/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/auditoria', component: () => import('@/views/admin/Auditoria/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/usuarios', component: () => import('@/views/admin/Usuarios/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/asistencia', component: () => import('@/views/admin/Asistencia/index.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
]



const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }

  if (auth.isAuthenticated && auth.debeCambiarPassword && to.path !== '/cambiar-password') {
    return '/cambiar-password'
  }

  if (to.meta.rol && auth.usuario?.rol !== to.meta.rol) {
    if (auth.isAdmin) return '/admin/dashboard'
    if (auth.esTrabajador) return '/trabajador/panel'
    return '/login'
  }
})

export default router  