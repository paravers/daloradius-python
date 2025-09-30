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
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
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
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.1)',
      },
    },
    y: {
      display: true,
      beginAtZero: true,
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.1)',
      },
    },
  },
  interaction: {
    mode: 'nearest' as const,
    axis: 'x' as const,
    intersect: false,
  },
  animation: {
    duration: 1000,
    easing: 'easeInOutQuart' as const,
  },
}

const createChart = () => {
  if (!chartCanvas.value || !props.data) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  // Merge options
  const chartOptions = {
    ...defaultOptions,
    ...props.options,
  }

  // Create new chart
  chartInstance = new ChartJS(chartCanvas.value, {
    type: 'line',
    data: props.data,
    options: chartOptions,
  })
}

const updateChart = () => {
  if (!chartInstance || !props.data) return

  chartInstance.data = props.data
  chartInstance.update('active')
}

// Watch for data changes
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

// Watch for options changes
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