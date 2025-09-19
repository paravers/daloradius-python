# 系统基础页面简化分析报告

## home-error.php 分析

### 职责
权限错误页面，当操作员缺少访问特定系统区域的权限时显示。

### 数据层面
- **输入**: 会话验证数据
- **输出**: 错误消息页面

### UI结构  
- 标准页面布局
- 错误消息显示
- 返回导航

### Python API 设计
```python
@app.get("/api/v1/errors/permission")
async def permission_error():
    return {"error": "Insufficient permissions", "code": 403}
```

### Vue 组件
```vue
<template>
  <div class="error-page">
    <el-result icon="warning" title="权限不足" sub-title="您没有访问此页面的权限">
      <template #extra>
        <el-button type="primary" @click="$router.go(-1)">返回</el-button>
      </template>
    </el-result>
  </div>
</template>
```

---

## help-main.php 分析

### 职责
帮助页面，提供daloRADIUS项目的联系方式和支持资源。

### 数据层面
- **输入**: 基本会话验证
- **输出**: 静态帮助内容

### UI结构
- 标准页面头部
- 链接列表（网站、GitHub、邮件列表等）
- 外部资源链接

### Python API 设计
```python
@app.get("/api/v1/help/resources")
async def get_help_resources():
    return {
        "website": "https://www.daloradius.com",
        "github": "https://github.com/lirantal/daloradius",
        "support_email": "daloradius-users@lists.sourceforge.net",
        "irc": "#daloradius on irc.freenode.net"
    }
```

### Vue 组件
```vue
<template>
  <div class="help-page">
    <el-card>
      <h2>获取帮助</h2>
      <ul>
        <li><a :href="resources.website" target="_blank">官方网站</a></li>
        <li><a :href="resources.github" target="_blank">GitHub项目</a></li>
        <li><a :href="`mailto:${resources.support_email}`">邮件支持</a></li>
      </ul>
    </el-card>
  </div>
</template>
```

---

## heartbeat.php 分析

### 职责
接收来自NAS设备的心跳数据，验证授权并更新/插入系统信息到数据库。

### 数据层面

**输入数据**:
```php
$_GET = [
    'secret_key' => string,      // 认证密钥（必须）
    'wan_iface' => string,       // WAN接口
    'wan_ip' => string,          // WAN IP
    'wan_mac' => string,         // WAN MAC
    'wifi_ssid' => string,       // WiFi SSID
    'wifi_key' => string,        // WiFi密钥
    'uptime' => string,          // 运行时间
    'memfree' => string,         // 空闲内存
    'nas_mac' => string,         // NAS MAC地址
    'firmware' => string,        // 固件版本
    'cpu' => string              // CPU信息
    // ... 其他系统信息
]
```

**数据处理**:
1. 验证HTTP方法（仅GET）
2. 验证secret_key
3. 检查设备是否存在（根据MAC地址）
4. 执行UPDATE或INSERT操作

### Python API 设计
```python
from pydantic import BaseModel, Field
from datetime import datetime

class HeartbeatData(BaseModel):
    wan_iface: str = ""
    wan_ip: str = ""
    wan_mac: str = ""
    wan_gateway: str = ""
    wifi_iface: str = ""
    wifi_ip: str = ""
    wifi_mac: str = ""
    wifi_ssid: str = ""
    wifi_key: str = ""
    wifi_channel: str = ""
    lan_iface: str = ""
    lan_mac: str = ""
    lan_ip: str = ""
    uptime: str = ""
    memfree: str = ""
    wan_bup: str = ""
    wan_bdown: str = ""
    nas_mac: str = Field(..., description="设备MAC地址")
    firmware: str = ""
    firmware_revision: str = ""
    cpu: str = ""

@app.post("/api/v1/devices/{device_mac}/heartbeat")
async def device_heartbeat(
    device_mac: str,
    heartbeat_data: HeartbeatData,
    api_key: str = Header(..., alias="X-API-Key"),
    device_service: DeviceService = Depends(get_device_service)
):
    """接收设备心跳数据"""
    
    # 验证API密钥
    if not await verify_api_key(api_key):
        raise HTTPException(403, "Invalid API key")
    
    # 验证设备MAC
    if device_mac != heartbeat_data.nas_mac:
        raise HTTPException(400, "MAC address mismatch")
    
    # 更新设备信息
    device_info = await device_service.update_or_create_device(
        mac_address=device_mac,
        heartbeat_data=heartbeat_data.dict(),
        last_seen=datetime.utcnow()
    )
    
    return {"status": "success", "device_id": device_info.id}

# 设备状态查询
@app.get("/api/v1/devices/{device_mac}/status")
async def get_device_status(
    device_mac: str,
    current_user: User = Depends(get_current_user),
    device_service: DeviceService = Depends(get_device_service)
):
    """获取设备状态"""
    device = await device_service.get_device_by_mac(device_mac)
    
    if not device:
        raise HTTPException(404, "Device not found")
    
    return {
        "mac_address": device.mac,
        "last_seen": device.time,
        "uptime": device.uptime,
        "memory_free": device.memfree,
        "firmware": device.firmware,
        "status": "online" if device.is_online else "offline"
    }
```

### 数据库模型
```python
class DeviceModel(Base):
    __tablename__ = "dalo_nodes"
    
    id = Column(Integer, primary_key=True)
    wan_iface = Column(String(50))
    wan_ip = Column(String(45))
    wan_mac = Column(String(17))
    wan_gateway = Column(String(45))
    wifi_iface = Column(String(50))
    wifi_ip = Column(String(45))
    wifi_mac = Column(String(17))
    wifi_ssid = Column(String(100))
    wifi_key = Column(String(255))
    wifi_channel = Column(String(10))
    lan_iface = Column(String(50))
    lan_mac = Column(String(17))
    lan_ip = Column(String(45))
    uptime = Column(String(50))
    memfree = Column(String(50))
    wan_bup = Column(String(50))
    wan_bdown = Column(String(50))
    firmware = Column(String(100))
    firmware_revision = Column(String(50))
    mac = Column(String(17), unique=True, index=True)
    time = Column(DateTime, default=datetime.utcnow)
    cpu = Column(String(100))
    
    @property
    def is_online(self) -> bool:
        """设备是否在线（5分钟内有心跳）"""
        if not self.time:
            return False
        return (datetime.utcnow() - self.time).total_seconds() < 300
```

---

## page-footer.php 分析

### 职责
页面底部组件，显示版权信息。

### 数据层面
- **输入**: 无（被包含文件）
- **输出**: 版权信息HTML

### UI结构
- 简单的版权信息展示
- 右对齐样式

### Python/Vue 设计
```vue
<template>
  <footer class="page-footer">
    <div class="copyright">
      {{ $t('common.copyright') }}
    </div>
  </footer>
</template>

<style scoped>
.page-footer {
  margin: 15px auto;
  text-align: right;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
```

---

## 技术债务总结

### 共同问题
1. **安全性**: heartbeat.php的secret_key验证过于简单
2. **错误处理**: 缺少完善的错误处理机制
3. **日志记录**: 缺少详细的审计日志
4. **API化**: 需要现代化的RESTful API接口

### 重构优先级
1. **高**: heartbeat.php安全强化和API化
2. **中**: 错误页面标准化和用户体验改进
3. **低**: 静态页面内容管理系统化

### 现代化建议
1. 使用JWT认证替代简单的secret_key
2. 实现WebSocket实时通信替代轮询心跳
3. 添加设备管理仪表板
4. 实现错误页面路由守卫
5. 使用内容管理系统管理帮助内容