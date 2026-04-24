// main.js — Punto de entrada de la aplicación Vue
// Registra los plugins principales: Router y Pinia
// Pinia maneja el estado global (auth, datos)
// Router maneja la navegación entre páginas

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/tema.css'
 
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')