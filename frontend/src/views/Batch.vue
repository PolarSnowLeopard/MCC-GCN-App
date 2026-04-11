<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">批量筛选</h1>
      <p class="page-desc">上传或输入多组分子对，批量预测共晶形成</p>
    </div>

    <div class="content-card">
      <div class="card-title">数据输入</div>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
        <el-form-item label="选择模型" prop="model_id">
          <el-select v-model="form.model_id" placeholder="请选择模型" style="width: 100%">
            <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="输入方式">
          <el-segmented v-model="inputMode" :options="[{label:'文本输入',value:'text'},{label:'上传 CSV',value:'file'}]" />
        </el-form-item>
        <el-form-item v-if="inputMode === 'text'" label="分子对列表">
          <el-input v-model="form.pairsText" type="textarea" :rows="8"
            placeholder="每行一对，格式：api_smiles,coformer_smiles&#10;&#10;CC(=O)Oc1ccccc1C(=O)O,c1ccc(O)cc1&#10;CC(=O)Nc1ccc(O)cc1,OC(=O)c1ccccc1" />
        </el-form-item>
        <el-form-item v-else label="CSV 文件">
          <el-upload :auto-upload="false" :limit="1" accept=".csv" :on-change="handleFileChange" :on-remove="() => (csvFile = null)" drag>
            <div style="padding:20px 0">
              <svg viewBox="0 0 20 20" fill="#94a3b8" width="32" height="32"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
              <p style="color:#94a3b8;margin-top:8px;font-size:13px">拖拽文件到此处，或点击上传</p>
              <p style="color:#cbd5e1;font-size:12px;margin-top:4px">CSV 格式，两列：api_smiles, coformer_smiles</p>
            </div>
          </el-upload>
        </el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleSubmit" style="height:44px;font-size:15px">开始筛选</el-button>
      </el-form>
    </div>

    <div class="content-card" v-if="results.length">
      <div style="display:flex;justify-content:space-between;align-items:center" class="card-title">
        <span>筛选结果 <el-tag round size="small" type="info">{{ results.length }} 组</el-tag></span>
        <el-button size="small" @click="exportCSV">导出 CSV</el-button>
      </div>
      <el-table :data="results" stripe style="width: 100%" :header-cell-style="{background:'#f8fafc'}">
        <el-table-column type="index" label="#" width="56" />
        <el-table-column prop="api_smiles" label="API SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column prop="coformer_smiles" label="Coformer SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column label="预测" width="120" align="center">
          <template #default="{ row }">
            <el-tag :color="CLASS_COLORS[row.prediction]" style="color:#fff;border:none" size="small" round>
              {{ CLASS_LABELS[row.prediction] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="100" align="center">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.probabilities ? (Math.max(...row.probabilities) * 100).toFixed(1) + '%' : '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'

const formRef = ref()
const models = ref([])
const inputMode = ref('text')
const csvFile = ref(null)
const submitting = ref(false)
const results = ref([])
const form = reactive({ model_id: '', pairsText: '' })
const rules = { model_id: [{ required: true, message: '请选择模型', trigger: 'change' }] }
const CLASS_COLORS = ['#94a3b8', '#f59e0b', '#22c55e', '#3b82f6']
const CLASS_LABELS = ['Negative', 'Salt', 'Cocrystal', 'Hydrate/Solvate']

function parsePairsFromText(text) {
  return text.split('\n').map(l => l.trim()).filter(Boolean).map(l => {
    const [api_smiles, coformer_smiles] = l.split(',').map(s => s.trim())
    return { api_smiles, coformer_smiles }
  }).filter(p => p.api_smiles && p.coformer_smiles)
}
function handleFileChange(file) { csvFile.value = file.raw }
async function parsePairsFromFile(file) {
  const text = await file.text()
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)
  const start = /smiles/i.test(lines[0]) ? 1 : 0
  return lines.slice(start).map(l => { const [a, c] = l.split(',').map(s => s.trim()); return { api_smiles: a, coformer_smiles: c } }).filter(p => p.api_smiles && p.coformer_smiles)
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  let pairs = inputMode.value === 'text' ? parsePairsFromText(form.pairsText) : csvFile.value ? await parsePairsFromFile(csvFile.value) : []
  if (!pairs.length) { ElMessage.warning('请输入至少一组分子对'); return }
  submitting.value = true; results.value = []
  try {
    const { data } = await taskApi.batchPredict({ model_id: form.model_id, pairs })
    if (data.status === 'pending') { ElMessage.info('批量任务已提交，请在历史记录中查看'); return }
    results.value = Array.isArray(data.result || data.results) ? (data.result || data.results) : []
    ElMessage.success('筛选完成')
  } catch (e) { ElMessage.error(e.response?.data?.detail || '筛选失败') }
  finally { submitting.value = false }
}

function exportCSV() {
  const header = 'API SMILES,Coformer SMILES,Prediction,Label,Confidence'
  const rows = results.value.map(r => `"${r.api_smiles}","${r.coformer_smiles}",${r.prediction},${CLASS_LABELS[r.prediction]},${r.probabilities ? (Math.max(...r.probabilities)*100).toFixed(1)+'%' : ''}`)
  const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv;charset=utf-8;' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'batch_results.csv'; a.click()
}

onMounted(async () => { try { const { data } = await modelApi.list(); models.value = data.results || data } catch {} })
</script>
