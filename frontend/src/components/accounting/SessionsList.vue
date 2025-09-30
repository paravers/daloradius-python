<!--
会话列表组件 (Sessions List Component)

可复用的会话列表组件，支持多种显示模式和交互功能
-->
<template>
  <div class="sessions-list">
    <!-- Loading State -->
    <v-skeleton-loader
      v-if="loading"
      type="table-tbody"
      :loading="loading"
    />

    <!-- Empty State -->
    <v-card v-else-if="!sessions || sessions.length === 0" class="text-center pa-8">
      <v-icon size="64" color="grey-lighten-1">mdi-history</v-icon>
      <h3 class="text-h6 mt-4 mb-2">{{ $t('accounting.no_sessions') }}</h3>
      <p class="text-grey">{{ $t('accounting.no_sessions_description') }}</p>
    </v-card>

    <!-- Sessions List -->
    <div v-else class="sessions-container">
      <!-- Compact Mode -->
      <template v-if="compact">
        <v-card 
          v-for="session in sessions" 
          :key="session.radacctid"
          class="session-card mb-3"
          elevation="1"
          hover
          @click="viewSession(session)"
        >
          <v-card-text class="pa-3">
            <div class="d-flex align-center">
              <!-- User Avatar and Info -->
              <div class="d-flex align-center flex-grow-1">
                <v-avatar size="32" class="mr-3">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ session.username }}</div>
                  <div class="text-caption text-grey">
                    {{ session.nasipaddress }}
                    <v-chip
                      :color="session.is_active ? 'success' : 'default'"
                      size="x-small"
                      class="ml-2"
                    >
                      {{ session.is_active ? $t('accounting.active') : $t('accounting.completed') }}
                    </v-chip>
                  </div>
                </div>
              </div>

              <!-- Session Stats -->
              <div class="text-right">
                <div class="text-caption text-grey">{{ $t('accounting.duration') }}</div>
                <div class="font-weight-medium">
                  {{ formatDuration(session.acctsessiontime) }}
                </div>
              </div>

              <!-- Traffic Stats -->
              <div class="text-right ml-4">
                <div class="text-caption text-grey">{{ $t('accounting.traffic') }}</div>
                <div class="font-weight-medium">
                  {{ formatBytes(session.total_bytes || 0) }}
                </div>
              </div>

              <!-- Actions -->
              <div v-if="showActions" class="ml-4">
                <v-btn
                  icon
                  size="small"
                  @click.stop="viewSession(session)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </template>

      <!-- Table Mode -->
      <template v-else>
        <v-data-table
          :headers="tableHeaders"
          :items="sessions"
          :loading="loading"
          class="elevation-1"
          item-value="radacctid"
          hover
        >
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

          <!-- Traffic Columns -->
          <template #item.acctinputoctets="{ item }">
            <span class="text-success">
              {{ formatBytes(item.acctinputoctets || 0) }}
            </span>
          </template>

          <template #item.acctoutputoctets="{ item }">
            <span class="text-info">
              {{ formatBytes(item.acctoutputoctets || 0) }}
            </span>
          </template>

          <template #item.total_bytes="{ item }">
            <span class="text-primary font-weight-bold">
              {{ formatBytes(item.total_bytes || 0) }}
            </span>
          </template>

          <!-- Time Columns -->
          <template #item.acctstarttime="{ item }">
            <span v-if="item.acctstarttime">
              {{ formatDateTime(item.acctstarttime) }}
            </span>
            <span v-else class="text-grey">-</span>
          </template>

          <template #item.acctstoptime="{ item }">
            <span v-if="item.acctstoptime">
              {{ formatDateTime(item.acctstoptime) }}
            </span>
            <span v-else class="text-grey">{{ $t('accounting.ongoing') }}</span>
          </template>

          <!-- Actions Column -->
          <template v-if="showActions" #item.actions="{ item }">
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
import { formatBytes, formatDateTime, formatDuration } from '@/utils/formatters'
import type { AccountingSession } from '@/types/accounting'

// Props
interface Props {
  sessions: AccountingSession[]
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
  (e: 'view-session', session: AccountingSession): void
  (e: 'view-user', username: string): void
  (e: 'view-details', session: AccountingSession): void
}

const emit = defineEmits<Emits>()

// Composables
const { t } = useI18n()

// Computed properties
const tableHeaders = computed(() => [
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
  ...(props.showActions ? [{ title: t('common.actions'), key: 'actions', sortable: false, width: 120 }] : [])
])

// Methods
const viewSession = (session: AccountingSession) => {
  emit('view-session', session)
}
</script>

<style scoped>
.sessions-list {
  width: 100%;
}

.sessions-container {
  width: 100%;
}

.session-card {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.session-card:hover {
  transform: translateY(-2px);
}

.cursor-pointer {
  cursor: pointer;
}

.text-grey {
  color: #666;
}
</style>