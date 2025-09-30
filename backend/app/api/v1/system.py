"""
System API Routes

Provides system health monitoring, heartbeat, and system status endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import psutil
import platform
import time

from app.core.deps import get_db, get_current_user
from app.models.access_control import User
from app.models.reports import HeartBeat
from app.services.reports import HeartBeatService
from app.schemas.reports import HeartBeatCreate, HeartBeatResponse, SystemStatus

router = APIRouter()


class HeartbeatData(BaseModel):
    """Device heartbeat data structure"""
    nas_mac: str = Field(..., description="NAS device MAC address")
    firmware: Optional[str] = Field("", description="Firmware version")
    firmware_revision: Optional[str] = Field("", description="Firmware revision")
    wan_iface: Optional[str] = Field("", description="WAN interface name")
    wan_ip: Optional[str] = Field("", description="WAN IP address")
    wan_mac: Optional[str] = Field("", description="WAN MAC address")
    wan_gateway: Optional[str] = Field("", description="WAN gateway")
    wifi_iface: Optional[str] = Field("", description="WiFi interface name")
    wifi_ip: Optional[str] = Field("", description="WiFi IP address") 
    wifi_mac: Optional[str] = Field("", description="WiFi MAC address")
    wifi_ssid: Optional[str] = Field("", description="WiFi SSID")
    wifi_key: Optional[str] = Field("", description="WiFi key/password")
    wifi_channel: Optional[str] = Field("", description="WiFi channel")
    lan_iface: Optional[str] = Field("", description="LAN interface name")
    lan_ip: Optional[str] = Field("", description="LAN IP address")
    lan_mac: Optional[str] = Field("", description="LAN MAC address")
    uptime: Optional[str] = Field("", description="System uptime")
    memfree: Optional[str] = Field("", description="Free memory")
    wan_bup: Optional[str] = Field("", description="WAN bytes up")
    wan_bdown: Optional[str] = Field("", description="WAN bytes down")
    cpu: Optional[str] = Field("", description="CPU usage")


class SystemInfoResponse(BaseModel):
    """System information response"""
    hostname: str
    platform: str
    architecture: str
    python_version: str
    uptime_seconds: int
    boot_time: datetime
    cpu_count: int
    memory_total_gb: float
    disk_total_gb: float


class SystemHealthResponse(BaseModel):
    """System health check response"""
    status: str
    timestamp: datetime
    database_status: str
    services_status: Dict[str, str]
    resource_usage: Dict[str, float]
    uptime_hours: float
    health_score: int


@router.get("/test")
async def test_system():
    """Test system API endpoint"""
    return {"message": "System API working", "timestamp": datetime.utcnow()}


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive system information
    
    Returns detailed system information including platform,
    hardware, and runtime details.
    """
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return SystemInfoResponse(
            hostname=platform.node(),
            platform=f"{platform.system()} {platform.release()}",
            architecture=platform.architecture()[0],
            python_version=platform.python_version(),
            uptime_seconds=int(time.time() - psutil.boot_time()),
            boot_time=boot_time,
            cpu_count=psutil.cpu_count(),
            memory_total_gb=round(psutil.virtual_memory().total / (1024**3), 2),
            disk_total_gb=round(psutil.disk_usage('/').total / (1024**3), 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system info: {str(e)}"
        )


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system health status
    
    Returns comprehensive health check including database,
    services, and resource usage.
    """
    try:
        # Get system resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime
        uptime_hours = (time.time() - psutil.boot_time()) / 3600
        
        # Check database status
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception:
            db_status = "error"
        
        # Check services (simplified check)
        services_status = {
            "database": db_status,
            "web_server": "healthy",  # If we can respond, web server is working
            "api": "healthy"  # If this endpoint responds, API is working
        }
        
        # Calculate health score (0-100)
        health_score = 100
        if cpu_percent > 80:
            health_score -= 20
        if memory.percent > 85:
            health_score -= 20
        if disk.percent > 90:
            health_score -= 30
        if db_status != "healthy":
            health_score -= 30
        
        overall_status = "healthy"
        if health_score < 70:
            overall_status = "warning"
        if health_score < 40:
            overall_status = "critical"
        
        return SystemHealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            database_status=db_status,
            services_status=services_status,
            resource_usage={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            uptime_hours=round(uptime_hours, 2),
            health_score=max(0, health_score)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.post("/heartbeat/{device_mac}")
async def device_heartbeat(
    device_mac: str,
    heartbeat_data: HeartbeatData,
    secret_key: str = Header(..., alias="X-Secret-Key"),
    db: Session = Depends(get_db)
):
    """
    Receive heartbeat from network devices
    
    Accepts heartbeat data from NAS devices and updates
    device status and monitoring information.
    """
    try:
        # Validate secret key (in production, this should be configurable)
        if secret_key != "your-secret-key":  # This should be from config
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret key"
            )
        
        # Validate device MAC
        if device_mac != heartbeat_data.nas_mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAC address mismatch"
            )
        
        # Create or update heartbeat record
        heartbeat_service = HeartBeatService(db)
        
        # Convert heartbeat data to service format
        service_data = HeartBeatCreate(
            service_name=f"nas-{device_mac}",
            service_type="nas_device",
            host_name=heartbeat_data.wan_ip or heartbeat_data.lan_ip or device_mac,
            ip_address=heartbeat_data.wan_ip or heartbeat_data.lan_ip,
            status=SystemStatus.ONLINE,
            uptime=int(heartbeat_data.uptime) if heartbeat_data.uptime.isdigit() else None,
            cpu_usage=float(heartbeat_data.cpu) if heartbeat_data.cpu and heartbeat_data.cpu.replace('.', '').isdigit() else None,
            memory_usage=float(heartbeat_data.memfree) if heartbeat_data.memfree and heartbeat_data.memfree.replace('.', '').isdigit() else None
        )
        
        # Check if device already exists
        existing = heartbeat_service.repository.get_by_service(
            f"nas-{device_mac}",
            heartbeat_data.wan_ip or heartbeat_data.lan_ip or device_mac
        )
        
        if existing:
            # Update existing record
            updated = await heartbeat_service.update_heartbeat(
                existing.id,
                {
                    "status": SystemStatus.ONLINE,
                    "last_heartbeat": datetime.utcnow(),
                    "uptime": service_data.uptime,
                    "cpu_usage": service_data.cpu_usage,
                    "memory_usage": service_data.memory_usage
                }
            )
            return {
                "status": "updated",
                "device_id": updated.id,
                "message": f"Heartbeat updated for device {device_mac}"
            }
        else:
            # Create new record
            created = await heartbeat_service.create_heartbeat(service_data)
            return {
                "status": "created", 
                "device_id": created.id,
                "message": f"New device {device_mac} registered"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process heartbeat: {str(e)}"
        )


@router.get("/heartbeat/devices")
async def get_device_heartbeats(
    status: Optional[SystemStatus] = Query(None, description="Filter by device status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of devices to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get heartbeat status of all registered devices
    
    Returns list of devices with their last heartbeat status.
    """
    try:
        heartbeat_service = HeartBeatService(db)
        
        # Get devices (NAS type heartbeats)
        devices = heartbeat_service.repository.get_services_by_type("nas_device")
        
        if status:
            devices = [d for d in devices if d.status == status]
        
        devices = devices[:limit]
        
        return {
            "devices": [HeartBeatResponse.from_orm(device) for device in devices],
            "total": len(devices),
            "online_count": len([d for d in devices if d.status == SystemStatus.ONLINE]),
            "offline_count": len([d for d in devices if d.status == SystemStatus.OFFLINE])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device heartbeats: {str(e)}"
        )


@router.get("/status")
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall system status summary
    
    Returns quick system status overview for monitoring.
    """
    try:
        # Get basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check database
        try:
            db.execute("SELECT 1")
            db_connected = True
        except Exception:
            db_connected = False
        
        # Get device count
        heartbeat_service = HeartBeatService(db)
        summary = await heartbeat_service.get_heartbeat_summary()
        
        return {
            "system": {
                "status": "healthy" if db_connected and cpu_percent < 80 else "warning",
                "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 1),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            },
            "resources": {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "disk_percent": round(disk.percent, 1)
            },
            "database": {
                "connected": db_connected,
                "status": "online" if db_connected else "offline"
            },
            "devices": {
                "total": summary.get("total", 0),
                "online": summary.get("online", 0),
                "offline": summary.get("offline", 0),
                "warning": summary.get("warning", 0)
            },
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )