<template>
  <div class="chart-wrapper">
    <canvas 
      ref="chartCanvas"
      :style="{ height: height + 'px' }"
    ></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface Props {
  data: any
  options?: any
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  options: () => ({}),
  height: 400
})

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: ChartJS | null = null

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    },
  },
  scales: {
    x: {
      display: true,
      beginAtZero: true,
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.1)',
      },
    },
    y: {
      display: true,
      grid: {
        display: false,
      },
    },
  },
  animation: {
    duration: 1000,
    easing: 'easeInOutQuart' as const,
  },
}

const createChart = () => {
  if (!chartCanvas.value || !props.data) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const chartOptions = {
    ...defaultOptions,
    ...props.options,
  }

  chartInstance = new ChartJS(chartCanvas.value, {
    type: 'bar',
    data: props.data,
    options: chartOptions,
  })
}

const updateChart = () => {
  if (!chartInstance || !props.data) return

  chartInstance.data = props.data
  chartInstance.update('active')
}

watch(
  () => props.data,
  (newData) => {
    if (newData) {
      if (chartInstance) {
        updateChart()
      } else {
        nextTick(() => createChart())
      }
    }
  },
  { deep: true }
)

watch(
  () => props.options,
  () => {
    if (chartInstance) {
      const chartOptions = {
        ...defaultOptions,
        ...props.options,
      }
      chartInstance.options = chartOptions
      chartInstance.update('active')
    }
  },
  { deep: true }
)

onMounted(() => {
  nextTick(() => {
    if (props.data) {
      createChart()
    }
  })
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
}

canvas {
  width: 100% !important;
}
</style>