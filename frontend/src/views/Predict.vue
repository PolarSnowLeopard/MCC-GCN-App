<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">单次预测</h1>
      <p class="page-desc">输入两个分子信息，预测多组分晶体形成结果</p>
    </div>

    <div class="predict-grid">
      <div class="content-card">
        <div class="card-title">分子输入</div>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
          <el-form-item label="选择模型" prop="model_id">
            <el-select v-model="form.model_id" placeholder="请选择预测模型" style="width: 100%" :loading="modelsLoading">
              <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <span>{{ m.name }}</span>
                  <el-tag size="small" :type="m.model_type === 'pretrained' ? '' : 'success'" round>
                    {{ m.model_type === 'pretrained' ? '预训练' : '微调' }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <!-- API molecule -->
          <div class="mol-section">
            <div class="mol-section-header">
              <span class="mol-section-label">药物分子 (API)</span>
              <el-segmented v-model="apiInputMode" :options="inputModes" size="small" />
            </div>
            <el-form-item v-if="apiInputMode === 'smiles'" prop="api_smiles">
              <el-input v-model="form.api_smiles" placeholder="输入 SMILES，例如 Cn1c(=O)c2c(ncn2C)n(C)c1=O">
                <template #prefix><span class="input-label">SMILES</span></template>
              </el-input>
            </el-form-item>
            <el-form-item v-else prop="api_smiles">
              <div class="name-search-row">
                <el-input v-model="apiNameQuery" placeholder="输入分子名称或 CAS 号，例如 Caffeine 或 58-08-2" @keyup.enter="lookupSmiles('api')" clearable>
                  <template #prefix><span class="input-label">名称</span></template>
                </el-input>
                <el-button type="primary" :loading="apiLookupLoading" @click="lookupSmiles('api')">查询</el-button>
              </div>
              <div v-if="form.api_smiles" class="resolved-smiles">
                <span class="resolved-label">SMILES</span>
                <code>{{ form.api_smiles }}</code>
              </div>
            </el-form-item>
            <div class="quick-picks">
              <span class="quick-label">常用：</span>
              <el-tag v-for="mol in COMMON_APIS" :key="mol.name" size="small" class="quick-tag" effect="plain" round @click="fillMol('api', mol)">
                {{ mol.name }}
              </el-tag>
            </div>
          </div>

          <!-- Coformer molecule -->
          <div class="mol-section">
            <div class="mol-section-header">
              <span class="mol-section-label">辅料分子 (Coformer)</span>
              <el-segmented v-model="cfInputMode" :options="inputModes" size="small" />
            </div>
            <el-form-item v-if="cfInputMode === 'smiles'" prop="coformer_smiles">
              <el-input v-model="form.coformer_smiles" placeholder="输入 SMILES，例如 OC(=O)CC(=O)O">
                <template #prefix><span class="input-label">SMILES</span></template>
              </el-input>
            </el-form-item>
            <el-form-item v-else prop="coformer_smiles">
              <div class="name-search-row">
                <el-input v-model="cfNameQuery" placeholder="输入分子名称或 CAS 号，例如 Glutaric acid 或 110-94-1" @keyup.enter="lookupSmiles('cf')" clearable>
                  <template #prefix><span class="input-label">名称</span></template>
                </el-input>
                <el-button type="primary" :loading="cfLookupLoading" @click="lookupSmiles('cf')">查询</el-button>
              </div>
              <div v-if="form.coformer_smiles" class="resolved-smiles">
                <span class="resolved-label">SMILES</span>
                <code>{{ form.coformer_smiles }}</code>
              </div>
            </el-form-item>
            <div class="quick-picks">
              <span class="quick-label">常用：</span>
              <el-tag v-for="mol in COMMON_COFORMERS" :key="mol.name" size="small" class="quick-tag" effect="plain" round @click="fillMol('cf', mol)">
                {{ mol.name }}
              </el-tag>
            </div>
          </div>

          <el-button type="primary" :loading="predicting" @click="handlePredict" style="width:100%;height:44px;font-size:15px;margin-top:8px">
            {{ predicting ? '预测中...' : '开始预测' }}
          </el-button>
        </el-form>
      </div>

      <div class="content-card result-card" v-if="result">
        <div class="card-title">预测结果</div>
        <div class="result-hero">
          <div class="result-class" :class="'class-' + result.prediction">
            <div class="result-class-num">Class {{ result.prediction }}</div>
            <div class="result-class-label">{{ result.label }}</div>
          </div>
          <div class="result-confidence">
            {{ (Math.max(...result.probabilities) * 100).toFixed(1) }}%
            <span>置信度</span>
          </div>
        </div>

        <div class="prob-bars">
          <div v-for="(prob, idx) in result.probabilities" :key="idx" class="prob-row">
            <div class="prob-label">
              <span class="prob-dot" :style="{ background: CLASS_COLORS[idx] }"></span>
              {{ CLASS_LABELS[idx] }}
            </div>
            <div class="prob-bar-bg">
              <div class="prob-bar-fill" :style="{ width: (prob * 100) + '%', background: CLASS_COLORS[idx] }"></div>
            </div>
            <div class="prob-value">{{ (prob * 100).toFixed(1) }}%</div>
          </div>
        </div>

        <div class="result-meta">
          <div class="meta-item">
            <span class="meta-key">API</span>
            <code>{{ result.api_smiles }}</code>
          </div>
          <div class="meta-item">
            <span class="meta-key">Coformer</span>
            <code>{{ result.coformer_smiles }}</code>
          </div>
        </div>
      </div>

      <div class="content-card result-placeholder" v-else>
        <div class="placeholder-icon">
          <svg viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5">
            <circle cx="24" cy="24" r="20" stroke-dasharray="4 3"/>
            <circle cx="18" cy="20" r="4"/><circle cx="30" cy="20" r="4"/><line x1="22" y1="20" x2="26" y2="20"/>
            <circle cx="24" cy="32" r="4"/><line x1="20" y1="23" x2="22" y2="29"/><line x1="28" y1="23" x2="26" y2="29"/>
          </svg>
        </div>
        <p>输入分子信息后，预测结果将在此显示</p>
        <div class="sample-hint">
          <el-button text type="primary" @click="fillSample">加载示例数据</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'
import axios from 'axios'

const formRef = ref()
const models = ref([])
const modelsLoading = ref(false)
const predicting = ref(false)
const result = ref(null)

const apiInputMode = ref('smiles')
const cfInputMode = ref('smiles')
const inputModes = [
  { label: 'SMILES', value: 'smiles' },
  { label: '名称 / CAS', value: 'name' },
]
const apiNameQuery = ref('')
const cfNameQuery = ref('')
const apiLookupLoading = ref(false)
const cfLookupLoading = ref(false)

const form = reactive({ model_id: '', api_smiles: '', coformer_smiles: '' })
const rules = {
  model_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
  api_smiles: [{ required: true, message: '请输入或查询药物 SMILES', trigger: 'blur' }],
  coformer_smiles: [{ required: true, message: '请输入或查询辅料 SMILES', trigger: 'blur' }],
}

const CLASS_COLORS = ['#94a3b8', '#22c55e', '#f59e0b', '#ef4444']
const CLASS_LABELS = ['无共晶', '共晶 I 型', '共晶 II 型', '共晶 III 型']

const COMMON_APIS = [
  { name: 'Caffeine', smiles: 'Cn1c(=O)c2c(ncn2C)n(C)c1=O' },
  { name: 'Carbamazepine', smiles: 'c1ccc2c(c1)C(=Nc3ccccc3N2)C(=O)N' },  
  { name: 'Ibuprofen', smiles: 'CC(C)Cc1ccc(cc1)C(C)C(=O)O' },
  { name: 'Piroxicam', smiles: 'CN1C(=C(c2ccccc2S1(=O)=O)O)C(=O)Nc3ccccn3' },
]

const COMMON_COFORMERS = [
  { name: 'Glutaric acid', smiles: 'OC(=O)CCCC(=O)O' },
  { name: 'Salicylic acid', smiles: 'OC(=O)c1ccccc1O' },
  { name: 'Nicotinamide', smiles: 'NC(=O)c1cccnc1' },
  { name: 'Saccharin', smiles: 'O=C1NS(=O)(=O)c2ccccc21' },
  { name: 'Benzoic acid', smiles: 'OC(=O)c1ccccc1' },
  { name: 'Oxalic acid', smiles: 'OC(=O)C(=O)O' },
]

async function lookupSmiles(target) {
  const query = target === 'api' ? apiNameQuery.value.trim() : cfNameQuery.value.trim()
  if (!query) { ElMessage.warning('请输入分子名称或 CAS 号'); return }
  const loadingRef = target === 'api' ? apiLookupLoading : cfLookupLoading
  loadingRef.value = true
  try {
    const { data } = await axios.get(
      `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${encodeURIComponent(query)}/property/CanonicalSMILES/JSON`
    )
    const smiles = data?.PropertyTable?.Properties?.[0]?.CanonicalSMILES
    if (!smiles) throw new Error('未找到')
    if (target === 'api') form.api_smiles = smiles
    else form.coformer_smiles = smiles
    ElMessage.success(`已获取 SMILES: ${smiles}`)
  } catch {
    ElMessage.error('未找到该分子，请检查名称或 CAS 号')
  } finally {
    loadingRef.value = false
  }
}

function fillMol(target, mol) {
  if (target === 'api') {
    form.api_smiles = mol.smiles
    apiNameQuery.value = mol.name
    apiInputMode.value = 'smiles'
  } else {
    form.coformer_smiles = mol.smiles
    cfNameQuery.value = mol.name
    cfInputMode.value = 'smiles'
  }
}

function fillSample() {
  form.api_smiles = 'Cn1c(=O)c2c(ncn2C)n(C)c1=O'
  form.coformer_smiles = 'OC(=O)CCCC(=O)O'
  apiInputMode.value = 'smiles'
  cfInputMode.value = 'smiles'
  if (models.value.length > 0 && !form.model_id) {
    const ft = models.value.find(m => m.model_type === 'finetuned' && m.is_builtin)
    form.model_id = ft ? ft.id : models.value[0].id
  }
  ElMessage.info('已加载示例：Caffeine + Glutaric acid')
}

async function loadModels() {
  modelsLoading.value = true
  try { const { data } = await modelApi.list(); models.value = data.results || data }
  catch { ElMessage.error('加载模型列表失败') }
  finally { modelsLoading.value = false }
}

async function handlePredict() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  predicting.value = true; result.value = null
  try {
    const { data } = await taskApi.predict({ model_id: form.model_id, api_smiles: form.api_smiles, coformer_smiles: form.coformer_smiles })
    result.value = data.result || data
    ElMessage.success('预测完成')
  } catch (e) { ElMessage.error(e.response?.data?.detail || '预测失败') }
  finally { predicting.value = false }
}

onMounted(loadModels)
</script>

<style scoped>
.predict-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.mol-section { margin-bottom: 8px; padding: 16px; background: #f8fafc; border-radius: 10px; border: 1px solid var(--border); }
.mol-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.mol-section-label { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.input-label { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: .5px; }

.name-search-row { display: flex; gap: 8px; width: 100%; }
.name-search-row .el-input { flex: 1; }

.resolved-smiles { margin-top: 8px; padding: 8px 12px; background: #eff6ff; border-radius: 6px; display: flex; align-items: center; gap: 8px; }
.resolved-label { font-size: 11px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
.resolved-smiles code { font-size: 12px; color: var(--text-secondary); word-break: break-all; }

.quick-picks { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.quick-label { font-size: 12px; color: var(--text-muted); flex-shrink: 0; }
.quick-tag { cursor: pointer; transition: all .2s; }
.quick-tag:hover { background: var(--accent); color: #fff; border-color: var(--accent); }

.result-hero { display: flex; align-items: center; gap: 24px; margin-bottom: 24px; }
.result-class { flex: 1; padding: 20px; border-radius: 10px; text-align: center; }
.result-class.class-0 { background: #f1f5f9; color: #475569; }
.result-class.class-1 { background: #f0fdf4; color: #15803d; }
.result-class.class-2 { background: #fffbeb; color: #b45309; }
.result-class.class-3 { background: #fef2f2; color: #dc2626; }
.result-class-num { font-size: 13px; font-weight: 600; opacity: .7; }
.result-class-label { font-size: 20px; font-weight: 700; margin-top: 4px; }

.result-confidence { text-align: center; padding: 16px 24px; background: #f8fafc; border-radius: 10px; }
.result-confidence { font-size: 28px; font-weight: 800; color: var(--accent); line-height: 1; }
.result-confidence span { display: block; font-size: 12px; font-weight: 500; color: var(--text-muted); margin-top: 4px; }

.prob-bars { margin-bottom: 20px; }
.prob-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.prob-label { width: 90px; font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.prob-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.prob-bar-bg { flex: 1; height: 10px; background: #f1f5f9; border-radius: 5px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 5px; transition: width .6s ease; }
.prob-value { width: 52px; text-align: right; font-size: 13px; font-weight: 600; color: var(--text-primary); }

.result-meta { border-top: 1px solid var(--border); padding-top: 16px; }
.meta-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.meta-key { font-size: 11px; font-weight: 700; color: var(--accent); background: #eff6ff; padding: 2px 8px; border-radius: 4px; flex-shrink: 0; }
.meta-item code { font-size: 12px; color: var(--text-secondary); word-break: break-all; }

.result-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; color: var(--text-muted); }
.placeholder-icon { margin-bottom: 16px; }
.result-placeholder p { font-size: 14px; }
.sample-hint { margin-top: 12px; }
</style>
