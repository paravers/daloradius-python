<!--
顶级用户列表组件 (Top Users List Component)

显示流量消耗排名靠前的用户列表
-->
<template>
  <div class="top-users-list">
    <!-- Loading State -->
    <v-skeleton-loader
      v-if="loading"
      type="list-item-avatar-three-line"
      :loading="loading"
    />

    <!-- Empty State -->
    <v-card v-else-if="!users || users.length === 0" class="text-center pa-8">
      <v-icon size="64" color="grey-lighten-1">mdi-trophy</v-icon>
      <h3 class="text-h6 mt-4 mb-2">{{ $t('accounting.no_top_users') }}</h3>
      <p class="text-grey">{{ $t('accounting.no_top_users_description') }}</p>
    </v-card>

    <!-- Users List -->
    <div v-else class="users-container">
      <!-- Compact Mode -->
      <template v-if="compact">
        <v-list class="pa-0">
          <v-list-item
            v-for="(user, index) in users"
            :key="user.username"
            @click="viewUser(user)"
            class="user-item"
          >
            <template #prepend>
              <v-badge
                :content="user.rank || (index + 1)"
                :color="getRankColor(user.rank || (index + 1))"
                offset-x="2"
                offset-y="2"
              >
                <v-avatar size="40" class="mr-3">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
              </v-badge>
            </template>

            <v-list-item-title class="font-weight-medium">
              {{ user.username }}
            </v-list-item-title>
            
            <v-list-item-subtitle>
              <div class="d-flex align-center text-caption">
                <span class="mr-2">{{ formatBytes(user.total_bytes) }}</span>
                <v-divider vertical class="mx-2" />
                <span class="mr-2">{{ user.total_sessions }} {{ $t('accounting.sessions') }}</span>
                <v-divider vertical class="mx-2" />
                <span>{{ formatDuration(user.total_session_time) }}</span>
              </div>
            </v-list-item-subtitle>

            <template #append>
              <div class="text-right">
                <div class="text-h6 text-primary">
                  {{ formatBytes(user.total_bytes) }}
                </div>
                <div class="text-caption text-grey">
                  {{ $t('accounting.total_traffic') }}
                </div>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </template>

      <!-- Table Mode -->
      <template v-else>
        <v-data-table
          :headers="tableHeaders"
          :items="users"
          :loading="loading"
          class="elevation-1"
          item-value="username"
          hover
        >
          <!-- Rank Column -->
          <template #item.rank="{ item, index }">
            <v-badge
              :content="item.rank || (index + 1)"
              :color="getRankColor(item.rank || (index + 1))"
              inline
            >
              <v-icon v-if="(item.rank || (index + 1)) <= 3" :color="getRankColor(item.rank || (index + 1))">
                mdi-trophy
              </v-icon>
              <v-icon v-else color="grey">mdi-numeric-{{ Math.min(item.rank || (index + 1), 9) }}-circle</v-icon>
            </v-badge>
          </template>

          <!-- Username Column -->
          <template #item.username="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" class="mr-2">
                <v-icon>mdi-account</v-icon>
              </v-avatar>
              <v-chip
                color="primary"
                size="small"
                @click="$emit('view-user', item.username)"
                class="cursor-pointer"
              >
                {{ item.username }}
              </v-chip>
            </div>
          </template>

          <!-- Total Traffic Column -->
          <template #item.total_bytes="{ item }">
            <div class="d-flex align-center">
              <v-progress-linear
                :model-value="getTrafficPercentage(item.total_bytes)"
                color="primary"
                height="8"
                rounded
                class="mr-3"
                style="min-width: 60px;"
              />
              <span class="text-primary font-weight-bold">
                {{ formatBytes(item.total_bytes) }}
              </span>
            </div>
          </template>

          <!-- Sessions Column -->
          <template #item.total_sessions="{ item }">
            <v-chip color="info" size="small" variant="outlined">
              {{ formatNumber(item.total_sessions) }}
            </v-chip>
          </template>

          <!-- Session Time Column -->
          <template #item.total_session_time="{ item }">
            <span class="font-mono">
              {{ formatDuration(item.total_session_time) }}
            </span>
          </template>

          <!-- Last Session Column -->
          <template #item.last_session="{ item }">
            <span v-if="item.last_session">
              {{ formatDateTime(item.last_session) }}
            </span>
            <span v-else class="text-grey">-</span>
          </template>

          <!-- Average Session Column -->
          <template #item.average_session_duration="{ item }">
            <span class="text-success">
              {{ calculateAverageSessionDuration(item) }}
            </span>
          </template>

          <!-- Actions Column -->
          <template v-if="showActions" #item.actions="{ item }">
            <v-btn
              icon
              size="small"
              @click="viewUser(item)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              @click="$emit('view-sessions', item.username)"
            >
              <v-icon>mdi-history</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              @click="$emit('view-details', item)"
            >
              <v-icon>mdi-information</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatBytes, formatDateTime, formatDuration, formatNumber } from '@/utils/formatters'
import type { TopUsersReport } from '@/types/accounting'

// Props
interface Props {
  users: TopUsersReport[]
  loading?: boolean
  compact?: boolean
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  compact: false,
  showActions: true
})

// Emits
interface Emits {
  (e: 'view-user', user: TopUsersReport): void
  (e: 'view-sessions', username: string): void
  (e: 'view-details', user: TopUsersReport): void
}

const emit = defineEmits<Emits>()

// Composables
const { t } = useI18n()

// Computed properties
const tableHeaders = computed(() => [
  { title: t('accounting.rank'), key: 'rank', sortable: false, width: 80 },
  { title: t('accounting.username'), key: 'username', sortable: true },
  { title: t('accounting.total_traffic'), key: 'total_bytes', sortable: true },
  { title: t('accounting.sessions'), key: 'total_sessions', sortable: true },
  { title: t('accounting.total_time'), key: 'total_session_time', sortable: true },
  { title: t('accounting.last_session'), key: 'last_session', sortable: true },
  { title: t('accounting.avg_session'), key: 'average_session_duration', sortable: false },
  ...(props.showActions ? [{ title: t('common.actions'), key: 'actions', sortable: false, width: 150 }] : [])
])

const maxTraffic = computed(() => {
  if (!props.users.length) return 0
  return Math.max(...props.users.map(user => user.total_bytes))
})

// Methods
const viewUser = (user: TopUsersReport) => {
  emit('view-user', user)
}

const getRankColor = (rank: number) => {
  switch (rank) {
    case 1: return 'amber'  // Gold
    case 2: return 'grey'   // Silver
    case 3: return 'orange' // Bronze
    default: return 'primary'
  }
}

const getTrafficPercentage = (bytes: number) => {
  if (maxTraffic.value === 0) return 0
  return (bytes / maxTraffic.value) * 100
}

const calculateAverageSessionDuration = (user: TopUsersReport) => {
  if (user.total_sessions === 0) return '-'
  const averageSeconds = user.total_session_time / user.total_sessions
  return formatDuration(Math.round(averageSeconds))
}
</script>

<style scoped>
.top-users-list {
  width: 100%;
}

.users-container {
  width: 100%;
}

.user-item {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.user-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.cursor-pointer {
  cursor: pointer;
}

.text-grey {
  color: #666;
}

.font-mono {
  font-family: 'Roboto Mono', monospace;
}
</style>