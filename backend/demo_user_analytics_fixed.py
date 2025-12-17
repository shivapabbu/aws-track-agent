"""Demo script to show User Analytics Agent with properly formatted sample data."""
import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load strands_agents stub
try:
    import strands_agents
except ImportError:
    import strands_agents_stub
    sys.modules['strands_agents'] = strands_agents_stub

from agents.user_analytics_agent import UserAnalyticsAgent
from tools.user_analytics_tools import (
    aggregate_usage_by_user,
    attribute_costs_to_users,
    get_user_usage_summary
)


def generate_realistic_events_for_users(user_count=50, events_per_user=20):
    """Generate realistic CloudTrail events with proper user structure."""
    events = []
    users = [f"user{i}@example.com" for i in range(1, user_count + 1)]
    
    event_types = [
        {"name": "RunInstances", "read_only": False},
        {"name": "TerminateInstances", "read_only": False},
        {"name": "CreateBucket", "read_only": False},
        {"name": "PutObject", "read_only": False},
        {"name": "DescribeInstances", "read_only": True},
        {"name": "ListBuckets", "read_only": True},
    ]
    
    base_time = datetime.utcnow()
    
    for user_name in users:
        for i in range(events_per_user):
            event_type = random.choice(event_types)
            event_time = base_time - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            event = {
                "event_id": f"event-{user_name}-{i}",
                "event_time": event_time.isoformat() + "Z",
                "event_name": event_type["name"],
                "event_source": "ec2.amazonaws.com" if "Instance" in event_type["name"] else "s3.amazonaws.com",
                "aws_region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "source_ip": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "aws-cli/2.0.0",
                "user_identity": {
                    "type": "IAMUser",
                    "principal_id": f"AIDA{random.randint(1000000000, 9999999999)}",
                    "arn": f"arn:aws:iam::123456789012:user/{user_name}",
                    "account_id": "123456789012",
                    "userName": user_name
                },
                "resources": [],
                "request_parameters": {},
                "response_elements": {},
                "read_only": event_type["read_only"],
                "management_event": True
            }
            events.append(event)
    
    return events


def generate_cost_data_for_attribution():
    """Generate cost data for attribution."""
    cost_data = []
    services = ["EC2", "S3", "RDS", "Lambda"]
    regions = ["us-east-1", "us-west-2"]
    
    for i in range(30):
        for service in services:
            for region in regions:
                cost_data.append({
                    "Date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "Service": service,
                    "Region": region,
                    "Amount": str(random.uniform(50, 500))
                })
    
    return cost_data


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_user_table(users, columns=None):
    """Print users in a formatted table."""
    if not users:
        print("  No users found.")
        return
    
    if columns is None:
        columns = ["user_name", "total_events", "activity_score"]
    
    # Print header
    header_parts = []
    for col in columns:
        if col == "user_name":
            header_parts.append("User Name".ljust(30))
        elif col == "total_events":
            header_parts.append("Total Events".rjust(15))
        elif col == "activity_score":
            header_parts.append("Activity Score".rjust(15))
        elif col == "total_cost":
            header_parts.append("Total Cost".rjust(15))
        elif col == "write_events":
            header_parts.append("Write Events".rjust(15))
        elif col == "high_risk_events":
            header_parts.append("High Risk".rjust(15))
        elif col == "resource_count":
            header_parts.append("Resources".rjust(15))
        else:
            header_parts.append(col.replace("_", " ").title().ljust(15))
    
    header = " | ".join(header_parts)
    print(f"\n  {header}")
    print("  " + "-" * len(header))
    
    # Print rows
    for user in users[:15]:  # Limit to top 15
        row = []
        for col in columns:
            value = user.get(col, "N/A")
            if isinstance(value, float):
                if "cost" in col.lower():
                    value = f"${value:,.2f}"
                else:
                    value = f"{value:.1f}"
            elif isinstance(value, int):
                value = f"{value:,}"
            elif isinstance(value, str) and len(value) > 25:
                value = value[:22] + "..."
            
            if col == "user_name":
                row.append(str(value).ljust(30))
            else:
                row.append(str(value).rjust(15))
        
        print(f"  {' | '.join(row)}")


async def demo_user_analytics():
    """Demonstrate User Analytics Agent with sample data."""
    
    print_section("AWS Track Agent - User Analytics Demo")
    print("\nThis demo shows person-level tracking for hundreds of users:")
    print("  • Who is using AWS")
    print("  • Who is using it much, who is not")
    print("  • What cost each person is influencing")
    
    # Initialize agent
    print_section("1. Initializing User Analytics Agent")
    agent = UserAnalyticsAgent()
    print(f"  ✅ Agent initialized: {agent.name}")
    print(f"  📝 Description: {agent.description}")
    
    # Generate sample data
    print_section("2. Generating Sample Data")
    print("  Generating CloudTrail events for 50 users...")
    events = generate_realistic_events_for_users(user_count=50, events_per_user=random.randint(10, 30))
    print(f"  ✅ Generated {len(events)} CloudTrail events from 50 users")
    
    print("  Generating cost data for attribution...")
    cost_data = generate_cost_data_for_attribution()
    print(f"  ✅ Generated {len(cost_data)} cost entries")
    
    # Process events for user analytics
    print_section("3. Processing Events for User Analytics")
    print("  Analyzing events to extract person-level metrics...")
    
    usage_metrics = await agent.process_events_for_analytics(events)
    
    print(f"  ✅ Analyzed {len(usage_metrics)} unique users")
    
    if usage_metrics:
        sample_user = list(usage_metrics.keys())[0]
        sample_metrics = usage_metrics[sample_user]
        print(f"\n  📊 Example metrics for {sample_user}:")
        print(f"     - Total Events: {sample_metrics.get('total_events', 0):,}")
        print(f"     - Read Events: {sample_metrics.get('read_events', 0):,}")
        print(f"     - Write Events: {sample_metrics.get('write_events', 0):,}")
        print(f"     - Activity Score: {sample_metrics.get('activity_score', 0):.1f}")
        print(f"     - Services Used: {', '.join(sample_metrics.get('services_used', [])[:3])}")
    
    # Process costs for attribution
    print_section("4. Attributing Costs to Users")
    print("  Attributing AWS costs to individual users...")
    
    cost_attribution = await agent.process_costs_for_attribution(cost_data, events)
    
    print(f"  ✅ Attributed costs to {len(cost_attribution)} users")
    
    if cost_attribution:
        sample_user = list(cost_attribution.keys())[0]
        sample_costs = cost_attribution[sample_user]
        print(f"\n  💰 Example cost attribution for {sample_user}:")
        print(f"     - Total Cost: ${sample_costs.get('total_cost', 0):,.2f}")
        print(f"     - Resources: {sample_costs.get('resource_count', 0)}")
        print(f"     - Cost per Resource: ${sample_costs.get('cost_per_resource', 0):.2f}")
    
    # Show top users by usage
    print_section("5. Top 15 Users by Activity/Usage")
    top_users_usage = agent.get_top_users_by_usage(limit=15)
    print_user_table(top_users_usage, ["user_name", "total_events", "write_events", "high_risk_events", "activity_score"])
    
    if top_users_usage:
        top_user = top_users_usage[0]
        print(f"\n  🏆 Most Active User: {top_user['user_name']}")
        print(f"     - Total Events: {top_user['total_events']:,}")
        print(f"     - Write Events: {top_user['write_events']:,}")
        print(f"     - Activity Score: {top_user['activity_score']:.1f}")
        print(f"     - Services Used: {', '.join(top_user.get('services_used', [])[:5])}")
    
    # Show top users by cost
    print_section("6. Top 15 Users by Cost")
    top_users_cost = agent.get_top_users_by_cost(limit=15)
    if top_users_cost:
        print_user_table(top_users_cost, ["user_name", "total_cost", "resource_count", "cost_per_resource"])
        
        top_cost_user = top_users_cost[0]
        print(f"\n  💸 Highest Cost User: {top_cost_user['user_name']}")
        print(f"     - Total Cost: ${top_cost_user['total_cost']:,.2f}")
        print(f"     - Resources: {top_cost_user['resource_count']}")
        print(f"     - Cost per Resource: ${top_cost_user['cost_per_resource']:.2f}")
        
        if top_cost_user.get('service_costs'):
            print(f"     - Top Service Costs:")
            for service, cost in list(top_cost_user['service_costs'].items())[:3]:
                print(f"       • {service}: ${cost:,.2f}")
    else:
        print("  ⚠️  Cost attribution in progress...")
    
    # Show inactive users
    print_section("7. Inactive Users (Not Used in 30+ Days)")
    inactive_users = agent.get_inactive_users(days_threshold=30)
    if inactive_users:
        print(f"  Found {len(inactive_users)} inactive users:")
        for user in inactive_users[:10]:
            print(f"     - {user['user_name']}: {user['days_inactive']} days inactive")
    else:
        print("  ✅ All users have been active in the last 30 days")
    
    # Show detailed user example
    print_section("8. Detailed User Example")
    if usage_metrics:
        sample_user = list(usage_metrics.keys())[0]
        user_details = agent.user_summaries.get(sample_user, {})
        user_metrics = usage_metrics.get(sample_user, {})
        user_costs = cost_attribution.get(sample_user, {})
        
        print(f"\n  👤 User: {sample_user}")
        print(f"\n  📊 Usage Metrics:")
        print(f"     - Total Events: {user_metrics.get('total_events', 0):,}")
        print(f"     - Read Events: {user_metrics.get('read_events', 0):,}")
        print(f"     - Write Events: {user_metrics.get('write_events', 0):,}")
        print(f"     - High-Risk Events: {user_metrics.get('high_risk_events', 0)}")
        print(f"     - Activity Score: {user_metrics.get('activity_score', 0):.1f}")
        print(f"     - Services Used: {', '.join(user_metrics.get('services_used', [])[:5])}")
        print(f"     - Regions Used: {', '.join(user_metrics.get('regions_used', []))}")
        print(f"     - First Seen: {user_metrics.get('first_seen', 'N/A')}")
        print(f"     - Last Seen: {user_metrics.get('last_seen', 'N/A')}")
        
        if user_costs:
            print(f"\n  💰 Cost Attribution:")
            print(f"     - Total Cost: ${user_costs.get('total_cost', 0):,.2f}")
            print(f"     - Resources: {user_costs.get('resource_count', 0)}")
            print(f"     - Cost per Resource: ${user_costs.get('cost_per_resource', 0):.2f}")
            if user_costs.get('service_costs'):
                print(f"     - Service Costs:")
                for service, cost in list(user_costs['service_costs'].items())[:5]:
                    print(f"       • {service}: ${cost:,.2f}")
        
        if user_details:
            print(f"\n  📈 Usage Category: {user_details.get('usage_category', 'N/A').upper()}")
    
    # Summary statistics
    print_section("9. Summary Statistics")
    total_users = len(usage_metrics)
    total_events = sum(m.get('total_events', 0) for m in usage_metrics.values())
    total_cost = sum(c.get('total_cost', 0) for c in cost_attribution.values())
    
    # Categorize users
    usage_categories = {"inactive": 0, "light": 0, "moderate": 0, "heavy": 0, "very_heavy": 0}
    for user_name, summary in agent.user_summaries.items():
        category = summary.get('usage_category', 'inactive')
        usage_categories[category] = usage_categories.get(category, 0) + 1
    
    print(f"\n  📊 Overall Statistics:")
    print(f"     - Total Users Tracked: {total_users}")
    print(f"     - Total Events: {total_events:,}")
    print(f"     - Total Cost Attributed: ${total_cost:,.2f}")
    if total_users > 0:
        print(f"     - Average Events per User: {total_events // total_users:,}")
        print(f"     - Average Cost per User: ${total_cost / total_users:,.2f}")
    
    print(f"\n  👥 Usage Distribution:")
    for category, count in usage_categories.items():
        if count > 0:
            percentage = (count / total_users) * 100 if total_users > 0 else 0
            print(f"     - {category.title()}: {count} users ({percentage:.1f}%)")
    
    # Show what this means for hundreds of users
    print_section("10. Scaling to Hundreds of Users")
    print("\n  ✅ The system is designed to handle hundreds of users:")
    print(f"     - Currently tracking: {total_users} users")
    print(f"     - Can scale to: 1000+ users")
    print(f"     - Each user tracked individually with:")
    print(f"       • Usage metrics (events, services, regions)")
    print(f"       • Cost attribution (total, by service, by region)")
    print(f"       • Activity scoring and categorization")
    print(f"       • Inactive user detection")
    
    print("\n  📈 Key Insights You Can Get:")
    if top_users_usage:
        print(f"     • Who is your most active user? → {top_users_usage[0]['user_name']}")
    if top_users_cost:
        print(f"     • Who is costing the most? → {top_users_cost[0]['user_name']}")
    print(f"     • How many inactive users? → {len(inactive_users)}")
    if total_users > 0:
        print(f"     • Average cost per user? → ${total_cost/total_users:,.2f}")
    
    print_section("Demo Complete!")
    print("\n  ✅ User Analytics Agent successfully tracks:")
    print("     • Person-level usage metrics")
    print("     • Cost attribution per person")
    print("     • Activity levels and categorization")
    print("     • Inactive user detection")
    print("\n  🚀 Ready to track hundreds of users in production!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("  Starting User Analytics Demo...")
    print("=" * 80)
    
    try:
        asyncio.run(demo_user_analytics())
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n  ❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
