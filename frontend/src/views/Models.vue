<template>
  <div>
    <div class="page-header" style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <h1 class="page-title">模型管理</h1>
        <p class="page-desc">管理预训练和微调模型文件</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true" size="large">
        <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" style="margin-right:6px"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd"/></svg>
        上传模型
      </el-button>
    </div>

    <div v-if="models.length === 0 && !loading" class="content-card empty-state">
      <svg viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5">
        <path d="M24 4L4 14v20l20 10 20-10V14L24 4z"/><line x1="4" y1="14" x2="24" y2="24"/><line x1="44" y1="14" x2="24" y2="24"/><line x1="24" y1="24" x2="24" y2="44"/>
      </svg>
      <p style="margin-top:12px;color:var(--text-muted)">还没有模型，点击右上角上传</p>
    </div>

    <div v-else class="model-grid" v-loading="loading">
      <div v-for="m in models" :key="m.id" class="model-card content-card">
        <div class="model-header">
          <div class="model-icon" :class="m.model_type === 'pretrained' ? 'pre' : 'ft'">
            {{ m.model_type === 'pretrained' ? 'P' : 'F' }}
          </div>
          <div>
            <div class="model-name">{{ m.name }}</div>
            <div class="model-meta">{{ m.model_type === 'pretrained' ? '预训练模型' : '微调模型' }} · {{ m.num_classes }} 类</div>
          </div>
        </div>
        <div class="model-desc">{{ m.description || '' }}</div>
        <div class="model-footer">
          <span class="model-date">
            <el-tag v-if="m.is_builtin" size="small" type="info" style="margin-right:6px">内置</el-tag>
            {{ formatDate(m.created_at) }}
          </span>
          <el-popconfirm v-if="!m.is_builtin" title="确定删除此模型？" @confirm="handleDelete(m.id)">
            <template #reference>
              <el-button type="danger" size="small" text>删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="上传模型" width="500px" @closed="resetForm">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-position="top" size="large">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="例如：MCC-GCN-v2-FT" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="模型描述（选填）" />
        </el-form-item>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <el-form-item label="模型类型" prop="model_type">
            <el-select v-model="uploadForm.model_type" style="width:100%">
              <el-option label="预训练模型" value="pretrained" />
              <el-option label="微调模型" value="finetuned" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类数">
            <el-input-number v-model="uploadForm.num_classes" :min="2" :max="10" style="width:100%" />
          </el-form-item>
        </div>
        <el-form-item label="模型文件" prop="model_file">
          <el-upload :auto-upload="false" :limit="1" :on-change="f => uploadForm.model_file = f.raw" :on-remove="() => uploadForm.model_file = null" drag>
            <div style="padding:16px 0">
              <p style="color:#94a3b8;font-size:13px">上传 .pt / .pth 权重文件</p>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi } from '../api'

const loading = ref(false)
const models = ref([])
const dialogVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref()
const uploadForm = reactive({ name: '', description: '', model_type: '', num_classes: 4, model_file: null })
const uploadRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  model_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

function formatDate(s) { return s ? new Date(s).toLocaleDateString('zh-CN') : '-' }

async function loadModels() { loading.value = true; try { const { data } = await modelApi.list(); models.value = data.results || data } catch { ElMessage.error('加载失败') } finally { loading.value = false } }

async function handleUpload() {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!uploadForm.model_file) { ElMessage.warning('请选择模型文件'); return }
  const fd = new FormData()
  Object.entries(uploadForm).forEach(([k, v]) => { if (v !== null) fd.append(k, v) })
  uploading.value = true
  try { await modelApi.create(fd); ElMessage.success('上传成功'); dialogVisible.value = false; loadModels() }
  catch (e) { ElMessage.error(e.response?.data?.detail || '上传失败') }
  finally { uploading.value = false }
}

async function handleDelete(id) { try { await modelApi.delete(id); ElMessage.success('已删除'); loadModels() } catch { ElMessage.error('删除失败') } }
function resetForm() { Object.assign(uploadForm, { name: '', description: '', model_type: '', num_classes: 4, model_file: null }) }

onMounted(loadModels)
</script>

<style scoped>
.model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; align-items: stretch; }
.model-card { display: flex; flex-direction: column; min-height: 180px; }
.model-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.model-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; flex-shrink: 0; }
.model-icon.pre { background: #eff6ff; color: #3b82f6; }
.model-icon.ft { background: #f0fdf4; color: #22c55e; }
.model-name { font-weight: 600; font-size: 15px; color: var(--text-primary); }
.model-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.model-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5; flex: 1; }
.model-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 12px; margin-top: auto; }
.model-date { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; }
</style>
