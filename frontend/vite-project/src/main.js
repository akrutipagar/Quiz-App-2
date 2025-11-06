import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios';


axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true  // Enable cookies for session auth

const app = createApp(App)
app.use(router)
app.mount('#app')



