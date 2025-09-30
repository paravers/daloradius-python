/**
 * Accounting Store
 * 
 * Pinia store for managing accounting/session statistics data and state
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  AccountingSession,
  AccountingState,
  AccountingQuery,
  AccountingOverview,
  TopUsersReport,
  SessionStatistics,
  ActiveSessionStatistics,
  TrafficStatistics,
  UserTrafficSummary,
  NasTrafficSummary,
  NasUsageReport,
  PaginatedAccountingResponse,
  PaginatedTopUsersResponse,
  AccountingApiParams,
  ReportFilters,
  CustomQueryRequest,
  MaintenanceRequest,
  AccountingTimeRangeEnum
} from '@/types/accounting'
import { accountingService } from '@/services/accounting'

export const useAccountingStore = defineStore('accounting', () => {
  // =====================================================================
  // State
  // =====================================================================

  // Session data
  const sessions = ref<AccountingSession[]>([])
  const activeSessions = ref<AccountingSession[]>([])
  const recentSessions = ref<AccountingSession[]>([])
  const selectedSession = ref<AccountingSession | null>(null)

  // Pagination
  const sessionsPagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  })

  const activeSessionsPagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  })

  // Statistics
  const overview = ref<AccountingOverview | null>(null)
  const sessionStatistics = ref<SessionStatistics>({
    total_sessions: 0,
    active_sessions: 0,
    completed_sessions: 0,
    average_session_duration: 0,
    total_session_time: 0,
    unique_users: 0
  })

  const activeSessionStatistics = ref<ActiveSessionStatistics>({
    total_active: 0,
    total_current_traffic: 0,
    unique_users: 0,
    average_session_duration: 0
  })

  // Reports
  const topUsers = ref<TopUsersReport[]>([])
  const overviewReport = ref<AccountingOverview | null>(null)
  const topUsersReport = ref<TopUsersReport[]>([])
  const trafficAnalysisReport = ref<any>(null)
  const nasUsageReport = ref<NasUsageReport[]>([])
  const timeAnalysisReport = ref<any>(null)

  // Traffic summaries
  const userTrafficSummaries = ref<UserTrafficSummary[]>([])
  const nasTrafficSummaries = ref<NasTrafficSummary[]>([])

  // Loading states
  const loading = ref({
    sessions: false,
    activeSessions: false,
    overview: false,
    reports: false,
    export: false
  })

  // Error state
  const error = ref<string | null>(null)

  // =====================================================================
  // Getters
  // =====================================================================

  const totalSessions = computed(() => sessions.value.length)
  const totalActiveSessions = computed(() => activeSessions.value.length)
  
  const sessionsByStatus = computed(() => ({
    active: sessions.value.filter(s => s.is_active).length,
    completed: sessions.value.filter(s => !s.is_active).length
  }))

  const totalTraffic = computed(() => {
    return sessions.value.reduce((total, session) => total + (session.total_bytes || 0), 0)
  })

  const averageSessionDuration = computed(() => {
    const totalDuration = sessions.value.reduce((total, session) => total + (session.acctsessiontime || 0), 0)
    return sessions.value.length > 0 ? totalDuration / sessions.value.length : 0
  })

  const isLoading = computed(() => {
    return Object.values(loading.value).some(state => state)
  })

  // =====================================================================
  // Actions
  // =====================================================================

  /**
   * Set error state
   */
  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Reset store to initial state
   */
  const reset = () => {
    sessions.value = []
    activeSessions.value = []
    recentSessions.value = []
    selectedSession.value = null
    overview.value = null
    topUsers.value = []
    error.value = null
    
    // Reset pagination
    sessionsPagination.value = {
      page: 1,
      page_size: 20,
      total: 0,
      total_pages: 0,
      has_next: false,
      has_prev: false
    }
    
    // Reset loading states
    Object.keys(loading.value).forEach(key => {
      loading.value[key as keyof typeof loading.value] = false
    })
  }

  // =====================================================================
  // Session Management Actions
  // =====================================================================

  /**
   * Fetch accounting sessions with pagination and filtering
   */
  const fetchSessions = async (query: AccountingQuery): Promise<void> => {
    try {
      loading.value.sessions = true
      clearError()

      const response = await accountingService.getSessions(query)
      
      sessions.value = response.data
      sessionsPagination.value = {
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages,
        has_next: response.has_next,
        has_prev: response.has_prev
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sessions')
      throw err
    } finally {
      loading.value.sessions = false
    }
  }

  /**
   * Fetch session by ID
   */
  const fetchSessionById = async (sessionId: number): Promise<AccountingSession> => {
    try {
      const session = await accountingService.getSessionById(sessionId)
      selectedSession.value = session
      return session
    } catch (err: any) {
      setError(err.message || 'Failed to fetch session')
      throw err
    }
  }

  /**
   * Fetch active sessions
   */
  const fetchActiveSessions = async (params: AccountingApiParams['activeSessions'] = {}): Promise<void> => {
    try {
      loading.value.activeSessions = true
      clearError()

      const response = await accountingService.getActiveSessions(params)
      
      activeSessions.value = response.data
      activeSessionsPagination.value = {
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages,
        has_next: response.has_next,
        has_prev: response.has_prev
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch active sessions')
      throw err
    } finally {
      loading.value.activeSessions = false
    }
  }

  /**
   * Fetch recent sessions for dashboard
   */
  const fetchRecentSessions = async (params: { page?: number; page_size?: number } = {}): Promise<void> => {
    try {
      const query: AccountingQuery = {
        page: params.page || 1,
        page_size: params.page_size || 5,
        sort_field: 'acctstarttime',
        sort_order: 'desc'
      }
      
      const response = await accountingService.getSessions(query)
      recentSessions.value = response.data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch recent sessions')
      throw err
    }
  }

  /**
   * Fetch user sessions
   */
  const fetchUserSessions = async (
    username: string, 
    params: { page?: number; page_size?: number; date_from?: string; date_to?: string } = {}
  ): Promise<PaginatedAccountingResponse> => {
    try {
      loading.value.sessions = true
      return await accountingService.getUserSessions(username, params)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user sessions')
      throw err
    } finally {
      loading.value.sessions = false
    }
  }

  // =====================================================================
  // Statistics Actions
  // =====================================================================

  /**
   * Fetch accounting overview
   */
  const fetchOverview = async (params: AccountingApiParams['overview'] = {}): Promise<void> => {
    try {
      loading.value.overview = true
      clearError()

      const data = await accountingService.getOverview(params)
      overview.value = data
      
      // Update local statistics
      sessionStatistics.value = data.session_stats
    } catch (err: any) {
      setError(err.message || 'Failed to fetch overview')
      throw err
    } finally {
      loading.value.overview = false
    }
  }

  // =====================================================================
  // Reports Actions
  // =====================================================================

  /**
   * Fetch top users report
   */
  const fetchTopUsers = async (params: AccountingApiParams['topUsers'] = {}): Promise<void> => {
    try {
      loading.value.reports = true
      clearError()

      const response = await accountingService.getTopUsersReport(params)
      topUsers.value = response.data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch top users')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  /**
   * Fetch overview report
   */
  const fetchOverviewReport = async (filters: ReportFilters): Promise<void> => {
    try {
      loading.value.reports = true
      const data = await accountingService.getOverview(filters)
      overviewReport.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch overview report')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  /**
   * Fetch top users report with pagination
   */
  const fetchTopUsersReport = async (params: AccountingApiParams['topUsers'] = {}): Promise<void> => {
    try {
      loading.value.reports = true
      const response = await accountingService.getTopUsersReport(params)
      topUsersReport.value = response.data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch top users report')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  /**
   * Fetch traffic analysis report
   */
  const fetchTrafficAnalysisReport = async (filters: ReportFilters): Promise<void> => {
    try {
      loading.value.reports = true
      const data = await accountingService.getHourlyTrafficReport(filters)
      trafficAnalysisReport.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch traffic analysis report')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  /**
   * Fetch NAS usage report
   */
  const fetchNasUsageReport = async (filters: ReportFilters): Promise<void> => {
    try {
      loading.value.reports = true
      const data = await accountingService.getNasUsageReport(filters)
      nasUsageReport.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch NAS usage report')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  /**
   * Fetch time analysis report
   */
  const fetchTimeAnalysisReport = async (filters: ReportFilters): Promise<void> => {
    try {
      loading.value.reports = true
      const data = await accountingService.getHourlyTrafficReport(filters)
      timeAnalysisReport.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch time analysis report')
      throw err
    } finally {
      loading.value.reports = false
    }
  }

  // =====================================================================
  // Traffic Summary Actions
  // =====================================================================

  /**
   * Fetch user traffic summary
   */
  const fetchUserTrafficSummary = async (
    username: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<void> => {
    try {
      const data = await accountingService.getUserTrafficSummary(username, dateFrom, dateTo)
      userTrafficSummaries.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user traffic summary')
      throw err
    }
  }

  /**
   * Fetch NAS traffic summary
   */
  const fetchNasTrafficSummary = async (
    nasIpAddress: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<void> => {
    try {
      const data = await accountingService.getNasTrafficSummary(nasIpAddress, dateFrom, dateTo)
      nasTrafficSummaries.value = data
    } catch (err: any) {
      setError(err.message || 'Failed to fetch NAS traffic summary')
      throw err
    }
  }

  // =====================================================================
  // Advanced Actions
  // =====================================================================

  /**
   * Execute custom query
   */
  const executeCustomQuery = async (request: CustomQueryRequest): Promise<any> => {
    try {
      return await accountingService.executeCustomQuery(request)
    } catch (err: any) {
      setError(err.message || 'Failed to execute custom query')
      throw err
    }
  }

  /**
   * Cleanup old sessions
   */
  const cleanupOldSessions = async (request: MaintenanceRequest): Promise<any> => {
    try {
      return await accountingService.cleanupOldSessions(request)
    } catch (err: any) {
      setError(err.message || 'Failed to cleanup old sessions')
      throw err
    }
  }

  /**
   * Disconnect session
   */
  const disconnectSession = async (sessionId: number): Promise<void> => {
    try {
      await accountingService.disconnectSession(sessionId)
      // Refresh active sessions after disconnect
      await fetchActiveSessions()
    } catch (err: any) {
      setError(err.message || 'Failed to disconnect session')
      throw err
    }
  }

  /**
   * Terminate session
   */
  const terminateSession = async (sessionId: number): Promise<void> => {
    try {
      await accountingService.terminateSession(sessionId)
      // Refresh active sessions after termination
      await fetchActiveSessions()
    } catch (err: any) {
      setError(err.message || 'Failed to terminate session')
      throw err
    }
  }

  // =====================================================================
  // Export Actions
  // =====================================================================

  /**
   * Export sessions
   */
  const exportSessions = async (params: { filters?: any; format?: string }): Promise<void> => {
    try {
      loading.value.export = true
      await accountingService.exportSessions(params)
    } catch (err: any) {
      setError(err.message || 'Failed to export sessions')
      throw err
    } finally {
      loading.value.export = false
    }
  }

  /**
   * Export report
   */
  const exportReport = async (params: AccountingApiParams['export']): Promise<void> => {
    try {
      loading.value.export = true
      await accountingService.exportReport(params)
    } catch (err: any) {
      setError(err.message || 'Failed to export report')
      throw err
    } finally {
      loading.value.export = false
    }
  }

  /**
   * Export all reports
   */
  const exportAllReports = async (params: { format?: string; filters?: any }): Promise<void> => {
    try {
      loading.value.export = true
      await accountingService.exportAllReports(params)
    } catch (err: any) {
      setError(err.message || 'Failed to export all reports')
      throw err
    } finally {
      loading.value.export = false
    }
  }

  // =====================================================================
  // Utility Actions
  // =====================================================================

  /**
   * Refresh all dashboard data
   */
  const refreshDashboard = async (): Promise<void> => {
    await Promise.allSettled([
      fetchOverview(),
      fetchRecentSessions({ page_size: 5 }),
      fetchTopUsers({ limit: 5 })
    ])
  }

  /**
   * Set selected session
   */
  const setSelectedSession = (session: AccountingSession | null) => {
    selectedSession.value = session
  }

  /**
   * Update session in local state
   */
  const updateSession = (updatedSession: AccountingSession) => {
    // Update in sessions array
    const sessionIndex = sessions.value.findIndex(s => s.radacctid === updatedSession.radacctid)
    if (sessionIndex !== -1) {
      sessions.value[sessionIndex] = updatedSession
    }

    // Update in active sessions array
    const activeSessionIndex = activeSessions.value.findIndex(s => s.radacctid === updatedSession.radacctid)
    if (activeSessionIndex !== -1) {
      activeSessions.value[activeSessionIndex] = updatedSession
    }

    // Update selected session if it matches
    if (selectedSession.value?.radacctid === updatedSession.radacctid) {
      selectedSession.value = updatedSession
    }
  }

  /**
   * Remove session from local state
   */
  const removeSession = (sessionId: number) => {
    sessions.value = sessions.value.filter(s => s.radacctid !== sessionId)
    activeSessions.value = activeSessions.value.filter(s => s.radacctid !== sessionId)
    recentSessions.value = recentSessions.value.filter(s => s.radacctid !== sessionId)
    
    if (selectedSession.value?.radacctid === sessionId) {
      selectedSession.value = null
    }
  }

  // =====================================================================
  // Return store interface
  // =====================================================================

  return {
    // State
    sessions,
    activeSessions,
    recentSessions,
    selectedSession,
    sessionsPagination,
    activeSessionsPagination,
    overview,
    sessionStatistics,
    activeSessionStatistics,
    topUsers,
    overviewReport,
    topUsersReport,
    trafficAnalysisReport,
    nasUsageReport,
    timeAnalysisReport,
    userTrafficSummaries,
    nasTrafficSummaries,
    loading,
    error,

    // Getters
    totalSessions,
    totalActiveSessions,
    sessionsByStatus,
    totalTraffic,
    averageSessionDuration,
    isLoading,

    // Actions
    setError,
    clearError,
    reset,
    
    // Session actions
    fetchSessions,
    fetchSessionById,
    fetchActiveSessions,
    fetchRecentSessions,
    fetchUserSessions,
    
    // Statistics actions
    fetchOverview,
    
    // Reports actions
    fetchTopUsers,
    fetchOverviewReport,
    fetchTopUsersReport,
    fetchTrafficAnalysisReport,
    fetchNasUsageReport,
    fetchTimeAnalysisReport,
    
    // Traffic summary actions
    fetchUserTrafficSummary,
    fetchNasTrafficSummary,
    
    // Advanced actions
    executeCustomQuery,
    cleanupOldSessions,
    disconnectSession,
    terminateSession,
    
    // Export actions
    exportSessions,
    exportReport,
    exportAllReports,
    
    // Utility actions
    refreshDashboard,
    setSelectedSession,
    updateSession,
    removeSession
  }
})