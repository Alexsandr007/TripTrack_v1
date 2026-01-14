import { createRouter, createWebHistory } from 'vue-router'
import baseHomeComponent from '../components/home/baseHomeComponent.vue'
import RegisterComponent from '../components/home/auth/RegisterComponent.vue'
import Login from '../components/home/auth/LoginComponent.vue'
import Recovery from '../components/home/auth/RecoveryComponent.vue'
import Profile from '../components/profile/profileComponent.vue'
import TestComponent from '@/components/TestComponent.vue'
import { useAuth } from '@/composables/useAuth'

const routes = [
  { path: '/', name: 'Home', component: baseHomeComponent },
  { path: '/login', name: 'Login', component: Login, meta: { requiresGuest: true } },
  { path: '/register', name: 'Register', component: RegisterComponent, meta: { requiresGuest: true } },
  { path: '/recovery', name: 'Recovery', component: Recovery, meta: { requiresGuest: true } },
  { 
    path: '/profile', 
    name: 'Profile', 
    component: Profile,
    meta: { requiresAuth: true }
  },
  { path: '/test-api', name: 'TestAPI', component: TestComponent }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Навигационные guard'ы
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, verifyAuth } = useAuth()
  
  // Проверяем авторизацию при необходимости
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    const isValid = await verifyAuth()
    if (!isValid) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  // Если пользователь авторизован, не пускаем на страницы для гостей
  if (to.meta.requiresGuest && isAuthenticated.value) {
    next({ path: '/' })
    return
  }
  
  next()
})

export default router