import { createApp } from 'vue'
import App from './components/App/App.vue'
import '../public/styles/global.css'
// Feature 017: Import highlight.js theme for syntax highlighting
import 'highlight.js/styles/vs2015.css'

const app = createApp(App)
app.mount('#app')
