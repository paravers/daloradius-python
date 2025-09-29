/**
 * RADIUS Group Management Service
 * 
 * This service provides API interactions for RADIUS group attribute management,
 * including RadGroupCheck and RadGroupReply operations.
 */

import { ApiService } from './apiService';

// ===== Type Definitions =====

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

/**
 * RadGroupCheck attribute for group authentication
 */
export interface RadGroupCheck extends BaseGroupAttribute {
  // Inherits all properties from BaseGroupAttribute
}

/**
 * RadGroupReply attribute for group authorization
 */
export interface RadGroupReply extends BaseGroupAttribute {
  // Inherits all properties from BaseGroupAttribute
}

/**
 * Group attribute creation data
 */
export interface GroupAttributeCreate {
  groupname: string;
  attribute: string;
  op: RadiusOperator;
  value: string;
}

/**
 * Group attribute update data
 */
export interface GroupAttributeUpdate {
  groupname?: string;
  attribute?: string;
  op?: RadiusOperator;
  value?: string;
}

/**
 * Group list response
 */
export interface GroupListResponse {
  groups: string[];
  total: number;
}

/**
 * Complete group attributes response
 */
export interface GroupAttributesResponse {
  groupname: string;
  check_attributes: RadGroupCheck[];
  reply_attributes: RadGroupReply[];
  total_attributes: number;
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
 * Paginated response for group attributes
 */
export interface PaginatedGroupAttributesResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Group attribute search parameters
 */
export interface GroupAttributeSearchParams {
  groupname?: string;
  attribute?: string;
  search?: string;
  page?: number;
  size?: number;
}

/**
 * Batch attribute creation data
 */
export interface BatchAttributeCreate {
  groupname: string;
  attributes: Array<{
    attribute: string;
    operator: RadiusOperator;
    value: string;
    type: 'check' | 'reply';
  }>;
}

/**
 * Batch operation result
 */
export interface BatchOperationResult {
  groupname: string;
  total_requested: number;
  created: number;
  failed: number;
  errors: string[];
  success_rate: number;
}

/**
 * Group cloning parameters
 */
export interface GroupCloneParams {
  source_group: string;
  target_group: string;
}

// ===== Service Class =====

export class GroupService extends ApiService {
  private readonly baseUrl = '/api/v1/radius';

  // ===== RadGroupCheck Operations =====

  /**
   * Get paginated list of RadGroupCheck attributes
   */
  async getGroupCheckAttributes(params?: GroupAttributeSearchParams): Promise<PaginatedGroupAttributesResponse<RadGroupCheck>> {
    const searchParams = new URLSearchParams();
    
    if (params?.groupname) searchParams.set('groupname', params.groupname);
    if (params?.attribute) searchParams.set('attribute', params.attribute);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/radgroupcheck?${searchParams.toString()}`);
  }

  /**
   * Create a new RadGroupCheck attribute
   */
  async createGroupCheckAttribute(data: GroupAttributeCreate): Promise<RadGroupCheck> {
    return this.post(`${this.baseUrl}/radgroupcheck`, data);
  }

  /**
   * Get a specific RadGroupCheck attribute
   */
  async getGroupCheckAttribute(attributeId: number): Promise<RadGroupCheck> {
    return this.get(`${this.baseUrl}/radgroupcheck/${attributeId}`);
  }

  /**
   * Update a RadGroupCheck attribute
   */
  async updateGroupCheckAttribute(attributeId: number, data: GroupAttributeCreate): Promise<RadGroupCheck> {
    return this.put(`${this.baseUrl}/radgroupcheck/${attributeId}`, data);
  }

  /**
   * Delete a RadGroupCheck attribute
   */
  async deleteGroupCheckAttribute(attributeId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/radgroupcheck/${attributeId}`);
  }

  // ===== RadGroupReply Operations =====

  /**
   * Get paginated list of RadGroupReply attributes
   */
  async getGroupReplyAttributes(params?: GroupAttributeSearchParams): Promise<PaginatedGroupAttributesResponse<RadGroupReply>> {
    const searchParams = new URLSearchParams();
    
    if (params?.groupname) searchParams.set('groupname', params.groupname);
    if (params?.attribute) searchParams.set('attribute', params.attribute);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/radgroupreply?${searchParams.toString()}`);
  }

  /**
   * Create a new RadGroupReply attribute
   */
  async createGroupReplyAttribute(data: GroupAttributeCreate): Promise<RadGroupReply> {
    return this.post(`${this.baseUrl}/radgroupreply`, data);
  }

  /**
   * Get a specific RadGroupReply attribute
   */
  async getGroupReplyAttribute(attributeId: number): Promise<RadGroupReply> {
    return this.get(`${this.baseUrl}/radgroupreply/${attributeId}`);
  }

  /**
   * Update a RadGroupReply attribute
   */
  async updateGroupReplyAttribute(attributeId: number, data: GroupAttributeCreate): Promise<RadGroupReply> {
    return this.put(`${this.baseUrl}/radgroupreply/${attributeId}`, data);
  }

  /**
   * Delete a RadGroupReply attribute
   */
  async deleteGroupReplyAttribute(attributeId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/radgroupreply/${attributeId}`);
  }

  // ===== Group Management Operations =====

  /**
   * Get list of all RADIUS groups
   */
  async getGroups(): Promise<GroupListResponse> {
    return this.get(`${this.baseUrl}/groups`);
  }

  /**
   * Get all attributes for a specific group
   */
  async getGroupAttributes(groupname: string): Promise<GroupAttributesResponse> {
    return this.get(`${this.baseUrl}/groups/${encodeURIComponent(groupname)}/attributes`);
  }

  /**
   * Delete all attributes for a specific group
   */
  async deleteGroupAllAttributes(groupname: string): Promise<{
    message: string;
    check_attributes_deleted: number;
    reply_attributes_deleted: number;
  }> {
    return this.delete(`${this.baseUrl}/groups/${encodeURIComponent(groupname)}/attributes`);
  }

  /**
   * Get group statistics
   */
  async getGroupStatistics(): Promise<GroupStatisticsResponse> {
    return this.get(`${this.baseUrl}/groups/statistics`);
  }

  // ===== Utility Operations =====

  /**
   * Validate group attribute name
   */
  validateAttributeName(attribute: string, type: 'check' | 'reply' = 'check'): { isValid: boolean; message: string } {
    if (!attribute || attribute.trim().length === 0) {
      return { isValid: false, message: 'Attribute name cannot be empty' };
    }

    if (attribute.length > 64) {
      return { isValid: false, message: 'Attribute name cannot exceed 64 characters' };
    }

    // Check for invalid characters
    const invalidChars = /[<>'"&]/;
    if (invalidChars.test(attribute)) {
      return { isValid: false, message: 'Attribute name contains invalid characters' };
    }

    // Common attribute validation
    if (type === 'check') {
      const commonCheckAttributes = [
        'Auth-Type', 'User-Password', 'Password', 'Crypt-Password',
        'MD5-Password', 'SHA-Password', 'CHAP-Password', 'LM-Password',
        'NT-Password', 'Group', 'Huntgroup-Name', 'Simultaneous-Use'
      ];
      
      if (commonCheckAttributes.includes(attribute)) {
        return { isValid: true, message: 'Valid check attribute' };
      }
    } else if (type === 'reply') {
      const commonReplyAttributes = [
        'Service-Type', 'Framed-Protocol', 'Framed-IP-Address',
        'Framed-IP-Netmask', 'Session-Timeout', 'Idle-Timeout',
        'Port-Limit', 'Acct-Interim-Interval', 'Filter-Id', 'Reply-Message'
      ];
      
      if (commonReplyAttributes.includes(attribute)) {
        return { isValid: true, message: 'Valid reply attribute' };
      }
    }

    return { isValid: true, message: 'Custom attribute - verify compatibility with your RADIUS server' };
  }

  /**
   * Validate attribute value
   */
  validateAttributeValue(value: string, attribute: string): { isValid: boolean; message: string } {
    if (!value || value.trim().length === 0) {
      return { isValid: false, message: 'Attribute value cannot be empty' };
    }

    if (value.length > 253) {
      return { isValid: false, message: 'Attribute value cannot exceed 253 characters' };
    }

    // Specific validation based on attribute
    switch (attribute) {
      case 'Session-Timeout':
      case 'Idle-Timeout':
      case 'Acct-Interim-Interval':
      case 'Port-Limit':
        const numValue = parseInt(value, 10);
        if (isNaN(numValue) || numValue < 0) {
          return { isValid: false, message: 'Value must be a positive number' };
        }
        break;
      
      case 'Framed-IP-Address':
        const ipPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (!ipPattern.test(value)) {
          return { isValid: false, message: 'Invalid IP address format' };
        }
        break;
      
      case 'Service-Type':
        const validServiceTypes = [
          'Login-User', 'Framed-User', 'Callback-Login-User',
          'Callback-Framed-User', 'Outbound-User', 'Administrative-User',
          'NAS-Prompt-User', 'Authenticate-Only', 'Callback-NAS-Prompt',
          'Call-Check', 'Callback-Administrative'
        ];
        if (!validServiceTypes.includes(value)) {
          return { isValid: false, message: 'Invalid Service-Type value' };
        }
        break;
    }

    return { isValid: true, message: 'Valid attribute value' };
  }

  /**
   * Get common attribute names by type
   */
  getCommonAttributes(type: 'check' | 'reply'): string[] {
    if (type === 'check') {
      return [
        'Auth-Type', 'User-Password', 'Password', 'Crypt-Password',
        'MD5-Password', 'SHA-Password', 'CHAP-Password', 'LM-Password',
        'NT-Password', 'SMB-Account-CTRL', 'SMB-Account-CTRL-TEXT',
        'Group', 'Huntgroup-Name', 'Simultaneous-Use', 'Called-Station-Id',
        'Calling-Station-Id', 'NAS-Port-Type'
      ];
    } else {
      return [
        'Service-Type', 'Framed-Protocol', 'Framed-IP-Address',
        'Framed-IP-Netmask', 'Framed-Routing', 'Filter-Id',
        'Framed-MTU', 'Framed-Compression', 'Login-IP-Host',
        'Login-Service', 'Login-TCP-Port', 'Reply-Message',
        'Callback-Number', 'Callback-Id', 'Framed-Route',
        'Class', 'Session-Timeout', 'Idle-Timeout',
        'Termination-Action', 'Port-Limit', 'Acct-Interim-Interval'
      ];
    }
  }

  /**
   * Get available operators
   */
  getOperators(): Array<{ value: RadiusOperator; label: string; description: string }> {
    return [
      { value: RadiusOperator.EQUAL, label: '==', description: 'Equal (exact match)' },
      { value: RadiusOperator.SET, label: ':=', description: 'Set (assignment)' },
      { value: RadiusOperator.ADD, label: '+=', description: 'Add to existing value' },
      { value: RadiusOperator.NOT_EQUAL, label: '!=', description: 'Not equal' },
      { value: RadiusOperator.LESS_THAN, label: '<', description: 'Less than' },
      { value: RadiusOperator.LESS_EQUAL, label: '<=', description: 'Less than or equal' },
      { value: RadiusOperator.GREATER_THAN, label: '>', description: 'Greater than' },
      { value: RadiusOperator.GREATER_EQUAL, label: '>=', description: 'Greater than or equal' },
      { value: RadiusOperator.REGEX_MATCH, label: '=~', description: 'Regular expression match' },
      { value: RadiusOperator.REGEX_NOT_MATCH, label: '!~', description: 'Regular expression not match' }
    ];
  }

  /**
   * Format attribute for display
   */
  formatAttributeForDisplay(attribute: BaseGroupAttribute): string {
    return `${attribute.groupname}:${attribute.attribute} ${attribute.op} "${attribute.value}"`;
  }

  /**
   * Search and filter attributes
   */
  filterAttributes(
    attributes: BaseGroupAttribute[], 
    searchTerm: string, 
    filters: { groupname?: string; attribute?: string }
  ): BaseGroupAttribute[] {
    return attributes.filter(attr => {
      // Apply groupname filter
      if (filters.groupname && attr.groupname !== filters.groupname) {
        return false;
      }

      // Apply attribute filter
      if (filters.attribute && attr.attribute !== filters.attribute) {
        return false;
      }

      // Apply search term
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        return (
          attr.groupname.toLowerCase().includes(term) ||
          attr.attribute.toLowerCase().includes(term) ||
          attr.value.toLowerCase().includes(term)
        );
      }

      return true;
    });
  }

  /**
   * Group attributes by groupname
   */
  groupAttributesByGroup(attributes: BaseGroupAttribute[]): Record<string, BaseGroupAttribute[]> {
    return attributes.reduce((groups, attr) => {
      if (!groups[attr.groupname]) {
        groups[attr.groupname] = [];
      }
      groups[attr.groupname].push(attr);
      return groups;
    }, {} as Record<string, BaseGroupAttribute[]>);
  }
}

// Export singleton instance
export const groupService = new GroupService();
export default groupService;