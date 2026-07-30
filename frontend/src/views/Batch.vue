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

        <el-alert
          v-if="validationErrors.length"
          class="validation-alert"
          type="error"
          :closable="false"
          show-icon
        >
          <template #title>
            {{ $t('batch.validationTitle', { count: validationErrors.length }) }}
          </template>
          <ul class="validation-list">
            <li v-for="(error, index) in validationErrors" :key="`${error.row}-${error.field}-${index}`">
              {{ $t('batch.rowLabel', { row: error.row }) }}: {{ error.message }}
            </li>
          </ul>
        </el-alert>
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
        <span class="result-summary">
          {{ $t('batch.title') }}
          <el-tag round size="small" type="success">{{ $t('batch.successCount', { count: successCount }) }}</el-tag>
          <el-tag v-if="failureCount" round size="small" type="danger">{{ $t('batch.failureCount', { count: failureCount }) }}</el-tag>
        </span>
        <el-button size="small" @click="exportCSV">{{ $t('common.export') }}</el-button>
      </div>
      <el-table :data="results" stripe style="width: 100%" :header-cell-style="{background:'#f8fafc'}" :row-class-name="rowClassName">
        <el-table-column type="index" label="#" width="56" />
        <el-table-column prop="api_smiles" label="API SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column prop="coformer_smiles" label="Coformer SMILES" min-width="200" show-overflow-tooltip />
        <el-table-column :label="$t('batch.prediction')" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.error" type="danger" size="small" round>
              {{ $t('batch.invalidRow') }}
            </el-tag>
            <el-tag v-else :color="CLASS_COLORS[row.prediction]" style="color:#fff;border:none" size="small" round>
              {{ CLASS_LABELS[row.prediction] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('batch.confidenceCol')" width="100" align="center">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.probabilities ? (Math.max(...row.probabilities) * 100).toFixed(1) + '%' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="failureCount" prop="error" :label="$t('batch.errorDetails')" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="row-error-message">{{ row.error || '-' }}</span>
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
import Papa from 'papaparse'
import { modelApi, taskApi } from '../api'

const { t } = useI18n()

const formRef = ref()
const models = ref([])
const inputMode = ref('text')
const csvFile = ref(null)
const submitting = ref(false)
const results = ref([])
const validationErrors = ref([])
const form = reactive({ model_id: '', pairsText: '' })
const successCount = computed(() => results.value.filter(row => !row.error).length)
const failureCount = computed(() => results.value.filter(row => row.error).length)

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
  if (row.error) return 'row-error'
  const cls = row.prediction
  if (cls === 0) return 'row-class-0'
  if (cls === 1) return 'row-class-1'
  if (cls === 2) return 'row-class-2'
  if (cls === 3) return 'row-class-3'
  return ''
}

function parsePairs(text) {
  const parsed = Papa.parse(text.replace(/^\uFEFF/, ''), {
    skipEmptyLines: 'greedy',
  })
  const rows = parsed.data
  const hasHeader = rows.length > 0 && rows[0].some(cell => /smiles/i.test(String(cell)))
  const start = hasHeader ? 1 : 0
  const pairs = []
  const rowNumbers = []
  const errors = parsed.errors.map(error => ({
    row: error.row + 1,
    field: 'csv',
    message: error.message,
  }))

  rows.slice(start).forEach((row, index) => {
    const rowNumber = start + index + 1
    if (row.length !== 2) {
      errors.push({
        row: rowNumber,
        field: 'csv',
        message: t('batch.invalidColumnCount'),
      })
      return
    }

    const [apiSmiles, coformerSmiles] = row.map(cell => String(cell).trim())
    if (!apiSmiles || !coformerSmiles) {
      errors.push({
        row: rowNumber,
        field: 'csv',
        message: t('batch.emptySmiles'),
      })
      return
    }

    pairs.push({
      api_smiles: apiSmiles,
      coformer_smiles: coformerSmiles,
    })
    rowNumbers.push(rowNumber)
  })

  return { pairs, rowNumbers, errors }
}

function handleFileChange(file) {
  csvFile.value = file.raw
  validationErrors.value = []
}

async function parsePairsFromFile(file) {
  return parsePairs(await file.text())
}

function extractPairErrors(data, rowNumbers) {
  if (!Array.isArray(data?.pairs)) return []
  const errors = []
  data.pairs.forEach((rowErrors, index) => {
    if (!rowErrors || typeof rowErrors !== 'object') return
    Object.entries(rowErrors).forEach(([field, messages]) => {
      const values = Array.isArray(messages) ? messages : [messages]
      values.forEach(message => {
        errors.push({
          row: rowNumbers[index] || index + 1,
          field,
          message: `${field === 'api_smiles' ? 'API SMILES' : 'Coformer SMILES'}: ${message}`,
        })
      })
    })
  })
  return errors
}

function getErrorMessage(data) {
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return getErrorMessage(data[0])
  if (data && typeof data === 'object') {
    return getErrorMessage(data.detail || data.error || Object.values(data)[0])
  }
  return t('batch.screenFailed')
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
        const failed = results.value.filter(row => row.error).length
        ElMessage[failed ? 'warning' : 'success'](
          failed
            ? t('batch.screenPartial', { success: results.value.length - failed, failed })
            : t('batch.screenSuccess'),
        )
      } else if (data.status === 'failed') {
        stopPolling()
        results.value = Array.isArray(data.result) ? data.result : []
        ElMessage.error(getErrorMessage(data.result || data))
      }
    } catch (error) {
      stopPolling()
      ElMessage.error(getErrorMessage(error.response?.data))
    }
  }, 3000)
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  validationErrors.value = []
  const parsed = inputMode.value === 'text'
    ? parsePairs(form.pairsText)
    : csvFile.value
      ? await parsePairsFromFile(csvFile.value)
      : { pairs: [], rowNumbers: [], errors: [] }
  if (parsed.errors.length) {
    validationErrors.value = parsed.errors
    return
  }
  if (!parsed.pairs.length) { ElMessage.warning(t('batch.atLeastOne')); return }

  submitting.value = true
  results.value = []
  try {
    const { data } = await taskApi.batchPredict({
      model_id: form.model_id,
      pairs: parsed.pairs,
    })
    if (data.task_id && data.status === 'pending') {
      ElMessage.info(t('batch.taskSubmitted'))
      startPolling(data.task_id)
    } else {
      results.value = Array.isArray(data.result || data.results) ? (data.result || data.results) : []
      ElMessage.success(t('batch.screenSuccess'))
    }
  } catch (e) {
    const pairErrors = extractPairErrors(e.response?.data, parsed.rowNumbers)
    if (pairErrors.length) {
      validationErrors.value = pairErrors
      ElMessage.error(t('batch.validationFailed'))
    } else {
      ElMessage.error(getErrorMessage(e.response?.data))
    }
  } finally {
    submitting.value = false
  }
}

function exportCSV() {
  const csv = Papa.unparse(results.value.map(row => ({
    api_smiles: row.api_smiles,
    coformer_smiles: row.coformer_smiles,
    prediction: row.error ? '' : row.prediction,
    label: row.error ? '' : CLASS_LABELS[row.prediction],
    confidence: row.probabilities ? `${(Math.max(...row.probabilities) * 100).toFixed(1)}%` : '',
    error: row.error || '',
  })))
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
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

.validation-alert { margin-top: 16px; }
.validation-list {
  margin: 8px 0 0;
  padding-left: 18px;
  line-height: 1.7;
}
.result-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.row-error-message { color: #dc2626; }

:deep(.row-class-0 td) { background: rgba(148,163,184,0.06) !important; }
:deep(.row-class-1 td) { background: rgba(245,158,11,0.06) !important; }
:deep(.row-class-2 td) { background: rgba(34,197,94,0.06) !important; }
:deep(.row-class-3 td) { background: rgba(59,130,246,0.06) !important; }
:deep(.row-error td) { background: rgba(239,68,68,0.06) !important; }
</style>
