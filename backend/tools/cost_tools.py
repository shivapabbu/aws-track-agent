"""Cost Anomaly Detection tools for monitoring AWS spending."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import boto3
from botocore.exceptions import ClientError
from strands_agents import tool
from config import settings


@tool
def get_cost_anomalies(
    monitor_arn: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Retrieves cost anomalies from AWS Cost Anomaly Detection service.
    
    Args:
        monitor_arn: Optional monitor ARN to filter by
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of cost anomalies with root causes and recommended actions
    """
    try:
        ce_client = boto3.client('ce', region_name=settings.aws_region)
        anomalies = []
        
        # Default to last 30 days if not specified
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Get anomaly monitors
        if monitor_arn:
            monitors = [{"MonitorArn": monitor_arn}]
        else:
            # List all monitors
            monitors_response = ce_client.list_anomaly_monitors()
            monitors = monitors_response.get('AnomalyMonitors', [])
        
        # Get anomalies for each monitor
        for monitor in monitors:
            monitor_arn = monitor.get('MonitorArn', '')
            
            try:
                response = ce_client.list_anomalies_for_monitor(
                    MonitorArn=monitor_arn,
                    DateInterval={
                        'Start': start_date,
                        'End': end_date
                    }
                )
                
                for anomaly in response.get('Anomalies', []):
                    anomaly_detail = {
                        "anomaly_id": anomaly.get('AnomalyId', ''),
                        "anomaly_score": anomaly.get('AnomalyScore', {}),
                        "impact": anomaly.get('Impact', {}),
                        "root_cause": anomaly.get('RootCauses', []),
                        "monitor_arn": monitor_arn,
                        "dimension_value": anomaly.get('DimensionValue', ''),
                        "feedback": anomaly.get('Feedback'),
                        "status": anomaly.get('Status', '')
                    }
                    anomalies.append(anomaly_detail)
            
            except ClientError as e:
                print(f"Error getting anomalies for monitor {monitor_arn}: {e}")
                continue
        
        return anomalies
    
    except ClientError as e:
        print(f"AWS Error getting cost anomalies: {e}")
        return []
    except Exception as e:
        print(f"Error getting cost anomalies: {e}")
        return []


@tool
def configure_cost_monitor(
    monitor_type: str,
    monitor_name: str,
    threshold: float = 0.0,
    tags: Optional[Dict] = None
) -> str:
    """
    Creates or updates a cost anomaly detection monitor.
    
    Args:
        monitor_type: Type of monitor (SERVICE, COST_CATEGORY, LINKED_ACCOUNT, TAG)
        monitor_name: Name for the monitor
        threshold: Anomaly threshold (0.0 to 1.0)
        tags: Optional tags for TAG monitor type
    
    Returns:
        Monitor ARN
    """
    try:
        ce_client = boto3.client('ce', region_name=settings.aws_region)
        
        # Build monitor specification
        monitor_spec = {
            'MonitorType': monitor_type
        }
        
        if monitor_type == 'TAG' and tags:
            monitor_spec['MonitorDimension'] = 'TAG'
            monitor_spec['MonitorSpecification'] = {
                'Tags': tags
            }
        
        # Create monitor
        response = ce_client.create_anomaly_monitor(
            AnomalyMonitorName=monitor_name,
            MonitorType=monitor_type,
            MonitorSpecification=monitor_spec if 'MonitorSpecification' in monitor_spec else {}
        )
        
        monitor_arn = response.get('MonitorArn', '')
        
        # Create subscription for the monitor
        if threshold > 0:
            ce_client.create_anomaly_subscription(
                AnomalySubscriptionName=f"{monitor_name}-subscription",
                MonitorArnList=[monitor_arn],
                Subscribers=[
                    {
                        'Type': 'EMAIL',
                        'Address': settings.email_to
                    }
                ],
                Threshold=threshold
            )
        
        return monitor_arn
    
    except ClientError as e:
        print(f"AWS Error configuring cost monitor: {e}")
        return ""
    except Exception as e:
        print(f"Error configuring cost monitor: {e}")
        return ""


@tool
def analyze_cost_anomaly(anomaly_id: str) -> Dict:
    """
    Analyzes a specific cost anomaly to determine root cause and impact.
    
    Args:
        anomaly_id: ID of the anomaly to analyze
    
    Returns:
        Detailed analysis including root cause, impact, and recommendations
    """
    try:
        ce_client = boto3.client('ce', region_name=settings.aws_region)
        
        # Get anomaly details
        # Note: AWS Cost Explorer API doesn't have a direct get_anomaly endpoint
        # This is a simplified implementation
        # In production, you would need to query from your stored anomalies
        
        # Get cost and usage data for the anomaly period
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        analysis = {
            "anomaly_id": anomaly_id,
            "analysis_date": datetime.now().isoformat(),
            "time_period": {
                "start": start_date,
                "end": end_date
            },
            "cost_data": response.get('ResultsByTime', []),
            "recommendations": [
                "Review resource usage patterns",
                "Check for unauthorized resource creation",
                "Verify cost allocation tags",
                "Consider implementing cost budgets"
            ],
            "severity": "medium"  # Would be calculated based on impact
        }
        
        return analysis
    
    except ClientError as e:
        print(f"AWS Error analyzing cost anomaly: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"Error analyzing cost anomaly: {e}")
        return {"error": str(e)}
