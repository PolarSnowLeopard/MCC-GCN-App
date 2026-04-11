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
          <span>共晶形成预测与筛选平台</span>
        </div>
      </div>
    </div>
    <div class="auth-right">
      <div class="auth-form-wrap">
        <div class="auth-form-header">
          <h2>创建账号</h2>
          <p>注册以开始使用预测平台</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleRegister" size="large">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="loading" class="auth-btn">注 册</el-button>
          </el-form-item>
        </el-form>
        <div class="auth-switch">
          已有账号？<router-link to="/login">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入有效的邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不少于6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请再次输入密码', trigger: 'blur' }, { validator: validateConfirm, trigger: 'blur' }],
}

function dotStyle(i) {
  const r = () => Math.random()
  return { left: `${r() * 90 + 5}%`, top: `${r() * 90 + 5}%`, animationDelay: `${r() * 6}s`, width: `${4 + r() * 6}px`, height: `${4 + r() * 6}px` }
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.register({ username: form.username, email: form.email, password: form.password })
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    ElMessage.error(data?.detail || data?.username?.[0] || data?.email?.[0] || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; min-height: 100vh; }
.auth-left { flex: 1; background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 50%, #0c4a6e 100%); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.molecule-grid { position: absolute; inset: 0; }
.mol-dot { position: absolute; border-radius: 50%; background: rgba(96,165,250,.15); animation: float 8s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0) scale(1); opacity: .3; } 50% { transform: translateY(-20px) scale(1.3); opacity: .6; } }
.auth-visual { position: relative; z-index: 1; text-align: center; padding: 40px; }
.auth-tagline h1 { font-size: 42px; font-weight: 800; color: #fff; letter-spacing: 3px; }
.auth-tagline p { color: #94a3b8; font-size: 15px; line-height: 1.8; margin-top: 12px; }
.tagline-divider { width: 40px; height: 3px; background: #3b82f6; margin: 20px auto; border-radius: 2px; }
.auth-tagline span { color: #60a5fa; font-size: 14px; letter-spacing: 2px; }
.auth-right { width: 480px; display: flex; align-items: center; justify-content: center; padding: 40px; background: #fff; }
.auth-form-wrap { width: 100%; max-width: 360px; }
.auth-form-header h2 { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.auth-form-header p { color: #94a3b8; font-size: 14px; margin-bottom: 32px; }
.auth-btn { width: 100%; height: 44px; font-size: 15px; border-radius: 10px !important; }
.auth-switch { text-align: center; margin-top: 20px; color: #94a3b8; font-size: 14px; }
.auth-switch a { color: #3b82f6; text-decoration: none; font-weight: 500; }
.auth-switch a:hover { text-decoration: underline; }
</style>
