"""
Help System API Routes

Provides help content, documentation, and support resources for daloRADIUS system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.access_control import User
from app.models.system import NotificationTemplate
from app.services.config import MessageService
from app.schemas.config import MessageResponse, MessageType

router = APIRouter()


@router.get("/resources")
async def get_help_resources():
    """
    Get help resources and external links

    Returns static help resources including documentation links,
    support contacts, and community resources.
    """
    return {
        "documentation": {
            "user_guide": "https://docs.daloradius.com/user-guide/",
            "admin_guide": "https://docs.daloradius.com/admin-guide/",
            "api_documentation": "https://docs.daloradius.com/api/",
            "installation_guide": "https://docs.daloradius.com/installation/"
        },
        "support": {
            "official_website": "https://www.daloradius.com",
            "github_project": "https://github.com/lirantal/daloradius",
            "issue_tracker": "https://github.com/lirantal/daloradius/issues",
            "community_forum": "https://github.com/lirantal/daloradius/discussions"
        },
        "contact": {
            "support_email": "support@daloradius.com",
            "documentation_email": "docs@daloradius.com",
            "security_email": "security@daloradius.com"
        },
        "version_info": {
            "current_version": "3.0.0",
            "release_date": "2024-01-01",
            "changelog_url": "https://github.com/lirantal/daloradius/releases"
        }
    }


@router.get("/content")
async def get_help_content(
    category: Optional[str] = Query(None, description="Help content category"),
    page: Optional[str] = Query(None, description="Specific help page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get help content from the system message database

    Returns help content for specific categories or pages.
    """
    try:
        message_service = MessageService(db)

        if category:
            # Get help messages for specific category
            messages = await message_service.get_messages_by_type(MessageType.SUPPORT)
            help_content = []

            for message in messages:
                help_content.append({
                    "id": message.id,
                    "title": f"Help: {category}",
                    "content": message.content,
                    "created_on": message.created_on,
                    "modified_on": message.modified_on
                })

            return {
                "category": category,
                "content": help_content,
                "total": len(help_content)
            }

        # Get all help content
        all_messages = await message_service.get_all_messages()
        help_messages = [
            msg for msg in all_messages if "help" in msg.content.lower()]

        return {
            "general_help": help_messages,
            "total": len(help_messages)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch help content: {str(e)}"
        )


@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get system information for help and support

    Returns system version, environment details, and configuration info
    useful for support and troubleshooting.
    """
    return {
        "system": {
            "name": "daloRADIUS Modern",
            "version": "3.0.0-python",
            "build": "stable",
            "environment": "production"
        },
        "platform": {
            "os": "Linux",
            "python_version": "3.9+",
            "database": "MySQL/PostgreSQL",
            "web_server": "FastAPI + Uvicorn"
        },
        "modules": {
            "user_management": "enabled",
            "accounting": "enabled",
            "billing": "enabled",
            "nas_management": "enabled",
            "reports": "enabled",
            "hotspots": "enabled",
            "dashboard": "enabled",
            "notifications": "enabled"
        },
        "support_info": {
            "user_role": current_user.operator_type if hasattr(current_user, 'operator_type') else 'user',
            "installation_date": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


@router.get("/troubleshooting")
async def get_troubleshooting_guide():
    """
    Get troubleshooting guide and common solutions

    Returns structured troubleshooting information for common issues.
    """
    return {
        "common_issues": [
            {
                "issue": "Unable to login",
                "solutions": [
                    "Check username and password",
                    "Verify user account is active",
                    "Clear browser cache and cookies",
                    "Contact system administrator"
                ],
                "category": "authentication"
            },
            {
                "issue": "RADIUS authentication failures",
                "solutions": [
                    "Check RADIUS server status",
                    "Verify NAS configuration",
                    "Review RADIUS logs",
                    "Test with radtest utility"
                ],
                "category": "radius"
            },
            {
                "issue": "Dashboard data not loading",
                "solutions": [
                    "Check database connectivity",
                    "Verify API endpoints are responsive",
                    "Clear browser cache",
                    "Check system logs for errors"
                ],
                "category": "dashboard"
            },
            {
                "issue": "Reports generation failing",
                "solutions": [
                    "Check disk space for temp files",
                    "Verify database permissions",
                    "Review report query parameters",
                    "Check system resource usage"
                ],
                "category": "reports"
            }
        ],
        "diagnostic_tools": {
            "database_check": "/api/v1/system/database-status",
            "radius_check": "/api/v1/system/radius-status",
            "api_health": "/health",
            "system_logs": "/api/v1/logs/system"
        },
        "contact_support": {
            "when_to_contact": [
                "Persistent system errors",
                "Data corruption issues",
                "Security concerns",
                "Custom feature requests"
            ],
            "required_info": [
                "System version and build",
                "Error messages or logs",
                "Steps to reproduce issue",
                "Environment details"
            ]
        }
    }


@router.get("/tutorials")
async def get_tutorials():
    """
    Get interactive tutorials and getting started guides

    Returns structured tutorial content for common tasks.
    """
    return {
        "getting_started": [
            {
                "title": "First Login and Setup",
                "steps": [
                    "Access the login page",
                    "Enter your credentials",
                    "Configure your profile",
                    "Explore the dashboard"
                ],
                "estimated_time": "5 minutes",
                "difficulty": "beginner"
            },
            {
                "title": "Adding Your First User",
                "steps": [
                    "Navigate to User Management",
                    "Click 'Add New User'",
                    "Fill in user details",
                    "Set authentication method",
                    "Save and test login"
                ],
                "estimated_time": "10 minutes",
                "difficulty": "beginner"
            }
        ],
        "advanced_tutorials": [
            {
                "title": "Setting Up NAS Devices",
                "steps": [
                    "Gather NAS device information",
                    "Add NAS in management section",
                    "Configure RADIUS settings",
                    "Test authentication flow"
                ],
                "estimated_time": "20 minutes",
                "difficulty": "intermediate"
            },
            {
                "title": "Creating Custom Reports",
                "steps": [
                    "Access Reports section",
                    "Choose report type",
                    "Configure parameters",
                    "Generate and export"
                ],
                "estimated_time": "15 minutes",
                "difficulty": "intermediate"
            }
        ],
        "video_tutorials": {
            "available": False,
            "planned": True,
            "coming_soon": "Video tutorials are in development"
        }
    }


@router.post("/feedback")
async def submit_feedback(
    feedback_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit user feedback about the help system

    Allows users to provide feedback on help content and suggestions.
    """
    try:
        # In a real implementation, this would save to a feedback table
        # For now, we'll return a success response

        feedback_entry = {
            "user_id": current_user.id,
            "category": feedback_data.get("category", "general"),
            "rating": feedback_data.get("rating", 0),
            "comment": feedback_data.get("comment", ""),
            "helpful": feedback_data.get("helpful", False),
            "submitted_at": datetime.utcnow(),
            "user_agent": feedback_data.get("user_agent", ""),
            "page_url": feedback_data.get("page_url", "")
        }

        return {
            "status": "success",
            "message": "Thank you for your feedback!",
            "feedback_id": f"fb_{datetime.now().timestamp()}",
            "follow_up": "Your feedback helps us improve the system."
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )
