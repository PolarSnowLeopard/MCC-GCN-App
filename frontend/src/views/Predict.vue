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

          <!-- Paper samples quick select -->
          <div class="paper-panel">
            <div class="paper-panel-title">
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/></svg>
              论文实验数据（64 对）
            </div>
            <div class="paper-row">
              <div class="paper-field">
                <span class="paper-label">API</span>
                <el-select v-model="selectedApi" placeholder="选择 API" size="default" style="width:100%" @change="onPaperSelect">
                  <el-option v-for="a in PAPER_APIS" :key="a.cas" :label="a.label" :value="a.cas" />
                </el-select>
              </div>
              <div class="paper-field" style="flex:2">
                <span class="paper-label">Coformer</span>
                <el-select v-model="selectedCf" placeholder="选择 Coformer" size="default" style="width:100%" filterable @change="onPaperSelect">
                  <el-option v-for="c in PAPER_COFORMERS" :key="c.cas" :label="c.label" :value="c.cas" />
                </el-select>
              </div>
            </div>
          </div>

          <!-- API molecule -->
          <div class="mol-section">
            <div class="mol-section-header">
              <span class="mol-section-label">药物分子 (API)</span>
              <el-segmented v-model="apiInputMode" :options="inputModes" size="small" />
            </div>
            <el-form-item v-if="apiInputMode === 'smiles'" prop="api_smiles">
              <el-input v-model="form.api_smiles" placeholder="输入 SMILES">
                <template #prefix><span class="input-label">SMILES</span></template>
              </el-input>
            </el-form-item>
            <el-form-item v-else prop="api_smiles">
              <div class="name-search-row">
                <el-input v-model="apiNameQuery" placeholder="输入分子名称或 CAS 号" @keyup.enter="lookupSmiles('api')" clearable>
                  <template #prefix><span class="input-label">名称</span></template>
                </el-input>
                <el-button type="primary" :loading="apiLookupLoading" @click="lookupSmiles('api')">查询</el-button>
              </div>
              <div v-if="form.api_smiles" class="resolved-smiles">
                <span class="resolved-label">SMILES</span>
                <code>{{ form.api_smiles }}</code>
              </div>
            </el-form-item>
          </div>

          <!-- Coformer molecule -->
          <div class="mol-section">
            <div class="mol-section-header">
              <span class="mol-section-label">辅料分子 (Coformer)</span>
              <el-segmented v-model="cfInputMode" :options="inputModes" size="small" />
            </div>
            <el-form-item v-if="cfInputMode === 'smiles'" prop="coformer_smiles">
              <el-input v-model="form.coformer_smiles" placeholder="输入 SMILES">
                <template #prefix><span class="input-label">SMILES</span></template>
              </el-input>
            </el-form-item>
            <el-form-item v-else prop="coformer_smiles">
              <div class="name-search-row">
                <el-input v-model="cfNameQuery" placeholder="输入分子名称或 CAS 号" @keyup.enter="lookupSmiles('cf')" clearable>
                  <template #prefix><span class="input-label">名称</span></template>
                </el-input>
                <el-button type="primary" :loading="cfLookupLoading" @click="lookupSmiles('cf')">查询</el-button>
              </div>
              <div v-if="form.coformer_smiles" class="resolved-smiles">
                <span class="resolved-label">SMILES</span>
                <code>{{ form.coformer_smiles }}</code>
              </div>
            </el-form-item>
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
          <el-button text type="primary" @click="fillSample">加载示例数据 (KPX + Salicylic acid)</el-button>
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

const selectedApi = ref('')
const selectedCf = ref('')

const form = reactive({ model_id: '', api_smiles: '', coformer_smiles: '' })
const rules = {
  model_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
  api_smiles: [{ required: true, message: '请输入或查询药物 SMILES', trigger: 'blur' }],
  coformer_smiles: [{ required: true, message: '请输入或查询辅料 SMILES', trigger: 'blur' }],
}

const CLASS_COLORS = ['#94a3b8', '#22c55e', '#f59e0b', '#ef4444']
const CLASS_LABELS = ['无共晶', '共晶 I 型', '共晶 II 型', '共晶 III 型']

const PAPER_APIS = [
  { cas: '74638-76-9', name: 'KPX', smiles: 'N=c1[nH]ccc(N)n1O', label: 'KPX (Kopexil) — 74638-76-9' },
  { cas: '55921-65-8', name: 'KPR', smiles: 'N=c1[nH]c(N2CCCC2)cc(N)n1O', label: 'KPR (Kopyrrol) — 55921-65-8' },
]

const PAPER_COFORMERS = [
  { cas: '110-15-6', name: 'Succinic acid', smiles: 'O=C(O)CCC(=O)O', label: 'Succinic acid — 110-15-6' },
  { cas: '110-17-8', name: 'Fumaric acid', smiles: 'O=C(O)/C=C/C(=O)O', label: 'Fumaric acid — 110-17-8' },
  { cas: '124-04-9', name: 'Adipic acid', smiles: 'O=C(O)CCCCC(=O)O', label: 'Adipic acid — 124-04-9' },
  { cas: '65-85-0', name: 'Benzoic acid', smiles: 'O=C(O)c1ccccc1', label: 'Benzoic acid — 65-85-0' },
  { cas: '86-48-6', name: '1-Hydroxy-2-naphthoic acid', smiles: 'O=C(O)c1ccc2ccccc2c1O', label: '1-Hydroxy-2-naphthoic acid — 86-48-6' },
  { cas: '99-96-7', name: '4-Hydroxybenzoic acid', smiles: 'O=C(O)c1ccc(O)cc1', label: '4-Hydroxybenzoic acid — 99-96-7' },
  { cas: '150-13-0', name: '4-Aminobenzoic acid', smiles: 'Nc1ccc(C(=O)O)cc1', label: '4-Aminobenzoic acid — 150-13-0' },
  { cas: '88-99-3', name: 'Phthalic acid', smiles: 'O=C(O)c1ccccc1C(=O)O', label: 'Phthalic acid — 88-99-3' },
  { cas: '121-91-5', name: 'Isophthalic acid', smiles: 'O=C(O)c1cccc(C(=O)O)c1', label: 'Isophthalic acid — 121-91-5' },
  { cas: '69-72-7', name: 'Salicylic acid', smiles: 'O=C(O)c1ccccc1O', label: 'Salicylic acid — 69-72-7' },
  { cas: '10312-55-7', name: '2-Aminoterephthalic acid', smiles: 'Nc1cc(C(=O)O)ccc1C(=O)O', label: '2-Aminoterephthalic acid — 10312-55-7' },
  { cas: '99-50-3', name: 'Protocatechuic acid', smiles: 'O=C(O)c1ccc(O)c(O)c1', label: 'Protocatechuic acid — 99-50-3' },
  { cas: '100-21-0', name: 'Terephthalic acid', smiles: 'O=C(O)c1ccc(C(=O)O)cc1', label: 'Terephthalic acid — 100-21-0' },
  { cas: '65-49-6', name: '4-Aminosalicylic acid', smiles: 'Nc1ccc(C(=O)O)c(O)c1', label: '4-Aminosalicylic acid — 65-49-6' },
  { cas: '89-86-1', name: '2,4-Dihydroxybenzoic acid', smiles: 'O=C(O)c1ccc(O)cc1O', label: '2,4-Dihydroxybenzoic acid — 89-86-1' },
  { cas: '87-69-4', name: 'Tartaric acid', smiles: 'O=C(O)C(O)C(O)C(=O)O', label: 'Tartaric acid — 87-69-4' },
  { cas: '24280-93-1', name: 'Mycophenolic acid', smiles: 'COc1c(C)c2c(c(O)c1C/C=C(\\C)CCC(=O)O)C(=O)OC2', label: 'Mycophenolic acid — 24280-93-1' },
  { cas: '144060-53-7', name: 'Febuxostat', smiles: 'Cc1nc(-c2ccc(OCC(C)C)c(C#N)c2)sc1C(=O)O', label: 'Febuxostat — 144060-53-7' },
  { cas: '120-18-3', name: '2-Naphthalenesulfonic acid', smiles: 'O=S(=O)(O)c1ccc2ccccc2c1', label: '2-Naphthalenesulfonic acid — 120-18-3' },
  { cas: '118-90-1', name: 'o-Toluic acid', smiles: 'Cc1ccccc1C(=O)O', label: 'o-Toluic acid — 118-90-1' },
  { cas: '98-73-7', name: '4-tert-Butylbenzoic acid', smiles: 'CC(C)(C)c1ccc(C(=O)O)cc1', label: '4-tert-Butylbenzoic acid — 98-73-7' },
  { cas: '51-36-5', name: '3,5-Dichlorobenzoic acid', smiles: 'O=C(O)c1cc(Cl)cc(Cl)c1', label: '3,5-Dichlorobenzoic acid — 51-36-5' },
  { cas: '50-85-1', name: '4-Methylsalicylic acid', smiles: 'Cc1ccc(C(=O)O)c(O)c1', label: '4-Methylsalicylic acid — 50-85-1' },
  { cas: '81-04-9', name: '1,5-Naphthalenedisulfonic acid', smiles: 'O=S(=O)(O)c1cccc2c(S(=O)(=O)O)cccc12', label: '1,5-Naphthalenedisulfonic acid — 81-04-9' },
  { cas: '618-83-7', name: '5-Hydroxyisophthalic acid', smiles: 'O=C(O)c1cc(O)cc(C(=O)O)c1', label: '5-Hydroxyisophthalic acid — 618-83-7' },
  { cas: '527-72-0', name: 'Thiophene-2-carboxylic acid', smiles: 'O=C(O)c1cccs1', label: 'Thiophene-2-carboxylic acid — 527-72-0' },
  { cas: '156-38-7', name: '4-Hydroxyphenylacetic acid', smiles: 'O=C(O)Cc1ccc(O)cc1', label: '4-Hydroxyphenylacetic acid — 156-38-7' },
  { cas: '51-44-5', name: '3,4-Dichlorobenzoic acid', smiles: 'O=C(O)c1ccc(Cl)c(Cl)c1', label: '3,4-Dichlorobenzoic acid — 51-44-5' },
  { cas: '50-84-0', name: '2,4-Dichlorobenzoic acid', smiles: 'O=C(O)c1ccc(Cl)cc1Cl', label: '2,4-Dichlorobenzoic acid — 50-84-0' },
  { cas: '1981-4-9', name: '1,5-Naphthalenedisulfonic acid (alt)', smiles: 'O=S(=O)(O)c1cccc2c(S(=O)(=O)O)cccc12', label: '1,5-Naphthalenedisulfonic acid — 1981-4-9' },
  { cas: '491-11-2', name: '3-Chloro-4-nitrophenol', smiles: 'O=[N+]([O-])c1ccc(O)cc1Cl', label: '3-Chloro-4-nitrophenol — 491-11-2' },
  { cas: '499-83-2', name: 'Dipicolinic acid', smiles: 'O=C(O)c1cccc(C(=O)O)n1', label: 'Dipicolinic acid — 499-83-2' },
]

function onPaperSelect() {
  if (selectedApi.value) {
    const api = PAPER_APIS.find(a => a.cas === selectedApi.value)
    if (api) {
      form.api_smiles = api.smiles
      apiInputMode.value = 'smiles'
    }
  }
  if (selectedCf.value) {
    const cf = PAPER_COFORMERS.find(c => c.cas === selectedCf.value)
    if (cf) {
      form.coformer_smiles = cf.smiles
      cfInputMode.value = 'smiles'
    }
  }
}

function fillSample() {
  selectedApi.value = '74638-76-9'
  selectedCf.value = '69-72-7'
  form.api_smiles = PAPER_APIS[0].smiles
  form.coformer_smiles = PAPER_COFORMERS.find(c => c.cas === '69-72-7').smiles
  apiInputMode.value = 'smiles'
  cfInputMode.value = 'smiles'
  if (models.value.length > 0 && !form.model_id) {
    const ft = models.value.find(m => m.model_type === 'finetuned' && m.is_builtin)
    form.model_id = ft ? ft.id : models.value[0].id
  }
  ElMessage.info('已加载示例：KPX + Salicylic acid')
}

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

.paper-panel { margin-bottom: 16px; padding: 14px 16px; background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border-radius: 10px; border: 1px solid #dbeafe; }
.paper-panel-title { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--accent); margin-bottom: 10px; }
.paper-row { display: flex; gap: 10px; }
.paper-field { flex: 1; }
.paper-label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: .5px; }

.mol-section { margin-bottom: 8px; padding: 16px; background: #f8fafc; border-radius: 10px; border: 1px solid var(--border); }
.mol-section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.mol-section-label { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.input-label { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: .5px; }

.name-search-row { display: flex; gap: 8px; width: 100%; }
.name-search-row .el-input { flex: 1; }

.resolved-smiles { margin-top: 8px; padding: 8px 12px; background: #eff6ff; border-radius: 6px; display: flex; align-items: center; gap: 8px; }
.resolved-label { font-size: 11px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
.resolved-smiles code { font-size: 12px; color: var(--text-secondary); word-break: break-all; }

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
