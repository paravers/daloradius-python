<!--
  GIS Main View
  
  Main interface for GIS functionality providing comprehensive map-based hotspot management.
  Includes interactive map, search capabilities, and hotspot management tools.
-->

<template>
  <div class="gis-main-view">
    <!-- Page Header -->
    <div class="page-header">
      <a-page-header
        title="GIS地图管理"
        sub-title="热点地理位置管理和可视化"
        @back="handleBack"
      >
        <template #extra>
          <a-space>
            <a-button @click="refreshData" :loading="loading">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
            
            <a-button type="primary" @click="showHelpModal = true">
              <template #icon><QuestionCircleOutlined /></template>
              帮助
            </a-button>
          </a-space>
        </template>
        
        <!-- Statistics Cards -->
        <div class="statistics-cards">
          <a-row :gutter="16">
            <a-col :span="6">
              <a-statistic
                title="总热点数"
                :value="mapData?.statistics.total_hotspots || 0"
                suffix="个"
                :value-style="{ color: '#1890ff' }"
              />
            </a-col>
            <a-col :span="6">
              <a-statistic
                title="活跃热点"
                :value="mapData?.statistics.active_hotspots || 0"
                suffix="个"
                :value-style="{ color: '#52c41a' }"
              />
            </a-col>
            <a-col :span="6">
              <a-statistic
                title="非活跃热点"
                :value="mapData?.statistics.inactive_hotspots || 0"
                suffix="个"
                :value-style="{ color: '#f5222d' }"
              />
            </a-col>
            <a-col :span="6">
              <a-statistic
                title="活跃率"
                :value="mapData?.statistics.activity_rate || 0"
                suffix="%"
                :precision="1"
                :value-style="{ color: '#722ed1' }"
              />
            </a-col>
          </a-row>
        </div>
      </a-page-header>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <a-row :gutter="16">
        <!-- Map Controls Sidebar -->
        <a-col :span="6">
          <gis-map-controls
            :show-search="true"
            :show-filters="true"
            :show-coordinate-tools="true"
            :show-statistics="true"
            :show-quick-actions="true"
            :editable="editMode"
            :statistics="mapData?.statistics"
            @text-search="handleTextSearch"
            @location-search="handleLocationSearch"
            @filter-change="handleFilterChange"
            @add-marker="handleAddMarker"
            @refresh="refreshData"
            @fit-bounds="handleFitBounds"
          />
        </a-col>

        <!-- Map Display -->
        <a-col :span="18">
          <div class="map-container">
            <!-- Map Toolbar -->
            <div class="map-toolbar">
              <a-space>
                <a-switch
                  v-model:checked="editMode"
                  checked-children="编辑"
                  un-checked-children="查看"
                />
                
                <a-select
                  v-model:value="viewMode"
                  style="width: 120px"
                  @change="handleViewModeChange"
                >
                  <a-select-option value="all">所有热点</a-select-option>
                  <a-select-option value="active">仅活跃</a-select-option>
                  <a-select-option value="inactive">仅非活跃</a-select-option>
                  <a-select-option value="no-location">无位置</a-select-option>
                </a-select>

                <a-button size="small" @click="exportMapData">
                  <template #icon><DownloadOutlined /></template>
                  导出
                </a-button>
              </a-space>
            </div>

            <!-- Interactive Map -->
            <gis-map-view
              ref="mapRef"
              :markers="filteredMarkers"
              :center="mapCenter"
              :bounds="mapData?.bounds"
              :editable="editMode"
              :show-filters="false"
              height="600px"
              :auto-fit="true"
              @marker-click="handleMarkerClick"
              @marker-add="handleMarkerAdd"
              @marker-move="handleMarkerMove"
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
        :editable="editMode"
        @update="handleHotspotUpdate"
        @close="showDetailsModal = false"
      />
    </a-modal>

    <!-- Location Edit Modal -->
    <a-modal
      v-model:open="showLocationModal"
      title="编辑位置"
      @ok="handleLocationSave"
      @cancel="handleLocationCancel"
    >
      <div class="location-edit-form">
        <a-form layout="vertical">
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="纬度">
                <a-input-number
                  v-model:value="editingLocation.latitude"
                  :min="-90"
                  :max="90"
                  :precision="6"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="经度">
                <a-input-number
                  v-model:value="editingLocation.longitude"
                  :min="-180"
                  :max="180"
                  :precision="6"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-form-item>
            <a-button @click="getCurrentLocation" :loading="gettingLocation">
              <template #icon><EnvironmentOutlined /></template>
              获取当前位置
            </a-button>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- Help Modal -->
    <a-modal
      v-model:open="showHelpModal"
      title="GIS地图帮助"
      width="800px"
      :footer="null"
    >
      <div class="help-content">
        <a-collapse>
          <a-collapse-panel key="basic" header="基本操作">
            <ul>
              <li>左键点击地图查看热点详情</li>
              <li>编辑模式下点击地图添加新热点位置</li>
              <li>拖拽热点标记更改位置</li>
              <li>使用鼠标滚轮缩放地图</li>
              <li>拖拽地图进行移动</li>
            </ul>
          </a-collapse-panel>
          
          <a-collapse-panel key="search" header="搜索功能">
            <ul>
              <li>文本搜索：按热点名称或描述搜索</li>
              <li>位置搜索：输入坐标和半径搜索附近热点</li>
              <li>状态过滤：按热点状态筛选显示</li>
              <li>时间过滤：按创建时间范围筛选</li>
            </ul>
          </a-collapse-panel>
          
          <a-collapse-panel key="tools" header="坐标工具">
            <ul>
              <li>坐标验证：验证经纬度坐标是否有效</li>
              <li>添加标记：手动输入坐标添加热点位置</li>
              <li>位置编辑：修改现有热点的地理坐标</li>
              <li>批量操作：支持批量更新热点位置</li>
            </ul>
          </a-collapse-panel>
        </a-collapse>
      </div>
    </a-modal>

    <!-- Search Results Drawer -->
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message, notification } from 'ant-design-vue'
import {
  ReloadOutlined,
  QuestionCircleOutlined,
  DownloadOutlined,
  EnvironmentOutlined
} from '@ant-design/icons-vue'

import GisMapView from '@/components/gis/GisMapView.vue'
import GisMapControls from '@/components/gis/GisMapControls.vue'
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
const editMode = ref(false)
const viewMode = ref('all')

const selectedHotspot = ref<HotspotLocation | null>(null)
const showDetailsModal = ref(false)
const showLocationModal = ref(false)
const showHelpModal = ref(false)
const showSearchResults = ref(false)

const editingLocation = reactive<GeoCoordinates>({ latitude: 0, longitude: 0 })
const gettingLocation = ref(false)

const searchResults = ref<HotspotLocation[]>([])
const searchLoading = ref(false)

const mapRef = ref()

// Computed
const filteredMarkers = computed(() => {
  if (!mapData.value) return []
  
  const markers = mapData.value.markers
  
  switch (viewMode.value) {
    case 'active':
      return markers.filter(m => m.status === 'active')
    case 'inactive':
      return markers.filter(m => m.status === 'inactive')
    case 'no-location':
      return [] // This will be handled separately
    default:
      return markers
  }
})

const mapCenter = computed(() => {
  return mapData.value?.center || { latitude: 39.9042, longitude: 116.4074 }
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

const handleTextSearch = async (query: string) => {
  searchLoading.value = true
  try {
    searchResults.value = await gisService.searchHotspotsByName(query, true)
    showSearchResults.value = true
    
    if (searchResults.value.length === 0) {
      message.info('未找到匹配的热点')
    }
  } catch (error) {
    message.error('搜索失败')
    console.error('Search error:', error)
  } finally {
    searchLoading.value = false
  }
}

const handleLocationSearch = async (location: GeoCoordinates, radius: number) => {
  searchLoading.value = true
  try {
    searchResults.value = await gisService.searchHotspotsNearLocation({
      latitude: location.latitude,
      longitude: location.longitude,
      radius_km: radius
    })
    showSearchResults.value = true
    
    if (searchResults.value.length === 0) {
      message.info('指定范围内未找到热点')
    } else {
      message.success(`找到 ${searchResults.value.length} 个热点`)
    }
  } catch (error) {
    message.error('位置搜索失败')
    console.error('Location search error:', error)
  } finally {
    searchLoading.value = false
  }
}

const handleFilterChange = (filters: any) => {
  // Apply filters to map display
  console.log('Filters changed:', filters)
  // Implement filter logic based on your requirements
}

const handleAddMarker = (coordinates: GeoCoordinates) => {
  editingLocation.latitude = coordinates.latitude
  editingLocation.longitude = coordinates.longitude
  showLocationModal.value = true
}

const handleMarkerClick = (marker: HotspotMarker) => {
  // Load full hotspot details
  loadHotspotDetails(marker.id)
}

const handleMarkerAdd = (coordinates: GeoCoordinates) => {
  if (editMode.value) {
    handleAddMarker(coordinates)
  }
}

const handleMarkerMove = async (markerId: number, coordinates: GeoCoordinates) => {
  try {
    await gisService.updateHotspotLocation(markerId, coordinates)
    message.success('热点位置已更新')
    await refreshData()
  } catch (error) {
    message.error('更新热点位置失败')
    console.error('Failed to update hotspot location:', error)
  }
}

const handleBoundsChange = (bounds: MapBounds) => {
  // Update current view bounds
  console.log('Bounds changed:', bounds)
}

const handleViewModeChange = async () => {
  if (viewMode.value === 'no-location') {
    // Load hotspots without location
    try {
      const result = await gisService.getHotspotsWithoutLocation()
      // Handle hotspots without location display
      console.log('Hotspots without location:', result)
    } catch (error) {
      message.error('加载无位置热点失败')
    }
  }
}

const handleFitBounds = () => {
  if (mapRef.value && mapData.value?.bounds) {
    mapRef.value.fitToBounds(mapData.value.bounds)
  }
}

const loadHotspotDetails = async (hotspotId: number) => {
  try {
    // Find hotspot in current data or load from API
    const marker = mapData.value?.markers.find(m => m.id === hotspotId)
    if (marker) {
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
  } catch (error) {
    message.error('加载热点详情失败')
    console.error('Failed to load hotspot details:', error)
  }
}

const handleHotspotUpdate = async (hotspot: HotspotLocation) => {
  try {
    // Update hotspot location if coordinates changed
    if (hotspot.coordinates) {
      await gisService.updateHotspotLocation(hotspot.id, hotspot.coordinates)
    }
    
    message.success('热点信息已更新')
    showDetailsModal.value = false
    await refreshData()
  } catch (error) {
    message.error('更新热点信息失败')
    console.error('Failed to update hotspot:', error)
  }
}

const handleLocationSave = async () => {
  try {
    // Add new hotspot location
    if (selectedHotspot.value) {
      await gisService.updateHotspotLocation(selectedHotspot.value.id, editingLocation)
    }
    
    message.success('位置已保存')
    showLocationModal.value = false
    await refreshData()
  } catch (error) {
    message.error('保存位置失败')
    console.error('Failed to save location:', error)
  }
}

const handleLocationCancel = () => {
  showLocationModal.value = false
  editingLocation.latitude = 0
  editingLocation.longitude = 0
}

const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    message.error('浏览器不支持地理位置获取')
    return
  }

  gettingLocation.value = true
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      editingLocation.latitude = position.coords.latitude
      editingLocation.longitude = position.coords.longitude
      message.success('已获取当前位置')
      gettingLocation.value = false
    },
    (error) => {
      message.error('获取当前位置失败')
      console.error('Geolocation error:', error)
      gettingLocation.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000
    }
  )
}

const handleSearchResultSelect = (hotspot: HotspotLocation) => {
  if (hotspot.coordinates) {
    // Center map on selected hotspot
    if (mapRef.value) {
      mapRef.value.resetView()
    }
  }
  
  selectedHotspot.value = hotspot
  showDetailsModal.value = true
  showSearchResults.value = false
}

const clearSearchResults = () => {
  searchResults.value = []
  showSearchResults.value = false
}

const exportMapData = async () => {
  try {
    const data = {
      markers: filteredMarkers.value,
      statistics: mapData.value?.statistics,
      exportTime: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `gis-map-data-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    URL.revokeObjectURL(url)
    message.success('地图数据已导出')
  } catch (error) {
    message.error('导出失败')
    console.error('Export error:', error)
  }
}
</script>

<style scoped>
.gis-main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.page-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.statistics-cards {
  margin-top: 16px;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.map-container {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.map-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.location-edit-form {
  padding: 16px 0;
}

.help-content {
  max-height: 500px;
  overflow-y: auto;
}

.help-content ul {
  margin: 0;
  padding-left: 20px;
}

.help-content li {
  margin: 8px 0;
  line-height: 1.5;
}

/* Responsive design */
@media (max-width: 1200px) {
  .main-content :deep(.ant-col:first-child) {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .statistics-cards :deep(.ant-col) {
    margin-bottom: 16px;
  }
  
  .main-content {
    padding: 8px;
  }
  
  .map-toolbar {
    padding: 8px 12px;
  }
}
</style>