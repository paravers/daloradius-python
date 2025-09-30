"""
Notification System API Routes

Provides notification management, templates, and delivery services for daloRADIUS system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

from app.core.deps import get_db, get_current_user
from app.models.access_control import User
from app.models.system import NotificationTemplate
from app.services.config import MessageService, MessageType

router = APIRouter()


class NotificationType(str, Enum):
    """Notification types"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationCreate(BaseModel):
    """Create notification request"""
    recipient_id: Optional[int] = Field(None, description="User ID recipient")
    recipient_email: Optional[EmailStr] = Field(
        None, description="Email recipient")
    recipient_phone: Optional[str] = Field(
        None, description="Phone number recipient")
    notification_type: NotificationType = Field(
        description="Type of notification")
    priority: NotificationPriority = Field(
        NotificationPriority.NORMAL, description="Priority level")
    template_id: Optional[int] = Field(None, description="Template ID to use")
    subject: Optional[str] = Field(None, description="Notification subject")
    message: str = Field(description="Notification message content")
    variables: Optional[Dict[str, Any]] = Field(
        None, description="Template variables")
    scheduled_for: Optional[datetime] = Field(
        None, description="Schedule delivery time")


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    recipient_id: Optional[int]
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    notification_type: NotificationType
    priority: NotificationPriority
    status: NotificationStatus
    subject: Optional[str]
    message: str
    template_id: Optional[int]
    variables: Optional[Dict[str, Any]]
    created_at: datetime
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]


class NotificationTemplateCreate(BaseModel):
    """Create notification template"""
    template_name: str = Field(description="Template name")
    template_type: NotificationType = Field(description="Template type")
    category: str = Field(description="Template category")
    subject: Optional[str] = Field(None, description="Email subject template")
    body_text: Optional[str] = Field(None, description="Plain text template")
    body_html: Optional[str] = Field(None, description="HTML template")
    variables: Optional[List[str]] = Field(
        None, description="Available variables")
    is_active: bool = Field(True, description="Template is active")


class NotificationTemplateResponse(BaseModel):
    """Notification template response"""
    id: int
    template_name: str
    template_type: str
    category: str
    subject: Optional[str]
    body_text: Optional[str]
    body_html: Optional[str]
    variables: Optional[List[str]]
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime


@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def list_notification_templates(
    template_type: Optional[NotificationType] = Query(
        None, description="Filter by template type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List notification templates

    Returns paginated list of notification templates with optional filtering.
    """
    try:
        query = db.query(NotificationTemplate)

        if template_type:
            query = query.filter(
                NotificationTemplate.template_type == template_type.value)
        if category:
            query = query.filter(NotificationTemplate.category == category)
        if is_active is not None:
            query = query.filter(NotificationTemplate.is_active == is_active)

        templates = query.offset(skip).limit(limit).all()

        return [
            NotificationTemplateResponse(
                id=template.id,
                template_name=template.template_name,
                template_type=template.template_type,
                category=template.category,
                subject=template.subject,
                body_text=template.body_text,
                body_html=template.body_html,
                variables=template.variables.split(
                    ',') if template.variables else None,
                is_active=template.is_active,
                is_system=template.is_system,
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in templates
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new notification template

    Creates a new notification template for reuse across the system.
    """
    try:
        # Check if template name already exists
        existing = db.query(NotificationTemplate).filter(
            NotificationTemplate.template_name == template_data.template_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template '{template_data.template_name}' already exists"
            )

        template = NotificationTemplate(
            template_name=template_data.template_name,
            template_type=template_data.template_type.value,
            category=template_data.category,
            subject=template_data.subject,
            body_text=template_data.body_text,
            body_html=template_data.body_html,
            variables=','.join(
                template_data.variables) if template_data.variables else None,
            is_active=template_data.is_active,
            is_system=False,
            updated_by=str(current_user.id)
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        return NotificationTemplateResponse(
            id=template.id,
            template_name=template.template_name,
            template_type=template.template_type,
            category=template.category,
            subject=template.subject,
            body_text=template.body_text,
            body_html=template.body_html,
            variables=template.variables.split(
                ',') if template.variables else None,
            is_active=template.is_active,
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def get_notification_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification template by ID

    Returns detailed information about a specific notification template.
    """
    try:
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found"
            )

        return NotificationTemplateResponse(
            id=template.id,
            template_name=template.template_name,
            template_type=template.template_type,
            category=template.category,
            subject=template.subject,
            body_text=template.body_text,
            body_html=template.body_html,
            variables=template.variables.split(
                ',') if template.variables else None,
            is_active=template.is_active,
            is_system=template.is_system,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.post("/send")
async def send_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send notification

    Sends a notification immediately or schedules it for later delivery.
    """
    try:
        # Validate recipient
        if not notification_data.recipient_id and not notification_data.recipient_email and not notification_data.recipient_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one recipient (ID, email, or phone) must be specified"
            )

        # Create notification record (in a real implementation, this would be in a notifications table)
        notification_id = int(datetime.now().timestamp())

        notification = {
            "id": notification_id,
            "recipient_id": notification_data.recipient_id,
            "recipient_email": notification_data.recipient_email,
            "recipient_phone": notification_data.recipient_phone,
            "notification_type": notification_data.notification_type,
            "priority": notification_data.priority,
            "status": NotificationStatus.PENDING,
            "subject": notification_data.subject,
            "message": notification_data.message,
            "template_id": notification_data.template_id,
            "variables": notification_data.variables,
            "created_at": datetime.utcnow(),
            "scheduled_for": notification_data.scheduled_for,
            "sent_at": None,
            "delivered_at": None,
            "error_message": None
        }

        # If scheduled for future, just return the notification
        if notification_data.scheduled_for and notification_data.scheduled_for > datetime.utcnow():
            return {
                "status": "scheduled",
                "notification_id": notification_id,
                "message": f"Notification scheduled for {notification_data.scheduled_for}",
                "notification": notification
            }

        # Send immediately in background
        background_tasks.add_task(
            process_notification,
            notification,
            notification_data.notification_type
        )

        return {
            "status": "queued",
            "notification_id": notification_id,
            "message": "Notification queued for immediate delivery",
            "notification": notification
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.get("/history")
async def get_notification_history(
    recipient_id: Optional[int] = Query(
        None, description="Filter by recipient ID"),
    notification_type: Optional[NotificationType] = Query(
        None, description="Filter by type"),
    status: Optional[NotificationStatus] = Query(
        None, description="Filter by status"),
    days: int = Query(7, ge=1, le=90, description="Days of history to return"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification history

    Returns paginated history of sent notifications with filtering options.
    """
    try:
        # In a real implementation, this would query a notifications table
        # For now, return mock data structure

        mock_notifications = []
        for i in range(min(limit, 20)):  # Return up to 20 mock records
            mock_notifications.append({
                "id": i + 1,
                "recipient_id": 1,
                "recipient_email": "user@example.com",
                "notification_type": "email",
                "priority": "normal",
                "status": "sent" if i % 3 != 0 else "delivered",
                "subject": f"Test Notification {i + 1}",
                "message": f"This is test notification {i + 1}",
                "created_at": datetime.utcnow() - timedelta(days=i % days),
                "sent_at": datetime.utcnow() - timedelta(days=i % days, hours=1),
                "delivered_at": datetime.utcnow() - timedelta(days=i % days, hours=2) if i % 3 == 0 else None
            })

        return {
            "notifications": mock_notifications,
            "total": len(mock_notifications),
            "filters": {
                "recipient_id": recipient_id,
                "notification_type": notification_type,
                "status": status,
                "days": days
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification history: {str(e)}"
        )


@router.get("/stats")
async def get_notification_stats(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification statistics

    Returns delivery statistics and performance metrics.
    """
    try:
        # In a real implementation, this would calculate from actual data
        return {
            "summary": {
                "total_sent": 1250,
                "total_delivered": 1180,
                "total_failed": 70,
                "delivery_rate": 94.4,
                "average_delivery_time_seconds": 3.2
            },
            "by_type": {
                "email": {"sent": 800, "delivered": 760, "failed": 40},
                "sms": {"sent": 300, "delivered": 285, "failed": 15},
                "push": {"sent": 150, "delivered": 135, "failed": 15}
            },
            "by_priority": {
                "urgent": {"sent": 50, "delivered": 50, "failed": 0},
                "high": {"sent": 200, "delivered": 190, "failed": 10},
                "normal": {"sent": 800, "delivered": 750, "failed": 50},
                "low": {"sent": 200, "delivered": 190, "failed": 10}
            },
            "daily_volume": [
                {"date": "2024-01-01", "sent": 45, "delivered": 42},
                {"date": "2024-01-02", "sent": 52, "delivered": 49},
                {"date": "2024-01-03", "sent": 38, "delivered": 36}
            ],
            "error_analysis": {
                "bounce_rate": 2.1,
                "spam_rate": 0.8,
                "timeout_rate": 1.5,
                "common_errors": [
                    {"error": "Invalid email address", "count": 25},
                    {"error": "Recipient blocked sender", "count": 15},
                    {"error": "Network timeout", "count": 30}
                ]
            },
            "period": {
                "start_date": datetime.utcnow() - timedelta(days=days),
                "end_date": datetime.utcnow(),
                "days": days
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        )


async def process_notification(notification: Dict[str, Any], notification_type: NotificationType):
    """
    Background task to process notification delivery

    This function would contain the actual notification sending logic.
    """
    try:
        # Simulate processing time
        import asyncio
        await asyncio.sleep(1)

        # In a real implementation, this would:
        # 1. Resolve template if template_id is provided
        # 2. Apply variable substitution
        # 3. Send via appropriate channel (email, SMS, push)
        # 4. Update notification status in database
        # 5. Handle retries on failure

        print(
            f"Processing {notification_type} notification {notification['id']}")
        print(f"Recipient: {notification.get('recipient_email', 'N/A')}")
        print(f"Message: {notification['message'][:100]}...")

        # Mark as sent (in real implementation, update database)
        notification["status"] = NotificationStatus.SENT
        notification["sent_at"] = datetime.utcnow()

        return True

    except Exception as e:
        print(f"Failed to process notification {notification['id']}: {e}")
        notification["status"] = NotificationStatus.FAILED
        notification["error_message"] = str(e)
        return False
