# Testing with Sample Data

This guide explains how to test the AWS Track Agent system with sample data without requiring real AWS credentials.

## Quick Start

### 1. Enable Test Mode

Create or update `backend/.env`:

```env
# Enable test mode and sample data
TEST_MODE=true
USE_SAMPLE_DATA=true

# You can leave AWS credentials empty in test mode
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
```

### 2. Start Backend

```bash
cd backend
python run.py
```

The API will start at `http://localhost:8000`

### 3. Inject Sample Data

#### Option A: Using the Test Script

```bash
cd backend
python test_with_sample_data.py
```

This script will:
- Check API health
- Inject sample CloudTrail events and cost anomalies
- Verify the data was injected correctly
- Display sample data

#### Option B: Using API Endpoints

**Inject Sample Data:**
```bash
curl -X POST http://localhost:8000/api/test/inject-sample-data \
  -H "Content-Type: application/json" \
  -d '{
    "cloudtrail_events_count": 15,
    "cost_anomalies_count": 8,
    "clear_existing": true
  }'
```

**Clear All Data:**
```bash
curl -X POST http://localhost:8000/api/test/clear-all-data
```

**Get Sample Stats:**
```bash
curl http://localhost:8000/api/test/sample-stats
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser to see the dashboard with sample data.

## Sample Data Details

### CloudTrail Events

The sample data generator creates realistic CloudTrail events including:

- **Event Types**: RunInstances, TerminateInstances, DeleteBucket, CreateUser, etc.
- **Suspicious Events**: ~20% of events are flagged as suspicious with:
  - High-risk operations (deletions, policy changes)
  - Access denied errors
  - Suspicious user agents
  - Unusual source IPs
- **User Identities**: Various IAM users and roles
- **Timestamps**: Events from the last hour

### Cost Anomalies

The sample data generator creates cost anomalies with:

- **Impact Amounts**: Ranging from $10 to $10,000
- **Severity Levels**: Based on impact (info, warning, critical)
- **Root Causes**: Various reasons (unusual usage, increased activity, etc.)
- **Dimensions**: Different services, regions, and tags
- **Status**: OPEN or CLOSED

## Testing Scenarios

### Scenario 1: Basic Dashboard View

1. Inject sample data (15 events, 8 anomalies)
2. Open dashboard
3. Verify:
   - Stats cards show correct counts
   - Agent status shows "Running"
   - Events table displays events
   - Anomalies table displays anomalies

### Scenario 2: Real-time Updates

1. Start backend and frontend
2. Inject initial data
3. Wait 5-10 seconds
4. Inject more data via API
5. Verify dashboard updates automatically

### Scenario 3: Multiple Injections

1. Inject data multiple times with `clear_existing: false`
2. Verify data accumulates
3. Check total counts increase

### Scenario 4: Clear and Re-inject

1. Inject data
2. Clear all data
3. Verify counts go to zero
4. Inject again
5. Verify new data appears

## API Endpoints for Testing

### Health Check
```bash
GET /health
```

### Agent Status
```bash
GET /api/agents
GET /api/agents/cloudtrail
GET /api/agents/cost
```

### Data Endpoints
```bash
GET /api/cloudtrail/events?limit=10
GET /api/cost/anomalies?limit=10
GET /api/dashboard/stats
```

### Test Endpoints
```bash
POST /api/test/inject-sample-data
POST /api/test/clear-all-data
GET /api/test/sample-stats
```

## Sample Data Structure

### CloudTrail Event Example
```json
{
  "eventID": "abc-123-def",
  "eventTime": "2024-01-15T10:30:00Z",
  "eventName": "TerminateInstances",
  "eventSource": "ec2.amazonaws.com",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.1",
  "userIdentity": {
    "type": "IAMUser",
    "userName": "admin@example.com",
    "arn": "arn:aws:iam::123456789012:user/admin@example.com"
  },
  "readOnly": false,
  "managementEvent": true
}
```

### Cost Anomaly Example
```json
{
  "anomaly_id": "anomaly-abc123",
  "impact": {
    "TotalImpact": {
      "Amount": "1250.50",
      "Unit": "USD"
    }
  },
  "dimension_value": "us-east-1",
  "status": "OPEN",
  "root_cause": [
    "Unusual usage in Amazon EC2",
    "Increased activity in production"
  ]
}
```

## Troubleshooting

### API Not Responding
- Check if backend is running: `curl http://localhost:8000/health`
- Check backend logs for errors
- Verify port 8000 is not in use

### No Data Showing
- Inject sample data first
- Check agent status: `GET /api/agents`
- Verify agents are running
- Check browser console for errors

### Frontend Not Updating
- Check API URL in frontend `.env.local`
- Verify CORS is enabled in backend
- Check browser network tab for API calls
- Refresh the page

### Test Endpoints Not Available
- Ensure `TEST_MODE=true` or `USE_SAMPLE_DATA=true` in `.env`
- Restart backend after changing `.env`
- Check backend logs for test router inclusion

## Next Steps

1. **Test with Real AWS**: Once verified with sample data, configure real AWS credentials
2. **Customize Detection Rules**: Modify agent logic for your specific needs
3. **Add More Sample Data**: Extend `utils/sample_data.py` with more scenarios
4. **Performance Testing**: Test with larger datasets (100+ events, 50+ anomalies)

## Example Test Session

```bash
# Terminal 1: Start backend
cd backend
python run.py

# Terminal 2: Inject sample data
cd backend
python test_with_sample_data.py

# Terminal 3: Start frontend
cd frontend
npm run dev

# Browser: Open http://localhost:3000
# You should see the dashboard with sample data!
```

## Automated Testing

You can also create automated tests:

```python
import requests

def test_sample_data_injection():
    response = requests.post(
        "http://localhost:8000/api/test/inject-sample-data",
        json={"cloudtrail_events_count": 10, "cost_anomalies_count": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cloudtrail_events_injected"] == 10
    assert data["cost_anomalies_injected"] == 5
```

Happy testing! 🚀
