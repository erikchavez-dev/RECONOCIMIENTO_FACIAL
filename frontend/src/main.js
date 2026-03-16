// main.js — Punto de entrada de la aplicación Vue
// Registra los plugins principales: Router y Pinia
// Pinia maneja el estado global (auth, datos)
// Router maneja la navegación entre páginas

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())  // Estado global
app.use(router)         // Navegación

app.mount('#app')