"""Test endpoints for sample data injection."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.sample_data import (
    generate_sample_cloudtrail_events,
    generate_sample_cost_anomalies,
    generate_sample_dashboard_stats
)
router = APIRouter(prefix="/api/test", tags=["test"])

# Global orchestrator reference (will be set by main.py)
_orchestrator = None

def set_orchestrator(orchestrator):
    """Set the orchestrator instance."""
    global _orchestrator
    _orchestrator = orchestrator


class InjectSampleDataRequest(BaseModel):
    cloudtrail_events_count: int = 10
    cost_anomalies_count: int = 5
    clear_existing: bool = False


@router.post("/inject-sample-data")
async def inject_sample_data(
    request: InjectSampleDataRequest
):
    """
    Inject sample data into agents for testing.
    """
    try:
        if not _orchestrator:
            raise HTTPException(status_code=500, detail="Orchestrator not initialized")
        
        cloudtrail_agent = _orchestrator.get_agent("cloudtrail")
        cost_agent = orchestrator.get_agent("cost")
        
        if not cloudtrail_agent or not cost_agent:
            raise HTTPException(status_code=404, detail="Agents not found")
        
        # Clear existing data if requested
        if request.clear_existing:
            if hasattr(cloudtrail_agent, 'suspicious_events'):
                cloudtrail_agent.suspicious_events = []
            if hasattr(cost_agent, 'detected_anomalies'):
                cost_agent.detected_anomalies = []
        
        # Generate and inject CloudTrail events
        events = generate_sample_cloudtrail_events(request.cloudtrail_events_count)
        if hasattr(cloudtrail_agent, 'suspicious_events'):
            cloudtrail_agent.suspicious_events.extend(events)
        
        # Generate and inject cost anomalies
        anomalies = generate_sample_cost_anomalies(request.cost_anomalies_count)
        if hasattr(cost_agent, 'detected_anomalies'):
            cost_agent.detected_anomalies.extend(anomalies)
        
        return {
            "message": "Sample data injected successfully",
            "cloudtrail_events_injected": len(events),
            "cost_anomalies_injected": len(anomalies),
            "total_cloudtrail_events": len(cloudtrail_agent.suspicious_events) if hasattr(cloudtrail_agent, 'suspicious_events') else 0,
            "total_cost_anomalies": len(cost_agent.detected_anomalies) if hasattr(cost_agent, 'detected_anomalies') else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-all-data")
async def clear_all_data():
    """
    Clear all data from agents.
    """
    try:
        if not _orchestrator:
            raise HTTPException(status_code=500, detail="Orchestrator not initialized")
        
        cloudtrail_agent = _orchestrator.get_agent("cloudtrail")
        cost_agent = orchestrator.get_agent("cost")
        
        if cloudtrail_agent and hasattr(cloudtrail_agent, 'suspicious_events'):
            cloudtrail_agent.suspicious_events = []
        
        if cost_agent and hasattr(cost_agent, 'detected_anomalies'):
            cost_agent.detected_anomalies = []
        
        return {
            "message": "All data cleared successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-stats")
async def get_sample_stats():
    """
    Get sample dashboard statistics (for testing frontend).
    """
    return generate_sample_dashboard_stats()
