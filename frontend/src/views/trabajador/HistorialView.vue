<template>
    <div class="panel" :class="{ light: !theme.oscuro }">

        <AppHeader />

        <main class="content">
            <div class="titulo-seccion">
                <button @click="$router.push('/trabajador/panel')" class="btn-volver">← Volver</button>
                <h2>Mi Historial de Marcaciones</h2>
                <span class="subtitulo">Mostrando últimos 50 registros</span>
            </div>

            <div v-if="cargando" class="estado-msg">
                <span class="estado-spinner"><img :src="relojArena" class="reloj-arena" alt="Reloj" /></span>
                Cargando historial...
            </div>

            <div v-else-if="error" class="error-box">{{ error }}</div>

            <div v-else-if="marcaciones.length > 0" class="tabla-wrapper">
                <table class="historia-tabla">
                    <thead>
                        <tr>
                            <th>Fecha de Registro</th>
                            <th>Hora Exacta</th>
                            <th>Tipo</th>
                            <th>Estado del Marcaje</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="m in itemsPagina" :key="m.id">

                            <td class="col-fecha">{{ formatearFecha(m.fecha) }}</td>

                            <td class="col-hora">{{ formatearHora(m.fecha) }}</td>

                            <td class="col-tipo">
                                <span class="type-pill" :class="tipoPillClass(m.tipo)">
                                    {{ formatearTipo(m.tipo) }}
                                </span>
                            </td>

                            <td class="col-estado">
                                <div class="status-indicator">
                                    <span class="dot" :class="estadoDotClass(m.estado)"></span>
                                    <span :class="estadoTextoClass(m.estado)">{{ m.estado || 'Fuera de Horario'
                                        }}</span>
                                </div>
                            </td>

                        </tr>
                    </tbody>
                </table>

                <div class="footer-tabla">
                    <span class="info-pagina">Página {{ paginaActual }} de {{ totalPaginas }}</span>

                    <div class="paginacion" v-if="totalPaginas > 1">
                        <button @click="paginaActual = 1" :disabled="paginaActual === 1"
                            class="btn-pagina btn-extremo">«</button>
                        <button @click="paginaActual--" :disabled="paginaActual === 1" class="btn-pagina">‹
                            Anterior</button>
                        <div class="paginas-numeros">
                            <button v-for="p in paginasVisibles" :key="p" @click="paginaActual = p"
                                :class="['btn-num', p === paginaActual ? 'activo' : '']">{{ p }}</button>
                        </div>
                        <button @click="paginaActual++" :disabled="paginaActual === totalPaginas"
                            class="btn-pagina">Siguiente ›</button>
                        <button @click="paginaActual = totalPaginas" :disabled="paginaActual === totalPaginas"
                            class="btn-pagina btn-extremo">»</button>
                    </div>
                </div>
            </div>

            <div v-else class="estado-msg">
                <span class="estado-emoji">📋</span>
                <span>No hay marcaciones registradas</span>
            </div>
        </main>
    </div>
</template>
<script setup>
import relojArena from '@/assets/reloj-de-arena.webp'

import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuth } from '@/composables/useAuth'
import AppHeader from '@/components/layout/AppHeader.vue'
import { usePaginacion } from '@/composables/usePaginacion'
import api from '@/services/api'

const theme = useThemeStore()
const { auth, handleLogout } = useAuth()

const marcaciones = ref([])
const cargando = ref(true)
const error = ref('')

const {
    paginaActual,
    totalPaginas,
    paginasVisibles,
    itemsPagina,
} = usePaginacion(marcaciones, 6)

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
    if (!fecha) return '—'
    return new Date(fecha).toLocaleDateString('es-PE', {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    }).replace(/^\w/, c => c.toUpperCase())
}

function formatearHora(fecha) {
    if (!fecha) return '—'
    return new Date(fecha).toLocaleTimeString('es-PE', {
        hour: '2-digit',
        minute: '2-digit'
    })
}

function formatearTipo(tipo) {
    if (!tipo) return '—'
    if (tipo.includes('ENTRADA')) return 'Entrada'
    if (tipo.includes('SALIDA')) return 'Salida'
    return tipo
}

function tipoPillClass(tipo = '') {
    if (tipo.includes('ENTRADA')) return 'pill-entrada'
    if (tipo.includes('SALIDA')) return 'pill-salida'
    return ''
}

function estadoDotClass(estado = '') {
    if (estado === 'PUNTUAL') return 'dot-puntual'
    return 'dot-fuera'
}

function estadoTextoClass(estado = '') {
    if (estado === 'PUNTUAL') return 'texto-puntual'
    return 'texto-fuera'
}
</script>
<style scoped>
/* ── TEMA OSCURO (defecto) ── */
.panel {
    --bg-main: #141416cc;
    --bg-card: #141416;
    --bg-soft: rgba(255, 255, 255, 0.08);
    --bg-table-head: rgba(255, 255, 255, 0.04);
    --bg-row-hover: rgba(255, 255, 255, 0.04);
    --text-main: #fcfcfd;
    --text-soft: rgba(255, 255, 255, 0.6);
    --text-muted: rgba(255, 255, 255, 0.35);
    --border-color: #232327;
    --accent: #18c440;

    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-main);
    color: var(--text-main);
}

/* ── TEMA CLARO ── */
.panel.light {
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --bg-soft: #f1f5f9;
    --bg-table-head: #f8fafc;
    --bg-row-hover: #f1f5f9;
    --text-main: #0f172a;
    --text-soft: #64748b;
    --text-muted: #94a3b8;
    --border-color: #e2e8f0;
    --accent: #2563eb;
}

/* ── CONTENT ── */
.content {
    position: relative;
    z-index: 10;
    flex: 1;
    padding: 28px 32px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    background-color: var(--bg-main);
    width: 100%;
    box-sizing: border-box;
}

/* ── TÍTULO ── */
.titulo-seccion {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}

.subtitulo {
    margin-left: auto;
    font-size: 0.85rem;
    color: var(--text-muted);
}

.btn-volver {
    background: var(--bg-soft);
    border: 1px solid var(--border-color);
    color: var(--text-main);
    font-size: 0.9rem;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.btn-volver:hover {
    border-color: var(--accent);
    color: var(--accent);
}

h2 {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 0;
}

.reloj-arena {
    height: 30px;
    width: 30px;
}

/* ── TABLA ── */
.tabla-wrapper {
    background: var(--bg-card);
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    border: 1px solid var(--border-color);
    width: 100%;
    box-sizing: border-box;
}

.panel.light .tabla-wrapper {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
}

.historia-tabla {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.historia-tabla thead {
    background-color: var(--bg-table-head);
    border-bottom: 2px solid var(--border-color);
}

.historia-tabla th {
    padding: 16px 24px;
    font-size: 0.8rem;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    font-weight: 600;
    white-space: nowrap;
}

.historia-tabla tbody tr {
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s;
}

.historia-tabla tbody tr:last-child {
    border-bottom: none;
}

.historia-tabla tbody tr:hover {
    background-color: var(--bg-row-hover);
}

.historia-tabla td {
    padding: 18px 24px;
    vertical-align: middle;
    font-size: 0.9rem;
}

/* ── CELDAS ── */
.col-fecha {
    font-weight: 600;
    color: var(--text-main);
    white-space: nowrap;
}

.col-hora {
    font-weight: 700;
    font-size: 1.05rem;
    color: #18c440;
    white-space: nowrap;
}

.panel.light .col-hora {
    color: #16a34a;
}

.type-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
    background: rgba(99, 102, 241, 0.2);
    color: #a5b4fc;
}

.pill-entrada {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
}

.pill-salida {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
}

.panel.light .pill-entrada {
    background: #dcfce7;
    color: #16a34a;
}

.panel.light .pill-salida {
    background: #fee2e2;
    color: #dc2626;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    white-space: nowrap;
}

.dot {
    height: 8px;
    width: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-puntual {
    background-color: #18c440;
}

.dot-fuera {
    background-color: #f39c12;
}

.texto-puntual {
    color: #18c440;
}

.texto-fuera {
    color: #f39c12;
}

.panel.light .texto-puntual {
    color: #16a34a;
}

.panel.light .texto-fuera {
    color: #d97706;
}

/* ── FOOTER TABLA ── */
.footer-tabla {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: var(--bg-table-head);
    border-top: 1px solid var(--border-color);
    flex-wrap: wrap;
    gap: 12px;
}

.info-pagina {
    font-size: 0.82rem;
    color: var(--text-muted);
}

/* ── PAGINACIÓN ── */
.paginacion {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
}

.paginas-numeros {
    display: flex;
    gap: 6px;
}

.btn-pagina,
.btn-num {
    background: #026d5f;
    flex-shrink: 0;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    transition: background 0.2s;
}

.btn-pagina:hover:not(:disabled),
.btn-num:hover {
    background: #01c5ab;
}

.btn-num.activo {
    background: #00f483;
    color: #000;
    font-weight: bold;
}

.paginacion button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* ── ESTADOS ── */
.estado-msg {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 60px 20px;
    color: var(--text-soft);
    font-size: 0.95rem;
    text-align: center;
}

.estado-emoji {
    font-size: 2.5rem;
}

.estado-spinner {
    font-size: 2rem;
}

.error-box {
    background: rgba(239, 68, 68, 0.1);
    color: #ff4444;
    border: 1px solid rgba(239, 68, 68, 0.25);
    padding: 14px 18px;
    border-radius: 10px;
    text-align: center;
    font-size: 0.9rem;
}

.panel.light .error-box {
    background: #fef2f2;
    color: #dc2626;
    border-color: #fecaca;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
    .content {
        padding: 16px;
        gap: 14px;
    }

    h2 {
        font-size: 1.1rem;
    }

    .subtitulo {
        display: none;
    }

    .historia-tabla th,
    .historia-tabla td {
        padding: 14px 12px;
    }

    /* Ocultar columna Hora en móvil si hay poco espacio */
    .historia-tabla th:nth-child(2),
    .historia-tabla td:nth-child(2) {
        display: none;
    }

    .footer-tabla {
        flex-direction: column;
        align-items: flex-start;
        padding: 14px 16px;
    }

    .paginacion {
        gap: 6px;
        flex-wrap: nowrap;
        overflow-x: auto;
        width: 100%;
    }

    .paginacion button {
        flex-shrink: 0;
        padding: 5px 8px;
        font-size: 0.78rem;
    }

    .btn-extremo {
        display: none;
    }
}
</style>