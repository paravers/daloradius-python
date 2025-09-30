<!--
  Hotspot Map Marker Component
  
  Individual marker component for displaying hotspots on the map.
  Supports different marker styles based on hotspot status and provides interaction capabilities.
-->

<template>
  <div
    class="hotspot-marker"
    :class="markerClasses"
    :style="markerStyle"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Marker Icon -->
    <div class="marker-icon">
      <component :is="statusIcon" :style="{ color: statusColor }" />
    </div>

    <!-- Marker Label -->
    <div v-if="showLabel" class="marker-label">
      {{ hotspot.name }}
    </div>

    <!-- Hover Tooltip -->
    <div v-if="showTooltip && hovered" class="marker-tooltip">
      <div class="tooltip-content">
        <h4>{{ hotspot.name }}</h4>
        <p><strong>状态:</strong> {{ statusText }}</p>
        <p><strong>坐标:</strong> {{ coordinateText }}</p>
        <p v-if="hotspot.comment"><strong>备注:</strong> {{ hotspot.comment }}</p>
        <p v-if="hotspot.distance_km"><strong>距离:</strong> {{ hotspot.distance_km }}km</p>
      </div>
    </div>

    <!-- Selection Ring -->
    <div v-if="selected" class="selection-ring"></div>

    <!-- Pulse Animation for Active Status -->
    <div v-if="hotspot.status === 'active' && showPulse" class="pulse-ring"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import {
  WifiOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  QuestionCircleOutlined,
  EnvironmentOutlined
} from '@ant-design/icons-vue'

import type { HotspotLocation } from '@/services/gisService'

// Props
interface Props {
  hotspot: HotspotLocation
  selected?: boolean
  showLabel?: boolean
  showTooltip?: boolean
  showPulse?: boolean
  size?: 'small' | 'medium' | 'large'
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  showLabel: false,
  showTooltip: true,
  showPulse: true,
  size: 'medium',
  clickable: true
})

// Emits
interface Emits {
  (e: 'click', hotspot: HotspotLocation): void
  (e: 'hover', hotspot: HotspotLocation): void
  (e: 'leave', hotspot: HotspotLocation): void
}

const emit = defineEmits<Emits>()

// Reactive data
const hovered = ref(false)

// Computed properties
const markerClasses = computed(() => ({
  'hotspot-marker--selected': props.selected,
  'hotspot-marker--clickable': props.clickable,
  'hotspot-marker--hovered': hovered.value,
  [`hotspot-marker--${props.size}`]: true,
  [`hotspot-marker--${props.hotspot.status?.toLowerCase()}`]: props.hotspot.status
}))

const markerStyle = computed(() => {
  const baseSize = getSizeValue(props.size)
  return {
    width: `${baseSize}px`,
    height: `${baseSize}px`
  }
})

const statusColor = computed(() => {
  switch (props.hotspot.status?.toLowerCase()) {
    case 'active':
      return '#52c41a' // Green
    case 'inactive':
      return '#f5222d' // Red
    case 'pending':
      return '#faad14' // Orange
    case 'maintenance':
      return '#722ed1' // Purple
    default:
      return '#d9d9d9' // Gray
  }
})

const statusIcon = computed(() => {
  switch (props.hotspot.status?.toLowerCase()) {
    case 'active':
      return WifiOutlined
    case 'inactive':
      return CloseCircleOutlined
    case 'pending':
      return ExclamationCircleOutlined
    case 'maintenance':
      return EnvironmentOutlined
    default:
      return QuestionCircleOutlined
  }
})

const statusText = computed(() => {
  switch (props.hotspot.status?.toLowerCase()) {
    case 'active':
      return '活跃'
    case 'inactive':
      return '非活跃'
    case 'pending':
      return '待处理'
    case 'maintenance':
      return '维护中'
    default:
      return '未知'
  }
})

const coordinateText = computed(() => {
  if (props.hotspot.coordinates) {
    const { latitude, longitude } = props.hotspot.coordinates
    return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
  }
  return props.hotspot.geocode || '无坐标'
})

// Methods
const handleClick = () => {
  if (props.clickable) {
    emit('click', props.hotspot)
  }
}

const handleMouseEnter = () => {
  hovered.value = true
  emit('hover', props.hotspot)
}

const handleMouseLeave = () => {
  hovered.value = false
  emit('leave', props.hotspot)
}

const getSizeValue = (size: string): number => {
  switch (size) {
    case 'small':
      return 20
    case 'large':
      return 40
    default: // medium
      return 30
  }
}
</script>

<style scoped>
.hotspot-marker {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  border: 2px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  cursor: default;
  z-index: 100;
}

.hotspot-marker--clickable {
  cursor: pointer;
}

.hotspot-marker--clickable:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.hotspot-marker--selected {
  border-width: 3px;
  z-index: 200;
}

.hotspot-marker--hovered {
  z-index: 150;
}

/* Size variants */
.hotspot-marker--small {
  font-size: 12px;
}

.hotspot-marker--medium {
  font-size: 14px;
}

.hotspot-marker--large {
  font-size: 16px;
}

/* Status variants */
.hotspot-marker--active {
  border-color: #52c41a;
  background: #f6ffed;
}

.hotspot-marker--inactive {
  border-color: #f5222d;
  background: #fff2f0;
}

.hotspot-marker--pending {
  border-color: #faad14;
  background: #fffbe6;
}

.hotspot-marker--maintenance {
  border-color: #722ed1;
  background: #f9f0ff;
}

.marker-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.marker-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  white-space: nowrap;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  margin-top: 4px;
  z-index: 10;
}

.marker-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  z-index: 1000;
}

.tooltip-content {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.tooltip-content h4 {
  margin: 0 0 4px 0;
  font-size: 13px;
  font-weight: 600;
}

.tooltip-content p {
  margin: 2px 0;
  line-height: 1.3;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.8);
}

.selection-ring {
  position: absolute;
  top: -6px;
  left: -6px;
  right: -6px;
  bottom: -6px;
  border: 2px solid #1890ff;
  border-radius: 50%;
  animation: selection-pulse 2s infinite;
}

@keyframes selection-pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.pulse-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 2px solid #52c41a;
  border-radius: 50%;
  opacity: 0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.7;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(1.5);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .hotspot-marker {
    transform: scale(0.9);
  }
  
  .tooltip-content {
    font-size: 11px;
    padding: 6px 10px;
  }
  
  .marker-label {
    font-size: 10px;
    padding: 1px 4px;
  }
}
</style>