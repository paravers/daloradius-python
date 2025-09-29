/**
 * RADIUS Management Service
 * 
 * This service provides API interactions for additional RADIUS management features
 * including IP pools, profiles, realms, proxies, and hunt groups.
 */

import { ApiService } from './apiService';

// ===== Type Definitions =====

/**
 * Base IP Pool entry interface
 */
export interface RadIpPoolEntry {
  id?: number;
  pool_name: string;
  framedipaddress: string;
  nasipaddress: string;
  calledstationid?: string;
  callingstationid?: string;
  expiry_time?: string;
  username?: string;
  pool_key?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * IP Pool creation data
 */
export interface RadIpPoolCreate {
  pool_name: string;
  framedipaddress: string;
  nasipaddress: string;
  calledstationid?: string;
  callingstationid?: string;
  expiry_time?: string;
  username?: string;
  pool_key?: string;
}

/**
 * IP Pool update data
 */
export interface RadIpPoolUpdate {
  pool_name?: string;
  framedipaddress?: string;
  nasipaddress?: string;
  calledstationid?: string;
  callingstationid?: string;
  expiry_time?: string;
  username?: string;
  pool_key?: string;
}

/**
 * RADIUS Attribute interface
 */
export interface RadiusAttribute {
  attribute: string;
  op: string;
  value: string;
}

/**
 * Profile interface
 */
export interface RadiusProfile {
  id?: number;
  profile_name: string;
  description?: string;
  check_attributes?: RadiusAttribute[];
  reply_attributes?: RadiusAttribute[];
  is_active?: boolean;
  usage_count?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * Profile creation data
 */
export interface ProfileCreate {
  profile_name: string;
  description?: string;
  check_attributes: RadiusAttribute[];
  reply_attributes: RadiusAttribute[];
}

/**
 * Profile update data
 */
export interface ProfileUpdate {
  profile_name?: string;
  description?: string;
}

/**
 * Realm interface
 */
export interface Realm {
  id?: number;
  realmname: string;
  type?: string;
  authhost?: string;
  accthost?: string;
  secret?: string;
  ldflag?: string;
  nostrip?: boolean;
  hints?: string;
  notrealm?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Realm creation data
 */
export interface RealmCreate {
  realmname: string;
  type?: string;
  authhost?: string;
  accthost?: string;
  secret?: string;
  ldflag?: string;
  nostrip?: boolean;
  hints?: string;
  notrealm?: string;
}

/**
 * Realm update data
 */
export interface RealmUpdate {
  type?: string;
  authhost?: string;
  accthost?: string;
  secret?: string;
  ldflag?: string;
  nostrip?: boolean;
  hints?: string;
  notrealm?: string;
}

/**
 * Proxy interface
 */
export interface Proxy {
  id?: number;
  proxyname: string;
  retry_delay?: number;
  retry_count?: number;
  dead_time?: number;
  default_fallback?: boolean;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Proxy creation data
 */
export interface ProxyCreate {
  proxyname: string;
  retry_delay?: number;
  retry_count?: number;
  dead_time?: number;
  default_fallback?: boolean;
}

/**
 * Proxy update data
 */
export interface ProxyUpdate {
  retry_delay?: number;
  retry_count?: number;
  dead_time?: number;
  default_fallback?: boolean;
}

/**
 * Hunt Group interface
 */
export interface HuntGroup {
  id?: number;
  groupname: string;
  nasipaddress: string;
  nasportid?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * Hunt Group creation data
 */
export interface HuntGroupCreate {
  groupname: string;
  nasipaddress: string;
  nasportid?: string;
}

/**
 * Hunt Group update data
 */
export interface HuntGroupUpdate {
  groupname?: string;
  nasipaddress?: string;
  nasportid?: string;
}

/**
 * Statistics interfaces
 */
export interface IpPoolStatistics {
  total_ips: number;
  assigned_ips: number;
  available_ips: number;
  expired_ips: number;
  pools_by_nas: Array<{
    nas_ip: string;
    ip_count: number;
  }>;
}

export interface HuntGroupStatistics {
  total_hunt_groups: number;
  unique_group_names: number;
  unique_nas_count: number;
  groups_by_nas: Record<string, number>;
}

/**
 * List response interfaces
 */
export interface NameListResponse {
  names?: string[];
  pools?: string[];
  profiles?: string[];
  realms?: string[];
  proxies?: string[];
  groups?: string[];
  total: number;
}

/**
 * Paginated response for RADIUS management
 */
export interface PaginatedRadiusResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Search parameters
 */
export interface RadiusSearchParams {
  pool_name?: string;
  nas_ip?: string;
  status?: string;
  groupname?: string;
  active_only?: boolean;
  include_attributes?: boolean;
  page?: number;
  size?: number;
}

// ===== Service Class =====

export class RadiusManagementService extends ApiService {
  private readonly baseUrl = '/api/v1/radius-management';

  // ===== IP Pool Management =====

  /**
   * Get paginated list of IP pool entries
   */
  async getIpPoolEntries(params?: RadiusSearchParams): Promise<PaginatedRadiusResponse<RadIpPoolEntry>> {
    const searchParams = new URLSearchParams();
    
    if (params?.pool_name) searchParams.set('pool_name', params.pool_name);
    if (params?.nas_ip) searchParams.set('nas_ip', params.nas_ip);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/ip-pools?${searchParams.toString()}`);
  }

  /**
   * Create new IP pool entry
   */
  async createIpPoolEntry(data: RadIpPoolCreate): Promise<RadIpPoolEntry> {
    return this.post(`${this.baseUrl}/ip-pools`, data);
  }

  /**
   * Get specific IP pool entry
   */
  async getIpPoolEntry(entryId: number): Promise<RadIpPoolEntry> {
    return this.get(`${this.baseUrl}/ip-pools/${entryId}`);
  }

  /**
   * Update IP pool entry
   */
  async updateIpPoolEntry(entryId: number, data: RadIpPoolUpdate): Promise<RadIpPoolEntry> {
    return this.put(`${this.baseUrl}/ip-pools/${entryId}`, data);
  }

  /**
   * Delete IP pool entry
   */
  async deleteIpPoolEntry(entryId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/ip-pools/${entryId}`);
  }

  /**
   * Assign IP to user
   */
  async assignIpToUser(
    poolName: string,
    username: string,
    nasIp: string,
    durationHours?: number
  ): Promise<{ message: string; ip_entry?: RadIpPoolEntry }> {
    const params = new URLSearchParams();
    params.set('pool_name', poolName);
    params.set('username', username);
    params.set('nas_ip', nasIp);
    if (durationHours) params.set('duration_hours', durationHours.toString());

    return this.post(`${this.baseUrl}/ip-pools/assign?${params.toString()}`);
  }

  /**
   * Release IP from user
   */
  async releaseIpFromUser(ipAddress: string): Promise<{ message: string }> {
    return this.post(`${this.baseUrl}/ip-pools/release/${encodeURIComponent(ipAddress)}`);
  }

  /**
   * Get list of pool names
   */
  async getPoolNames(): Promise<NameListResponse> {
    return this.get(`${this.baseUrl}/ip-pools/pools/list`);
  }

  /**
   * Get IP pool statistics
   */
  async getIpPoolStatistics(): Promise<IpPoolStatistics> {
    return this.get(`${this.baseUrl}/ip-pools/statistics`);
  }

  // ===== Profile Management =====

  /**
   * Get paginated list of profiles
   */
  async getProfiles(params?: RadiusSearchParams): Promise<PaginatedRadiusResponse<RadiusProfile>> {
    const searchParams = new URLSearchParams();
    
    if (params?.include_attributes) searchParams.set('include_attributes', params.include_attributes.toString());
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/profiles?${searchParams.toString()}`);
  }

  /**
   * Create new profile
   */
  async createProfile(data: ProfileCreate): Promise<RadiusProfile> {
    return this.post(`${this.baseUrl}/profiles`, data);
  }

  /**
   * Get specific profile
   */
  async getProfile(profileId: number): Promise<RadiusProfile> {
    return this.get(`${this.baseUrl}/profiles/${profileId}`);
  }

  /**
   * Get profile by name
   */
  async getProfileByName(profileName: string): Promise<RadiusProfile> {
    return this.get(`${this.baseUrl}/profiles/by-name/${encodeURIComponent(profileName)}`);
  }

  /**
   * Update profile
   */
  async updateProfile(profileId: number, data: ProfileUpdate): Promise<RadiusProfile> {
    return this.put(`${this.baseUrl}/profiles/${profileId}`, data);
  }

  /**
   * Duplicate profile
   */
  async duplicateProfile(
    sourceProfile: string,
    newProfile: string,
    description?: string
  ): Promise<RadiusProfile> {
    const params = new URLSearchParams();
    params.set('source_profile', sourceProfile);
    params.set('new_profile', newProfile);
    if (description) params.set('description', description);

    return this.post(`${this.baseUrl}/profiles/duplicate?${params.toString()}`);
  }

  /**
   * Delete profile
   */
  async deleteProfile(profileId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/profiles/${profileId}`);
  }

  /**
   * Get list of profile names
   */
  async getProfileNames(): Promise<NameListResponse> {
    return this.get(`${this.baseUrl}/profiles/names/list`);
  }

  // ===== Realm Management =====

  /**
   * Get paginated list of realms
   */
  async getRealms(params?: RadiusSearchParams): Promise<PaginatedRadiusResponse<Realm>> {
    const searchParams = new URLSearchParams();
    
    if (params?.active_only) searchParams.set('active_only', params.active_only.toString());
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/realms?${searchParams.toString()}`);
  }

  /**
   * Create new realm
   */
  async createRealm(data: RealmCreate): Promise<Realm> {
    return this.post(`${this.baseUrl}/realms`, data);
  }

  /**
   * Get specific realm
   */
  async getRealm(realmId: number): Promise<Realm> {
    return this.get(`${this.baseUrl}/realms/${realmId}`);
  }

  /**
   * Get realm by name
   */
  async getRealmByName(realmname: string): Promise<Realm> {
    return this.get(`${this.baseUrl}/realms/by-name/${encodeURIComponent(realmname)}`);
  }

  /**
   * Update realm
   */
  async updateRealm(realmId: number, data: RealmUpdate): Promise<Realm> {
    return this.put(`${this.baseUrl}/realms/${realmId}`, data);
  }

  /**
   * Delete realm
   */
  async deleteRealm(realmId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/realms/${realmId}`);
  }

  /**
   * Get list of realm names
   */
  async getRealmNames(): Promise<NameListResponse> {
    return this.get(`${this.baseUrl}/realms/names/list`);
  }

  // ===== Proxy Management =====

  /**
   * Get paginated list of proxies
   */
  async getProxies(params?: RadiusSearchParams): Promise<PaginatedRadiusResponse<Proxy>> {
    const searchParams = new URLSearchParams();
    
    if (params?.active_only) searchParams.set('active_only', params.active_only.toString());
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/proxies?${searchParams.toString()}`);
  }

  /**
   * Create new proxy
   */
  async createProxy(data: ProxyCreate): Promise<Proxy> {
    return this.post(`${this.baseUrl}/proxies`, data);
  }

  /**
   * Get specific proxy
   */
  async getProxy(proxyId: number): Promise<Proxy> {
    return this.get(`${this.baseUrl}/proxies/${proxyId}`);
  }

  /**
   * Update proxy
   */
  async updateProxy(proxyId: number, data: ProxyUpdate): Promise<Proxy> {
    return this.put(`${this.baseUrl}/proxies/${proxyId}`, data);
  }

  /**
   * Delete proxy
   */
  async deleteProxy(proxyId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/proxies/${proxyId}`);
  }

  /**
   * Get list of proxy names
   */
  async getProxyNames(): Promise<NameListResponse> {
    return this.get(`${this.baseUrl}/proxies/names/list`);
  }

  // ===== Hunt Group Management =====

  /**
   * Get paginated list of hunt groups
   */
  async getHuntGroups(params?: RadiusSearchParams): Promise<PaginatedRadiusResponse<HuntGroup>> {
    const searchParams = new URLSearchParams();
    
    if (params?.groupname) searchParams.set('groupname', params.groupname);
    if (params?.nas_ip) searchParams.set('nas_ip', params.nas_ip);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/hunt-groups?${searchParams.toString()}`);
  }

  /**
   * Create new hunt group
   */
  async createHuntGroup(data: HuntGroupCreate): Promise<HuntGroup> {
    return this.post(`${this.baseUrl}/hunt-groups`, data);
  }

  /**
   * Get specific hunt group
   */
  async getHuntGroup(groupId: number): Promise<HuntGroup> {
    return this.get(`${this.baseUrl}/hunt-groups/${groupId}`);
  }

  /**
   * Update hunt group
   */
  async updateHuntGroup(groupId: number, data: HuntGroupUpdate): Promise<HuntGroup> {
    return this.put(`${this.baseUrl}/hunt-groups/${groupId}`, data);
  }

  /**
   * Delete hunt group
   */
  async deleteHuntGroup(groupId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/hunt-groups/${groupId}`);
  }

  /**
   * Get list of hunt group names
   */
  async getHuntGroupNames(): Promise<NameListResponse> {
    return this.get(`${this.baseUrl}/hunt-groups/groups/list`);
  }

  /**
   * Get NAS IPs for a hunt group
   */
  async getNasIpsForHuntGroup(groupname: string): Promise<{ groupname: string; nas_ips: string[]; total: number }> {
    return this.get(`${this.baseUrl}/hunt-groups/groups/${encodeURIComponent(groupname)}/nas-ips`);
  }

  /**
   * Get hunt group statistics
   */
  async getHuntGroupStatistics(): Promise<HuntGroupStatistics> {
    return this.get(`${this.baseUrl}/hunt-groups/statistics`);
  }

  // ===== Validation Methods =====

  /**
   * Validate IP address
   */
  validateIpAddress(ip: string): { isValid: boolean; message: string } {
    const ipPattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    
    if (!ip || ip.trim().length === 0) {
      return { isValid: false, message: 'IP address cannot be empty' };
    }

    if (!ipPattern.test(ip.trim())) {
      return { isValid: false, message: 'Invalid IP address format' };
    }

    return { isValid: true, message: 'Valid IP address' };
  }

  /**
   * Validate pool name
   */
  validatePoolName(poolName: string): { isValid: boolean; message: string } {
    if (!poolName || poolName.trim().length === 0) {
      return { isValid: false, message: 'Pool name cannot be empty' };
    }

    if (poolName.length > 30) {
      return { isValid: false, message: 'Pool name cannot exceed 30 characters' };
    }

    // Check for invalid characters
    const invalidChars = ['<', '>', '"', "'", '&', '\n', '\r', '\t'];
    if (invalidChars.some(char => poolName.includes(char))) {
      return { isValid: false, message: 'Pool name contains invalid characters' };
    }

    return { isValid: true, message: 'Valid pool name' };
  }

  /**
   * Validate profile name
   */
  validateProfileName(profileName: string): { isValid: boolean; message: string } {
    if (!profileName || profileName.trim().length === 0) {
      return { isValid: false, message: 'Profile name cannot be empty' };
    }

    if (profileName.length > 64) {
      return { isValid: false, message: 'Profile name cannot exceed 64 characters' };
    }

    return { isValid: true, message: 'Valid profile name' };
  }

  /**
   * Validate RADIUS attribute
   */
  validateRadiusAttribute(attribute: RadiusAttribute): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!attribute.attribute || attribute.attribute.trim().length === 0) {
      errors.push('Attribute name cannot be empty');
    } else if (attribute.attribute.length > 64) {
      errors.push('Attribute name cannot exceed 64 characters');
    }

    const validOperators = ['==', ':=', '+=', '!=', '>', '>=', '<', '<=', '=~', '!~'];
    if (!attribute.op || !validOperators.includes(attribute.op)) {
      errors.push('Invalid operator. Must be one of: ==, :=, +=, !=, >, >=, <, <=, =~, !~');
    }

    if (!attribute.value || attribute.value.trim().length === 0) {
      errors.push('Attribute value cannot be empty');
    } else if (attribute.value.length > 253) {
      errors.push('Attribute value cannot exceed 253 characters');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // ===== Utility Methods =====

  /**
   * Format IP pool entry for display
   */
  formatIpPoolForDisplay(entry: RadIpPoolEntry): string {
    const status = entry.username ? 'Assigned' : 'Available';
    return `${entry.framedipaddress} (${entry.pool_name}) - ${status}`;
  }

  /**
   * Format profile for display
   */
  formatProfileForDisplay(profile: RadiusProfile): string {
    const attrCount = (profile.check_attributes?.length || 0) + (profile.reply_attributes?.length || 0);
    return `${profile.profile_name} (${attrCount} attributes)`;
  }

  /**
   * Get available IP status text
   */
  getIpStatusText(entry: RadIpPoolEntry): string {
    if (!entry.username) return 'Available';
    
    if (entry.expiry_time) {
      const expiryDate = new Date(entry.expiry_time);
      const now = new Date();
      
      if (expiryDate <= now) {
        return 'Expired';
      }
    }
    
    return 'Assigned';
  }

  /**
   * Get IP status color
   */
  getIpStatusColor(entry: RadIpPoolEntry): string {
    const status = this.getIpStatusText(entry);
    
    switch (status) {
      case 'Available': return 'success';
      case 'Assigned': return 'processing';
      case 'Expired': return 'warning';
      default: return 'default';
    }
  }

  /**
   * Format realm for display
   */
  formatRealmForDisplay(realm: Realm): string {
    return `${realm.realmname} (${realm.type || 'Default'})`;
  }

  /**
   * Format proxy for display
   */
  formatProxyForDisplay(proxy: Proxy): string {
    const status = proxy.is_active ? 'Active' : 'Inactive';
    const fallback = proxy.default_fallback ? ', Fallback' : '';
    return `${proxy.proxyname} (${status}${fallback})`;
  }

  /**
   * Format hunt group for display
   */
  formatHuntGroupForDisplay(group: HuntGroup): string {
    return `${group.groupname} → ${group.nasipaddress}${group.nasportid ? ':' + group.nasportid : ''}`;
  }
}

// Export singleton instance
export const radiusManagementService = new RadiusManagementService();
export default radiusManagementService;