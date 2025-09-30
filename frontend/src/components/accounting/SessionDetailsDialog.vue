<!--
会话详情对话框组件 (Session Details Dialog Component)

显示会话的详细信息，包括所有会计统计数据
-->
<template>
  <v-dialog
    v-model="localDialog"
    max-width="800px"
    persistent
    scrollable
  >
    <v-card v-if="session">
      <!-- Header -->
      <v-card-title class="bg-primary">
        <div class="d-flex align-center">
          <v-icon left color="white">mdi-information</v-icon>
          <span class="text-white">{{ $t('accounting.session_details') }}</span>
          <v-spacer />
          <v-chip
            :color="session.is_active ? 'success' : 'default'"
            size="small"
            variant="elevated"
          >
            {{ session.is_active ? $t('accounting.active') : $t('accounting.completed') }}
          </v-chip>
        </div>
      </v-card-title>

      <!-- Content -->
      <v-card-text class="pa-0">
        <v-tabs v-model="activeTab">
          <v-tab value="general">
            <v-icon left>mdi-information-outline</v-icon>
            {{ $t('accounting.general_info') }}
          </v-tab>
          <v-tab value="traffic">
            <v-icon left>mdi-chart-line</v-icon>
            {{ $t('accounting.traffic_stats') }}
          </v-tab>
          <v-tab value="technical">
            <v-icon left>mdi-cog</v-icon>
            {{ $t('accounting.technical_details') }}
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="pa-6">
          <!-- General Information Tab -->
          <v-window-item value="general">
            <v-row>
              <!-- Basic Session Info -->
              <v-col cols="12" md="6">
                <h4 class="text-h6 mb-4">{{ $t('accounting.session_info') }}</h4>
                <v-list dense>
                  <v-list-item>
                    <v-list-item-title>{{ $t('accounting.session_id') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.radacctid }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ $t('accounting.username') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip color="primary" size="small">{{ session.username }}</v-chip>
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.realm">
                    <v-list-item-title>{{ $t('accounting.realm') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.realm }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.groupname">
                    <v-list-item-title>{{ $t('accounting.group') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.groupname }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>{{ $t('accounting.session_status') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="session.is_active ? 'success' : 'default'"
                        size="small"
                      >
                        {{ session.is_active ? $t('accounting.active') : $t('accounting.completed') }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>

              <!-- Network Info -->
              <v-col cols="12" md="6">
                <h4 class="text-h6 mb-4">{{ $t('accounting.network_info') }}</h4>
                <v-list dense>
                  <v-list-item>
                    <v-list-item-title>{{ $t('accounting.nas_ip') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip color="info" size="small">{{ session.nasipaddress }}</v-chip>
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.framedipaddress">
                    <v-list-item-title>{{ $t('accounting.framed_ip') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.framedipaddress }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.callingstationid">
                    <v-list-item-title>{{ $t('accounting.calling_station') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.callingstationid }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.calledstationid">
                    <v-list-item-title>{{ $t('accounting.called_station') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.calledstationid }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.servicetype">
                    <v-list-item-title>{{ $t('accounting.service_type') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.servicetype }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>

              <!-- Time Information -->
              <v-col cols="12">
                <h4 class="text-h6 mb-4">{{ $t('accounting.time_info') }}</h4>
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="outlined">
                      <v-card-text class="text-center">
                        <v-icon color="success" size="32">mdi-play</v-icon>
                        <h4 class="text-h6 mt-2">{{ $t('accounting.start_time') }}</h4>
                        <p class="text-caption mb-0">
                          {{ session.acctstarttime ? formatDateTime(session.acctstarttime) : '-' }}
                        </p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="outlined">
                      <v-card-text class="text-center">
                        <v-icon :color="session.is_active ? 'warning' : 'error'" size="32">
                          {{ session.is_active ? 'mdi-clock' : 'mdi-stop' }}
                        </v-icon>
                        <h4 class="text-h6 mt-2">{{ $t('accounting.stop_time') }}</h4>
                        <p class="text-caption mb-0">
                          {{ session.acctstoptime ? formatDateTime(session.acctstoptime) : $t('accounting.ongoing') }}
                        </p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="outlined">
                      <v-card-text class="text-center">
                        <v-icon color="primary" size="32">mdi-timer</v-icon>
                        <h4 class="text-h6 mt-2">{{ $t('accounting.duration') }}</h4>
                        <p class="text-caption mb-0">
                          {{ session.acctsessiontime ? formatDuration(session.acctsessiontime) : '-' }}
                        </p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="outlined">
                      <v-card-text class="text-center">
                        <v-icon color="info" size="32">mdi-speedometer</v-icon>
                        <h4 class="text-h6 mt-2">{{ $t('accounting.avg_speed') }}</h4>
                        <p class="text-caption mb-0">
                          {{ calculateAverageSpeed() }}
                        </p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Traffic Statistics Tab -->
          <v-window-item value="traffic">
            <v-row>
              <!-- Traffic Overview -->
              <v-col cols="12">
                <h4 class="text-h6 mb-4">{{ $t('accounting.traffic_overview') }}</h4>
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-card color="success" variant="tonal">
                      <v-card-text class="text-center">
                        <v-icon color="success" size="48">mdi-download</v-icon>
                        <h3 class="text-h5 mt-2">{{ formatBytes(session.acctinputoctets || 0) }}</h3>
                        <p class="text-caption">{{ $t('accounting.input_traffic') }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card color="info" variant="tonal">
                      <v-card-text class="text-center">
                        <v-icon color="info" size="48">mdi-upload</v-icon>
                        <h3 class="text-h5 mt-2">{{ formatBytes(session.acctoutputoctets || 0) }}</h3>
                        <p class="text-caption">{{ $t('accounting.output_traffic') }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card color="primary" variant="tonal">
                      <v-card-text class="text-center">
                        <v-icon color="primary" size="48">mdi-swap-vertical</v-icon>
                        <h3 class="text-h5 mt-2">{{ formatBytes(session.total_bytes || 0) }}</h3>
                        <p class="text-caption">{{ $t('accounting.total_traffic') }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card color="warning" variant="tonal">
                      <v-card-text class="text-center">
                        <v-icon color="warning" size="48">mdi-package-variant</v-icon>
                        <h3 class="text-h5 mt-2">{{ formatNumber(session.total_packets || 0) }}</h3>
                        <p class="text-caption">{{ $t('accounting.total_packets') }}</p>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-col>

              <!-- Traffic Chart -->
              <v-col cols="12" v-if="session.acctinputoctets || session.acctoutputoctets">
                <h4 class="text-h6 mb-4">{{ $t('accounting.traffic_distribution') }}</h4>
                <v-card variant="outlined">
                  <v-card-text>
                    <!-- Simple pie chart representation -->
                    <div class="d-flex align-center justify-center">
                      <div class="traffic-chart">
                        <v-progress-circular
                          :model-value="getInputPercentage()"
                          color="success"
                          size="100"
                          width="15"
                        >
                          <span class="text-h6">{{ Math.round(getInputPercentage()) }}%</span>
                        </v-progress-circular>
                        <p class="text-center mt-2">{{ $t('accounting.input_ratio') }}</p>
                      </div>
                      <v-divider vertical class="mx-8" />
                      <div class="traffic-chart">
                        <v-progress-circular
                          :model-value="getOutputPercentage()"
                          color="info"
                          size="100"
                          width="15"
                        >
                          <span class="text-h6">{{ Math.round(getOutputPercentage()) }}%</span>
                        </v-progress-circular>
                        <p class="text-center mt-2">{{ $t('accounting.output_ratio') }}</p>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Technical Details Tab -->
          <v-window-item value="technical">
            <v-row>
              <v-col cols="12" md="6">
                <h4 class="text-h6 mb-4">{{ $t('accounting.session_identifiers') }}</h4>
                <v-list dense>
                  <v-list-item>
                    <v-list-item-title>{{ $t('accounting.acct_session_id') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.acctsessionid }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.acctuniqueid">
                    <v-list-item-title>{{ $t('accounting.acct_unique_id') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.acctuniqueid }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              
              <v-col cols="12" md="6">
                <h4 class="text-h6 mb-4">{{ $t('accounting.network_details') }}</h4>
                <v-list dense>
                  <v-list-item v-if="session.nasportid">
                    <v-list-item-title>{{ $t('accounting.nas_port_id') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.nasportid }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="session.nasporttype">
                    <v-list-item-title>{{ $t('accounting.nas_port_type') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ session.nasporttype }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>

              <v-col cols="12" v-if="session.acctterminatecause">
                <h4 class="text-h6 mb-4">{{ $t('accounting.termination_info') }}</h4>
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="d-flex align-center">
                      <v-icon left color="error">mdi-stop-circle</v-icon>
                      <div>
                        <div class="font-weight-medium">{{ $t('accounting.terminate_cause') }}</div>
                        <div class="text-caption">{{ session.acctterminatecause }}</div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>
        </v-window>
      </v-card-text>

      <!-- Actions -->
      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="exportSession"
          :loading="exporting"
        >
          <v-icon left>mdi-download</v-icon>
          {{ $t('common.export') }}
        </v-btn>
        <v-btn
          color="primary"
          @click="closeDialog"
        >
          {{ $t('common.close') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatBytes, formatDateTime, formatDuration, formatNumber } from '@/utils/formatters'
import type { AccountingSession } from '@/types/accounting'

// Props
interface Props {
  modelValue: boolean
  session: AccountingSession | null
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const emit = defineEmits<Emits>()

// Composables
const { t } = useI18n()

// Reactive data
const activeTab = ref('general')
const exporting = ref(false)

// Computed properties
const localDialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Methods
const closeDialog = () => {
  localDialog.value = false
}

const calculateAverageSpeed = () => {
  if (!props.session?.acctsessiontime || !props.session?.total_bytes) {
    return '-'
  }
  
  const bytesPerSecond = props.session.total_bytes / props.session.acctsessiontime
  return formatBytes(bytesPerSecond) + '/s'
}

const getInputPercentage = () => {
  if (!props.session?.total_bytes) return 0
  return ((props.session.acctinputoctets || 0) / props.session.total_bytes) * 100
}

const getOutputPercentage = () => {
  if (!props.session?.total_bytes) return 0
  return ((props.session.acctoutputoctets || 0) / props.session.total_bytes) * 100
}

const exportSession = async () => {
  if (!props.session) return
  
  try {
    exporting.value = true
    // Implementation for exporting session data
    // This would typically call an API endpoint or use a utility function
    console.log('Exporting session:', props.session.radacctid)
  } catch (error) {
    console.error('Failed to export session:', error)
  } finally {
    exporting.value = false
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    activeTab.value = 'general'
  }
})
</script>

<style scoped>
.traffic-chart {
  text-align: center;
}

.v-progress-circular {
  margin: 16px;
}
</style>