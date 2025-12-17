# User Analytics Requirements - Person-Level Tracking

## Business Requirements

You mentioned you're giving access to **hundreds of people** and need to track:

1. **Who is using AWS** - Person-level identification
2. **Who is using it much, who is not** - Usage metrics per person
3. **What is the cost each one is influencing** - Cost attribution per person

## Implementation Status

### ✅ What Has Been Added

#### 1. User Analytics Agent (`backend/agents/user_analytics_agent.py`)
- **Purpose**: Tracks individual users/persons and their AWS usage
- **Features**:
  - Aggregates usage metrics by user
  - Attributes costs to individual users
  - Identifies active vs inactive users
  - Calculates activity scores per user

#### 2. User Analytics Tools (`backend/tools/user_analytics_tools.py`)

**`aggregate_usage_by_user`**
- Tracks per-person metrics:
  - Total events (read/write breakdown)
  - High-risk events count
  - Services used
  - Regions used
  - Activity timeline
  - Activity score (weighted metric)

**`attribute_costs_to_users`**
- Attributes AWS costs to individual users:
  - Total cost per user
  - Cost by service
  - Cost by region
  - Cost by date
  - Cost per resource

**`get_user_usage_summary`**
- Detailed summary for each person:
  - Usage category (inactive, light, moderate, heavy, very_heavy)
  - Activity timeline
  - Services and regions used
  - Last activity timestamp

#### 3. API Endpoints (`backend/api/main.py`)

**User Analytics Endpoints:**
- `GET /api/users/analytics` - Get all user analytics
- `GET /api/users/top-by-usage` - Top users by activity
- `GET /api/users/top-by-cost` - Top users by cost
- `GET /api/users/inactive` - Inactive users (haven't used in X days)
- `GET /api/users/{user_name}` - Detailed view for specific user
- `POST /api/users/analyze` - Manually trigger user analysis

#### 4. Integration with Existing Agents

- **CloudTrail Agent** → Provides events for user analysis
- **Cost Agent** → Provides cost data for attribution
- **User Analytics Agent** → Processes both to create person-level insights

## How It Works

### Data Flow

```
CloudTrail Events → User Analytics Agent → Person-Level Metrics
Cost Data         → User Analytics Agent → Cost Attribution per Person
```

### Metrics Tracked Per Person

1. **Usage Metrics:**
   - Total events (read/write)
   - High-risk operations
   - Services used
   - Regions used
   - Activity score
   - First/last seen

2. **Cost Metrics:**
   - Total cost attributed
   - Cost by service
   - Cost by region
   - Cost per resource
   - Cost timeline

3. **Usage Categories:**
   - **Inactive**: No activity
   - **Light**: < 10 events
   - **Moderate**: 10-100 events
   - **Heavy**: 100-500 events
   - **Very Heavy**: 500+ events

## Example API Responses

### Get Top Users by Usage
```json
{
  "users": [
    {
      "user_name": "alice@example.com",
      "total_events": 450,
      "activity_score": 485.5,
      "services_used": ["EC2", "S3", "RDS"],
      "write_events": 120,
      "high_risk_events": 5
    }
  ],
  "count": 10
}
```

### Get Top Users by Cost
```json
{
  "users": [
    {
      "user_name": "bob@example.com",
      "total_cost": 4523.50,
      "service_costs": {
        "EC2": 2800.00,
        "S3": 1200.00,
        "RDS": 523.50
      },
      "resource_count": 25,
      "cost_per_resource": 180.94
    }
  ],
  "count": 10
}
```

### Get User Details
```json
{
  "user_name": "alice@example.com",
  "summary": {
    "usage_category": "heavy",
    "total_events": 450,
    "services_used": ["EC2", "S3", "RDS"],
    "last_activity": "2024-01-15T10:30:00Z"
  },
  "metrics": {
    "activity_score": 485.5,
    "read_events": 330,
    "write_events": 120
  },
  "costs": {
    "total_cost": 4523.50,
    "cost_per_resource": 180.94
  }
}
```

## Next Steps for Frontend

You'll need frontend components to display:

1. **User Dashboard** - Overview of all users
2. **Top Users Table** - Sortable by usage or cost
3. **User Detail View** - Individual person's metrics
4. **Inactive Users List** - People not using AWS
5. **Cost Attribution Chart** - Visualize costs per person
6. **Usage Trends** - Activity over time per user

## Testing with Sample Data

The system includes sample data generators:
- `generate_sample_user_analytics()` - Creates user metrics
- `generate_sample_user_costs()` - Creates cost attribution

You can test the endpoints with sample data to see person-level insights.

## Key Features for Your Use Case

✅ **Person-Level Tracking** - Each user/person is tracked individually
✅ **Usage Metrics** - Who is using much, who is not
✅ **Cost Attribution** - What cost each person is influencing
✅ **Activity Scoring** - Quantified usage levels
✅ **Inactive Detection** - Identify people not using AWS
✅ **Service/Region Breakdown** - What each person is using where

This implementation addresses your requirement to track hundreds of people and understand:
- Who is using AWS
- How much each person is using
- What each person is costing
