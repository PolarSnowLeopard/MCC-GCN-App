<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ $t('finetune.title') }}</h1>
      <p class="page-desc">{{ $t('finetune.desc') }}</p>
    </div>

    <div class="ft-grid">
      <!-- Left: Configuration -->
      <div class="content-card">
        <div class="card-title">{{ $t('finetune.config') }}</div>

        <div class="input-hint">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style="flex-shrink:0;margin-top:1px"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
          <div>
            <div>{{ $t('finetune.formatHint') }}</div>
            <code class="hint-example">api_smiles,coformer_smiles,label<br/>CCO,O=C(O)c1ccccc1O,2<br/>c1ccccc1,CC(=O)O,0</code>
            <div style="margin-top:4px;font-size:12px;opacity:.8">{{ $t('finetune.labelHint') }}</div>
          </div>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
          <el-form-item :label="$t('finetune.baseModel')" prop="base_model_id">
            <el-select v-model="form.base_model_id" :placeholder="$t('finetune.baseModelPlaceholder')" style="width: 100%">
              <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id">
                <span>{{ m.name }}</span>
                <el-tag size="small" :type="m.model_type === 'pretrained' ? 'primary' : 'success'" style="margin-left:8px" round>
                  {{ m.model_type === 'pretrained' ? 'P' : 'FT' }}
                </el-tag>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('finetune.taskName')" prop="name">
            <el-input v-model="form.name" :placeholder="$t('finetune.taskNamePlaceholder')" />
          </el-form-item>

          <el-form-item :label="$t('finetune.trainingData')" prop="training_file">
            <div style="display:flex;gap:8px;width:100%;align-items:flex-start">
              <el-upload
                :auto-upload="false" :limit="1" accept=".csv"
                :on-change="f => form.training_file = f.raw"
                :on-remove="() => form.training_file = null"
                drag style="flex:1"
              >
                <div style="padding:16px 0">
                  <svg viewBox="0 0 20 20" fill="#94a3b8" width="28" height="28"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
                  <p style="color:#94a3b8;margin-top:6px;font-size:13px">{{ $t('finetune.uploadTrainingData') }}</p>
                </div>
              </el-upload>
              <el-button class="template-btn" @click="downloadTemplate">
                <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="margin-right:4px"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                {{ $t('finetune.downloadTemplate') }}
              </el-button>
            </div>
          </el-form-item>

          <details class="params-toggle">
            <summary>{{ $t('finetune.advancedParams') }}</summary>
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

          <el-button type="primary" :loading="submitting" @click="handleSubmit" style="width:100%;height:44px;margin-top:12px">
            {{ $t('finetune.submitTask') }}
          </el-button>
        </el-form>
      </div>

      <!-- Right: Task list -->
      <div class="content-card">
        <div style="display:flex;justify-content:space-between;align-items:center" class="card-title">
          <span>{{ $t('finetune.taskList') }}</span>
          <el-button size="small" text @click="loadTasks">{{ $t('common.refresh') }}</el-button>
        </div>
        <div v-if="tasks.length === 0 && !tasksLoading" class="empty-state">
          <p>{{ $t('finetune.noTasks') }}</p>
        </div>
        <div v-loading="tasksLoading">
          <div v-for="task in tasks" :key="task.id" class="task-item" :class="{ active: expandedTask === task.id }" @click="toggleTask(task)">
            <div class="task-main">
              <div class="task-info">
                <div class="task-name">{{ task.name }}</div>
                <div class="task-time">{{ formatDate(task.created_at) }}</div>
              </div>
              <el-tag :type="statusType(task.status)" size="small" round>{{ statusLabel(task.status) }}</el-tag>
            </div>

            <!-- Expanded detail -->
            <div v-if="expandedTask === task.id" class="task-detail" @click.stop>
              <!-- Polling indicator for running tasks -->
              <div v-if="task.status === 'running' || task.status === 'pending'" class="poll-status">
                <el-progress :percentage="task.status === 'running' ? 50 : 10" :indeterminate="true" :stroke-width="6" />
                <span>{{ task.status === 'running' ? $t('finetune.taskRunning') : $t('finetune.taskQueued') }}</span>
              </div>

              <!-- Training log -->
              <div v-if="taskDetail?.log" class="log-section">
                <div class="log-title">{{ $t('finetune.trainingLog') }}</div>
                <pre class="log-content">{{ taskDetail.log }}</pre>
              </div>

              <!-- Actions for completed tasks -->
              <div v-if="task.status === 'completed' && taskDetail?.result_model" class="task-actions">
                <div class="result-model-info">
                  <span class="result-label">{{ $t('finetune.resultModel') }}:</span>
                  <span class="result-name">{{ taskDetail.result_model_name || task.name }}</span>
                  <el-tag v-if="resultModelStatus === 'draft'" size="small" type="warning" round>Draft</el-tag>
                  <el-tag v-else size="small" type="success" round>Published</el-tag>
                </div>
                <div class="action-btns">
                  <el-button size="small" @click.stop="testModel(taskDetail.result_model)">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="margin-right:4px"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/></svg>
                    {{ $t('finetune.testModel') }}
                  </el-button>
                  <el-button v-if="resultModelStatus === 'draft'" type="primary" size="small" @click.stop="publishModel(taskDetail.result_model)">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="margin-right:4px"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                    {{ $t('finetune.publishModel') }}
                  </el-button>
                </div>
              </div>

              <!-- Error message for failed tasks -->
              <div v-if="task.status === 'failed' && taskDetail?.log" class="error-section">
                <pre class="error-content">{{ taskDetail.log }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Test model dialog -->
    <el-dialog v-model="testDialogVisible" :title="$t('finetune.testModelTitle')" width="600px" destroy-on-close>
      <el-form label-position="top" size="large">
        <el-form-item :label="$t('predict.apiLabel')">
          <el-input v-model="testForm.api_smiles" placeholder="SMILES" />
        </el-form-item>
        <el-form-item :label="$t('predict.coformerLabel')">
          <el-input v-model="testForm.coformer_smiles" placeholder="SMILES" />
        </el-form-item>
      </el-form>
      <div v-if="testResult" class="test-result">
        <div class="test-result-label" :style="{ color: CLASS_COLORS[testResult.prediction] }">
          {{ testResult.label }}
        </div>
        <div class="test-result-probs">
          <div v-for="(p, i) in testResult.probabilities" :key="i" class="prob-bar-row">
            <span class="prob-label">{{ CLASS_LABELS[i] }}</span>
            <el-progress :percentage="Math.round(p * 100)" :color="CLASS_COLORS[i]" :stroke-width="14" :show-text="true" style="flex:1" />
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="testPredicting" @click="runTestPredict">
          {{ $t('predict.startPredict') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'

const { t, locale } = useI18n()

const formRef = ref()
const models = ref([])
const submitting = ref(false)
const tasks = ref([])
const tasksLoading = ref(false)
const expandedTask = ref(null)
const taskDetail = ref(null)
const resultModelStatus = ref(null)
let pollTimer = null

const form = reactive({
  base_model_id: '', name: '', training_file: null,
  epochs: 50, batch_size: 16, learning_rate: 0.0003,
})

const rules = computed(() => ({
  base_model_id: [{ required: true, message: t('finetune.baseModelRequired'), trigger: 'change' }],
  name: [{ required: true, message: t('finetune.taskNameRequired'), trigger: 'blur' }],
}))

const STATUS_MAP = computed(() => ({
  pending: { type: 'info', label: t('status.pending') },
  running: { type: 'warning', label: t('status.running') },
  completed: { type: 'success', label: t('status.completed') },
  failed: { type: 'danger', label: t('status.failed') },
}))

const CLASS_COLORS = ['#94a3b8', '#f59e0b', '#22c55e', '#3b82f6']
const CLASS_LABELS = ['Negative', 'Salt', 'Cocrystal', 'Solvate']

function statusType(s) { return STATUS_MAP.value[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP.value[s]?.label || s }
function formatDate(s) { return s ? new Date(s).toLocaleString(locale.value) : '-' }

async function loadTasks() {
  tasksLoading.value = true
  try {
    const { data } = await taskApi.finetuneList()
    tasks.value = data.results || data
  } catch { /* empty */ }
  finally { tasksLoading.value = false }
}

async function toggleTask(task) {
  if (expandedTask.value === task.id) {
    expandedTask.value = null
    taskDetail.value = null
    stopPolling()
    return
  }
  expandedTask.value = task.id
  await fetchTaskDetail(task.id)

  if (task.status === 'pending' || task.status === 'running') {
    startPolling(task.id)
  }
}

async function fetchTaskDetail(id) {
  try {
    const { data } = await taskApi.finetuneDetail(id)
    taskDetail.value = data

    if (data.result_model) {
      try {
        const models = await modelApi.list()
        const allModels = models.data.results || models.data
        const m = allModels.find(m => m.id === data.result_model)
        resultModelStatus.value = m?.status || 'draft'
        taskDetail.value.result_model_name = m?.name
      } catch {
        resultModelStatus.value = 'draft'
      }
    }

    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx >= 0) {
      tasks.value[idx].status = data.status
    }
  } catch { /* empty */ }
}

function startPolling(taskId) {
  stopPolling()
  pollTimer = setInterval(async () => {
    await fetchTaskDetail(taskId)
    if (taskDetail.value && (taskDetail.value.status === 'completed' || taskDetail.value.status === 'failed')) {
      stopPolling()
      loadTasks()
    }
  }, 4000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function downloadTemplate() {
  const csv = 'api_smiles,coformer_smiles,label\nCCO,O=C(O)c1ccccc1O,2\nc1ccccc1,CC(=O)O,0\n'
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'finetune_template.csv'
  a.click()
  URL.revokeObjectURL(url)
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  if (!form.training_file) { ElMessage.warning(t('finetune.uploadRequired')); return }

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
    ElMessage.success(t('finetune.taskSubmitted'))
    form.name = ''
    form.training_file = null
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('finetune.submitFailed'))
  } finally {
    submitting.value = false
  }
}

// --- Test model ---
const testDialogVisible = ref(false)
const testPredicting = ref(false)
const testResult = ref(null)
const testModelId = ref(null)
const testForm = reactive({ api_smiles: '', coformer_smiles: '' })

function testModel(modelId) {
  testModelId.value = modelId
  testResult.value = null
  testForm.api_smiles = ''
  testForm.coformer_smiles = ''
  testDialogVisible.value = true
}

async function runTestPredict() {
  if (!testForm.api_smiles || !testForm.coformer_smiles) {
    ElMessage.warning(t('predict.smilesRequired'))
    return
  }
  testPredicting.value = true
  try {
    const { data } = await taskApi.predict({
      model_id: testModelId.value,
      api_smiles: testForm.api_smiles,
      coformer_smiles: testForm.coformer_smiles,
    })
    testResult.value = data.result
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('predict.predictFailed'))
  } finally {
    testPredicting.value = false
  }
}

// --- Publish model ---
async function publishModel(modelId) {
  try {
    await modelApi.publish(modelId)
    resultModelStatus.value = 'published'
    ElMessage.success(t('finetune.publishSuccess'))
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('finetune.publishFailed'))
  }
}

onMounted(() => {
  modelApi.list().then(r => models.value = r.data.results || r.data).catch(() => {})
  loadTasks()
})

onBeforeUnmount(stopPolling)
</script>

<style scoped>
.ft-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.input-hint {
  display: flex; gap: 10px; padding: 14px 16px; border-radius: 8px;
  background: #eff6ff; color: #1e40af; font-size: 13px; line-height: 1.6; margin-bottom: 20px;
}
.hint-example {
  display: block; margin-top: 6px; padding: 6px 10px; border-radius: 4px;
  background: rgba(59, 130, 246, .08); font-size: 12px; line-height: 1.5;
}

.template-btn {
  flex-shrink: 0; height: auto; white-space: nowrap;
  display: flex; align-items: center; padding: 8px 14px;
  border: 1px dashed var(--border); border-radius: 8px; background: var(--bg-card);
  color: var(--text-secondary); cursor: pointer; font-size: 13px; transition: all .15s;
}
.template-btn:hover { border-color: var(--accent); color: var(--accent); }

.params-toggle { margin-top: 8px; border: 1px solid var(--border); border-radius: 8px; padding: 0 16px; }
.params-toggle summary { padding: 12px 0; cursor: pointer; color: var(--text-secondary); font-size: 14px; font-weight: 500; }
.params-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; padding-bottom: 12px; }

.task-item {
  padding: 14px 0; border-bottom: 1px solid var(--border); cursor: pointer;
  transition: background .15s;
}
.task-item:last-child { border-bottom: none; }
.task-item:hover { background: rgba(59, 130, 246, .02); }
.task-item.active { background: rgba(59, 130, 246, .04); }
.task-main { display: flex; justify-content: space-between; align-items: center; }
.task-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.task-time { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.empty-state { text-align: center; padding: 40px 0; color: var(--text-muted); font-size: 14px; }

.task-detail { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--border); }

.poll-status {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  background: #fffbeb; border-radius: 8px; font-size: 13px; color: #92400e;
}
.poll-status .el-progress { flex: 0 0 100px; }

.log-section { margin-top: 10px; }
.log-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.log-content {
  font-size: 11px; line-height: 1.6; padding: 12px; border-radius: 8px;
  background: #1e293b; color: #e2e8f0; max-height: 240px; overflow: auto;
  white-space: pre-wrap; word-break: break-all;
}

.error-section { margin-top: 10px; }
.error-content {
  font-size: 11px; line-height: 1.6; padding: 12px; border-radius: 8px;
  background: #fef2f2; color: #991b1b; max-height: 160px; overflow: auto;
  white-space: pre-wrap; word-break: break-all;
}

.task-actions { margin-top: 10px; }
.result-model-info {
  display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
  font-size: 13px; color: var(--text-secondary);
}
.result-label { font-weight: 600; }
.result-name { color: var(--text-primary); font-weight: 500; }
.action-btns { display: flex; gap: 8px; }

/* Test dialog */
.test-result { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.test-result-label { font-size: 20px; font-weight: 700; text-align: center; margin-bottom: 16px; }
.test-result-probs { display: flex; flex-direction: column; gap: 8px; }
.prob-bar-row { display: flex; align-items: center; gap: 10px; }
.prob-label { font-size: 12px; color: var(--text-secondary); width: 100px; text-align: right; }
</style>
