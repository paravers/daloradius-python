<!--
  GIS Map Controls Component
  
  Control panel for map operations including search, filters, layer management,
  and coordinate input for GIS functionality.
-->

<template>
  <div class="gis-map-controls">
    <!-- Search Panel -->
    <a-card size="small" class="control-panel" v-if="showSearch">
      <template #title>
        <SearchOutlined /> 搜索热点
      </template>
      
      <a-space direction="vertical" style="width: 100%">
        <!-- Text Search -->
        <a-input-search
          v-model:value="searchQuery"
          placeholder="按名称或描述搜索..."
          @search="handleTextSearch"
          :loading="searchLoading"
          allow-clear
        />

        <!-- Location Search -->
        <a-collapse>
          <a-collapse-panel key="location" header="位置搜索">
            <a-space direction="vertical" style="width: 100%">
              <a-row :gutter="8">
                <a-col :span="12">
                  <a-input-number
                    v-model:value="searchLocation.latitude"
                    placeholder="纬度"
                    :min="-90"
                    :max="90"
                    :precision="6"
                    style="width: 100%"
                  />
                </a-col>
                <a-col :span="12">
                  <a-input-number
                    v-model:value="searchLocation.longitude"
                    placeholder="经度"
                    :min="-180"
                    :max="180"
                    :precision="6"
                    style="width: 100%"
                  />
                </a-col>
              </a-row>
              
              <a-input-number
                v-model:value="searchRadius"
                placeholder="搜索半径 (km)"
                :min="0.1"
                :max="1000"
                style="width: 100%"
              />
              
              <a-button
                type="primary"
                @click="handleLocationSearch"
                :loading="searchLoading"
                :disabled="!isValidSearchLocation"
                block
              >
                <EnvironmentOutlined /> 位置搜索
              </a-button>
            </a-space>
          </a-collapse-panel>
        </a-collapse>
      </a-space>
    </a-card>

    <!-- Filter Panel -->
    <a-card size="small" class="control-panel" v-if="showFilters">
      <template #title>
        <FilterOutlined /> 过滤选项
      </template>
      
      <a-space direction="vertical" style="width: 100%">
        <!-- Status Filter -->
        <div>
          <div class="filter-label">状态过滤</div>
          <a-checkbox-group v-model:value="statusFilter" @change="handleFilterChange">
            <a-checkbox value="active">活跃</a-checkbox>
            <a-checkbox value="inactive">非活跃</a-checkbox>
            <a-checkbox value="pending">待处理</a-checkbox>
            <a-checkbox value="maintenance">维护中</a-checkbox>
          </a-checkbox-group>
        </div>

        <!-- Date Range Filter -->
        <div>
          <div class="filter-label">创建时间</div>
          <a-range-picker
            v-model:value="dateRange"
            @change="handleFilterChange"
            style="width: 100%"
          />
        </div>

        <!-- Reset Filters -->
        <a-button @click="resetFilters" size="small" block>
          重置过滤
        </a-button>
      </a-space>
    </a-card>

    <!-- Coordinate Tools -->
    <a-card size="small" class="control-panel" v-if="showCoordinateTools">
      <template #title>
        <AimOutlined /> 坐标工具
      </template>
      
      <a-space direction="vertical" style="width: 100%">
        <!-- Add Marker -->
        <div v-if="editable">
          <div class="filter-label">添加标记</div>
          <a-row :gutter="8">
            <a-col :span="12">
              <a-input-number
                v-model:value="newMarker.latitude"
                placeholder="纬度"
                :min="-90"
                :max="90"
                :precision="6"
                style="width: 100%"
              />
            </a-col>
            <a-col :span="12">
              <a-input-number
                v-model:value="newMarker.longitude"
                placeholder="经度"
                :min="-180"
                :max="180"
                :precision="6"
                style="width: 100%"
              />
            </a-col>
          </a-row>
          
          <a-button
            type="primary"
            @click="handleAddMarker"
            :disabled="!isValidNewMarker"
            size="small"
            block
            style="margin-top: 8px"
          >
            <PlusOutlined /> 添加标记
          </a-button>
        </div>

        <!-- Coordinate Validation -->
        <div>
          <div class="filter-label">坐标验证</div>
          <a-row :gutter="8">
            <a-col :span="12">
              <a-input-number
                v-model:value="validateCoords.latitude"
                placeholder="纬度"
                :min="-90"
                :max="90"
                :precision="6"
                style="width: 100%"
              />
            </a-col>
            <a-col :span="12">
              <a-input-number
                v-model:value="validateCoords.longitude"
                placeholder="经度"
                :min="-180"
                :max="180"
                :precision="6"
                style="width: 100%"
              />
            </a-col>
          </a-row>
          
          <a-button
            @click="handleValidateCoordinates"
            :disabled="!isValidateCoords"
            size="small"
            block
            style="margin-top: 8px"
          >
            <CheckOutlined /> 验证坐标
          </a-button>
          
          <div v-if="validationResult" class="validation-result">
            <a-alert
              :type="validationResult.valid ? 'success' : 'error'"
              :message="validationResult.valid ? '坐标有效' : '坐标无效'"
              :description="validationResult.errors?.join(', ')"
              size="small"
              show-icon
            />
          </div>
        </div>
      </a-space>
    </a-card>

    <!-- Map Statistics -->
    <a-card size="small" class="control-panel" v-if="showStatistics && statistics">
      <template #title>
        <BarChartOutlined /> 地图统计
      </template>
      
      <a-space direction="vertical" style="width: 100%">
        <a-statistic
          title="总热点数"
          :value="statistics.total_hotspots"
          suffix="个"
          :value-style="{ fontSize: '14px' }"
        />
        
        <a-statistic
          title="活跃热点"
          :value="statistics.active_hotspots"
          suffix="个"
          :value-style="{ fontSize: '14px', color: '#52c41a' }"
        />
        
        <a-statistic
          title="活跃率"
          :value="statistics.activity_rate"
          suffix="%"
          :precision="1"
          :value-style="{ fontSize: '14px' }"
        />
      </a-space>
    </a-card>

    <!-- Quick Actions -->
    <a-card size="small" class="control-panel" v-if="showQuickActions">
      <template #title>
        <ThunderboltOutlined /> 快速操作
      </template>
      
      <a-space direction="vertical" style="width: 100%">
        <a-button @click="handleRefresh" :loading="refreshLoading" size="small" block>
          <ReloadOutlined /> 刷新地图
        </a-button>
        
        <a-button @click="handleFitBounds" size="small" block>
          <CompressOutlined /> 适应边界
        </a-button>
        
        <a-button @click="handleExportData" size="small" block v-if="showExport">
          <DownloadOutlined /> 导出数据
        </a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import type { Dayjs } from 'dayjs'
import {
  SearchOutlined,
  FilterOutlined,
  AimOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  EnvironmentOutlined,
  PlusOutlined,
  CheckOutlined,
  ReloadOutlined,
  CompressOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

import type { GeoCoordinates, CoordinateValidationResponse } from '@/services/gisService'

// Props
interface Props {
  showSearch?: boolean
  showFilters?: boolean
  showCoordinateTools?: boolean
  showStatistics?: boolean
  showQuickActions?: boolean
  showExport?: boolean
  editable?: boolean
  statistics?: {
    total_hotspots: number
    active_hotspots: number
    inactive_hotspots: number
    activity_rate: number
  }
}

const props = withDefaults(defineProps<Props>(), {
  showSearch: true,
  showFilters: true,
  showCoordinateTools: true,
  showStatistics: true,
  showQuickActions: true,
  showExport: false,
  editable: false
})

// Emits
interface Emits {
  (e: 'text-search', query: string): void
  (e: 'location-search', location: GeoCoordinates, radius: number): void
  (e: 'filter-change', filters: any): void
  (e: 'add-marker', coordinates: GeoCoordinates): void
  (e: 'refresh'): void
  (e: 'fit-bounds'): void
  (e: 'export-data'): void
}

const emit = defineEmits<Emits>()

// Reactive data
const searchQuery = ref('')
const searchLoading = ref(false)
const searchLocation = ref<GeoCoordinates>({ latitude: 0, longitude: 0 })
const searchRadius = ref(10)

const statusFilter = ref<string[]>(['active', 'inactive', 'pending', 'maintenance'])
const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const newMarker = ref<GeoCoordinates>({ latitude: 0, longitude: 0 })
const validateCoords = ref<GeoCoordinates>({ latitude: 0, longitude: 0 })
const validationResult = ref<CoordinateValidationResponse | null>(null)

const refreshLoading = ref(false)

// Computed
const isValidSearchLocation = computed(() => {
  return (
    searchLocation.value.latitude >= -90 &&
    searchLocation.value.latitude <= 90 &&
    searchLocation.value.longitude >= -180 &&
    searchLocation.value.longitude <= 180 &&
    searchRadius.value > 0
  )
})

const isValidNewMarker = computed(() => {
  return (
    newMarker.value.latitude >= -90 &&
    newMarker.value.latitude <= 90 &&
    newMarker.value.longitude >= -180 &&
    newMarker.value.longitude <= 180
  )
})

const isValidateCoords = computed(() => {
  return (
    validateCoords.value.latitude !== 0 ||
    validateCoords.value.longitude !== 0
  )
})

// Methods
const handleTextSearch = async () => {
  if (!searchQuery.value.trim()) {
    message.warning('请输入搜索内容')
    return
  }

  searchLoading.value = true
  try {
    emit('text-search', searchQuery.value.trim())
  } finally {
    searchLoading.value = false
  }
}

const handleLocationSearch = async () => {
  if (!isValidSearchLocation.value) {
    message.error('请输入有效的搜索坐标和半径')
    return
  }

  searchLoading.value = true
  try {
    emit('location-search', searchLocation.value, searchRadius.value)
  } finally {
    searchLoading.value = false
  }
}

const handleFilterChange = () => {
  const filters = {
    status: statusFilter.value,
    dateRange: dateRange.value
  }
  emit('filter-change', filters)
}

const resetFilters = () => {
  statusFilter.value = ['active', 'inactive', 'pending', 'maintenance']
  dateRange.value = null
  handleFilterChange()
}

const handleAddMarker = () => {
  if (!isValidNewMarker.value) {
    message.error('请输入有效的坐标')
    return
  }

  emit('add-marker', { ...newMarker.value })
  
  // Reset form
  newMarker.value = { latitude: 0, longitude: 0 }
  message.success('标记已添加')
}

const handleValidateCoordinates = async () => {
  if (!isValidateCoords.value) {
    message.warning('请输入要验证的坐标')
    return
  }

  try {
    // Import service dynamically to avoid circular dependencies
    const { gisService } = await import('@/services/gisService')
    
    const result = await gisService.validateCoordinates(validateCoords.value)
    validationResult.value = result
    
    if (result.valid) {
      message.success('坐标验证通过')
    } else {
      message.error('坐标验证失败')
    }
  } catch (error) {
    message.error('坐标验证失败')
    console.error('Coordinate validation error:', error)
  }
}

const handleRefresh = async () => {
  refreshLoading.value = true
  try {
    emit('refresh')
    message.success('地图已刷新')
  } finally {
    setTimeout(() => {
      refreshLoading.value = false
    }, 1000)
  }
}

const handleFitBounds = () => {
  emit('fit-bounds')
  message.info('已适应地图边界')
}

const handleExportData = () => {
  emit('export-data')
}

// Watchers
watch(statusFilter, handleFilterChange, { deep: true })
</script>

<style scoped>
.gis-map-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 300px;
  max-height: 80vh;
  overflow-y: auto;
}

.control-panel {
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.control-panel :deep(.ant-card-head) {
  padding: 8px 16px;
  min-height: auto;
}

.control-panel :deep(.ant-card-head-title) {
  font-size: 14px;
  font-weight: 500;
}

.control-panel :deep(.ant-card-body) {
  padding: 12px 16px;
}

.filter-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
  font-weight: 500;
}

.validation-result {
  margin-top: 8px;
}

.validation-result :deep(.ant-alert) {
  font-size: 11px;
}

/* Responsive design */
@media (max-width: 768px) {
  .gis-map-controls {
    width: 100%;
    max-height: none;
  }
  
  .control-panel {
    margin-bottom: 8px;
  }
}

/* Custom scrollbar */
.gis-map-controls::-webkit-scrollbar {
  width: 4px;
}

.gis-map-controls::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 2px;
}

.gis-map-controls::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 2px;
}

.gis-map-controls::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>