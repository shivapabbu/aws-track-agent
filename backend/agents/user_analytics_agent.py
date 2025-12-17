"""User Analytics Agent for person-level tracking and cost attribution."""
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
from strands_agents import Agent, Tool
from tools.user_analytics_tools import (
    aggregate_usage_by_user,
    attribute_costs_to_users,
    get_user_usage_summary
)
from config import settings


class UserAnalyticsAgent(Agent):
    """
    Agent that tracks individual user/person usage and cost attribution.
    Provides person-level insights: who is using AWS, how much, and what they cost.
    """
    
    def __init__(self):
        super().__init__(
            name="UserAnalyticsAgent",
            description="Tracks individual user usage and cost attribution at person level",
            tools=[
                Tool(aggregate_usage_by_user),
                Tool(attribute_costs_to_users),
                Tool(get_user_usage_summary)
            ]
        )
        self.last_analysis_time = None
        self.running = False
        self.user_metrics = {}  # user_name -> metrics
        self.user_costs = {}  # user_name -> cost data
        self.user_summaries = {}  # user_name -> summary
    
    async def analyze_continuously(self):
        """Main continuous analysis loop."""
        self.running = True
        print(f"[{self.name}] Starting continuous user analytics...")
        
        while self.running:
            try:
                await self.analyze_user_activity()
                await asyncio.sleep(settings.monitoring_interval_seconds)
            except Exception as e:
                print(f"[{self.name}] Error in analysis loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def analyze_user_activity(self):
        """Analyze user activity from CloudTrail events."""
        try:
            # Get events from CloudTrail agent
            # In a real implementation, this would fetch from the CloudTrail agent
            # For now, we'll use the events stored in the agent
            
            print(f"[{self.name}] Analyzing user activity...")
            
            # This would typically get events from CloudTrail agent
            # For now, we'll process any events we have access to
            # In production, you'd integrate with the CloudTrail agent's data
            
            end_time = datetime.utcnow()
            if self.last_analysis_time:
                start_time = self.last_analysis_time
            else:
                start_time = end_time - timedelta(days=30)
            
            # Note: In production, fetch events from CloudTrail agent or database
            # For now, this is a placeholder that shows the structure
            
            self.last_analysis_time = end_time
            print(f"[{self.name}] User analysis complete")
            
        except Exception as e:
            print(f"[{self.name}] Error analyzing user activity: {e}")
            raise
    
    async def process_events_for_analytics(self, events: List[Dict]):
        """Process CloudTrail events to generate user analytics."""
        try:
            print(f"[{self.name}] Processing {len(events)} events for user analytics...")
            
            # Aggregate usage by user
            usage_metrics = await self.execute_tool(
                "aggregate_usage_by_user",
                events=events
            )
            
            self.user_metrics = usage_metrics
            
            print(f"[{self.name}] Analyzed {len(usage_metrics)} users")
            
            # Generate summaries for each user
            for user_name in usage_metrics.keys():
                summary = await self.execute_tool(
                    "get_user_usage_summary",
                    user_name=user_name,
                    events=events,
                    days=30
                )
                self.user_summaries[user_name] = summary
            
            return usage_metrics
            
        except Exception as e:
            print(f"[{self.name}] Error processing events: {e}")
            raise
    
    async def process_costs_for_attribution(self, cost_data: List[Dict], events: List[Dict]):
        """Process cost data to attribute costs to users."""
        try:
            print(f"[{self.name}] Attributing costs to users...")
            
            # Attribute costs to users
            cost_attribution = await self.execute_tool(
                "attribute_costs_to_users",
                cost_data=cost_data,
                events=events
            )
            
            self.user_costs = cost_attribution
            
            print(f"[{self.name}] Attributed costs to {len(cost_attribution)} users")
            
            return cost_attribution
            
        except Exception as e:
            print(f"[{self.name}] Error attributing costs: {e}")
            raise
    
    def get_top_users_by_usage(self, limit: int = 10) -> List[Dict]:
        """Get top users by activity/usage."""
        if not self.user_metrics:
            return []
        
        sorted_users = sorted(
            self.user_metrics.items(),
            key=lambda x: x[1].get("activity_score", 0),
            reverse=True
        )
        
        return [
            {
                "user_name": user_name,
                **metrics
            }
            for user_name, metrics in sorted_users[:limit]
        ]
    
    def get_top_users_by_cost(self, limit: int = 10) -> List[Dict]:
        """Get top users by cost."""
        if not self.user_costs:
            return []
        
        sorted_users = sorted(
            self.user_costs.items(),
            key=lambda x: x[1].get("total_cost", 0),
            reverse=True
        )
        
        return [
            {
                "user_name": user_name,
                **costs
            }
            for user_name, costs in sorted_users[:limit]
        ]
    
    def get_inactive_users(self, days_threshold: int = 30) -> List[Dict]:
        """Get users who haven't been active recently."""
        inactive = []
        
        for user_name, metrics in self.user_metrics.items():
            last_seen_str = metrics.get("last_seen")
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
                    days_inactive = (datetime.now(last_seen.tzinfo) - last_seen).days
                    
                    if days_inactive >= days_threshold:
                        inactive.append({
                            "user_name": user_name,
                            "days_inactive": days_inactive,
                            **metrics
                        })
                except:
                    pass
        
        return sorted(inactive, key=lambda x: x.get("days_inactive", 0), reverse=True)
    
    def stop(self):
        """Stop the continuous analysis."""
        self.running = False
        print(f"[{self.name}] Stopping user analytics...")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "name": self.name,
            "running": self.running,
            "last_analysis_time": self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            "users_tracked": len(self.user_metrics),
            "users_with_costs": len(self.user_costs),
            "analysis_interval_seconds": settings.monitoring_interval_seconds
        }
