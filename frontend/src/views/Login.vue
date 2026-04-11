<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh">
    <el-card style="width: 380px">
      <template #header><h3 style="text-align: center">MCC-GCN 共晶预测平台</h3></template>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
        <el-form-item><el-button type="primary" native-type="submit" style="width:100%">登录</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({ username: '', password: '' })

function handleLogin() {
  // TODO: API call
}
</script>
