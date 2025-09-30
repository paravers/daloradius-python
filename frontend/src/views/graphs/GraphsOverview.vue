<template>
  <div class="graphs-container">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-chart-line"></i>
        图表统计
      </h1>
      <p class="page-description">
        系统统计图表和数据可视化分析
      </p>
    </div>

    <!-- Quick Stats Cards -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-icon">
          <i class="fas fa-users text-blue"></i>
        </div>
        <div class="stats-content">
          <h3>{{ realTimeStats.online_users }}</h3>
          <p>在线用户</p>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">
          <i class="fas fa-sign-in-alt text-green"></i>
        </div>
        <div class="stats-content">
          <h3>{{ realTimeStats.today_logins }}</h3>
          <p>今日登录</p>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">
          <i class="fas fa-download text-purple"></i>
        </div>
        <div class="stats-content">
          <h3>{{ realTimeStats.today_traffic_gb }}GB</h3>
          <p>今日流量</p>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">
          <i class="fas fa-heartbeat text-red"></i>
        </div>
        <div class="stats-content">
          <h3>{{ realTimeStats.system_health }}%</h3>
          <p>系统健康度</p>
        </div>
      </div>
    </div>

    <!-- Graph Navigation Tabs -->
    <div class="graph-tabs">
      <button 
        v-for="tab in graphTabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="setActiveTab(tab.id)"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </button>
    </div>

    <!-- Graph Content -->
    <div class="graph-content">
      <!-- Overall Logins Tab -->
      <div v-if="activeTab === 'overall_logins'" class="graph-section">
        <GraphCard
          title="整体登录统计"
          subtitle="系统登录成功、失败统计"
          :loading="loading.overall_logins"
          @refresh="loadOverallLogins"
        >
          <template #controls>
            <DateRangePicker 
              v-model:start-date="dateRanges.overall_logins.start"
              v-model:end-date="dateRanges.overall_logins.end"
              @change="loadOverallLogins"
            />
            <GranularitySelector
              v-model="granularity.overall_logins"
              @change="loadOverallLogins"
            />
          </template>
          
          <LineChart
            v-if="chartData.overall_logins"
            :data="chartData.overall_logins"
            :options="chartOptions.line"
            height="400"
          />
        </GraphCard>
      </div>

      <!-- Download/Upload Stats Tab -->
      <div v-if="activeTab === 'download_upload'" class="graph-section">
        <GraphCard
          title="下载/上传统计"
          subtitle="流量使用统计分析"
          :loading="loading.download_upload"
          @refresh="loadDownloadUploadStats"
        >
          <template #controls>
            <DateRangePicker 
              v-model:start-date="dateRanges.download_upload.start"
              v-model:end-date="dateRanges.download_upload.end"
              @change="loadDownloadUploadStats"
            />
            <GranularitySelector
              v-model="granularity.download_upload"
              @change="loadDownloadUploadStats"
            />
          </template>
          
          <AreaChart
            v-if="chartData.download_upload"
            :data="chartData.download_upload"
            :options="chartOptions.area"
            height="400"
          />
        </GraphCard>
      </div>

      <!-- Logged Users Tab -->
      <div v-if="activeTab === 'logged_users'" class="graph-section">
        <GraphCard
          title="已登录用户"
          subtitle="用户活跃度和增长趋势"
          :loading="loading.logged_users"
          @refresh="loadLoggedUsers"
        >
          <template #controls>
            <DateRangePicker 
              v-model:start-date="dateRanges.logged_users.start"
              v-model:end-date="dateRanges.logged_users.end"
              @change="loadLoggedUsers"
            />
          </template>
          
          <LineChart
            v-if="chartData.logged_users"
            :data="chartData.logged_users"
            :options="chartOptions.multiLine"
            height="400"
          />
        </GraphCard>
      </div>

      <!-- All-time Stats Tab -->
      <div v-if="activeTab === 'alltime_stats'" class="graph-section">
        <div class="alltime-stats-grid">
          <GraphCard
            title="系统总览"
            subtitle="全系统统计概览"
            :loading="loading.alltime_stats"
            @refresh="loadAlltimeStats"
            class="overview-card"
          >
            <BarChart
              v-if="chartData.alltime_stats"
              :data="chartData.alltime_stats"
              :options="chartOptions.bar"
              height="300"
            />
          </GraphCard>

          <GraphCard
            title="热门用户"
            subtitle="流量使用排行"
            :loading="loading.top_users"
            @refresh="loadTopUsers"
            class="top-users-card"
          >
            <template #controls>
              <select v-model="topUsersType" @change="loadTopUsers" class="form-select">
                <option value="total">总流量</option>
                <option value="upload">上传流量</option>
                <option value="download">下载流量</option>
              </select>
            </template>
            
            <HorizontalBarChart
              v-if="chartData.top_users"
              :data="chartData.top_users"
              :options="chartOptions.horizontalBar"
              height="300"
            />
          </GraphCard>

          <GraphCard
            title="流量对比"
            subtitle="上传下载对比分析"
            :loading="loading.traffic_comparison"
            @refresh="loadTrafficComparison"
            class="traffic-comparison-card"
          >
            <StackedAreaChart
              v-if="chartData.traffic_comparison"
              :data="chartData.traffic_comparison"
              :options="chartOptions.stackedArea"
              height="300"
            />
          </GraphCard>

          <GraphCard
            title="系统性能"
            subtitle="服务器性能监控"
            :loading="loading.system_performance"
            @refresh="loadSystemPerformance"
            class="performance-card"
          >
            <template #controls>
              <select v-model="performanceHours" @change="loadSystemPerformance" class="form-select">
                <option value="24">24小时</option>
                <option value="48">48小时</option>
                <option value="168">7天</option>
              </select>
            </template>
            
            <LineChart
              v-if="chartData.system_performance"
              :data="chartData.system_performance"
              :options="chartOptions.performance"
              height="300"
            />
          </GraphCard>
        </div>
      </div>
    </div>

    <!-- Export Options -->
    <div class="export-section">
      <h3>数据导出</h3>
      <div class="export-buttons">
        <button @click="exportData('csv')" class="btn btn-outline-primary">
          <i class="fas fa-file-csv"></i>
          导出 CSV
        </button>
        <button @click="exportData('json')" class="btn btn-outline-secondary">
          <i class="fas fa-file-code"></i>
          导出 JSON
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  LineChart, 
  AreaChart, 
  BarChart, 
  HorizontalBarChart, 
  StackedAreaChart 
} from '@/components/charts'
import GraphCard from '@/components/graphs/GraphCard.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'
import GranularitySelector from '@/components/common/GranularitySelector.vue'
import { graphsApi } from '@/api/graphs'
import { formatDate, addDays } from '@/utils/date'
import { showNotification } from '@/utils/notifications'

// Reactive state
const router = useRouter()
const activeTab = ref('overall_logins')
const topUsersType = ref('total')
const performanceHours = ref(24)

// Loading states
const loading = reactive({
  overall_logins: false,
  download_upload: false,
  logged_users: false,
  alltime_stats: false,
  top_users: false,
  traffic_comparison: false,
  system_performance: false,
  realtime: false
})

// Chart data
const chartData = reactive({
  overall_logins: null,
  download_upload: null,
  logged_users: null,
  alltime_stats: null,
  top_users: null,
  traffic_comparison: null,
  system_performance: null
})

// Date ranges
const dateRanges = reactive({
  overall_logins: {
    start: formatDate(addDays(new Date(), -30)),
    end: formatDate(new Date())
  },
  download_upload: {
    start: formatDate(addDays(new Date(), -30)),
    end: formatDate(new Date())
  },
  logged_users: {
    start: formatDate(addDays(new Date(), -30)),
    end: formatDate(new Date())
  }
})

// Granularity settings
const granularity = reactive({
  overall_logins: 'day',
  download_upload: 'day'
})

// Real-time stats
const realTimeStats = reactive({
  online_users: 0,
  today_logins: 0,
  today_traffic_gb: 0,
  system_health: 0,
  last_updated: null
})

// Graph tabs configuration
const graphTabs = [
  {
    id: 'overall_logins',
    name: '整体登录',
    icon: 'fas fa-sign-in-alt'
  },
  {
    id: 'download_upload',
    name: '上传下载',
    icon: 'fas fa-exchange-alt'
  },
  {
    id: 'logged_users',
    name: '用户活跃',
    icon: 'fas fa-users'
  },
  {
    id: 'alltime_stats',
    name: '综合统计',
    icon: 'fas fa-chart-pie'
  }
]

// Chart options
const chartOptions = {
  line: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  },
  area: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '流量 (GB)'
        }
      }
    },
    fill: true
  },
  multiLine: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '用户数量'
        }
      }
    }
  },
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  },
  horizontalBar: {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: '流量 (GB)'
        }
      }
    }
  },
  stackedArea: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        stacked: true,
        title: {
          display: true,
          text: '流量 (GB)'
        }
      },
      x: {
        stacked: true
      }
    }
  },
  performance: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: '使用率 (%)'
        }
      }
    }
  }
}

// Methods
const setActiveTab = (tabId: string) => {
  activeTab.value = tabId
  
  // Load data for the active tab if not already loaded
  switch (tabId) {
    case 'overall_logins':
      if (!chartData.overall_logins) loadOverallLogins()
      break
    case 'download_upload':
      if (!chartData.download_upload) loadDownloadUploadStats()
      break
    case 'logged_users':
      if (!chartData.logged_users) loadLoggedUsers()
      break
    case 'alltime_stats':
      loadAlltimeStats()
      break
  }
}

const loadRealTimeStats = async () => {
  try {
    loading.realtime = true
    const data = await graphsApi.getRealTimeStats()
    
    Object.assign(realTimeStats, {
      online_users: data.online_users || 0,
      today_logins: data.today_logins || 0,
      today_traffic_gb: data.today_traffic_gb || 0,
      system_health: data.system_health || 0,
      last_updated: new Date()
    })
  } catch (error) {
    console.error('Failed to load real-time stats:', error)
    showNotification('加载实时统计失败', 'error')
  } finally {
    loading.realtime = false
  }
}

const loadOverallLogins = async () => {
  try {
    loading.overall_logins = true
    const data = await graphsApi.getOverallLogins({
      start_date: dateRanges.overall_logins.start,
      end_date: dateRanges.overall_logins.end,
      granularity: granularity.overall_logins
    })
    chartData.overall_logins = data.data
  } catch (error) {
    console.error('Failed to load overall logins:', error)
    showNotification('加载登录统计失败', 'error')
  } finally {
    loading.overall_logins = false
  }
}

const loadDownloadUploadStats = async () => {
  try {
    loading.download_upload = true
    const data = await graphsApi.getDownloadUploadStats({
      start_date: dateRanges.download_upload.start,
      end_date: dateRanges.download_upload.end,
      granularity: granularity.download_upload
    })
    chartData.download_upload = data.data
  } catch (error) {
    console.error('Failed to load download/upload stats:', error)
    showNotification('加载流量统计失败', 'error')
  } finally {
    loading.download_upload = false
  }
}

const loadLoggedUsers = async () => {
  try {
    loading.logged_users = true
    const data = await graphsApi.getLoggedUsers({
      start_date: dateRanges.logged_users.start,
      end_date: dateRanges.logged_users.end
    })
    chartData.logged_users = data.data
  } catch (error) {
    console.error('Failed to load logged users:', error)
    showNotification('加载用户活跃统计失败', 'error')
  } finally {
    loading.logged_users = false
  }
}

const loadAlltimeStats = async () => {
  try {
    loading.alltime_stats = true
    const data = await graphsApi.getAlltimeStats()
    chartData.alltime_stats = data.data
  } catch (error) {
    console.error('Failed to load alltime stats:', error)
    showNotification('加载综合统计失败', 'error')
  } finally {
    loading.alltime_stats = false
  }
}

const loadTopUsers = async () => {
  try {
    loading.top_users = true
    const data = await graphsApi.getTopUsers({
      start_date: formatDate(addDays(new Date(), -30)),
      end_date: formatDate(new Date()),
      limit: 10,
      traffic_type: topUsersType.value
    })
    chartData.top_users = data.data
  } catch (error) {
    console.error('Failed to load top users:', error)
    showNotification('加载热门用户失败', 'error')
  } finally {
    loading.top_users = false
  }
}

const loadTrafficComparison = async () => {
  try {
    loading.traffic_comparison = true
    const data = await graphsApi.getTrafficComparison({
      start_date: formatDate(addDays(new Date(), -30)),
      end_date: formatDate(new Date())
    })
    chartData.traffic_comparison = data.data
  } catch (error) {
    console.error('Failed to load traffic comparison:', error)
    showNotification('加载流量对比失败', 'error')
  } finally {
    loading.traffic_comparison = false
  }
}

const loadSystemPerformance = async () => {
  try {
    loading.system_performance = true
    const data = await graphsApi.getSystemPerformance({
      hours: performanceHours.value
    })
    chartData.system_performance = data.data
  } catch (error) {
    console.error('Failed to load system performance:', error)
    showNotification('加载系统性能失败', 'error')
  } finally {
    loading.system_performance = false
  }
}

const exportData = async (format: string) => {
  try {
    const params = {
      graph_type: activeTab.value,
      start_date: dateRanges[activeTab.value]?.start || formatDate(addDays(new Date(), -30)),
      end_date: dateRanges[activeTab.value]?.end || formatDate(new Date())
    }
    
    if (format === 'csv') {
      await graphsApi.exportDataCsv(params)
    } else {
      await graphsApi.exportDataJson(params)
    }
    
    showNotification(`数据已导出为 ${format.toUpperCase()} 格式`, 'success')
  } catch (error) {
    console.error('Failed to export data:', error)
    showNotification('数据导出失败', 'error')
  }
}

// Auto-refresh real-time stats
const startRealTimeUpdates = () => {
  loadRealTimeStats()
  setInterval(loadRealTimeStats, 30000) // Refresh every 30 seconds
}

// Lifecycle
onMounted(() => {
  startRealTimeUpdates()
  loadOverallLogins() // Load default tab data
})
</script>

<style scoped>
.graphs-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.page-title i {
  margin-right: 12px;
  color: #3b82f6;
}

.page-description {
  font-size: 1.1rem;
  color: #6b7280;
  margin: 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
}

.stats-icon {
  margin-right: 16px;
  font-size: 2rem;
}

.stats-icon .text-blue { color: #3b82f6; }
.stats-icon .text-green { color: #10b981; }
.stats-icon .text-purple { color: #8b5cf6; }
.stats-icon .text-red { color: #ef4444; }

.stats-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
}

.stats-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.graph-tabs {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 8px;
  margin-bottom: 32px;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.tab-button {
  flex: 1;
  padding: 12px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  min-width: 120px;
}

.tab-button:hover {
  color: #3b82f6;
  background: #f3f4f6;
}

.tab-button.active {
  color: white;
  background: #3b82f6;
  box-shadow: 0 2px 4px -1px rgba(59, 130, 246, 0.5);
}

.tab-button i {
  margin-right: 8px;
}

.graph-content {
  margin-bottom: 32px;
}

.graph-section {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.alltime-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
}

.export-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.export-section h3 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.export-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid;
}

.btn i {
  margin-right: 8px;
}

.btn-outline-primary {
  color: #3b82f6;
  border-color: #3b82f6;
  background: white;
}

.btn-outline-primary:hover {
  background: #3b82f6;
  color: white;
}

.btn-outline-secondary {
  color: #6b7280;
  border-color: #6b7280;
  background: white;
}

.btn-outline-secondary:hover {
  background: #6b7280;
  color: white;
}

.form-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  font-size: 0.875rem;
}

.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

@media (max-width: 768px) {
  .graphs-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .graph-tabs {
    padding: 4px;
  }
  
  .tab-button {
    padding: 10px 16px;
    font-size: 0.875rem;
  }
  
  .alltime-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>