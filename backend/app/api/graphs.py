"""
Graphs API Endpoints

This module contains FastAPI routers for graphs and dashboard functionality.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.graphs import (
    GraphDataService,
    DashboardService,
    GraphTemplateService,
    RealTimeStatsService
)
from app.schemas.graphs import (
    GraphDataRequest,
    GraphDataResponse,
    GraphQueryParams,
    DashboardOverview,
    GraphTemplateResponse,
    GraphTemplateCreate,
    GraphTemplateUpdate,
    DashboardWidgetResponse,
    DashboardWidgetCreate,
    DashboardWidgetUpdate,
    GraphsListResponse
)
from app.models.graphs import GraphType, TimeGranularity
from app.core.auth import get_current_user
from app.models.user import User


# Create API router
graphs_router = APIRouter(prefix="/api/graphs", tags=["graphs"])
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# =============================================================================
# Graph Data Endpoints
# =============================================================================

@graphs_router.post("/data", response_model=GraphDataResponse)
async def get_graph_data(
    request: GraphDataRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get graph data based on request parameters"""
    try:
        service = GraphDataService(db)
        return await service.get_graph_data(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@graphs_router.get("/overall-logins", response_model=GraphDataResponse)
async def get_overall_logins(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    granularity: TimeGranularity = Query(TimeGranularity.DAY, description="Time granularity"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall login statistics graph"""
    request = GraphDataRequest(
        graph_type="overall_logins",
        data_source="login_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today(),
            granularity=granularity
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/download-upload-stats", response_model=GraphDataResponse)
async def get_download_upload_stats(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    granularity: TimeGranularity = Query(TimeGranularity.DAY, description="Time granularity"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get download/upload statistics graph"""
    request = GraphDataRequest(
        graph_type="download_upload_stats",
        data_source="traffic_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today(),
            granularity=granularity
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/logged-users", response_model=GraphDataResponse)
async def get_logged_users(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get logged users activity graph"""
    request = GraphDataRequest(
        graph_type="logged_users",
        data_source="user_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today(),
            granularity=TimeGranularity.DAY
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/alltime-stats", response_model=GraphDataResponse)
async def get_alltime_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all-time statistics overview"""
    request = GraphDataRequest(
        graph_type="alltime_stats",
        data_source="aggregate_statistics",
        time_range=GraphQueryParams()
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/top-users", response_model=GraphDataResponse)
async def get_top_users(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=100, description="Number of top users"),
    traffic_type: str = Query("total", description="Traffic type: total, upload, download"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top users by traffic"""
    request = GraphDataRequest(
        graph_type="top_users",
        data_source="traffic_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today(),
            limit=limit,
            filters={"traffic_type": traffic_type}
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/traffic-comparison", response_model=GraphDataResponse)
async def get_traffic_comparison(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get traffic comparison (upload vs download)"""
    request = GraphDataRequest(
        graph_type="traffic_comparison",
        data_source="traffic_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today(),
            granularity=TimeGranularity.DAY
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


@graphs_router.get("/system-performance", response_model=GraphDataResponse)
async def get_system_performance(
    hours: int = Query(24, ge=1, le=168, description="Hours to show"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get system performance metrics"""
    request = GraphDataRequest(
        graph_type="system_performance",
        data_source="system_metrics",
        time_range=GraphQueryParams(
            filters={"hours": hours}
        )
    )
    
    service = GraphDataService(db)
    return await service.get_graph_data(request)


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@dashboard_router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard overview"""
    service = DashboardService(db)
    return await service.get_dashboard_overview()


@dashboard_router.get("/widgets/{dashboard_id}")
async def get_dashboard_widgets(
    dashboard_id: str = Path(..., description="Dashboard ID"),
    include_shared: bool = Query(True, description="Include shared widgets"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard widgets with data"""
    service = DashboardService(db)
    return await service.get_dashboard_widgets(
        dashboard_id, current_user.username, include_shared
    )


@dashboard_router.post("/widgets", response_model=DashboardWidgetResponse)
async def create_dashboard_widget(
    widget: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dashboard widget"""
    from app.repositories.graphs import DashboardWidgetRepository
    
    widget_data = widget.dict()
    widget_data['created_by'] = current_user.username
    
    repo = DashboardWidgetRepository(db)
    new_widget = await repo.create(**widget_data)
    return new_widget


@dashboard_router.put("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_dashboard_widget(
    widget_id: int = Path(..., description="Widget ID"),
    widget_update: DashboardWidgetUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update dashboard widget"""
    from app.repositories.graphs import DashboardWidgetRepository
    
    repo = DashboardWidgetRepository(db)
    
    # Check if widget exists and user has permission
    existing_widget = await repo.get_by_id(widget_id)
    if not existing_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    if existing_widget.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Update widget
    update_data = widget_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(existing_widget, key):
            setattr(existing_widget, key, value)
    
    await db.commit()
    await db.refresh(existing_widget)
    return existing_widget


@dashboard_router.put("/widgets/{widget_id}/position")
async def update_widget_position(
    widget_id: int = Path(..., description="Widget ID"),
    position_x: int = Query(..., description="X position"),
    position_y: int = Query(..., description="Y position"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update widget position"""
    from app.repositories.graphs import DashboardWidgetRepository
    
    repo = DashboardWidgetRepository(db)
    
    # Check permission
    widget = await repo.get_by_id(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    if widget.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    updated_widget = await repo.update_position(widget_id, position_x, position_y)
    return {"message": "Widget position updated", "widget_id": widget_id}


@dashboard_router.put("/widgets/{widget_id}/size")
async def update_widget_size(
    widget_id: int = Path(..., description="Widget ID"),
    width: int = Query(..., ge=1, le=12, description="Width"),
    height: int = Query(..., ge=1, le=12, description="Height"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update widget size"""
    from app.repositories.graphs import DashboardWidgetRepository
    
    repo = DashboardWidgetRepository(db)
    
    # Check permission
    widget = await repo.get_by_id(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    if widget.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    updated_widget = await repo.update_size(widget_id, width, height)
    return {"message": "Widget size updated", "widget_id": widget_id}


@dashboard_router.delete("/widgets/{widget_id}")
async def delete_dashboard_widget(
    widget_id: int = Path(..., description="Widget ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete dashboard widget"""
    from app.repositories.graphs import DashboardWidgetRepository
    
    repo = DashboardWidgetRepository(db)
    
    # Check permission
    widget = await repo.get_by_id(widget_id)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    if widget.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    success = await repo.delete(widget_id)
    if success:
        return {"message": "Widget deleted", "widget_id": widget_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete widget")


# =============================================================================
# Graph Template Endpoints
# =============================================================================

@graphs_router.get("/templates", response_model=List[Dict[str, Any]])
async def get_graph_templates(
    category: Optional[str] = Query(None, description="Template category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available graph templates"""
    service = GraphTemplateService(db)
    return await service.get_available_templates(category)


@graphs_router.post("/templates", response_model=Dict[str, Any])
async def create_graph_template(
    template: GraphTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new graph template"""
    from app.repositories.graphs import GraphTemplateRepository
    
    template_data = template.dict()
    template_data['created_by'] = current_user.username
    
    repo = GraphTemplateRepository(db)
    new_template = await repo.create(**template_data)
    
    return {
        'id': new_template.id,
        'name': new_template.name,
        'description': new_template.description,
        'category': new_template.category,
        'graph_type': new_template.graph_type.value,
        'created_at': new_template.created_at
    }


@graphs_router.get("/templates/{template_id}", response_model=GraphTemplateResponse)
async def get_graph_template(
    template_id: int = Path(..., description="Template ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific graph template"""
    from app.repositories.graphs import GraphTemplateRepository
    
    repo = GraphTemplateRepository(db)
    template = await repo.get_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@graphs_router.put("/templates/{template_id}", response_model=GraphTemplateResponse)
async def update_graph_template(
    template_id: int = Path(..., description="Template ID"),
    template_update: GraphTemplateUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update graph template"""
    from app.repositories.graphs import GraphTemplateRepository
    
    repo = GraphTemplateRepository(db)
    
    # Check if template exists and user has permission
    existing_template = await repo.get_by_id(template_id)
    if not existing_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if existing_template.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Update template
    update_data = template_update.dict(exclude_unset=True)
    updated_template = await repo.update(template_id, **update_data)
    
    if not updated_template:
        raise HTTPException(status_code=500, detail="Failed to update template")
    
    return updated_template


# =============================================================================
# Real-time Statistics Endpoints
# =============================================================================

@graphs_router.get("/realtime/stats")
async def get_realtime_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time system statistics"""
    service = RealTimeStatsService(db)
    return await service.get_live_stats()


@graphs_router.get("/realtime/trends")
async def get_realtime_trends(
    hours: int = Query(24, ge=1, le=168, description="Hours to show"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time hourly trends"""
    service = RealTimeStatsService(db)
    return await service.get_hourly_trends(hours)


# =============================================================================
# Data Export Endpoints
# =============================================================================

@graphs_router.get("/export/csv")
async def export_graph_data_csv(
    graph_type: str = Query(..., description="Graph type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export graph data as CSV"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    # Get graph data
    request = GraphDataRequest(
        graph_type=graph_type,
        data_source=f"{graph_type}_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today()
        )
    )
    
    service = GraphDataService(db)
    graph_data = await service.get_graph_data(request)
    
    # Convert to CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    if graph_data.data.get('labels') and graph_data.data.get('datasets'):
        headers = ['Date'] + [dataset['label'] for dataset in graph_data.data['datasets']]
        writer.writerow(headers)
        
        # Write data rows
        labels = graph_data.data['labels']
        for i, label in enumerate(labels):
            row = [label]
            for dataset in graph_data.data['datasets']:
                row.append(dataset['data'][i] if i < len(dataset['data']) else '')
            writer.writerow(row)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={graph_type}_export.csv"}
    )


@graphs_router.get("/export/json")
async def export_graph_data_json(
    graph_type: str = Query(..., description="Graph type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export graph data as JSON"""
    from fastapi.responses import JSONResponse
    
    # Get graph data
    request = GraphDataRequest(
        graph_type=graph_type,
        data_source=f"{graph_type}_statistics",
        time_range=GraphQueryParams(
            start_date=start_date or date.today() - timedelta(days=30),
            end_date=end_date or date.today()
        )
    )
    
    service = GraphDataService(db)
    graph_data = await service.get_graph_data(request)
    
    return JSONResponse(
        content=graph_data.dict(),
        headers={"Content-Disposition": f"attachment; filename={graph_type}_export.json"}
    )


# =============================================================================
# Graph Types and Metadata Endpoints
# =============================================================================

@graphs_router.get("/types")
async def get_available_graph_types(
    current_user: User = Depends(get_current_user)
):
    """Get available graph types"""
    return {
        "graph_types": [
            {
                "id": "overall_logins",
                "name": "Overall Logins",
                "description": "Login statistics over time",
                "category": "authentication"
            },
            {
                "id": "download_upload_stats",
                "name": "Download/Upload Stats",
                "description": "Traffic download and upload statistics",
                "category": "traffic"
            },
            {
                "id": "logged_users",
                "name": "Logged Users",
                "description": "User activity and growth trends",
                "category": "users"
            },
            {
                "id": "alltime_stats",
                "name": "All-time Stats",
                "description": "Comprehensive system overview",
                "category": "overview"
            },
            {
                "id": "top_users",
                "name": "Top Users",
                "description": "Top users by traffic usage",
                "category": "traffic"
            },
            {
                "id": "traffic_comparison",
                "name": "Traffic Comparison",
                "description": "Upload vs download comparison",
                "category": "traffic"
            },
            {
                "id": "system_performance",
                "name": "System Performance",
                "description": "System performance metrics",
                "category": "system"
            }
        ],
        "time_granularities": [
            {"id": "hour", "name": "Hourly"},
            {"id": "day", "name": "Daily"},
            {"id": "week", "name": "Weekly"},
            {"id": "month", "name": "Monthly"},
            {"id": "year", "name": "Yearly"}
        ]
    }


# Register routers
def get_graphs_routers():
    """Get all graph-related routers"""
    return [graphs_router, dashboard_router]