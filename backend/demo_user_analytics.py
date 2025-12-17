"""Demo script to show User Analytics Agent with sample data."""
import sys
import os
import asyncio
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load strands_agents stub
try:
    import strands_agents
except ImportError:
    import strands_agents_stub
    sys.modules['strands_agents'] = strands_agents_stub

from utils.sample_data import (
    generate_sample_cloudtrail_events,
    generate_sample_cost_anomalies,
    generate_sample_user_analytics,
    generate_sample_user_costs
)
from agents.user_analytics_agent import UserAnalyticsAgent
from tools.user_analytics_tools import (
    aggregate_usage_by_user,
    attribute_costs_to_users,
    get_user_usage_summary
)


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
        columns = ["user_name", "total_events", "activity_score", "total_cost"]
    
    # Print header
    header = " | ".join([col.replace("_", " ").title().ljust(20) for col in columns])
    print(f"\n  {header}")
    print("  " + "-" * len(header))
    
    # Print rows
    for user in users[:10]:  # Limit to top 10
        row = []
        for col in columns:
            value = user.get(col, "N/A")
            if isinstance(value, float):
                value = f"${value:,.2f}" if "cost" in col else f"{value:.1f}"
            elif isinstance(value, int):
                value = f"{value:,}"
            row.append(str(value).ljust(20))
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
    print("  Generating CloudTrail events for 100 users...")
    events = generate_sample_cloudtrail_events(count=200)
    print(f"  ✅ Generated {len(events)} CloudTrail events")
    
    print("  Generating cost data...")
    cost_data = []
    for i in range(30):  # 30 days of cost data
        cost_data.append({
            "Date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "Service": "EC2",
            "Region": "us-east-1",
            "Amount": str(1000 + i * 50)
        })
    print(f"  ✅ Generated {len(cost_data)} cost entries")
    
    # Process events for user analytics
    print_section("3. Processing Events for User Analytics")
    print("  Analyzing events to extract person-level metrics...")
    
    usage_metrics = await agent.process_events_for_analytics(events)
    
    print(f"  ✅ Analyzed {len(usage_metrics)} unique users")
    print(f"  📊 Metrics tracked per user:")
    print(f"     - Total events (read/write breakdown)")
    print(f"     - High-risk operations")
    print(f"     - Services and regions used")
    print(f"     - Activity score")
    print(f"     - First/last seen timestamps")
    
    # Process costs for attribution
    print_section("4. Attributing Costs to Users")
    print("  Attributing AWS costs to individual users...")
    
    cost_attribution = await agent.process_costs_for_attribution(cost_data, events)
    
    print(f"  ✅ Attributed costs to {len(cost_attribution)} users")
    print(f"  💰 Cost metrics per user:")
    print(f"     - Total cost")
    print(f"     - Cost by service")
    print(f"     - Cost by region")
    print(f"     - Cost per resource")
    
    # Show top users by usage
    print_section("5. Top 10 Users by Activity/Usage")
    top_users_usage = agent.get_top_users_by_usage(limit=10)
    print_user_table(top_users_usage, ["user_name", "total_events", "write_events", "high_risk_events", "activity_score"])
    
    if top_users_usage:
        top_user = top_users_usage[0]
        print(f"\n  🏆 Most Active User: {top_user['user_name']}")
        print(f"     - Total Events: {top_user['total_events']:,}")
        print(f"     - Activity Score: {top_user['activity_score']:.1f}")
        print(f"     - Services Used: {', '.join(top_user.get('services_used', [])[:5])}")
    
    # Show top users by cost
    print_section("6. Top 10 Users by Cost")
    top_users_cost = agent.get_top_users_by_cost(limit=10)
    if top_users_cost:
        print_user_table(top_users_cost, ["user_name", "total_cost", "resource_count", "cost_per_resource"])
        
        top_cost_user = top_users_cost[0]
        print(f"\n  💸 Highest Cost User: {top_cost_user['user_name']}")
        print(f"     - Total Cost: ${top_cost_user['total_cost']:,.2f}")
        print(f"     - Resources: {top_cost_user['resource_count']}")
        print(f"     - Cost per Resource: ${top_cost_user['cost_per_resource']:.2f}")
    else:
        print("  ⚠️  No cost data available yet. Cost attribution requires cost data from AWS.")
    
    # Show inactive users
    print_section("7. Inactive Users (Not Used in 30+ Days)")
    inactive_users = agent.get_inactive_users(days_threshold=30)
    if inactive_users:
        print(f"  Found {len(inactive_users)} inactive users:")
        for user in inactive_users[:5]:
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
        print(f"     - Last Seen: {user_metrics.get('last_seen', 'N/A')}")
        
        if user_costs:
            print(f"\n  💰 Cost Attribution:")
            print(f"     - Total Cost: ${user_costs.get('total_cost', 0):,.2f}")
            print(f"     - Resources: {user_costs.get('resource_count', 0)}")
            print(f"     - Cost per Resource: ${user_costs.get('cost_per_resource', 0):.2f}")
            if user_costs.get('service_costs'):
                print(f"     - Top Service Costs:")
                for service, cost in list(user_costs['service_costs'].items())[:3]:
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
    print(f"\n  👥 Usage Distribution:")
    for category, count in usage_categories.items():
        if count > 0:
            percentage = (count / total_users) * 100
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
    print(f"     • Who is your most active user? → {top_users_usage[0]['user_name'] if top_users_usage else 'N/A'}")
    print(f"     • Who is costing the most? → {top_users_cost[0]['user_name'] if top_users_cost else 'N/A'}")
    print(f"     • How many inactive users? → {len(inactive_users)}")
    print(f"     • Average cost per user? → ${total_cost/total_users:,.2f}" if total_users > 0 else "     • Average cost per user? → N/A")
    
    print_section("Demo Complete!")
    print("\n  ✅ User Analytics Agent successfully tracks:")
    print("     • Person-level usage metrics")
    print("     • Cost attribution per person")
    print("     • Activity levels and categorization")
    print("     • Inactive user detection")
    print("\n  🚀 Ready to track hundreds of users in production!")


if __name__ == "__main__":
    # Import timedelta
    from datetime import timedelta
    
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
