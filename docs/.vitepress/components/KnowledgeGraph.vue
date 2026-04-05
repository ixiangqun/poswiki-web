<template>
  <div class="graph-container">
    <div ref="chartRef" class="echarts-graph"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null

onMounted(async () => {
  chartInstance = echarts.init(chartRef.value)
  
  // Show loading
  chartInstance.showLoading('default', {
    text: '正在初始化脑图宇宙...',
    color: '#0055ff',
    textColor: '#888',
    maskColor: 'rgba(255, 255, 255, 0.8)',
    zlevel: 0
  })

  try {
    const response = await fetch('/graph_data.json')
    const json = await response.json()
    
    chartInstance.hideLoading()

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}'
      },
      legend: {
        data: ['概念', '案例', '框架', '笔记'],
        bottom: 0,
        textStyle: {
          color: '#666'
        }
      },
      color: [
        '#3B82F6', // 蓝色 - 概念
        '#10B981', // 绿色 - 案例
        '#F59E0B', // 橙色 - 框架
        '#9CA3AF'  // 灰色 - 笔记
      ],
      series: [
        {
          type: 'graph',
          layout: 'force',
          data: json.nodes,
          links: json.links,
          categories: json.categories,
          roam: true, // 允许拖拽和平移
          label: {
            show: true,
            position: 'right',
            formatter: '{b}',
            fontSize: 12,
            color: '#333'
          },
          force: {
            repulsion: 300,
            edgeLength: [50, 150], // 线条长度
            gravity: 0.1
          },
          lineStyle: {
            color: 'source',
            curveness: 0.1, // 略带弧度的连线显得更优美
            opacity: 0.4,
            width: 1.5
          },
          emphasis: {
            focus: 'adjacency', // 悬停高亮相邻节点
            lineStyle: {
              width: 3,
              opacity: 1
            }
          }
        }
      ]
    }
    
    chartInstance.setOption(option)
    
    // 点击任意节点，在原网页路由里直接跳转！
    chartInstance.on('click', function(params) {
      if (params.dataType === 'node') {
        const route_base = params.data.id
        const catArray = ['concepts', 'cases', 'frameworks', 'notes']
        const prefix = catArray[params.data.category] || 'concepts'
        window.location.href = `/${prefix}/${route_base}`
      }
    })

  } catch (err) {
    console.error("加载知识图谱失败", err)
    chartInstance.hideLoading()
  }
  
  // Responsive resize
  const resizeHandler = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }
  window.addEventListener('resize', resizeHandler)
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
    if (chartInstance) {
      chartInstance.dispose()
    }
  })
})
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 550px;
  margin: 2rem 0;
  border-radius: 12px;
  border: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg-soft);
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.echarts-graph {
  width: 100%;
  height: 100%;
}

/* 适配暗黑模式 */
:root.dark .graph-container {
  background: #111;
  border-color: #333;
}
:root.dark :deep(canvas) {
  /* 使用 CSS 滤镜降低亮色过爆感，或者你也可以在 options 里写入更复杂的 dark 配色 */
}
</style>
