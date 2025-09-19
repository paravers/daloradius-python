# home-main.php 分析报告

## 模块概述

### 职责
系统主要仪表板页面，展示 RADIUS 服务的关键统计信息、最近连接尝试、当前在线用户和月度热门用户数据。

### 业务价值
作为系统的主控制中心，为管理员提供系统运营状况的全貌视图，支持快速决策和监控。

## 数据层面分析

### 输入数据结构

**会话数据**:
```php
$_SESSION = [
    'operator_user' => string,           // 当前操作员用户名
    'daloradius_logged_in' => boolean,   // 登录状态验证
    'location_name' => string            // 位置信息
]
```

**配置数据**:
```php
$configValues = [
    'CONFIG_DB_TBL_RADPOSTAUTH' => string,     // postauth表名
    'CONFIG_DB_TBL_RADACCT' => string,         // accounting表名  
    'CONFIG_DB_TBL_DALOOPERATORS' => string,   // 操作员表名
    'FREERADIUS_VERSION' => string,            // FreeRADIUS版本
    'OPERATORS_LIBRARY' => string,             // 库文件路径
    'OPERATORS_LANG' => string,                // 语言文件路径
    'COMMON_INCLUDES' => string                // 公共包含路径
]
```

### 数据处理逻辑

#### 1. 统计数据查询
```php
// 用户总数统计
$total_users = count_users($dbSocket);

// 热点总数统计  
$total_hotspots = count_hotspots($dbSocket);

// NAS设备总数统计
$total_nas = count_nas($dbSocket);
```

#### 2. 最近连接尝试查询
```php
$sql = sprintf("SELECT %s AS `username`, reply, %s AS `datetime` FROM %s ORDER BY `datetime` DESC LIMIT 10",
               $tableSetting['postauth']['user'], 
               $tableSetting['postauth']['date'],
               $configValues['CONFIG_DB_TBL_RADPOSTAUTH']);
```

#### 3. 当前在线用户查询
```php
$sql = sprintf("SELECT `username`, `acctstarttime` FROM %s
                WHERE `acctstoptime` IS NULL OR `acctstoptime`='0000-00-00 00:00:00'
                ORDER BY `acctstarttime` DESC LIMIT 10",
               $configValues['CONFIG_DB_TBL_RADACCT']);
```

#### 4. 月度热门用户统计
```php
$sql = sprintf("SELECT DISTINCT(ra.username) AS `username`, 
                SUM(ra.AcctSessionTime) AS `session_time`,
                SUM(ra.AcctInputOctets) AS `uploaded_bytes`, 
                SUM(ra.AcctOutputOctets) AS `downloaded_bytes`
                FROM %s AS ra 
                WHERE ra.acctstarttime >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) 
                GROUP BY `username` 
                ORDER BY `session_time` DESC 
                LIMIT 10", $configValues['CONFIG_DB_TBL_RADACCT']);
```

### 输出数据结构

**仪表板卡片数据**:
```php
$card_params = [
    [
        "title" => "Users",
        "total" => "Total: <strong>$total_users</strong>",
        "linkText" => "Go to users list",
        "linkURL" => "mng-list-all.php",
        "bgColor" => "success",
        "icon" => "people-fill"
    ],
    [
        "title" => "NAS",
        "total" => "Total: <strong>$total_nas</strong>",
        "linkText" => "Go to NAS list", 
        "linkURL" => "mng-rad-nas-list.php",
        "bgColor" => "danger",
        "icon" => "router-fill"
    ],
    [
        "title" => "Hotspots",
        "total" => "Total: <strong>$total_hotspots</strong>",
        "linkText" => "Go to hotspots list",
        "linkURL" => "mng-hs-list.php", 
        "bgColor" => "primary",
        "icon" => "wifi"
    ]
]
```

**表格数据结构**:
```php
// 连接尝试数据
$connection_attempts = [
    ['username' => string, 'reply' => string, 'datetime' => string],
    // ...
];

// 在线用户数据  
$online_users = [
    ['username' => string, 'acctstarttime' => string],
    // ...
];

// 热门用户数据
$top_users = [
    [
        'username' => string,
        'session_time' => integer,
        'uploaded_bytes' => integer, 
        'downloaded_bytes' => integer
    ],
    // ...
];
```

## UI结构分析

### 页面布局架构

**整体结构**: 
- Bootstrap 5 网格系统布局
- 响应式设计，支持移动端适配
- 分为4个主要区域：统计卡片、连接尝试、在线用户、热门用户

**布局层次**:
```html
<div class="container-fluid">
  <!-- 页面标题区域 -->
  <h1>daloRADIUS</h1>
  
  <!-- 统计卡片区域 -->
  <div class="row mb-4">
    <div class="col-md-4">卡片1：用户统计</div>
    <div class="col-md-4">卡片2：NAS统计</div>  
    <div class="col-md-4">卡片3：热点统计</div>
  </div>
  
  <!-- 双列数据表格区域 -->
  <div class="row mb-4">
    <div class="col-sm-12 col-md-6">最近连接尝试表格</div>
    <div class="col-sm-12 col-md-6">当前在线用户表格</div>
  </div>
  
  <!-- 热门用户全宽表格区域 -->
  <div class="row">
    <div class="col-12">月度热门用户表格</div>
  </div>
</div>
```

### 核心UI组件

#### 1. 统计卡片组件
```php
function generateCard($title, $total, $linkText, $linkURL, $bgColor, $icon) {
    return <<<HTML
<div class="col-md-4 m-0 p-0">
    <div class="card m-1 rounded-0">
        <div class="row g-0">
            <div class="d-none d-md-flex col-md-2 text-bg-{$bgColor} align-items-center justify-content-center">
                <i class="bi bi-{$icon} fs-2"></i>
            </div>
            <div class="col-md-10 p-1 d-flex align-items-center justify-content-center flex-column text-bg-{$bgColor}">
                <h5 class="card-title">{$title}</h5>
                <p class="card-text">{$total}</p>
                <a href="{$linkURL}" class="btn btn-light btn-sm">{$linkText}</a>
            </div>
        </div>
    </div>
</div>
HTML;
}
```

#### 2. 表格组件系统
```php
// 表格头部组件
function print_dashboard_table_head($headers) {
    echo '<table class="table table-hover table-striped"><tr>';
    foreach ($headers as $header) {
        printf('<th>%s</th>', $header);
    }
    echo '</tr>';
}

// 表格行组件
function print_dashboard_table_row($items) {
    echo '<tr>';
    foreach ($items as $item) {
        printf('<td>%s</td>', $item);
    }
    echo '</tr>';
}

// 信息提示组件
function print_dashboard_info_message($message) {
    echo <<<EOF
<div class="col-12 m-0">
  <div class="alert alert-info d-flex align-items-center" role="alert">
    <i class="bi bi-exclamation-triangle-fill me-2"></i>
    <div>{$message}</div>
  </div>
</div>
EOF;
}
```

#### 3. 标题组件
```php
function print_title($title, $href, $icon) {
    echo <<<HTML
<span class="d-flex align-items-center justify-content-start mb-2">
    <h1 class="fs-4 m-0">{$title}</h1>
    <a class="ms-2 text-decoration-none" href="{$href}"><i class="bi $icon fs-6"></i></a>
</span>
HTML;
}
```

### 用户交互流程

1. **页面加载** - 认证检查 → 数据库连接 → 统计数据查询
2. **统计展示** - 渲染三个统计卡片（用户/NAS/热点）
3. **实时数据** - 显示最近连接尝试和当前在线用户
4. **趋势分析** - 展示月度热门用户统计
5. **快速导航** - 点击卡片或链接跳转到详细页面

### 响应式设计特性

- **移动端适配**: `col-sm-12 col-md-6` 响应式列布局
- **图标隐藏**: `d-none d-md-flex` 小屏幕隐藏装饰图标
- **Bootstrap组件**: 使用Bootstrap 5原生组件和工具类
- **自适应表格**: 表格在小屏幕下自动堆叠

## Python RESTful API 设计

### 仪表板数据API

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

# 响应模型定义
class DashboardStats(BaseModel):
    """仪表板统计数据"""
    total_users: int = Field(description="用户总数")
    total_nas: int = Field(description="NAS设备总数") 
    total_hotspots: int = Field(description="热点总数")
    active_users: int = Field(description="当前活跃用户数")
    today_sessions: int = Field(description="今日会话数")
    last_updated: datetime = Field(description="最后更新时间")

class ConnectionAttempt(BaseModel):
    """连接尝试记录"""
    username: str
    reply: str
    status: str = Field(description="success/failed")
    auth_date: datetime
    nas_ip: Optional[str] = None
    
class OnlineUser(BaseModel):
    """在线用户信息"""
    username: str
    session_start: datetime
    session_duration: int = Field(description="会话时长(秒)")
    nas_ip: str
    nas_port: Optional[str] = None
    input_bytes: int = 0
    output_bytes: int = 0

class TopUser(BaseModel):
    """热门用户统计"""
    username: str
    total_session_time: int = Field(description="总会话时长(秒)")
    uploaded_bytes: int
    downloaded_bytes: int
    total_bytes: int
    session_count: int = Field(description="会话次数")
    avg_session_time: int = Field(description="平均会话时长(秒)")

class DashboardResponse(BaseModel):
    """仪表板完整响应"""
    stats: DashboardStats
    recent_attempts: List[ConnectionAttempt]
    online_users: List[OnlineUser] 
    top_users: List[TopUser]
    charts_data: Optional[dict] = None

# API端点实现
@app.get("/api/v1/dashboard", 
         response_model=DashboardResponse,
         summary="获取仪表板数据",
         description="获取系统仪表板的所有统计信息和实时数据")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_cache)
):
    """
    获取仪表板数据
    
    返回系统概览信息：
    - 统计数据（用户、NAS、热点总数）
    - 最近连接尝试（最近10条）
    - 当前在线用户（最多10个）
    - 月度热门用户（Top 10）
    """
    try:
        # 检查缓存
        cache_key = f"dashboard:data:{current_user.location}"
        cached_data = await cache.get(cache_key)
        
        if cached_data:
            return DashboardResponse.parse_raw(cached_data)
        
        # 并行获取所有数据
        stats_task = get_dashboard_stats(db, current_user.location)
        attempts_task = get_recent_connection_attempts(db, limit=10)
        online_task = get_online_users(db, limit=10)
        top_users_task = get_top_users_monthly(db, limit=10)
        
        stats, recent_attempts, online_users, top_users = await asyncio.gather(
            stats_task, attempts_task, online_task, top_users_task
        )
        
        dashboard_data = DashboardResponse(
            stats=stats,
            recent_attempts=recent_attempts,
            online_users=online_users,
            top_users=top_users
        )
        
        # 缓存数据（5分钟）
        await cache.setex(
            cache_key, 
            300, 
            dashboard_data.json()
        )
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

# 统计数据服务
async def get_dashboard_stats(db: AsyncSession, location: str) -> DashboardStats:
    """获取仪表板统计数据"""
    
    # 基础统计查询
    users_query = select(func.count(UserModel.id)).where(
        UserModel.is_active == True
    )
    
    nas_query = select(func.count(NASModel.id))
    
    hotspots_query = select(func.count(HotspotModel.id)).where(
        HotspotModel.location == location
    )
    
    # 今日活跃用户
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    active_users_query = select(func.count(distinct(AccountingModel.username))).where(
        and_(
            AccountingModel.acctstarttime >= today_start,
            AccountingModel.acctstoptime.is_(None)
        )
    )
    
    # 今日会话数
    today_sessions_query = select(func.count(AccountingModel.radacctid)).where(
        AccountingModel.acctstarttime >= today_start
    )
    
    # 执行查询
    results = await asyncio.gather(
        db.execute(users_query),
        db.execute(nas_query), 
        db.execute(hotspots_query),
        db.execute(active_users_query),
        db.execute(today_sessions_query)
    )
    
    total_users = results[0].scalar() or 0
    total_nas = results[1].scalar() or 0
    total_hotspots = results[2].scalar() or 0
    active_users = results[3].scalar() or 0
    today_sessions = results[4].scalar() or 0
    
    return DashboardStats(
        total_users=total_users,
        total_nas=total_nas,
        total_hotspots=total_hotspots,
        active_users=active_users,
        today_sessions=today_sessions,
        last_updated=datetime.now()
    )

async def get_recent_connection_attempts(db: AsyncSession, limit: int = 10) -> List[ConnectionAttempt]:
    """获取最近连接尝试"""
    
    query = select(
        PostAuthModel.username,
        PostAuthModel.reply,
        PostAuthModel.authdate,
        PostAuthModel.nasipaddress
    ).order_by(
        PostAuthModel.authdate.desc()
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    attempts = []
    for row in rows:
        status = "success" if row.reply == "Access-Accept" else "failed"
        attempts.append(ConnectionAttempt(
            username=row.username,
            reply=row.reply,
            status=status,
            auth_date=row.authdate,
            nas_ip=row.nasipaddress
        ))
    
    return attempts

async def get_online_users(db: AsyncSession, limit: int = 10) -> List[OnlineUser]:
    """获取当前在线用户"""
    
    query = select(
        AccountingModel.username,
        AccountingModel.acctstarttime,
        AccountingModel.nasipaddress,
        AccountingModel.nasportid,
        AccountingModel.acctinputoctets,
        AccountingModel.acctoutputoctets
    ).where(
        or_(
            AccountingModel.acctstoptime.is_(None),
            AccountingModel.acctstoptime == '0000-00-00 00:00:00'
        )
    ).order_by(
        AccountingModel.acctstarttime.desc()
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    online_users = []
    now = datetime.now()
    
    for row in rows:
        session_duration = int((now - row.acctstarttime).total_seconds())
        
        online_users.append(OnlineUser(
            username=row.username,
            session_start=row.acctstarttime,
            session_duration=session_duration,
            nas_ip=row.nasipaddress,
            nas_port=row.nasportid,
            input_bytes=row.acctinputoctets or 0,
            output_bytes=row.acctoutputoctets or 0
        ))
    
    return online_users

async def get_top_users_monthly(db: AsyncSession, limit: int = 10) -> List[TopUser]:
    """获取月度热门用户"""
    
    # 一个月前的日期
    one_month_ago = datetime.now() - timedelta(days=30)
    
    query = select(
        AccountingModel.username,
        func.sum(AccountingModel.acctsessiontime).label('total_session_time'),
        func.sum(AccountingModel.acctinputoctets).label('uploaded_bytes'),
        func.sum(AccountingModel.acctoutputoctets).label('downloaded_bytes'),
        func.count(AccountingModel.radacctid).label('session_count'),
        func.avg(AccountingModel.acctsessiontime).label('avg_session_time')
    ).where(
        AccountingModel.acctstarttime >= one_month_ago
    ).group_by(
        AccountingModel.username
    ).order_by(
        func.sum(AccountingModel.acctsessiontime).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    top_users = []
    for row in rows:
        uploaded = row.uploaded_bytes or 0
        downloaded = row.downloaded_bytes or 0
        
        top_users.append(TopUser(
            username=row.username,
            total_session_time=row.total_session_time or 0,
            uploaded_bytes=uploaded,
            downloaded_bytes=downloaded,
            total_bytes=uploaded + downloaded,
            session_count=row.session_count or 0,
            avg_session_time=int(row.avg_session_time or 0)
        ))
    
    return top_users

# 实时更新API
@app.get("/api/v1/dashboard/realtime")
async def get_realtime_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取实时更新数据（在线用户数、当前会话等）"""
    
    # 当前在线用户数
    online_count_query = select(func.count(AccountingModel.radacctid)).where(
        or_(
            AccountingModel.acctstoptime.is_(None),
            AccountingModel.acctstoptime == '0000-00-00 00:00:00'
        )
    )
    
    # 今日新用户
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    new_users_today_query = select(func.count(UserModel.id)).where(
        UserModel.created_at >= today_start
    )
    
    online_count = await db.execute(online_count_query)
    new_users_today = await db.execute(new_users_today_query)
    
    return {
        "online_users_count": online_count.scalar() or 0,
        "new_users_today": new_users_today.scalar() or 0,
        "timestamp": datetime.now().isoformat()
    }
```

### 缓存策略

```python
# service/dashboard_cache.py
from typing import Optional, Dict, Any
import json
import redis
from datetime import datetime, timedelta

class DashboardCacheService:
    """仪表板缓存服务"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = {
            'stats': 300,        # 统计数据 5分钟
            'attempts': 60,      # 连接尝试 1分钟  
            'online': 30,        # 在线用户 30秒
            'top_users': 3600    # 热门用户 1小时
        }
    
    async def get_dashboard_cache(self, location: str) -> Optional[Dict[str, Any]]:
        """获取仪表板缓存数据"""
        cache_key = f"dashboard:full:{location}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_dashboard_cache(self, location: str, data: Dict[str, Any]):
        """设置仪表板缓存"""
        cache_key = f"dashboard:full:{location}"
        
        # 设置最短TTL（在线用户更新频率）
        ttl = min(self.cache_ttl.values())
        
        await self.redis.setex(
            cache_key,
            ttl, 
            json.dumps(data, default=str)
        )
    
    async def invalidate_dashboard_cache(self, location: str):
        """使仪表板缓存失效"""
        pattern = f"dashboard:*:{location}"
        keys = await self.redis.keys(pattern)
        
        if keys:
            await self.redis.delete(*keys)
    
    async def get_partial_cache(self, cache_type: str, location: str) -> Optional[Any]:
        """获取部分缓存数据"""
        cache_key = f"dashboard:{cache_type}:{location}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_partial_cache(self, cache_type: str, location: str, data: Any):
        """设置部分缓存数据"""
        cache_key = f"dashboard:{cache_type}:{location}"
        ttl = self.cache_ttl.get(cache_type, 300)
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )
```

## Vue 前端组件设计

### 仪表板主组件

```vue
<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">
        <i class="icon-dashboard"></i>
        {{ $t('dashboard.title') }}
      </h1>
      
      <div class="dashboard-actions">
        <el-button 
          @click="refreshData" 
          :loading="isRefreshing"
          type="primary" 
          size="small"
        >
          <el-icon><Refresh /></el-icon>
          {{ $t('common.refresh') }}
        </el-button>
        
        <el-button 
          @click="toggleAutoRefresh"
          :type="autoRefresh ? 'success' : 'info'"
          size="small"
        >
          <el-icon><Timer /></el-icon>
          {{ autoRefresh ? $t('dashboard.autoRefreshOn') : $t('dashboard.autoRefreshOff') }}
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-cards-container">
      <StatsCard
        v-for="card in statsCards"
        :key="card.key"
        :title="card.title"
        :value="card.value"
        :change="card.change"
        :icon="card.icon"
        :color="card.color"
        :loading="statsLoading"
        :link="card.link"
        @click="handleCardClick(card)"
      />
    </div>

    <!-- 数据表格区域 -->
    <div class="dashboard-tables">
      <el-row :gutter="20">
        <!-- 最近连接尝试 -->
        <el-col :span="12" :xs="24">
          <DashboardTable
            :title="$t('dashboard.recentAttempts')"
            :data="recentAttempts"
            :columns="attemptColumns"
            :loading="attemptsLoading"
            :link="'/reports/connections'"
            icon="connection"
          />
        </el-col>
        
        <!-- 当前在线用户 -->
        <el-col :span="12" :xs="24">
          <DashboardTable
            :title="$t('dashboard.onlineUsers')"
            :data="onlineUsers"
            :columns="onlineColumns"
            :loading="onlineLoading"
            :link="'/reports/online'"
            icon="user-online"
          />
        </el-col>
      </el-row>
      
      <!-- 热门用户统计 -->
      <div class="top-users-section">
        <DashboardTable
          :title="$t('dashboard.topUsers')"
          :data="topUsers"
          :columns="topUserColumns"
          :loading="topUsersLoading"
          :link="'/reports/top-users'"
          icon="trophy"
          :full-width="true"
        />
      </div>
    </div>

    <!-- 图表区域（可选） -->
    <div class="dashboard-charts" v-if="showCharts">
      <el-row :gutter="20">
        <el-col :span="12">
          <ChartWidget
            type="line"
            :title="$t('dashboard.sessionTrend')"
            :data="sessionTrendData"
            :loading="chartsLoading"
          />
        </el-col>
        
        <el-col :span="12">
          <ChartWidget
            type="pie"
            :title="$t('dashboard.deviceTypes')"
            :data="deviceTypesData"
            :loading="chartsLoading"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Timer } from '@element-plus/icons-vue'

import StatsCard from './components/StatsCard.vue'
import DashboardTable from './components/DashboardTable.vue'
import ChartWidget from './components/ChartWidget.vue'

import { useDashboard } from '@/composables/useDashboard'
import { useRealTimeData } from '@/composables/useRealTimeData'
import { formatBytes, formatDuration, formatDateTime } from '@/utils/formatters'

const router = useRouter()

// 组合函数
const {
  dashboardData,
  isLoading,
  error,
  refreshData,
  isRefreshing
} = useDashboard()

const {
  realtimeData,
  autoRefresh,
  toggleAutoRefresh
} = useRealTimeData()

// 响应式数据
const showCharts = ref(true)

// 计算属性 - 统计卡片数据
const statsCards = computed(() => [
  {
    key: 'users',
    title: 'dashboard.totalUsers',
    value: dashboardData.value?.stats.total_users || 0,
    change: realtimeData.value?.new_users_today || 0,
    icon: 'users',
    color: 'success',
    link: '/management/users'
  },
  {
    key: 'nas',
    title: 'dashboard.totalNAS',
    value: dashboardData.value?.stats.total_nas || 0,
    change: null,
    icon: 'server',
    color: 'danger',
    link: '/management/nas'
  },
  {
    key: 'hotspots',
    title: 'dashboard.totalHotspots',
    value: dashboardData.value?.stats.total_hotspots || 0,
    change: null,
    icon: 'wifi',
    color: 'primary',
    link: '/management/hotspots'
  },
  {
    key: 'online',
    title: 'dashboard.onlineUsers',
    value: realtimeData.value?.online_users_count || 0,
    change: null,
    icon: 'user-online',
    color: 'warning',
    link: '/reports/online'
  }
])

// 表格列定义
const attemptColumns = [
  {
    prop: 'username',
    label: 'dashboard.username',
    width: 120
  },
  {
    prop: 'reply',
    label: 'dashboard.result',
    width: 100,
    formatter: (row: any) => {
      const isSuccess = row.reply === 'Access-Accept'
      return `<span class="status-badge ${isSuccess ? 'success' : 'danger'}">${row.reply}</span>`
    }
  },
  {
    prop: 'auth_date',
    label: 'dashboard.time',
    formatter: (row: any) => formatDateTime(row.auth_date)
  }
]

const onlineColumns = [
  {
    prop: 'username',
    label: 'dashboard.username',
    width: 120
  },
  {
    prop: 'session_duration',
    label: 'dashboard.duration',
    formatter: (row: any) => formatDuration(row.session_duration)
  }
]

const topUserColumns = [
  {
    prop: 'username',
    label: 'dashboard.username',
    width: 120
  },
  {
    prop: 'total_session_time',
    label: 'dashboard.totalTime',
    formatter: (row: any) => formatDuration(row.total_session_time)
  },
  {
    prop: 'uploaded_bytes',
    label: 'dashboard.uploaded',
    formatter: (row: any) => formatBytes(row.uploaded_bytes)
  },
  {
    prop: 'downloaded_bytes',
    label: 'dashboard.downloaded',
    formatter: (row: any) => formatBytes(row.downloaded_bytes)
  }
]

// 计算衍生数据
const recentAttempts = computed(() => dashboardData.value?.recent_attempts || [])
const onlineUsers = computed(() => dashboardData.value?.online_users || [])
const topUsers = computed(() => dashboardData.value?.top_users || [])

const statsLoading = computed(() => isLoading.value)
const attemptsLoading = computed(() => isLoading.value)
const onlineLoading = computed(() => isLoading.value)
const topUsersLoading = computed(() => isLoading.value)
const chartsLoading = computed(() => isLoading.value)

// 图表数据
const sessionTrendData = computed(() => {
  // 处理会话趋势数据
  return dashboardData.value?.charts_data?.session_trend || []
})

const deviceTypesData = computed(() => {
  // 处理设备类型分布数据
  return dashboardData.value?.charts_data?.device_types || []
})

// 事件处理
const handleCardClick = (card: any) => {
  if (card.link) {
    router.push(card.link)
  }
}

// 生命周期
onMounted(async () => {
  try {
    await refreshData()
    
    // 启动自动刷新
    if (autoRefresh.value) {
      toggleAutoRefresh()
    }
  } catch (error: any) {
    ElMessage.error('Failed to load dashboard data')
    console.error('Dashboard load error:', error)
  }
})

onUnmounted(() => {
  // 清理定时器
  if (autoRefresh.value) {
    toggleAutoRefresh()
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.dashboard-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
  
  .icon-dashboard {
    margin-right: 12px;
    font-size: 28px;
    color: var(--el-color-primary);
  }
}

.dashboard-actions {
  display: flex;
  gap: 12px;
}

.stats-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.dashboard-tables {
  margin-bottom: 24px;
}

.top-users-section {
  margin-top: 20px;
}

.dashboard-charts {
  margin-top: 24px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  
  &.success {
    background-color: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
  
  &.danger {
    background-color: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 12px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .dashboard-actions {
    justify-content: center;
  }
  
  .stats-cards-container {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
```

### 统计卡片组件

```vue
<template>
  <div 
    class="stats-card" 
    :class="[`stats-card--${color}`, { 'stats-card--clickable': !!link }]"
    @click="handleClick"
  >
    <div class="stats-card__content">
      <div class="stats-card__icon">
        <el-icon v-if="!loading" :class="iconClass">
          <component :is="iconComponent" />
        </el-icon>
        <el-skeleton v-else animated>
          <template #default>
            <div class="skeleton-icon" />
          </template>
        </el-skeleton>
      </div>
      
      <div class="stats-card__info">
        <div class="stats-card__title">
          {{ $t(title) }}
        </div>
        
        <div class="stats-card__value">
          <el-skeleton v-if="loading" animated>
            <template #default>
              <div class="skeleton-value" />
            </template>
          </el-skeleton>
          
          <span v-else class="value-number">
            {{ formattedValue }}
          </span>
        </div>
        
        <div class="stats-card__change" v-if="change !== null && !loading">
          <span :class="changeClass">
            <el-icon><TrendCharts /></el-icon>
            {{ changeText }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="stats-card__action" v-if="link">
      <el-icon><ArrowRight /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Users, 
  Server, 
  Wifi, 
  UserFilled,
  TrendCharts,
  ArrowRight 
} from '@element-plus/icons-vue'

interface Props {
  title: string
  value: number
  change?: number | null
  icon: string
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  loading?: boolean
  link?: string
}

const props = withDefaults(defineProps<Props>(), {
  change: null,
  loading: false
})

const emit = defineEmits<{
  click: []
}>()

// 图标映射
const iconMap = {
  users: Users,
  server: Server,
  wifi: Wifi,
  'user-online': UserFilled
}

// 计算属性
const iconComponent = computed(() => iconMap[props.icon as keyof typeof iconMap] || Users)

const iconClass = computed(() => `icon-${props.icon}`)

const formattedValue = computed(() => {
  if (props.value >= 1000000) {
    return `${(props.value / 1000000).toFixed(1)}M`
  } else if (props.value >= 1000) {
    return `${(props.value / 1000).toFixed(1)}K`
  }
  return props.value.toString()
})

const changeClass = computed(() => {
  if (props.change === null || props.change === 0) return ''
  return props.change > 0 ? 'change-positive' : 'change-negative'
})

const changeText = computed(() => {
  if (props.change === null) return ''
  const prefix = props.change > 0 ? '+' : ''
  return `${prefix}${props.change}`
})

// 事件处理
const handleClick = () => {
  if (props.link) {
    emit('click')
  }
}
</script>

<style scoped>
.stats-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--card-accent-color);
    transition: all 0.3s ease;
  }
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
  
  &--clickable {
    cursor: pointer;
  }
  
  &--primary {
    --card-accent-color: var(--el-color-primary);
  }
  
  &--success {
    --card-accent-color: var(--el-color-success);
  }
  
  &--warning {
    --card-accent-color: var(--el-color-warning);
  }
  
  &--danger {
    --card-accent-color: var(--el-color-danger);
  }
  
  &--info {
    --card-accent-color: var(--el-color-info);
  }
}

.stats-card__content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.stats-card__icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--card-accent-color), var(--card-accent-color)88);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stats-card__info {
  flex: 1;
  min-width: 0;
}

.stats-card__title {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 8px;
  font-weight: 500;
}

.stats-card__value {
  margin-bottom: 4px;
}

.value-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.stats-card__change {
  font-size: 12px;
  
  .change-positive {
    color: var(--el-color-success);
  }
  
  .change-negative {
    color: var(--el-color-danger);
  }
}

.stats-card__action {
  position: absolute;
  top: 16px;
  right: 16px;
  color: var(--el-text-color-placeholder);
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stats-card--clickable:hover .stats-card__action {
  opacity: 1;
}

.skeleton-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.skeleton-value {
  width: 80px;
  height: 32px;
  border-radius: 4px;
}
</style>
```

## 技术债务和改进建议

### 当前实现的问题

1. **性能问题**:
   ```php
   // 同步执行多个数据库查询，影响页面加载速度
   $total_users = count_users($dbSocket);
   $total_hotspots = count_hotspots($dbSocket);
   $total_nas = count_nas($dbSocket);
   ```

2. **缺少缓存机制**:
   - 每次页面加载都执行数据库查询
   - 统计数据变化不频繁，应该缓存

3. **硬编码限制**:
   ```php
   // 硬编码限制10条记录
   ORDER BY `datetime` DESC LIMIT 10
   ```

4. **SQL注入风险**:
   - 虽然使用了sprintf，但仍存在潜在风险
   - 应该使用参数化查询

5. **响应式设计不完整**:
   - Bootstrap使用较基础
   - 移动端体验有待改善

### 重构优先级评估

**高优先级**:
1. 实现异步数据加载和缓存
2. 使用参数化查询防止SQL注入
3. 添加实时数据更新功能
4. 优化移动端响应式设计

**中优先级**:
1. 添加图表可视化
2. 实现数据导出功能
3. 添加时间范围选择
4. 支持个性化仪表板

**低优先级**:
1. 添加高级筛选功能
2. 实现仪表板配置
3. 支持自定义小部件
4. 添加数据钻取功能

### 性能优化建议

```python
# 性能优化实现示例
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedDashboardService:
    """优化的仪表板服务"""
    
    def __init__(self, db, cache, thread_pool):
        self.db = db
        self.cache = cache
        self.thread_pool = thread_pool
    
    @lru_cache(maxsize=128)
    async def get_cached_stats(self, location: str, cache_key: str):
        """带缓存的统计数据获取"""
        
        # 检查Redis缓存
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 并行执行数据库查询
        async with self.db.begin() as conn:
            tasks = [
                self.get_user_count(conn),
                self.get_nas_count(conn),
                self.get_hotspot_count(conn, location),
                self.get_active_sessions_count(conn)
            ]
            
            results = await asyncio.gather(*tasks)
            
            stats = {
                'total_users': results[0],
                'total_nas': results[1], 
                'total_hotspots': results[2],
                'active_sessions': results[3],
                'timestamp': datetime.now().isoformat()
            }
            
            # 缓存5分钟
            await self.cache.setex(cache_key, 300, json.dumps(stats))
            
            return stats
    
    async def get_paginated_data(self, query_type: str, page: int = 1, 
                               limit: int = 10, location: str = None):
        """分页数据获取"""
        
        offset = (page - 1) * limit
        cache_key = f"dashboard:{query_type}:{location}:{page}:{limit}"
        
        # 检查缓存
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 根据查询类型执行相应查询
        if query_type == 'recent_attempts':
            data = await self.get_recent_attempts(offset, limit)
        elif query_type == 'online_users':
            data = await self.get_online_users(offset, limit)
        elif query_type == 'top_users':
            data = await self.get_top_users(offset, limit)
        else:
            raise ValueError(f"Unknown query type: {query_type}")
        
        # 缓存1分钟
        await self.cache.setex(cache_key, 60, json.dumps(data, default=str))
        
        return data
    
    async def preload_dashboard_data(self, location: str):
        """预加载仪表板数据"""
        
        # 在后台预加载常用数据
        tasks = [
            self.get_cached_stats(location, f"stats:{location}"),
            self.get_paginated_data('recent_attempts', 1, 10, location),
            self.get_paginated_data('online_users', 1, 10, location),
            self.get_paginated_data('top_users', 1, 10, location)
        ]
        
        # 并行执行但不等待结果（预加载）
        asyncio.create_task(asyncio.gather(*tasks, return_exceptions=True))
```

## 设计原则符合性检查

### ❌ 当前实现的问题
- **SRP**: 单一页面承担了太多数据展示职责
- **性能**: 同步查询导致页面加载缓慢
- **可维护性**: 硬编码和重复代码过多

### ✅ 重构后的改进
- **SRP**: 分离数据获取、缓存、展示逻辑
- **OCP**: 支持插件化的小部件扩展
- **DIP**: 依赖抽象的数据服务接口
- **性能**: 异步加载、缓存策略、实时更新
- **用户体验**: 现代化的响应式界面设计

## 总结

home-main.php 是系统的核心仪表板，需要重点关注性能优化和用户体验改进。重构时应采用现代的异步数据加载、智能缓存和实时更新机制，同时提供直观的可视化界面和流畅的交互体验。建议优先实现API化改造和前端组件化重构。