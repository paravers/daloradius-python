<template>
  <div class="online-users-monitor">
    <a-card title="在线用户监控" :loading="loading">
      <template #extra>
        <a-space>
          <a-switch 
            v-model:checked="autoRefresh" 
            checked-children="自动刷新" 
            un-checked-children="手动刷新"
            @change="handleAutoRefreshChange"
          />
          <a-button 
            :icon="h(ReloadOutlined)" 
            @click="refreshData"
            :loading="loading"
          >
            刷新
          </a-button>
        </a-space>
      </template>

      <!-- 统计信息 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <a-statistic
          title="总在线用户"
          :value="statistics.totalOnline"
          :value-style="{ color: '#1890ff' }"
        >
          <template #prefix>
            <user-outlined />
          </template>
        </a-statistic>

        <a-statistic
          title="活跃连接"
          :value="statistics.activeConnections"
          :value-style="{ color: '#52c41a' }"
        >
          <template #prefix>
            <wifi-outlined />
          </template>
        </a-statistic>

        <a-statistic
          title="平均会话时长"
          :value="statistics.avgSessionDuration"
          suffix="分钟"
          :value-style="{ color: '#722ed1' }"
        >
          <template #prefix>
            <clock-circle-outlined />
          </template>
        </a-statistic>

        <a-statistic
          title="峰值并发"
          :value="statistics.peakConcurrent"
          :value-style="{ color: '#fa541c' }"
        >
          <template #prefix>
            <bar-chart-outlined />
          </template>
        </a-statistic>
      </div>

      <!-- 筛选器 -->
      <div class="mb-4 p-4 bg-gray-50 rounded">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-input
              v-model:value="filters.username"
              placeholder="搜索用户名"
              :prefix="h(SearchOutlined)"
              @press-enter="applyFilters"
            />
          </a-col>
          <a-col :span="6">
            <a-select
              v-model:value="filters.connectionType"
              placeholder="连接类型"
              style="width: 100%"
              allow-clear
            >
              <a-select-option value="pppoe">PPPoE</a-select-option>
              <a-select-option value="hotspot">Hotspot</a-select-option>
              <a-select-option value="vpn">VPN</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-select
              v-model:value="filters.nasId"
              placeholder="NAS设备"
              style="width: 100%"
              allow-clear
            >
              <a-select-option 
                v-for="nas in nasDevices"
                :key="nas.id"
                :value="nas.id"
              >
                {{ nas.name }}
              </a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <a-button type="primary" @click="applyFilters">
              筛选
            </a-button>
            <a-button class="ml-2" @click="resetFilters">
              重置
            </a-button>
          </a-col>
        </a-row>
      </div>

      <!-- 在线用户表格 -->
      <a-table
        :columns="columns"
        :data-source="onlineUsers"
        :loading="loading"
        :pagination="paginationConfig"
        row-key="sessionId"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-badge 
              :status="record.status === 'online' ? 'processing' : 'default'"
              :text="record.status === 'online' ? '在线' : '离线'"
            />
          </template>

          <template v-else-if="column.key === 'connectionType'">
            <a-tag :color="getConnectionTypeColor(record.connectionType)">
              {{ getConnectionTypeText(record.connectionType) }}
            </a-tag>
          </template>

          <template v-else-if="column.key === 'duration'">
            {{ formatDuration(record.startTime) }}
          </template>

          <template v-else-if="column.key === 'traffic'">
            <div class="text-xs">
              <div class="text-green-600">↓ {{ formatBytes(record.inputBytes) }}</div>
              <div class="text-red-600">↑ {{ formatBytes(record.outputBytes) }}</div>
            </div>
          </template>

          <template v-else-if="column.key === 'actions'">
            <a-space size="small">
              <a-tooltip title="查看详情">
                <a-button 
                  type="text" 
                  :icon="h(EyeOutlined)" 
                  size="small"
                  @click="viewSessionDetail(record)"
                />
              </a-tooltip>
              
              <a-tooltip title="踢下线">
                <a-button 
                  type="text" 
                  danger
                  :icon="h(DisconnectOutlined)" 
                  size="small"
                  @click="disconnectUser(record)"
                />
              </a-tooltip>

              <a-tooltip title="发送消息">
                <a-button 
                  type="text" 
                  :icon="h(MessageOutlined)" 
                  size="small"
                  @click="sendMessage(record)"
                />
              </a-tooltip>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 会话详情弹窗 -->
      <a-modal
        v-model:open="detailVisible"
        title="会话详情"
        :width="800"
        :footer="null"
      >
        <a-descriptions 
          v-if="selectedSession"
          :column="2" 
          bordered
          size="small"
        >
          <a-descriptions-item label="会话ID">
            {{ selectedSession.sessionId }}
          </a-descriptions-item>
          <a-descriptions-item label="用户名">
            {{ selectedSession.username }}
          </a-descriptions-item>
          <a-descriptions-item label="IP地址">
            {{ selectedSession.framedIpAddress }}
          </a-descriptions-item>
          <a-descriptions-item label="MAC地址">
            {{ selectedSession.callingStationId }}
          </a-descriptions-item>
          <a-descriptions-item label="NAS设备">
            {{ selectedSession.nasIpAddress }}
          </a-descriptions-item>
          <a-descriptions-item label="NAS端口">
            {{ selectedSession.nasPortId }}
          </a-descriptions-item>
          <a-descriptions-item label="连接类型">
            {{ getConnectionTypeText(selectedSession.connectionType) }}
          </a-descriptions-item>
          <a-descriptions-item label="服务类型">
            {{ selectedSession.serviceType }}
          </a-descriptions-item>
          <a-descriptions-item label="开始时间">
            {{ formatDateTime(selectedSession.startTime) }}
          </a-descriptions-item>
          <a-descriptions-item label="会话时长">
            {{ formatDuration(selectedSession.startTime) }}
          </a-descriptions-item>
          <a-descriptions-item label="上行流量">
            <span class="text-red-600">{{ formatBytes(selectedSession.outputBytes) }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="下行流量">
            <span class="text-green-600">{{ formatBytes(selectedSession.inputBytes) }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </a-modal>

      <!-- 发送消息弹窗 -->
      <a-modal
        v-model:open="messageVisible"
        title="发送消息"
        @ok="handleSendMessage"
        :confirm-loading="sendingMessage"
      >
        <a-form layout="vertical">
          <a-form-item label="收件人">
            <a-input 
              :value="messageTarget?.username" 
              readonly 
            />
          </a-form-item>
          <a-form-item label="消息内容" required>
            <a-textarea
              v-model:value="messageContent"
              :rows="4"
              placeholder="请输入要发送的消息..."
              :maxlength="500"
              show-count
            />
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, h } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  UserOutlined,
  WifiOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  DisconnectOutlined,
  MessageOutlined
} from '@ant-design/icons-vue'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

interface OnlineUser {
  sessionId: string
  username: string
  framedIpAddress: string
  callingStationId: string
  nasIpAddress: string
  nasPortId: string
  connectionType: string
  serviceType: string
  startTime: string
  inputBytes: number
  outputBytes: number
  status: 'online' | 'offline'
}

interface NasDevice {
  id: string
  name: string
  ipAddress: string
}

// 响应式数据
const loading = ref(false)
const autoRefresh = ref(true)
const refreshTimer = ref<NodeJS.Timeout>()

const onlineUsers = ref<OnlineUser[]>([])
const nasDevices = ref<NasDevice[]>([])

// 统计信息
const statistics = reactive({
  totalOnline: 0,
  activeConnections: 0,
  avgSessionDuration: 0,
  peakConcurrent: 0
})

// 筛选器
const filters = reactive({
  username: '',
  connectionType: undefined,
  nasId: undefined
})

// 分页配置
const paginationConfig = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`
})

// 弹窗状态
const detailVisible = ref(false)
const messageVisible = ref(false)
const selectedSession = ref<OnlineUser | null>(null)
const messageTarget = ref<OnlineUser | null>(null)
const messageContent = ref('')
const sendingMessage = ref(false)

// 表格列配置
const columns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 120,
    fixed: 'left'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80
  },
  {
    title: 'IP地址',
    dataIndex: 'framedIpAddress',
    key: 'framedIpAddress',
    width: 120
  },
  {
    title: 'MAC地址',
    dataIndex: 'callingStationId',
    key: 'callingStationId',
    width: 140
  },
  {
    title: 'NAS设备',
    dataIndex: 'nasIpAddress',
    key: 'nasIpAddress',
    width: 120
  },
  {
    title: '连接类型',
    dataIndex: 'connectionType',
    key: 'connectionType',
    width: 100
  },
  {
    title: '会话时长',
    dataIndex: 'duration',
    key: 'duration',
    width: 100
  },
  {
    title: '流量统计',
    dataIndex: 'traffic',
    key: 'traffic',
    width: 120
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    fixed: 'right'
  }
]

// 获取在线用户数据
const fetchOnlineUsers = async () => {
  try {
    loading.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    const mockUsers: OnlineUser[] = [
      {
        sessionId: 'sess_001',
        username: 'user001',
        framedIpAddress: '192.168.1.100',
        callingStationId: '00:11:22:33:44:55',
        nasIpAddress: '192.168.1.1',
        nasPortId: 'eth0/1',
        connectionType: 'pppoe',
        serviceType: 'Framed-User',
        startTime: new Date(Date.now() - 3600000).toISOString(),
        inputBytes: 1024 * 1024 * 100,
        outputBytes: 1024 * 1024 * 50,
        status: 'online'
      },
      {
        sessionId: 'sess_002',
        username: 'user002',
        framedIpAddress: '192.168.1.101',
        callingStationId: '00:11:22:33:44:56',
        nasIpAddress: '192.168.1.2',
        nasPortId: 'eth0/2',
        connectionType: 'hotspot',
        serviceType: 'Login-User',
        startTime: new Date(Date.now() - 1800000).toISOString(),
        inputBytes: 1024 * 1024 * 200,
        outputBytes: 1024 * 1024 * 80,
        status: 'online'
      }
    ]
    
    onlineUsers.value = mockUsers
    paginationConfig.total = mockUsers.length
    
    // 更新统计信息
    statistics.totalOnline = mockUsers.length
    statistics.activeConnections = mockUsers.filter(u => u.status === 'online').length
    statistics.avgSessionDuration = 65
    statistics.peakConcurrent = 150
    
  } catch (error) {
    message.error('获取在线用户数据失败')
  } finally {
    loading.value = false
  }
}

// 获取NAS设备列表
const fetchNasDevices = async () => {
  try {
    // 模拟API调用
    nasDevices.value = [
      { id: 'nas1', name: 'NAS-01', ipAddress: '192.168.1.1' },
      { id: 'nas2', name: 'NAS-02', ipAddress: '192.168.1.2' },
      { id: 'nas3', name: 'NAS-03', ipAddress: '192.168.1.3' }
    ]
  } catch (error) {
    console.error('获取NAS设备列表失败:', error)
  }
}

// 应用筛选器
const applyFilters = () => {
  // 这里应该根据筛选条件重新获取数据
  console.log('应用筛选器:', filters)
  fetchOnlineUsers()
}

// 重置筛选器
const resetFilters = () => {
  filters.username = ''
  filters.connectionType = undefined
  filters.nasId = undefined
  fetchOnlineUsers()
}

// 刷新数据
const refreshData = () => {
  fetchOnlineUsers()
}

// 处理自动刷新
const handleAutoRefreshChange = (checked: boolean) => {
  if (checked) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

// 开始自动刷新
const startAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  
  refreshTimer.value = setInterval(() => {
    fetchOnlineUsers()
  }, 30000) // 30秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = undefined
  }
}

// 查看会话详情
const viewSessionDetail = (record: OnlineUser) => {
  selectedSession.value = record
  detailVisible.value = true
}

// 踢下线
const disconnectUser = (record: OnlineUser) => {
  Modal.confirm({
    title: '确认踢下线',
    content: `确定要将用户 "${record.username}" 踢下线吗？`,
    onOk: async () => {
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        message.success('用户已被踢下线')
        refreshData()
      } catch (error) {
        message.error('操作失败')
      }
    }
  })
}

// 发送消息
const sendMessage = (record: OnlineUser) => {
  messageTarget.value = record
  messageContent.value = ''
  messageVisible.value = true
}

// 处理发送消息
const handleSendMessage = async () => {
  if (!messageContent.value.trim()) {
    message.warning('请输入消息内容')
    return
  }

  try {
    sendingMessage.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    message.success('消息发送成功')
    messageVisible.value = false
  } catch (error) {
    message.error('消息发送失败')
  } finally {
    sendingMessage.value = false
  }
}

// 辅助函数
const getConnectionTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    pppoe: 'blue',
    hotspot: 'green',
    vpn: 'purple'
  }
  return colorMap[type] || 'default'
}

const getConnectionTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    pppoe: 'PPPoE',
    hotspot: 'Hotspot',
    vpn: 'VPN'
  }
  return textMap[type] || type
}

const formatDuration = (startTime: string) => {
  return formatDistanceToNow(new Date(startTime), { locale: zhCN })
}

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchOnlineUsers()
  fetchNasDevices()
  
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.online-users-monitor {
  padding: 24px;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.gap-4 {
  gap: 1rem;
}
</style>