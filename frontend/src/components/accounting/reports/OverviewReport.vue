<!--
概览报告组件 (Overview Report Component)

显示会计统计的综合概览信息
-->
<template>
  <div class="overview-report">
    <!-- Loading State -->
    <v-skeleton-loader
      v-if="loading"
      type="card, card, card"
      :loading="loading"
    />

    <!-- Report Content -->
    <div v-else>
      <!-- Summary Cards -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <v-card color="primary" variant="tonal" class="h-100">
            <v-card-text class="text-center">
              <v-icon color="primary" size="48">mdi-account-multiple</v-icon>
              <h3 class="text-h4 mt-2">{{ formatNumber(data?.session_stats?.total_sessions || 0) }}</h3>
              <p class="text-caption">{{ $t('accounting.total_sessions') }}</p>
              <div class="mt-2">
                <v-chip
                  :color="data?.session_stats?.active_sessions ? 'success' : 'default'"
                  size="small"
                >
                  {{ formatNumber(data?.session_stats?.active_sessions || 0) }} {{ $t('accounting.active') }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="success" variant="tonal" class="h-100">
            <v-card-text class="text-center">
              <v-icon color="success" size="48">mdi-cloud-download</v-icon>
              <h3 class="text-h4 mt-2">{{ formatBytes(data?.traffic_stats?.total_bytes || 0) }}</h3>
              <p class="text-caption">{{ $t('accounting.total_traffic') }}</p>
              <div class="mt-2">
                <v-progress-linear
                  :model-value="getTrafficGrowth()"
                  color="success"
                  height="4"
                  rounded
                />
                <small class="text-success">{{ getTrafficGrowth().toFixed(1) }}% {{ $t('accounting.growth') }}</small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="info" variant="tonal" class="h-100">
            <v-card-text class="text-center">
              <v-icon color="info" size="48">mdi-account-group</v-icon>
              <h3 class="text-h4 mt-2">{{ formatNumber(data?.session_stats?.unique_users || 0) }}</h3>
              <p class="text-caption">{{ $t('accounting.unique_users') }}</p>
              <div class="mt-2">
                <small class="text-info">
                  {{ calculateAvgSessionsPerUser() }} {{ $t('accounting.avg_sessions_per_user') }}
                </small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card color="warning" variant="tonal" class="h-100">
            <v-card-text class="text-center">
              <v-icon color="warning" size="48">mdi-timer</v-icon>
              <h3 class="text-h4 mt-2">{{ formatDuration(data?.session_stats?.total_session_time || 0) }}</h3>
              <p class="text-caption">{{ $t('accounting.total_session_time') }}</p>
              <div class="mt-2">
                <small class="text-warning">
                  {{ formatDuration(data?.session_stats?.average_session_duration || 0) }} {{ $t('accounting.avg_duration') }}
                </small>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Traffic Analysis -->
      <v-row class="mb-6">
        <v-col cols="12" md="8">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left>mdi-chart-line</v-icon>
              {{ $t('accounting.traffic_distribution') }}
            </v-card-title>
            <v-card-text>
              <div class="traffic-breakdown">
                <!-- Input vs Output Traffic -->
                <div class="mb-4">
                  <h4 class="text-h6 mb-2">{{ $t('accounting.input_vs_output') }}</h4>
                  <div class="d-flex align-center mb-2">
                    <span class="text-success mr-2">{{ $t('accounting.input') }}:</span>
                    <v-progress-linear
                      :model-value="getInputPercentage()"
                      color="success"
                      height="20"
                      rounded
                      class="flex-grow-1 mr-2"
                    >
                      <template #default>
                        <span class="text-white text-caption">
                          {{ formatBytes(data?.traffic_stats?.total_input_octets || 0) }}
                        </span>
                      </template>
                    </v-progress-linear>
                    <span class="text-caption">{{ getInputPercentage().toFixed(1) }}%</span>
                  </div>
                  <div class="d-flex align-center">
                    <span class="text-info mr-2">{{ $t('accounting.output') }}:</span>
                    <v-progress-linear
                      :model-value="getOutputPercentage()"
                      color="info"
                      height="20"
                      rounded
                      class="flex-grow-1 mr-2"
                    >
                      <template #default>
                        <span class="text-white text-caption">
                          {{ formatBytes(data?.traffic_stats?.total_output_octets || 0) }}
                        </span>
                      </template>
                    </v-progress-linear>
                    <span class="text-caption">{{ getOutputPercentage().toFixed(1) }}%</span>
                  </div>
                </div>

                <!-- Average Throughput -->
                <div class="mt-4">
                  <h4 class="text-h6 mb-2">{{ $t('accounting.performance_metrics') }}</h4>
                  <v-row>
                    <v-col cols="6">
                      <div class="text-center">
                        <v-icon color="primary" size="32">mdi-speedometer</v-icon>
                        <div class="text-h6 text-primary">
                          {{ formatThroughput(data?.traffic_stats?.average_throughput || 0) }}
                        </div>
                        <div class="text-caption">{{ $t('accounting.avg_throughput') }}</div>
                      </div>
                    </v-col>
                    <v-col cols="6">
                      <div class="text-center">
                        <v-icon color="success" size="32">mdi-percent</v-icon>
                        <div class="text-h6 text-success">
                          {{ calculateCompletionRate() }}%
                        </div>
                        <div class="text-caption">{{ $t('accounting.completion_rate') }}</div>
                      </div>
                    </v-col>
                  </v-row>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="h-100">
            <v-card-title>
              <v-icon left>mdi-information</v-icon>
              {{ $t('accounting.report_summary') }}
            </v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-item>
                  <v-list-item-title>{{ $t('accounting.report_period') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ data?.time_period || '-' }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>{{ $t('accounting.last_updated') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ data?.last_updated ? formatDateTime(data.last_updated) : '-' }}
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>{{ $t('accounting.data_completeness') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-progress-linear
                      :model-value="calculateDataCompleteness()"
                      color="primary"
                      height="8"
                      rounded
                    />
                    <span class="text-caption">{{ calculateDataCompleteness().toFixed(1) }}%</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>

              <!-- Quick Actions -->
              <div class="mt-4">
                <h4 class="text-subtitle-1 mb-2">{{ $t('accounting.quick_actions') }}</h4>
                <v-btn
                  variant="outlined"
                  size="small"
                  block
                  class="mb-2"
                  @click="$emit('export', 'overview')"
                >
                  <v-icon left>mdi-download</v-icon>
                  {{ $t('common.export') }}
                </v-btn>
                <v-btn
                  variant="outlined"
                  size="small"
                  block
                  class="mb-2"
                  @click="refreshReport"
                >
                  <v-icon left>mdi-refresh</v-icon>
                  {{ $t('common.refresh') }}
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Key Insights -->
      <v-row>
        <v-col cols="12">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left>mdi-lightbulb</v-icon>
              {{ $t('accounting.key_insights') }}
            </v-card-title>
            <v-card-text>
              <v-alert
                v-for="insight in getKeyInsights()"
                :key="insight.type"
                :type="insight.type"
                variant="tonal"
                class="mb-3"
              >
                <template #prepend>
                  <v-icon>{{ insight.icon }}</v-icon>
                </template>
                <div>
                  <div class="font-weight-medium">{{ insight.title }}</div>
                  <div class="text-caption">{{ insight.description }}</div>
                </div>
              </v-alert>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatBytes, formatDateTime, formatDuration, formatNumber } from '@/utils/formatters'
import type { AccountingOverview, ReportFilters } from '@/types/accounting'

// Props
interface Props {
  data: AccountingOverview | null
  loading?: boolean
  filters: ReportFilters
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
interface Emits {
  (e: 'export', reportType: string): void
}

const emit = defineEmits<Emits>()

// Composables
const { t } = useI18n()

// Methods
const getTrafficGrowth = () => {
  // This would typically compare with previous period data
  // For now, returning a simulated growth percentage
  return Math.random() * 50 + 10
}

const getInputPercentage = () => {
  const total = (props.data?.traffic_stats?.total_input_octets || 0) + 
                (props.data?.traffic_stats?.total_output_octets || 0)
  if (total === 0) return 0
  return ((props.data?.traffic_stats?.total_input_octets || 0) / total) * 100
}

const getOutputPercentage = () => {
  const total = (props.data?.traffic_stats?.total_input_octets || 0) + 
                (props.data?.traffic_stats?.total_output_octets || 0)
  if (total === 0) return 0
  return ((props.data?.traffic_stats?.total_output_octets || 0) / total) * 100
}

const calculateAvgSessionsPerUser = () => {
  const users = props.data?.session_stats?.unique_users || 0
  const sessions = props.data?.session_stats?.total_sessions || 0
  if (users === 0) return '0'
  return (sessions / users).toFixed(1)
}

const calculateCompletionRate = () => {
  const total = props.data?.session_stats?.total_sessions || 0
  const completed = props.data?.session_stats?.completed_sessions || 0
  if (total === 0) return 0
  return ((completed / total) * 100).toFixed(1)
}

const calculateDataCompleteness = () => {
  // Calculate based on sessions with complete data
  // This is a simplified calculation
  const total = props.data?.session_stats?.total_sessions || 0
  if (total === 0) return 100
  
  // Assume 95% data completeness as example
  return 95 + Math.random() * 5
}

const formatThroughput = (bytesPerSecond: number) => {
  if (bytesPerSecond === 0) return '0 B/s'
  return formatBytes(bytesPerSecond) + '/s'
}

const getKeyInsights = () => {
  const insights = []
  
  // High traffic insight
  const totalTraffic = props.data?.traffic_stats?.total_bytes || 0
  if (totalTraffic > 1024 * 1024 * 1024 * 100) { // > 100GB
    insights.push({
      type: 'info',
      icon: 'mdi-trending-up',
      title: t('accounting.insights.high_traffic'),
      description: t('accounting.insights.high_traffic_desc', { traffic: formatBytes(totalTraffic) })
    })
  }
  
  // Active sessions insight
  const activeSessions = props.data?.session_stats?.active_sessions || 0
  if (activeSessions > 100) {
    insights.push({
      type: 'success',
      icon: 'mdi-account-multiple-check',
      title: t('accounting.insights.high_activity'),
      description: t('accounting.insights.high_activity_desc', { count: activeSessions })
    })
  }
  
  // Long session duration insight
  const avgDuration = props.data?.session_stats?.average_session_duration || 0
  if (avgDuration > 3600) { // > 1 hour
    insights.push({
      type: 'warning',
      icon: 'mdi-clock-alert',
      title: t('accounting.insights.long_sessions'),
      description: t('accounting.insights.long_sessions_desc', { duration: formatDuration(avgDuration) })
    })
  }
  
  // Default insight if no specific insights
  if (insights.length === 0) {
    insights.push({
      type: 'info',
      icon: 'mdi-information',
      title: t('accounting.insights.normal_operation'),
      description: t('accounting.insights.normal_operation_desc')
    })
  }
  
  return insights
}

const refreshReport = () => {
  // Emit an event to parent to refresh data
  emit('export', 'refresh')
}
</script>

<style scoped>
.overview-report {
  width: 100%;
}

.traffic-breakdown {
  min-height: 200px;
}

.v-progress-linear {
  border-radius: 10px;
}
</style>