<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center">
      <h2 style="margin-top: 0">模型管理</h2>
      <el-button type="primary" @click="dialogVisible = true">上传模型</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="models" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="name" label="模型名称" min-width="160" />
        <el-table-column prop="model_type" label="模型类型" width="120" align="center" />
        <el-table-column prop="num_classes" label="分类数" width="80" align="center" />
        <el-table-column label="大模型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_large ? 'success' : 'info'" size="small">
              {{ row.is_large ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_display" label="上传者" width="100" />
        <el-table-column label="上传时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-popconfirm title="确定要删除此模型吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="上传模型" width="520px" @closed="resetUploadForm">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" placeholder="模型描述（选填）" />
        </el-form-item>
        <el-form-item label="模型类型" prop="model_type">
          <el-select v-model="uploadForm.model_type" placeholder="请选择" style="width: 100%">
            <el-option label="GCN" value="gcn" />
            <el-option label="MCC-GCN" value="mcc_gcn" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类数">
          <el-input-number v-model="uploadForm.num_classes" :min="2" :max="10" />
        </el-form-item>
        <el-form-item label="大模型">
          <el-switch v-model="uploadForm.is_large" />
        </el-form-item>
        <el-form-item label="模型文件" prop="model_file">
          <el-upload
            :auto-upload="false"
            :limit="1"
            :on-change="(f) => (uploadForm.model_file = f.raw)"
            :on-remove="() => (uploadForm.model_file = null)"
          >
            <template #trigger>
              <el-button>选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">上传 .pt / .pth 模型文件</div>
            </template>
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

const uploadForm = reactive({
  name: '',
  description: '',
  model_type: '',
  num_classes: 4,
  is_large: false,
  model_file: null,
})

const uploadRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  model_file: [{ required: true, message: '请上传模型文件', trigger: 'change' }],
}

function formatDate(str) {
  if (!str) return '-'
  return new Date(str).toLocaleString('zh-CN')
}

async function loadModels() {
  loading.value = true
  try {
    const { data } = await modelApi.list()
    models.value = data.results || data
  } catch {
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

async function handleUpload() {
  const valid = await uploadFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!uploadForm.model_file) {
    ElMessage.warning('请选择模型文件')
    return
  }

  const fd = new FormData()
  fd.append('name', uploadForm.name)
  fd.append('description', uploadForm.description)
  fd.append('model_type', uploadForm.model_type)
  fd.append('num_classes', uploadForm.num_classes)
  fd.append('is_large', uploadForm.is_large)
  fd.append('model_file', uploadForm.model_file)

  uploading.value = true
  try {
    await modelApi.create(fd)
    ElMessage.success('模型上传成功')
    dialogVisible.value = false
    loadModels()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleDelete(id) {
  try {
    await modelApi.delete(id)
    ElMessage.success('删除成功')
    loadModels()
  } catch {
    ElMessage.error('删除失败')
  }
}

function resetUploadForm() {
  uploadForm.name = ''
  uploadForm.description = ''
  uploadForm.model_type = ''
  uploadForm.num_classes = 4
  uploadForm.is_large = false
  uploadForm.model_file = null
}

onMounted(loadModels)
</script>
