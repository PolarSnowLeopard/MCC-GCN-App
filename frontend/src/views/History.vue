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
                <el-tag :type="row.task_type === 'single' ? '' : 'warning'" size="small" round>
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

    <el-dialog v-model="detailVisible" :title="$t('history.predictDetail')" width="600px" :close-on-click-modal="true">
      <template v-if="detailData">
        <div class="detail-grid">
          <div class="detail-item"><span class="detail-label">{{ $t('history.taskId') }}</span><span>{{ detailData.id }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.type') }}</span><span>{{ detailData.task_type === 'single' ? $t('history.singlePredict') : $t('history.batchPredict') }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.statusCol') }}</span><el-tag :type="statusType(detailData.status)" size="small" round>{{ statusLabel(detailData.status) }}</el-tag></div>
          <div class="detail-item"><span class="detail-label">{{ $t('history.time') }}</span><span>{{ formatDate(detailData.created_at) }}</span></div>
        </div>
        <template v-if="detailData.result && detailData.task_type === 'single'">
          <div class="detail-result">
            <div class="result-badge" :class="'class-' + detailData.result.prediction">
              Class {{ detailData.result.prediction }} — {{ detailData.result.label }}
            </div>
            <div v-if="detailData.result.probabilities" class="mini-probs">
              <div v-for="(p, i) in detailData.result.probabilities" :key="i" class="mini-prob">
                <span class="mini-dot" :style="{background: CLASS_COLORS[i]}"></span>
                {{ (p * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </template>
        <template v-else-if="detailData.result">
          <pre class="result-json">{{ JSON.stringify(detailData.result, null, 2) }}</pre>
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
function statusType(s) { return STATUS_MAP.value[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP.value[s]?.label || s }
function formatDate(s) { return s ? new Date(s).toLocaleString(locale.value) : '-' }

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
.detail-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
.detail-result { margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 10px; }
.result-badge { display: inline-block; padding: 6px 16px; border-radius: 8px; font-weight: 600; font-size: 14px; margin-bottom: 12px; }
.result-badge.class-0 { background: #f1f5f9; color: #475569; }
.result-badge.class-1 { background: #f0fdf4; color: #15803d; }
.result-badge.class-2 { background: #fffbeb; color: #b45309; }
.result-badge.class-3 { background: #fef2f2; color: #dc2626; }
.mini-probs { display: flex; gap: 16px; }
.mini-prob { font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; }
.mini-dot { width: 8px; height: 8px; border-radius: 50%; }
.result-json { background: #f8fafc; padding: 16px; border-radius: 8px; font-size: 12px; overflow: auto; max-height: 300px; color: var(--text-secondary); }
</style>
