import iconoPerfil from '@/assets/icon-perfil.svg'
import iconoLuna   from '@/assets/icon-luna.svg'
import iconoSol    from '@/assets/icon-sol.svg'
import relojArena  from '@/assets/reloj-de-arena.webp'

import { ref, onMounted } from 'vue'
import { useRouter }      from 'vue-router'
import { useAuthStore }   from '@/stores/auth'
import { useThemeStore }  from '@/stores/theme'
import api                from '@/services/api'

export default {
  setup() {
    const router = useRouter()
    const auth   = useAuthStore()
    const theme  = useThemeStore()

    const marcaciones = ref([])
    const cargando    = ref(true)
    const error       = ref('')

    onMounted(async () => {
      try {
        const trabajadorId = auth.usuario?.trabajador_id
        const response = await api.get(`/api/marcaciones/historial/${trabajadorId}/`)
        marcaciones.value = response.data
      } catch (e) {
        error.value = 'Error al cargar el historial'
      } finally {
        cargando.value = false
      }
    })

    function formatearFecha(fecha) {
      return new Date(fecha).toLocaleDateString('es-PE', {
        weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit'
      })
    }

    function formatearHora(fecha) {
      return new Date(fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit', minute: '2-digit'
      })
    }

    async function handleLogout() {
      await auth.logout()
      router.push('/login')
    }

    return {
      iconoPerfil, iconoLuna, iconoSol, relojArena,
      auth, theme,
      marcaciones, cargando, error,
      formatearFecha, formatearHora, handleLogout,
    }
  }
}