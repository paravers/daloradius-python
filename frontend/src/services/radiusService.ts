/**
 * RADIUS Attributes Service
 * 
 * This service handles all API communications for RADIUS check and reply attributes,
 * providing a clean interface between the frontend and the backend API.
 */

import { api } from './api';
import type {
  RadCheck,
  RadCheckCreate,
  RadCheckUpdate,
  RadReply,
  RadReplyCreate,
  RadReplyUpdate,
  UserAttributes,
  PasswordUpdate,
  RadiusSearchParams,
  PaginatedRadiusResponse,
  CommonCheckAttributes,
  CommonReplyAttributes,
  RadiusOperator
} from '@/types/radius';

// ===== RadCheck Service Methods =====

/**
 * Get paginated list of RadCheck attributes
 */
export const getRadCheckAttributes = async (
  params: RadiusSearchParams = {}
): Promise<PaginatedRadiusResponse<RadCheck>> => {
  const response = await api.get('/radius/radcheck', { params });
  return response.data;
};

/**
 * Get specific RadCheck attribute by ID
 */
export const getRadCheckAttribute = async (id: number): Promise<RadCheck> => {
  const response = await api.get(`/radius/radcheck/${id}`);
  return response.data;
};

/**
 * Create new RadCheck attribute
 */
export const createRadCheckAttribute = async (
  data: RadCheckCreate
): Promise<RadCheck> => {
  const response = await api.post('/radius/radcheck', data);
  return response.data;
};

/**
 * Update existing RadCheck attribute
 */
export const updateRadCheckAttribute = async (
  id: number,
  data: RadCheckUpdate
): Promise<RadCheck> => {
  const response = await api.put(`/radius/radcheck/${id}`, data);
  return response.data;
};

/**
 * Delete RadCheck attribute
 */
export const deleteRadCheckAttribute = async (id: number): Promise<void> => {
  await api.delete(`/radius/radcheck/${id}`);
};

// ===== RadReply Service Methods =====

/**
 * Get paginated list of RadReply attributes
 */
export const getRadReplyAttributes = async (
  params: RadiusSearchParams = {}
): Promise<PaginatedRadiusResponse<RadReply>> => {
  const response = await api.get('/radius/radreply', { params });
  return response.data;
};

/**
 * Get specific RadReply attribute by ID
 */
export const getRadReplyAttribute = async (id: number): Promise<RadReply> => {
  const response = await api.get(`/radius/radreply/${id}`);
  return response.data;
};

/**
 * Create new RadReply attribute
 */
export const createRadReplyAttribute = async (
  data: RadReplyCreate
): Promise<RadReply> => {
  const response = await api.post('/radius/radreply', data);
  return response.data;
};

/**
 * Update existing RadReply attribute
 */
export const updateRadReplyAttribute = async (
  id: number,
  data: RadReplyUpdate
): Promise<RadReply> => {
  const response = await api.put(`/radius/radreply/${id}`, data);
  return response.data;
};

/**
 * Delete RadReply attribute
 */
export const deleteRadReplyAttribute = async (id: number): Promise<void> => {
  await api.delete(`/radius/radreply/${id}`);
};

// ===== User-Specific Attribute Methods =====

/**
 * Get all attributes for a specific user
 */
export const getUserAttributes = async (username: string): Promise<UserAttributes> => {
  const response = await api.get(`/radius/users/${username}/attributes`);
  return response.data;
};

/**
 * Set or update user password
 */
export const setUserPassword = async (
  username: string,
  passwordData: PasswordUpdate
): Promise<{ message: string; attribute: RadCheck }> => {
  const response = await api.post(`/radius/users/${username}/password`, passwordData);
  return response.data;
};

// ===== Utility Methods =====

/**
 * Get available RADIUS operators
 */
export const getRadiusOperators = async (): Promise<string[]> => {
  const response = await api.get('/radius/attributes/operators');
  return response.data;
};

/**
 * Get common RadCheck attribute names
 */
export const getCommonCheckAttributes = async (): Promise<CommonCheckAttributes> => {
  const response = await api.get('/radius/attributes/common-check');
  return response.data;
};

/**
 * Get common RadReply attribute names  
 */
export const getCommonReplyAttributes = async (): Promise<CommonReplyAttributes> => {
  const response = await api.get('/radius/attributes/common-reply');
  return response.data;
};

// ===== Batch Operations =====

/**
 * Create multiple RadCheck attributes
 */
export const createMultipleRadCheckAttributes = async (
  attributes: RadCheckCreate[]
): Promise<RadCheck[]> => {
  const promises = attributes.map(attr => createRadCheckAttribute(attr));
  return await Promise.all(promises);
};

/**
 * Create multiple RadReply attributes
 */
export const createMultipleRadReplyAttributes = async (
  attributes: RadReplyCreate[]
): Promise<RadReply[]> => {
  const promises = attributes.map(attr => createRadReplyAttribute(attr));
  return await Promise.all(promises);
};

/**
 * Delete multiple RadCheck attributes
 */
export const deleteMultipleRadCheckAttributes = async (
  ids: number[]
): Promise<void> => {
  const promises = ids.map(id => deleteRadCheckAttribute(id));
  await Promise.all(promises);
};

/**
 * Delete multiple RadReply attributes
 */
export const deleteMultipleRadReplyAttributes = async (
  ids: number[]
): Promise<void> => {
  const promises = ids.map(id => deleteRadReplyAttribute(id));
  await Promise.all(promises);
};

// ===== Search and Filter Methods =====

/**
 * Search RadCheck attributes by username
 */
export const searchRadCheckByUsername = async (
  username: string,
  params: Omit<RadiusSearchParams, 'username'> = {}
): Promise<PaginatedRadiusResponse<RadCheck>> => {
  return await getRadCheckAttributes({ ...params, username });
};

/**
 * Search RadReply attributes by username
 */
export const searchRadReplyByUsername = async (
  username: string,
  params: Omit<RadiusSearchParams, 'username'> = {}
): Promise<PaginatedRadiusResponse<RadReply>> => {
  return await getRadReplyAttributes({ ...params, username });
};

/**
 * Search attributes by attribute name
 */
export const searchAttributesByName = async (
  attributeName: string,
  type: 'check' | 'reply' = 'check',
  params: Omit<RadiusSearchParams, 'attribute'> = {}
): Promise<PaginatedRadiusResponse<RadCheck | RadReply>> => {
  if (type === 'check') {
    return await getRadCheckAttributes({ ...params, attribute: attributeName });
  } else {
    return await getRadReplyAttributes({ ...params, attribute: attributeName });
  }
};

/**
 * Search all attributes with general search term
 */
export const searchAllAttributes = async (
  searchTerm: string,
  params: Omit<RadiusSearchParams, 'search'> = {}
): Promise<{
  check: PaginatedRadiusResponse<RadCheck>;
  reply: PaginatedRadiusResponse<RadReply>;
}> => {
  const [checkResults, replyResults] = await Promise.all([
    getRadCheckAttributes({ ...params, search: searchTerm }),
    getRadReplyAttributes({ ...params, search: searchTerm })
  ]);

  return {
    check: checkResults,
    reply: replyResults
  };
};

// ===== Validation Methods =====

/**
 * Validate attribute name format
 */
export const validateAttributeName = (attributeName: string): boolean => {
  // Basic validation for RADIUS attribute names
  const validPattern = /^[A-Za-z][A-Za-z0-9\-_]*$/;
  return validPattern.test(attributeName) && attributeName.length <= 64;
};

/**
 * Validate attribute value format
 */
export const validateAttributeValue = (value: string): boolean => {
  // Basic validation for attribute values
  return value.length > 0 && value.length <= 253;
};

/**
 * Validate username format
 */
export const validateUsername = (username: string): boolean => {
  // Basic validation for usernames
  const validPattern = /^[a-zA-Z0-9\-_@.]+$/;
  return validPattern.test(username) && username.length > 0 && username.length <= 64;
};

// ===== Constants =====

/**
 * Default pagination parameters
 */
export const DEFAULT_PAGINATION = {
  page: 1,
  size: 20
};

/**
 * Maximum items per page
 */
export const MAX_PAGE_SIZE = 100;

/**
 * Common password attribute types
 */
export const PASSWORD_ATTRIBUTES = [
  'User-Password',
  'Cleartext-Password',
  'Crypt-Password',
  'MD5-Password',
  'SHA-Password',
  'NT-Password',
  'LM-Password'
];

/**
 * Common session control attributes
 */
export const SESSION_CONTROL_ATTRIBUTES = [
  'Session-Timeout',
  'Idle-Timeout',
  'Simultaneous-Use',
  'Max-Daily-Session',
  'Max-Monthly-Session'
];

/**
 * Common network attributes
 */
export const NETWORK_ATTRIBUTES = [
  'Framed-IP-Address',
  'Framed-IP-Netmask',
  'Framed-Protocol',
  'Framed-Route'
];

// ===== Default Export =====
export default {
  // RadCheck methods
  getRadCheckAttributes,
  getRadCheckAttribute,
  createRadCheckAttribute,
  updateRadCheckAttribute,
  deleteRadCheckAttribute,
  
  // RadReply methods
  getRadReplyAttributes,
  getRadReplyAttribute,
  createRadReplyAttribute,
  updateRadReplyAttribute,
  deleteRadReplyAttribute,
  
  // User-specific methods
  getUserAttributes,
  setUserPassword,
  
  // Utility methods
  getRadiusOperators,
  getCommonCheckAttributes,
  getCommonReplyAttributes,
  
  // Batch operations
  createMultipleRadCheckAttributes,
  createMultipleRadReplyAttributes,
  deleteMultipleRadCheckAttributes,
  deleteMultipleRadReplyAttributes,
  
  // Search methods
  searchRadCheckByUsername,
  searchRadReplyByUsername,
  searchAttributesByName,
  searchAllAttributes,
  
  // Validation methods
  validateAttributeName,
  validateAttributeValue,
  validateUsername,
  
  // Constants
  DEFAULT_PAGINATION,
  MAX_PAGE_SIZE,
  PASSWORD_ATTRIBUTES,
  SESSION_CONTROL_ATTRIBUTES,
  NETWORK_ATTRIBUTES
};