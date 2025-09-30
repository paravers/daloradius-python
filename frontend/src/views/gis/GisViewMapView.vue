<!--
  GIS View Map View
  
  Focused map viewing interface for hotspot visualization without editing capabilities.
  Optimized for read-only map display and exploration.
-->

<template>
  <div class="gis-view-map">
    <!-- Header -->
    <div class="view-header">
      <a-page-header
        title="地图查看"
        sub-title="热点地理位置查看和分析"
        @back="handleBack"
      >
        <template #extra>
          <a-space>
            <a-button @click="refreshData" :loading="loading">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
            
            <a-button @click="showFullscreen = true">
              <template #icon><ExpandOutlined /></template>
              全屏
            </a-button>
            
            <a-dropdown>
              <a-button>
                <template #icon><DownloadOutlined /></template>
                导出
                <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu @click="handleExport">
                  <a-menu-item key="json">导出JSON</a-menu-item>
                  <a-menu-item key="csv">导出CSV</a-menu-item>
                  <a-menu-item key="image">导出图片</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </template>
      </a-page-header>
    </div>

    <!-- Map Content -->
    <div class="map-content">
      <a-row :gutter="16">
        <!-- Sidebar -->
        <a-col :span="showSidebar ? 6 : 0" v-show="showSidebar">
          <div class="sidebar">
            <!-- Map Information -->
            <a-card size="small" title="地图信息" class="info-card">
              <a-descriptions size="small" :column="1">
                <a-descriptions-item label="总热点">
                  {{ mapData?.statistics.total_hotspots || 0 }} 个
                </a-descriptions-item>
                <a-descriptions-item label="活跃热点">
                  <span style="color: #52c41a">
                    {{ mapData?.statistics.active_hotspots || 0 }} 个
                  </span>
                </a-descriptions-item>
                <a-descriptions-item label="非活跃热点">
                  <span style="color: #f5222d">
                    {{ mapData?.statistics.inactive_hotspots || 0 }} 个
                  </span>
                </a-descriptions-item>
                <a-descriptions-item label="活跃率">
                  {{ (mapData?.statistics.activity_rate || 0).toFixed(1) }}%
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <!-- Quick Filters -->
            <a-card size="small" title="快速过滤" class="filter-card">
              <a-space direction="vertical" style="width: 100%">
                <a-radio-group
                  v-model:value="statusFilter"
                  @change="handleStatusFilter"
                  size="small"
                >
                  <a-radio-button value="all">全部</a-radio-button>
                  <a-radio-button value="active">活跃</a-radio-button>
                  <a-radio-button value="inactive">非活跃</a-radio-button>
                </a-radio-group>

                <a-input-search
                  v-model:value="searchQuery"
                  placeholder="搜索热点..."
                  @search="handleSearch"
                  size="small"
                />
              </a-space>
            </a-card>

            <!-- Legend -->
            <a-card size="small" title="图例" class="legend-card">
              <div class="legend-items">
                <div class="legend-item">
                  <div class="legend-marker active"></div>
                  <span>活跃热点</span>
                </div>
                <div class="legend-item">
                  <div class="legend-marker inactive"></div>
                  <span>非活跃热点</span>
                </div>
                <div class="legend-item">
                  <div class="legend-marker pending"></div>
                  <span>待处理热点</span>
                </div>
                <div class="legend-item">
                  <div class="legend-marker maintenance"></div>
                  <span>维护中热点</span>
                </div>
              </div>
            </a-card>

            <!-- Current View Info -->
            <a-card size="small" title="当前视图" class="view-info-card" v-if="currentBounds">
              <a-descriptions size="small" :column="1">
                <a-descriptions-item label="北纬">
                  {{ currentBounds.north.toFixed(6) }}°
                </a-descriptions-item>
                <a-descriptions-item label="南纬">
                  {{ currentBounds.south.toFixed(6) }}°
                </a-descriptions-item>
                <a-descriptions-item label="东经">
                  {{ currentBounds.east.toFixed(6) }}°
                </a-descriptions-item>
                <a-descriptions-item label="西经">
                  {{ currentBounds.west.toFixed(6) }}°
                </a-descriptions-item>
                <a-descriptions-item label="可见热点">
                  {{ visibleMarkers.length }} 个
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </div>
        </a-col>

        <!-- Map Area -->
        <a-col :span="showSidebar ? 18 : 24">
          <div class="map-area">
            <!-- Map Controls -->
            <div class="map-controls-bar">
              <a-space>
                <a-button
                  size="small"
                  @click="showSidebar = !showSidebar"
                  :icon="showSidebar ? h(MenuFoldOutlined) : h(MenuUnfoldOutlined)"
                >
                  {{ showSidebar ? '隐藏' : '显示' }}侧栏
                </a-button>

                <a-select
                  v-model:value="mapLayer"
                  size="small"
                  style="width: 120px"
                  @change="handleLayerChange"
                >
                  <a-select-option value="street">街道地图</a-select-option>
                  <a-select-option value="satellite">卫星地图</a-select-option>
                  <a-select-option value="terrain">地形地图</a-select-option>
                </a-select>

                <a-button size="small" @click="handleFitBounds">
                  <template #icon><CompressOutlined /></template>
                  适应边界
                </a-button>

                <a-button size="small" @click="handleResetView">
                  <template #icon><HomeOutlined /></template>
                  重置视图
                </a-button>
              </a-space>
            </div>

            <!-- Map Component -->
            <gis-map-view
              ref="mapRef"
              :markers="visibleMarkers"
              :center="mapCenter"
              :bounds="mapData?.bounds"
              :editable="false"
              :show-filters="false"
              :height="mapHeight"
              :auto-fit="autoFit"
              @marker-click="handleMarkerClick"
              @bounds-change="handleBoundsChange"
              @refresh="refreshData"
            />
          </div>
        </a-col>
      </a-row>
    </div>

    <!-- Hotspot Details Modal -->
    <a-modal
      v-model:open="showDetailsModal"
      title="热点详情"
      width="600px"
      :footer="null"
    >
      <hotspot-details-panel
        v-if="selectedHotspot"
        :hotspot="selectedHotspot"
        :editable="false"
        @close="showDetailsModal = false"
      />
    </a-modal>

    <!-- Fullscreen Modal -->
    <a-modal
      v-model:open="showFullscreen"
      title="全屏地图"
      width="95vw"
      :style="{ top: '20px' }"
      :footer="null"
      :mask-closable="false"
    >
      <gis-map-view
        :markers="visibleMarkers"
        :center="mapCenter"
        :bounds="mapData?.bounds"
        :editable="false"
        :show-filters="true"
        height="80vh"
        :auto-fit="false"
        @marker-click="handleMarkerClick"
        @bounds-change="handleBoundsChange"
      />
    </a-modal>

    <!-- Search Results -->
    <a-drawer
      v-model:open="showSearchResults"
      title="搜索结果"
      placement="right"
      width="400"
    >
      <search-results-panel
        :results="searchResults"
        :loading="searchLoading"
        @select="handleSearchResultSelect"
        @clear="clearSearchResults"
      />
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  ExpandOutlined,
  DownloadOutlined,
  DownOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  CompressOutlined,
  HomeOutlined
} from '@ant-design/icons-vue'

import GisMapView from '@/components/gis/GisMapView.vue'
import HotspotDetailsPanel from '@/components/gis/HotspotDetailsPanel.vue'
import SearchResultsPanel from '@/components/gis/SearchResultsPanel.vue'

import { gisService } from '@/services/gisService'
import type {
  MapData,
  HotspotMarker,
  HotspotLocation,
  GeoCoordinates,
  MapBounds
} from '@/services/gisService'

// Router
const router = useRouter()

// Reactive data
const loading = ref(false)
const mapData = ref<MapData | null>(null)
const showSidebar = ref(true)
const showFullscreen = ref(false)
const showDetailsModal = ref(false)
const showSearchResults = ref(false)

const statusFilter = ref('all')
const searchQuery = ref('')
const mapLayer = ref('street')
const autoFit = ref(true)

const selectedHotspot = ref<HotspotLocation | null>(null)
const currentBounds = ref<MapBounds | null>(null)
const searchResults = ref<HotspotLocation[]>([])
const searchLoading = ref(false)

const mapRef = ref()

// Computed
const visibleMarkers = computed(() => {
  if (!mapData.value) return []
  
  let markers = mapData.value.markers
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    markers = markers.filter(m => m.status === statusFilter.value)
  }
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    markers = markers.filter(m => 
      m.name.toLowerCase().includes(query) ||
      (m.comment && m.comment.toLowerCase().includes(query))
    )
  }
  
  return markers
})

const mapCenter = computed(() => {
  return mapData.value?.center || { latitude: 39.9042, longitude: 116.4074 }
})

const mapHeight = computed(() => {
  return showSidebar.value ? '500px' : '600px'
})

// Lifecycle
onMounted(() => {
  loadMapData()
})

// Methods
const loadMapData = async () => {
  loading.value = true
  try {
    mapData.value = await gisService.getMapData()
  } catch (error) {
    message.error('加载地图数据失败')
    console.error('Failed to load map data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadMapData()
  message.success('地图数据已刷新')
}

const handleBack = () => {
  router.back()
}

const handleStatusFilter = () => {
  // Filtering is handled by computed property
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    return
  }

  searchLoading.value = true
  try {
    searchResults.value = await gisService.searchHotspotsByName(searchQuery.value, true)
    if (searchResults.value.length > 0) {
      showSearchResults.value = true
    } else {
      message.info('未找到匹配的热点')
    }
  } catch (error) {
    message.error('搜索失败')
    console.error('Search error:', error)
  } finally {
    searchLoading.value = false
  }
}

const handleLayerChange = () => {
  // Layer change is handled by the map component
}

const handleFitBounds = () => {
  if (mapRef.value && mapData.value?.bounds) {
    mapRef.value.fitToBounds(mapData.value.bounds)
    autoFit.value = true
  }
}

const handleResetView = () => {
  if (mapRef.value) {
    mapRef.value.resetView()
    autoFit.value = false
  }
}

const handleMarkerClick = (marker: HotspotMarker) => {
  selectedHotspot.value = {
    id: marker.id,
    name: marker.name,
    status: marker.status,
    comment: marker.comment,
    coordinates: {
      latitude: marker.latitude,
      longitude: marker.longitude
    },
    creationby: marker.creationby,
    creationdate: marker.creationdate
  }
  showDetailsModal.value = true
}

const handleBoundsChange = (bounds: MapBounds) => {
  currentBounds.value = bounds
}

const handleSearchResultSelect = (hotspot: HotspotLocation) => {
  selectedHotspot.value = hotspot
  showDetailsModal.value = true
  showSearchResults.value = false
  
  // Center map on selected hotspot
  if (hotspot.coordinates && mapRef.value) {
    // Focus on the selected hotspot
    const center = {
      latitude: hotspot.coordinates.latitude,
      longitude: hotspot.coordinates.longitude
    }
    // You might want to implement a method to center the map on specific coordinates
  }
}

const clearSearchResults = () => {
  searchResults.value = []
  showSearchResults.value = false
  searchQuery.value = ''
}

const handleExport = ({ key }: { key: string }) => {
  switch (key) {
    case 'json':
      exportAsJSON()
      break
    case 'csv':
      exportAsCSV()
      break
    case 'image':
      exportAsImage()
      break
  }
}

const exportAsJSON = () => {
  try {
    const data = {
      markers: visibleMarkers.value,
      statistics: mapData.value?.statistics,
      bounds: currentBounds.value,
      exportTime: new Date().toISOString(),
      filters: {
        status: statusFilter.value,
        search: searchQuery.value
      }
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    })
    
    downloadBlob(blob, `map-view-${Date.now()}.json`)
    message.success('JSON数据已导出')
  } catch (error) {
    message.error('导出失败')
    console.error('Export error:', error)
  }
}

const exportAsCSV = () => {
  try {
    const headers = ['ID', '名称', '状态', '纬度', '经度', '备注', '创建者', '创建时间']
    const rows = visibleMarkers.value.map(marker => [
      marker.id,
      marker.name,
      marker.status,
      marker.latitude,
      marker.longitude,
      marker.comment || '',
      marker.creationby || '',
      marker.creationdate || ''
    ])
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    downloadBlob(blob, `map-view-${Date.now()}.csv`)
    message.success('CSV数据已导出')
  } catch (error) {
    message.error('导出失败')
    console.error('Export error:', error)
  }
}

const exportAsImage = () => {
  // This would require additional implementation to capture the map as an image
  message.info('图片导出功能正在开发中')
}

const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.gis-view-map {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.view-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.map-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.info-card,
.filter-card,
.legend-card,
.view-info-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.legend-marker.active {
  background-color: #52c41a;
}

.legend-marker.inactive {
  background-color: #f5222d;
}

.legend-marker.pending {
  background-color: #faad14;
}

.legend-marker.maintenance {
  background-color: #722ed1;
}

.map-area {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.map-controls-bar {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

/* Responsive design */
@media (max-width: 1200px) {
  .sidebar {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .map-content {
    padding: 8px;
  }
  
  .map-controls-bar {
    padding: 8px 12px;
  }
  
  .sidebar {
    margin-bottom: 16px;
  }
}

/* Custom scrollbar for sidebar */
.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>