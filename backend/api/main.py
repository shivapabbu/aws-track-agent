"""FastAPI application for AWS Track Agent."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import asyncio
import sys
import os

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Try to import strands_agents, use stub if not available
try:
    import strands_agents
    print("Using strands_agents package")
except ImportError:
    print("strands_agents not found, using stub...")
    import strands_agents_stub
    sys.modules['strands_agents'] = strands_agents_stub

from agents.orchestrator_agent import OrchestratorAgent
from config import settings

app = FastAPI(title="AWS Track Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = OrchestratorAgent()

# Set orchestrator for test endpoints and include router
if settings.test_mode or settings.use_sample_data:
    from api.test_endpoints import set_orchestrator, router as test_router
    set_orchestrator(orchestrator)
    app.include_router(test_router)


# Pydantic models
class AgentStatusResponse(BaseModel):
    name: str
    running: bool
    last_check_time: Optional[str]
    status: Dict


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agents: Dict


class StartMonitoringRequest(BaseModel):
    agent_name: Optional[str] = None  # None means start all


class AlertResponse(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    timestamp: str
    metadata: Dict


@app.on_event("startup")
async def startup_event():
    """Start all agents on application startup."""
    print("Starting AWS Track Agent...")
    await orchestrator.start_all_agents()
    print("AWS Track Agent started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop all agents on application shutdown."""
    print("Shutting down AWS Track Agent...")
    await orchestrator.stop_all_agents()
    print("AWS Track Agent stopped")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AWS Track Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    status = orchestrator.get_all_agent_status()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        agents=status
    )


@app.get("/api/agents", response_model=Dict)
async def get_agents():
    """Get status of all agents."""
    return orchestrator.get_all_agent_status()


@app.get("/api/agents/{agent_name}", response_model=AgentStatusResponse)
async def get_agent(agent_name: str):
    """Get status of a specific agent."""
    agent = orchestrator.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    status = agent.get_status()
    return AgentStatusResponse(
        name=status["name"],
        running=status["running"],
        last_check_time=status.get("last_check_time"),
        status=status
    )


@app.post("/api/agents/start")
async def start_agent(request: StartMonitoringRequest):
    """Start a specific agent or all agents."""
    if request.agent_name:
        agent = orchestrator.get_agent(request.agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
        
        if agent.running:
            return {"message": f"Agent '{request.agent_name}' is already running"}
        
        # Start specific agent
        if request.agent_name == "cloudtrail":
            asyncio.create_task(agent.monitor_continuously())
        elif request.agent_name == "cost":
            asyncio.create_task(agent.monitor_continuously())
        
        return {"message": f"Agent '{request.agent_name}' started"}
    else:
        # Start all agents
        await orchestrator.start_all_agents()
        return {"message": "All agents started"}


@app.post("/api/agents/stop")
async def stop_agent(request: StartMonitoringRequest):
    """Stop a specific agent or all agents."""
    if request.agent_name:
        agent = orchestrator.get_agent(request.agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")
        
        agent.stop()
        return {"message": f"Agent '{request.agent_name}' stopped"}
    else:
        await orchestrator.stop_all_agents()
        return {"message": "All agents stopped"}


@app.get("/api/cloudtrail/events")
async def get_cloudtrail_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
):
    """Get CloudTrail events (from agent's recent findings)."""
    agent = orchestrator.get_agent("cloudtrail")
    if not agent:
        raise HTTPException(status_code=404, detail="CloudTrail agent not found")
    
    events = agent.suspicious_events[-limit:] if hasattr(agent, 'suspicious_events') else []
    return {
        "events": events,
        "count": len(events),
        "total": len(agent.suspicious_events) if hasattr(agent, 'suspicious_events') else 0
    }


@app.get("/api/cost/anomalies")
async def get_cost_anomalies(limit: int = 100):
    """Get cost anomalies (from agent's recent findings)."""
    agent = orchestrator.get_agent("cost")
    if not agent:
        raise HTTPException(status_code=404, detail="Cost agent not found")
    
    anomalies = agent.detected_anomalies[-limit:] if hasattr(agent, 'detected_anomalies') else []
    return {
        "anomalies": anomalies,
        "count": len(anomalies),
        "total": len(agent.detected_anomalies) if hasattr(agent, 'detected_anomalies') else 0
    }


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    cloudtrail_agent = orchestrator.get_agent("cloudtrail")
    cost_agent = orchestrator.get_agent("cost")
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    
    stats = {
        "cloudtrail": {
            "suspicious_events": len(cloudtrail_agent.suspicious_events) if cloudtrail_agent and hasattr(cloudtrail_agent, 'suspicious_events') else 0,
            "running": cloudtrail_agent.running if cloudtrail_agent else False,
            "last_check": cloudtrail_agent.last_check_time.isoformat() if cloudtrail_agent and cloudtrail_agent.last_check_time else None
        },
        "cost": {
            "anomalies": len(cost_agent.detected_anomalies) if cost_agent and hasattr(cost_agent, 'detected_anomalies') else 0,
            "running": cost_agent.running if cost_agent else False,
            "last_check": cost_agent.last_check_time.isoformat() if cost_agent and cost_agent.last_check_time else None
        },
        "user_analytics": {
            "users_tracked": len(user_analytics_agent.user_metrics) if user_analytics_agent and hasattr(user_analytics_agent, 'user_metrics') else 0,
            "running": user_analytics_agent.running if user_analytics_agent else False,
            "last_analysis": user_analytics_agent.last_analysis_time.isoformat() if user_analytics_agent and user_analytics_agent.last_analysis_time else None
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return stats


@app.get("/api/users/analytics")
async def get_user_analytics(limit: int = 100):
    """Get user-level analytics - who is using AWS and how much."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    
    return {
        "users": user_analytics_agent.user_metrics if hasattr(user_analytics_agent, 'user_metrics') else {},
        "count": len(user_analytics_agent.user_metrics) if hasattr(user_analytics_agent, 'user_metrics') else 0
    }


@app.get("/api/users/top-by-usage")
async def get_top_users_by_usage(limit: int = 10):
    """Get top users by activity/usage."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    
    top_users = user_analytics_agent.get_top_users_by_usage(limit) if hasattr(user_analytics_agent, 'get_top_users_by_usage') else []
    return {
        "users": top_users,
        "count": len(top_users)
    }


@app.get("/api/users/top-by-cost")
async def get_top_users_by_cost(limit: int = 10):
    """Get top users by cost attribution."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    
    top_users = user_analytics_agent.get_top_users_by_cost(limit) if hasattr(user_analytics_agent, 'get_top_users_by_cost') else []
    return {
        "users": top_users,
        "count": len(top_users)
    }


@app.get("/api/users/inactive")
async def get_inactive_users(days: int = 30):
    """Get users who haven't been active recently."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    
    inactive = user_analytics_agent.get_inactive_users(days) if hasattr(user_analytics_agent, 'get_inactive_users') else []
    return {
        "users": inactive,
        "count": len(inactive),
        "days_threshold": days
    }


@app.get("/api/users/{user_name}")
async def get_user_details(user_name: str):
    """Get detailed usage summary for a specific user."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    
    # Get user summary
    summary = user_analytics_agent.user_summaries.get(user_name) if hasattr(user_analytics_agent, 'user_summaries') else None
    
    # Get user metrics
    metrics = user_analytics_agent.user_metrics.get(user_name) if hasattr(user_analytics_agent, 'user_metrics') else None
    
    # Get user costs
    costs = user_analytics_agent.user_costs.get(user_name) if hasattr(user_analytics_agent, 'user_costs') else None
    
    if not summary and not metrics:
        raise HTTPException(status_code=404, detail=f"User '{user_name}' not found")
    
    return {
        "user_name": user_name,
        "summary": summary,
        "metrics": metrics,
        "costs": costs
    }


@app.post("/api/users/analyze")
async def trigger_user_analysis():
    """Manually trigger user analytics analysis from CloudTrail events."""
    user_analytics_agent = orchestrator.get_agent("user_analytics")
    cloudtrail_agent = orchestrator.get_agent("cloudtrail")
    
    if not user_analytics_agent:
        raise HTTPException(status_code=404, detail="User Analytics agent not found")
    if not cloudtrail_agent:
        raise HTTPException(status_code=404, detail="CloudTrail agent not found")
    
    # Get events from CloudTrail agent
    events = cloudtrail_agent.suspicious_events if hasattr(cloudtrail_agent, 'suspicious_events') else []
    
    # Process events for analytics
    await user_analytics_agent.process_events_for_analytics(events)
    
    return {
        "message": "User analysis completed",
        "users_analyzed": len(user_analytics_agent.user_metrics) if hasattr(user_analytics_agent, 'user_metrics') else 0
    }


if __name__ == "__main__":
    import asyncio
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
