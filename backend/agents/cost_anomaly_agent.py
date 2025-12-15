"""Cost Anomaly Detection Agent for continuous spending monitoring."""
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
from strands_agents import Agent, Tool
from tools.cost_tools import (
    get_cost_anomalies,
    configure_cost_monitor,
    analyze_cost_anomaly
)
from tools.alerting_tools import send_sns_notification, send_slack_alert
from config import settings


class CostAnomalyDetectionAgent(Agent):
    """
    Agent that continuously monitors AWS costs for anomalies and unusual spending patterns.
    Runs 24/7 and detects cost spikes, budget overruns, and unexpected charges.
    """
    
    def __init__(self):
        super().__init__(
            name="CostAnomalyDetectionAgent",
            description="Monitors AWS costs for anomalies and unusual spending patterns",
            tools=[
                Tool(get_cost_anomalies),
                Tool(configure_cost_monitor),
                Tool(analyze_cost_anomaly),
                Tool(send_sns_notification),
                Tool(send_slack_alert)
            ]
        )
        self.last_check_time = None
        self.running = False
        self.detected_anomalies = []
        self.monitors_configured = False
    
    async def initialize_monitors(self):
        """Initialize cost anomaly detection monitors."""
        if self.monitors_configured:
            return
        
        try:
            print(f"[{self.name}] Initializing cost anomaly monitors...")
            
            # Configure monitors for different dimensions
            monitor_types = [
                ("SERVICE", "Service-level cost monitoring"),
                ("LINKED_ACCOUNT", "Account-level cost monitoring")
            ]
            
            for monitor_type, description in monitor_types:
                monitor_arn = await self.execute_tool(
                    "configure_cost_monitor",
                    monitor_type=monitor_type,
                    monitor_name=f"aws-track-agent-{monitor_type.lower()}",
                    threshold=0.1  # 10% threshold
                )
                
                if monitor_arn:
                    print(f"[{self.name}] Configured {monitor_type} monitor: {monitor_arn}")
            
            self.monitors_configured = True
            
        except Exception as e:
            print(f"[{self.name}] Error initializing monitors: {e}")
    
    async def monitor_continuously(self):
        """Main continuous monitoring loop."""
        self.running = True
        
        # Initialize monitors on startup
        if settings.cost_anomaly_detection_enabled:
            await self.initialize_monitors()
        
        print(f"[{self.name}] Starting continuous cost monitoring...")
        
        while self.running:
            try:
                await self.check_cost_anomalies()
                await asyncio.sleep(settings.cost_check_interval_seconds)
            except Exception as e:
                print(f"[{self.name}] Error in monitoring loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying
    
    async def check_cost_anomalies(self):
        """Check for cost anomalies."""
        try:
            if not settings.cost_anomaly_detection_enabled:
                return
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            print(f"[{self.name}] Checking cost anomalies from {start_date} to {end_date}")
            
            # Get anomalies
            anomalies = await self.execute_tool(
                "get_cost_anomalies",
                start_date=start_date,
                end_date=end_date
            )
            
            if not anomalies:
                print(f"[{self.name}] No cost anomalies detected")
                self.last_check_time = datetime.now()
                return
            
            print(f"[{self.name}] Found {len(anomalies)} cost anomalies")
            
            # Process each anomaly
            new_anomalies = []
            for anomaly in anomalies:
                anomaly_id = anomaly.get("anomaly_id", "")
                
                # Check if we've already processed this anomaly
                if not any(a.get("anomaly_id") == anomaly_id for a in self.detected_anomalies):
                    new_anomalies.append(anomaly)
                    self.detected_anomalies.append(anomaly)
                    
                    # Analyze and handle the anomaly
                    await self.handle_cost_anomaly(anomaly)
            
            self.last_check_time = datetime.now()
            
            if new_anomalies:
                print(f"[{self.name}] Processed {len(new_anomalies)} new anomalies")
            
        except Exception as e:
            print(f"[{self.name}] Error checking cost anomalies: {e}")
            raise
    
    async def handle_cost_anomaly(self, anomaly: Dict):
        """Handle a detected cost anomaly."""
        try:
            anomaly_id = anomaly.get("anomaly_id", "")
            impact = anomaly.get("impact", {})
            root_causes = anomaly.get("root_cause", [])
            dimension_value = anomaly.get("dimension_value", "Unknown")
            
            # Get detailed analysis
            analysis = await self.execute_tool("analyze_cost_anomaly", anomaly_id=anomaly_id)
            
            # Calculate severity based on impact
            total_impact = impact.get("TotalImpact", {}).get("Amount", 0)
            severity = "warning"
            if total_impact > 1000:  # $1000 threshold
                severity = "error"
            if total_impact > 10000:  # $10,000 threshold
                severity = "critical"
            
            message = f"""
Cost Anomaly Detected

Anomaly ID: {anomaly_id}
Dimension: {dimension_value}
Total Impact: ${total_impact}
Status: {anomaly.get('status', 'Unknown')}

Root Causes:
{chr(10).join([f"- {cause}" for cause in root_causes[:3]])}

Recommendations:
{chr(10).join([f"- {rec}" for rec in analysis.get('recommendations', [])[:3]])}

Please review and take appropriate action.
"""
            
            # Send alerts
            await self.execute_tool(
                "send_sns_notification",
                subject=f"Cost Anomaly Alert: ${total_impact} Impact",
                message=message
            )
            
            await self.execute_tool(
                "send_slack_alert",
                message=message,
                severity=severity
            )
            
            print(f"[{self.name}] Alert sent for cost anomaly: {anomaly_id}")
            
        except Exception as e:
            print(f"[{self.name}] Error handling cost anomaly: {e}")
    
    def stop(self):
        """Stop the continuous monitoring."""
        self.running = False
        print(f"[{self.name}] Stopping cost monitoring...")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "name": self.name,
            "running": self.running,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "anomalies_detected_count": len(self.detected_anomalies),
            "monitors_configured": self.monitors_configured,
            "check_interval_seconds": settings.cost_check_interval_seconds
        }
