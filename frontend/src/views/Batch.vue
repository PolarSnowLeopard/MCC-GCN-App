<template>
  <div>
    <h2 style="margin-top: 0">批量筛选</h2>
    <el-card shadow="never">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="选择模型" prop="model_id">
          <el-select v-model="form.model_id" placeholder="请选择模型" style="width: 100%">
            <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="输入方式">
          <el-radio-group v-model="inputMode">
            <el-radio value="text">文本输入</el-radio>
            <el-radio value="file">上传文件</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="inputMode === 'text'" label="分子对列表" prop="pairsText">
          <el-input
            v-model="form.pairsText"
            type="textarea"
            :rows="8"
            placeholder="每行一对，格式：api_smiles,coformer_smiles&#10;例如：&#10;CC(=O)Oc1ccccc1C(=O)O,c1ccc(O)cc1&#10;CC(=O)Nc1ccc(O)cc1,OC(=O)c1ccccc1"
          />
        </el-form-item>

        <el-form-item v-if="inputMode === 'file'" label="CSV 文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".csv"
            :on-change="handleFileChange"
            :on-remove="() => (csvFile = null)"
          >
            <template #trigger>
              <el-button>选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">CSV 文件，两列：api_smiles, coformer_smiles</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            开始筛选
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="results.length" shadow="never" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-weight: 600">筛选结果 ({{ results.length }} 对)</span>
          <el-button type="success" size="small" @click="exportCSV">导出 CSV</el-button>
        </div>
      </template>
      <el-table :data="results" stripe border style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="api_smiles" label="API SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column prop="coformer_smiles" label="Coformer SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column label="预测类别" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="classTagType(row.prediction)" effect="dark">
              Class {{ row.prediction }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="120" align="center">
          <template #default="{ row }">
            {{ row.probabilities ? (Math.max(...row.probabilities) * 100).toFixed(1) + '%' : '-' }}
          </template>
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
const uploadRef = ref()
const models = ref([])
const inputMode = ref('text')
const csvFile = ref(null)
const submitting = ref(false)
const results = ref([])

const form = reactive({ model_id: '', pairsText: '' })

const rules = {
  model_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
}

const TAG_TYPES = ['info', 'success', 'warning', 'danger']
function classTagType(idx) { return TAG_TYPES[idx] || 'info' }

function parsePairsFromText(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [api_smiles, coformer_smiles] = line.split(',').map((s) => s.trim())
      return { api_smiles, coformer_smiles }
    })
    .filter((p) => p.api_smiles && p.coformer_smiles)
}

function handleFileChange(file) {
  csvFile.value = file.raw
}

async function parsePairsFromFile(file) {
  const text = await file.text()
  const lines = text.split('\n').map((l) => l.trim()).filter(Boolean)
  const startIdx = /smiles/i.test(lines[0]) ? 1 : 0
  return lines.slice(startIdx).map((line) => {
    const [api_smiles, coformer_smiles] = line.split(',').map((s) => s.trim())
    return { api_smiles, coformer_smiles }
  }).filter((p) => p.api_smiles && p.coformer_smiles)
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  let pairs = []
  if (inputMode.value === 'text') {
    pairs = parsePairsFromText(form.pairsText)
  } else if (csvFile.value) {
    pairs = await parsePairsFromFile(csvFile.value)
  }

  if (!pairs.length) {
    ElMessage.warning('请输入至少一组分子对')
    return
  }

  submitting.value = true
  results.value = []
  try {
    const { data } = await taskApi.batchPredict({ model_id: form.model_id, pairs })
    if (data.status === 'pending' || data.status === 'processing') {
      ElMessage.info('批量任务已提交，请在历史记录中查看结果')
      return
    }
    const taskResults = data.result || data.results || []
    results.value = Array.isArray(taskResults) ? taskResults : pairs.map((p, i) => ({ ...p, ...taskResults }))
    ElMessage.success('筛选完成')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '筛选失败')
  } finally {
    submitting.value = false
  }
}

function exportCSV() {
  const header = 'API SMILES,Coformer SMILES,Prediction,Confidence'
  const rows = results.value.map((r) => {
    const confidence = r.probabilities ? (Math.max(...r.probabilities) * 100).toFixed(1) + '%' : ''
    return `"${r.api_smiles}","${r.coformer_smiles}",${r.prediction},${confidence}`
  })
  const csv = [header, ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'batch_results.csv'
  a.click()
  URL.revokeObjectURL(url)
}

async function loadModels() {
  try {
    const { data } = await modelApi.list()
    models.value = data.results || data
  } catch {
    ElMessage.error('加载模型列表失败')
  }
}

onMounted(loadModels)
</script>
