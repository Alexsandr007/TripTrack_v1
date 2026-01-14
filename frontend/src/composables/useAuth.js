import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'

const token = ref(localStorage.getItem('token') || null)
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const isLoading = ref(false)
const error = ref(null)

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null

      console.log('Отправка запроса на:', `${API_URL}/auth/login/`)
      console.log('Данные:', credentials)

      const response = await axios.post(`${API_URL}/auth/login/`, {
        login: credentials.username,
        password: credentials.password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('Ответ сервера:', response.data)

      if (response.data.success) {
        token.value = response.data.token
        user.value = response.data.user

        // Сохраняем в localStorage
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true }
      } else {
        error.value = response.data.error || 'Ошибка авторизации'
        return { 
          success: false, 
          error: error.value 
        }
      }
    } catch (err) {
      console.error('Ошибка авторизации:', err)
      
      let errorMessage = 'Ошибка при подключении к серверу'
      
      if (err.response) {
        console.log('Статус ошибки:', err.response.status)
        console.log('Данные ошибки:', err.response.data)
        
        if (err.response.status === 401) {
          errorMessage = 'Неверный логин или пароль'
        } else if (err.response.data?.error) {
          errorMessage = err.response.data.error
        } else if (err.response.data?.errors) {
          errorMessage = Object.values(err.response.data.errors).flat().join(', ')
        }
      }
      
      error.value = errorMessage
      return { 
        success: false, 
        error: errorMessage 
      }
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await axios.post(`${API_URL}/auth/logout/`, {}, {
          headers: {
            'Authorization': `Token ${token.value}`
          }
        })
      }
    } catch (err) {
      console.error('Ошибка при выходе:', err)
    } finally {
      // Очищаем данные в любом случае
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
  }

  const verifyAuth = async () => {
    if (!token.value) {
      return false
    }

    try {
      const response = await axios.get(`${API_URL}/auth/verify/`, {
        headers: {
          'Authorization': `Token ${token.value}`
        }
      })

      if (response.data.success) {
        user.value = response.data.user
        return true
      }
    } catch (err) {
      console.error('Ошибка проверки авторизации:', err)
      // Если токен невалиден, очищаем
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }

    return false
  }

  const getAuthHeader = () => {
    return token.value ? { 'Authorization': `Token ${token.value}` } : {}
  }

  return {
    token: computed(() => token.value),
    user: computed(() => user.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    isAuthenticated,
    login,
    logout,
    verifyAuth,
    getAuthHeader
  }
}