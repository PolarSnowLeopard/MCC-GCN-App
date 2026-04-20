<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ $t('batch.title') }}</h1>
      <p class="page-desc">{{ $t('batch.desc') }}</p>
    </div>

    <div class="content-card">
      <div class="card-title">{{ $t('batch.dataInput') }}</div>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
        <el-form-item :label="$t('predict.selectModel')" prop="model_id">
          <el-select v-model="form.model_id" :placeholder="$t('predict.selectModelPlaceholder')" style="width: 100%">
            <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('batch.dataInput')">
          <el-segmented v-model="inputMode" :options="inputModeOptions" />
        </el-form-item>

        <div v-if="inputMode === 'text'">
          <div class="input-hint">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
            <div>
              <div>{{ $t('batch.formatHint') }}</div>
              <code class="hint-example">CCO,O=C(O)c1ccccc1O</code>
            </div>
          </div>
          <el-form-item :label="''">
            <el-input v-model="form.pairsText" type="textarea" :rows="8"
              :placeholder="$t('batch.pairsPlaceholder')" />
          </el-form-item>
        </div>

        <div v-else>
          <div class="input-hint">
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
            <div>
              <div>{{ $t('batch.formatHint') }}</div>
              <code class="hint-example">CCO,O=C(O)c1ccccc1O</code>
            </div>
          </div>
          <div class="upload-row">
            <el-form-item :label="$t('batch.csvFile')" class="upload-item">
              <el-upload :auto-upload="false" :limit="1" accept=".csv" :on-change="handleFileChange" :on-remove="() => (csvFile = null)" drag>
                <div style="padding:20px 0">
                  <svg viewBox="0 0 20 20" fill="#94a3b8" width="32" height="32"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
                  <p style="color:#94a3b8;margin-top:8px;font-size:13px">{{ $t('batch.dragUpload') }}</p>
                  <p style="color:#cbd5e1;font-size:12px;margin-top:4px">{{ $t('batch.csvFormat') }}</p>
                </div>
              </el-upload>
            </el-form-item>
            <el-button class="template-btn" @click="downloadTemplate">
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              {{ $t('batch.downloadTemplate') }}
            </el-button>
          </div>
        </div>

        <el-button type="primary" :loading="submitting" :disabled="polling" @click="handleSubmit" style="height:44px;font-size:15px">
          {{ $t('batch.startScreen') }}
        </el-button>
      </el-form>
    </div>

    <!-- Polling status -->
    <div class="content-card poll-status" v-if="polling">
      <div class="poll-inner">
        <el-progress :percentage="pollProgress" :stroke-width="8" :show-text="false" status="primary" style="flex:1" />
        <div class="poll-text">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span v-if="taskStatus === 'pending'">{{ $t('batch.taskQueued') }}</span>
          <span v-else-if="taskStatus === 'running'">{{ $t('batch.taskRunning') }}</span>
          <span v-else>{{ $t('batch.polling') }}</span>
        </div>
      </div>
    </div>

    <div class="content-card" v-if="results.length">
      <div style="display:flex;justify-content:space-between;align-items:center" class="card-title">
        <span>{{ $t('batch.title') }} <el-tag round size="small" type="info">{{ $t('batch.resultCount', { count: results.length }) }}</el-tag></span>
        <el-button size="small" @click="exportCSV">{{ $t('common.export') }}</el-button>
      </div>
      <el-table :data="results" stripe style="width: 100%" :header-cell-style="{background:'#f8fafc'}" :row-class-name="rowClassName">
        <el-table-column type="index" label="#" width="56" />
        <el-table-column prop="api_smiles" label="API SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column prop="coformer_smiles" label="Coformer SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column :label="$t('batch.prediction')" width="120" align="center">
          <template #default="{ row }">
            <el-tag :color="CLASS_COLORS[row.prediction]" style="color:#fff;border:none" size="small" round>
              {{ CLASS_LABELS[row.prediction] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('batch.confidenceCol')" width="100" align="center">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.probabilities ? (Math.max(...row.probabilities) * 100).toFixed(1) + '%' : '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { modelApi, taskApi } from '../api'

const { t } = useI18n()

const formRef = ref()
const models = ref([])
const inputMode = ref('text')
const csvFile = ref(null)
const submitting = ref(false)
const results = ref([])
const form = reactive({ model_id: '', pairsText: '' })

const polling = ref(false)
const taskStatus = ref('')
const pollProgress = ref(0)
let pollTimer = null
let pollTaskId = null

const rules = computed(() => ({
  model_id: [{ required: true, message: t('predict.modelRequired'), trigger: 'change' }],
}))
const inputModeOptions = computed(() => [
  { label: t('batch.textInput'), value: 'text' },
  { label: t('batch.uploadCsv'), value: 'file' },
])
const CLASS_COLORS = ['#94a3b8', '#f59e0b', '#22c55e', '#3b82f6']
const CLASS_LABELS = ['Negative', 'Salt', 'Cocrystal', 'Solvate']
const ROW_BG = ['rgba(148,163,184,0.08)', 'rgba(245,158,11,0.08)', 'rgba(34,197,94,0.08)', 'rgba(59,130,246,0.08)']

function rowClassName({ row }) {
  const cls = row.prediction
  if (cls === 0) return 'row-class-0'
  if (cls === 1) return 'row-class-1'
  if (cls === 2) return 'row-class-2'
  if (cls === 3) return 'row-class-3'
  return ''
}

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
  return lines.slice(start).map(l => {
    const [a, c] = l.split(',').map(s => s.trim())
    return { api_smiles: a, coformer_smiles: c }
  }).filter(p => p.api_smiles && p.coformer_smiles)
}

function downloadTemplate() {
  const csv = 'api_smiles,coformer_smiles\nCCO,O=C(O)c1ccccc1O\nO=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]\n'
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'batch_template.csv'
  a.click()
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  polling.value = false
  pollTaskId = null
  taskStatus.value = ''
  pollProgress.value = 0
}

function startPolling(taskId) {
  pollTaskId = taskId
  polling.value = true
  taskStatus.value = 'pending'
  pollProgress.value = 10
  let ticks = 0

  pollTimer = setInterval(async () => {
    ticks++
    try {
      const { data } = await taskApi.detail(taskId)
      taskStatus.value = data.status

      if (data.status === 'pending') {
        pollProgress.value = Math.min(30, 10 + ticks * 2)
      } else if (data.status === 'running') {
        pollProgress.value = Math.min(85, 30 + ticks * 3)
      }

      if (data.status === 'completed') {
        pollProgress.value = 100
        stopPolling()
        results.value = Array.isArray(data.result || data.results) ? (data.result || data.results) : []
        ElMessage.success(t('batch.screenSuccess'))
      } else if (data.status === 'failed') {
        stopPolling()
        ElMessage.error(data.error || t('batch.screenFailed'))
      }
    } catch {
      stopPolling()
      ElMessage.error(t('batch.screenFailed'))
    }
  }, 3000)
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  let pairs = inputMode.value === 'text'
    ? parsePairsFromText(form.pairsText)
    : csvFile.value ? await parsePairsFromFile(csvFile.value) : []
  if (!pairs.length) { ElMessage.warning(t('batch.atLeastOne')); return }

  submitting.value = true
  results.value = []
  try {
    const { data } = await taskApi.batchPredict({ model_id: form.model_id, pairs })
    if (data.task_id && data.status === 'pending') {
      ElMessage.info(t('batch.taskSubmitted'))
      startPolling(data.task_id)
    } else {
      results.value = Array.isArray(data.result || data.results) ? (data.result || data.results) : []
      ElMessage.success(t('batch.screenSuccess'))
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('batch.screenFailed'))
  } finally {
    submitting.value = false
  }
}

function exportCSV() {
  const header = 'API SMILES,Coformer SMILES,Prediction,Label,Confidence'
  const rows = results.value.map(r =>
    `"${r.api_smiles}","${r.coformer_smiles}",${r.prediction},${CLASS_LABELS[r.prediction]},${r.probabilities ? (Math.max(...r.probabilities) * 100).toFixed(1) + '%' : ''}`
  )
  const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv;charset=utf-8;' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'batch_results.csv'
  a.click()
}

onMounted(async () => {
  try {
    const { data } = await modelApi.list()
    models.value = data.results || data
  } catch {}
})

onBeforeUnmount(() => { stopPolling() })
</script>

<style scoped>
.input-hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #1e40af;
  font-size: 12px;
  line-height: 1.6;
  margin-bottom: 16px;
}
.input-hint svg { flex-shrink: 0; margin-top: 2px; }
.hint-example {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: #1e40af;
  font-family: monospace;
}

.upload-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.upload-item { flex: 1; }

.template-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 40px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px dashed #93c5fd;
  background: #eff6ff;
  color: #2563eb;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  margin-top: 30px;
  transition: all .2s;
}
.template-btn:hover {
  background: #dbeafe;
  border-color: #60a5fa;
}

.poll-status {
  border: 1px solid #dbeafe;
  background: #f0f7ff;
}
.poll-inner {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.poll-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #2563eb;
  font-weight: 500;
}
.poll-text .is-loading { font-size: 16px; }

:deep(.row-class-0 td) { background: rgba(148,163,184,0.06) !important; }
:deep(.row-class-1 td) { background: rgba(245,158,11,0.06) !important; }
:deep(.row-class-2 td) { background: rgba(34,197,94,0.06) !important; }
:deep(.row-class-3 td) { background: rgba(59,130,246,0.06) !important; }
</style>
