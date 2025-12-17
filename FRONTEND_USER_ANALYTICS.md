# Frontend User Analytics - Quick Start

## What Was Added

### ✅ New Frontend Components

1. **UserAnalytics Component** (`frontend/components/UserAnalytics.tsx`)
   - Displays person-level analytics
   - Shows top users by usage and cost
   - Displays inactive users
   - User detail modal with full metrics

2. **Tab Navigation** (Updated `frontend/app/page.tsx`)
   - Dashboard tab (existing)
   - User Analytics tab (new)

### ✅ Backend Updates

1. **Test Endpoints Updated** (`backend/api/test_endpoints.py`)
   - Now injects user analytics sample data
   - Generates 50 sample users with metrics and costs

## How to See Sample Data in Frontend

### Step 1: Start Backend

```bash
cd backend
python3 run.py
```

### Step 2: Inject Sample Data

In another terminal:

```bash
curl -X POST http://localhost:8000/api/test/inject-sample-data \
  -H "Content-Type: application/json" \
  -d '{
    "cloudtrail_events_count": 15,
    "cost_anomalies_count": 8,
    "clear_existing": true
  }'
```

Or use the test script:

```bash
cd backend
python3 test_with_sample_data.py
```

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 4: View User Analytics

1. Open `http://localhost:3000` in your browser
2. Click on the **"User Analytics"** tab
3. You'll see:
   - Summary cards (Total Users, Total Events, Total Cost, Inactive Users)
   - Top Users by Activity table
   - Top Users by Cost table
   - Click any user to see detailed metrics

## What You'll See

### Summary Cards
- **Total Users**: Number of users tracked
- **Total Events**: Sum of all user events
- **Total Cost**: Sum of all user costs
- **Inactive Users**: Users not active in 30+ days

### Top Users by Activity
Table showing:
- User name
- Total events
- Activity score

### Top Users by Cost
Table showing:
- User name
- Total cost
- Resource count

### User Details Modal
Click any user to see:
- Usage metrics (events, activity score, services, regions)
- Cost attribution (total cost, resources, service breakdown)
- Usage category (inactive, light, moderate, heavy, very_heavy)

## Sample Data Generated

When you inject sample data, it creates:
- **50 users** with realistic metrics
- **User analytics** with activity scores
- **Cost attribution** per user
- **Usage categories** for each user

## API Endpoints Used

The frontend calls:
- `GET /api/users/analytics` - All user analytics
- `GET /api/users/top-by-usage` - Top users by activity
- `GET /api/users/top-by-cost` - Top users by cost
- `GET /api/users/inactive` - Inactive users
- `GET /api/users/{user_name}` - Specific user details

## Troubleshooting

**No data showing?**
1. Make sure backend is running
2. Inject sample data using the curl command above
3. Check browser console for errors
4. Verify API URL in frontend `.env.local`

**Users not appearing?**
- The sample data generates 50 users
- Refresh the page after injecting data
- Check the Network tab in browser dev tools

**Cost data showing $0?**
- Cost attribution requires cost data
- Sample data includes cost attribution
- In production, connect to AWS Cost Explorer

## Next Steps

1. **Customize UI**: Modify colors, layouts, add charts
2. **Add Filters**: Filter users by activity, cost, category
3. **Add Charts**: Visualize usage trends, cost distribution
4. **Export Data**: Add CSV/PDF export functionality
5. **Real-time Updates**: Enhance auto-refresh intervals

Enjoy exploring person-level analytics! 🚀
