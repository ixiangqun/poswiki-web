import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "POSWIKI",
  description: "战略定位知识库",
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '概念词条', link: '/concepts/' },
      { text: '案例库', link: '/cases/' },
      { text: '分析框架', link: '/frameworks/' },
      { text: '章节笔记', link: '/notes/' },
    ],
    sidebar: {
      '/concepts/': [
        {
          text: '概念词条',
          items: [
            { text: '定位理论概述', link: '/concepts/定位理论概述' },
            { text: '心智阶梯', link: '/concepts/心智阶梯' },
            { text: '品类战略', link: '/concepts/品类战略' },
            { text: '领导者定位原则', link: '/concepts/领导者定位原则' },
            { text: '差异化原则', link: '/concepts/差异化原则' },
            { text: '命名战略', link: '/concepts/命名战略' },
            { text: '重新定位战略', link: '/concepts/重新定位战略' },
            { text: '四种战略形式', link: '/concepts/四种战略形式' },
            { text: '品牌延伸陷阱', link: '/concepts/品牌延伸陷阱' },
            { text: '商业将领特质', link: '/concepts/商业将领特质' },
          ]
        }
      ],
      '/frameworks/': [
        {
          text: '分析框架',
          items: [
            { text: '定位诊断模板', link: '/frameworks/定位诊断模板' },
            { text: '竞争地图', link: '/frameworks/竞争地图' },
            { text: '定位决策框架', link: '/frameworks/定位决策框架' },
            { text: '定位六问决策框架', link: '/frameworks/定位六问决策框架' }
          ]
        }
      ]
    },
    search: {
      provider: 'local'
    }
  }
})
