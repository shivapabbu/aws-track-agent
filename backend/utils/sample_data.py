"""Sample data generators for testing AWS Track Agent."""
from datetime import datetime, timedelta
from typing import List, Dict
import random
import uuid


def generate_sample_cloudtrail_events(count: int = 10) -> List[Dict]:
    """Generate sample CloudTrail events for testing."""
    events = []
    
    # Sample event types
    event_types = [
        {"name": "RunInstances", "risk": "medium", "read_only": False},
        {"name": "TerminateInstances", "risk": "high", "read_only": False},
        {"name": "DeleteBucket", "risk": "high", "read_only": False},
        {"name": "CreateUser", "risk": "medium", "read_only": False},
        {"name": "DeleteUser", "risk": "high", "read_only": False},
        {"name": "PutBucketPolicy", "risk": "high", "read_only": False},
        {"name": "AttachRolePolicy", "risk": "high", "read_only": False},
        {"name": "CreateAccessKey", "risk": "medium", "read_only": False},
        {"name": "DescribeInstances", "risk": "low", "read_only": True},
        {"name": "ListBuckets", "risk": "low", "read_only": True},
        {"name": "GetObject", "risk": "low", "read_only": True},
    ]
    
    # Sample users
    users = [
        "admin@example.com",
        "developer@example.com",
        "automation@example.com",
        "unknown-user",
    ]
    
    # Sample source IPs
    source_ips = [
        "203.0.113.1",
        "198.51.100.1",
        "192.0.2.1",
        "10.0.0.1",
        "172.16.0.1",
    ]
    
    base_time = datetime.utcnow()
    
    for i in range(count):
        event_type = random.choice(event_types)
        event_time = base_time - timedelta(minutes=random.randint(0, 60))
        
        # Generate suspicious events (20% chance)
        is_suspicious = random.random() < 0.2
        
        event = {
            "eventID": str(uuid.uuid4()),
            "eventTime": event_time.isoformat() + "Z",
            "eventName": event_type["name"],
            "eventSource": "ec2.amazonaws.com" if "Instance" in event_type["name"] else "s3.amazonaws.com",
            "awsRegion": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
            "sourceIPAddress": random.choice(source_ips),
            "userAgent": random.choice([
                "aws-cli/2.0.0",
                "Mozilla/5.0",
                "bot-scanner",
                "aws-sdk-python/1.20.0"
            ]),
            "userIdentity": {
                "type": "IAMUser",
                "principalId": f"AIDA{random.randint(1000000000, 9999999999)}",
                "arn": f"arn:aws:iam::123456789012:user/{random.choice(users)}",
                "accountId": "123456789012",
                "userName": random.choice(users),
                "accessKeyId": f"AKIA{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))}"
            },
            "resources": [],
            "requestParameters": {
                "instanceType": "t2.micro" if "Instance" in event_type["name"] else None
            },
            "responseElements": {},
            "readOnly": event_type["read_only"],
            "managementEvent": True
        }
        
        # Add suspicious indicators
        if is_suspicious:
            # High-risk event
            if random.random() < 0.5:
                event["eventName"] = random.choice(["TerminateInstances", "DeleteBucket", "DeleteUser"])
            
            # Error (unauthorized attempt)
            if random.random() < 0.3:
                event["errorCode"] = "AccessDenied"
                event["errorMessage"] = "User is not authorized to perform this operation"
            
            # Suspicious user agent
            if random.random() < 0.3:
                event["userAgent"] = "bot-scanner"
            
            # Unusual source IP
            if random.random() < 0.3:
                event["sourceIPAddress"] = "203.0.113.999"  # Invalid IP
        
        events.append(event)
    
    return events


def generate_sample_cost_anomalies(count: int = 5) -> List[Dict]:
    """Generate sample cost anomalies for testing."""
    anomalies = []
    
    # Sample services
    services = [
        "Amazon EC2",
        "Amazon S3",
        "Amazon RDS",
        "AWS Lambda",
        "Amazon CloudFront",
        "Amazon ECS",
        "Amazon EKS",
    ]
    
    # Sample dimensions
    dimensions = [
        "us-east-1",
        "us-west-2",
        "production",
        "development",
        "team-alpha",
        "team-beta",
    ]
    
    base_date = datetime.now()
    
    for i in range(count):
        anomaly_date = base_date - timedelta(days=random.randint(0, 7))
        
        # Generate impact amount (some high, some low)
        if random.random() < 0.3:
            impact_amount = random.uniform(1000, 10000)  # High impact
            severity = "critical"
        elif random.random() < 0.5:
            impact_amount = random.uniform(100, 1000)  # Medium impact
            severity = "warning"
        else:
            impact_amount = random.uniform(10, 100)  # Low impact
            severity = "info"
        
        anomaly = {
            "anomaly_id": f"anomaly-{uuid.uuid4().hex[:8]}",
            "anomaly_score": {
                "MaxScore": random.uniform(0.7, 1.0)
            },
            "impact": {
                "TotalImpact": {
                    "Amount": str(impact_amount),
                    "Unit": "USD"
                },
                "MaxImpact": {
                    "Amount": str(impact_amount * 1.2),
                    "Unit": "USD"
                }
            },
            "root_cause": [
                f"Unusual usage in {random.choice(services)}",
                f"Increased activity in {random.choice(dimensions)}",
                "New resource deployment",
                "Configuration change"
            ][:random.randint(1, 3)],
            "monitor_arn": f"arn:aws:ce::123456789012:anomalymonitor/{uuid.uuid4().hex[:8]}",
            "dimension_value": random.choice(dimensions),
            "feedback": None,
            "status": random.choice(["OPEN", "CLOSED"]),
            "date": anomaly_date.strftime("%Y-%m-%d")
        }
        
        anomalies.append(anomaly)
    
    return anomalies


def generate_sample_dashboard_stats() -> Dict:
    """Generate sample dashboard statistics."""
    return {
        "cloudtrail": {
            "suspicious_events": random.randint(5, 25),
            "running": True,
            "last_check": (datetime.now() - timedelta(minutes=random.randint(1, 5))).isoformat()
        },
        "cost": {
            "anomalies": random.randint(2, 10),
            "running": True,
            "last_check": (datetime.now() - timedelta(hours=random.randint(1, 2))).isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }
