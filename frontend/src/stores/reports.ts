/**
 * Reports Store
 * 
 * Pinia store for managing reports state and actions
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { reportsApiService } from '@/services/reports'
import { ReportType, SystemStatus } from '@/types/reports'
import type { LastConnect } from '@/types/reports'
import type {
  // Types
  UpsStatusResponse,
  RaidStatusResponse,
  HeartBeatResponse,
  ReportTemplateResponse,
  ReportGenerationResponse,
  OnlineUserReport,
  HistoryReportItem,
  NewUserReportItem,
  TopUserReportItem,
  SystemLogReportItem,
  BatchReportItem,
  SystemStatusReport,
  ReportsDashboard,
  
  // Create types
  UpsStatusCreate,
  RaidStatusCreate,
  HeartBeatCreate,
  ReportTemplateCreate,
  ReportGenerationCreate,
  
  // Update types
  UpsStatusUpdate,
  RaidStatusUpdate,
  HeartBeatUpdate,
  ReportTemplateUpdate,
  
  // Query types
  OnlineUsersReportQuery,
  HistoryReportQuery,
  NewUsersReportQuery,
  TopUsersReportQuery,
  SystemLogQuery,
  BatchReportQuery
} from '@/types/reports'

export const useReportsStore = defineStore('reports', () => {
  // =============================================================================
  // State
  // =============================================================================

  // UPS Status
  const upsStatusList = ref<UpsStatusResponse[]>([])
  const upsStatusLoading = ref(false)
  const upsSummary = ref<Record<string, unknown>>({})

  // RAID Status
  const raidStatusList = ref<RaidStatusResponse[]>([])
  const raidStatusLoading = ref(false)
  const raidSummary = ref<Record<string, unknown>>({})

  // HeartBeat
  const heartBeatList = ref<HeartBeatResponse[]>([])
  const heartBeatLoading = ref(false)
  const heartBeatSummary = ref<Record<string, unknown>>({})

  // Report Templates
  const reportTemplates = ref<ReportTemplateResponse[]>([])
  const templatesLoading = ref(false)

  // Report Generations
  const reportGenerations = ref<ReportGenerationResponse[]>([])
  const generationsLoading = ref(false)
  const pendingReports = ref<ReportGenerationResponse[]>([])

  // Report Data
  const onlineUsers = ref<OnlineUserReport[]>([])
  const historyReports = ref<HistoryReportItem[]>([])
  const newUsersReports = ref<NewUserReportItem[]>([])
  const topUsersReports = ref<TopUserReportItem[]>([])
  const systemLogsReports = ref<SystemLogReportItem[]>([])
  const batchReports = ref<BatchReportItem[]>([])
  const lastConnectReports = ref<LastConnect[]>([])

  // System Status
  const systemStatusReport = ref<SystemStatusReport | null>(null)
  const reportsDashboard = ref<ReportsDashboard | null>(null)

  // UI State
  const reportDataLoading = ref(false)
  const dashboardLoading = ref(false)
  const selectedReportType = ref<ReportType>(ReportType.ONLINE_USERS)
  const reportFilters = ref<Record<string, unknown>>({})

  // =============================================================================
  // Getters
  // =============================================================================

  const activeUpsDevices = computed(() => 
    upsStatusList.value.filter(ups => ups.status === SystemStatus.ONLINE)
  )

  const offlineUpsDevices = computed(() => 
    upsStatusList.value.filter(ups => ups.status === SystemStatus.OFFLINE)
  )

  const degradedRaidArrays = computed(() => 
    raidStatusList.value.filter(raid => 
      raid.status === SystemStatus.WARNING || raid.failed_disks > 0
    )
  )

  const offlineServices = computed(() => 
    heartBeatList.value.filter(hb => hb.status === SystemStatus.OFFLINE)
  )

  const publicTemplates = computed(() => 
    reportTemplates.value.filter(template => template.is_public && template.is_active)
  )

  const runningReports = computed(() => 
    reportGenerations.value.filter(report => 
      report.status === 'running' || report.status === 'pending'
    )
  )

  const completedReports = computed(() => 
    reportGenerations.value.filter(report => report.status === 'completed')
  )

  const systemHealthScore = computed(() => {
    if (!systemStatusReport.value) return 0
    
    const totalServices = heartBeatList.value.length
    const onlineServices = heartBeatList.value.filter(hb => hb.status === SystemStatus.ONLINE).length
    
    if (totalServices === 0) return 100
    return Math.round((onlineServices / totalServices) * 100)
  })

  // =============================================================================
  // UPS Status Actions
  // =============================================================================

  const fetchUpsStatusList = async () => {
    try {
      upsStatusLoading.value = true
      const data = await reportsApiService.listUpsStatus()
      upsStatusList.value = data
    } catch (error) {
      console.error('Error fetching UPS status list:', error)
      message.error('Failed to fetch UPS status list')
    } finally {
      upsStatusLoading.value = false
    }
  }

  const createUpsStatus = async (data: UpsStatusCreate) => {
    try {
      const newUps = await reportsApiService.createUpsStatus(data)
      upsStatusList.value.push(newUps)
      message.success('UPS status created successfully')
      return newUps
    } catch (error) {
      console.error('Error creating UPS status:', error)
      message.error('Failed to create UPS status')
      throw error
    }
  }

  const updateUpsStatus = async (id: number, data: UpsStatusUpdate) => {
    try {
      const updatedUps = await reportsApiService.updateUpsStatus(id, data)
      const index = upsStatusList.value.findIndex(ups => ups.id === id)
      if (index !== -1) {
        upsStatusList.value[index] = updatedUps
      }
      message.success('UPS status updated successfully')
      return updatedUps
    } catch (error) {
      console.error('Error updating UPS status:', error)
      message.error('Failed to update UPS status')
      throw error
    }
  }

  const deleteUpsStatus = async (id: number) => {
    try {
      await reportsApiService.deleteUpsStatus(id)
      upsStatusList.value = upsStatusList.value.filter(ups => ups.id !== id)
      message.success('UPS status deleted successfully')
    } catch (error) {
      console.error('Error deleting UPS status:', error)
      message.error('Failed to delete UPS status')
      throw error
    }
  }

  const fetchUpsSummary = async () => {
    try {
      const data = await reportsApiService.getUpsSummary()
      upsSummary.value = data
    } catch (error) {
      console.error('Error fetching UPS summary:', error)
    }
  }

  // =============================================================================
  // RAID Status Actions
  // =============================================================================

  const fetchRaidStatusList = async () => {
    try {
      raidStatusLoading.value = true
      const data = await reportsApiService.listRaidStatus()
      raidStatusList.value = data
    } catch (error) {
      console.error('Error fetching RAID status list:', error)
      message.error('Failed to fetch RAID status list')
    } finally {
      raidStatusLoading.value = false
    }
  }

  const createRaidStatus = async (data: RaidStatusCreate) => {
    try {
      const newRaid = await reportsApiService.createRaidStatus(data)
      raidStatusList.value.push(newRaid)
      message.success('RAID status created successfully')
      return newRaid
    } catch (error) {
      console.error('Error creating RAID status:', error)
      message.error('Failed to create RAID status')
      throw error
    }
  }

  const updateRaidStatus = async (id: number, data: RaidStatusUpdate) => {
    try {
      const updatedRaid = await reportsApiService.updateRaidStatus(id, data)
      const index = raidStatusList.value.findIndex(raid => raid.id === id)
      if (index !== -1) {
        raidStatusList.value[index] = updatedRaid
      }
      message.success('RAID status updated successfully')
      return updatedRaid
    } catch (error) {
      console.error('Error updating RAID status:', error)
      message.error('Failed to update RAID status')
      throw error
    }
  }

  const deleteRaidStatus = async (id: number) => {
    try {
      await reportsApiService.deleteRaidStatus(id)
      raidStatusList.value = raidStatusList.value.filter(raid => raid.id !== id)
      message.success('RAID status deleted successfully')
    } catch (error) {
      console.error('Error deleting RAID status:', error)
      message.error('Failed to delete RAID status')
      throw error
    }
  }

  const fetchRaidSummary = async () => {
    try {
      const data = await reportsApiService.getRaidSummary()
      raidSummary.value = data
    } catch (error) {
      console.error('Error fetching RAID summary:', error)
    }
  }

  // =============================================================================
  // HeartBeat Actions
  // =============================================================================

  const fetchHeartBeatList = async () => {
    try {
      heartBeatLoading.value = true
      const data = await reportsApiService.listHeartBeats()
      heartBeatList.value = data
    } catch (error) {
      console.error('Error fetching HeartBeat list:', error)
      message.error('Failed to fetch HeartBeat list')
    } finally {
      heartBeatLoading.value = false
    }
  }

  const createHeartBeat = async (data: HeartBeatCreate) => {
    try {
      const newHeartBeat = await reportsApiService.createHeartBeat(data)
      heartBeatList.value.push(newHeartBeat)
      message.success('HeartBeat created successfully')
      return newHeartBeat
    } catch (error) {
      console.error('Error creating HeartBeat:', error)
      message.error('Failed to create HeartBeat')
      throw error
    }
  }

  const updateHeartBeat = async (id: number, data: HeartBeatUpdate) => {
    try {
      const updatedHeartBeat = await reportsApiService.updateHeartBeat(id, data)
      const index = heartBeatList.value.findIndex(hb => hb.id === id)
      if (index !== -1) {
        heartBeatList.value[index] = updatedHeartBeat
      }
      message.success('HeartBeat updated successfully')
      return updatedHeartBeat
    } catch (error) {
      console.error('Error updating HeartBeat:', error)
      message.error('Failed to update HeartBeat')
      throw error
    }
  }

  const deleteHeartBeat = async (id: number) => {
    try {
      await reportsApiService.deleteHeartBeat(id)
      heartBeatList.value = heartBeatList.value.filter(hb => hb.id !== id)
      message.success('HeartBeat deleted successfully')
    } catch (error) {
      console.error('Error deleting HeartBeat:', error)
      message.error('Failed to delete HeartBeat')
      throw error
    }
  }

  const fetchHeartBeatSummary = async () => {
    try {
      const data = await reportsApiService.getHeartBeatSummary()
      heartBeatSummary.value = data
    } catch (error) {
      console.error('Error fetching HeartBeat summary:', error)
    }
  }

  // =============================================================================
  // Report Template Actions
  // =============================================================================

  const fetchReportTemplates = async () => {
    try {
      templatesLoading.value = true
      const data = await reportsApiService.listReportTemplates()
      reportTemplates.value = data
    } catch (error) {
      console.error('Error fetching report templates:', error)
      message.error('Failed to fetch report templates')
    } finally {
      templatesLoading.value = false
    }
  }

  const createReportTemplate = async (data: ReportTemplateCreate) => {
    try {
      const newTemplate = await reportsApiService.createReportTemplate(data)
      reportTemplates.value.push(newTemplate)
      message.success('Report template created successfully')
      return newTemplate
    } catch (error) {
      console.error('Error creating report template:', error)
      message.error('Failed to create report template')
      throw error
    }
  }

  const updateReportTemplate = async (id: number, data: ReportTemplateUpdate) => {
    try {
      const updatedTemplate = await reportsApiService.updateReportTemplate(id, data)
      const index = reportTemplates.value.findIndex(template => template.id === id)
      if (index !== -1) {
        reportTemplates.value[index] = updatedTemplate
      }
      message.success('Report template updated successfully')
      return updatedTemplate
    } catch (error) {
      console.error('Error updating report template:', error)
      message.error('Failed to update report template')
      throw error
    }
  }

  const deleteReportTemplate = async (id: number) => {
    try {
      await reportsApiService.deleteReportTemplate(id)
      reportTemplates.value = reportTemplates.value.filter(template => template.id !== id)
      message.success('Report template deleted successfully')
    } catch (error) {
      console.error('Error deleting report template:', error)
      message.error('Failed to delete report template')
      throw error
    }
  }

  // =============================================================================
  // Report Generation Actions
  // =============================================================================

  const createReportGeneration = async (data: ReportGenerationCreate) => {
    try {
      const newGeneration = await reportsApiService.createReportGeneration(data)
      reportGenerations.value.unshift(newGeneration)
      message.success('Report generation started successfully')
      return newGeneration
    } catch (error) {
      console.error('Error creating report generation:', error)
      message.error('Failed to start report generation')
      throw error
    }
  }

  const fetchUserReportGenerations = async (username: string) => {
    try {
      generationsLoading.value = true
      const data = await reportsApiService.getUserReportGenerations(username)
      reportGenerations.value = data
    } catch (error) {
      console.error('Error fetching user report generations:', error)
      message.error('Failed to fetch report generations')
    } finally {
      generationsLoading.value = false
    }
  }

  const fetchPendingReports = async () => {
    try {
      const data = await reportsApiService.getPendingReports()
      pendingReports.value = data
    } catch (error) {
      console.error('Error fetching pending reports:', error)
    }
  }

  const pollReportStatus = async (generationId: number) => {
    try {
      const report = await reportsApiService.getReportGeneration(generationId)
      const index = reportGenerations.value.findIndex(r => r.id === generationId)
      if (index !== -1) {
        reportGenerations.value[index] = report
      }
      return report
    } catch (error) {
      console.error('Error polling report status:', error)
      throw error
    }
  }

  // =============================================================================
  // Report Data Actions
  // =============================================================================

  const fetchOnlineUsersReport = async (query?: OnlineUsersReportQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getOnlineUsersReport(query)
      onlineUsers.value = data
    } catch (error) {
      console.error('Error fetching online users report:', error)
      message.error('Failed to fetch online users report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchHistoryReport = async (query?: HistoryReportQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getHistoryReport(query)
      historyReports.value = data
    } catch (error) {
      console.error('Error fetching history report:', error)
      message.error('Failed to fetch history report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchLastConnectReport = async (limit = 100) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getLastConnectReport(limit)
      lastConnectReports.value = data as unknown as LastConnect[]
    } catch (error) {
      console.error('Error fetching last connect report:', error)
      message.error('Failed to fetch last connect report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchNewUsersReport = async (query?: NewUsersReportQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getNewUsersReport(query)
      newUsersReports.value = data
    } catch (error) {
      console.error('Error fetching new users report:', error)
      message.error('Failed to fetch new users report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchTopUsersReport = async (query?: TopUsersReportQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getTopUsersReport(query)
      topUsersReports.value = data
    } catch (error) {
      console.error('Error fetching top users report:', error)
      message.error('Failed to fetch top users report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchSystemLogsReport = async (query?: SystemLogQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getSystemLogsReport(query)
      systemLogsReports.value = data
    } catch (error) {
      console.error('Error fetching system logs report:', error)
      message.error('Failed to fetch system logs report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchBatchReport = async (query?: BatchReportQuery) => {
    try {
      reportDataLoading.value = true
      const data = await reportsApiService.getBatchReport(query)
      batchReports.value = data
    } catch (error) {
      console.error('Error fetching batch report:', error)
      message.error('Failed to fetch batch report')
    } finally {
      reportDataLoading.value = false
    }
  }

  const fetchSystemStatusReport = async () => {
    try {
      const data = await reportsApiService.getSystemStatusReport()
      systemStatusReport.value = data
    } catch (error) {
      console.error('Error fetching system status report:', error)
      message.error('Failed to fetch system status report')
    }
  }

  const fetchReportsDashboard = async () => {
    try {
      dashboardLoading.value = true
      const data = await reportsApiService.getReportsDashboard()
      reportsDashboard.value = data
    } catch (error) {
      console.error('Error fetching reports dashboard:', error)
      message.error('Failed to fetch reports dashboard')
    } finally {
      dashboardLoading.value = false
    }
  }

  // =============================================================================
  // Utility Actions
  // =============================================================================

  const exportReport = async (
    reportType: string,
    format: 'csv' | 'excel' | 'pdf' | 'json',
    query?: Record<string, unknown>
  ) => {
    try {
      const blob = await reportsApiService.exportReport(reportType, format, query)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${reportType}_report.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('Report exported successfully')
    } catch (error) {
      console.error('Error exporting report:', error)
      message.error('Failed to export report')
      throw error
    }
  }

  const downloadReportFile = async (generationId: number, filename?: string) => {
    try {
      const blob = await reportsApiService.downloadReportFile(generationId)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || `report_${generationId}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('Report downloaded successfully')
    } catch (error) {
      console.error('Error downloading report:', error)
      message.error('Failed to download report')
      throw error
    }
  }

  const refreshAllSystemData = async () => {
    await Promise.all([
      fetchUpsStatusList(),
      fetchRaidStatusList(),
      fetchHeartBeatList(),
      fetchUpsSummary(),
      fetchRaidSummary(),
      fetchHeartBeatSummary(),
      fetchSystemStatusReport()
    ])
  }

  const setReportType = (type: ReportType) => {
    selectedReportType.value = type
  }

  const setReportFilters = (filters: Record<string, unknown>) => {
    reportFilters.value = filters
  }

  const clearReportData = () => {
    onlineUsers.value = []
    historyReports.value = []
    newUsersReports.value = []
    topUsersReports.value = []
    systemLogsReports.value = []
    batchReports.value = []
    lastConnectReports.value = []
  }

  // =============================================================================
  // Return store interface
  // =============================================================================

  return {
    // State
    upsStatusList,
    upsStatusLoading,
    upsSummary,
    raidStatusList,
    raidStatusLoading,
    raidSummary,
    heartBeatList,
    heartBeatLoading,
    heartBeatSummary,
    reportTemplates,
    templatesLoading,
    reportGenerations,
    generationsLoading,
    pendingReports,
    onlineUsers,
    historyReports,
    newUsersReports,
    topUsersReports,
    systemLogsReports,
    batchReports,
    lastConnectReports,
    systemStatusReport,
    reportsDashboard,
    reportDataLoading,
    dashboardLoading,
    selectedReportType,
    reportFilters,

    // Getters
    activeUpsDevices,
    offlineUpsDevices,
    degradedRaidArrays,
    offlineServices,
    publicTemplates,
    runningReports,
    completedReports,
    systemHealthScore,

    // Actions
    fetchUpsStatusList,
    createUpsStatus,
    updateUpsStatus,
    deleteUpsStatus,
    fetchUpsSummary,
    fetchRaidStatusList,
    createRaidStatus,
    updateRaidStatus,
    deleteRaidStatus,
    fetchRaidSummary,
    fetchHeartBeatList,
    createHeartBeat,
    updateHeartBeat,
    deleteHeartBeat,
    fetchHeartBeatSummary,
    fetchReportTemplates,
    createReportTemplate,
    updateReportTemplate,
    deleteReportTemplate,
    createReportGeneration,
    fetchUserReportGenerations,
    fetchPendingReports,
    pollReportStatus,
    fetchOnlineUsersReport,
    fetchHistoryReport,
    fetchLastConnectReport,
    fetchNewUsersReport,
    fetchTopUsersReport,
    fetchSystemLogsReport,
    fetchBatchReport,
    fetchSystemStatusReport,
    fetchReportsDashboard,
    exportReport,
    downloadReportFile,
    refreshAllSystemData,
    setReportType,
    setReportFilters,
    clearReportData
  }
})