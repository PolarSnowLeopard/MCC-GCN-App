<template>
  <el-container style="min-height: 100vh">
    <el-aside v-if="showSidebar" width="220px" style="background: #001529">
      <el-menu
        :default-active="route.path"
        router
        background-color="#001529"
        text-color="#ffffffb3"
        active-text-color="#409eff"
        style="height: 100%; display: flex; flex-direction: column; border-right: none"
      >
        <div style="padding: 20px 16px 12px; text-align: center; color: #fff">
          <div style="font-weight: 700; font-size: 17px; letter-spacing: 1px">MCC-GCN</div>
          <div style="font-size: 12px; color: #ffffffa0; margin-top: 4px">共晶预测平台</div>
        </div>

        <div v-if="userStore.user" style="padding: 6px 20px 14px; text-align: center; color: #ffffffb3; font-size: 13px; border-bottom: 1px solid #ffffff1a">
          <el-icon :size="14" style="vertical-align: -2px"><User /></el-icon>
          {{ userStore.user.username }}
        </div>

        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>单次预测</span>
        </el-menu-item>
        <el-menu-item index="/batch">
          <el-icon><Document /></el-icon>
          <span>批量筛选</span>
        </el-menu-item>
        <el-menu-item index="/finetune">
          <el-icon><Setting /></el-icon>
          <span>模型微调</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
        <el-menu-item index="/models">
          <el-icon><Files /></el-icon>
          <span>模型管理</span>
        </el-menu-item>

        <div style="flex: 1"></div>

        <div style="padding: 12px 16px; border-top: 1px solid #ffffff1a">
          <el-button
            type="danger"
            plain
            style="width: 100%"
            @click="handleLogout"
          >
            退出登录
          </el-button>
        </div>
      </el-menu>
    </el-aside>
    <el-main style="background: #f5f7fa; padding: 24px">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Monitor, Document, Setting, Clock, Files, User } from '@element-plus/icons-vue'
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
