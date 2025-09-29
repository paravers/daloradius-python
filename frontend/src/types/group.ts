/**
 * RADIUS Group Management Type Definitions
 * 
 * This file defines TypeScript interfaces for RADIUS group check and reply attributes
 * used throughout the frontend application.
 */

// ===== Enums =====

/**
 * RADIUS attribute operators
 */
export enum RadiusOperator {
  EQUAL = '==',
  NOT_EQUAL = '!=',
  SET = ':=',
  ADD = '+=',
  SUBTRACT = '-=',
  LESS_THAN = '<',
  LESS_EQUAL = '<=',
  GREATER_THAN = '>',
  GREATER_EQUAL = '>=',
  REGEX_MATCH = '=~',
  REGEX_NOT_MATCH = '!~'
}

/**
 * Group attribute types
 */
export enum GroupAttributeType {
  CHECK = 'check',
  REPLY = 'reply'
}

// ===== Base Interfaces =====

/**
 * Base RADIUS group attribute interface
 */
export interface BaseGroupAttribute {
  id?: number;
  groupname: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
  created_at?: string;
  updated_at?: string;
}

// ===== RadGroupCheck Interfaces =====

/**
 * RadGroupCheck attribute for group authentication
 */
export interface RadGroupCheck extends BaseGroupAttribute {
  // Inherits all properties from BaseGroupAttribute
}

/**
 * RadGroupCheck creation data
 */
export interface RadGroupCheckCreate {
  groupname: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
}

/**
 * RadGroupCheck update data
 */
export interface RadGroupCheckUpdate {
  groupname?: string;
  attribute?: string;
  op?: RadiusOperator;
  value?: string;
}

// ===== RadGroupReply Interfaces =====

/**
 * RadGroupReply attribute for group authorization
 */
export interface RadGroupReply extends BaseGroupAttribute {
  // Inherits all properties from BaseGroupAttribute
}

/**
 * RadGroupReply creation data
 */
export interface RadGroupReplyCreate {
  groupname: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
}

/**
 * RadGroupReply update data
 */
export interface RadGroupReplyUpdate {
  groupname?: string;
  attribute?: string;
  op?: RadiusOperator;
  value?: string;
}

// ===== Combined Group Interfaces =====

/**
 * Complete group attributes (RadGroupCheck + RadGroupReply)
 */
export interface GroupAttributes {
  groupname: string;
  check_attributes: RadGroupCheck[];
  reply_attributes: RadGroupReply[];
  total_attributes: number;
}

/**
 * Group information summary
 */
export interface GroupSummary {
  groupname: string;
  check_count: number;
  reply_count: number;
  total_count: number;
  last_modified?: string;
}

// ===== API Response Interfaces =====

/**
 * Paginated RADIUS group attributes response
 */
export interface PaginatedGroupAttributesResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Group list response
 */
export interface GroupListResponse {
  groups: string[];
  total: number;
}

/**
 * Group statistics response
 */
export interface GroupStatisticsResponse {
  total_groups: number;
  total_check_attributes: number;
  total_reply_attributes: number;
  groups_with_attributes: number;
}

/**
 * Group deletion response
 */
export interface GroupDeletionResponse {
  message: string;
  check_attributes_deleted: number;
  reply_attributes_deleted: number;
}

// ===== Search and Filter Interfaces =====

/**
 * RADIUS group attribute search parameters
 */
export interface GroupAttributeSearchParams {
  groupname?: string;
  attribute?: string;
  search?: string;
  page?: number;
  size?: number;
}

/**
 * RADIUS group attribute filter options
 */
export interface GroupAttributeFilterOptions {
  groupnames: string[];
  attribute_types: string[];
  operators: RadiusOperator[];
}

/**
 * Group attribute table column configuration
 */
export interface GroupAttributeTableColumn {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number;
  fixed?: 'left' | 'right';
  sorter?: boolean | ((a: any, b: any) => number);
  filterable?: boolean;
  searchable?: boolean;
}

// ===== Form and UI Interfaces =====

/**
 * Group attribute form data
 */
export interface GroupAttributeFormData {
  groupname: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
  type: GroupAttributeType;
}

/**
 * Group attribute validation result
 */
export interface ValidationResult {
  isValid: boolean;
  message: string;
  field?: string;
}

/**
 * Group attribute template
 */
export interface GroupAttributeTemplate {
  name: string;
  description: string;
  type: GroupAttributeType;
  attributes: Array<{
    attribute: string;
    op: RadiusOperator;
    value: string;
    description?: string;
  }>;
}

/**
 * Batch operation configuration
 */
export interface BatchOperationConfig {
  operation: 'create' | 'update' | 'delete';
  groupname: string;
  attributes: GroupAttributeFormData[];
  validation_enabled: boolean;
  continue_on_error: boolean;
}

/**
 * Batch operation result
 */
export interface BatchOperationResult {
  groupname: string;
  total_requested: number;
  created: number;
  updated?: number;
  deleted?: number;
  failed: number;
  errors: string[];
  success_rate: number;
}

// ===== Utility Interfaces =====

/**
 * Common RADIUS attributes by category
 */
export interface CommonRadiusAttributes {
  check_attributes: {
    authentication: string[];
    access_control: string[];
    other: string[];
  };
  reply_attributes: {
    networking: string[];
    service_control: string[];
    other: string[];
  };
}

/**
 * Operator information
 */
export interface OperatorInfo {
  value: RadiusOperator;
  label: string;
  description: string;
  category: 'comparison' | 'assignment' | 'arithmetic' | 'pattern';
}

/**
 * Group attribute export configuration
 */
export interface ExportConfig {
  format: 'json' | 'csv' | 'xml';
  include_metadata: boolean;
  filter_by_group?: string;
  filter_by_type?: GroupAttributeType;
}

/**
 * Group attribute import configuration
 */
export interface ImportConfig {
  format: 'json' | 'csv';
  validation_enabled: boolean;
  overwrite_existing: boolean;
  create_missing_groups: boolean;
}

// ===== Constants =====

/**
 * Default pagination settings
 */
export const DEFAULT_PAGINATION = {
  page: 1,
  size: 20,
  pageSizeOptions: ['10', '20', '50', '100']
};

/**
 * Table column configurations
 */
export const GROUP_ATTRIBUTE_COLUMNS: GroupAttributeTableColumn[] = [
  {
    key: 'groupname',
    title: 'Group Name',
    dataIndex: 'groupname',
    width: 150,
    sorter: true,
    filterable: true,
    searchable: true
  },
  {
    key: 'attribute',
    title: 'Attribute',
    dataIndex: 'attribute',
    width: 200,
    sorter: true,
    filterable: true,
    searchable: true
  },
  {
    key: 'op',
    title: 'Operator',
    dataIndex: 'op',
    width: 100,
    sorter: true,
    filterable: true
  },
  {
    key: 'value',
    title: 'Value',
    dataIndex: 'value',
    width: 200,
    sorter: false,
    searchable: true
  },
  {
    key: 'created_at',
    title: 'Created',
    dataIndex: 'created_at',
    width: 150,
    sorter: true
  },
  {
    key: 'actions',
    title: 'Actions',
    width: 120,
    fixed: 'right'
  }
];

