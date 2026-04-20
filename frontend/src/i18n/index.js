import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import en from './en'

const savedLang = localStorage.getItem('lang') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: savedLang,
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': zhCN, en },
})

export function setLocale(lang) {
  i18n.global.locale.value = lang
  localStorage.setItem('lang', lang)
  document.documentElement.setAttribute('lang', lang === 'zh-CN' ? 'zh' : 'en')
}

export default i18n
