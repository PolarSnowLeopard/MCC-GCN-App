import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', name: 'Predict', component: () => import('../views/Predict.vue') },
  { path: '/batch', name: 'Batch', component: () => import('../views/Batch.vue') },
  { path: '/finetune', name: 'Finetune', component: () => import('../views/Finetune.vue') },
  { path: '/history', name: 'History', component: () => import('../views/History.vue') },
  { path: '/models', name: 'Models', component: () => import('../views/Models.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
