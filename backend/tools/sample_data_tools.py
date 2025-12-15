"""Sample data tools for testing (mock AWS tools)."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
from strands_agents import tool
from utils.sample_data import (
    generate_sample_cloudtrail_events,
    generate_sample_cost_anomalies
)


@tool
def fetch_cloudtrail_logs_sample(
    start_time: str,
    end_time: str,
    account_id: Optional[str] = None,
    event_name: Optional[str] = None
) -> List[Dict]:
    """
    Mock version of fetch_cloudtrail_logs that returns sample data.
    Use this for testing when AWS credentials are not available.
    """
    # Generate sample events
    events = generate_sample_cloudtrail_events(count=random.randint(5, 15))
    
    # Apply filters if provided
    if account_id:
        for event in events:
            event["userIdentity"]["accountId"] = account_id
    
    if event_name:
        events = [e for e in events if e.get("eventName") == event_name]
    
    return events


@tool
def get_cost_anomalies_sample(
    monitor_arn: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Mock version of get_cost_anomalies that returns sample data.
    Use this for testing when AWS credentials are not available.
    """
    return generate_sample_cost_anomalies(count=random.randint(3, 8))
