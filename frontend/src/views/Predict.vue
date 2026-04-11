<template>
  <div>
    <h2 style="margin-top: 0">单次预测</h2>
    <el-card shadow="never">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="选择模型" prop="model_id">
          <el-select
            v-model="form.model_id"
            placeholder="请选择模型"
            style="width: 100%"
            :loading="modelsLoading"
          >
            <el-option
              v-for="m in models"
              :key="m.id"
              :label="m.name"
              :value="m.id"
            >
              <span>{{ m.name }}</span>
              <span style="float: right; color: #909399; font-size: 12px">{{ m.model_type }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="药物 SMILES" prop="api_smiles">
          <el-input v-model="form.api_smiles" placeholder="输入 API (药物) 的 SMILES 字符串" />
        </el-form-item>
        <el-form-item label="辅料 SMILES" prop="coformer_smiles">
          <el-input v-model="form.coformer_smiles" placeholder="输入 Coformer (辅料) 的 SMILES 字符串" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="predicting" @click="handlePredict">
            预 测
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="result" shadow="never" style="margin-top: 20px">
      <template #header>
        <span style="font-weight: 600">预测结果</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="API SMILES">{{ result.api_smiles }}</el-descriptions-item>
        <el-descriptions-item label="Coformer SMILES">{{ result.coformer_smiles }}</el-descriptions-item>
        <el-descriptions-item label="预测类别">
          <el-tag :type="classTagType(result.prediction)" size="large" effect="dark">
            Class {{ result.prediction }} - {{ classLabel(result.prediction) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预测标签">{{ result.label }}</el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px">
        <h4 style="margin-bottom: 12px">各类别概率</h4>
        <div v-for="(prob, idx) in result.probabilities" :key="idx" style="margin-bottom: 10px">
          <div style="display: flex; align-items: center; gap: 10px">
            <span style="width: 80px; font-size: 13px; color: #606266">Class {{ idx }}</span>
            <el-progress
              :percentage="+(prob * 100).toFixed(1)"
              :color="classColor(idx)"
              :stroke-width="20"
              :text-inside="true"
              style="flex: 1"
            />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'

const formRef = ref()
const models = ref([])
const modelsLoading = ref(false)
const predicting = ref(false)
const result = ref(null)

const form = reactive({
  model_id: '',
  api_smiles: '',
  coformer_smiles: '',
})

const rules = {
  model_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
  api_smiles: [{ required: true, message: '请输入药物 SMILES', trigger: 'blur' }],
  coformer_smiles: [{ required: true, message: '请输入辅料 SMILES', trigger: 'blur' }],
}

const CLASS_COLORS = ['#909399', '#67c23a', '#e6a23c', '#f56c6c']
const CLASS_LABELS = ['无共晶', '共晶 I', '共晶 II', '共晶 III']
const TAG_TYPES = ['info', 'success', 'warning', 'danger']

function classColor(idx) { return CLASS_COLORS[idx] || '#909399' }
function classLabel(idx) { return CLASS_LABELS[idx] || `Class ${idx}` }
function classTagType(idx) { return TAG_TYPES[idx] || 'info' }

async function loadModels() {
  modelsLoading.value = true
  try {
    const { data } = await modelApi.list()
    models.value = data.results || data
  } catch {
    ElMessage.error('加载模型列表失败')
  } finally {
    modelsLoading.value = false
  }
}

async function handlePredict() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  predicting.value = true
  result.value = null
  try {
    const { data } = await taskApi.predict({
      model_id: form.model_id,
      api_smiles: form.api_smiles,
      coformer_smiles: form.coformer_smiles,
    })
    result.value = data.result || data
    ElMessage.success('预测完成')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '预测失败')
  } finally {
    predicting.value = false
  }
}

onMounted(loadModels)
</script>
