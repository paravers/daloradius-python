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
  elements: {
    line: {
      tension: 0.3,
      fill: true,
    },
    point: {
      radius: 3,
      hoverRadius: 6,
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

  if (chartInstance) {
    chartInstance.destroy()
  }

  // Ensure datasets have fill property
  const chartData = {
    ...props.data,
    datasets: props.data.datasets?.map((dataset: any) => ({
      ...dataset,
      fill: dataset.fill !== undefined ? dataset.fill : true,
      tension: dataset.tension !== undefined ? dataset.tension : 0.3,
    })),
  }

  const chartOptions = {
    ...defaultOptions,
    ...props.options,
  }

  chartInstance = new ChartJS(chartCanvas.value, {
    type: 'line',
    data: chartData,
    options: chartOptions,
  })
}

const updateChart = () => {
  if (!chartInstance || !props.data) return

  const chartData = {
    ...props.data,
    datasets: props.data.datasets?.map((dataset: any) => ({
      ...dataset,
      fill: dataset.fill !== undefined ? dataset.fill : true,
      tension: dataset.tension !== undefined ? dataset.tension : 0.3,
    })),
  }

  chartInstance.data = chartData
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