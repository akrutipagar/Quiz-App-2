import { createRouter, createWebHistory } from 'vue-router'
import Register from '../views/register.vue'
import Login from '../views/login.vue'
import AdminDashboard from '../views/admindashboard.vue'
import UserDashboard from '../views/userdashboard.vue'

const routes = [
  { path: '/', redirect: '/register' },
  { path: '/register', component: Register },
  { path: '/login', component: Login },
  { path: '/admindashboard', component: AdminDashboard },
  { path: '/userdashboard', component: UserDashboard }
]

export default createRouter({
  history: createWebHistory(),
  routes
})

