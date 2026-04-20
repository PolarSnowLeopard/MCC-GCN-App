<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ $t('predict.title') }}</h1>
      <p class="page-desc">{{ $t('predict.desc') }}</p>
    </div>

    <div class="predict-grid">
      <!-- Left: Input panel -->
      <div class="content-card">
        <el-tabs v-model="mainTab" class="main-tabs">
          <!-- ===== Tab 1: Free Prediction ===== -->
          <el-tab-pane :label="$t('predict.tabFree')" name="free">
            <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
              <el-form-item :label="$t('predict.selectModel')" prop="model_id">
                <el-select v-model="form.model_id" :placeholder="$t('predict.selectModelPlaceholder')" style="width:100%" :loading="modelsLoading">
                  <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <span>{{ m.name }}</span>
                      <el-tag size="small" :type="m.model_type === 'pretrained' ? '' : 'success'" round>
                        {{ m.model_type === 'pretrained' ? $t('predict.pretrained') : $t('predict.finetuned') }}
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-tabs v-model="inputTab" type="card" class="input-tabs">
                <!-- SMILES input mode -->
                <el-tab-pane :label="$t('predict.tabSmiles')" name="smiles">
                  <div class="input-hint">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
                    <span>{{ $t('predict.smilesHint') }}</span>
                  </div>
                  <div class="mol-section">
                    <span class="mol-section-label">{{ $t('predict.apiLabel') }}</span>
                    <el-form-item prop="api_smiles">
                      <el-input v-model="form.api_smiles" :placeholder="$t('predict.smilesPlaceholder')">
                        <template #prefix><span class="input-label">SMILES</span></template>
                      </el-input>
                    </el-form-item>
                  </div>
                  <div class="mol-section">
                    <span class="mol-section-label">{{ $t('predict.coformerLabel') }}</span>
                    <el-form-item prop="coformer_smiles">
                      <el-input v-model="form.coformer_smiles" :placeholder="$t('predict.smilesPlaceholder')">
                        <template #prefix><span class="input-label">SMILES</span></template>
                      </el-input>
                    </el-form-item>
                  </div>
                </el-tab-pane>

                <!-- Name / CAS input mode -->
                <el-tab-pane :label="$t('predict.tabName')" name="name">
                  <div class="input-hint hint-warning">
                    <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
                    <span>{{ $t('predict.nameHint') }}</span>
                  </div>
                  <div class="mol-section">
                    <span class="mol-section-label">{{ $t('predict.apiLabel') }}</span>
                    <el-form-item prop="api_smiles">
                      <div class="name-search-row">
                        <el-input v-model="apiNameQuery" :placeholder="$t('predict.namePlaceholder')" @keyup.enter="lookupSmiles('api')" clearable />
                        <el-button type="primary" :loading="apiLookupLoading" @click="lookupSmiles('api')">{{ $t('predict.lookup') }}</el-button>
                      </div>
                      <div v-if="form.api_smiles" class="resolved-smiles">
                        <span class="resolved-label">SMILES</span>
                        <code>{{ form.api_smiles }}</code>
                      </div>
                    </el-form-item>
                  </div>
                  <div class="mol-section">
                    <span class="mol-section-label">{{ $t('predict.coformerLabel') }}</span>
                    <el-form-item prop="coformer_smiles">
                      <div class="name-search-row">
                        <el-input v-model="cfNameQuery" :placeholder="$t('predict.namePlaceholder')" @keyup.enter="lookupSmiles('cf')" clearable />
                        <el-button type="primary" :loading="cfLookupLoading" @click="lookupSmiles('cf')">{{ $t('predict.lookup') }}</el-button>
                      </div>
                      <div v-if="form.coformer_smiles" class="resolved-smiles">
                        <span class="resolved-label">SMILES</span>
                        <code>{{ form.coformer_smiles }}</code>
                      </div>
                    </el-form-item>
                  </div>
                </el-tab-pane>
              </el-tabs>

              <el-button type="primary" :loading="predicting" @click="handlePredict" style="width:100%;height:44px;font-size:15px;margin-top:8px">
                {{ predicting ? $t('predict.predicting') : $t('predict.startPredict') }}
              </el-button>
            </el-form>
          </el-tab-pane>

          <!-- ===== Tab 2: Paper Samples ===== -->
          <el-tab-pane :label="$t('predict.tabPaper')" name="paper">
            <div class="input-hint">
              <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/></svg>
              <span>{{ $t('predict.paperDesc') }}</span>
            </div>

            <el-form :model="paperForm" :rules="paperRules" ref="paperFormRef" label-position="top" size="large">
              <el-form-item :label="$t('predict.selectModel')" prop="model_id">
                <el-select v-model="paperForm.model_id" :placeholder="$t('predict.selectModelPlaceholder')" style="width:100%" :loading="modelsLoading">
                  <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <span>{{ m.name }}</span>
                      <el-tag size="small" :type="m.model_type === 'pretrained' ? '' : 'success'" round>
                        {{ m.model_type === 'pretrained' ? $t('predict.pretrained') : $t('predict.finetuned') }}
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <div class="paper-select-grid">
                <div class="paper-field">
                  <span class="paper-label">{{ $t('predict.apiLabel') }}</span>
                  <el-select v-model="selectedApi" :placeholder="$t('predict.selectApiPlaceholder')" style="width:100%" @change="onPaperApiChange">
                    <el-option v-for="a in PAPER_APIS" :key="a.cas" :label="a.label" :value="a.cas" />
                  </el-select>
                </div>
                <div class="paper-field">
                  <span class="paper-label">{{ $t('predict.coformerLabel') }}</span>
                  <el-select v-model="selectedCf" :placeholder="$t('predict.selectCfPlaceholder')" style="width:100%" filterable @change="onPaperCfChange">
                    <el-option v-for="c in PAPER_COFORMERS" :key="c.cas" :label="c.label" :value="c.cas" />
                  </el-select>
                </div>
              </div>

              <div v-if="paperForm.api_smiles || paperForm.coformer_smiles" class="paper-smiles-preview">
                <div v-if="paperForm.api_smiles" class="resolved-smiles">
                  <span class="resolved-label">API SMILES</span>
                  <code>{{ paperForm.api_smiles }}</code>
                </div>
                <div v-if="paperForm.coformer_smiles" class="resolved-smiles">
                  <span class="resolved-label">Coformer SMILES</span>
                  <code>{{ paperForm.coformer_smiles }}</code>
                </div>
              </div>

              <el-button type="primary" :loading="predicting" @click="handlePaperPredict" style="width:100%;height:44px;font-size:15px;margin-top:16px">
                {{ predicting ? $t('predict.predicting') : $t('predict.paperPredict') }}
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- Right: Result panel -->
      <div class="content-card result-card" v-if="result">
        <div class="card-title">{{ $t('predict.result') }}</div>
        <div class="result-hero">
          <div class="result-class" :class="'class-' + result.prediction">
            <div class="result-class-num">Class {{ result.prediction }}</div>
            <div class="result-class-label">{{ result.label }}</div>
          </div>
          <div class="result-confidence">
            {{ (Math.max(...result.probabilities) * 100).toFixed(1) }}%
            <span>{{ $t('predict.confidence') }}</span>
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
        <p>{{ $t('predict.resultPlaceholder') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi, taskApi } from '../api'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const formRef = ref()
const paperFormRef = ref()
const models = ref([])
const modelsLoading = ref(false)
const predicting = ref(false)
const result = ref(null)

const mainTab = ref('free')
const inputTab = ref('smiles')

const apiNameQuery = ref('')
const cfNameQuery = ref('')
const apiLookupLoading = ref(false)
const cfLookupLoading = ref(false)

const selectedApi = ref('')
const selectedCf = ref('')

const form = reactive({ model_id: '', api_smiles: '', coformer_smiles: '' })
const paperForm = reactive({ model_id: '', api_smiles: '', coformer_smiles: '' })

const rules = computed(() => ({
  model_id: [{ required: true, message: t('predict.modelRequired'), trigger: 'change' }],
  api_smiles: [{ required: true, message: t('predict.smilesRequired'), trigger: 'blur' }],
  coformer_smiles: [{ required: true, message: t('predict.coformerRequired'), trigger: 'blur' }],
}))
const paperRules = computed(() => ({
  model_id: [{ required: true, message: t('predict.modelRequired'), trigger: 'change' }],
}))

const CLASS_COLORS = ['#94a3b8', '#f59e0b', '#22c55e', '#3b82f6']
const CLASS_LABELS = ['Negative', 'Salt', 'Cocrystal', 'Solvate']

const PAPER_APIS = [
  { cas: '74638-76-9', name: 'KPX', smiles: 'Nc1ccnc(N)[n+]1[O-]', label: 'KPX (Kopexil) — 74638-76-9' },
  { cas: '55921-65-8', name: 'KPR', smiles: 'Nc1cc(N2CCCC2)nc(N)[n+]1[O-]', label: 'KPR (Kopyrrol) — 55921-65-8' },
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
  { cas: '303-07-1', name: '2,6-Dihydroxybenzoic acid', smiles: 'O=C(O)c1c(O)cccc1O', label: '2,6-Dihydroxybenzoic acid — 303-07-1' },
  { cas: '491-11-2', name: '3-Chloro-4-nitrophenol', smiles: 'O=[N+]([O-])c1ccc(O)cc1Cl', label: '3-Chloro-4-nitrophenol — 491-11-2' },
  { cas: '499-83-2', name: 'Dipicolinic acid', smiles: 'O=C(O)c1cccc(C(=O)O)n1', label: 'Dipicolinic acid — 499-83-2' },
]

function onPaperApiChange(cas) {
  const api = PAPER_APIS.find(a => a.cas === cas)
  if (api) paperForm.api_smiles = api.smiles
}

function onPaperCfChange(cas) {
  const cf = PAPER_COFORMERS.find(c => c.cas === cas)
  if (cf) paperForm.coformer_smiles = cf.smiles
}

async function lookupSmiles(target) {
  const query = target === 'api' ? apiNameQuery.value.trim() : cfNameQuery.value.trim()
  if (!query) { ElMessage.warning(t('predict.enterNameOrCas')); return }
  const loadingRef = target === 'api' ? apiLookupLoading : cfLookupLoading
  loadingRef.value = true
  try {
    const { data } = await axios.get(
      `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${encodeURIComponent(query)}/property/CanonicalSMILES/JSON`
    )
    const smiles = data?.PropertyTable?.Properties?.[0]?.CanonicalSMILES
    if (!smiles) throw new Error('not found')
    if (target === 'api') form.api_smiles = smiles
    else form.coformer_smiles = smiles
    ElMessage.success(t('predict.smilesResolved', { smiles }))
  } catch {
    ElMessage.error(t('predict.smilesNotFound'))
  } finally {
    loadingRef.value = false
  }
}

async function loadModels() {
  modelsLoading.value = true
  try { const { data } = await modelApi.list(); models.value = data.results || data }
  catch { ElMessage.error(t('predict.predictFailed')) }
  finally { modelsLoading.value = false }
}

function autoSelectModel(formObj) {
  if (models.value.length > 0 && !formObj.model_id) {
    const ft = models.value.find(m => m.model_type === 'finetuned' && m.is_builtin)
    formObj.model_id = ft ? ft.id : models.value[0].id
  }
}

async function handlePredict() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  predicting.value = true; result.value = null
  try {
    const { data } = await taskApi.predict({ model_id: form.model_id, api_smiles: form.api_smiles, coformer_smiles: form.coformer_smiles })
    result.value = data.result || data
    ElMessage.success(t('predict.predictSuccess'))
  } catch (e) { ElMessage.error(e.response?.data?.detail || t('predict.predictFailed')) }
  finally { predicting.value = false }
}

async function handlePaperPredict() {
  autoSelectModel(paperForm)
  if (!paperForm.model_id) { ElMessage.warning(t('predict.modelRequired')); return }
  if (!paperForm.api_smiles || !paperForm.coformer_smiles) {
    ElMessage.warning(t('predict.smilesRequired')); return
  }
  predicting.value = true; result.value = null
  try {
    const { data } = await taskApi.predict({ model_id: paperForm.model_id, api_smiles: paperForm.api_smiles, coformer_smiles: paperForm.coformer_smiles })
    result.value = data.result || data
    ElMessage.success(t('predict.predictSuccess'))
  } catch (e) { ElMessage.error(e.response?.data?.detail || t('predict.predictFailed')) }
  finally { predicting.value = false }
}

onMounted(loadModels)
</script>

<style scoped>
.predict-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }

.main-tabs :deep(.el-tabs__header) { margin-bottom: 20px; }
.main-tabs :deep(.el-tabs__item) { font-size: 15px; font-weight: 600; }

.input-tabs { margin-bottom: 4px; }
.input-tabs :deep(.el-tabs__header) { margin-bottom: 0; }
.input-tabs :deep(.el-tabs__item) { font-size: 13px; }
.input-tabs :deep(.el-tab-pane) { padding-top: 12px; }

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
.input-hint.hint-warning {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}

.mol-section { margin-bottom: 12px; padding: 14px 16px; background: #f8fafc; border-radius: 10px; border: 1px solid var(--border); }
.mol-section-label { display: block; font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
.input-label { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: .5px; }

.name-search-row { display: flex; gap: 8px; width: 100%; }
.name-search-row .el-input { flex: 1; }

.resolved-smiles { margin-top: 8px; padding: 8px 12px; background: #eff6ff; border-radius: 6px; display: flex; align-items: center; gap: 8px; }
.resolved-label { font-size: 11px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
.resolved-smiles code { font-size: 12px; color: var(--text-secondary); word-break: break-all; }

.paper-select-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 8px; }
.paper-field {}
.paper-label { display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }

.paper-smiles-preview { margin-top: 8px; display: flex; flex-direction: column; gap: 6px; }

.result-hero { display: flex; align-items: center; gap: 24px; margin-bottom: 24px; }
.result-class { flex: 1; padding: 20px; border-radius: 10px; text-align: center; }
.result-class.class-0 { background: #f1f5f9; color: #475569; }
.result-class.class-1 { background: #fffbeb; color: #b45309; }
.result-class.class-2 { background: #f0fdf4; color: #15803d; }
.result-class.class-3 { background: #eff6ff; color: #1d4ed8; }
.result-class-num { font-size: 13px; font-weight: 600; opacity: .7; }
.result-class-label { font-size: 20px; font-weight: 700; margin-top: 4px; }

.result-confidence { text-align: center; padding: 16px 24px; background: #f8fafc; border-radius: 10px; }
.result-confidence { font-size: 28px; font-weight: 800; color: var(--accent); line-height: 1; }
.result-confidence span { display: block; font-size: 12px; font-weight: 500; color: var(--text-muted); margin-top: 4px; }

.prob-bars { margin-bottom: 20px; }
.prob-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.prob-label { width: 110px; font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
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
</style>
