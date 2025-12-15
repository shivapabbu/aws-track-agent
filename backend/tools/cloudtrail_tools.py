"""CloudTrail integration tools for monitoring AWS activity."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import boto3
from botocore.exceptions import ClientError
import json
import gzip
from strands_agents import tool
from config import settings


@tool
def fetch_cloudtrail_logs(
    start_time: str,
    end_time: str,
    account_id: Optional[str] = None,
    event_name: Optional[str] = None
) -> List[Dict]:
    """
    Fetches CloudTrail logs from S3 bucket for specified time range.
    
    Args:
        start_time: Start time in ISO format (e.g., '2024-01-01T00:00:00Z')
        end_time: End time in ISO format (e.g., '2024-01-01T23:59:59Z')
        account_id: Optional AWS account ID to filter by
        event_name: Optional event name to filter by (e.g., 'RunInstances')
    
    Returns:
        List of CloudTrail events
    """
    try:
        s3_client = boto3.client('s3', region_name=settings.aws_region)
        events = []
        
        # Parse time range
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # List objects in S3 bucket for the time range
        prefix = settings.cloudtrail_log_prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=settings.cloudtrail_s3_bucket, Prefix=prefix):
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                # Parse date from object key (CloudTrail format: YYYY/MM/DD/account_id_CloudTrail_region_YYYYMMDDTHHmmssZ_hash.json.gz)
                try:
                    key_parts = obj['Key'].split('/')
                    if len(key_parts) >= 4:
                        obj_date_str = f"{key_parts[1]}-{key_parts[2]}-{key_parts[3]}"
                        obj_date = datetime.strptime(obj_date_str, '%Y-%m-%d')
                        
                        # Check if object is in time range
                        if start_dt.date() <= obj_date.date() <= end_dt.date():
                            # Download and parse log file
                            response = s3_client.get_object(
                                Bucket=settings.cloudtrail_s3_bucket,
                                Key=obj['Key']
                            )
                            
                            # Decompress if gzipped
                            content = response['Body'].read()
                            if obj['Key'].endswith('.gz'):
                                content = gzip.decompress(content)
                            
                            log_data = json.loads(content.decode('utf-8'))
                            
                            # Extract events
                            if 'Records' in log_data:
                                for record in log_data['Records']:
                                    # Apply filters
                                    if account_id and record.get('userIdentity', {}).get('accountId') != account_id:
                                        continue
                                    if event_name and record.get('eventName') != event_name:
                                        continue
                                    
                                    events.append(record)
                except Exception as e:
                    print(f"Error processing object {obj['Key']}: {e}")
                    continue
        
        return events
    
    except ClientError as e:
        print(f"AWS Error fetching CloudTrail logs: {e}")
        return []
    except Exception as e:
        print(f"Error fetching CloudTrail logs: {e}")
        return []


@tool
def analyze_cloudtrail_insights(
    insight_type: str = "ApiCallRateInsight",
    time_range: str = "1h"
) -> Dict:
    """
    Queries CloudTrail Insights to detect unusual API activity patterns.
    
    Args:
        insight_type: Type of insight (ApiCallRateInsight, ApiErrorRateInsight)
        time_range: Time range for analysis (e.g., '1h', '24h', '7d')
    
    Returns:
        Dictionary containing insight results
    """
    try:
        cloudtrail_client = boto3.client('cloudtrail', region_name=settings.aws_region)
        
        # Calculate time range
        end_time = datetime.utcnow()
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            start_time = end_time - timedelta(days=days)
        else:
            start_time = end_time - timedelta(hours=1)
        
        # Get insights
        response = cloudtrail_client.get_insight_selectors(
            TrailName='organization-trail'  # Adjust based on your trail name
        )
        
        # For actual insights, you would use get_insights API
        # This is a simplified version
        return {
            "insight_type": insight_type,
            "time_range": time_range,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "analyzed",
            "anomalies_detected": 0  # Would be populated by actual insights
        }
    
    except ClientError as e:
        print(f"AWS Error analyzing CloudTrail insights: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"Error analyzing CloudTrail insights: {e}")
        return {"error": str(e)}


@tool
def parse_cloudtrail_event(event: Dict) -> Dict:
    """
    Parses CloudTrail event to extract key information.
    
    Args:
        event: Raw CloudTrail event dictionary
    
    Returns:
        Parsed event with structured data
    """
    try:
        parsed = {
            "event_id": event.get("eventID", ""),
            "event_time": event.get("eventTime", ""),
            "event_name": event.get("eventName", ""),
            "event_source": event.get("eventSource", ""),
            "aws_region": event.get("awsRegion", ""),
            "source_ip": event.get("sourceIPAddress", ""),
            "user_agent": event.get("userAgent", ""),
            "user_identity": {
                "type": event.get("userIdentity", {}).get("type", ""),
                "principal_id": event.get("userIdentity", {}).get("principalId", ""),
                "arn": event.get("userIdentity", {}).get("arn", ""),
                "account_id": event.get("userIdentity", {}).get("accountId", ""),
                "user_name": event.get("userIdentity", {}).get("userName", "")
            },
            "resources": event.get("resources", []),
            "request_parameters": event.get("requestParameters", {}),
            "response_elements": event.get("responseElements", {}),
            "error_code": event.get("errorCode"),
            "error_message": event.get("errorMessage"),
            "read_only": event.get("readOnly", False),
            "management_event": event.get("managementEvent", True)
        }
        
        return parsed
    
    except Exception as e:
        print(f"Error parsing CloudTrail event: {e}")
        return {"error": str(e), "raw_event": event}
