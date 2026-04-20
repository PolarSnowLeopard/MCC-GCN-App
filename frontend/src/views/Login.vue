<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="auth-visual">
        <div class="molecule-grid">
          <div class="mol-dot" v-for="i in 20" :key="i" :style="dotStyle(i)"></div>
        </div>
        <div class="auth-tagline">
          <h1>MCC-GCN</h1>
          <p>Multi-Component Crystal<br/>Graph Convolutional Network</p>
          <div class="tagline-divider"></div>
          <span>{{ $t('auth.platformSlogan') }}</span>
        </div>
      </div>
    </div>
    <div class="auth-right">
      <div class="auth-form-wrap">
        <div class="auth-form-header">
          <h2>{{ $t('auth.welcomeBack') }}</h2>
          <p>{{ $t('auth.loginSubtitle') }}</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin" size="large">
          <el-form-item :label="$t('auth.username')" prop="username">
            <el-input v-model="form.username" :placeholder="$t('auth.usernamePlaceholder')" />
          </el-form-item>
          <el-form-item :label="$t('auth.password')" prop="password">
            <el-input v-model="form.password" type="password" :placeholder="$t('auth.passwordPlaceholder')" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="loading" class="auth-btn">{{ $t('auth.login') }}</el-button>
          </el-form-item>
        </el-form>
        <div class="auth-switch">
          {{ $t('auth.noAccount') }}<router-link to="/register">{{ $t('auth.goRegister') }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = computed(() => ({
  username: [{ required: true, message: t('auth.usernameRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('auth.passwordRequired'), trigger: 'blur' }],
}))

function dotStyle(i) {
  const r = () => Math.random()
  return { left: `${r() * 90 + 5}%`, top: `${r() * 90 + 5}%`, animationDelay: `${r() * 6}s`, width: `${4 + r() * 6}px`, height: `${4 + r() * 6}px` }
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success(t('auth.loginSuccess'))
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.response?.data?.non_field_errors?.[0] || t('auth.loginFailed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; min-height: 100vh; }

.auth-left {
  flex: 1;
  background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.molecule-grid { position: absolute; inset: 0; }

.mol-dot {
  position: absolute;
  border-radius: 50%;
  background: rgba(96,165,250,.15);
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); opacity: .3; }
  50% { transform: translateY(-20px) scale(1.3); opacity: .6; }
}

.auth-visual { position: relative; z-index: 1; text-align: center; padding: 40px; }

.auth-tagline h1 {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 3px;
}

.auth-tagline p {
  color: #94a3b8;
  font-size: 15px;
  line-height: 1.8;
  margin-top: 12px;
}

.tagline-divider {
  width: 40px;
  height: 3px;
  background: #3b82f6;
  margin: 20px auto;
  border-radius: 2px;
}

.auth-tagline span {
  color: #60a5fa;
  font-size: 14px;
  letter-spacing: 2px;
}

.auth-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.auth-form-wrap { width: 100%; max-width: 360px; }

.auth-form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.auth-form-header p {
  color: #94a3b8;
  font-size: 14px;
  margin-bottom: 32px;
}

.auth-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  border-radius: 10px !important;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  color: #94a3b8;
  font-size: 14px;
}

.auth-switch a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.auth-switch a:hover { text-decoration: underline; }
</style>
