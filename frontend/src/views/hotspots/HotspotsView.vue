<template>
  <div class="hotspot-management">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <WifiIcon class="title-icon" />
            Hotspot Management
          </h1>
          <p class="page-description">
            Manage WiFi hotspot locations, configurations, and contact information
          </p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-primary"
            @click="openCreateModal"
          >
            <PlusIcon class="btn-icon" />
            Add Hotspot
          </button>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid" v-if="statistics">
      <div class="stat-card">
        <div class="stat-icon">
          <WifiIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.total_hotspots }}</div>
          <div class="stat-label">Total Hotspots</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <ClockIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.recent_hotspots }}</div>
          <div class="stat-label">Recent (30 days)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <TagIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.unique_types }}</div>
          <div class="stat-label">Unique Types</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <BuildingOfficeIcon />
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ statistics.unique_companies }}</div>
          <div class="stat-label">Companies</div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="search-filters">
        <div class="filter-group">
          <label>Search</label>
          <div class="search-input">
            <MagnifyingGlassIcon class="search-icon" />
            <input
              v-model="filters.query"
              type="text"
              placeholder="Search by name, MAC, owner, company..."
              @input="debouncedSearch"
            />
            <button 
              v-if="filters.query"
              class="clear-search"
              @click="clearSearch"
            >
              <XMarkIcon />
            </button>
          </div>
        </div>
        
        <div class="filter-group">
          <label>Type</label>
          <select v-model="filters.type" @change="applyFilters">
            <option value="">All Types</option>
            <option v-for="type in options?.types || []" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Owner</label>
          <select v-model="filters.owner" @change="applyFilters">
            <option value="">All Owners</option>
            <option v-for="owner in options?.owners || []" :key="owner" :value="owner">
              {{ owner }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Company</label>
          <select v-model="filters.company" @change="applyFilters">
            <option value="">All Companies</option>
            <option v-for="company in options?.companies || []" :key="company" :value="company">
              {{ company }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="filter-actions">
        <button class="btn btn-secondary" @click="resetFilters">
          <ArrowPathIcon class="btn-icon" />
          Reset
        </button>
        <button class="btn btn-secondary" @click="exportHotspots">
          <ArrowDownTrayIcon class="btn-icon" />
          Export
        </button>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedHotspots.length > 0" class="bulk-actions">
      <div class="bulk-info">
        <span>{{ selectedHotspots.length }} hotspot(s) selected</span>
      </div>
      <div class="bulk-buttons">
        <button 
          class="btn btn-danger"
          @click="confirmBulkDelete"
        >
          <TrashIcon class="btn-icon" />
          Delete Selected
        </button>
      </div>
    </div>

    <!-- Hotspots Table -->
    <div class="table-container">
      <div class="table-header">
        <h3>Hotspots ({{ pagination.total }})</h3>
        <div class="table-controls">
          <select v-model="pagination.per_page" @change="changePageSize">
            <option value="10">10 per page</option>
            <option value="20">20 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        </div>
      </div>
      
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="checkbox-column">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleAllSelection"
                />
              </th>
              <th 
                v-for="column in tableColumns" 
                :key="column.key"
                :class="{ sortable: column.sortable, [column.align || 'left']: true }"
                :style="{ width: column.width }"
                @click="column.sortable ? sortBy(column.key) : null"
              >
                {{ column.title }}
                <template v-if="column.sortable">
                  <ChevronUpIcon 
                    v-if="sort.field === column.key && sort.direction === 'asc'"
                    class="sort-icon"
                  />
                  <ChevronDownIcon 
                    v-else-if="sort.field === column.key && sort.direction === 'desc'"
                    class="sort-icon"
                  />
                  <div v-else class="sort-placeholder"></div>
                </template>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="loading-row">
              <td :colspan="tableColumns.length + 1" class="loading-cell">
                <div class="loading-spinner"></div>
                Loading hotspots...
              </td>
            </tr>
            <tr v-else-if="hotspots.length === 0" class="empty-row">
              <td :colspan="tableColumns.length + 1" class="empty-cell">
                <div class="empty-state">
                  <WifiIcon class="empty-icon" />
                  <h3>No hotspots found</h3>
                  <p v-if="hasActiveFilters">
                    Try adjusting your search criteria or 
                    <button class="link-button" @click="resetFilters">reset filters</button>
                  </p>
                  <p v-else>
                    <button class="btn btn-primary" @click="openCreateModal">
                      Create your first hotspot
                    </button>
                  </p>
                </div>
              </td>
            </tr>
            <tr 
              v-else
              v-for="hotspot in hotspots" 
              :key="hotspot.id"
              class="data-row"
              :class="{ selected: selectedHotspots.includes(hotspot.id) }"
            >
              <td class="checkbox-column">
                <input
                  type="checkbox"
                  :checked="selectedHotspots.includes(hotspot.id)"
                  @change="toggleSelection(hotspot.id)"
                />
              </td>
              <td>{{ hotspot.id }}</td>
              <td>
                <div class="hotspot-name">
                  <WifiIcon class="hotspot-icon" />
                  <span>{{ hotspot.name }}</span>
                </div>
              </td>
              <td>
                <code class="mac-address">{{ hotspot.mac }}</code>
              </td>
              <td>
                <span v-if="hotspot.type" class="type-badge">
                  {{ hotspot.type }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <div v-if="hotspot.owner" class="owner-info">
                  <div class="owner-name">{{ hotspot.owner }}</div>
                  <div v-if="hotspot.email_owner" class="owner-email">
                    {{ hotspot.email_owner }}
                  </div>
                </div>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="hotspot.company">{{ hotspot.company }}</span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="hotspot.address" class="address-text">
                  {{ hotspot.address }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="hotspot.creationdate" class="date-text">
                  {{ formatDate(hotspot.creationdate) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="actions-column">
                <div class="action-buttons">
                  <button
                    class="btn-icon btn-icon-secondary"
                    @click="viewHotspot(hotspot)"
                    title="View Details"
                  >
                    <EyeIcon />
                  </button>
                  <button
                    class="btn-icon btn-icon-primary"
                    @click="editHotspot(hotspot)"
                    title="Edit"
                  >
                    <PencilIcon />
                  </button>
                  <button
                    class="btn-icon btn-icon-danger"
                    @click="confirmDelete(hotspot)"
                    title="Delete"
                  >
                    <TrashIcon />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.pages > 1" class="pagination-container">
      <div class="pagination-info">
        Showing {{ (pagination.page - 1) * pagination.per_page + 1 }} 
        to {{ Math.min(pagination.page * pagination.per_page, pagination.total) }} 
        of {{ pagination.total }} results
      </div>
      <div class="pagination-controls">
        <button 
          class="btn btn-secondary"
          :disabled="pagination.page === 1"
          @click="goToPage(pagination.page - 1)"
        >
          <ChevronLeftIcon class="btn-icon" />
          Previous
        </button>
        
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: page === pagination.page }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          class="btn btn-secondary"
          :disabled="pagination.page === pagination.pages"
          @click="goToPage(pagination.page + 1)"
        >
          Next
          <ChevronRightIcon class="btn-icon" />
        </button>
      </div>
    </div>

    <!-- Modals -->
    <HotspotModal
      v-if="showModal"
      :hotspot="selectedHotspot"
      :mode="modalMode"
      @close="closeModal"
      @save="handleSave"
    />
    
    <ConfirmDialog
      v-if="showDeleteConfirm"
      :title="deleteConfirm.title"
      :message="deleteConfirm.message"
      :type="deleteConfirm.type"
      @confirm="handleDeleteConfirm"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { debounce } from 'lodash-es'
import { 
  WifiIcon,
  PlusIcon,
  ClockIcon,
  TagIcon,
  BuildingOfficeIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  EyeIcon,
  PencilIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

import { HotspotService } from '@/services/hotspots/hotspotService'
import HotspotModal from '@/components/hotspots/HotspotModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

import type {
  Hotspot,
  HotspotFilters,
  HotspotSort,
  HotspotPagination,
  HotspotFormMode,
  HotspotStatisticsResponse,
  HotspotOptionsResponse
} from '@/types/hotspot'

import {
  HOTSPOT_TABLE_COLUMNS,
  DEFAULT_HOTSPOT_FILTERS,
  DEFAULT_HOTSPOT_SORT,
  DEFAULT_HOTSPOT_PAGINATION
} from '@/types/hotspot'

// State
const loading = ref(false)
const hotspots = ref<Hotspot[]>([])
const statistics = ref<HotspotStatisticsResponse | null>(null)
const options = ref<HotspotOptionsResponse | null>(null)
const selectedHotspots = ref<number[]>([])

// Filters and sorting
const filters = reactive<HotspotFilters>({ ...DEFAULT_HOTSPOT_FILTERS })
const sort = reactive<HotspotSort>({ ...DEFAULT_HOTSPOT_SORT })
const pagination = reactive<HotspotPagination>({ ...DEFAULT_HOTSPOT_PAGINATION })

// Modal state
const showModal = ref(false)
const modalMode = ref<HotspotFormMode>('create')
const selectedHotspot = ref<Hotspot | null>(null)

// Delete confirmation
const showDeleteConfirm = ref(false)
const deleteConfirm = reactive({
  title: '',
  message: '',
  type: 'danger' as const,
  action: null as (() => void) | null
})

// Table configuration
const tableColumns = HOTSPOT_TABLE_COLUMNS.filter(col => col.key !== 'actions')

// Computed properties
const hasActiveFilters = computed(() => {
  return filters.query || filters.type || filters.owner || filters.company
})

const isAllSelected = computed(() => {
  return hotspots.value.length > 0 && selectedHotspots.value.length === hotspots.value.length
})

const visiblePages = computed(() => {
  const current = pagination.page
  const total = pagination.pages
  const delta = 2
  const pages: number[] = []
  
  for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
const loadHotspots = async () => {
  try {
    loading.value = true
    const response = await HotspotService.getHotspots({
      ...filters,
      page: pagination.page,
      per_page: pagination.per_page,
      order_by: sort.field,
      order_type: sort.direction
    })
    
    hotspots.value = response.hotspots
    pagination.total = response.total
    pagination.pages = response.pages
  } catch (error) {
    console.error('Error loading hotspots:', error)
    // Handle error notification here
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    statistics.value = await HotspotService.getStatistics()
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
}

const loadOptions = async () => {
  try {
    options.value = await HotspotService.getOptions()
  } catch (error) {
    console.error('Error loading options:', error)
  }
}

const debouncedSearch = debounce(() => {
  pagination.page = 1
  loadHotspots()
}, 300)

const applyFilters = () => {
  pagination.page = 1
  loadHotspots()
}

const resetFilters = () => {
  Object.assign(filters, { ...DEFAULT_HOTSPOT_FILTERS })
  pagination.page = 1
  loadHotspots()
}

const clearSearch = () => {
  filters.query = ''
  applyFilters()
}

const sortBy = (field: string) => {
  if (sort.field === field) {
    sort.direction = sort.direction === 'asc' ? 'desc' : 'asc'
  } else {
    sort.field = field
    sort.direction = 'asc'
  }
  loadHotspots()
}

const goToPage = (page: number) => {
  pagination.page = page
  loadHotspots()
}

const changePageSize = () => {
  pagination.page = 1
  loadHotspots()
}

// Selection methods
const toggleSelection = (id: number) => {
  const index = selectedHotspots.value.indexOf(id)
  if (index > -1) {
    selectedHotspots.value.splice(index, 1)
  } else {
    selectedHotspots.value.push(id)
  }
}

const toggleAllSelection = () => {
  if (isAllSelected.value) {
    selectedHotspots.value = []
  } else {
    selectedHotspots.value = hotspots.value.map(h => h.id)
  }
}

// Modal methods
const openCreateModal = () => {
  selectedHotspot.value = null
  modalMode.value = 'create'
  showModal.value = true
}

const viewHotspot = (hotspot: Hotspot) => {
  selectedHotspot.value = hotspot
  modalMode.value = 'view'
  showModal.value = true
}

const editHotspot = (hotspot: Hotspot) => {
  selectedHotspot.value = hotspot
  modalMode.value = 'edit'
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedHotspot.value = null
}

const handleSave = () => {
  closeModal()
  loadHotspots()
  loadStatistics() // Refresh statistics
  if (modalMode.value === 'create') {
    loadOptions() // Refresh options if new data might have been added
  }
}

// Delete methods
const confirmDelete = (hotspot: Hotspot) => {
  deleteConfirm.title = 'Delete Hotspot'
  deleteConfirm.message = `Are you sure you want to delete "${hotspot.name}"? This action cannot be undone.`
  deleteConfirm.type = 'danger'
  deleteConfirm.action = () => deleteHotspot(hotspot.id)
  showDeleteConfirm.value = true
}

const confirmBulkDelete = () => {
  deleteConfirm.title = 'Delete Selected Hotspots'
  deleteConfirm.message = `Are you sure you want to delete ${selectedHotspots.value.length} selected hotspot(s)? This action cannot be undone.`
  deleteConfirm.type = 'danger'
  deleteConfirm.action = bulkDelete
  showDeleteConfirm.value = true
}

const handleDeleteConfirm = () => {
  if (deleteConfirm.action) {
    deleteConfirm.action()
  }
  showDeleteConfirm.value = false
}

const deleteHotspot = async (id: number) => {
  try {
    await HotspotService.deleteHotspot(id)
    loadHotspots()
    loadStatistics()
    // Show success notification
  } catch (error) {
    console.error('Error deleting hotspot:', error)
    // Show error notification
  }
}

const bulkDelete = async () => {
  try {
    await HotspotService.bulkDelete(selectedHotspots.value)
    selectedHotspots.value = []
    loadHotspots()
    loadStatistics()
    // Show success notification
  } catch (error) {
    console.error('Error bulk deleting hotspots:', error)
    // Show error notification
  }
}

// Export method
const exportHotspots = async () => {
  try {
    const data = await HotspotService.exportHotspots(filters)
    // Implement CSV/Excel export logic here
    console.log('Exporting hotspots:', data)
  } catch (error) {
    console.error('Error exporting hotspots:', error)
  }
}

// Utility methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadHotspots(),
    loadStatistics(),
    loadOptions()
  ])
})

// Watch for filter changes
watch(filters, () => {
  debouncedSearch()
})
</script>

<style scoped>
.hotspot-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.title-icon {
  width: 36px;
  height: 36px;
  color: #3b82f6;
}

.page-description {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Statistics Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
  color: #6b7280;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

/* Filters */
.filters-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
}

.search-filters {
  display: flex;
  gap: 20px;
  flex: 1;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 20px;
  height: 20px;
  color: #9ca3af;
}

.search-input input {
  padding: 10px 12px 10px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  width: 300px;
}

.clear-search {
  position: absolute;
  right: 8px;
  padding: 4px;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
}

.clear-search:hover {
  color: #6b7280;
}

.clear-search svg {
  width: 16px;
  height: 16px;
}

.filter-group select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  min-width: 160px;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

/* Bulk Actions */
.bulk-actions {
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  padding: 16px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bulk-info {
  color: #92400e;
  font-weight: 500;
}

.bulk-buttons {
  display: flex;
  gap: 12px;
}

/* Table */
.table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.table-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.table-controls select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.data-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.data-table th.sortable:hover {
  background: #f3f4f6;
}

.sort-icon,
.sort-placeholder {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
}

.sort-icon {
  color: #6b7280;
}

.checkbox-column {
  width: 40px;
  text-align: center;
}

.data-row:hover {
  background: #f9fafb;
}

.data-row.selected {
  background: #eff6ff;
}

.loading-row,
.empty-row {
  background: #f9fafb;
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 48px 24px;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  color: #6b7280;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #d1d5db;
  margin: 0 auto 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-state p {
  margin: 0;
}

.link-button {
  background: none;
  border: none;
  color: #3b82f6;
  text-decoration: underline;
  cursor: pointer;
}

/* Table Content */
.hotspot-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hotspot-icon {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.mac-address {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.type-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.owner-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.owner-name {
  font-weight: 500;
}

.owner-email {
  font-size: 12px;
  color: #6b7280;
}

.address-text {
  max-width: 200px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.date-text {
  font-size: 13px;
  color: #6b7280;
}

.text-muted {
  color: #9ca3af;
  font-style: italic;
}

.actions-column {
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

/* Pagination */
.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  color: #6b7280;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover {
  background: #f9fafb;
}

.page-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Common Button Styles */
.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-icon {
  padding: 8px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon svg {
  width: 16px;
  height: 16px;
}

.btn-icon-primary {
  background: #eff6ff;
  color: #3b82f6;
}

.btn-icon-primary:hover {
  background: #dbeafe;
}

.btn-icon-secondary {
  background: #f3f4f6;
  color: #6b7280;
}

.btn-icon-secondary:hover {
  background: #e5e7eb;
}

.btn-icon-danger {
  background: #fef2f2;
  color: #ef4444;
}

.btn-icon-danger:hover {
  background: #fee2e2;
}

/* Responsive */
@media (max-width: 768px) {
  .hotspot-management {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters {
    flex-direction: column;
  }
  
  .search-input input {
    width: 100%;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .table-wrapper {
    font-size: 14px;
  }
  
  .address-text {
    max-width: 150px;
  }
}
</style>