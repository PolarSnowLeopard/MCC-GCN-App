import { defineConfig } from 'vitepress'

const enNav = [
  { text: 'Guide', link: '/guide/getting-started' },
  { text: 'FAQ', link: '/guide/faq' },
  { text: 'Back to App', link: '/' },
]

const zhNav = [
  { text: '指南', link: '/zh/guide/getting-started' },
  { text: '常见问题', link: '/zh/guide/faq' },
  { text: '返回应用', link: '/' },
]

const enSidebar = [
  {
    text: 'Getting Started',
    items: [
      { text: 'Introduction', link: '/guide/introduction' },
      { text: 'Quick Start', link: '/guide/getting-started' },
      { text: 'Interface Tour', link: '/guide/interface' },
    ],
  },
  {
    text: 'Core Workflows',
    items: [
      { text: 'Single Prediction', link: '/guide/predict' },
      { text: 'Batch Screening', link: '/guide/batch' },
      { text: 'Fine-tuning', link: '/guide/finetune' },
    ],
  },
  {
    text: 'Manage',
    items: [
      { text: 'Models', link: '/guide/models' },
      { text: 'History', link: '/guide/history' },
      { text: 'Account & Language', link: '/guide/account' },
    ],
  },
  {
    text: 'Reference',
    items: [
      { text: 'Data Formats', link: '/guide/data-formats' },
      { text: 'FAQ', link: '/guide/faq' },
    ],
  },
]

const zhSidebar = [
  {
    text: '快速上手',
    items: [
      { text: '系统简介', link: '/zh/guide/introduction' },
      { text: '5 分钟快速上手', link: '/zh/guide/getting-started' },
      { text: '界面总览', link: '/zh/guide/interface' },
    ],
  },
  {
    text: '核心工作流',
    items: [
      { text: '单次预测', link: '/zh/guide/predict' },
      { text: '批量筛选', link: '/zh/guide/batch' },
      { text: '模型微调', link: '/zh/guide/finetune' },
    ],
  },
  {
    text: '日常管理',
    items: [
      { text: '模型管理', link: '/zh/guide/models' },
      { text: '历史记录', link: '/zh/guide/history' },
      { text: '账户与语言', link: '/zh/guide/account' },
    ],
  },
  {
    text: '参考',
    items: [
      { text: '数据格式', link: '/zh/guide/data-formats' },
      { text: '常见问题', link: '/zh/guide/faq' },
    ],
  },
]

export default defineConfig({
  base: '/docs/',
  title: 'MCC-GCN',
  description: 'User guide for the MCC-GCN cocrystal prediction platform.',
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/docs/favicon.svg' }],
  ],

  themeConfig: {
    logo: '/logo.svg',
    socialLinks: [
      { icon: 'github', link: 'https://github.com/PolarSnowLeopard/MCC-GCN-App' },
    ],
    search: { provider: 'local' },
    outline: { level: [2, 3] },
  },

  locales: {
    root: {
      label: 'English',
      lang: 'en-US',
      themeConfig: {
        nav: enNav,
        sidebar: { '/guide/': enSidebar },
        editLink: {
          pattern:
            'https://github.com/PolarSnowLeopard/MCC-GCN-App/edit/main/docs/:path',
          text: 'Edit this page on GitHub',
        },
        docFooter: { prev: 'Previous', next: 'Next' },
        lastUpdatedText: 'Last updated',
      },
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      themeConfig: {
        nav: zhNav,
        sidebar: { '/zh/guide/': zhSidebar },
        editLink: {
          pattern:
            'https://github.com/PolarSnowLeopard/MCC-GCN-App/edit/main/docs/:path',
          text: '在 GitHub 上编辑此页',
        },
        docFooter: { prev: '上一页', next: '下一页' },
        outlineTitle: '本页内容',
        lastUpdatedText: '上次更新',
        returnToTopLabel: '返回顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '主题',
        lightModeSwitchTitle: '切换到浅色模式',
        darkModeSwitchTitle: '切换到深色模式',
      },
    },
  },
})
