import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

import App from './App.vue'
import router from './router'
import i18n from './i18n'

const elLocales = { 'zh-CN': zhCn, en }

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(ElementPlus, { locale: elLocales[i18n.global.locale.value] || zhCn })

watch(
  () => i18n.global.locale.value,
  (lang) => {
    app.config.globalProperties.$ELEMENT = { locale: elLocales[lang] || zhCn }
  },
)

app.mount('#app')
