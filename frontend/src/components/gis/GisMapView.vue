<!--
  GIS Map View Component
  
  Interactive map component using Leaflet for hotspot visualization and geographic operations.
  Supports marker display, location editing, and map interaction.
-->

<template>
  <div class="gis-map-container">
    <!-- Map Container -->
    <div
      ref="mapContainer"
      class="gis-map"
      :style="{ height: mapHeight }"
    ></div>

    <!-- Map Controls -->
    <div class="map-controls">
      <!-- Zoom Controls -->
      <div class="zoom-controls">
        <a-button-group size="small">
          <a-button @click="zoomIn" :icon="h(ZoomInOutlined)" />
          <a-button @click="zoomOut" :icon="h(ZoomOutOutlined)" />
          <a-button @click="resetView" :icon="h(HomeOutlined)" />
        </a-button-group>
      </div>

      <!-- Layer Controls -->
      <div class="layer-controls">
        <a-select
          v-model:value="selectedBaseLayer"
          size="small"
          style="width: 120px"
          @change="changeBaseLayer"
        >
          <a-select-option value="osm">街道地图</a-select-option>
          <a-select-option value="satellite">卫星地图</a-select-option>
          <a-select-option value="terrain">地形地图</a-select-option>
        </a-select>
      </div>

      <!-- Filter Controls -->
      <div class="filter-controls" v-if="showFilters">
        <a-space size="small">
          <a-checkbox v-model:checked="showActiveOnly">
            仅显示活跃热点
          </a-checkbox>
          <a-button size="small" @click="refreshMarkers" :loading="loading">
            刷新
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="map-loading">
      <a-spin size="large" />
      <div class="loading-text">加载地图数据...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, h } from 'vue'
import { message } from 'ant-design-vue'
import { ZoomInOutlined, ZoomOutOutlined, HomeOutlined } from '@ant-design/icons-vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Import marker icons
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

import type { HotspotMarker, MapBounds, GeoCoordinates } from '@/services/gisService'

// Fix Leaflet default markers
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

// Props
interface Props {
  markers?: HotspotMarker[]
  center?: GeoCoordinates
  zoom?: number
  bounds?: MapBounds
  editable?: boolean
  showFilters?: boolean
  height?: string
  autoFit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  markers: () => [],
  zoom: 13,
  editable: false,
  showFilters: true,
  height: '500px',
  autoFit: true
})

// Emits
interface Emits {
  (e: 'marker-click', marker: HotspotMarker): void
  (e: 'marker-add', coordinates: GeoCoordinates): void
  (e: 'marker-move', markerId: number, coordinates: GeoCoordinates): void
  (e: 'bounds-change', bounds: MapBounds): void
  (e: 'refresh'): void
}

const emit = defineEmits<Emits>()

// Reactive data
const mapContainer = ref<HTMLElement>()
const map = ref<L.Map>()
const markerLayer = ref<L.LayerGroup>()
const selectedBaseLayer = ref('osm')
const showActiveOnly = ref(false)
const loading = ref(false)

// Computed
const mapHeight = computed(() => props.height)

// Base layers
const baseLayers = {
  osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri'
  }),
  terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
  })
}

// Lifecycle
onMounted(async () => {
  await nextTick()
  initializeMap()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})

// Watchers
watch(() => props.markers, (newMarkers) => {
  updateMarkers(newMarkers)
}, { deep: true })

watch(() => props.center, (newCenter) => {
  if (newCenter && map.value) {
    map.value.setView([newCenter.latitude, newCenter.longitude], map.value.getZoom())
  }
})

watch(() => props.bounds, (newBounds) => {
  if (newBounds && map.value && props.autoFit) {
    fitToBounds(newBounds)
  }
})

watch(showActiveOnly, () => {
  updateMarkers(props.markers)
})

// Methods
const initializeMap = () => {
  if (!mapContainer.value) return

  // Initialize map
  const defaultCenter: [number, number] = props.center 
    ? [props.center.latitude, props.center.longitude]
    : [39.9042, 116.4074] // Beijing coordinates

  map.value = L.map(mapContainer.value, {
    center: defaultCenter,
    zoom: props.zoom,
    zoomControl: false // We'll add custom controls
  })

  // Add base layer
  baseLayers[selectedBaseLayer.value].addTo(map.value)

  // Create marker layer
  markerLayer.value = L.layerGroup().addTo(map.value)

  // Add click handler for editable mode
  if (props.editable) {
    map.value.on('click', handleMapClick)
  }

  // Add bounds change handler
  map.value.on('moveend', handleBoundsChange)

  // Initial marker setup
  updateMarkers(props.markers)

  // Fit to bounds if available
  if (props.bounds && props.autoFit) {
    fitToBounds(props.bounds)
  }
}

const updateMarkers = (markers: HotspotMarker[]) => {
  if (!markerLayer.value) return

  // Clear existing markers
  markerLayer.value.clearLayers()

  // Filter markers if needed
  const filteredMarkers = showActiveOnly.value 
    ? markers.filter(marker => marker.status === 'active')
    : markers

  // Add markers to map
  filteredMarkers.forEach(marker => {
    addMarkerToMap(marker)
  })
}

const addMarkerToMap = (marker: HotspotMarker) => {
  if (!markerLayer.value) return

  // Create marker icon based on status
  const icon = createMarkerIcon(marker.status)

  // Create marker
  const leafletMarker = L.marker([marker.latitude, marker.longitude], { icon })

  // Create popup content
  const popupContent = createPopupContent(marker)
  leafletMarker.bindPopup(popupContent)

  // Add click handler
  leafletMarker.on('click', () => {
    emit('marker-click', marker)
  })

  // Make draggable if editable
  if (props.editable) {
    leafletMarker.setDraggable(true)
    leafletMarker.on('dragend', (e) => {
      const position = e.target.getLatLng()
      emit('marker-move', marker.id, {
        latitude: position.lat,
        longitude: position.lng
      })
    })
  }

  // Add to layer
  markerLayer.value.addLayer(leafletMarker)
}

const createMarkerIcon = (status: string) => {
  const color = getStatusColor(status)
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  })
}

const getStatusColor = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'active':
      return '#52c41a' // Green
    case 'inactive':
      return '#f5222d' // Red
    case 'pending':
      return '#faad14' // Orange
    default:
      return '#d9d9d9' // Gray
  }
}

const createPopupContent = (marker: HotspotMarker): string => {
  return `
    <div class="marker-popup">
      <h4>${marker.name}</h4>
      <p><strong>状态:</strong> ${getStatusText(marker.status)}</p>
      <p><strong>坐标:</strong> ${marker.latitude.toFixed(6)}, ${marker.longitude.toFixed(6)}</p>
      ${marker.comment ? `<p><strong>备注:</strong> ${marker.comment}</p>` : ''}
      ${marker.creationby ? `<p><strong>创建者:</strong> ${marker.creationby}</p>` : ''}
    </div>
  `
}

const getStatusText = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'active':
      return '活跃'
    case 'inactive':
      return '非活跃'
    case 'pending':
      return '待处理'
    default:
      return '未知'
  }
}

const handleMapClick = (e: L.LeafletMouseEvent) => {
  if (props.editable) {
    emit('marker-add', {
      latitude: e.latlng.lat,
      longitude: e.latlng.lng
    })
  }
}

const handleBoundsChange = () => {
  if (!map.value) return

  const bounds = map.value.getBounds()
  emit('bounds-change', {
    north: bounds.getNorth(),
    south: bounds.getSouth(),
    east: bounds.getEast(),
    west: bounds.getWest()
  })
}

const zoomIn = () => {
  if (map.value) {
    map.value.zoomIn()
  }
}

const zoomOut = () => {
  if (map.value) {
    map.value.zoomOut()
  }
}

const resetView = () => {
  if (map.value) {
    if (props.bounds && props.autoFit) {
      fitToBounds(props.bounds)
    } else if (props.center) {
      map.value.setView([props.center.latitude, props.center.longitude], props.zoom)
    }
  }
}

const changeBaseLayer = (layerKey: string) => {
  if (!map.value) return

  // Remove current base layer
  map.value.eachLayer((layer) => {
    if (layer instanceof L.TileLayer) {
      map.value!.removeLayer(layer)
    }
  })

  // Add new base layer
  baseLayers[layerKey as keyof typeof baseLayers].addTo(map.value)
}

const fitToBounds = (bounds: MapBounds) => {
  if (!map.value) return

  const leafletBounds = L.latLngBounds([
    [bounds.south, bounds.west],
    [bounds.north, bounds.east]
  ])

  map.value.fitBounds(leafletBounds, { padding: [20, 20] })
}

const refreshMarkers = () => {
  loading.value = true
  emit('refresh')
  
  // Simulate loading delay
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

// Expose methods for parent components
defineExpose({
  zoomIn,
  zoomOut,
  resetView,
  fitToBounds,
  refreshMarkers
})
</script>

<style scoped>
.gis-map-container {
  position: relative;
  width: 100%;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.gis-map {
  width: 100%;
  background: #f0f2f5;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.zoom-controls,
.layer-controls,
.filter-controls {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 4px;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-text {
  margin-top: 16px;
  color: #666;
}

:deep(.marker-popup) {
  font-size: 14px;
}

:deep(.marker-popup h4) {
  margin: 0 0 8px 0;
  color: #1890ff;
}

:deep(.marker-popup p) {
  margin: 4px 0;
  line-height: 1.4;
}

:deep(.custom-marker) {
  background: transparent !important;
  border: none !important;
}

/* Leaflet control overrides */
:deep(.leaflet-control-zoom) {
  display: none;
}

:deep(.leaflet-control-attribution) {
  font-size: 10px;
  background: rgba(255, 255, 255, 0.8);
}
</style>