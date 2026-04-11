<template>
  <div>
    <h2 style="margin-top: 0">模型微调</h2>

    <el-card shadow="never">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="基础模型" prop="base_model_id">
          <el-select v-model="form.base_model_id" placeholder="请选择基础模型" style="width: 100%">
            <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="给微调任务起个名字" />
        </el-form-item>
        <el-form-item label="训练数据" prop="training_file">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".csv"
            :on-change="(f) => (form.training_file = f.raw)"
            :on-remove="() => (form.training_file = null)"
          >
            <template #trigger>
              <el-button>选择 CSV 文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">CSV 格式训练数据</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-collapse style="margin-bottom: 20px">
          <el-collapse-item title="超参数设置" name="params">
            <el-form-item label="Epochs">
              <el-input-number v-model="form.epochs" :min="1" :max="500" />
            </el-form-item>
            <el-form-item label="Batch Size">
              <el-input-number v-model="form.batch_size" :min="1" :max="256" />
            </el-form-item>
            <el-form-item label="Learning Rate">
              <el-input-number v-model="form.learning_rate" :min="0.00001" :max="0.1" :step="0.0001" :precision="5" />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            开始微调
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">微调任务列表</span>
          <el-button size="small" @click="loadTasks">刷新</el-button>
        </div>
      </template>
      <el-table :data="tasks" v-loading="tasksLoading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="160" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
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

const form = reactive({
  base_model_id: '',
  name: '',
  training_file: null,
  epochs: 50,
  batch_size: 16,
  learning_rate: 0.0003,
})

const rules = {
  base_model_id: [{ required: true, message: '请选择基础模型', trigger: 'change' }],
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  training_file: [{ required: true, message: '请上传训练数据', trigger: 'change' }],
}

const STATUS_MAP = {
  pending: { type: 'info', label: '等待中' },
  processing: { type: 'warning', label: '处理中' },
  completed: { type: 'success', label: '已完成' },
  success: { type: 'success', label: '已完成' },
  failed: { type: 'danger', label: '失败' },
}

function statusType(s) { return STATUS_MAP[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP[s]?.label || s }
function formatDate(str) { return str ? new Date(str).toLocaleString('zh-CN') : '-' }

async function loadModels() {
  try {
    const { data } = await modelApi.list()
    models.value = data.results || data
  } catch {
    ElMessage.error('加载模型列表失败')
  }
}

async function loadTasks() {
  tasksLoading.value = true
  try {
    const { data } = await taskApi.finetuneList()
    tasks.value = data.results || data
  } catch {
    ElMessage.error('加载微调任务失败')
  } finally {
    tasksLoading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.training_file) {
    ElMessage.warning('请上传训练数据文件')
    return
  }

  const fd = new FormData()
  fd.append('base_model_id', form.base_model_id)
  fd.append('name', form.name)
  fd.append('training_file', form.training_file)
  fd.append('epochs', form.epochs)
  fd.append('batch_size', form.batch_size)
  fd.append('learning_rate', form.learning_rate)

  submitting.value = true
  try {
    await taskApi.finetune(fd)
    ElMessage.success('微调任务已提交')
    form.name = ''
    form.training_file = null
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadModels()
  loadTasks()
})
</script>
