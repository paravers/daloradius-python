/**
 * User Group Association Service
 * 
 * This service provides API interactions for user group association management,
 * including user-group relationships, group statistics, and batch operations.
 */

import { ApiService } from './apiService';

// ===== Type Definitions =====

/**
 * Base user group association interface
 */
export interface BaseUserGroup {
  id?: number;
  username: string;
  groupname: string;
  priority: number;
  user_id?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * User group creation data
 */
export interface UserGroupCreate {
  username: string;
  groupname: string;
  priority: number;
}

/**
 * User group update data
 */
export interface UserGroupUpdate {
  groupname?: string;
  priority?: number;
}

/**
 * User group with details
 */
export interface UserGroupDetail extends BaseUserGroup {
  member_count: number;
  joined_at: string;
}

/**
 * Group list response
 */
export interface GroupListResponse {
  groups: string[];
  total: number;
}

/**
 * User group statistics response
 */
export interface UserGroupStatistics {
  total_associations: number;
  total_groups: number;
  total_users: number;
  top_groups: Array<{
    groupname: string;
    user_count: number;
  }>;
  average_users_per_group?: number;
  empty_groups?: string[];
  empty_groups_count?: number;
  groups_with_users?: number;
}

/**
 * Group with user count
 */
export interface GroupWithUserCount {
  groupname: string;
  user_count: number;
}

/**
 * Batch operation data
 */
export interface BatchUserGroupOperation {
  usernames: string[];
  groupname: string;
  priority: number;
}

/**
 * Batch operation result
 */
export interface BatchUserGroupResult {
  groupname: string;
  requested: number;
  added?: number;
  removed?: number;
  failed: number;
  errors: string[];
}

/**
 * Paginated response for user groups
 */
export interface PaginatedUserGroupResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * User group search parameters
 */
export interface UserGroupSearchParams {
  username?: string;
  groupname?: string;
  search?: string;
  page?: number;
  size?: number;
}

/**
 * User with group details
 */
export interface UserWithGroups {
  username: string;
  total_groups: number;
  highest_priority: number;
  lowest_priority: number;
  groups: UserGroupDetail[];
  user_info: {
    id: number;
    created_at: string;
    is_active: boolean;
  };
}

/**
 * Group with user details
 */
export interface GroupWithUsers {
  groupname: string;
  total_users: number;
  users: Array<{
    username: string;
    priority: number;
    joined_at: string;
    association_id: number;
    user_id?: number;
    user_created_at?: string;
    is_active?: boolean;
  }>;
}

// ===== Service Class =====

export class UserGroupService extends ApiService {
  private readonly baseUrl = '/api/v1/user-groups';

  // ===== User Group Association CRUD =====

  /**
   * Get paginated list of user group associations
   */
  async getUserGroupAssociations(params?: UserGroupSearchParams): Promise<PaginatedUserGroupResponse<BaseUserGroup>> {
    const searchParams = new URLSearchParams();
    
    if (params?.username) searchParams.set('username', params.username);
    if (params?.groupname) searchParams.set('groupname', params.groupname);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.size) searchParams.set('size', params.size.toString());

    return this.get(`${this.baseUrl}/user-groups?${searchParams.toString()}`);
  }

  /**
   * Create a new user-group association
   */
  async createUserGroupAssociation(data: UserGroupCreate): Promise<BaseUserGroup> {
    return this.post(`${this.baseUrl}/user-groups`, data);
  }

  /**
   * Get a specific user-group association
   */
  async getUserGroupAssociation(associationId: number): Promise<BaseUserGroup> {
    return this.get(`${this.baseUrl}/user-groups/${associationId}`);
  }

  /**
   * Update a user-group association
   */
  async updateUserGroupAssociation(associationId: number, data: UserGroupUpdate): Promise<BaseUserGroup> {
    return this.put(`${this.baseUrl}/user-groups/${associationId}`, data);
  }

  /**
   * Delete a user-group association
   */
  async deleteUserGroupAssociation(associationId: number): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/user-groups/${associationId}`);
  }

  // ===== User-Specific Group Management =====

  /**
   * Get all groups for a specific user with details
   */
  async getUserGroups(username: string): Promise<UserGroupDetail[]> {
    return this.get(`${this.baseUrl}/users/${encodeURIComponent(username)}/groups`);
  }

  /**
   * Add a user to a group
   */
  async addUserToGroup(username: string, data: UserGroupCreate): Promise<BaseUserGroup> {
    return this.post(`${this.baseUrl}/users/${encodeURIComponent(username)}/groups`, data);
  }

  /**
   * Remove a user from a group
   */
  async removeUserFromGroup(username: string, groupname: string): Promise<{ message: string }> {
    return this.delete(`${this.baseUrl}/users/${encodeURIComponent(username)}/groups/${encodeURIComponent(groupname)}`);
  }

  /**
   * Update user's priority in a specific group
   */
  async updateUserGroupPriority(username: string, groupname: string, priority: number): Promise<{ message: string; new_priority: number }> {
    return this.put(`${this.baseUrl}/users/${encodeURIComponent(username)}/groups/${encodeURIComponent(groupname)}/priority?priority=${priority}`);
  }

  // ===== Group Management =====

  /**
   * Get list of all groups
   */
  async getGroups(): Promise<GroupListResponse> {
    return this.get(`${this.baseUrl}/groups`);
  }

  /**
   * Get all users in a specific group
   */
  async getGroupUsers(groupname: string): Promise<BaseUserGroup[]> {
    return this.get(`${this.baseUrl}/groups/${encodeURIComponent(groupname)}/users`);
  }

  /**
   * Get all groups with their user counts
   */
  async getGroupsWithUserCounts(): Promise<GroupWithUserCount[]> {
    return this.get(`${this.baseUrl}/groups/counts`);
  }

  /**
   * Get user group statistics
   */
  async getUserGroupStatistics(): Promise<UserGroupStatistics> {
    return this.get(`${this.baseUrl}/groups/statistics`);
  }

  // ===== Batch Operations =====

  /**
   * Batch add multiple users to a group
   */
  async batchAddUsersToGroup(groupname: string, data: BatchUserGroupOperation): Promise<BatchUserGroupResult> {
    return this.post(`${this.baseUrl}/groups/${encodeURIComponent(groupname)}/users/batch-add`, data);
  }

  /**
   * Batch remove multiple users from a group
   */
  async batchRemoveUsersFromGroup(groupname: string, data: BatchUserGroupOperation): Promise<BatchUserGroupResult> {
    return this.post(`${this.baseUrl}/groups/${encodeURIComponent(groupname)}/users/batch-remove`, data);
  }

  // ===== Search and Utility =====

  /**
   * Search user group associations with patterns
   */
  async searchUserGroups(params: {
    username_pattern?: string;
    groupname_pattern?: string;
    skip?: number;
    limit?: number;
  }): Promise<BaseUserGroup[]> {
    const searchParams = new URLSearchParams();
    
    if (params.username_pattern) searchParams.set('username_pattern', params.username_pattern);
    if (params.groupname_pattern) searchParams.set('groupname_pattern', params.groupname_pattern);
    if (params.skip !== undefined) searchParams.set('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());

    return this.get(`${this.baseUrl}/user-groups/search?${searchParams.toString()}`);
  }

  // ===== Extended Service Methods =====

  /**
   * Get detailed user information with groups (using service layer)
   */
  async getUserWithGroups(username: string): Promise<UserWithGroups> {
    // This would call a service endpoint that provides detailed user-group information
    // For now, we'll build it from existing endpoints
    const userGroups = await this.getUserGroups(username);
    
    const totalGroups = userGroups.length;
    const priorities = userGroups.map(g => g.priority);
    const highestPriority = Math.max(...priorities, 0);
    const lowestPriority = Math.min(...priorities, 0);

    return {
      username,
      total_groups: totalGroups,
      highest_priority: highestPriority,
      lowest_priority: lowestPriority,
      groups: userGroups,
      user_info: {
        id: userGroups[0]?.user_id || 0,
        created_at: userGroups[0]?.created_at || new Date().toISOString(),
        is_active: true
      }
    };
  }

  /**
   * Get detailed group information with users
   */
  async getGroupWithUsers(groupname: string): Promise<GroupWithUsers> {
    const groupUsers = await this.getGroupUsers(groupname);
    
    const usersWithDetails = groupUsers.map(ug => ({
      username: ug.username,
      priority: ug.priority,
      joined_at: ug.created_at || new Date().toISOString(),
      association_id: ug.id || 0,
      user_id: ug.user_id,
      user_created_at: ug.created_at,
      is_active: true
    }));

    // Sort by priority
    usersWithDetails.sort((a, b) => a.priority - b.priority);

    return {
      groupname,
      total_users: usersWithDetails.length,
      users: usersWithDetails
    };
  }

  // ===== Validation Methods =====

  /**
   * Validate group name
   */
  validateGroupName(groupname: string): { isValid: boolean; message: string } {
    if (!groupname || groupname.trim().length === 0) {
      return { isValid: false, message: 'Group name cannot be empty' };
    }

    if (groupname.length > 64) {
      return { isValid: false, message: 'Group name cannot exceed 64 characters' };
    }

    // Check for invalid characters
    const invalidChars = ['<', '>', '"', "'", '&', '\n', '\r', '\t'];
    if (invalidChars.some(char => groupname.includes(char))) {
      return { isValid: false, message: 'Group name contains invalid characters' };
    }

    return { isValid: true, message: 'Valid group name' };
  }

  /**
   * Validate priority value
   */
  validatePriority(priority: number): { isValid: boolean; message: string } {
    if (priority < 0 || priority > 9999) {
      return { isValid: false, message: 'Priority must be between 0 and 9999' };
    }

    return { isValid: true, message: 'Valid priority' };
  }

  /**
   * Validate user group association data
   */
  validateUserGroupData(data: UserGroupCreate): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate username
    if (!data.username || data.username.trim().length === 0) {
      errors.push('Username cannot be empty');
    } else if (data.username.length > 64) {
      errors.push('Username cannot exceed 64 characters');
    }

    // Validate group name
    const groupValidation = this.validateGroupName(data.groupname);
    if (!groupValidation.isValid) {
      errors.push(groupValidation.message);
    }

    // Validate priority
    const priorityValidation = this.validatePriority(data.priority);
    if (!priorityValidation.isValid) {
      errors.push(priorityValidation.message);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // ===== Utility Methods =====

  /**
   * Sort users by priority
   */
  sortUsersByPriority(users: BaseUserGroup[]): BaseUserGroup[] {
    return [...users].sort((a, b) => a.priority - b.priority);
  }

  /**
   * Group users by priority level
   */
  groupUsersByPriority(users: BaseUserGroup[]): Record<number, BaseUserGroup[]> {
    return users.reduce((groups, user) => {
      if (!groups[user.priority]) {
        groups[user.priority] = [];
      }
      groups[user.priority].push(user);
      return groups;
    }, {} as Record<number, BaseUserGroup[]>);
  }

  /**
   * Get users not in a specific group
   */
  async getUsersNotInGroup(groupname: string, allUsers: string[]): Promise<string[]> {
    const groupUsers = await this.getGroupUsers(groupname);
    const usersInGroup = new Set(groupUsers.map(ug => ug.username));
    
    return allUsers.filter(username => !usersInGroup.has(username));
  }

  /**
   * Format user group association for display
   */
  formatUserGroupForDisplay(userGroup: BaseUserGroup): string {
    return `${userGroup.username} → ${userGroup.groupname} (Priority: ${userGroup.priority})`;
  }

  /**
   * Calculate group statistics
   */
  calculateGroupStatistics(groups: GroupWithUserCount[]): {
    totalGroups: number;
    totalUsers: number;
    averageUsersPerGroup: number;
    largestGroup: string | null;
    smallestGroup: string | null;
  } {
    const totalGroups = groups.length;
    const totalUsers = groups.reduce((sum, group) => sum + group.user_count, 0);
    const averageUsersPerGroup = totalGroups > 0 ? totalUsers / totalGroups : 0;

    const sortedGroups = [...groups].sort((a, b) => b.user_count - a.user_count);
    const largestGroup = sortedGroups[0]?.groupname || null;
    const smallestGroup = sortedGroups[sortedGroups.length - 1]?.groupname || null;

    return {
      totalGroups,
      totalUsers,
      averageUsersPerGroup: Math.round(averageUsersPerGroup * 100) / 100,
      largestGroup,
      smallestGroup
    };
  }
}

// Export singleton instance
export const userGroupService = new UserGroupService();
export default userGroupService;