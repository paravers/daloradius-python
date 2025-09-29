<!-- 设备统计组件 -->
<template>
  <div class="device-statistics">
    <a-spin :spinning="loading">
      <!-- 统计概览 -->
      <div class="stats-overview">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-statistic
              title="总用户数"
              :value="statistics?.totalUsers || 0"
              :precision="0"
              style="text-align: center"
            >
              <template #prefix>
                <UserOutlined style="color: #1890ff" />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="活跃用户"
              :value="statistics?.activeUsers || 0"
              :precision="0"
              style="text-align: center"
            >
              <template #prefix>
                <TeamOutlined style="color: #52c41a" />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="总会话数"
              :value="statistics?.totalSessions || 0"
              :precision="0"
              style="text-align: center"
            >
              <template #prefix>
                <LinkOutlined style="color: #722ed1" />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="活跃会话"
              :value="statistics?.activeSessions || 0"
              :precision="0"
              style="text-align: center"
            >
              <template #prefix>
                <ApiOutlined style="color: #fa8c16" />
              </template>
            </a-statistic>
          </a-col>
        </a-row>
      </div>

      <!-- 流量统计 -->
      <div class="traffic-stats">
        <h3>流量统计</h3>
        <a-row :gutter="24">
          <a-col :span="12">
            <div class="traffic-item">
              <div class="traffic-label">
                <ArrowUpOutlined style="color: #1890ff; margin-right: 8px;" />
                上行流量
              </div>
              <div class="traffic-value">
                {{ formatTraffic(statistics?.totalTraffic?.upload || 0) }}
              </div>
            </div>
          </a-col>
          <a-col :span="12">
            <div class="traffic-item">
              <div class="traffic-label">
                <ArrowDownOutlined style="color: #52c41a; margin-right: 8px;" />
                下行流量
              </div>
              <div class="traffic-value">
                {{ formatTraffic(statistics?.totalTraffic?.download || 0) }}
              </div>
            </div>
          </a-col>
        </a-row>
      </div>

      <!-- 运行时间和最后活动 -->
      <div class="uptime-stats">
        <h3>运行状态</h3>
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="运行时间">
            <a-tag color="green">
              {{ formatUptime(statistics?.uptime || 0) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="最后活动">
            {{ statistics?.lastActivity || '-' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <!-- 流量趋势图表 -->
      <div class="traffic-chart">
        <h3>流量趋势（最近7天）</h3>
        <div class="chart-container">
          <a-empty v-if="!chartData.length" description="暂无图表数据" />
          <div v-else ref="chartRef" class="chart"></div>
        </div>
      </div>

      <!-- 会话趋势图表 -->
      <div class="session-chart">
        <h3>会话趋势（最近24小时）</h3>
        <div class="chart-container">
          <a-empty v-if="!sessionChartData.length" description="暂无图表数据" />
          <div v-else ref="sessionChartRef" class="chart"></div>
        </div>
      </div>

      <!-- 详细信息表格 -->
      <div class="detail-table">
        <h3>详细统计</h3>
        <a-table
          :columns="detailColumns"
          :data-source="detailData"
          :pagination="false"
          size="small"
          bordered
        >
          <template #value="{ record }">
            <span v-if="record.type === 'traffic'">
              {{ formatTraffic(record.value) }}
            </span>
            <span v-else-if="record.type === 'time'">
              {{ formatUptime(record.value) }}
            </span>
            <span v-else>
              {{ record.value }}
            </span>
          </template>
        </a-table>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import {
  UserOutlined,
  TeamOutlined,
  LinkOutlined,
  ApiOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design-icons-vue';
import { useDeviceStatistics } from '@/composables/useDeviceManagement';
import * as echarts from 'echarts';

interface Props {
  deviceId: string;
}

const props = defineProps<Props>();

const { statistics, loading, fetchStatistics, formatTraffic, formatUptime } = useDeviceStatistics();

// 图表相关
const chartRef = ref<HTMLDivElement>();
const sessionChartRef = ref<HTMLDivElement>();
const chartData = ref<any[]>([]);
const sessionChartData = ref<any[]>([]);

// 详细信息表格配置
const detailColumns = [
  {
    title: '指标',
    dataIndex: 'label',
    key: 'label',
    width: 200
  },
  {
    title: '数值',
    dataIndex: 'value',
    key: 'value',
    slots: { customRender: 'value' }
  },
  {
    title: '说明',
    dataIndex: 'description',
    key: 'description'
  }
];

// 详细数据
const detailData = computed(() => {
  if (!statistics.value) return [];
  
  const stats = statistics.value;
  return [
    {
      label: '设备名称',
      value: stats.deviceName,
      description: '设备的唯一标识名称',
      type: 'text'
    },
    {
      label: '总用户数',
      value: stats.totalUsers,
      description: '在此设备上注册的用户总数',
      type: 'number'
    },
    {
      label: '活跃用户数',
      value: stats.activeUsers,
      description: '当前在线或最近活跃的用户数',
      type: 'number'
    },
    {
      label: '总会话数',
      value: stats.totalSessions,
      description: '历史累计会话连接数',
      type: 'number'
    },
    {
      label: '活跃会话数',
      value: stats.activeSessions,
      description: '当前正在进行的会话数',
      type: 'number'
    },
    {
      label: '上行流量',
      value: stats.totalTraffic?.upload || 0,
      description: '设备累计上传流量',
      type: 'traffic'
    },
    {
      label: '下行流量',
      value: stats.totalTraffic?.download || 0,
      description: '设备累计下载流量',
      type: 'traffic'
    },
    {
      label: '运行时间',
      value: stats.uptime || 0,
      description: '设备持续运行的时间',
      type: 'time'
    },
    {
      label: '最后活动时间',
      value: stats.lastActivity,
      description: '设备最后一次记录活动的时间',
      type: 'text'
    }
  ];
});

// 生成模拟图表数据
const generateChartData = () => {
  // 流量趋势数据（最近7天）
  chartData.value = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toLocaleDateString(),
      upload: Math.floor(Math.random() * 100) + 50,
      download: Math.floor(Math.random() * 300) + 100
    };
  });

  // 会话趋势数据（最近24小时）
  sessionChartData.value = Array.from({ length: 24 }, (_, i) => {
    return {
      hour: `${i.toString().padStart(2, '0')}:00`,
      sessions: Math.floor(Math.random() * 50) + 10,
      users: Math.floor(Math.random() * 30) + 5
    };
  });
};

// 初始化流量图表
const initTrafficChart = () => {
  if (!chartRef.value) return;

  const chart = echarts.init(chartRef.value);
  
  const option = {
    title: {
      text: '流量趋势',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue;
        let content = `${date}<br/>`;
        params.forEach((item: any) => {
          content += `${item.marker}${item.seriesName}: ${formatTraffic(item.value * 1024 * 1024)}<br/>`;
        });
        return content;
      }
    },
    legend: {
      data: ['上行流量', '下行流量']
    },
    xAxis: {
      type: 'category',
      data: chartData.value.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: 'MB',
      axisLabel: {
        formatter: '{value} MB'
      }
    },
    series: [
      {
        name: '上行流量',
        type: 'line',
        data: chartData.value.map(item => item.upload),
        smooth: true,
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '下行流量',
        type: 'line',
        data: chartData.value.map(item => item.download),
        smooth: true,
        itemStyle: { color: '#52c41a' }
      }
    ]
  };

  chart.setOption(option);
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize();
  });
};

// 初始化会话图表
const initSessionChart = () => {
  if (!sessionChartRef.value) return;

  const chart = echarts.init(sessionChartRef.value);
  
  const option = {
    title: {
      text: '会话趋势',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['活跃会话', '在线用户']
    },
    xAxis: {
      type: 'category',
      data: sessionChartData.value.map(item => item.hour)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '活跃会话',
        type: 'bar',
        data: sessionChartData.value.map(item => item.sessions),
        itemStyle: { color: '#722ed1' }
      },
      {
        name: '在线用户',
        type: 'line',
        data: sessionChartData.value.map(item => item.users),
        smooth: true,
        itemStyle: { color: '#fa8c16' }
      }
    ]
  };

  chart.setOption(option);
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize();
  });
};

// 生命周期
onMounted(async () => {
  await fetchStatistics(props.deviceId);
  generateChartData();
  
  await nextTick();
  initTrafficChart();
  initSessionChart();
});
</script>

<style scoped>
.device-statistics {
  padding: 0;
}

.stats-overview {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.traffic-stats,
.uptime-stats,
.traffic-chart,
.session-chart,
.detail-table {
  margin-bottom: 24px;
}

.traffic-stats h3,
.uptime-stats h3,
.traffic-chart h3,
.session-chart h3,
.detail-table h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.traffic-item {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
  text-align: center;
}

.traffic-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.traffic-value {
  font-size: 20px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.chart-container {
  height: 300px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.chart {
  width: 100%;
  height: 100%;
}

:deep(.ant-statistic-title) {
  font-size: 14px;
}

:deep(.ant-statistic-content) {
  font-size: 20px;
}
</style>