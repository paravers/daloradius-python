<template>
  <div class="chart-container">
    <canvas ref="chartRef" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

// 注册 Chart.js 组件
Chart.register(...registerables)

interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
    borderWidth?: number
    fill?: boolean
    tension?: number
  }[]
}

interface Props {
  data: ChartData
  type: 'line' | 'bar' | 'area' | 'pie' | 'doughnut'
  options?: any
  width?: number
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'line',
  width: 400,
  height: 300,
  options: () => ({})
})

const chartRef = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
  },
  scales: {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    }
  },
  elements: {
    line: {
      tension: 0.4
    },
    point: {
      radius: 4,
      hoverRadius: 6
    }
  }
}

const getChartType = (type: string) => {
  if (type === 'area') return 'line'
  return type
}

const processData = (data: ChartData, type: string) => {
  if (type === 'area') {
    return {
      ...data,
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        fill: true,
        backgroundColor: dataset.backgroundColor ? 
          dataset.backgroundColor.replace('1)', '0.2)') : 
          'rgba(24, 144, 255, 0.2)',
        borderColor: dataset.borderColor || dataset.backgroundColor || '#1890ff',
        borderWidth: 2
      }))
    }
  }
  return data
}

const createChart = async () => {
  if (!chartRef.value) return
  
  await nextTick()
  
  // 销毁现有图表
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  const ctx = chartRef.value.getContext('2d')
  if (!ctx) return
  
  const chartType = getChartType(props.type)
  const chartData = processData(props.data, props.type)
  
  chartInstance = new Chart(ctx, {
    type: chartType as any,
    data: chartData,
    options: {
      ...defaultOptions,
      ...props.options
    }
  })
}

onMounted(() => {
  createChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })

watch(() => props.type, () => {
  createChart()
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

canvas {
  max-width: 100%;
  max-height: 100%;
}
</style>