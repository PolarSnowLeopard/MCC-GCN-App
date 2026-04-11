<template>
  <div>
    <h2 style="margin-top: 0">历史记录</h2>
    <el-card shadow="never">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="预测任务" name="predict">
          <el-table :data="predictTasks" v-loading="loading" stripe border style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.task_type === 'single' ? '' : 'warning'" size="small">
                  {{ row.task_type === 'single' ? '单次' : '批量' }}
                </el-tag>
              </template>
            </el-table-column>
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
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" text @click="showDetail(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="微调任务" name="finetune">
          <el-table :data="finetuneTasks" v-loading="loading" stripe border style="width: 100%">
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
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" text @click="showFinetuneDetail(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Predict detail dialog -->
    <el-dialog v-model="detailVisible" title="任务详情" width="640px">
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务 ID">{{ detailData.id }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ detailData.task_type === 'single' ? '单次预测' : '批量预测' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailData.status)">{{ statusLabel(detailData.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(detailData.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <template v-if="detailData.input_data">
          <h4 style="margin: 16px 0 8px">输入数据</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item
              v-for="(val, key) in detailData.input_data"
              :key="key"
              :label="key"
            >
              <span v-if="typeof val === 'string'">{{ val }}</span>
              <pre v-else style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(val, null, 2) }}</pre>
            </el-descriptions-item>
          </el-descriptions>
        </template>

        <template v-if="detailData.result">
          <h4 style="margin: 16px 0 8px">预测结果</h4>
          <template v-if="detailData.task_type === 'single' && detailData.result.prediction !== undefined">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="预测类别">
                <el-tag :type="classTagType(detailData.result.prediction)" effect="dark">
                  Class {{ detailData.result.prediction }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="标签">{{ detailData.result.label }}</el-descriptions-item>
            </el-descriptions>
            <div v-if="detailData.result.probabilities" style="margin-top: 12px">
              <div v-for="(prob, idx) in detailData.result.probabilities" :key="idx" style="margin-bottom: 6px; display: flex; align-items: center; gap: 8px">
                <span style="width: 70px; font-size: 13px">Class {{ idx }}</span>
                <el-progress :percentage="+(prob * 100).toFixed(1)" :color="classColor(idx)" :stroke-width="16" :text-inside="true" style="flex: 1" />
              </div>
            </div>
          </template>
          <pre v-else style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 12px; overflow: auto; max-height: 300px">{{ JSON.stringify(detailData.result, null, 2) }}</pre>
        </template>
      </template>
    </el-dialog>

    <!-- Finetune detail dialog -->
    <el-dialog v-model="finetuneDetailVisible" title="微调任务详情" width="560px">
      <template v-if="finetuneDetailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(val, key) in finetuneDetailData"
            :key="key"
            :label="key"
          >
            <el-tag v-if="key === 'status'" :type="statusType(val)">{{ statusLabel(val) }}</el-tag>
            <span v-else>{{ val }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { taskApi } from '../api'

const activeTab = ref('predict')
const loading = ref(false)
const predictTasks = ref([])
const finetuneTasks = ref([])
const detailVisible = ref(false)
const detailData = ref(null)
const finetuneDetailVisible = ref(false)
const finetuneDetailData = ref(null)

const STATUS_MAP = {
  pending: { type: 'info', label: '等待中' },
  processing: { type: 'warning', label: '处理中' },
  completed: { type: 'success', label: '已完成' },
  success: { type: 'success', label: '已完成' },
  failed: { type: 'danger', label: '失败' },
}
const CLASS_COLORS = ['#909399', '#67c23a', '#e6a23c', '#f56c6c']
const TAG_TYPES = ['info', 'success', 'warning', 'danger']

function statusType(s) { return STATUS_MAP[s]?.type || 'info' }
function statusLabel(s) { return STATUS_MAP[s]?.label || s }
function classColor(idx) { return CLASS_COLORS[idx] || '#909399' }
function classTagType(idx) { return TAG_TYPES[idx] || 'info' }
function formatDate(str) { return str ? new Date(str).toLocaleString('zh-CN') : '-' }

async function loadPredictTasks() {
  loading.value = true
  try {
    const { data } = await taskApi.list({ type: activeTab.value === 'predict' ? undefined : undefined })
    predictTasks.value = data.results || data
  } catch {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

async function loadFinetuneTasks() {
  loading.value = true
  try {
    const { data } = await taskApi.finetuneList()
    finetuneTasks.value = data.results || data
  } catch {
    ElMessage.error('加载微调任务列表失败')
  } finally {
    loading.value = false
  }
}

function handleTabChange(tab) {
  if (tab === 'predict') loadPredictTasks()
  else loadFinetuneTasks()
}

async function showDetail(row) {
  try {
    const { data } = await taskApi.detail(row.id)
    detailData.value = data
    detailVisible.value = true
  } catch {
    ElMessage.error('获取任务详情失败')
  }
}

async function showFinetuneDetail(row) {
  try {
    const { data } = await taskApi.finetuneDetail(row.id)
    finetuneDetailData.value = data
    finetuneDetailVisible.value = true
  } catch {
    ElMessage.error('获取微调详情失败')
  }
}

onMounted(() => {
  loadPredictTasks()
})
</script>
