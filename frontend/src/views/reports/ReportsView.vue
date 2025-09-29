<template>
  <div class="reports-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1>报表中心</h1>
          <p class="page-description">数据统计和分析报表管理</p>
        </div>
        <div class="header-actions">
          <a-button type="primary" @click="showCreateModal = true">
            <template #icon><PlusOutlined /></template>
            创建报表
          </a-button>
          <a-button @click="showTemplateModal = true">
            <template #icon><FileTextOutlined /></template>
            报表模板
          </a-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        title="总报表数"
        :value="total"
        :loading="loading"
        color="blue"
        icon="file-text"
      />
      <StatCard
        title="活跃报表"
        :value="activeReportsCount"
        :loading="loading"
        color="green"
        icon="check-circle"
      />
      <StatCard
        title="草稿报表"
        :value="draftReportsCount"
        :loading="loading"
        color="orange"
        icon="edit"
      />
      <StatCard
        title="本月生成"
        :value="monthlyGeneratedCount"
        :loading="loading"
        color="purple"
        icon="bar-chart"
      />
    </div>

    <!-- 搜索和工具栏 -->
    <a-card class="search-card">
      <SearchForm
        v-model:values="searchParams"
        :fields="searchFields"
        @search="searchReports"
        @reset="resetSearch"
      />
      
      <div class="table-toolbar">
        <div class="toolbar-left">
          <span v-if="hasSelection" class="selection-info">
            已选择 {{ selectionCount }} 项
          </span>
        </div>
        <div class="toolbar-right">
          <a-button
            v-if="hasSelection"
            danger
            @click="handleBatchDelete"
            :loading="loading"
          >
            <template #icon><DeleteOutlined /></template>
            批量删除
          </a-button>
          <a-button @click="fetchReports" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 报表列表 -->
    <a-card title="报表列表">
      <DataTable
        :columns="columns"
        :data="reports"
        :loading="loading"
        :pagination="{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 项，共 ${total} 项`
        }"
        :row-selection="{
          selectedRowKeys: selectedReports,
          onChange: (keys) => selectedReports = keys,
          onSelectAll: toggleAllSelection
        }"
        @change="handleTableChange"
      >
        <!-- 报表类型 -->
        <template #type="{ record }">
          <a-tag color="blue">
            {{ getTypeText(record.type) }}
          </a-tag>
        </template>

        <!-- 报表状态 -->
        <template #status="{ record }">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>

        <!-- 最后运行时间 -->
        <template #lastRunTime="{ record }">
          {{ record.lastRunTime || '-' }}
        </template>

        <!-- 操作列 -->
        <template #actions="{ record }">
          <div class="action-buttons">
            <a-button
              type="link"
              size="small"
              @click="viewReport(record)"
            >
              查看
            </a-button>
            <a-button
              type="link"
              size="small"
              @click="generateReportData(record)"
              :loading="generating"
            >
              生成
            </a-button>
            <a-dropdown>
              <a-button type="link" size="small">
                更多
                <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="editReport(record)">
                    <EditOutlined /> 编辑
                  </a-menu-item>
                  <a-menu-item @click="duplicateReport(record)">
                    <CopyOutlined /> 复制
                  </a-menu-item>
                  <a-menu-item @click="scheduleReport(record)">
                    <ClockCircleOutlined /> 定时任务
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="deleteReport(record.id)" danger>
                    <DeleteOutlined /> 删除
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </template>
      </DataTable>
    </a-card>

    <!-- 报表详情抽屉 -->
    <a-drawer
      v-model:open="showDetailDrawer"
      title="报表详情"
      :width="700"
      placement="right"
    >
      <ReportDetail
        v-if="selectedReport"
        :report="selectedReport"
        @edit="editReport"
        @generate="generateReportData"
        @delete="deleteReport"
      />
    </a-drawer>

    <!-- 创建报表模态框 -->
    <a-modal
      v-model:open="showCreateModal"
      title="创建报表"
      :width="900"
      :footer="null"
    >
      <ReportForm
        @submit="handleCreateReport"
        @cancel="showCreateModal = false"
      />
    </a-modal>

    <!-- 编辑报表模态框 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑报表"
      :width="900"
      :footer="null"
    >
      <ReportForm
        v-if="editingReport"
        :report="editingReport"
        @submit="handleUpdateReport"
        @cancel="showEditModal = false"
      />
    </a-modal>

    <!-- 报表生成结果模态框 -->
    <a-modal
      v-model:open="showResultModal"
      :title="`报表生成结果 - ${reportData?.reportName}`"
      :width="1200"
      :footer="null"
      class="report-result-modal"
    >
      <ReportResult
        v-if="reportData"
        :report-data="reportData"
        @export="handleExportReport"
      />
    </a-modal>

    <!-- 报表模板模态框 -->
    <a-modal
      v-model:open="showTemplateModal"
      title="报表模板"
      :width="1000"
      :footer="null"
    >
      <ReportTemplates
        @select="handleSelectTemplate"
        @close="showTemplateModal = false"
      />
    </a-modal>

    <!-- 定时任务配置模态框 -->
    <a-modal
      v-model:open="showScheduleModal"
      title="定时任务配置"
      :width="600"
      :footer="null"
    >
      <ReportSchedule
        v-if="schedulingReport"
        :report="schedulingReport"
        @submit="handleScheduleReport"
        @cancel="showScheduleModal = false"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  EditOutlined,
  CopyOutlined,
  ClockCircleOutlined,
  DownOutlined
} from '@ant-design/icons-vue';
import DataTable from '@/components/common/DataTable.vue';
import SearchForm from '@/components/common/SearchForm.vue';
import StatCard from '@/components/common/StatCard.vue';
import ReportDetail from '@/components/reports/ReportDetail.vue';
import ReportForm from '@/components/reports/ReportForm.vue';
import ReportResult from '@/components/reports/ReportResult.vue';
import ReportTemplates from '@/components/reports/ReportTemplates.vue';
import ReportSchedule from '@/components/reports/ReportSchedule.vue';
import { useReportManagement, useReportGeneration } from '@/composables/useReportManagement';
import type { 
  Report, 
  CreateReportRequest, 
  UpdateReportRequest, 
  ReportType, 
  ReportStatus, 
  ReportFormat 
} from '@/types/report';
import { REPORT_TYPE_OPTIONS, REPORT_STATUS_OPTIONS } from '@/types/report';

// 组合式函数
const {
  reports,
  loading,
  total,
  currentPage,
  pageSize,
  searchParams,
  selectedReports,
  selectedReport,
  hasSelection,
  selectionCount,
  fetchReports,
  createReport,
  updateReport,
  deleteReport: deleteReportById,
  deleteSelectedReports,
  searchReports,
  resetSearch,
  onPageChange,
  toggleAllSelection,
  clearSelection
} = useReportManagement();

const {
  reportData,
  generating,
  exporting,
  generateReport,
  exportReport,
  clearReportData
} = useReportGeneration();

// 响应式状态
const showDetailDrawer = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showResultModal = ref(false);
const showTemplateModal = ref(false);
const showScheduleModal = ref(false);
const editingReport = ref<Report | null>(null);
const schedulingReport = ref<Report | null>(null);

// 模拟统计数据
const monthlyGeneratedCount = ref(45);

// 计算属性
const activeReportsCount = computed(() => 
  reports.value.filter(r => r.status === 'active').length
);

const draftReportsCount = computed(() => 
  reports.value.filter(r => r.status === 'draft').length
);

// 搜索字段配置
const searchFields = [
  {
    key: 'name',
    label: '报表名称',
    type: 'input',
    placeholder: '请输入报表名称'
  },
  {
    key: 'type',
    label: '报表类型',
    type: 'select',
    options: REPORT_TYPE_OPTIONS
  },
  {
    key: 'status',
    label: '报表状态',
    type: 'select',
    options: REPORT_STATUS_OPTIONS
  },
  {
    key: 'createdBy',
    label: '创建人',
    type: 'input',
    placeholder: '请输入创建人'
  }
];

// 表格列配置
const columns = [
  {
    title: '报表名称',
    dataIndex: 'name',
    key: 'name',
    sorter: true,
    width: 200
  },
  {
    title: '报表类型',
    dataIndex: 'type',
    key: 'type',
    slots: { customRender: 'type' },
    width: 120
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    slots: { customRender: 'status' },
    width: 100
  },
  {
    title: '创建人',
    dataIndex: 'createdBy',
    key: 'createdBy',
    width: 100
  },
  {
    title: '最后运行',
    dataIndex: 'lastRunTime',
    key: 'lastRunTime',
    slots: { customRender: 'lastRunTime' },
    width: 160
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    key: 'createTime',
    sorter: true,
    width: 160
  },
  {
    title: '操作',
    key: 'actions',
    slots: { customRender: 'actions' },
    width: 150,
    fixed: 'right'
  }
];

// 事件处理
const handleTableChange = ({ current, pageSize: size }: any) => {
  onPageChange(current, size);
};

const viewReport = (report: Report) => {
  selectedReport.value = report;
  showDetailDrawer.value = true;
};

const editReport = (report: Report) => {
  editingReport.value = report;
  showEditModal.value = true;
};

const handleCreateReport = async (data: CreateReportRequest) => {
  try {
    await createReport(data);
    showCreateModal.value = false;
  } catch (error) {
    console.error(error);
  }
};

const handleUpdateReport = async (data: UpdateReportRequest) => {
  if (!editingReport.value) return;
  
  try {
    await updateReport(editingReport.value.id, data);
    showEditModal.value = false;
    editingReport.value = null;
  } catch (error) {
    console.error(error);
  }
};

const deleteReport = (reportId: string) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个报表吗？删除后无法恢复。',
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => deleteReportById(reportId)
  });
};

const handleBatchDelete = () => {
  if (selectedReports.value.length === 0) {
    message.warning('请先选择要删除的报表');
    return;
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedReports.value.length} 个报表吗？删除后无法恢复。`,
    okText: '确定',
    cancelText: '取消',
    okType: 'danger',
    onOk: deleteSelectedReports
  });
};

const generateReportData = async (report: Report) => {
  try {
    // 这里可以添加参数输入对话框
    const request = {
      reportId: report.id,
      parameters: {}, // 实际应该从用户输入获取
      format: 'json' as ReportFormat
    };
    
    const data = await generateReport(request);
    showResultModal.value = true;
  } catch (error) {
    console.error(error);
  }
};

const duplicateReport = async (report: Report) => {
  try {
    const duplicateData = {
      ...report,
      name: `${report.name} - 副本`,
      status: 'draft' as ReportStatus
    };
    
    await createReport(duplicateData);
    message.success('报表复制成功');
  } catch (error) {
    console.error(error);
  }
};

const scheduleReport = (report: Report) => {
  schedulingReport.value = report;
  showScheduleModal.value = true;
};

const handleScheduleReport = (scheduleData: any) => {
  message.success('定时任务配置成功');
  showScheduleModal.value = false;
  schedulingReport.value = null;
};

const handleSelectTemplate = (template: any) => {
  // 基于模板创建报表
  const templateData = {
    name: `基于${template.name}的报表`,
    type: template.type,
    description: template.description,
    parameters: template.parameters,
    templateId: template.id
  };
  
  showTemplateModal.value = false;
  // 可以直接创建或打开表单预填充数据
  handleCreateReport(templateData);
};

const handleExportReport = (format: ReportFormat) => {
  if (!reportData.value) return;
  exportReport(reportData.value.reportId, format, reportData.value);
};

// 工具函数
const getTypeText = (type: ReportType): string => {
  const typeMap = {
    user_usage: '用户使用统计',
    traffic_analysis: '流量分析',
    revenue_statistics: '收入统计',
    device_performance: '设备性能',
    session_analysis: '会话分析',
    billing_summary: '计费汇总',
    custom_query: '自定义查询'
  };
  return typeMap[type] || type;
};

const getStatusColor = (status: ReportStatus): string => {
  const colorMap = {
    draft: 'default',
    active: 'green',
    paused: 'orange',
    archived: 'red'
  };
  return colorMap[status] || 'default';
};

const getStatusText = (status: ReportStatus): string => {
  const textMap = {
    draft: '草稿',
    active: '活跃',
    paused: '暂停',
    archived: '归档'
  };
  return textMap[status] || status;
};

// 生命周期
onMounted(() => {
  fetchReports();
});
</script>

<style scoped>
.reports-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.page-description {
  margin: 8px 0 0 0;
  color: rgba(0, 0, 0, 0.65);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.search-card {
  margin-bottom: 24px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-info {
  color: #1890ff;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons .ant-btn-link {
  padding: 0;
  height: auto;
}

.report-result-modal :deep(.ant-modal-body) {
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}
</style>