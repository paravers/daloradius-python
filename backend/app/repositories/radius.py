"""
RADIUS Repository Implementations

This module contains repository classes for RADIUS operations including
authentication attributes, accounting records, and NAS management.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, and_, or_, func, text, desc
from sqlalchemy.exc import IntegrityError
from ipaddress import IPv4Address

from .base import BaseRepository
from ..models.radius import RadCheck, RadReply, GroupCheck, GroupReply
from ..models.accounting import RadAcct
from ..models.nas import Nas
from ..schemas.radius import (
    RadcheckCreate, RadcheckUpdate, RadreplyCreate, RadreplyUpdate,
    RadacctCreate, RadacctUpdate, NasCreate, NasUpdate,
    RadgroupcheckCreate, RadgroupreplyCreate, AccountingQuery
)


class RadcheckRepository(BaseRepository[RadCheck, RadcheckCreate, RadcheckUpdate]):
    """Repository for RADIUS check attributes (authorization)"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Radcheck, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for radcheck queries"""
        return query

    async def get_user_attributes(self, username: str) -> List[Radcheck]:
        """Get all check attributes for a user"""
        filters = {"username": username}
        return await self.get_multi(filters=filters, order_by="attribute")

    async def get_user_attribute(
        self, 
        username: str, 
        attribute: str
    ) -> Optional[Radcheck]:
        """Get specific attribute for a user"""
        query = select(Radcheck).where(
            and_(
                Radcheck.username == username,
                Radcheck.attribute == attribute
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def set_user_password(
        self,
        username: str,
        password: str,
        password_type: str = "Cleartext-Password"
    ) -> Radcheck:
        """Set or update user password in RADIUS"""
        # Check if password attribute exists
        existing = await self.get_user_attribute(username, password_type)
        
        if existing:
            # Update existing password
            update_data = RadcheckUpdate(value=password)
            return await self.update(existing, update_data)
        else:
            # Create new password attribute
            password_data = RadcheckCreate(
                username=username,
                attribute=password_type,
                op="==",
                value=password
            )
            return await self.create(password_data)

    async def set_user_attribute(
        self,
        username: str,
        attribute: str,
        operator: str,
        value: str
    ) -> Radcheck:
        """Set or update a user attribute"""
        existing = await self.get_user_attribute(username, attribute)
        
        if existing:
            update_data = RadcheckUpdate(op=operator, value=value)
            return await self.update(existing, update_data)
        else:
            attr_data = RadcheckCreate(
                username=username,
                attribute=attribute,
                op=operator,
                value=value
            )
            return await self.create(attr_data)

    async def delete_user_attribute(
        self,
        username: str,
        attribute: str
    ) -> bool:
        """Delete a specific user attribute"""
        existing = await self.get_user_attribute(username, attribute)
        if existing:
            return await self.delete(existing.id)
        return False

    async def delete_user_attributes(self, username: str) -> int:
        """Delete all attributes for a user"""
        query = select(Radcheck).where(Radcheck.username == username)
        result = await self.db.execute(query)
        attributes = result.scalars().all()
        
        if attributes:
            ids = [attr.id for attr in attributes]
            return await self.delete_multi(ids)
        return 0

    async def get_attributes_by_type(
        self,
        attribute: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Radcheck]:
        """Get all entries for a specific attribute type"""
        filters = {"attribute": attribute}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="username"
        )

    async def search_attributes(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Radcheck]:
        """Search attributes by username, attribute, or value"""
        search_fields = ["username", "attribute", "value"]
        return await self.search(
            search_term=search_term,
            search_fields=search_fields,
            skip=skip,
            limit=limit
        )


class RadreplyRepository(BaseRepository[Radreply, RadreplyCreate, RadreplyUpdate]):
    """Repository for RADIUS reply attributes (authorization response)"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Radreply, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for radreply queries"""
        return query

    async def get_user_attributes(self, username: str) -> List[Radreply]:
        """Get all reply attributes for a user"""
        filters = {"username": username}
        return await self.get_multi(filters=filters, order_by="attribute")

    async def get_user_attribute(
        self,
        username: str,
        attribute: str
    ) -> Optional[Radreply]:
        """Get specific reply attribute for a user"""
        query = select(Radreply).where(
            and_(
                Radreply.username == username,
                Radreply.attribute == attribute
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def set_user_attribute(
        self,
        username: str,
        attribute: str,
        operator: str,
        value: str
    ) -> Radreply:
        """Set or update a user reply attribute"""
        existing = await self.get_user_attribute(username, attribute)
        
        if existing:
            update_data = RadreplyUpdate(op=operator, value=value)
            return await self.update(existing, update_data)
        else:
            attr_data = RadreplyCreate(
                username=username,
                attribute=attribute,
                op=operator,
                value=value
            )
            return await self.create(attr_data)

    async def delete_user_attributes(self, username: str) -> int:
        """Delete all reply attributes for a user"""
        query = select(Radreply).where(Radreply.username == username)
        result = await self.db.execute(query)
        attributes = result.scalars().all()
        
        if attributes:
            ids = [attr.id for attr in attributes]
            return await self.delete_multi(ids)
        return 0

    async def set_session_timeout(self, username: str, timeout: int) -> Radreply:
        """Set session timeout for user"""
        return await self.set_user_attribute(
            username=username,
            attribute="Session-Timeout",
            operator=":=",
            value=str(timeout)
        )

    async def set_idle_timeout(self, username: str, timeout: int) -> Radreply:
        """Set idle timeout for user"""
        return await self.set_user_attribute(
            username=username,
            attribute="Idle-Timeout",
            operator=":=",
            value=str(timeout)
        )

    async def set_bandwidth_limits(
        self,
        username: str,
        download_kbps: Optional[int] = None,
        upload_kbps: Optional[int] = None
    ) -> List[Radreply]:
        """Set bandwidth limits for user"""
        results = []
        
        if download_kbps:
            result = await self.set_user_attribute(
                username=username,
                attribute="WISPr-Bandwidth-Max-Down",
                operator=":=",
                value=str(download_kbps * 1000)  # Convert to bps
            )
            results.append(result)
            
        if upload_kbps:
            result = await self.set_user_attribute(
                username=username,
                attribute="WISPr-Bandwidth-Max-Up",
                operator=":=",
                value=str(upload_kbps * 1000)  # Convert to bps
            )
            results.append(result)
            
        return results


class RadacctRepository(BaseRepository[Radacct, RadacctCreate, RadacctUpdate]):
    """Repository for RADIUS accounting records"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Radacct, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for radacct queries"""
        return query

    async def get_user_sessions(
        self,
        username: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Radacct]:
        """Get accounting sessions for a user"""
        filters = {"username": username}
        
        if active_only:
            filters["acct_stop_time"] = None
            
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="acct_start_time",
            order_desc=True
        )

    async def get_active_sessions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Radacct]:
        """Get all active sessions (no stop time)"""
        filters = {"acct_stop_time": None}
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="acct_start_time",
            order_desc=True
        )

    async def get_session_by_id(self, session_id: str) -> Optional[Radacct]:
        """Get session by accounting session ID"""
        return await self.get_by_field("acct_session_id", session_id)

    async def get_session_by_unique_id(self, unique_id: str) -> Optional[Radacct]:
        """Get session by unique accounting ID"""
        return await self.get_by_field("acct_unique_id", unique_id)

    async def start_session(self, session_data: RadacctCreate) -> Radacct:
        """Start a new accounting session"""
        session_data.acct_start_time = datetime.utcnow()
        return await self.create(session_data)

    async def stop_session(
        self,
        unique_id: str,
        stop_data: Dict[str, Any]
    ) -> Optional[Radacct]:
        """Stop an accounting session"""
        session = await self.get_session_by_unique_id(unique_id)
        if not session:
            return None
            
        # Calculate session time if not provided
        if "acct_session_time" not in stop_data and session.acct_start_time:
            stop_time = stop_data.get("acct_stop_time", datetime.utcnow())
            duration = (stop_time - session.acct_start_time).total_seconds()
            stop_data["acct_session_time"] = int(duration)
            
        if "acct_stop_time" not in stop_data:
            stop_data["acct_stop_time"] = datetime.utcnow()
            
        update_data = RadacctUpdate(**stop_data)
        return await self.update(session, update_data)

    async def update_session(
        self,
        unique_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Radacct]:
        """Update an active session (interim update)"""
        session = await self.get_session_by_unique_id(unique_id)
        if not session:
            return None
            
        update_obj = RadacctUpdate(**update_data)
        return await self.update(session, update_obj)

    async def get_sessions_by_nas(
        self,
        nas_ip: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Radacct]:
        """Get sessions by NAS IP address"""
        filters = {"nas_ip_address": nas_ip}
        
        if active_only:
            filters["acct_stop_time"] = None
            
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="acct_start_time",
            order_desc=True
        )

    async def get_sessions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Radacct]:
        """Get sessions within date range"""
        filters = {
            "acct_start_time": {
                ">=": start_date,
                "<=": end_date
            }
        }
        
        if username:
            filters["username"] = username
            
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="acct_start_time",
            order_desc=True
        )

    async def get_user_statistics(
        self,
        username: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        query = select(
            func.count(Radacct.radacctid).label('total_sessions'),
            func.sum(Radacct.acct_session_time).label('total_time'),
            func.sum(Radacct.acct_input_octets).label('total_input'),
            func.sum(Radacct.acct_output_octets).label('total_output'),
            func.max(Radacct.acct_start_time).label('last_session')
        ).where(Radacct.username == username)
        
        if start_date:
            query = query.where(Radacct.acct_start_time >= start_date)
        if end_date:
            query = query.where(Radacct.acct_start_time <= end_date)
            
        result = await self.db.execute(query)
        row = result.first()
        
        return {
            "total_sessions": row.total_sessions or 0,
            "total_session_time": row.total_time or 0,
            "total_input_octets": row.total_input or 0,
            "total_output_octets": row.total_output or 0,
            "total_data_mb": ((row.total_input or 0) + (row.total_output or 0)) / (1024 * 1024),
            "last_session_start": row.last_session
        }

    async def get_daily_statistics(
        self,
        start_date: date,
        end_date: date,
        username: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get daily usage statistics"""
        query = select(
            func.date(Radacct.acct_start_time).label('date'),
            func.count(Radacct.radacctid).label('sessions'),
            func.sum(Radacct.acct_session_time).label('total_time'),
            func.sum(Radacct.acct_input_octets + Radacct.acct_output_octets).label('total_bytes')
        ).where(
            func.date(Radacct.acct_start_time).between(start_date, end_date)
        ).group_by(
            func.date(Radacct.acct_start_time)
        ).order_by(
            func.date(Radacct.acct_start_time)
        )
        
        if username:
            query = query.where(Radacct.username == username)
            
        result = await self.db.execute(query)
        
        return [
            {
                "date": row.date,
                "sessions": row.sessions or 0,
                "total_session_time": row.total_time or 0,
                "total_data_mb": (row.total_bytes or 0) / (1024 * 1024)
            }
            for row in result.all()
        ]

    async def get_top_users_by_usage(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
        sort_by: str = "data"  # "data", "time", or "sessions"
    ) -> List[Dict[str, Any]]:
        """Get top users by usage metrics"""
        if sort_by == "data":
            order_field = func.sum(Radacct.acct_input_octets + Radacct.acct_output_octets).desc()
        elif sort_by == "time":
            order_field = func.sum(Radacct.acct_session_time).desc()
        else:  # sessions
            order_field = func.count(Radacct.radacctid).desc()
            
        query = select(
            Radacct.username,
            func.count(Radacct.radacctid).label('sessions'),
            func.sum(Radacct.acct_session_time).label('total_time'),
            func.sum(Radacct.acct_input_octets + Radacct.acct_output_octets).label('total_bytes')
        ).where(
            Radacct.acct_start_time.between(start_date, end_date)
        ).group_by(
            Radacct.username
        ).order_by(
            order_field
        ).limit(limit)
        
        result = await self.db.execute(query)
        
        return [
            {
                "username": row.username,
                "sessions": row.sessions or 0,
                "total_session_time": row.total_time or 0,
                "total_data_mb": (row.total_bytes or 0) / (1024 * 1024)
            }
            for row in result.all()
        ]


class NasRepository(BaseRepository[Nas, NasCreate, NasUpdate]):
    """Repository for Network Access Server (NAS) management"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Nas, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for NAS queries"""
        return query

    async def get_by_name(self, nasname: str) -> Optional[Nas]:
        """Get NAS by name"""
        return await self.get_by_field("nasname", nasname)

    async def get_by_shortname(self, shortname: str) -> Optional[Nas]:
        """Get NAS by short name"""
        return await self.get_by_field("shortname", shortname)

    async def get_active_nas(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Nas]:
        """Get all active NAS devices"""
        # Assuming there's an 'active' field, otherwise return all
        return await self.get_multi(
            skip=skip,
            limit=limit,
            order_by="shortname"
        )

    async def search_nas(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Nas]:
        """Search NAS devices"""
        search_fields = ["nasname", "shortname", "description", "server"]
        return await self.search(
            search_term=search_term,
            search_fields=search_fields,
            skip=skip,
            limit=limit
        )

    async def get_nas_with_session_count(self) -> List[Dict[str, Any]]:
        """Get NAS devices with active session count"""
        query = select(
            Nas.id,
            Nas.nasname,
            Nas.shortname,
            func.count(Radacct.radacctid).label('active_sessions')
        ).outerjoin(
            Radacct,
            and_(
                Nas.nasname == Radacct.nas_ip_address,
                Radacct.acct_stop_time.is_(None)
            )
        ).group_by(
            Nas.id,
            Nas.nasname,
            Nas.shortname
        ).order_by(Nas.shortname)
        
        result = await self.db.execute(query)
        
        return [
            {
                "id": row.id,
                "nasname": row.nasname,
                "shortname": row.shortname,
                "active_sessions": row.active_sessions or 0
            }
            for row in result.all()
        ]


class RadgroupcheckRepository(BaseRepository[Radgroupcheck, RadgroupcheckCreate, None]):
    """Repository for RADIUS group check attributes"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Radgroupcheck, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for radgroupcheck queries"""
        return query

    async def get_group_attributes(self, groupname: str) -> List[Radgroupcheck]:
        """Get all check attributes for a group"""
        filters = {"groupname": groupname}
        return await self.get_multi(filters=filters, order_by="attribute")

    async def set_group_attribute(
        self,
        groupname: str,
        attribute: str,
        operator: str,
        value: str
    ) -> Radgroupcheck:
        """Set or update a group attribute"""
        # Check if attribute exists
        query = select(Radgroupcheck).where(
            and_(
                Radgroupcheck.groupname == groupname,
                Radgroupcheck.attribute == attribute
            )
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.op = operator
            existing.value = value
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new
            attr_data = RadgroupcheckCreate(
                groupname=groupname,
                attribute=attribute,
                op=operator,
                value=value
            )
            return await self.create(attr_data)


class RadgroupreplyRepository(BaseRepository[Radgroupreply, RadgroupreplyCreate, None]):
    """Repository for RADIUS group reply attributes"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Radgroupreply, db_session)

    def _add_relationship_loading(self, query):
        """Add relationship loading for radgroupreply queries"""
        return query

    async def get_group_attributes(self, groupname: str) -> List[Radgroupreply]:
        """Get all reply attributes for a group"""
        filters = {"groupname": groupname}
        return await self.get_multi(filters=filters, order_by="attribute")

    async def set_group_attribute(
        self,
        groupname: str,
        attribute: str,
        operator: str,
        value: str
    ) -> Radgroupreply:
        """Set or update a group reply attribute"""
        # Check if attribute exists
        query = select(Radgroupreply).where(
            and_(
                Radgroupreply.groupname == groupname,
                Radgroupreply.attribute == attribute
            )
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.op = operator
            existing.value = value
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new
            attr_data = RadgroupreplyCreate(
                groupname=groupname,
                attribute=attribute,
                op=operator,
                value=value
            )
            return await self.create(attr_data)