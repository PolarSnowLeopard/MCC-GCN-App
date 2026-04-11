<template>
  <div class="app-layout" v-if="showSidebar">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="16" cy="16" r="6" />
            <circle cx="8" cy="8" r="3" /><line x1="12" y1="12" x2="10" y2="10" />
            <circle cx="24" cy="8" r="3" /><line x1="20" y1="12" x2="22" y2="10" />
            <circle cx="16" cy="26" r="3" /><line x1="16" y1="22" x2="16" y2="24" />
          </svg>
        </div>
        <div>
          <div class="brand-name">MCC-GCN</div>
          <div class="brand-sub">Cocrystal Prediction</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.789l1.599.799L9 4.323V3a1 1 0 011-1z"/></svg>
          <span>单次预测</span>
        </router-link>
        <router-link to="/batch" class="nav-item" :class="{ active: route.path === '/batch' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2h-1.528A6 6 0 004 9.528V4z"/><path fill-rule="evenodd" d="M8 10a4 4 0 00-3.446 6.032l-1.261 1.26a1 1 0 101.414 1.415l1.261-1.261A4 4 0 108 10zm-2 4a2 2 0 114 0 2 2 0 01-4 0z" clip-rule="evenodd"/></svg>
          <span>批量筛选</span>
        </router-link>
        <router-link to="/finetune" class="nav-item" :class="{ active: route.path === '/finetune' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/></svg>
          <span>模型微调</span>
        </router-link>

        <div class="nav-divider"></div>

        <router-link to="/history" class="nav-item" :class="{ active: route.path === '/history' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/></svg>
          <span>历史记录</span>
        </router-link>
        <router-link to="/models" class="nav-item" :class="{ active: route.path === '/models' }">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M3 12v3c0 1.657 3.134 3 7 3s7-1.343 7-3v-3c0 1.657-3.134 3-7 3s-7-1.343-7-3z"/><path d="M3 7v3c0 1.657 3.134 3 7 3s7-1.343 7-3V7c0 1.657-3.134 3-7 3S3 8.657 3 7z"/><path d="M17 5c0 1.657-3.134 3-7 3S3 6.657 3 5s3.134-3 7-3 7 1.343 7 3z"/></svg>
          <span>模型管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info" v-if="userStore.user">
          <div class="user-avatar">{{ userStore.user.username?.[0]?.toUpperCase() }}</div>
          <div class="user-meta">
            <div class="user-name">{{ userStore.user.username }}</div>
            <div class="user-role">{{ userStore.user.role === 'admin' ? '管理员' : '研究员' }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd"/></svg>
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showSidebar = computed(() => route.name !== 'Login' && route.name !== 'Register')

watch(
  () => userStore.isLoggedIn,
  (loggedIn) => {
    if (loggedIn && !userStore.user) {
      userStore.fetchUser().catch(() => {})
    }
  },
  { immediate: true },
)

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style>
:root {
  --sidebar-width: 240px;
  --sidebar-bg: #0f172a;
  --sidebar-hover: #1e293b;
  --sidebar-active: #334155;
  --accent: #3b82f6;
  --accent-light: #60a5fa;
  --bg-primary: #f8fafc;
  --bg-card: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --radius: 10px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
  --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,.07), 0 2px 4px -2px rgba(0,0,0,.05);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px 20px;
  border-bottom: 1px solid rgba(255,255,255,.06);
}

.brand-icon {
  color: var(--accent-light);
  flex-shrink: 0;
}

.brand-name {
  color: #f1f5f9;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: .5px;
}

.brand-sub {
  color: #64748b;
  font-size: 11px;
  margin-top: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  transition: all .15s;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: #e2e8f0;
}

.nav-item.active {
  background: var(--accent);
  color: #fff;
  font-weight: 500;
}

.nav-divider {
  height: 1px;
  background: rgba(255,255,255,.06);
  margin: 10px 14px;
}

.sidebar-footer {
  padding: 14px;
  border-top: 1px solid rgba(255,255,255,.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.user-name {
  color: #e2e8f0;
  font-size: 13px;
  font-weight: 500;
}

.user-role {
  color: #64748b;
  font-size: 11px;
}

.logout-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all .15s;
  display: flex;
}

.logout-btn:hover {
  background: rgba(239,68,68,.15);
  color: #f87171;
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: 32px 36px;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 4px;
}

.content-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.content-card + .content-card {
  margin-top: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.el-button--primary {
  border-radius: 8px !important;
}

.el-input__wrapper, .el-select__wrapper, .el-textarea__inner {
  border-radius: 8px !important;
}

.el-table {
  border-radius: var(--radius) !important;
  overflow: hidden;
}

.el-table th.el-table__cell {
  background: #f8fafc !important;
  color: var(--text-secondary) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  text-transform: uppercase;
  letter-spacing: .5px;
}

.el-dialog {
  border-radius: 14px !important;
}

.el-card {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
</style>
