<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ $t('history.title') }}</h1>
      <p class="page-desc">{{ $t('history.desc') }}</p>
    </div>

    <div class="content-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane :label="$t('history.predictTab')" name="predict">
          <el-table :data="predictTasks" v-loading="loading" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column :label="$t('history.type')" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.task_type === 'single' ? 'primary' : 'warning'" size="small" round>
                  {{ row.task_type === 'single' ? $t('history.typeSingle') : $t('history.typeBatch') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('history.statusCol')" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small" round>{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('history.createdAt')" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="" width="100" align="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" text @click="showDetail(row)">{{ $t('common.detail') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="$t('history.finetuneTab')" name="finetune">
          <el-table :data="finetuneTasks" v-loading="loading" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" :label="$t('history.taskName')" min-width="160" />
            <el-table-column :label="$t('history.statusCol')" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small" round>{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('history.createdAt')" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="" width="100" align="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" text @click="showFinetuneDetail(row)">{{ $t('common.detail') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="detailVisible"
      :title="$t('history.predictDetail')"
      :width="detailData?.task_type === 'batch' ? '92vw' : 'min(700px, 92vw)'"
      :close-on-click-modal="true"
    >
      <template v-if="detailData">
        <div class="detail-grid">
          <div class="detail-item"><span class="detail-label">{{ $t('history.taskId') }}</span><span>{{ detailData.id }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.type') }}</span><span>{{ detailData.task_type === 'single' ? $t('history.singlePredict') : $t('history.batchPredict') }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.statusCol') }}</span><el-tag :type="statusType(detailData.status)" size="small" round>{{ statusLabel(detailData.status) }}</el-tag></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.time') }}</span><span>{{ formatDate(detailData.created_at) }}</span></div>
        </div>

        <template v-if="detailData.task_type === 'single'">
          <div class="molecule-pair-grid">
            <div class="molecule-field">
              <span class="detail-label">{{ $t('history.apiSmiles') }}</span>
              <code>{{ singlePair.api_smiles || '-' }}</code>
            </div>
            <div class="molecule-field">
              <span class="detail-label">{{ $t('history.coformerSmiles') }}</span>
              <code>{{ singlePair.coformer_smiles || '-' }}</code>
            </div>
          </div>

          <el-alert
            v-if="detailData.result?.error"
            type="error"
            :title="detailData.result.error"
            :closable="false"
            show-icon
          />
          <div v-else-if="detailData.result" class="detail-result">
            <div class="result-badge" :class="'class-' + detailData.result.prediction">
              {{ predictionLabel(detailData.result) }}
            </div>
            <div v-if="detailData.result.probabilities" class="mini-probs">
              <div v-for="(p, i) in detailData.result.probabilities" :key="i" class="mini-prob">
                <span class="mini-dot" :style="{ background: CLASS_COLORS[i] }"></span>
                <span>{{ CLASS_LABELS[i] }}</span>
                <strong>{{ (p * 100).toFixed(1) }}%</strong>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="batch-detail-header">
            <span>{{ $t('history.pairCount', { count: batchRows.length }) }}</span>
            <el-button
              v-if="batchRows.length"
              :icon="Download"
              size="small"
              @click="exportBatchHistory"
            >
              {{ $t('common.export') }}
            </el-button>
          </div>
          <el-alert
            v-if="batchTaskError"
            type="error"
            :title="batchTaskError"
            :closable="false"
            show-icon
          />
          <el-table
            v-if="batchRows.length"
            :data="batchRows"
            stripe
            max-height="480"
            style="width: 100%"
            :header-cell-style="{ background: '#f8fafc' }"
          >
            <el-table-column type="index" label="#" width="56" />
            <el-table-column prop="api_smiles" :label="$t('history.apiSmiles')" min-width="220" show-overflow-tooltip />
            <el-table-column prop="coformer_smiles" :label="$t('history.coformerSmiles')" min-width="220" show-overflow-tooltip />
            <el-table-column :label="$t('history.prediction')" width="130" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.error" type="danger" size="small" round>
                  {{ $t('history.failedRow') }}
                </el-tag>
                <el-tag
                  v-else-if="Number.isInteger(row.prediction)"
                  :color="CLASS_COLORS[row.prediction]"
                  style="color: #fff; border: none"
                  size="small"
                  round
                >
                  {{ predictionLabel(row) }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column :label="$t('history.confidence')" width="120" align="center">
              <template #default="{ row }">
                <strong>{{ confidenceLabel(row) }}</strong>
              </template>
            </el-table-column>
            <el-table-column
              v-if="batchHasErrors"
              prop="error"
              :label="$t('history.error')"
              min-width="220"
              show-overflow-tooltip
            >
              <template #default="{ row }">{{ row.error || '-' }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-else :description="$t('common.noData')" :image-size="72" />
        </template>
      </template>
    </el-dialog>

    <el-dialog v-model="finetuneDetailVisible" :title="$t('history.finetuneDetail')" width="500px">
      <template v-if="finetuneDetailData">
        <div class="detail-grid">
          <div class="detail-item" v-for="(val, key) in finetuneDetailData" :key="key">
            <span class="detail-label">{{ key }}</span>
            <el-tag v-if="key === 'status'" :type="statusType(val)" size="small" round>{{ statusLabel(val) }}</el-tag>
            <span v-else>{{ val }}</span>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import Papa from 'papaparse'
import { taskApi } from '../api'

const { t, locale } = useI18n()

const activeTab = ref('predict')
const loading = ref(false)
const predictTasks = ref([])
const finetuneTasks = ref([])
const detailVisible = ref(false)
const detailData = ref(null)
const finetuneDetailVisible = ref(false)
const finetuneDetailData = ref(null)

const STATUS_MAP = computed(() => ({
  pending: { type: 'info', label: t('status.pending') },
  running: { type: 'warning', label: t('status.running') },
  completed: { type: 'success', label: t('status.completed') },
  failed: { type: 'danger', label: t('status.failed') },
}))
const CLASS_COLORS = ['#94a3b8', '#f59e0b', '#22c55e', '#3b82f6']
const CLASS_LABELS = computed(() => [
  t('history.classNegative'),
  t('history.classSalt'),
  t('history.classCocrystal'),
  t('history.classSolvate'),
])
const singlePair = computed(() => ({
  ...(detailData.value?.input_data || {}),
  ...(detailData.value?.result || {}),
}))
const batchRows = computed(() => {
  if (detailData.value?.task_type !== 'batch') return []
  const pairs = detailData.value.input_data?.pairs || []
  const results = Array.isArray(detailData.value.result) ? detailData.value.result : []
  const rowCount = Math.max(pairs.length, results.length)
  return Array.from({ length: rowCount }, (_, index) => ({
    ...(pairs[index] || {}),
    ...(results[index] || {}),
  }))
})
const batchHasErrors = computed(() => batchRows.value.some(row => row.error))
const batchTaskError = computed(() => {
  const result = detailData.value?.result
  return result && !Array.isArray(result) ? result.error || '' : ''
})
function statusType(s) { return STATUS_MAP.value[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP.value[s]?.label || s }
function formatDate(s) { return s ? new Date(s).toLocaleString(locale.value) : '-' }
function predictionLabel(row) {
  return Number.isInteger(row?.prediction) ? CLASS_LABELS.value[row.prediction] : row?.label || '-'
}
function confidenceLabel(row) {
  return Array.isArray(row?.probabilities)
    ? `${(Math.max(...row.probabilities) * 100).toFixed(1)}%`
    : '-'
}

function exportBatchHistory() {
  const csv = Papa.unparse(batchRows.value.map(row => ({
    api_smiles: row.api_smiles || '',
    coformer_smiles: row.coformer_smiles || '',
    prediction: Number.isInteger(row.prediction) ? row.prediction : '',
    label: Number.isInteger(row.prediction) ? predictionLabel(row) : '',
    confidence: confidenceLabel(row) === '-' ? '' : confidenceLabel(row),
    error: row.error || '',
  })))
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `prediction_task_${detailData.value.id}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

async function loadPredictTasks() { loading.value = true; try { const { data } = await taskApi.list(); predictTasks.value = data.results || data } catch { ElMessage.error(t('history.loadFailed')) } finally { loading.value = false } }
async function loadFinetuneTasks() { loading.value = true; try { const { data } = await taskApi.finetuneList(); finetuneTasks.value = data.results || data } catch { ElMessage.error(t('history.loadFailed')) } finally { loading.value = false } }
function handleTabChange(tab) { tab === 'predict' ? loadPredictTasks() : loadFinetuneTasks() }
async function showDetail(row) { try { const { data } = await taskApi.detail(row.id); detailData.value = data; detailVisible.value = true } catch { ElMessage.error(t('history.detailFailed')) } }
async function showFinetuneDetail(row) { try { const { data } = await taskApi.finetuneDetail(row.id); finetuneDetailData.value = data; finetuneDetailVisible.value = true } catch { ElMessage.error(t('history.detailFailed')) } }

onMounted(loadPredictTasks)
</script>

<style scoped>
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; }
.detail-item .el-tag { align-self: flex-start; }
.detail-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
.molecule-pair-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.molecule-field { min-width: 0; padding: 12px; background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; }
.molecule-field code { display: block; margin-top: 6px; overflow-wrap: anywhere; color: var(--text-primary); font-size: 13px; line-height: 1.5; }
.detail-result { margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 10px; }
.result-badge { display: inline-block; padding: 6px 16px; border-radius: 8px; font-weight: 600; font-size: 14px; margin-bottom: 12px; }
.result-badge.class-0 { background: #f1f5f9; color: #475569; }
.result-badge.class-1 { background: #f0fdf4; color: #15803d; }
.result-badge.class-2 { background: #fffbeb; color: #b45309; }
.result-badge.class-3 { background: #fef2f2; color: #dc2626; }
.mini-probs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 16px; }
.mini-prob { font-size: 13px; color: var(--text-secondary); display: grid; grid-template-columns: 8px 1fr auto; align-items: center; gap: 6px; }
.mini-dot { width: 8px; height: 8px; border-radius: 50%; }
.batch-detail-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 12px; font-size: 13px; color: var(--text-secondary); }
@media (max-width: 640px) {
  .detail-grid,
  .molecule-pair-grid { grid-template-columns: 1fr; }
  .mini-probs { grid-template-columns: 1fr; }
}
</style>
