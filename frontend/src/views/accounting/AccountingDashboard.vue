<!--
会计统计主页面 (Accounting Main Page)

提供会计统计模块的综合概览和导航入口
-->
<template>
  <div class="accounting-page">
    <!-- Page Header -->
    <PageHeader
      :title="$t('accounting.title')"
      :subtitle="$t('accounting.subtitle')"
      icon="mdi-chart-line"
    />

    <!-- Overview Statistics -->
    <div class="stats-section mb-6">
      <v-row>
        <!-- Session Statistics Card -->
        <v-col cols="12" md="6" lg="3">
          <v-card class="h-100" elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-avatar color="primary" size="48">
                  <v-icon color="white">mdi-account-multiple</v-icon>
                </v-avatar>
                <div class="ml-4">
                  <h3 class="text-h6 text-primary">
                    {{ formatNumber(overview?.session_stats?.active_sessions || 0) }}
                  </h3>
                  <p class="text-caption mb-0">{{ $t('accounting.active_sessions') }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Total Sessions Card -->
        <v-col cols="12" md="6" lg="3">
          <v-card class="h-100" elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-avatar color="success" size="48">
                  <v-icon color="white">mdi-history</v-icon>
                </v-avatar>
                <div class="ml-4">
                  <h3 class="text-h6 text-success">
                    {{ formatNumber(overview?.session_stats?.total_sessions || 0) }}
                  </h3>
                  <p class="text-caption mb-0">{{ $t('accounting.total_sessions') }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Traffic Volume Card -->
        <v-col cols="12" md="6" lg="3">
          <v-card class="h-100" elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-avatar color="info" size="48">
                  <v-icon color="white">mdi-cloud-download</v-icon>
                </v-avatar>
                <div class="ml-4">
                  <h3 class="text-h6 text-info">
                    {{ formatBytes(overview?.traffic_stats?.total_bytes || 0) }}
                  </h3>
                  <p class="text-caption mb-0">{{ $t('accounting.total_traffic') }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Unique Users Card -->
        <v-col cols="12" md="6" lg="3">
          <v-card class="h-100" elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-avatar color="warning" size="48">
                  <v-icon color="white">mdi-account-group</v-icon>
                </v-avatar>
                <div class="ml-4">
                  <h3 class="text-h6 text-warning">
                    {{ formatNumber(overview?.session_stats?.unique_users || 0) }}
                  </h3>
                  <p class="text-caption mb-0">{{ $t('accounting.unique_users') }}</p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Quick Actions -->
    <div class="actions-section mb-6">
      <v-card elevation="2">
        <v-card-title>
          <v-icon left>mdi-lightning-bolt</v-icon>
          {{ $t('accounting.quick_actions') }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6" md="4" lg="3">
              <v-btn
                color="primary"
                variant="outlined"
                block
                size="large"
                @click="navigateTo('/accounting/sessions')"
              >
                <v-icon left>mdi-format-list-bulleted</v-icon>
                {{ $t('accounting.view_sessions') }}
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="3">
              <v-btn
                color="success"
                variant="outlined"
                block
                size="large"
                @click="navigateTo('/accounting/active')"
              >
                <v-icon left>mdi-play-circle</v-icon>
                {{ $t('accounting.active_sessions') }}
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="3">
              <v-btn
                color="info"
                variant="outlined"
                block
                size="large"
                @click="navigateTo('/accounting/reports')"
              >
                <v-icon left>mdi-chart-bar</v-icon>
                {{ $t('accounting.reports') }}
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4" lg="3">
              <v-btn
                color="warning"
                variant="outlined"
                block
                size="large"
                @click="navigateTo('/accounting/custom-query')"
              >
                <v-icon left>mdi-database-search</v-icon>
                {{ $t('accounting.custom_query') }}
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity-section">
      <v-row>
        <!-- Recent Sessions -->
        <v-col cols="12" lg="8">
          <v-card elevation="2" class="h-100">
            <v-card-title>
              <v-icon left>mdi-clock-outline</v-icon>
              {{ $t('accounting.recent_sessions') }}
            </v-card-title>
            <v-card-text>
              <SessionsList
                :sessions="recentSessions"
                :loading="sessionsLoading"
                compact
                :show-actions="false"
                @view-session="viewSession"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                variant="text"
                @click="navigateTo('/accounting/sessions')"
              >
                {{ $t('common.view_all') }}
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <!-- Top Users -->
        <v-col cols="12" lg="4">
          <v-card elevation="2" class="h-100">
            <v-card-title>
              <v-icon left>mdi-trophy</v-icon>
              {{ $t('accounting.top_users') }}
            </v-card-title>
            <v-card-text>
              <TopUsersList
                :users="topUsers"
                :loading="topUsersLoading"
                compact
                @view-user="viewUser"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                variant="text"
                @click="navigateTo('/accounting/reports/top-users')"
              >
                {{ $t('common.view_all') }}
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="overviewLoading"
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
    </v-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccountingStore } from '@/stores/accounting'
import PageHeader from '@/components/common/PageHeader.vue'
import SessionsList from '@/components/accounting/SessionsList.vue'
import TopUsersList from '@/components/accounting/TopUsersList.vue'
import { formatBytes, formatNumber } from '@/utils/formatters'

// Composables
const router = useRouter()
const { t } = useI18n()
const accountingStore = useAccountingStore()

// Reactive data
const overviewLoading = ref(false)
const sessionsLoading = ref(false)
const topUsersLoading = ref(false)

// Computed properties
const overview = computed(() => accountingStore.overview)
const recentSessions = computed(() => accountingStore.recentSessions)
const topUsers = computed(() => accountingStore.topUsers)

// Methods
const navigateTo = (path: string) => {
  router.push(path)
}

const viewSession = (sessionId: number) => {
  router.push(`/accounting/sessions/${sessionId}`)
}

const viewUser = (username: string) => {
  router.push(`/accounting/sessions/user/${username}`)
}

const loadOverview = async () => {
  try {
    overviewLoading.value = true
    await accountingStore.fetchOverview()
  } catch (error) {
    console.error('Failed to load accounting overview:', error)
  } finally {
    overviewLoading.value = false
  }
}

const loadRecentSessions = async () => {
  try {
    sessionsLoading.value = true
    await accountingStore.fetchRecentSessions({ page: 1, page_size: 5 })
  } catch (error) {
    console.error('Failed to load recent sessions:', error)
  } finally {
    sessionsLoading.value = false
  }
}

const loadTopUsers = async () => {
  try {
    topUsersLoading.value = true
    await accountingStore.fetchTopUsers({ limit: 5 })
  } catch (error) {
    console.error('Failed to load top users:', error)
  } finally {
    topUsersLoading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadOverview(),
    loadRecentSessions(),
    loadTopUsers()
  ])
})
</script>

<style scoped>
.accounting-page {
  padding: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.actions-section {
  margin-bottom: 24px;
}

.recent-activity-section {
  margin-bottom: 24px;
}

/* Card hover effects */
.v-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

/* Avatar animations */
.v-avatar {
  transition: transform 0.3s ease-in-out;
}

.v-card:hover .v-avatar {
  transform: scale(1.1);
}

/* Button animations */
.v-btn {
  transition: all 0.2s ease-in-out;
}

.v-btn:hover {
  transform: translateY(-1px);
}
</style>