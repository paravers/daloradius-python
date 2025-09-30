<!--
活跃会话页面 (Active Sessions Page)

显示当前活跃的会话，支持实时监控和会话管理
-->
<template>
  <div class="active-sessions-page">
    <!-- Page Header -->
    <PageHeader
      :title="$t('accounting.active_sessions.title')"
      :subtitle="$t('accounting.active_sessions.subtitle')"
      icon="mdi-play-circle"
    >
      <template #actions>
        <v-btn
          color="primary"
          variant="outlined"
          @click="refreshSessions"
          :loading="loading"
        >
          <v-icon left>mdi-refresh</v-icon>
          {{ $t('common.refresh') }}
        </v-btn>
        <v-btn
          color="info"
          variant="outlined"
          @click="toggleAutoRefresh"
        >
          <v-icon left>
            {{ autoRefresh ? 'mdi-pause' : 'mdi-play' }}
          </v-icon>
          {{ autoRefresh ? $t('common.pause_refresh') : $t('common.auto_refresh') }}
        </v-btn>
      </template>
    </PageHeader>

    <!-- Active Sessions Statistics -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>
        <v-icon left>mdi-chart-line</v-icon>
        {{ $t('accounting.active_session_statistics') }}
        <v-spacer />
        <v-chip color="success" size="small">
          <v-icon left size="small">mdi-circle</v-icon>
          {{ $t('accounting.live_data') }}
        </v-chip>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h4 text-success">
                {{ formatNumber(activeStats.total_active) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.total_active_sessions') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h4 text-info">
                {{ formatBytes(activeStats.total_current_traffic) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.current_traffic') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h4 text-warning">
                {{ formatNumber(activeStats.unique_users) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.unique_active_users') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h4 text-primary">
                {{ formatDuration(activeStats.average_session_duration) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.average_duration') }}</p>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Filters Section -->
    <FilterCard class="mb-6">
      <v-row>
        <v-col cols="12" sm="6" md="4">
          <v-text-field
            v-model="filters.username"
            :label="$t('accounting.filters.username')"
            clearable
            @keyup.enter="applyFilters"
          />
        </v-col>
        <v-col cols="12" sm="6" md="4">
          <v-text-field
            v-model="filters.nas_ip"
            :label="$t('accounting.filters.nas_ip')"
            clearable
            @keyup.enter="applyFilters"
          />
        </v-col>
        <v-col cols="12" sm="6" md="4">
          <v-select
            v-model="filters.sort_by"
            :items="sortOptions"
            :label="$t('accounting.filters.sort_by')"
            @update:model-value="applyFilters"
          />
        </v-col>
      </v-row>

      <template #actions>
        <v-btn
          color="primary"
          @click="applyFilters"
        >
          <v-icon left>mdi-filter</v-icon>
          {{ $t('common.apply_filters') }}
        </v-btn>
        <v-btn
          variant="outlined"
          @click="clearFilters"
        >
          <v-icon left>mdi-filter-off</v-icon>
          {{ $t('common.clear_filters') }}
        </v-btn>
      </template>
    </FilterCard>

    <!-- Active Sessions Table -->
    <DataTable
      :headers="headers"
      :items="activeSessions"
      :loading="loading"
      :total-items="totalItems"
      :page="currentPage"
      :items-per-page="itemsPerPage"
      @update:page="updatePage"
      @update:items-per-page="updateItemsPerPage"
      :search="searchQuery"
      @update:search="updateSearch"
    >
      <!-- Username Column -->
      <template #item.username="{ item }">
        <div class="d-flex align-center">
          <v-avatar size="32" class="mr-2">
            <v-icon>mdi-account</v-icon>
          </v-avatar>
          <div>
            <v-chip
              color="primary"
              size="small"
              @click="navigateTo(`/accounting/sessions/user/${item.username}`)"
              class="cursor-pointer"
            >
              {{ item.username }}
            </v-chip>
          </div>
        </div>
      </template>

      <!-- NAS IP Column -->
      <template #item.nasipaddress="{ item }">
        <v-chip
          color="info"
          size="small"
          variant="outlined"
        >
          {{ item.nasipaddress }}
        </v-chip>
      </template>

      <!-- Session Duration Column -->
      <template #item.session_duration="{ item }">
        <div class="d-flex align-center">
          <v-icon left size="small" color="success">mdi-clock</v-icon>
          <span class="font-weight-bold">
            {{ formatSessionDuration(item.acctstarttime) }}
          </span>
        </div>
      </template>

      <!-- Current Traffic Column -->
      <template #item.current_traffic="{ item }">
        <div>
          <div class="text-success">
            ↓ {{ formatBytes(item.acctinputoctets || 0) }}
          </div>
          <div class="text-info">
            ↑ {{ formatBytes(item.acctoutputoctets || 0) }}
          </div>
        </div>
      </template>

      <!-- Throughput Column -->
      <template #item.throughput="{ item }">
        <div class="text-center">
          <v-progress-circular
            :model-value="calculateThroughputPercentage(item)"
            :color="getThroughputColor(item)"
            size="40"
            width="4"
          >
            <small>{{ formatThroughput(calculateThroughput(item)) }}</small>
          </v-progress-circular>
        </div>
      </template>

      <!-- Start Time Column -->
      <template #item.acctstarttime="{ item }">
        <div>
          <div>{{ formatDateTime(item.acctstarttime) }}</div>
          <small class="text-grey">
            {{ getTimeAgo(item.acctstarttime) }}
          </small>
        </div>
      </template>

      <!-- Status Column -->
      <template #item.status="{ item }">
        <v-chip
          color="success"
          size="small"
          variant="elevated"
        >
          <v-icon left size="small">mdi-wifi</v-icon>
          {{ $t('accounting.online') }}
        </v-chip>
      </template>

      <!-- Actions Column -->
      <template #item.actions="{ item }">
        <v-btn
          icon
          size="small"
          @click="viewSessionDetails(item)"
        >
          <v-icon>mdi-eye</v-icon>
        </v-btn>
        <v-btn
          icon
          size="small"
          color="warning"
          @click="disconnectSession(item)"
          :loading="disconnectingSessionId === item.radacctid"
        >
          <v-icon>mdi-connection</v-icon>
        </v-btn>
        <v-btn
          icon
          size="small"
          color="error"
          @click="terminateSession(item)"
          :loading="terminatingSessionId === item.radacctid"
        >
          <v-icon>mdi-stop</v-icon>
        </v-btn>
      </template>
    </DataTable>

    <!-- Session Details Dialog -->
    <SessionDetailsDialog
      v-model="detailsDialog"
      :session="selectedSession"
    />

    <!-- Disconnect Confirmation Dialog -->
    <ConfirmDialog
      v-model="disconnectDialog"
      :title="$t('accounting.disconnect_session')"
      :message="$t('accounting.disconnect_session_message', { username: selectedSession?.username })"
      :confirm-text="$t('accounting.disconnect')"
      confirm-color="warning"
      @confirm="confirmDisconnect"
    />

    <!-- Terminate Confirmation Dialog -->
    <ConfirmDialog
      v-model="terminateDialog"
      :title="$t('accounting.terminate_session')"
      :message="$t('accounting.terminate_session_message', { username: selectedSession?.username })"
      :confirm-text="$t('accounting.terminate')"
      confirm-color="error"
      @confirm="confirmTerminate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccountingStore } from '@/stores/accounting'
import { useNotification } from '@/composables/useNotification'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterCard from '@/components/common/FilterCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import SessionDetailsDialog from '@/components/accounting/SessionDetailsDialog.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import { formatBytes, formatNumber, formatDateTime, formatDuration } from '@/utils/formatters'
import type { AccountingSession, ActiveSessionFilters } from '@/types/accounting'

// Composables
const router = useRouter()
const { t } = useI18n()
const accountingStore = useAccountingStore()
const notification = useNotification()

// Reactive data
const loading = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref<NodeJS.Timeout | null>(null)
const detailsDialog = ref(false)
const disconnectDialog = ref(false)
const terminateDialog = ref(false)
const selectedSession = ref<AccountingSession | null>(null)
const disconnectingSessionId = ref<number | null>(null)
const terminatingSessionId = ref<number | null>(null)
const searchQuery = ref('')

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(20)

// Filters
const filters = reactive<ActiveSessionFilters>({
  username: null,
  nas_ip: null,
  sort_by: 'acctstarttime'
})

// Computed properties
const activeSessions = computed(() => accountingStore.activeSessions)
const totalItems = computed(() => accountingStore.activeSessionsPagination.total)
const activeStats = computed(() => accountingStore.activeSessionStatistics)

// Table headers
const headers = computed(() => [
  { title: t('accounting.username'), key: 'username', sortable: true },
  { title: t('accounting.nas_ip'), key: 'nasipaddress', sortable: true },
  { title: t('accounting.framed_ip'), key: 'framedipaddress', sortable: true },
  { title: t('accounting.start_time'), key: 'acctstarttime', sortable: true },
  { title: t('accounting.session_duration'), key: 'session_duration', sortable: false },
  { title: t('accounting.current_traffic'), key: 'current_traffic', sortable: false },
  { title: t('accounting.throughput'), key: 'throughput', sortable: false },
  { title: t('accounting.status'), key: 'status', sortable: false },
  { title: t('common.actions'), key: 'actions', sortable: false, width: 150 }
])

// Sort options
const sortOptions = computed(() => [
  { title: t('accounting.sort.start_time'), value: 'acctstarttime' },
  { title: t('accounting.sort.username'), value: 'username' },
  { title: t('accounting.sort.traffic'), value: 'total_bytes' },
  { title: t('accounting.sort.nas_ip'), value: 'nasipaddress' }
])

// Methods
const navigateTo = (path: string) => {
  router.push(path)
}

const loadActiveSessions = async () => {
  try {
    loading.value = true
    await accountingStore.fetchActiveSessions({
      page: currentPage.value,
      page_size: itemsPerPage.value,
      username: filters.username,
      nas_ip: filters.nas_ip
    })
  } catch (error) {
    notification.error(t('accounting.errors.load_active_sessions_failed'))
    console.error('Failed to load active sessions:', error)
  } finally {
    loading.value = false
  }
}

const refreshSessions = () => {
  loadActiveSessions()
}

const applyFilters = () => {
  currentPage.value = 1
  loadActiveSessions()
}

const clearFilters = () => {
  filters.username = null
  filters.nas_ip = null
  filters.sort_by = 'acctstarttime'
  applyFilters()
}

const updatePage = (page: number) => {
  currentPage.value = page
  loadActiveSessions()
}

const updateItemsPerPage = (perPage: number) => {
  itemsPerPage.value = perPage
  currentPage.value = 1
  loadActiveSessions()
}

const updateSearch = (query: string) => {
  searchQuery.value = query
  // Implement local search if needed
}

const viewSessionDetails = (session: AccountingSession) => {
  selectedSession.value = session
  detailsDialog.value = true
}

const disconnectSession = (session: AccountingSession) => {
  selectedSession.value = session
  disconnectDialog.value = true
}

const terminateSession = (session: AccountingSession) => {
  selectedSession.value = session
  terminateDialog.value = true
}

const confirmDisconnect = async () => {
  if (!selectedSession.value) return

  try {
    disconnectingSessionId.value = selectedSession.value.radacctid
    await accountingStore.disconnectSession(selectedSession.value.radacctid)
    notification.success(t('accounting.session_disconnected'))
    await loadActiveSessions() // Refresh the list
  } catch (error) {
    notification.error(t('accounting.errors.disconnect_session_failed'))
    console.error('Failed to disconnect session:', error)
  } finally {
    disconnectingSessionId.value = null
    disconnectDialog.value = false
  }
}

const confirmTerminate = async () => {
  if (!selectedSession.value) return

  try {
    terminatingSessionId.value = selectedSession.value.radacctid
    await accountingStore.terminateSession(selectedSession.value.radacctid)
    notification.success(t('accounting.session_terminated'))
    await loadActiveSessions() // Refresh the list
  } catch (error) {
    notification.error(t('accounting.errors.terminate_session_failed'))
    console.error('Failed to terminate session:', error)
  } finally {
    terminatingSessionId.value = null
    terminateDialog.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    refreshInterval.value = setInterval(() => {
      loadActiveSessions()
    }, 30000) // Refresh every 30 seconds
    notification.info(t('accounting.auto_refresh_enabled'))
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
    notification.info(t('accounting.auto_refresh_disabled'))
  }
}

// Helper methods
const formatSessionDuration = (startTime: string) => {
  const start = new Date(startTime)
  const now = new Date()
  const durationMs = now.getTime() - start.getTime()
  const durationSeconds = Math.floor(durationMs / 1000)
  return formatDuration(durationSeconds)
}

const getTimeAgo = (dateTime: string) => {
  const date = new Date(dateTime)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  
  if (diffMinutes < 1) return t('common.just_now')
  if (diffMinutes < 60) return t('common.minutes_ago', { count: diffMinutes })
  
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return t('common.hours_ago', { count: diffHours })
  
  const diffDays = Math.floor(diffHours / 24)
  return t('common.days_ago', { count: diffDays })
}

const calculateThroughput = (session: AccountingSession) => {
  if (!session.acctstarttime) return 0
  
  const start = new Date(session.acctstarttime)
  const now = new Date()
  const durationSeconds = Math.floor((now.getTime() - start.getTime()) / 1000)
  
  if (durationSeconds === 0) return 0
  
  const totalBytes = (session.acctinputoctets || 0) + (session.acctoutputoctets || 0)
  return totalBytes / durationSeconds // bytes per second
}

const calculateThroughputPercentage = (session: AccountingSession) => {
  const throughput = calculateThroughput(session)
  const maxThroughput = 1024 * 1024 // 1 MB/s as reference
  return Math.min((throughput / maxThroughput) * 100, 100)
}

const getThroughputColor = (session: AccountingSession) => {
  const percentage = calculateThroughputPercentage(session)
  if (percentage > 80) return 'error'
  if (percentage > 50) return 'warning'
  return 'success'
}

const formatThroughput = (bytesPerSecond: number) => {
  if (bytesPerSecond < 1024) return `${Math.round(bytesPerSecond)}B/s`
  if (bytesPerSecond < 1024 * 1024) return `${Math.round(bytesPerSecond / 1024)}KB/s`
  return `${Math.round(bytesPerSecond / (1024 * 1024))}MB/s`
}

// Watchers
watch([currentPage, itemsPerPage], () => {
  loadActiveSessions()
})

// Lifecycle
onMounted(() => {
  loadActiveSessions()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.active-sessions-page {
  padding: 24px;
}

.cursor-pointer {
  cursor: pointer;
}

.text-grey {
  color: #666;
}
</style>