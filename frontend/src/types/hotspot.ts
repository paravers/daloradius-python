/**
 * Hotspot Types
 * 
 * TypeScript type definitions for hotspot management.
 * Defines interfaces for hotspot entities and related operations.
 */

export interface Hotspot {
  id: number
  name: string
  mac: string
  geocode?: string | null
  type?: string | null
  
  // Owner information
  owner?: string | null
  email_owner?: string | null
  
  // Manager information
  manager?: string | null
  email_manager?: string | null
  
  // Location and contact details
  address?: string | null
  phone1?: string | null
  phone2?: string | null
  
  // Company information
  company?: string | null
  companywebsite?: string | null
  companyemail?: string | null
  companycontact?: string | null
  companyphone?: string | null
  
  // Audit fields
  creationdate?: string | null
  creationby?: string | null
  updatedate?: string | null
  updateby?: string | null
}

export interface HotspotCreate {
  name: string
  mac: string
  geocode?: string
  type?: string
  
  // Owner information
  owner?: string
  email_owner?: string
  
  // Manager information
  manager?: string
  email_manager?: string
  
  // Location and contact details
  address?: string
  phone1?: string
  phone2?: string
  
  // Company information
  company?: string
  companywebsite?: string
  companyemail?: string
  companycontact?: string
  companyphone?: string
}

export interface HotspotUpdate {
  name?: string
  mac?: string
  geocode?: string
  type?: string
  
  // Owner information
  owner?: string
  email_owner?: string
  
  // Manager information
  manager?: string
  email_manager?: string
  
  // Location and contact details
  address?: string
  phone1?: string
  phone2?: string
  
  // Company information
  company?: string
  companywebsite?: string
  companyemail?: string
  companycontact?: string
  companyphone?: string
}

export interface HotspotListResponse {
  hotspots: Hotspot[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface HotspotSearchRequest {
  query?: string
  type?: string
  owner?: string
  company?: string
  page: number
  per_page: number
  order_by: string
  order_type: 'asc' | 'desc'
}

export interface HotspotValidationResponse {
  valid: boolean
  message?: string
}

export interface HotspotBulkDeleteResponse {
  deleted_count: number
  message: string
}

export interface HotspotStatisticsResponse {
  total_hotspots: number
  recent_hotspots: number
  unique_types: number
  unique_companies: number
  unique_owners: number
  types_distribution: Record<string, number>
}

export interface HotspotOptionsResponse {
  types: string[]
  companies: string[]
  owners: string[]
}

// Form-related types
export interface HotspotFormData extends Omit<HotspotCreate, 'name' | 'mac'> {
  name: string
  mac: string
}

export interface HotspotFormErrors {
  name?: string
  mac?: string
  email_owner?: string
  email_manager?: string
  companyemail?: string
  companywebsite?: string
  [key: string]: string | undefined
}

// Table column types
export interface HotspotTableColumn {
  key: string
  title: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
}

// Filter types
export interface HotspotFilters {
  query: string
  type: string
  owner: string
  company: string
}

// Sort types
export interface HotspotSort {
  field: string
  direction: 'asc' | 'desc'
}

// Pagination types
export interface HotspotPagination {
  page: number
  per_page: number
  total: number
  pages: number
}

// Action types for hotspot management
export type HotspotAction = 
  | 'create'
  | 'edit'
  | 'delete'
  | 'view'
  | 'bulk_delete'
  | 'export'

// Form mode types
export type HotspotFormMode = 'create' | 'edit' | 'view'

// Export formats
export type ExportFormat = 'csv' | 'excel' | 'json'

// Default values
export const DEFAULT_HOTSPOT_FILTERS: HotspotFilters = {
  query: '',
  type: '',
  owner: '',
  company: ''
}

export const DEFAULT_HOTSPOT_SORT: HotspotSort = {
  field: 'name',
  direction: 'asc'
}

export const DEFAULT_HOTSPOT_PAGINATION: HotspotPagination = {
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
}

export const HOTSPOT_TABLE_COLUMNS: HotspotTableColumn[] = [
  { key: 'id', title: 'ID', sortable: true, width: '80px', align: 'center' },
  { key: 'name', title: 'Hotspot Name', sortable: true },
  { key: 'mac', title: 'MAC/IP Address', sortable: true },
  { key: 'type', title: 'Type', sortable: true },
  { key: 'owner', title: 'Owner', sortable: true },
  { key: 'company', title: 'Company', sortable: true },
  { key: 'address', title: 'Address', sortable: false },
  { key: 'creationdate', title: 'Created', sortable: true, width: '120px' },
  { key: 'actions', title: 'Actions', sortable: false, width: '120px', align: 'center' }
]

// Validation rules
export const HOTSPOT_VALIDATION_RULES = {
  name: {
    required: true,
    minLength: 1,
    maxLength: 200,
    pattern: /^[^%]*$/,
    message: 'Hotspot name is required and cannot contain % characters'
  },
  mac: {
    required: true,
    minLength: 1,
    maxLength: 200,
    patterns: [
      /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/, // XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
      /^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$/, // XXXX.XXXX.XXXX
      /^([0-9A-Fa-f]{12})$/, // XXXXXXXXXXXX
      /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/ // IP address
    ],
    message: 'Must be a valid MAC address or IP address'
  },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: 'Must be a valid email address'
  },
  website: {
    pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
    message: 'Must be a valid website URL'
  }
}