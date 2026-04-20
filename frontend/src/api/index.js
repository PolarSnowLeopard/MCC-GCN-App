import axios from 'axios'
import router from '../router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

export default api

export const userApi = {
  login: (data) => api.post('/users/login/', data),
  register: (data) => api.post('/users/register/', data),
  logout: () => api.post('/users/logout/'),
  me: () => api.get('/users/me/'),
}

export const modelApi = {
  list: () => api.get('/models/'),
  create: (formData) => api.post('/models/', formData),
  delete: (id) => api.delete(`/models/${id}/`),
  publish: (id) => api.post(`/models/${id}/publish/`),
}

export const taskApi = {
  predict: (data) => api.post('/tasks/predict/', data),
  batchPredict: (data) => api.post('/tasks/batch/', data),
  list: (params) => api.get('/tasks/', { params }),
  detail: (id) => api.get(`/tasks/${id}/`),
  finetune: (formData) => api.post('/tasks/finetune/', formData),
  finetuneList: () => api.get('/tasks/finetune/list/'),
  finetuneDetail: (id) => api.get(`/tasks/finetune/${id}/`),
}
