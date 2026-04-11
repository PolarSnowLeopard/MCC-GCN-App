<template>
  <el-container style="min-height: 100vh">
    <el-aside v-if="route.name !== 'Login'" width="200px">
      <el-menu :default-active="route.path" router style="height: 100%">
        <div style="padding: 16px; text-align: center; font-weight: bold; font-size: 16px">
          MCC-GCN
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
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { Monitor, Document, Setting, Clock, Files } from '@element-plus/icons-vue'

const route = useRoute()
</script>
