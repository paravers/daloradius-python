<!--
会计统计报告页面 (Accounting Reports Page)

提供各种会计统计报告和数据分析功能
-->
<template>
  <div class="accounting-reports-page">
    <!-- Page Header -->
    <PageHeader
      :title="$t('accounting.reports.title')"
      :subtitle="$t('accounting.reports.subtitle')"
      icon="mdi-chart-bar"
    >
      <template #actions>
        <v-btn
          color="primary"
          variant="outlined"
          @click="refreshReports"
          :loading="refreshing"
        >
          <v-icon left>mdi-refresh</v-icon>
          {{ $t('common.refresh') }}
        </v-btn>
        <v-btn
          color="info"
          @click="exportAllReports"
          :loading="exporting"
        >
          <v-icon left>mdi-download</v-icon>
          {{ $t('accounting.export_all_reports') }}
        </v-btn>
      </template>
    </PageHeader>

    <!-- Report Filters -->
    <FilterCard class="mb-6">
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="reportFilters.time_range"
            :items="timeRangeOptions"
            :label="$t('accounting.filters.time_range')"
            clearable
            @update:model-value="updateReports"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="reportFilters.start_date"
            :label="$t('accounting.filters.start_date')"
            type="date"
            clearable
            @update:model-value="updateReports"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="reportFilters.end_date"
            :label="$t('accounting.filters.end_date')"
            type="date"
            clearable
            @update:model-value="updateReports"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="reportFilters.report_type"
            :items="reportTypeOptions"
            :label="$t('accounting.report_type')"
            @update:model-value="updateReports"
          />
        </v-col>
      </v-row>
    </FilterCard>

    <!-- Report Tabs -->
    <v-tabs v-model="activeTab" class="mb-6">
      <v-tab value="overview">
        <v-icon left>mdi-view-dashboard</v-icon>
        {{ $t('accounting.reports.overview') }}
      </v-tab>
      <v-tab value="top-users">
        <v-icon left>mdi-trophy</v-icon>
        {{ $t('accounting.reports.top_users') }}
      </v-tab>
      <v-tab value="traffic-analysis">
        <v-icon left>mdi-chart-line</v-icon>
        {{ $t('accounting.reports.traffic_analysis') }}
      </v-tab>
      <v-tab value="nas-usage">
        <v-icon left>mdi-server</v-icon>
        {{ $t('accounting.reports.nas_usage') }}
      </v-tab>
      <v-tab value="time-analysis">
        <v-icon left>mdi-clock</v-icon>
        {{ $t('accounting.reports.time_analysis') }}
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <!-- Overview Tab -->
      <v-window-item value="overview">
        <OverviewReport
          :data="overviewData"
          :loading="loadingOverview"
          :filters="reportFilters"
          @export="exportReport"
        />
      </v-window-item>

      <!-- Top Users Tab -->
      <v-window-item value="top-users">
        <TopUsersReport
          :data="topUsersData"
          :loading="loadingTopUsers"
          :filters="reportFilters"
          @export="exportReport"
          @view-user="viewUserSessions"
        />
      </v-window-item>

      <!-- Traffic Analysis Tab -->
      <v-window-item value="traffic-analysis">
        <TrafficAnalysisReport
          :data="trafficAnalysisData"
          :loading="loadingTrafficAnalysis"
          :filters="reportFilters"
          @export="exportReport"
        />
      </v-window-item>

      <!-- NAS Usage Tab -->
      <v-window-item value="nas-usage">
        <NasUsageReport
          :data="nasUsageData"
          :loading="loadingNasUsage"
          :filters="reportFilters"
          @export="exportReport"
          @view-nas="viewNasSessions"
        />
      </v-window-item>

      <!-- Time Analysis Tab -->
      <v-window-item value="time-analysis">
        <TimeAnalysisReport
          :data="timeAnalysisData"
          :loading="loadingTimeAnalysis"
          :filters="reportFilters"
          @export="exportReport"
        />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccountingStore } from '@/stores/accounting'
import { useNotification } from '@/composables/useNotification'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterCard from '@/components/common/FilterCard.vue'
import OverviewReport from '@/components/accounting/reports/OverviewReport.vue'
import TopUsersReport from '@/components/accounting/reports/TopUsersReport.vue'
import TrafficAnalysisReport from '@/components/accounting/reports/TrafficAnalysisReport.vue'
import NasUsageReport from '@/components/accounting/reports/NasUsageReport.vue'
import TimeAnalysisReport from '@/components/accounting/reports/TimeAnalysisReport.vue'
import type { ReportFilters } from '@/types/accounting'

// Composables
const router = useRouter()
const { t } = useI18n()
const accountingStore = useAccountingStore()
const notification = useNotification()

// Reactive data
const activeTab = ref('overview')
const refreshing = ref(false)
const exporting = ref(false)

// Loading states for each report
const loadingOverview = ref(false)
const loadingTopUsers = ref(false)
const loadingTrafficAnalysis = ref(false)
const loadingNasUsage = ref(false)
const loadingTimeAnalysis = ref(false)

// Report filters
const reportFilters = reactive<ReportFilters>({
  time_range: 'THIS_MONTH',
  start_date: null,
  end_date: null,
  report_type: 'summary'
})

// Computed properties
const overviewData = computed(() => accountingStore.overviewReport)
const topUsersData = computed(() => accountingStore.topUsersReport)
const trafficAnalysisData = computed(() => accountingStore.trafficAnalysisReport)
const nasUsageData = computed(() => accountingStore.nasUsageReport)
const timeAnalysisData = computed(() => accountingStore.timeAnalysisReport)

// Filter options
const timeRangeOptions = computed(() => [
  { title: t('accounting.time_ranges.today'), value: 'TODAY' },
  { title: t('accounting.time_ranges.yesterday'), value: 'YESTERDAY' },
  { title: t('accounting.time_ranges.this_week'), value: 'THIS_WEEK' },
  { title: t('accounting.time_ranges.last_week'), value: 'LAST_WEEK' },
  { title: t('accounting.time_ranges.this_month'), value: 'THIS_MONTH' },
  { title: t('accounting.time_ranges.last_month'), value: 'LAST_MONTH' },
  { title: t('accounting.time_ranges.this_year'), value: 'THIS_YEAR' }
])

const reportTypeOptions = computed(() => [
  { title: t('accounting.report_types.summary'), value: 'summary' },
  { title: t('accounting.report_types.detailed'), value: 'detailed' },
  { title: t('accounting.report_types.comparative'), value: 'comparative' }
])

// Methods
const refreshReports = async () => {
  try {
    refreshing.value = true
    await updateReports()
    notification.success(t('accounting.reports_refreshed'))
  } catch (error) {
    notification.error(t('accounting.errors.refresh_reports_failed'))
    console.error('Failed to refresh reports:', error)
  } finally {
    refreshing.value = false
  }
}

const updateReports = async () => {
  // Load reports based on active tab
  switch (activeTab.value) {
    case 'overview':
      await loadOverviewReport()
      break
    case 'top-users':
      await loadTopUsersReport()
      break
    case 'traffic-analysis':
      await loadTrafficAnalysisReport()
      break
    case 'nas-usage':
      await loadNasUsageReport()
      break
    case 'time-analysis':
      await loadTimeAnalysisReport()
      break
    default:
      await loadAllReports()
  }
}

const loadOverviewReport = async () => {
  try {
    loadingOverview.value = true
    await accountingStore.fetchOverviewReport(reportFilters)
  } catch (error) {
    console.error('Failed to load overview report:', error)
  } finally {
    loadingOverview.value = false
  }
}

const loadTopUsersReport = async () => {
  try {
    loadingTopUsers.value = true
    await accountingStore.fetchTopUsersReport({
      ...reportFilters,
      limit: 50
    })
  } catch (error) {
    console.error('Failed to load top users report:', error)
  } finally {
    loadingTopUsers.value = false
  }
}

const loadTrafficAnalysisReport = async () => {
  try {
    loadingTrafficAnalysis.value = true
    await accountingStore.fetchTrafficAnalysisReport(reportFilters)
  } catch (error) {
    console.error('Failed to load traffic analysis report:', error)
  } finally {
    loadingTrafficAnalysis.value = false
  }
}

const loadNasUsageReport = async () => {
  try {
    loadingNasUsage.value = true
    await accountingStore.fetchNasUsageReport(reportFilters)
  } catch (error) {
    console.error('Failed to load NAS usage report:', error)
  } finally {
    loadingNasUsage.value = false
  }
}

const loadTimeAnalysisReport = async () => {
  try {
    loadingTimeAnalysis.value = true
    await accountingStore.fetchTimeAnalysisReport(reportFilters)
  } catch (error) {
    console.error('Failed to load time analysis report:', error)
  } finally {
    loadingTimeAnalysis.value = false
  }
}

const loadAllReports = async () => {
  await Promise.all([
    loadOverviewReport(),
    loadTopUsersReport(),
    loadTrafficAnalysisReport(),
    loadNasUsageReport(),
    loadTimeAnalysisReport()
  ])
}

const exportReport = async (reportType: string, format: string = 'csv') => {
  try {
    exporting.value = true
    await accountingStore.exportReport({
      type: reportType,
      format: format,
      filters: reportFilters
    })
    notification.success(t('accounting.report_exported'))
  } catch (error) {
    notification.error(t('accounting.errors.export_report_failed'))
    console.error('Failed to export report:', error)
  } finally {
    exporting.value = false
  }
}

const exportAllReports = async () => {
  try {
    exporting.value = true
    await accountingStore.exportAllReports({
      format: 'xlsx',
      filters: reportFilters
    })
    notification.success(t('accounting.all_reports_exported'))
  } catch (error) {
    notification.error(t('accounting.errors.export_all_reports_failed'))
    console.error('Failed to export all reports:', error)
  } finally {
    exporting.value = false
  }
}

const viewUserSessions = (username: string) => {
  router.push(`/accounting/sessions/user/${username}`)
}

const viewNasSessions = (nasIp: string) => {
  router.push(`/accounting/sessions?nas_ip=${nasIp}`)
}

// Watchers
watch(activeTab, (newTab) => {
  updateReports()
})

watch(
  () => [reportFilters.time_range, reportFilters.start_date, reportFilters.end_date],
  () => {
    updateReports()
  },
  { deep: true }
)

// Lifecycle
onMounted(() => {
  loadAllReports()
})
</script>

<style scoped>
.accounting-reports-page {
  padding: 24px;
}

.v-tabs {
  margin-bottom: 24px;
}

.v-window {
  margin-top: 24px;
}
</style>