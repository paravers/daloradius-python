/**
 * RADIUS Attributes Type Definitions
 * 
 * This file defines TypeScript interfaces for RADIUS check and reply attributes
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

// ===== Base Interfaces =====

/**
 * Base RADIUS attribute interface
 */
export interface BaseRadiusAttribute {
  id?: number;
  username: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
  created_at?: string;
  updated_at?: string;
}

// ===== RadCheck Interfaces =====

/**
 * RadCheck attribute for user authentication
 */
export interface RadCheck extends BaseRadiusAttribute {
  // Inherits all properties from BaseRadiusAttribute
}

/**
 * RadCheck creation data
 */
export interface RadCheckCreate {
  username: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
}

/**
 * RadCheck update data
 */
export interface RadCheckUpdate {
  attribute?: string;
  op?: RadiusOperator;
  value?: string;
}

// ===== RadReply Interfaces =====

/**
 * RadReply attribute for user authorization
 */
export interface RadReply extends BaseRadiusAttribute {
  // Inherits all properties from BaseRadiusAttribute  
}

/**
 * RadReply creation data
 */
export interface RadReplyCreate {
  username: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
}

/**
 * RadReply update data
 */
export interface RadReplyUpdate {
  attribute?: string;
  op?: RadiusOperator;
  value?: string;
}

// ===== Combined User Attributes =====

/**
 * Complete user attributes (RadCheck + RadReply)
 */
export interface UserAttributes {
  username: string;
  check_attributes: RadCheck[];
  reply_attributes: RadReply[];
  total_attributes: number;
}

/**
 * Password update data
 */
export interface PasswordUpdate {
  password: string;
  password_type?: string;
}

// ===== Common Attribute Lists =====

/**
 * Common RadCheck attribute names grouped by category
 */
export interface CommonCheckAttributes {
  password_attributes: string[];
  access_control: string[];
}

/**
 * Common RadReply attribute names grouped by category  
 */
export interface CommonReplyAttributes {
  networking: string[];
  service_control: string[];
  other: string[];
}

// ===== Search and Filter Interfaces =====

/**
 * RADIUS attribute search parameters
 */
export interface RadiusSearchParams {
  username?: string;
  attribute?: string;
  search?: string;
  page?: number;
  size?: number;
}

/**
 * RADIUS attribute filter options
 */
export interface RadiusFilterOptions {
  operators: RadiusOperator[];
  attributes: string[];
  users: string[];
}

// ===== API Response Interfaces =====

/**
 * Paginated RADIUS attributes response
 */
export interface PaginatedRadiusResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * RADIUS API error response
 */
export interface RadiusApiError {
  detail: string;
  status_code: number;
}

/**
 * RADIUS operation result
 */
export interface RadiusOperationResult {
  success: boolean;
  message: string;
  data?: any;
}

// ===== Form Interfaces =====

/**
 * RADIUS attribute form data
 */
export interface RadiusAttributeForm {
  username: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
  type: 'check' | 'reply';
}

/**
 * RADIUS attribute form validation
 */
export interface RadiusAttributeFormValidation {
  username?: string;
  attribute?: string;
  value?: string;
}

// ===== Statistics Interfaces =====

/**
 * RADIUS attributes statistics
 */
export interface RadiusAttributeStats {
  total_check_attributes: number;
  total_reply_attributes: number;
  unique_users: number;
  unique_attributes: number;
  most_used_attributes: Array<{
    attribute: string;
    count: number;
  }>;
}

// ===== Table Column Interfaces =====

/**
 * RADIUS attribute table column definition
 */
export interface RadiusAttributeColumn {
  key: string;
  title: string;
  dataIndex: string;
  width?: number;
  fixed?: 'left' | 'right';
  sorter?: boolean;
  filterable?: boolean;
}

// ===== All types are exported above as interfaces and can be imported directly =====