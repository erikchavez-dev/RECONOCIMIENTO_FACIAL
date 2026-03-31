// router/index.js — Configuración de rutas de la aplicación
// Incluye guardas de navegación que verifican:
// - Si el usuario está autenticado
// - Si tiene el rol correcto (ADMIN o TRABAJADOR)
// - Si debe cambiar su contraseña antes de continuar

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // Página de inicio pública
  { path: '/', component: () => import('@/views/InicioView.vue') },
  
  // Login público
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  
  // Cambiar contraseña — solo usuarios autenticados
  { path: '/cambiar-password', component: () => import('@/views/CambiarPasswordView.vue'), meta: { requiresAuth: true } },

  // Panel del trabajador
  { path: '/trabajador/panel', component: () => import('@/views/trabajador/PanelView.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/historial', component: () => import('@/views/trabajador/HistorialView.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/marcar', component: () => import('@/views/trabajador/MarcarView.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },
  { path: '/trabajador/asistencia', component: () => import('@/views/trabajador/AsistenciaView.vue'), meta: { requiresAuth: true, rol: 'TRABAJADOR' } },

  // Panel del administrador
  { path: '/admin/dashboard', component: () => import('@/views/admin/DashboardView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/trabajadores', component: () => import('@/views/admin/TrabajadoresView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/marcaciones', component: () => import('@/views/admin/MarcacionesView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/reportes', component: () => import('@/views/admin/ReportesView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/configuracion', component: () => import('@/views/admin/ConfiguracionView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/auditoria', component: () => import('@/views/admin/AuditoriaView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/usuarios', component: () => import('@/views/admin/UsuariosView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
  { path: '/admin/asistencia', component: () => import('@/views/admin/AsistenciaView.vue'), meta: { requiresAuth: true, rol: 'ADMIN' } },
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