import axios from 'axios'
import { useAuth } from './useAuth'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'

export function useAxios() {
  const { getAuthHeader } = useAuth()

  const api = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // Добавляем interceptor для авторизации
  api.interceptors.request.use(
    (config) => {
      const authHeader = getAuthHeader()
      if (authHeader.Authorization) {
        config.headers.Authorization = authHeader.Authorization
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  return { api }
}