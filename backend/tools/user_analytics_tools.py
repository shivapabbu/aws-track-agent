"""User analytics tools for person-level tracking and cost attribution."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
from strands_agents import tool
from config import settings


@tool
def aggregate_usage_by_user(
    events: List[Dict],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Dict]:
    """
    Aggregate AWS usage metrics by individual user/person.
    
    Args:
        events: List of CloudTrail events
        start_date: Start date for analysis
        end_date: End date for analysis
    
    Returns:
        Dictionary mapping user identifiers to usage metrics
    """
    user_metrics = defaultdict(lambda: {
        "user_name": "",
        "user_arn": "",
        "total_events": 0,
        "read_events": 0,
        "write_events": 0,
        "high_risk_events": 0,
        "services_used": set(),
        "regions_used": set(),
        "first_seen": None,
        "last_seen": None,
        "event_types": defaultdict(int),
        "error_count": 0,
        "activity_score": 0
    })
    
    high_risk_events = [
        "DeleteBucket", "TerminateInstances", "DeleteDBInstance",
        "DeleteUser", "PutBucketPolicy", "AttachRolePolicy"
    ]
    
    for event in events:
        user_identity = event.get("user_identity", {})
        user_name = user_identity.get("userName") or user_identity.get("arn", "Unknown")
        user_arn = user_identity.get("arn", "")
        
        if not user_name or user_name == "Unknown":
            continue
        
        metrics = user_metrics[user_name]
        metrics["user_name"] = user_name
        metrics["user_arn"] = user_arn
        metrics["total_events"] += 1
        
        # Track read vs write
        if event.get("read_only", True):
            metrics["read_events"] += 1
        else:
            metrics["write_events"] += 1
        
        # Track high-risk events
        event_name = event.get("event_name", "")
        if event_name in high_risk_events:
            metrics["high_risk_events"] += 1
        
        # Track services and regions
        event_source = event.get("event_source", "")
        if event_source:
            service = event_source.split(".")[0] if "." in event_source else event_source
            metrics["services_used"].add(service)
        
        region = event.get("aws_region", "")
        if region:
            metrics["regions_used"].add(region)
        
        # Track event types
        metrics["event_types"][event_name] += 1
        
        # Track errors
        if event.get("error_code") or event.get("error_message"):
            metrics["error_count"] += 1
        
        # Track timestamps
        event_time_str = event.get("event_time")
        if event_time_str:
            try:
                event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                if not metrics["first_seen"] or event_time < metrics["first_seen"]:
                    metrics["first_seen"] = event_time
                if not metrics["last_seen"] or event_time > metrics["last_seen"]:
                    metrics["last_seen"] = event_time
            except:
                pass
    
    # Calculate activity score and convert sets to lists
    result = {}
    for user_name, metrics in user_metrics.items():
        # Convert sets to lists for JSON serialization
        metrics["services_used"] = list(metrics["services_used"])
        metrics["regions_used"] = list(metrics["regions_used"])
        metrics["event_types"] = dict(metrics["event_types"])
        
        # Calculate activity score (weighted by event types and recency)
        activity_score = (
            metrics["total_events"] * 1.0 +
            metrics["write_events"] * 2.0 +
            metrics["high_risk_events"] * 5.0 -
            metrics["error_count"] * 0.5
        )
        
        # Add recency bonus (more recent activity = higher score)
        if metrics["last_seen"]:
            days_since_last = (datetime.now(metrics["last_seen"].tzinfo) - metrics["last_seen"]).days
            recency_bonus = max(0, 10 - days_since_last)
            activity_score += recency_bonus
        
        metrics["activity_score"] = round(activity_score, 2)
        
        # Convert datetime to string
        if metrics["first_seen"]:
            metrics["first_seen"] = metrics["first_seen"].isoformat()
        if metrics["last_seen"]:
            metrics["last_seen"] = metrics["last_seen"].isoformat()
        
        result[user_name] = metrics
    
    return result


@tool
def attribute_costs_to_users(
    cost_data: List[Dict],
    events: List[Dict],
    time_period: str = "daily"
) -> Dict[str, Dict]:
    """
    Attribute AWS costs to individual users based on their resource usage.
    
    Args:
        cost_data: Cost and usage data from AWS Cost Explorer
        events: CloudTrail events to correlate with costs
        time_period: Time period for cost attribution (daily, weekly, monthly)
    
    Returns:
        Dictionary mapping users to their attributed costs
    """
    user_costs = defaultdict(lambda: {
        "user_name": "",
        "total_cost": 0.0,
        "service_costs": defaultdict(float),
        "region_costs": defaultdict(float),
        "cost_by_date": defaultdict(float),
        "resource_count": 0,
        "cost_per_resource": 0.0
    })
    
    # First, aggregate resource usage by user from events
    user_resources = defaultdict(set)
    for event in events:
        user_identity = event.get("user_identity", {})
        user_name = user_identity.get("userName") or user_identity.get("arn", "Unknown")
        
        if not user_name or user_name == "Unknown":
            continue
        
        # Extract resource ARNs from event
        resources = event.get("resources", [])
        for resource in resources:
            resource_arn = resource.get("resourceName") or resource.get("resourceARN", "")
            if resource_arn:
                user_resources[user_name].add(resource_arn)
        
        # Also check response elements for created resources
        response_elements = event.get("response_elements", {})
        if "instancesSet" in response_elements:
            for instance in response_elements.get("instancesSet", {}).get("items", []):
                instance_id = instance.get("instanceId", "")
                if instance_id:
                    user_resources[user_name].add(f"ec2:{instance_id}")
    
    # Attribute costs based on resource usage
    for cost_entry in cost_data:
        # This is a simplified attribution - in production, you'd use
        # cost allocation tags, resource tags, or more sophisticated matching
        cost_amount = float(cost_entry.get("Amount", 0))
        service = cost_entry.get("Service", "Unknown")
        region = cost_entry.get("Region", "Unknown")
        date = cost_entry.get("Date", "")
        
        # Distribute cost proportionally based on resource usage
        # In production, this would be more sophisticated
        total_resources = sum(len(resources) for resources in user_resources.values())
        
        if total_resources > 0:
            for user_name, resources in user_resources.items():
                if len(resources) > 0:
                    proportion = len(resources) / total_resources
                    user_cost = cost_amount * proportion
                    
                    user_costs[user_name]["user_name"] = user_name
                    user_costs[user_name]["total_cost"] += user_cost
                    user_costs[user_name]["service_costs"][service] += user_cost
                    user_costs[user_name]["region_costs"][region] += user_cost
                    if date:
                        user_costs[user_name]["cost_by_date"][date] += user_cost
                    user_costs[user_name]["resource_count"] = len(resources)
    
    # Calculate cost per resource
    result = {}
    for user_name, costs in user_costs.items():
        costs["service_costs"] = dict(costs["service_costs"])
        costs["region_costs"] = dict(costs["region_costs"])
        costs["cost_by_date"] = dict(costs["cost_by_date"])
        
        if costs["resource_count"] > 0:
            costs["cost_per_resource"] = costs["total_cost"] / costs["resource_count"]
        else:
            costs["cost_per_resource"] = 0.0
        
        costs["total_cost"] = round(costs["total_cost"], 2)
        costs["cost_per_resource"] = round(costs["cost_per_resource"], 2)
        
        result[user_name] = costs
    
    return result


@tool
def get_user_usage_summary(
    user_name: str,
    events: List[Dict],
    days: int = 30
) -> Dict:
    """
    Get detailed usage summary for a specific user.
    
    Args:
        user_name: Name or ARN of the user
        events: List of CloudTrail events
        days: Number of days to analyze
    
    Returns:
        Detailed usage summary for the user
    """
    user_events = [
        e for e in events
        if (e.get("user_identity", {}).get("userName") == user_name or
            e.get("user_identity", {}).get("arn") == user_name)
    ]
    
    if not user_events:
        return {
            "user_name": user_name,
            "status": "no_activity",
            "message": f"No activity found for user {user_name}"
        }
    
    # Calculate metrics
    total_events = len(user_events)
    read_events = sum(1 for e in user_events if e.get("read_only", True))
    write_events = total_events - read_events
    
    # Get unique services
    services = set()
    for event in user_events:
        event_source = event.get("event_source", "")
        if event_source:
            service = event_source.split(".")[0] if "." in event_source else event_source
            services.add(service)
    
    # Get activity timeline
    timeline = defaultdict(int)
    for event in user_events:
        event_time_str = event.get("event_time", "")
        if event_time_str:
            try:
                event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                date_key = event_time.date().isoformat()
                timeline[date_key] += 1
            except:
                pass
    
    # Calculate usage category
    if total_events == 0:
        usage_category = "inactive"
    elif total_events < 10:
        usage_category = "light"
    elif total_events < 100:
        usage_category = "moderate"
    elif total_events < 500:
        usage_category = "heavy"
    else:
        usage_category = "very_heavy"
    
    return {
        "user_name": user_name,
        "status": "active",
        "total_events": total_events,
        "read_events": read_events,
        "write_events": write_events,
        "services_used": list(services),
        "usage_category": usage_category,
        "activity_timeline": dict(timeline),
        "last_activity": max(
            (e.get("event_time", "") for e in user_events),
            default=""
        )
    }
