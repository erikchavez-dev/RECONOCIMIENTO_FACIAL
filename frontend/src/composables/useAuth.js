// Lógica de autenticación reutilizable.
// Centraliza el logout para que todas las vistas lo usen igual
// sin repetir las mismas 3 líneas en cada archivo.
// Acepta un callback opcional `antesDeLogout` para ejecutar
// lógica específica de la vista antes de cerrar sesión

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function useAuth({ antesDeLogout } = {}) {
  const router = useRouter()
  const auth   = useAuthStore()

  async function handleLogout() {
    if (antesDeLogout) antesDeLogout()
    await auth.logout()
    router.push('/login')
  }

  return {
    auth,
    handleLogout,
  }
}