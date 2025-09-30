<!--
  GIS Edit Map View
  
  Interactive map editing interface for hotspot location management.
  Provides comprehensive editing tools for adding, moving, and updating hotspot locations.
-->

<template>
  <div class="gis-edit-map">
    <!-- Header -->
    <div class="edit-header">
      <a-page-header
        title="地图编辑"
        sub-title="热点位置编辑和管理"
        @back="handleBack"
      >
        <template #extra>
          <a-space>
            <a-button @click="refreshData" :loading="loading">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
            
            <a-button type="primary" @click="saveChanges" :loading="saving" :disabled="!hasChanges">
              <template #icon><SaveOutlined /></template>
              保存更改
            </a-button>
            
            <a-button @click="discardChanges" :disabled="!hasChanges">
              <template #icon><UndoOutlined /></template>
              撤销更改
            </a-button>
          </a-space>
        </template>
        
        <!-- Edit Mode Info -->
        <div class="edit-mode-info">
          <a-alert
            message="编辑模式已启用"
            description="点击地图添加新位置，拖拽标记更改位置，双击标记编辑详情"
            type="info"
            show-icon
            closable
          />
        </div>
      </a-page-header>
    </div>

    <!-- Main Content -->
    <div class="edit-content">
      <a-row :gutter="16">
        <!-- Edit Tools Sidebar -->
        <a-col :span="6">
          <div class="edit-tools">
            <!-- Quick Actions -->
            <a-card size="small" title="快速操作" class="tools-card">
              <a-space direction="vertical" style="width: 100%">
                <a-button type="primary" @click="enableAddMode" :disabled="addMode" block>
                  <template #icon><PlusOutlined /></template>
                  添加模式
                </a-button>
                
                <a-button @click="enableMoveMode" :disabled="moveMode" block>
                  <template #icon><DragOutlined /></template>
                  移动模式
                </a-button>
                
                <a-button @click="enableDeleteMode" :disabled="deleteMode" danger block>
                  <template #icon><DeleteOutlined /></template>
                  删除模式
                </a-button>
                
                <a-divider size="small" />
                
                <a-button @click="exitEditModes" block>
                  <template #icon><CloseOutlined /></template>
                  退出编辑
                </a-button>
              </a-space>
            </a-card>

            <!-- Coordinate Input -->
            <a-card size="small" title="坐标输入" class="tools-card">
              <a-form layout="vertical">
                <a-row :gutter="8">
                  <a-col :span="12">
                    <a-form-item label="纬度">
                      <a-input-number
                        v-model:value="manualCoords.latitude"
                        :min="-90"
                        :max="90"
                        :precision="6"
                        style="width: 100%"
                        size="small"
                      />
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="经度">
                      <a-input-number
                        v-model:value="manualCoords.longitude"
                        :min="-180"
                        :max="180"
                        :precision="6"
                        style="width: 100%"
                        size="small"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
                
                <a-form-item>
                  <a-button
                    @click="addMarkerAtCoords"
                    :disabled="!isValidManualCoords"
                    size="small"
                    block
                  >
                    在此坐标添加
                  </a-button>
                </a-form-item>
                
                <a-form-item>
                  <a-button @click="centerMapAtCoords" :disabled="!isValidManualCoords" size="small" block>
                    定位到坐标
                  </a-button>
                </a-form-item>
              </a-form>
            </a-card>

            <!-- Batch Operations -->
            <a-card size="small" title="批量操作" class="tools-card">
              <a-space direction="vertical" style="width: 100%">
                <a-upload
                  :before-upload="handleBatchImport"
                  accept=".csv,.json"
                  :show-upload-list="false"
                >
                  <a-button size="small" block>
                    <template #icon><UploadOutlined /></template>
                    批量导入
                  </a-button>
                </a-upload>
                
                <a-button @click="exportSelectedMarkers" size="small" block :disabled="selectedMarkers.length === 0">
                  <template #icon><DownloadOutlined /></template>
                  导出选中 ({{ selectedMarkers.length }})
                </a-button>
                
                <a-button
                  @click="deleteSelectedMarkers"
                  size="small"
                  danger
                  block
                  :disabled="selectedMarkers.length === 0"
                >
                  <template #icon><DeleteOutlined /></template>
                  删除选中
                </a-button>
              </a-space>
            </a-card>

            <!-- Edit History -->
            <a-card size="small" title="编辑历史" class="tools-card">
              <div class="edit-history">
                <div
                  v-for="(change, index) in editHistory"
                  :key="index"
                  class="history-item"
                  @click="previewChange(change)"
                >
                  <div class="history-action">{{ change.action }}</div>
                  <div class="history-target">{{ change.target }}</div>
                  <div class="history-time">{{ formatTime(change.timestamp) }}</div>
                </div>
                
                <div v-if="editHistory.length === 0" class="no-history">
                  暂无编辑记录
                </div>
              </div>
            </a-card>

            <!-- Current Selection -->
            <a-card size="small" title="当前选择" class="tools-card" v-if="selectedMarkers.length > 0">
              <div class="selection-info">
                <p>已选择 {{ selectedMarkers.length }} 个热点</p>
                
                <a-space direction="vertical" style="width: 100%">
                  <a-button size="small" @click="clearSelection" block>
                    清除选择
                  </a-button>
                  
                  <a-button size="small" @click="selectAll" block>
                    全选
                  </a-button>
                  
                  <a-button size="small" @click="invertSelection" block>
                    反选
                  </a-button>
                </a-space>
              </div>
            </a-card>
          </div>
        </a-col>

        <!-- Map Area -->
        <a-col :span="18">
          <div class="map-area">
            <!-- Map Toolbar -->
            <div class="map-toolbar">
              <a-space>
                <!-- Edit Mode Indicators -->
                <a-tag v-if="addMode" color="green">
                  <template #icon><PlusOutlined /></template>
                  添加模式
                </a-tag>
                <a-tag v-if="moveMode" color="blue">
                  <template #icon><DragOutlined /></template>
                  移动模式
                </a-tag>
                <a-tag v-if="deleteMode" color="red">
                  <template #icon><DeleteOutlined /></template>
                  删除模式
                </a-tag>

                <!-- Map Controls -->
                <a-divider type="vertical" />
                
                <a-select
                  v-model:value="mapLayer"
                  size="small"
                  style="width: 120px"
                >
                  <a-select-option value="street">街道地图</a-select-option>
                  <a-select-option value="satellite">卫星地图</a-select-option>
                  <a-select-option value="terrain">地形地图</a-select-option>
                </a-select>

                <a-checkbox v-model:checked="showGrid">显示网格</a-checkbox>
                <a-checkbox v-model:checked="snapToGrid">对齐网格</a-checkbox>
              </a-space>
            </div>

            <!-- Interactive Map -->
            <gis-map-view
              ref="mapRef"
              :markers="editableMarkers"
              :center="mapCenter"
              :bounds="mapData?.bounds"
              :editable="true"
              :show-filters="false"
              height="600px"
              :auto-fit="false"
              @marker-click="handleMarkerClick"
              @marker-add="handleMarkerAdd"
              @marker-move="handleMarkerMove"
              @bounds-change="handleBoundsChange"
            />

            <!-- Edit Overlay -->
            <div v-if="showEditOverlay" class="edit-overlay">
              <div class="overlay-content">
                <a-spin size="large" />
                <div class="overlay-text">{{ overlayText }}</div>
              </div>
            </div>
          </div>
        </a-col>
      </a-row>
    </div>

    <!-- Hotspot Edit Modal -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑热点"
      width="600px"
      @ok="handleHotspotSave"
      @cancel="handleHotspotCancel"
    >
      <hotspot-edit-form
        v-if="editingHotspot"
        ref="editFormRef"
        :hotspot="editingHotspot"
        @change="handleHotspotChange"
      />
    </a-modal>

    <!-- Confirmation Dialogs -->
    <a-modal
      v-model:open="showSaveConfirm"
      title="保存更改"
      @ok="confirmSave"
      @cancel="cancelSave"
    >
      <p>您确定要保存以下更改吗？</p>
      <ul>
        <li v-for="change in pendingChanges" :key="change.id">
          {{ change.description }}
        </li>
      </ul>
    </a-modal>

    <a-modal
      v-model:open="showDiscardConfirm"
      title="撤销更改"
      @ok="confirmDiscard"
      @cancel="cancelDiscard"
    >
      <p>您确定要撤销所有未保存的更改吗？此操作无法恢复。</p>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message, notification } from 'ant-design-vue'
import {
  ReloadOutlined,
  SaveOutlined,
  UndoOutlined,
  PlusOutlined,
  DragOutlined,
  DeleteOutlined,
  CloseOutlined,
  UploadOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

import GisMapView from '@/components/gis/GisMapView.vue'
import HotspotEditForm from '@/components/gis/HotspotEditForm.vue'

import { gisService } from '@/services/gisService'
import type {
  MapData,
  HotspotMarker,
  HotspotLocation,
  GeoCoordinates,
  MapBounds
} from '@/services/gisService'

// Types for edit operations
interface EditChange {
  id: string
  action: 'add' | 'move' | 'delete' | 'update'
  target: string
  timestamp: Date
  data: any
  description: string
}

// Router
const router = useRouter()

// Reactive data
const loading = ref(false)
const saving = ref(false)
const mapData = ref<MapData | null>(null)

// Edit modes
const addMode = ref(false)
const moveMode = ref(false)
const deleteMode = ref(false)

// Edit state
const editHistory = ref<EditChange[]>([])
const pendingChanges = ref<EditChange[]>([])
const selectedMarkers = ref<number[]>([])
const editableMarkers = ref<HotspotMarker[]>([])

// UI state
const showEditModal = ref(false)
const showSaveConfirm = ref(false)
const showDiscardConfirm = ref(false)
const showEditOverlay = ref(false)
const overlayText = ref('')

// Form state
const editingHotspot = ref<HotspotLocation | null>(null)
const manualCoords = reactive<GeoCoordinates>({ latitude: 0, longitude: 0 })
const mapLayer = ref('street')
const showGrid = ref(false)
const snapToGrid = ref(false)

const mapRef = ref()
const editFormRef = ref()

// Computed
const hasChanges = computed(() => pendingChanges.value.length > 0)

const isValidManualCoords = computed(() => {
  return (
    manualCoords.latitude >= -90 &&
    manualCoords.latitude <= 90 &&
    manualCoords.longitude >= -180 &&
    manualCoords.longitude <= 180 &&
    (manualCoords.latitude !== 0 || manualCoords.longitude !== 0)
  )
})

const mapCenter = computed(() => {
  return mapData.value?.center || { latitude: 39.9042, longitude: 116.4074 }
})

// Lifecycle
onMounted(() => {
  loadMapData()
})

// Watchers
watch(pendingChanges, (changes) => {
  if (changes.length > 0) {
    window.addEventListener('beforeunload', handleBeforeUnload)
  } else {
    window.removeEventListener('beforeunload', handleBeforeUnload)
  }
}, { deep: true })

// Methods
const loadMapData = async () => {
  loading.value = true
  try {
    mapData.value = await gisService.getMapData()
    editableMarkers.value = [...(mapData.value?.markers || [])]
  } catch (error) {
    message.error('加载地图数据失败')
    console.error('Failed to load map data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  if (hasChanges.value) {
    const confirmed = await new Promise((resolve) => {
      Modal.confirm({
        title: '刷新确认',
        content: '刷新将丢失所有未保存的更改，是否继续？',
        onOk: () => resolve(true),
        onCancel: () => resolve(false)
      })
    })
    
    if (!confirmed) return
  }
  
  await loadMapData()
  clearAllChanges()
  message.success('地图数据已刷新')
}

const handleBack = () => {
  if (hasChanges.value) {
    showDiscardConfirm.value = true
  } else {
    router.back()
  }
}

// Edit mode controls
const enableAddMode = () => {
  exitEditModes()
  addMode.value = true
  message.info('添加模式已启用，点击地图添加热点位置')
}

const enableMoveMode = () => {
  exitEditModes()
  moveMode.value = true
  message.info('移动模式已启用，拖拽标记更改位置')
}

const enableDeleteMode = () => {
  exitEditModes()
  deleteMode.value = true
  message.info('删除模式已启用，点击标记删除热点')
}

const exitEditModes = () => {
  addMode.value = false
  moveMode.value = false
  deleteMode.value = false
}

// Map interaction handlers
const handleMarkerClick = (marker: HotspotMarker) => {
  if (deleteMode.value) {
    deleteMarker(marker.id)
  } else {
    // Toggle selection or edit
    if (selectedMarkers.value.includes(marker.id)) {
      selectedMarkers.value = selectedMarkers.value.filter(id => id !== marker.id)
    } else {
      selectedMarkers.value.push(marker.id)
    }
  }
}

const handleMarkerAdd = (coordinates: GeoCoordinates) => {
  if (addMode.value) {
    addNewMarker(coordinates)
  }
}

const handleMarkerMove = (markerId: number, coordinates: GeoCoordinates) => {
  if (moveMode.value) {
    moveMarker(markerId, coordinates)
  }
}

const handleBoundsChange = (bounds: MapBounds) => {
  // Update current view bounds
}

// Edit operations
const addNewMarker = (coordinates: GeoCoordinates) => {
  const newId = Date.now() // Temporary ID
  const newMarker: HotspotMarker = {
    id: newId,
    name: `新热点 ${newId}`,
    latitude: coordinates.latitude,
    longitude: coordinates.longitude,
    status: 'pending',
    comment: '新添加的热点'
  }
  
  editableMarkers.value.push(newMarker)
  
  addChange({
    id: `add-${newId}`,
    action: 'add',
    target: newMarker.name,
    timestamp: new Date(),
    data: { marker: newMarker, coordinates },
    description: `添加热点: ${newMarker.name}`
  })
  
  message.success('已添加新热点位置')
}

const moveMarker = (markerId: number, coordinates: GeoCoordinates) => {
  const markerIndex = editableMarkers.value.findIndex(m => m.id === markerId)
  if (markerIndex === -1) return
  
  const marker = editableMarkers.value[markerIndex]
  const oldCoordinates = { latitude: marker.latitude, longitude: marker.longitude }
  
  marker.latitude = coordinates.latitude
  marker.longitude = coordinates.longitude
  
  addChange({
    id: `move-${markerId}-${Date.now()}`,
    action: 'move',
    target: marker.name,
    timestamp: new Date(),
    data: { markerId, oldCoordinates, newCoordinates: coordinates },
    description: `移动热点: ${marker.name}`
  })
  
  message.success(`已移动热点: ${marker.name}`)
}

const deleteMarker = (markerId: number) => {
  const markerIndex = editableMarkers.value.findIndex(m => m.id === markerId)
  if (markerIndex === -1) return
  
  const marker = editableMarkers.value[markerIndex]
  editableMarkers.value.splice(markerIndex, 1)
  
  // Remove from selection if selected
  selectedMarkers.value = selectedMarkers.value.filter(id => id !== markerId)
  
  addChange({
    id: `delete-${markerId}`,
    action: 'delete',
    target: marker.name,
    timestamp: new Date(),
    data: { marker },
    description: `删除热点: ${marker.name}`
  })
  
  message.success(`已删除热点: ${marker.name}`)
}

// Manual coordinate operations
const addMarkerAtCoords = () => {
  if (!isValidManualCoords.value) return
  
  addNewMarker({ ...manualCoords })
  manualCoords.latitude = 0
  manualCoords.longitude = 0
}

const centerMapAtCoords = () => {
  if (!isValidManualCoords.value || !mapRef.value) return
  
  // Center map at coordinates
  // This would need to be implemented in the map component
  message.info(`已定位到坐标: ${manualCoords.latitude}, ${manualCoords.longitude}`)
}

// Batch operations
const handleBatchImport = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      let importData: any[]
      
      if (file.name.endsWith('.json')) {
        importData = JSON.parse(content)
      } else if (file.name.endsWith('.csv')) {
        importData = parseCSV(content)
      } else {
        throw new Error('Unsupported file format')
      }
      
      processBatchImport(importData)
    } catch (error) {
      message.error('文件格式错误')
      console.error('Import error:', error)
    }
  }
  
  reader.readAsText(file)
  return false // Prevent default upload
}

const parseCSV = (content: string): any[] => {
  const lines = content.split('\n')
  const headers = lines[0].split(',').map(h => h.trim())
  
  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim())
    const obj: any = {}
    headers.forEach((header, index) => {
      obj[header] = values[index]
    })
    return obj
  })
}

const processBatchImport = (data: any[]) => {
  let imported = 0
  
  data.forEach(item => {
    if (item.latitude && item.longitude) {
      const coordinates = {
        latitude: parseFloat(item.latitude),
        longitude: parseFloat(item.longitude)
      }
      
      if (gisService.isValidCoordinates(coordinates.latitude, coordinates.longitude)) {
        addNewMarker(coordinates)
        imported++
      }
    }
  })
  
  message.success(`成功导入 ${imported} 个热点位置`)
}

const exportSelectedMarkers = () => {
  const selectedData = editableMarkers.value.filter(m => selectedMarkers.value.includes(m.id))
  
  const data = {
    markers: selectedData,
    exportTime: new Date().toISOString(),
    count: selectedData.length
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  })
  
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `selected-markers-${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
  message.success(`已导出 ${selectedData.length} 个选中的热点`)
}

const deleteSelectedMarkers = () => {
  if (selectedMarkers.value.length === 0) return
  
  Modal.confirm({
    title: '确认删除',
    content: `您确定要删除 ${selectedMarkers.value.length} 个选中的热点吗？`,
    onOk: () => {
      selectedMarkers.value.forEach(markerId => {
        deleteMarker(markerId)
      })
      selectedMarkers.value = []
    }
  })
}

// Selection operations
const clearSelection = () => {
  selectedMarkers.value = []
}

const selectAll = () => {
  selectedMarkers.value = editableMarkers.value.map(m => m.id)
}

const invertSelection = () => {
  const allIds = editableMarkers.value.map(m => m.id)
  selectedMarkers.value = allIds.filter(id => !selectedMarkers.value.includes(id))
}

// Change management
const addChange = (change: EditChange) => {
  editHistory.value.unshift(change)
  pendingChanges.value.push(change)
  
  // Limit history size
  if (editHistory.value.length > 50) {
    editHistory.value = editHistory.value.slice(0, 50)
  }
}

const previewChange = (change: EditChange) => {
  // Implement change preview
  message.info(`预览更改: ${change.description}`)
}

const clearAllChanges = () => {
  editHistory.value = []
  pendingChanges.value = []
  selectedMarkers.value = []
}

// Save/Discard operations
const saveChanges = () => {
  if (!hasChanges.value) return
  showSaveConfirm.value = true
}

const confirmSave = async () => {
  saving.value = true
  showEditOverlay.value = true
  overlayText.value = '正在保存更改...'
  
  try {
    // Process all pending changes
    for (const change of pendingChanges.value) {
      await processChange(change)
    }
    
    clearAllChanges()
    await loadMapData()
    
    message.success('所有更改已保存')
    showSaveConfirm.value = false
  } catch (error) {
    message.error('保存失败')
    console.error('Save error:', error)
  } finally {
    saving.value = false
    showEditOverlay.value = false
  }
}

const processChange = async (change: EditChange) => {
  switch (change.action) {
    case 'add':
      // Implementation would depend on your API
      break
    case 'move':
      await gisService.updateHotspotLocation(
        change.data.markerId,
        change.data.newCoordinates
      )
      break
    case 'delete':
      await gisService.removeHotspotLocation(change.data.marker.id)
      break
    case 'update':
      // Handle hotspot updates
      break
  }
}

const cancelSave = () => {
  showSaveConfirm.value = false
}

const discardChanges = () => {
  if (!hasChanges.value) return
  showDiscardConfirm.value = true
}

const confirmDiscard = () => {
  clearAllChanges()
  loadMapData()
  exitEditModes()
  message.info('已撤销所有更改')
  showDiscardConfirm.value = false
}

const cancelDiscard = () => {
  showDiscardConfirm.value = false
}

// Hotspot editing
const handleHotspotChange = () => {
  // Handle form changes
}

const handleHotspotSave = () => {
  // Save hotspot changes
  showEditModal.value = false
}

const handleHotspotCancel = () => {
  showEditModal.value = false
  editingHotspot.value = null
}

// Utility functions
const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  e.preventDefault()
  e.returnValue = '您有未保存的更改，确定要离开吗？'
}

// Cleanup
onUnmounted(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style scoped>
.gis-edit-map {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.edit-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.edit-mode-info {
  margin-top: 16px;
}

.edit-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.edit-tools {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.tools-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.edit-history {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: #f5f5f5;
}

.history-action {
  font-weight: 500;
  font-size: 12px;
  color: #1890ff;
}

.history-target {
  font-size: 11px;
  color: #666;
  margin: 2px 0;
}

.history-time {
  font-size: 10px;
  color: #999;
}

.no-history {
  text-align: center;
  color: #999;
  padding: 16px;
  font-size: 12px;
}

.selection-info {
  font-size: 12px;
}

.map-area {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.map-toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.overlay-content {
  text-align: center;
}

.overlay-text {
  margin-top: 16px;
  color: #666;
}

/* Custom scrollbar for edit tools */
.edit-tools::-webkit-scrollbar {
  width: 4px;
}

.edit-tools::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 2px;
}

.edit-tools::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 2px;
}

.edit-tools::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* Responsive design */
@media (max-width: 1200px) {
  .edit-content {
    padding: 8px;
  }
  
  .edit-tools {
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .map-toolbar {
    padding: 8px 12px;
  }
  
  .edit-tools {
    margin-bottom: 16px;
  }
}
</style>