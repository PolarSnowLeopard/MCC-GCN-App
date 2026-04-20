<template>
  <div>
    <div class="page-header" style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <h1 class="page-title">{{ $t('models.title') }}</h1>
        <p class="page-desc">{{ $t('models.desc') }}</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true" size="large">
        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style="margin-right:6px"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd"/></svg>
        {{ $t('models.upload') }}
      </el-button>
    </div>

    <div v-if="models.length === 0 && !loading" class="content-card empty-state">
      <svg viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5">
        <path d="M24 4L4 14v20l20 10 20-10V14L24 4z"/><line x1="4" y1="14" x2="24" y2="24"/><line x1="44" y1="14" x2="24" y2="24"/><line x1="24" y1="24" x2="24" y2="44"/>
      </svg>
      <p style="margin-top:12px;color:var(--text-muted)">{{ $t('models.noModels') }}</p>
    </div>

    <div v-else class="model-grid" v-loading="loading">
      <div v-for="m in models" :key="m.id" class="model-card content-card" :class="{ 'draft-card': m.status === 'draft' }">
        <div class="model-header">
          <div class="model-icon" :class="m.model_type === 'pretrained' ? 'pre' : 'ft'">
            {{ m.model_type === 'pretrained' ? 'P' : 'F' }}
          </div>
          <div>
            <div class="model-name">{{ m.name }}</div>
            <div class="model-meta">
              {{ m.model_type === 'pretrained' ? $t('models.pretrainedModel') : $t('models.finetunedModel') }}
              · {{ $t('models.classes', { n: m.num_classes }) }}
            </div>
          </div>
        </div>
        <div class="model-desc">{{ m.description || '' }}</div>
        <div class="model-footer">
          <span class="model-date">
            <el-tag v-if="m.is_builtin" size="small" type="info" style="margin-right:6px">{{ $t('common.builtin') }}</el-tag>
            <el-tag v-if="m.status === 'draft'" size="small" type="warning" style="margin-right:6px">Draft</el-tag>
            <el-tag v-else-if="!m.is_builtin" size="small" type="success" style="margin-right:6px">{{ $t('models.published') }}</el-tag>
            {{ formatDate(m.created_at) }}
          </span>
          <div class="model-actions">
            <el-button v-if="m.status === 'draft'" type="primary" size="small" text @click="handlePublish(m.id)">
              {{ $t('models.publish') }}
            </el-button>
            <el-popconfirm v-if="!m.is_builtin" :title="$t('models.confirmDelete')" @confirm="handleDelete(m.id)">
              <template #reference>
                <el-button type="danger" size="small" text>{{ $t('common.delete') }}</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="$t('models.upload')" width="500px" @closed="resetForm">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-position="top" size="large">
        <el-form-item :label="$t('models.modelName')" prop="name">
          <el-input v-model="uploadForm.name" :placeholder="$t('models.modelNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="$t('models.description')">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" :placeholder="$t('models.descPlaceholder')" />
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <el-form-item :label="$t('models.modelType')" prop="model_type">
            <el-select v-model="uploadForm.model_type" style="width:100%">
              <el-option :label="$t('models.pretrainedModel')" value="pretrained" />
              <el-option :label="$t('models.finetunedModel')" value="finetuned" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('models.numClasses')">
            <el-input-number v-model="uploadForm.num_classes" :min="2" :max="10" style="width:100%" />
          </el-form-item>
        </div>
        <el-form-item :label="$t('models.modelFile')" prop="model_file">
          <el-upload :auto-upload="false" :limit="1" :on-change="f => uploadForm.model_file = f.raw" :on-remove="() => uploadForm.model_file = null" drag>
            <div style="padding:16px 0">
              <p style="color:#94a3b8;font-size:13px">{{ $t('models.uploadHint') }}</p>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">{{ $t('models.upload') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { modelApi } from '../api'

const { t, locale } = useI18n()

const loading = ref(false)
const models = ref([])
const dialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref()
const uploadForm = reactive({ name: '', description: '', model_type: '', num_classes: 4, model_file: null })
const uploadRules = computed(() => ({
  name: [{ required: true, message: t('models.nameRequired'), trigger: 'blur' }],
  model_type: [{ required: true, message: t('models.typeRequired'), trigger: 'change' }],
}))

function formatDate(s) { return s ? new Date(s).toLocaleDateString(locale.value) : '-' }

async function loadModels() {
  loading.value = true
  try { const { data } = await modelApi.list(); models.value = data.results || data }
  catch { ElMessage.error(t('models.loadFailed')) }
  finally { loading.value = false }
}

async function handleUpload() {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!uploadForm.model_file) { ElMessage.warning(t('models.selectFile')); return }
  const fd = new FormData()
  Object.entries(uploadForm).forEach(([k, v]) => { if (v !== null) fd.append(k, v) })
  uploading.value = true
  try {
    await modelApi.create(fd)
    ElMessage.success(t('models.uploadSuccess'))
    dialogVisible.value = false
    loadModels()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('models.uploadFailed'))
  } finally {
    uploading.value = false
  }
}

async function handlePublish(id) {
  try {
    await modelApi.publish(id)
    ElMessage.success(t('models.publishSuccess'))
    loadModels()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('common.failed'))
  }
}

async function handleDelete(id) {
  try {
    await modelApi.delete(id)
    ElMessage.success(t('models.deleted'))
    loadModels()
  } catch {
    ElMessage.error(t('models.deleteFailed'))
  }
}

function resetForm() {
  Object.assign(uploadForm, { name: '', description: '', model_type: '', num_classes: 4, model_file: null })
}

onMounted(loadModels)
</script>

<style scoped>
.model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; align-items: stretch; }
/* Override the global `.content-card + .content-card { margin-top: 20px }` rule,
   which would otherwise push all but the first grid item down by 20px and
   break stretch-based row alignment. */
.model-grid .model-card { margin-top: 0; align-self: stretch; }
.model-card { display: flex; flex-direction: column; min-height: 180px; transition: border-color .2s; }
.model-card.draft-card { border: 1px dashed #f59e0b; background: #fffdf5; }
.model-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.model-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; flex-shrink: 0; }
.model-icon.pre { background: #eff6ff; color: #3b82f6; }
.model-icon.ft { background: #f0fdf4; color: #22c55e; }
.model-name { font-weight: 600; font-size: 15px; color: var(--text-primary); }
.model-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.model-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5; flex: 1; }
.model-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 12px; margin-top: auto; }
.model-date { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.model-actions { display: flex; gap: 4px; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; }
</style>
