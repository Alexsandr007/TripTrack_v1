import { useRouter, useRoute } from 'vue-router'

// Основные функции навигации
export const useNavigation = () => {
  const router = useRouter()
  const route = useRoute()
    router.onError((error) => {
  console.log('Router error:', error)
})
  const goToLogin = () => {
    router.push('/login')
  }

  const goToRegister = () => {
    router.push('/register')
  }

  const goToRecovery = () => {
    router.push('/recovery')
  }

  const goToHome = () => {
    router.push('/')
  }

  const goBack = () => {
    router.back()
  }

  const goForward = () => {
    router.forward()
  }

  const navigateTo = (path) => {
    router.push(path)
  }

  return {
    // Текущий маршрут
    currentRoute: route,
    
    // Функции навигации
    goToLogin,
    goToRegister,
    goToRecovery,
    goToHome,
    goBack,
    goForward,
    navigateTo,
    
    // Роутер для сложных операций
    router
  }
}

// Альтернативный вариант - прямые функции (без композабл)
export const navigate = {
  toLogin: () => {
    const router = useRouter()
    router.push('/login')
  },
  
  toRegister: () => {
    const router = useRouter()
    router.push('/register')
  },
  
  toHome: () => {
    const router = useRouter()
    router.push('/')
  },
  
  to: (path) => {
    const router = useRouter()
    router.push(path)
  }
}

// Экспорт по умолчанию для обратной совместимости
export default {
  useNavigation,
  navigate
}