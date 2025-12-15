"""CloudTrail Monitoring Agent for continuous activity monitoring."""
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
import time
from strands_agents import Agent, Tool
from tools.cloudtrail_tools import (
    fetch_cloudtrail_logs,
    analyze_cloudtrail_insights,
    parse_cloudtrail_event
)
from tools.alerting_tools import send_sns_notification, send_slack_alert
from config import settings


class CloudTrailMonitoringAgent(Agent):
    """
    Agent that continuously monitors AWS CloudTrail logs for suspicious activity.
    Runs 24/7 and detects unusual API call patterns, policy violations, and security threats.
    """
    
    def __init__(self):
        super().__init__(
            name="CloudTrailMonitoringAgent",
            description="Monitors AWS CloudTrail logs for suspicious activity and policy violations",
            tools=[
                Tool(fetch_cloudtrail_logs),
                Tool(analyze_cloudtrail_insights),
                Tool(parse_cloudtrail_event),
                Tool(send_sns_notification),
                Tool(send_slack_alert)
            ]
        )
        self.last_check_time = None
        self.running = False
        self.suspicious_events = []
        self.event_patterns = {}
    
    async def monitor_continuously(self):
        """Main continuous monitoring loop."""
        self.running = True
        print(f"[{self.name}] Starting continuous monitoring...")
        
        while self.running:
            try:
                await self.check_cloudtrail_events()
                await asyncio.sleep(settings.cloudtrail_check_interval_seconds)
            except Exception as e:
                print(f"[{self.name}] Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def check_cloudtrail_events(self):
        """Check for new CloudTrail events and analyze them."""
        try:
            # Calculate time range (last check to now)
            end_time = datetime.utcnow()
            if self.last_check_time:
                start_time = self.last_check_time
            else:
                # First run: check last hour
                start_time = end_time - timedelta(hours=1)
            
            print(f"[{self.name}] Checking events from {start_time} to {end_time}")
            
            # Fetch events
            events = await self.execute_tool(
                "fetch_cloudtrail_logs",
                start_time=start_time.isoformat() + "Z",
                end_time=end_time.isoformat() + "Z"
            )
            
            if not events:
                print(f"[{self.name}] No new events found")
                self.last_check_time = end_time
                return
            
            print(f"[{self.name}] Found {len(events)} events")
            
            # Analyze each event
            suspicious_count = 0
            for event in events:
                parsed = await self.execute_tool("parse_cloudtrail_event", event=event)
                
                # Check for suspicious patterns
                if await self.is_suspicious(parsed):
                    suspicious_count += 1
                    self.suspicious_events.append(parsed)
                    await self.handle_suspicious_event(parsed)
            
            # Check for unusual patterns using CloudTrail Insights
            insights = await self.execute_tool(
                "analyze_cloudtrail_insights",
                insight_type="ApiCallRateInsight",
                time_range="1h"
            )
            
            if insights.get("anomalies_detected", 0) > 0:
                await self.handle_insight_anomaly(insights)
            
            # Update last check time
            self.last_check_time = end_time
            
            print(f"[{self.name}] Analysis complete. Suspicious events: {suspicious_count}")
            
        except Exception as e:
            print(f"[{self.name}] Error checking CloudTrail events: {e}")
            raise
    
    async def is_suspicious(self, event: Dict) -> bool:
        """Determine if an event is suspicious."""
        # Check for high-risk event names
        high_risk_events = [
            "DeleteBucket",
            "TerminateInstances",
            "DeleteDBInstance",
            "DeleteUser",
            "PutBucketPolicy",
            "AttachRolePolicy",
            "CreateAccessKey",
            "DeleteAccessKey"
        ]
        
        event_name = event.get("event_name", "")
        if event_name in high_risk_events:
            return True
        
        # Check for errors (potential unauthorized access attempts)
        if event.get("error_code") or event.get("error_message"):
            return True
        
        # Check for unusual source IPs (would need IP whitelist in production)
        # Check for unusual user agents
        user_agent = event.get("user_agent", "")
        if "bot" in user_agent.lower() or "scanner" in user_agent.lower():
            return True
        
        # Check for read-only violations
        if not event.get("read_only", True) and event.get("management_event", True):
            # Non-read operations are potentially suspicious
            # This is a simplified check - in production, you'd have more sophisticated rules
            pass
        
        return False
    
    async def handle_suspicious_event(self, event: Dict):
        """Handle a detected suspicious event."""
        try:
            event_name = event.get("event_name", "Unknown")
            user_identity = event.get("user_identity", {})
            source_ip = event.get("source_ip", "Unknown")
            event_time = event.get("event_time", "Unknown")
            
            message = f"""
Suspicious CloudTrail Event Detected

Event: {event_name}
Time: {event_time}
User: {user_identity.get('arn', 'Unknown')}
Source IP: {source_ip}
Region: {event.get('aws_region', 'Unknown')}

Please review this event immediately.
"""
            
            # Send alerts
            await self.execute_tool(
                "send_sns_notification",
                subject=f"Suspicious AWS Activity: {event_name}",
                message=message
            )
            
            await self.execute_tool(
                "send_slack_alert",
                message=message,
                severity="warning"
            )
            
            print(f"[{self.name}] Alert sent for suspicious event: {event_name}")
            
        except Exception as e:
            print(f"[{self.name}] Error handling suspicious event: {e}")
    
    async def handle_insight_anomaly(self, insights: Dict):
        """Handle CloudTrail Insights anomaly detection."""
        try:
            message = f"""
CloudTrail Insights detected unusual API activity patterns.

Insight Type: {insights.get('insight_type')}
Time Range: {insights.get('time_range')}
Anomalies Detected: {insights.get('anomalies_detected', 0)}

Please review the CloudTrail logs for this period.
"""
            
            await self.execute_tool(
                "send_sns_notification",
                subject="CloudTrail Insights: Unusual Activity Detected",
                message=message
            )
            
            await self.execute_tool(
                "send_slack_alert",
                message=message,
                severity="warning"
            )
            
        except Exception as e:
            print(f"[{self.name}] Error handling insight anomaly: {e}")
    
    def stop(self):
        """Stop the continuous monitoring."""
        self.running = False
        print(f"[{self.name}] Stopping monitoring...")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "name": self.name,
            "running": self.running,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "suspicious_events_count": len(self.suspicious_events),
            "check_interval_seconds": settings.cloudtrail_check_interval_seconds
        }
