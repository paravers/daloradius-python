<template>
  <div class="billing-plan-detail">
    <!-- 计划概览 -->
    <div class="detail-header">
      <div class="plan-info">
        <h2 class="plan-name">
          {{ plan.name }}
          <Badge 
            :status="plan.active ? 'success' : 'default'"
            :text="plan.active ? '激活' : '停用'"
          />
        </h2>
        <p class="plan-description">{{ plan.description || '暂无描述' }}</p>
        <div class="plan-meta">
          <Tag :color="getPlanTypeColor(plan.type)">
            {{ getPlanTypeText(plan.type) }}
          </Tag>
          <span class="meta-item">
            <Icon name="Calendar" />
            创建于 {{ formatDate(plan.createdAt) }}
          </span>
          <span class="meta-item">
            <Icon name="RefreshCw" />
            更新于 {{ formatDate(plan.updatedAt) }}
          </span>
        </div>
      </div>
      <div class="header-actions">
        <Button @click="$emit('edit', plan)">
          <Icon name="Edit" />
          编辑计划
        </Button>
        <Button @click="$emit('close')">
          关闭
        </Button>
      </div>
    </div>

    <!-- 详细信息 -->
    <div class="detail-content">
      <!-- 基本信息卡片 -->
      <Card title="基本信息" class="info-card">
        <div class="info-grid">
          <div class="info-item">
            <label>计划名称</label>
            <span>{{ plan.name }}</span>
          </div>
          <div class="info-item">
            <label>计划类型</label>
            <Tag :color="getPlanTypeColor(plan.type)">
              {{ getPlanTypeText(plan.type) }}
            </Tag>
          </div>
          <div class="info-item">
            <label>状态</label>
            <Badge 
              :status="plan.active ? 'success' : 'default'"
              :text="plan.active ? '激活' : '停用'"
            />
          </div>
          <div class="info-item">
            <label>最大用户数</label>
            <span>{{ plan.maxUsers?.toLocaleString() || '无限制' }}</span>
          </div>
          <div class="info-item">
            <label>生效时间</label>
            <span>{{ formatDateTime(plan.validFrom) }}</span>
          </div>
          <div class="info-item">
            <label>失效时间</label>
            <span>{{ plan.validTo ? formatDateTime(plan.validTo) : '永久有效' }}</span>
          </div>
        </div>
        <div v-if="plan.description" class="description-section">
          <label>计划描述</label>
          <p>{{ plan.description }}</p>
        </div>
      </Card>

      <!-- 费率配置卡片 -->
      <Card title="费率配置" class="rates-card">
        <div v-if="plan.rates && plan.rates.length > 0" class="rates-container">
          <div
            v-for="(rate, index) in plan.rates"
            :key="rate.id || index"
            class="rate-item"
          >
            <div class="rate-header">
              <h4 class="rate-name">{{ rate.name }}</h4>
              <Tag :color="getRateTypeColor(rate.type)">
                {{ getRateTypeText(rate.type) }}
              </Tag>
            </div>
            <div class="rate-details">
              <div class="rate-price">
                <label>单价</label>
                <span class="price-value">
                  {{ formatMoney(rate.unitPrice) }}
                </span>
              </div>
              <div class="rate-validity">
                <label>生效时间</label>
                <span>{{ formatDateTime(rate.validFrom) }}</span>
              </div>
            </div>

            <!-- 阶梯费率详情 -->
            <div v-if="rate.type === 'tiered' && rate.tierRates" class="tier-rates-section">
              <h5>阶梯费率</h5>
              <div class="tier-rates-table">
                <div class="tier-header-row">
                  <span>起始值</span>
                  <span>结束值</span>
                  <span>单价</span>
                </div>
                <div
                  v-for="(tier, tierIndex) in rate.tierRates"
                  :key="tierIndex"
                  class="tier-row"
                >
                  <span>{{ formatDataSize(tier.from) }}</span>
                  <span>{{ tier.to ? formatDataSize(tier.to) : '无上限' }}</span>
                  <span>{{ formatMoney(tier.price) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <Empty v-else description="暂无费率配置" />
      </Card>

      <!-- 功能特性卡片 -->
      <Card v-if="plan.features && plan.features.length > 0" title="功能特性" class="features-card">
        <div class="features-list">
          <Tag
            v-for="feature in plan.features"
            :key="feature"
            class="feature-tag"
          >
            <Icon name="Check" />
            {{ feature }}
          </Tag>
        </div>
      </Card>

      <!-- 使用统计卡片（模拟数据） -->
      <Card title="使用统计" class="stats-card">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ mockStats.userCount }}</div>
            <div class="stat-label">当前用户数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatMoney(mockStats.monthlyRevenue) }}</div>
            <div class="stat-label">月度收入</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ mockStats.usageRate }}%</div>
            <div class="stat-label">使用率</div>
          </div>
        </div>
      </Card>

      <!-- 费用计算器 -->
      <Card title="费用计算器" class="calculator-card">
        <div class="calculator-form">
          <div class="form-row">
            <div class="form-item">
              <label>数据流量 (GB)</label>
              <InputNumber
                v-model:value="calculator.dataUsage"
                :min="0"
                :precision="2"
                placeholder="输入数据流量"
                style="width: 100%"
              />
            </div>
            <div class="form-item">
              <label>使用时长 (小时)</label>
              <InputNumber
                v-model:value="calculator.duration"
                :min="0"
                :precision="1"
                placeholder="输入使用时长"
                style="width: 100%"
              />
            </div>
            <div class="form-item">
              <Button
                type="primary"
                @click="calculateCost"
                :loading="calculating"
              >
                计算费用
              </Button>
            </div>
          </div>
          <div v-if="calculatedCost" class="calculation-result">
            <Alert
              :message="`预估费用: ${formatMoney(calculatedCost)}`"
              type="info"
              show-icon
            />
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { BillingPlan, Money, UsageData } from '@/types/billing'
import { useBillingCalculation } from '@/composables/useBillingPlans'
import { formatDateTime } from '@/utils/date'
import { 
  Card, 
  Badge, 
  Tag, 
  Button, 
  Empty,
  InputNumber,
  Alert
} from 'ant-design-vue'
import Icon from '@/components/common/Icon.vue'

// 组件属性
interface Props {
  plan: BillingPlan
}

const props = defineProps<Props>()

// 组件事件
interface Emits {
  (e: 'edit', plan: BillingPlan): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

// 费用计算组合式函数
const { calculateCost: calculateCostService } = useBillingCalculation()

// 响应式状态
const calculating = ref(false)
const calculatedCost = ref<Money | null>(null)

// 计算器表单
const calculator = reactive({
  dataUsage: 0,
  duration: 0
})

// 模拟统计数据
const mockStats = reactive({
  userCount: Math.floor(Math.random() * 1000) + 100,
  monthlyRevenue: {
    amount: Math.floor(Math.random() * 100000) + 10000,
    currency: 'CNY' as const
  },
  usageRate: Math.floor(Math.random() * 80) + 20
})

// 计算费用
async function calculateCost() {
  if (!calculator.dataUsage && !calculator.duration) {
    return
  }

  try {
    calculating.value = true
    
    const usage: UsageData = {
      sessionTime: calculator.duration * 3600, // 转换为秒
      dataTransfer: {
        total: calculator.dataUsage * 1024 * 1024 * 1024, // 转换为字节
        upload: (calculator.dataUsage * 1024 * 1024 * 1024) / 2,
        download: (calculator.dataUsage * 1024 * 1024 * 1024) / 2
      },
      sessionCount: 1,
      peakBandwidth: 10 * 1024 * 1024, // 10 Mbps
      period: {
        start: new Date().toISOString(),
        end: new Date().toISOString()
      }
    }

    calculatedCost.value = await calculateCostService(props.plan.id, usage)
  } catch (error) {
    console.error('费用计算失败:', error)
    calculatedCost.value = null
  } finally {
    calculating.value = false
  }
}

// 工具函数
function getPlanTypeColor(type: string): string {
  const colors: Record<string, string> = {
    monthly: 'blue',
    usage: 'green', 
    hybrid: 'orange',
    prepaid: 'purple',
    postpaid: 'red'
  }
  return colors[type] || 'default'
}

function getPlanTypeText(type: string): string {
  const texts: Record<string, string> = {
    monthly: '月租',
    usage: '按量计费',
    hybrid: '混合计费',
    prepaid: '预付费',
    postpaid: '后付费'
  }
  return texts[type] || type
}

function getRateTypeColor(type: string): string {
  const colors: Record<string, string> = {
    fixed: 'blue',
    volume: 'green',
    tiered: 'orange',
    bandwidth: 'purple',
    time_based: 'cyan'
  }
  return colors[type] || 'default'
}

function getRateTypeText(type: string): string {
  const texts: Record<string, string> = {
    fixed: '固定费用',
    volume: '流量计费',
    tiered: '阶梯计费',
    bandwidth: '带宽计费',
    time_based: '时长计费'
  }
  return texts[type] || type
}

function formatDate(dateString: string): string {
  return formatDateTime(dateString, 'YYYY-MM-DD')
}

function formatMoney(money: Money): string {
  return `${money.amount.toLocaleString()} ${money.currency}`
}

function formatDataSize(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  if (bytes === 0) return '0 B'
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = bytes / Math.pow(1024, i)
  
  return `${size.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`
}
</script>

<style scoped>
.billing-plan-detail {
  max-width: 100%;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.plan-info {
  flex: 1;
}

.plan-name {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.plan-description {
  margin: 0 0 12px 0;
  color: #8c8c8c;
  font-size: 14px;
}

.plan-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8c8c8c;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.detail-content {
  display: grid;
  gap: 24px;
}

.info-card,
.rates-card,
.features-card,
.stats-card,
.calculator-card {
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 500;
}

.info-item span {
  font-size: 14px;
  color: #262626;
}

.description-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.description-section label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 500;
}

.description-section p {
  margin: 0;
  color: #262626;
  line-height: 1.6;
}

.rates-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rate-item {
  padding: 16px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
}

.rate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rate-name {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.rate-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
}

.rate-details > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rate-details label {
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 500;
}

.price-value {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
}

.tier-rates-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8e8e8;
}

.tier-rates-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #595959;
}

.tier-rates-table {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.tier-header-row,
.tier-row {
  display: contents;
}

.tier-header-row span {
  padding: 8px 12px;
  background: #fafafa;
  font-size: 12px;
  font-weight: 500;
  color: #8c8c8c;
}

.tier-row span {
  padding: 8px 12px;
  background: white;
  font-size: 12px;
  color: #262626;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #389e0d;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
}

.calculator-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-item label {
  font-size: 12px;
  color: #8c8c8c;
  font-weight: 500;
}

.calculation-result {
  padding: 16px;
  background: #f6ffed;
  border-radius: 6px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .plan-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .tier-rates-table {
    grid-template-columns: 1fr;
  }
  
  .tier-header-row span:not(:first-child),
  .tier-row span:not(:first-child) {
    display: none;
  }
}
</style>