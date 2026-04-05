import { defineConfig } from 'vitepress'

export default defineConfig({
  ignoreDeadLinks: true,
  title: "定位词典",
  description: "A professional wiki for Strategic Positioning",
  themeConfig: {
    logo: '/logo.png',
    siteTitle: false, // 因为 logo 图片自带“定位词典”文字，隐藏系统默认文字标题
    // 置空顶栏右上角的快捷链接导航，完全依赖首页大盘和全局搜索
    nav: [],
    
    // 配置网站底部的版权栏，提升公信力与学术正式感
    footer: {
      message: '基于特劳特与里斯定位理论构建的公开战略知识索引。',
      copyright: 'Copyright © 2026 POSWIKI 定位词典'
    },

    // 强制关闭所有左侧导航栏，消除由于左右两边都有侧边栏带来的“复杂感”
    sidebar: false,

    // 保留并优化右侧的页内大纲（TOC），方便读者在阅读长篇单页时跳转
    outline: {
      label: '本页分类',
      level: [2, 3]
    },
    
    search: {
      provider: 'local'
    }
  }
})
