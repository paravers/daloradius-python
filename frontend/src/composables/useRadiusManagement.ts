/**
 * RADIUS Management Composable
 * 
 * This composable provides reactive state management for RADIUS attributes,
 * including RadCheck and RadReply operations with proper error handling
 * and loading states.
 */

import { ref, reactive, computed, watch } from 'vue';
import { message } from 'ant-design-vue';
import type {
  RadCheck,
  RadCheckCreate,
  RadCheckUpdate,
  RadReply,
  RadReplyCreate,
  RadReplyUpdate,
  UserAttributes,
  RadiusSearchParams,
  PaginatedRadiusResponse,
  RadiusOperator,
  CommonCheckAttributes,
  CommonReplyAttributes
} from '@/types/radius';
import radiusService from '@/services/radiusService';

// ===== Main Composable =====

export function useRadiusManagement() {
  // ===== Reactive State =====
  
  // Loading states
  const loading = ref(false);
  const loadingCheck = ref(false);
  const loadingReply = ref(false);
  const submitting = ref(false);
  
  // Data states
  const radCheckAttributes = ref<RadCheck[]>([]);
  const radReplyAttributes = ref<RadReply[]>([]);
  const currentCheckAttribute = ref<RadCheck | null>(null);
  const currentReplyAttribute = ref<RadReply | null>(null);
  const userAttributes = ref<UserAttributes | null>(null);
  
  // Pagination states
  const checkPagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true
  });
  
  const replyPagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true
  });
  
  // Search and filter states
  const searchParams = reactive<RadiusSearchParams>({
    username: '',
    attribute: '',
    search: '',
    page: 1,
    size: 20
  });
  
  // Common attributes cache
  const commonCheckAttributes = ref<CommonCheckAttributes | null>(null);
  const commonReplyAttributes = ref<CommonReplyAttributes | null>(null);
  const radiusOperators = ref<RadiusOperator[]>([]);
  
  // Error state
  const error = ref<string | null>(null);
  
  // ===== Computed Properties =====
  
  const hasCheckAttributes = computed(() => radCheckAttributes.value.length > 0);
  const hasReplyAttributes = computed(() => radReplyAttributes.value.length > 0);
  const totalAttributes = computed(() => 
    radCheckAttributes.value.length + radReplyAttributes.value.length
  );
  
  const isLoading = computed(() => 
    loading.value || loadingCheck.value || loadingReply.value || submitting.value
  );
  
  // ===== RadCheck Methods =====
  
  /**
   * Load RadCheck attributes with pagination
   */
  const loadRadCheckAttributes = async (params?: RadiusSearchParams) => {
    loadingCheck.value = true;
    error.value = null;
    
    try {
      const searchData = { ...searchParams, ...params };
      const response = await radiusService.getRadCheckAttributes(searchData);
      
      radCheckAttributes.value = response.items;
      checkPagination.total = response.total;
      checkPagination.current = response.page;
      checkPagination.pageSize = response.size;
      
      return response;
    } catch (err: any) {
      error.value = err.message || 'Failed to load RadCheck attributes';
      message.error(error.value);
      throw err;
    } finally {
      loadingCheck.value = false;
    }
  };
  
  /**
   * Get specific RadCheck attribute
   */
  const getRadCheckAttribute = async (id: number) => {
    loading.value = true;
    
    try {
      const attribute = await radiusService.getRadCheckAttribute(id);
      currentCheckAttribute.value = attribute;
      return attribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to get RadCheck attribute';
      message.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Create new RadCheck attribute
   */
  const createRadCheckAttribute = async (data: RadCheckCreate) => {
    submitting.value = true;
    
    try {
      const newAttribute = await radiusService.createRadCheckAttribute(data);
      radCheckAttributes.value.unshift(newAttribute);
      message.success('RadCheck attribute created successfully');
      return newAttribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to create RadCheck attribute';
      message.error(error.value);
      throw err;
    } finally {
      submitting.value = false;
    }
  };
  
  /**
   * Update RadCheck attribute
   */
  const updateRadCheckAttribute = async (id: number, data: RadCheckUpdate) => {
    submitting.value = true;
    
    try {
      const updatedAttribute = await radiusService.updateRadCheckAttribute(id, data);
      
      // Update in the list
      const index = radCheckAttributes.value.findIndex(attr => attr.id === id);
      if (index !== -1) {
        radCheckAttributes.value[index] = updatedAttribute;
      }
      
      // Update current attribute if it's the same
      if (currentCheckAttribute.value?.id === id) {
        currentCheckAttribute.value = updatedAttribute;
      }
      
      message.success('RadCheck attribute updated successfully');
      return updatedAttribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to update RadCheck attribute';
      message.error(error.value);
      throw err;
    } finally {
      submitting.value = false;
    }
  };
  
  /**
   * Delete RadCheck attribute
   */
  const deleteRadCheckAttribute = async (id: number) => {
    loading.value = true;
    
    try {
      await radiusService.deleteRadCheckAttribute(id);
      
      // Remove from list
      radCheckAttributes.value = radCheckAttributes.value.filter(attr => attr.id !== id);
      
      // Clear current attribute if it's the deleted one
      if (currentCheckAttribute.value?.id === id) {
        currentCheckAttribute.value = null;
      }
      
      message.success('RadCheck attribute deleted successfully');
    } catch (err: any) {
      error.value = err.message || 'Failed to delete RadCheck attribute';
      message.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // ===== RadReply Methods =====
  
  /**
   * Load RadReply attributes with pagination
   */
  const loadRadReplyAttributes = async (params?: RadiusSearchParams) => {
    loadingReply.value = true;
    error.value = null;
    
    try {
      const searchData = { ...searchParams, ...params };
      const response = await radiusService.getRadReplyAttributes(searchData);
      
      radReplyAttributes.value = response.items;
      replyPagination.total = response.total;
      replyPagination.current = response.page;
      replyPagination.pageSize = response.size;
      
      return response;
    } catch (err: any) {
      error.value = err.message || 'Failed to load RadReply attributes';
      message.error(error.value);
      throw err;
    } finally {
      loadingReply.value = false;
    }
  };
  
  /**
   * Get specific RadReply attribute
   */
  const getRadReplyAttribute = async (id: number) => {
    loading.value = true;
    
    try {
      const attribute = await radiusService.getRadReplyAttribute(id);
      currentReplyAttribute.value = attribute;
      return attribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to get RadReply attribute';
      message.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Create new RadReply attribute
   */
  const createRadReplyAttribute = async (data: RadReplyCreate) => {
    submitting.value = true;
    
    try {
      const newAttribute = await radiusService.createRadReplyAttribute(data);
      radReplyAttributes.value.unshift(newAttribute);
      message.success('RadReply attribute created successfully');
      return newAttribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to create RadReply attribute';
      message.error(error.value);
      throw err;
    } finally {
      submitting.value = false;
    }
  };
  
  /**
   * Update RadReply attribute
   */
  const updateRadReplyAttribute = async (id: number, data: RadReplyUpdate) => {
    submitting.value = true;
    
    try {
      const updatedAttribute = await radiusService.updateRadReplyAttribute(id, data);
      
      // Update in the list
      const index = radReplyAttributes.value.findIndex(attr => attr.id === id);
      if (index !== -1) {
        radReplyAttributes.value[index] = updatedAttribute;
      }
      
      // Update current attribute if it's the same
      if (currentReplyAttribute.value?.id === id) {
        currentReplyAttribute.value = updatedAttribute;
      }
      
      message.success('RadReply attribute updated successfully');
      return updatedAttribute;
    } catch (err: any) {
      error.value = err.message || 'Failed to update RadReply attribute';
      message.error(error.value);
      throw err;
    } finally {
      submitting.value = false;
    }
  };
  
  /**
   * Delete RadReply attribute
   */
  const deleteRadReplyAttribute = async (id: number) => {
    loading.value = true;
    
    try {
      await radiusService.deleteRadReplyAttribute(id);
      
      // Remove from list
      radReplyAttributes.value = radReplyAttributes.value.filter(attr => attr.id !== id);
      
      // Clear current attribute if it's the deleted one
      if (currentReplyAttribute.value?.id === id) {
        currentReplyAttribute.value = null;
      }
      
      message.success('RadReply attribute deleted successfully');
    } catch (err: any) {
      error.value = err.message || 'Failed to delete RadReply attribute';
      message.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // ===== User-Specific Methods =====
  
  /**
   * Load all attributes for a specific user
   */
  const loadUserAttributes = async (username: string) => {
    loading.value = true;
    
    try {
      const attributes = await radiusService.getUserAttributes(username);
      userAttributes.value = attributes;
      return attributes;
    } catch (err: any) {
      error.value = err.message || 'Failed to load user attributes';
      message.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Set user password
   */
  const setUserPassword = async (username: string, password: string, passwordType?: string) => {
    submitting.value = true;
    
    try {
      const result = await radiusService.setUserPassword(username, {
        password,
        password_type: passwordType
      });
      
      message.success('User password updated successfully');
      
      // Reload user attributes to reflect changes
      if (userAttributes.value?.username === username) {
        await loadUserAttributes(username);
      }
      
      return result;
    } catch (err: any) {
      error.value = err.message || 'Failed to set user password';
      message.error(error.value);
      throw err;
    } finally {
      submitting.value = false;
    }
  };
  
  // ===== Utility Methods =====
  
  /**
   * Load common attributes and operators
   */
  const loadCommonData = async () => {
    try {
      const [operators, checkAttrs, replyAttrs] = await Promise.all([
        radiusService.getRadiusOperators(),
        radiusService.getCommonCheckAttributes(),
        radiusService.getCommonReplyAttributes()
      ]);
      
      radiusOperators.value = operators as RadiusOperator[];
      commonCheckAttributes.value = checkAttrs;
      commonReplyAttributes.value = replyAttrs;
    } catch (err: any) {
      console.error('Failed to load common RADIUS data:', err);
    }
  };
  
  /**
   * Reset search parameters
   */
  const resetSearch = () => {
    Object.assign(searchParams, {
      username: '',
      attribute: '',
      search: '',
      page: 1,
      size: 20
    });
  };
  
  /**
   * Clear all data
   */
  const clearData = () => {
    radCheckAttributes.value = [];
    radReplyAttributes.value = [];
    currentCheckAttribute.value = null;
    currentReplyAttribute.value = null;
    userAttributes.value = null;
    error.value = null;
  };
  
  // ===== Pagination Handlers =====
  
  /**
   * Handle RadCheck pagination change
   */
  const handleCheckPaginationChange = async (page: number, pageSize: number) => {
    await loadRadCheckAttributes({
      ...searchParams,
      page,
      size: pageSize
    });
  };
  
  /**
   * Handle RadReply pagination change
   */
  const handleReplyPaginationChange = async (page: number, pageSize: number) => {
    await loadRadReplyAttributes({
      ...searchParams,
      page,
      size: pageSize
    });
  };
  
  // ===== Search Handlers =====
  
  /**
   * Search both RadCheck and RadReply attributes
   */
  const searchAttributes = async (searchTerm: string) => {
    searchParams.search = searchTerm;
    searchParams.page = 1; // Reset to first page
    
    await Promise.all([
      loadRadCheckAttributes(),
      loadRadReplyAttributes()
    ]);
  };
  
  /**
   * Filter by username
   */
  const filterByUsername = async (username: string) => {
    searchParams.username = username;
    searchParams.page = 1; // Reset to first page
    
    await Promise.all([
      loadRadCheckAttributes(),
      loadRadReplyAttributes()
    ]);
  };
  
  /**
   * Filter by attribute name
   */
  const filterByAttribute = async (attributeName: string) => {
    searchParams.attribute = attributeName;
    searchParams.page = 1; // Reset to first page
    
    await Promise.all([
      loadRadCheckAttributes(),
      loadRadReplyAttributes()
    ]);
  };
  
  // ===== Watchers =====
  
  // Auto-load common data when composable is used
  watch(() => commonCheckAttributes.value, (newVal) => {
    if (!newVal) {
      loadCommonData();
    }
  }, { immediate: true });
  
  // ===== Return Public API =====
  
  return {
    // State
    loading,
    loadingCheck,
    loadingReply,
    submitting,
    radCheckAttributes,
    radReplyAttributes,
    currentCheckAttribute,
    currentReplyAttribute,
    userAttributes,
    checkPagination,
    replyPagination,
    searchParams,
    commonCheckAttributes,
    commonReplyAttributes,
    radiusOperators,
    error,
    
    // Computed
    hasCheckAttributes,
    hasReplyAttributes,
    totalAttributes,
    isLoading,
    
    // RadCheck methods
    loadRadCheckAttributes,
    getRadCheckAttribute,
    createRadCheckAttribute,
    updateRadCheckAttribute,
    deleteRadCheckAttribute,
    
    // RadReply methods
    loadRadReplyAttributes,
    getRadReplyAttribute,
    createRadReplyAttribute,
    updateRadReplyAttribute,
    deleteRadReplyAttribute,
    
    // User methods
    loadUserAttributes,
    setUserPassword,
    
    // Utility methods
    loadCommonData,
    resetSearch,
    clearData,
    
    // Event handlers
    handleCheckPaginationChange,
    handleReplyPaginationChange,
    searchAttributes,
    filterByUsername,
    filterByAttribute
  };
}

// ===== Specialized Composables =====

/**
 * Composable for RadCheck-only operations
 */
export function useRadCheckManagement() {
  const {
    loadingCheck: loading,
    radCheckAttributes: attributes,
    currentCheckAttribute: currentAttribute,
    checkPagination: pagination,
    loadRadCheckAttributes: loadAttributes,
    getRadCheckAttribute: getAttribute,
    createRadCheckAttribute: createAttribute,
    updateRadCheckAttribute: updateAttribute,
    deleteRadCheckAttribute: deleteAttribute,
    handleCheckPaginationChange: handlePaginationChange,
    ...rest
  } = useRadiusManagement();
  
  return {
    loading,
    attributes,
    currentAttribute,
    pagination,
    loadAttributes,
    getAttribute,
    createAttribute,
    updateAttribute,
    deleteAttribute,
    handlePaginationChange,
    ...rest
  };
}

/**
 * Composable for RadReply-only operations
 */
export function useRadReplyManagement() {
  const {
    loadingReply: loading,
    radReplyAttributes: attributes,
    currentReplyAttribute: currentAttribute,
    replyPagination: pagination,
    loadRadReplyAttributes: loadAttributes,
    getRadReplyAttribute: getAttribute,
    createRadReplyAttribute: createAttribute,
    updateRadReplyAttribute: updateAttribute,
    deleteRadReplyAttribute: deleteAttribute,
    handleReplyPaginationChange: handlePaginationChange,
    ...rest
  } = useRadiusManagement();
  
  return {
    loading,
    attributes,
    currentAttribute,
    pagination,
    loadAttributes,
    getAttribute,
    createAttribute,
    updateAttribute,
    deleteAttribute,
    handlePaginationChange,
    ...rest
  };
}

/**
 * Composable for user-specific attribute operations
 */
export function useUserRadiusManagement(username: string) {
  const management = useRadiusManagement();
  
  // Auto-load user attributes when username changes
  watch(() => username, (newUsername) => {
    if (newUsername) {
      management.loadUserAttributes(newUsername);
    }
  }, { immediate: true });
  
  return {
    ...management,
    username
  };
}