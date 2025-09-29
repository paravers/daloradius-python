"""
NAS Service Layer

Business logic for NAS (Network Access Server) management operations including
connectivity testing, monitoring, and complex NAS operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import asyncio
import socket
import logging

from app.repositories.radius import NasRepository
from app.models.nas import Nas, NasMonitoring
from app.models.radius import RadAcct
from app.schemas.radius import (
    NasCreate, NasUpdate, NasResponse,
    NasMonitoringResponse
)

logger = logging.getLogger(__name__)

class NasService:
    """Service class for NAS management business logic"""
    
    def __init__(self, nas_repository: NasRepository):
        self.nas_repo = nas_repository
    
    async def create_nas(
        self, 
        nas_data: NasCreate, 
        created_by: Optional[str] = None
    ) -> NasResponse:
        """
        Create a new NAS device with validation and initial connectivity test
        
        Args:
            nas_data: NAS creation data
            created_by: Username who created the NAS
            
        Returns:
            Created NAS response
        """
        # Add audit fields
        nas_dict = nas_data.dict()
        nas_dict['created_by'] = created_by
        
        # Validate NAS name format (IP address or hostname)
        if not self._validate_nas_name(nas_data.nasname):
            raise ValueError("Invalid NAS name format. Must be IP address or valid hostname")
        
        # Create the NAS device
        nas_device = await self.nas_repo.create(NasCreate(**nas_dict))
        
        # Perform initial connectivity test (async, don't wait for result)
        asyncio.create_task(self._perform_initial_connectivity_test(nas_device.id))
        
        return NasResponse.from_orm(nas_device)
    
    async def update_nas(
        self, 
        nas_id: int, 
        nas_data: NasUpdate,
        updated_by: Optional[str] = None
    ) -> NasResponse:
        """
        Update NAS device with validation
        
        Args:
            nas_id: NAS ID to update
            nas_data: Update data
            updated_by: Username who updated the NAS
            
        Returns:
            Updated NAS response
        """
        # Add audit fields
        update_dict = nas_data.dict(exclude_unset=True)
        update_dict['updated_by'] = updated_by
        
        # Validate NAS name format if being updated
        if 'nasname' in update_dict:
            if not self._validate_nas_name(update_dict['nasname']):
                raise ValueError("Invalid NAS name format")
        
        # Update NAS device
        nas_device = await self.nas_repo.update(nas_id, NasUpdate(**update_dict))
        
        return NasResponse.from_orm(nas_device)
    
    async def get_nas_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "shortname",
        sort_order: str = "asc"
    ) -> Tuple[List[NasResponse], int]:
        """
        Get paginated NAS devices with search and filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term
            filters: Additional filters
            sort_by: Sort field
            sort_order: Sort direction
            
        Returns:
            Tuple of (NAS list, total count)
        """
        nas_devices, total = await self.nas_repo.get_paginated(
            skip=skip,
            limit=limit,
            search_fields=['nasname', 'shortname', 'description', 'server'] if search else None,
            search_term=search,
            filters=filters or {},
            order_by=sort_by,
            order_desc=sort_order == "desc"
        )
        
        nas_responses = [NasResponse.from_orm(nas) for nas in nas_devices]
        return nas_responses, total
    
    async def test_nas_connectivity(self, nas_id: int) -> Dict[str, Any]:
        """
        Test connectivity to NAS device
        
        Args:
            nas_id: NAS device ID
            
        Returns:
            Connectivity test results
        """
        nas_device = await self.nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise ValueError("NAS device not found")
        
        results = {
            "nas_id": nas_id,
            "nasname": nas_device.nasname,
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {}
        }
        
        # Test basic network connectivity (ping)
        ping_result = await self._test_ping_connectivity(nas_device.nasname)
        results["tests"]["ping"] = ping_result
        
        # Test RADIUS port connectivity
        radius_result = await self._test_radius_ports(nas_device.nasname)
        results["tests"]["radius"] = radius_result
        
        # Test SNMP if community string is provided
        if nas_device.community:
            snmp_result = await self._test_snmp_connectivity(
                nas_device.nasname, 
                nas_device.community
            )
            results["tests"]["snmp"] = snmp_result
        
        # Store monitoring result
        await self._store_monitoring_result(nas_id, results["tests"])
        
        # Update last_seen timestamp
        await self.nas_repo.update(nas_id, NasUpdate(
            last_seen=datetime.utcnow()
        ))
        
        return results
    
    async def get_nas_status(self, nas_id: int) -> Dict[str, Any]:
        """
        Get current status of NAS device
        
        Args:
            nas_id: NAS device ID
            
        Returns:
            Current status information
        """
        nas_device = await self.nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise ValueError("NAS device not found")
        
        # Get active sessions count
        active_sessions = await self._get_active_sessions_count(nas_device.nasname)
        
        # Get latest monitoring results
        latest_monitoring = await self._get_latest_monitoring(nas_id)
        
        # Calculate uptime and performance metrics
        performance_metrics = await self._calculate_performance_metrics(nas_id)
        
        return {
            "nas_id": nas_id,
            "nasname": nas_device.nasname,
            "shortname": nas_device.shortname,
            "is_active": nas_device.is_active,
            "last_seen": nas_device.last_seen.isoformat() if nas_device.last_seen else None,
            "active_sessions": active_sessions,
            "total_ports": nas_device.ports,
            "port_utilization": (active_sessions / nas_device.ports * 100) if nas_device.ports else 0,
            "monitoring": latest_monitoring,
            "performance": performance_metrics,
            "status": self._determine_overall_status(latest_monitoring, active_sessions, nas_device.ports)
        }
    
    async def get_nas_active_sessions(
        self, 
        nas_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get active sessions for a specific NAS device
        
        Args:
            nas_id: NAS device ID
            skip: Number of sessions to skip
            limit: Maximum sessions to return
            
        Returns:
            Active sessions data
        """
        nas_device = await self.nas_repo.get_by_id(nas_id)
        if not nas_device:
            raise ValueError("NAS device not found")
        
        # Query active sessions (no AcctStopTime)
        query = select(RadAcct).where(
            and_(
                RadAcct.nas_ip_address == nas_device.nasname,
                RadAcct.acct_stop_time.is_(None)
            )
        ).offset(skip).limit(limit).order_by(RadAcct.acct_start_time.desc())
        
        result = await self.nas_repo.db.execute(query)
        sessions = result.scalars().all()
        
        # Count total active sessions
        count_query = select(func.count(RadAcct.rad_acct_id)).where(
            and_(
                RadAcct.nas_ip_address == nas_device.nasname,
                RadAcct.acct_stop_time.is_(None)
            )
        )
        count_result = await self.nas_repo.db.execute(count_query)
        total = count_result.scalar()
        
        return {
            "sessions": [
                {
                    "session_id": session.acct_session_id,
                    "username": session.username,
                    "start_time": session.acct_start_time.isoformat(),
                    "session_time": session.acct_session_time or 0,
                    "input_octets": session.acct_input_octets or 0,
                    "output_octets": session.acct_output_octets or 0,
                    "framed_ip": session.framed_ip_address,
                    "calling_station": session.calling_station_id,
                    "called_station": session.called_station_id
                }
                for session in sessions
            ],
            "total": total,
            "page": skip // limit + 1,
            "per_page": limit,
            "pages": (total + limit - 1) // limit
        }
    
    async def has_active_sessions(self, nas_id: int) -> bool:
        """
        Check if NAS device has active sessions
        
        Args:
            nas_id: NAS device ID
            
        Returns:
            True if has active sessions, False otherwise
        """
        nas_device = await self.nas_repo.get_by_id(nas_id)
        if not nas_device:
            return False
        
        count = await self._get_active_sessions_count(nas_device.nasname)
        return count > 0
    
    async def batch_delete_nas(self, nas_ids: List[int]) -> Dict[str, Any]:
        """
        Delete multiple NAS devices in batch
        
        Args:
            nas_ids: List of NAS device IDs
            
        Returns:
            Batch operation result
        """
        result = {
            "total_requested": len(nas_ids),
            "deleted_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        for nas_id in nas_ids:
            try:
                # Check for active sessions
                if await self.has_active_sessions(nas_id):
                    result["failed_count"] += 1
                    result["errors"].append(f"NAS {nas_id} has active sessions")
                    continue
                
                success = await self.nas_repo.delete(nas_id)
                if success:
                    result["deleted_count"] += 1
                else:
                    result["failed_count"] += 1
                    result["errors"].append(f"Failed to delete NAS {nas_id}")
                    
            except Exception as e:
                result["failed_count"] += 1
                result["errors"].append(f"Error deleting NAS {nas_id}: {str(e)}")
        
        return result
    
    async def get_nas_statistics(self) -> Dict[str, Any]:
        """
        Get overview statistics for all NAS devices
        
        Returns:
            NAS statistics overview
        """
        # Get total NAS count
        total_nas = await self.nas_repo.count()
        
        # Get active NAS count
        active_nas_count = await self.nas_repo.count({"is_active": True})
        
        # Get NAS with session counts
        nas_with_sessions = await self.nas_repo.get_nas_with_session_count()
        
        total_active_sessions = sum(nas["active_sessions"] for nas in nas_with_sessions)
        
        # Calculate utilization
        total_ports = sum(
            nas.ports for nas in await self.nas_repo.get_multi(limit=1000)
            if nas.ports
        )
        
        utilization = (total_active_sessions / total_ports * 100) if total_ports else 0
        
        # Get NAS types distribution
        all_nas = await self.nas_repo.get_multi(limit=1000)
        type_distribution = {}
        for nas in all_nas:
            nas_type = nas.type or "other"
            type_distribution[nas_type] = type_distribution.get(nas_type, 0) + 1
        
        return {
            "total_nas": total_nas,
            "active_nas": active_nas_count,
            "inactive_nas": total_nas - active_nas_count,
            "total_active_sessions": total_active_sessions,
            "total_ports": total_ports,
            "utilization_percent": round(utilization, 2),
            "nas_by_type": type_distribution,
            "top_nas_by_sessions": sorted(
                nas_with_sessions, 
                key=lambda x: x["active_sessions"], 
                reverse=True
            )[:10]
        }
    
    # Private helper methods
    def _validate_nas_name(self, nasname: str) -> bool:
        """Validate NAS name format (IP address or hostname)"""
        try:
            # Try to resolve as hostname or validate as IP
            socket.gethostbyname(nasname)
            return True
        except socket.gaierror:
            return False
    
    async def _perform_initial_connectivity_test(self, nas_id: int):
        """Perform initial connectivity test after NAS creation"""
        try:
            await asyncio.sleep(2)  # Brief delay
            await self.test_nas_connectivity(nas_id)
        except Exception as e:
            logger.warning(f"Initial connectivity test failed for NAS {nas_id}: {str(e)}")
    
    async def _test_ping_connectivity(self, nasname: str) -> Dict[str, Any]:
        """Test ping connectivity to NAS"""
        try:
            # Simple ping test using subprocess
            import subprocess
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", nasname],
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "response_time_ms": None,  # Could parse from ping output
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {
                "success": False,
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def _test_radius_ports(self, nasname: str) -> Dict[str, Any]:
        """Test RADIUS port connectivity"""
        results = {}
        
        # Test standard RADIUS ports
        ports = [1812, 1813]  # Auth, Acct
        
        for port in ports:
            try:
                # Simple socket connection test
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(3)
                
                # For UDP, we can't really test connection, but we can test if host is reachable
                try:
                    sock.connect((nasname, port))
                    results[f"port_{port}"] = {"success": True, "error": None}
                except Exception as e:
                    results[f"port_{port}"] = {"success": False, "error": str(e)}
                finally:
                    sock.close()
                    
            except Exception as e:
                results[f"port_{port}"] = {"success": False, "error": str(e)}
        
        return results
    
    async def _test_snmp_connectivity(self, nasname: str, community: str) -> Dict[str, Any]:
        """Test SNMP connectivity"""
        try:
            # Placeholder for SNMP test
            # In real implementation, would use pysnmp or similar
            return {
                "success": False,
                "error": "SNMP testing not implemented"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _store_monitoring_result(self, nas_id: int, test_results: Dict[str, Any]):
        """Store monitoring test results"""
        try:
            # Create monitoring record
            monitoring_data = {
                "nas_id": nas_id,
                "check_time": datetime.utcnow(),
                "ping_success": test_results.get("ping", {}).get("success"),
                "radius_auth_success": test_results.get("radius", {}).get("port_1812", {}).get("success"),
                "radius_acct_success": test_results.get("radius", {}).get("port_1813", {}).get("success"),
                "snmp_success": test_results.get("snmp", {}).get("success"),
                "status": "healthy" if test_results.get("ping", {}).get("success") else "critical"
            }
            
            monitoring = NasMonitoring(**monitoring_data)
            self.nas_repo.db.add(monitoring)
            await self.nas_repo.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store monitoring result: {str(e)}")
    
    async def _get_active_sessions_count(self, nasname: str) -> int:
        """Get count of active sessions for NAS"""
        query = select(func.count(RadAcct.rad_acct_id)).where(
            and_(
                RadAcct.nas_ip_address == nasname,
                RadAcct.acct_stop_time.is_(None)
            )
        )
        
        result = await self.nas_repo.db.execute(query)
        return result.scalar() or 0
    
    async def _get_latest_monitoring(self, nas_id: int) -> Optional[Dict[str, Any]]:
        """Get latest monitoring results for NAS"""
        try:
            query = select(NasMonitoring).where(
                NasMonitoring.nas_id == nas_id
            ).order_by(NasMonitoring.check_time.desc()).limit(1)
            
            result = await self.nas_repo.db.execute(query)
            monitoring = result.scalar_one_or_none()
            
            if monitoring:
                return {
                    "check_time": monitoring.check_time.isoformat(),
                    "ping_success": monitoring.ping_success,
                    "radius_auth_success": monitoring.radius_auth_success,
                    "radius_acct_success": monitoring.radius_acct_success,
                    "snmp_success": monitoring.snmp_success,
                    "status": monitoring.status
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest monitoring: {str(e)}")
            return None
    
    async def _calculate_performance_metrics(self, nas_id: int) -> Dict[str, Any]:
        """Calculate performance metrics for NAS"""
        try:
            nas_device = await self.nas_repo.get_by_id(nas_id)
            if not nas_device:
                return {}
            
            return {
                "total_requests": nas_device.total_requests,
                "successful_requests": nas_device.successful_requests,
                "success_rate": (
                    nas_device.successful_requests / nas_device.total_requests * 100
                    if nas_device.total_requests > 0 else 0
                ),
                "last_seen": nas_device.last_seen.isoformat() if nas_device.last_seen else None
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {str(e)}")
            return {}
    
    def _determine_overall_status(
        self, 
        monitoring: Optional[Dict[str, Any]], 
        active_sessions: int,
        total_ports: Optional[int]
    ) -> str:
        """Determine overall NAS status"""
        if not monitoring:
            return "unknown"
        
        if not monitoring.get("ping_success"):
            return "critical"
        
        if not monitoring.get("radius_auth_success") or not monitoring.get("radius_acct_success"):
            return "warning"
        
        # Check port utilization
        if total_ports and active_sessions / total_ports > 0.9:
            return "warning"
        
        return "healthy"