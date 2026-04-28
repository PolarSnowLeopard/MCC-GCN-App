---
layout: home

hero:
  name: MCC-GCN
  text: 用户手册
  tagline: 多组分晶体预测平台 — 五分钟内完成注册到首次预测的全流程
  image:
    src: /logo.svg
    alt: MCC-GCN
  actions:
    - theme: brand
      text: 快速上手 →
      link: /zh/guide/getting-started
    - theme: alt
      text: 系统简介
      link: /zh/guide/introduction
    - theme: alt
      text: English
      link: /

features:
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><circle cx="6" cy="6" r="2.5"/><line x1="9" y1="9" x2="8" y2="8"/><circle cx="18" cy="6" r="2.5"/><line x1="15" y1="9" x2="16" y2="8"/><circle cx="12" cy="20" r="2.5"/><line x1="12" y1="16" x2="12" y2="18"/></svg>
    title: 单次预测
    details: 通过 SMILES、化合物名称或 CAS 号输入两个分子，平台在数秒内返回四分类共晶预测结果。
    link: /zh/guide/predict
    linkText: 查看用法
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
    title: 批量筛选
    details: 上传包含数百至数千对分子的 CSV 文件，通过异步队列处理后以可下载表格形式呈现结果。
    link: /zh/guide/batch
    linkText: 提交批量任务
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
    title: 模型微调
    details: 基于预训练 GCN 主干在自有标注数据集上进行迁移学习，产出团队专属或私有模型。
    link: /zh/guide/finetune
    linkText: 训练你的模型
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
    title: 模型管理
    details: 内置模型、微调模型与外部上传模型集中管理。支持发布、共享或保持私有。
    link: /zh/guide/models
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    title: 完整历史
    details: 所有预测与微调任务自动归档，可随时查阅、回溯或导出历史结果。
    link: /zh/guide/history
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
    title: 中英双语
    details: 一键切换中英文界面，语言偏好跨会话持久保存。
    link: /zh/guide/account
---
