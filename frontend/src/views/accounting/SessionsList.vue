<!--
会计统计会话列表页面 (Accounting Sessions List Page)

显示所有会计统计会话记录，支持筛选、排序和分页
-->
<template>
  <div class="sessions-page">
    <!-- Page Header -->
    <PageHeader
      :title="$t('accounting.sessions.title')"
      :subtitle="$t('accounting.sessions.subtitle')"
      icon="mdi-format-list-bulleted"
    >
      <template #actions>
        <v-btn
          color="success"
          @click="navigateTo('/accounting/active')"
        >
          <v-icon left>mdi-play-circle</v-icon>
          {{ $t('accounting.view_active_sessions') }}
        </v-btn>
      </template>
    </PageHeader>

    <!-- Filters Section -->
    <FilterCard class="mb-6">
      <v-row>
        <!-- Time Range Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="filters.time_range"
            :items="timeRangeOptions"
            :label="$t('accounting.filters.time_range')"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>

        <!-- Custom Date Range -->
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="filters.start_date"
            :label="$t('accounting.filters.start_date')"
            type="date"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="filters.end_date"
            :label="$t('accounting.filters.end_date')"
            type="date"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>

        <!-- Username Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="filters.username"
            :label="$t('accounting.filters.username')"
            clearable
            @keyup.enter="applyFilters"
          />
        </v-col>

        <!-- NAS IP Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="filters.nasipaddress"
            :label="$t('accounting.filters.nas_ip')"
            clearable
            @keyup.enter="applyFilters"
          />
        </v-col>

        <!-- Framed IP Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-text-field
            v-model="filters.framedipaddress"
            :label="$t('accounting.filters.framed_ip')"
            clearable
            @keyup.enter="applyFilters"
          />
        </v-col>

        <!-- Service Type Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="filters.servicetype"
            :items="serviceTypeOptions"
            :label="$t('accounting.filters.service_type')"
            clearable
            @update:model-value="applyFilters"
          />
        </v-col>

        <!-- Active Only Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-checkbox
            v-model="filters.active_only"
            :label="$t('accounting.filters.active_only')"
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
        <v-btn
          color="info"
          variant="outlined"
          @click="exportSessions"
          :loading="exportLoading"
        >
          <v-icon left>mdi-download</v-icon>
          {{ $t('common.export') }}
        </v-btn>
      </template>
    </FilterCard>

    <!-- Statistics Summary -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>
        <v-icon left>mdi-chart-bar</v-icon>
        {{ $t('accounting.session_statistics') }}
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h5 text-primary">
                {{ formatNumber(sessionStats.total_sessions) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.total_sessions') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h5 text-success">
                {{ formatNumber(sessionStats.active_sessions) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.active_sessions') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h5 text-info">
                {{ formatBytes(sessionStats.total_traffic) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.total_traffic') }}</p>
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-center">
              <h3 class="text-h5 text-warning">
                {{ formatDuration(sessionStats.total_session_time) }}
              </h3>
              <p class="text-caption">{{ $t('accounting.total_session_time') }}</p>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Sessions Data Table -->
    <DataTable
      :headers="headers"
      :items="sessions"
      :loading="loading"
      :total-items="totalItems"
      :page="currentPage"
      :items-per-page="itemsPerPage"
      :sort-by="sortBy"
      :sort-desc="sortDesc"
      @update:page="updatePage"
      @update:items-per-page="updateItemsPerPage"
      @update:sort-by="updateSortBy"
      @update:sort-desc="updateSortDesc"
      :search="searchQuery"
      @update:search="updateSearch"
    >
      <!-- Username Column -->
      <template #item.username="{ item }">
        <v-chip
          color="primary"
          size="small"
          @click="navigateTo(`/accounting/sessions/user/${item.username}`)"
          class="cursor-pointer"
        >
          {{ item.username }}
        </v-chip>
      </template>

      <!-- Status Column -->
      <template #item.is_active="{ item }">
        <v-chip
          :color="item.is_active ? 'success' : 'default'"
          size="small"
        >
          <v-icon left size="small">
            {{ item.is_active ? 'mdi-play-circle' : 'mdi-stop-circle' }}
          </v-icon>
          {{ item.is_active ? $t('accounting.active') : $t('accounting.completed') }}
        </v-chip>
      </template>

      <!-- Session Time Column -->
      <template #item.acctsessiontime="{ item }">
        <span v-if="item.acctsessiontime">
          {{ formatDuration(item.acctsessiontime) }}
        </span>
        <span v-else class="text-grey">-</span>
      </template>

      <!-- Input Traffic Column -->
      <template #item.acctinputoctets="{ item }">
        <span class="text-success">
          {{ formatBytes(item.acctinputoctets || 0) }}
        </span>
      </template>

      <!-- Output Traffic Column -->
      <template #item.acctoutputoctets="{ item }">
        <span class="text-info">
          {{ formatBytes(item.acctoutputoctets || 0) }}
        </span>
      </template>

      <!-- Total Traffic Column -->
      <template #item.total_bytes="{ item }">
        <span class="text-primary font-weight-bold">
          {{ formatBytes(item.total_bytes || 0) }}
        </span>
      </template>

      <!-- Start Time Column -->
      <template #item.acctstarttime="{ item }">
        <span v-if="item.acctstarttime">
          {{ formatDateTime(item.acctstarttime) }}
        </span>
        <span v-else class="text-grey">-</span>
      </template>

      <!-- Stop Time Column -->
      <template #item.acctstoptime="{ item }">
        <span v-if="item.acctstoptime">
          {{ formatDateTime(item.acctstoptime) }}
        </span>
        <span v-else class="text-grey">{{ $t('accounting.ongoing') }}</span>
      </template>

      <!-- Actions Column -->
      <template #item.actions="{ item }">
        <v-btn
          icon
          size="small"
          @click="viewSession(item)"
        >
          <v-icon>mdi-eye</v-icon>
        </v-btn>
        <v-btn
          icon
          size="small"
          @click="showSessionDetails(item)"
        >
          <v-icon>mdi-information</v-icon>
        </v-btn>
      </template>
    </DataTable>

    <!-- Session Details Dialog -->
    <SessionDetailsDialog
      v-model="detailsDialog"
      :session="selectedSession"
    />
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
import DataTable from '@/components/common/DataTable.vue'
import SessionDetailsDialog from '@/components/accounting/SessionDetailsDialog.vue'
import { formatBytes, formatNumber, formatDateTime, formatDuration } from '@/utils/formatters'
import type { AccountingSession, SessionFilters } from '@/types/accounting'

// Composables
const router = useRouter()
const { t } = useI18n()
const accountingStore = useAccountingStore()
const notification = useNotification()

// Reactive data
const loading = ref(false)
const exportLoading = ref(false)
const detailsDialog = ref(false)
const selectedSession = ref<AccountingSession | null>(null)
const searchQuery = ref('')

// Pagination and sorting
const currentPage = ref(1)
const itemsPerPage = ref(20)
const sortBy = ref('acctstarttime')
const sortDesc = ref(true)

// Filters
const filters = reactive<SessionFilters>({
  time_range: null,
  start_date: null,
  end_date: null,
  username: null,
  nasipaddress: null,
  framedipaddress: null,
  servicetype: null,
  active_only: false
})

// Computed properties
const sessions = computed(() => accountingStore.sessions)
const totalItems = computed(() => accountingStore.sessionsPagination.total)
const sessionStats = computed(() => accountingStore.sessionStatistics)

// Table headers
const headers = computed(() => [
  { title: t('accounting.username'), key: 'username', sortable: true },
  { title: t('accounting.status'), key: 'is_active', sortable: true },
  { title: t('accounting.nas_ip'), key: 'nasipaddress', sortable: true },
  { title: t('accounting.framed_ip'), key: 'framedipaddress', sortable: true },
  { title: t('accounting.start_time'), key: 'acctstarttime', sortable: true },
  { title: t('accounting.stop_time'), key: 'acctstoptime', sortable: true },
  { title: t('accounting.session_time'), key: 'acctsessiontime', sortable: true },
  { title: t('accounting.input_traffic'), key: 'acctinputoctets', sortable: true },
  { title: t('accounting.output_traffic'), key: 'acctoutputoctets', sortable: true },
  { title: t('accounting.total_traffic'), key: 'total_bytes', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false, width: 120 }
])

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

const serviceTypeOptions = computed(() => [
  { title: 'Framed-User', value: 'Framed-User' },
  { title: 'Login-User', value: 'Login-User' },
  { title: 'Callback-Login-User', value: 'Callback-Login-User' },
  { title: 'Callback-Framed-User', value: 'Callback-Framed-User' },
  { title: 'Outbound-User', value: 'Outbound-User' },
  { title: 'Administrative-User', value: 'Administrative-User' }
])

// Methods
const navigateTo = (path: string) => {
  router.push(path)
}

const loadSessions = async () => {
  try {
    loading.value = true
    await accountingStore.fetchSessions({
      page: currentPage.value,
      page_size: itemsPerPage.value,
      sort_field: sortBy.value,
      sort_order: sortDesc.value ? 'desc' : 'asc',
      filters: filters
    })
  } catch (error) {
    notification.error(t('accounting.errors.load_sessions_failed'))
    console.error('Failed to load sessions:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  loadSessions()
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = null
  })
  filters.active_only = false
  applyFilters()
}

const updatePage = (page: number) => {
  currentPage.value = page
  loadSessions()
}

const updateItemsPerPage = (perPage: number) => {
  itemsPerPage.value = perPage
  currentPage.value = 1
  loadSessions()
}

const updateSortBy = (field: string) => {
  sortBy.value = field
  loadSessions()
}

const updateSortDesc = (desc: boolean) => {
  sortDesc.value = desc
  loadSessions()
}

const updateSearch = (query: string) => {
  searchQuery.value = query
  // Implement search functionality if needed
}

const viewSession = (session: AccountingSession) => {
  router.push(`/accounting/sessions/${session.radacctid}`)
}

const showSessionDetails = (session: AccountingSession) => {
  selectedSession.value = session
  detailsDialog.value = true
}

const exportSessions = async () => {
  try {
    exportLoading.value = true
    await accountingStore.exportSessions({
      filters: filters,
      format: 'csv'
    })
    notification.success(t('accounting.export_success'))
  } catch (error) {
    notification.error(t('accounting.export_failed'))
    console.error('Failed to export sessions:', error)
  } finally {
    exportLoading.value = false
  }
}

// Watchers
watch([currentPage, itemsPerPage, sortBy, sortDesc], () => {
  loadSessions()
})

// Lifecycle
onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.sessions-page {
  padding: 24px;
}

.cursor-pointer {
  cursor: pointer;
}

.text-grey {
  color: #666;
}
</style>