"""Alerting and notification tools."""
from datetime import datetime
from typing import List, Dict, Optional
import boto3
from botocore.exceptions import ClientError
import aiohttp
import json
from strands_agents import tool
from config import settings


@tool
def send_sns_notification(
    subject: str,
    message: str,
    topic_arn: Optional[str] = None,
    attributes: Optional[Dict] = None
) -> str:
    """
    Sends alert notification via AWS SNS.
    
    Args:
        subject: Notification subject
        message: Notification message
        topic_arn: SNS topic ARN (uses default from config if not provided)
        attributes: Optional message attributes
    
    Returns:
        Message ID
    """
    try:
        sns_client = boto3.client('sns', region_name=settings.aws_region)
        topic = topic_arn or settings.sns_topic_arn
        
        if not topic:
            return "No SNS topic configured"
        
        publish_kwargs = {
            'TopicArn': topic,
            'Subject': subject,
            'Message': message
        }
        
        if attributes:
            publish_kwargs['MessageAttributes'] = attributes
        
        response = sns_client.publish(**publish_kwargs)
        return response.get('MessageId', '')
    
    except ClientError as e:
        print(f"AWS Error sending SNS notification: {e}")
        return ""
    except Exception as e:
        print(f"Error sending SNS notification: {e}")
        return ""


@tool
async def send_slack_alert(
    message: str,
    channel: str = "#alerts",
    severity: str = "info",
    webhook_url: Optional[str] = None
) -> bool:
    """
    Sends alert to Slack channel.
    
    Args:
        message: Alert message
        channel: Slack channel name
        severity: Severity level (info, warning, error, critical)
        webhook_url: Slack webhook URL (uses default from config if not provided)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        webhook = webhook_url or settings.slack_webhook_url
        
        if not webhook:
            print("No Slack webhook URL configured")
            return False
        
        # Color coding based on severity
        color_map = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff0000",
            "critical": "#8b0000"
        }
        
        payload = {
            "channel": channel,
            "username": "AWS Track Agent",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color_map.get(severity, "#36a64f"),
                    "title": f"AWS Monitoring Alert - {severity.upper()}",
                    "text": message,
                    "footer": "AWS Track Agent",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook, json=payload) as response:
                return response.status == 200
    
    except Exception as e:
        print(f"Error sending Slack alert: {e}")
        return False


@tool
def send_email_alert(
    recipients: List[str],
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None
) -> bool:
    """
    Sends email alert via AWS SES.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
        attachments: Optional list of file paths to attach
    
    Returns:
        True if successful, False otherwise
    """
    try:
        ses_client = boto3.client('ses', region_name=settings.aws_region)
        
        response = ses_client.send_email(
            Source=settings.email_from,
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body, 'Charset': 'UTF-8'},
                    'Html': {'Data': body.replace('\n', '<br>'), 'Charset': 'UTF-8'}
                }
            }
        )
        
        return response.get('MessageId') is not None
    
    except ClientError as e:
        print(f"AWS Error sending email: {e}")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
