<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">模型微调</h1>
      <p class="page-desc">基于已有模型，使用自定义数据进行微调训练</p>
    </div>

    <div class="ft-grid">
      <div class="content-card">
        <div class="card-title">微调配置</div>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
          <el-form-item label="基础模型" prop="base_model_id">
            <el-select v-model="form.base_model_id" placeholder="选择要微调的基础模型" style="width: 100%">
              <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="任务名称" prop="name">
            <el-input v-model="form.name" placeholder="为微调任务命名" />
          </el-form-item>
          <el-form-item label="训练数据" prop="training_file">
            <el-upload :auto-upload="false" :limit="1" accept=".csv" :on-change="f => form.training_file = f.raw" :on-remove="() => form.training_file = null" drag>
              <div style="padding:16px 0">
                <svg viewBox="0 0 20 20" fill="#94a3b8" width="28" height="28"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
                <p style="color:#94a3b8;margin-top:6px;font-size:13px">上传 CSV 训练数据</p>
              </div>
            </el-upload>
          </el-form-item>

          <details class="params-toggle">
            <summary>高级参数</summary>
            <div class="params-grid">
              <el-form-item label="Epochs">
                <el-input-number v-model="form.epochs" :min="1" :max="500" style="width:100%" />
              </el-form-item>
              <el-form-item label="Batch Size">
                <el-input-number v-model="form.batch_size" :min="1" :max="256" style="width:100%" />
              </el-form-item>
              <el-form-item label="Learning Rate">
                <el-input-number v-model="form.learning_rate" :min="0.00001" :max="0.1" :step="0.0001" :precision="5" style="width:100%" />
              </el-form-item>
            </div>
          </details>

          <el-button type="primary" :loading="submitting" @click="handleSubmit" style="width:100%;height:44px;margin-top:12px">提交微调任务</el-button>
        </el-form>
      </div>

      <div class="content-card">
        <div style="display:flex;justify-content:space-between;align-items:center" class="card-title">
          <span>微调任务</span>
          <el-button size="small" text @click="loadTasks">刷新</el-button>
        </div>
        <div v-if="tasks.length === 0 && !tasksLoading" class="empty-state">
          <p>暂无微调任务</p>
        </div>
        <div v-loading="tasksLoading">
          <div v-for="t in tasks" :key="t.id" class="task-item">
            <div class="task-info">
              <div class="task-name">{{ t.name }}</div>
              <div class="task-time">{{ formatDate(t.created_at) }}</div>
            </div>
            <el-tag :type="statusType(t.status)" size="small" round>{{ statusLabel(t.status) }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'

const formRef = ref()
const models = ref([])
const submitting = ref(false)
const tasks = ref([])
const tasksLoading = ref(false)
const form = reactive({ base_model_id: '', name: '', training_file: null, epochs: 50, batch_size: 16, learning_rate: 0.0003 })
const rules = {
  base_model_id: [{ required: true, message: '请选择基础模型', trigger: 'change' }],
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
}

const STATUS_MAP = { pending: { type: 'info', label: '排队中' }, running: { type: 'warning', label: '训练中' }, completed: { type: 'success', label: '已完成' }, failed: { type: 'danger', label: '失败' } }
function statusType(s) { return STATUS_MAP[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP[s]?.label || s }
function formatDate(s) { return s ? new Date(s).toLocaleString('zh-CN') : '-' }

async function loadTasks() {
  tasksLoading.value = true
  try { const { data } = await taskApi.finetuneList(); tasks.value = data.results || data }
  catch {} finally { tasksLoading.value = false }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.training_file) { ElMessage.warning('请上传训练数据'); return }
  const fd = new FormData()
  fd.append('base_model_id', form.base_model_id); fd.append('name', form.name)
  fd.append('training_file', form.training_file); fd.append('epochs', form.epochs)
  fd.append('batch_size', form.batch_size); fd.append('learning_rate', form.learning_rate)
  submitting.value = true
  try { await taskApi.finetune(fd); ElMessage.success('任务已提交'); form.name = ''; form.training_file = null; loadTasks() }
  catch (e) { ElMessage.error(e.response?.data?.detail || '提交失败') }
  finally { submitting.value = false }
}

onMounted(() => { modelApi.list().then(r => models.value = r.data.results || r.data).catch(() => {}); loadTasks() })
</script>

<style scoped>
.ft-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.params-toggle { margin-top: 8px; border: 1px solid var(--border); border-radius: 8px; padding: 0 16px; }
.params-toggle summary { padding: 12px 0; cursor: pointer; color: var(--text-secondary); font-size: 14px; font-weight: 500; }
.params-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; padding-bottom: 12px; }
.task-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--border); }
.task-item:last-child { border-bottom: none; }
.task-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.task-time { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.empty-state { text-align: center; padding: 40px 0; color: var(--text-muted); font-size: 14px; }
</style>
