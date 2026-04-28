import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
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

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && to.name !== 'Register' && !token) {
    return { name: 'Login' }
  }
})

// When a redeploy invalidates the chunks that the currently cached
// index.html is referencing, dynamic imports start failing with messages
// like "Failed to fetch dynamically imported module" or "Loading chunk
// failed". The cleanest recovery is a hard reload, which fetches the new
// index.html (no-store on nginx) and therefore the new chunk hashes.
//
// A sessionStorage flag prevents an infinite reload loop in the very
// unlikely case that the failure has nothing to do with stale chunks.
const RELOAD_FLAG = 'mcc-chunk-reload-attempted'
const CHUNK_ERROR_RE =
  /dynamically imported module|Loading chunk \w+ failed|Importing a module script failed/i

router.onError((error, to) => {
  const msg = error?.message || String(error)
  if (!CHUNK_ERROR_RE.test(msg)) return

  if (sessionStorage.getItem(RELOAD_FLAG)) {
    console.error('[router] chunk load still failing after reload:', error)
    return
  }
  sessionStorage.setItem(RELOAD_FLAG, '1')
  window.location.assign(to?.fullPath || window.location.pathname)
})

router.afterEach(() => {
  sessionStorage.removeItem(RELOAD_FLAG)
})

export default router
