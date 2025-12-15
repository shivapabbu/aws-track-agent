# Quick Test Guide - Sample Data

## 🚀 Fastest Way to Test

### Step 1: Enable Test Mode

Create `backend/.env`:
```env
TEST_MODE=true
USE_SAMPLE_DATA=true
```

### Step 2: Start Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Wait for: `Application startup complete`

### Step 3: Inject Sample Data

In a new terminal:
```bash
cd backend
python test_with_sample_data.py
```

You should see:
```
✅ API is running
✅ Sample data injected successfully
✅ Dashboard stats retrieved
✅ Retrieved X events
✅ Retrieved X anomalies
```

### Step 4: Start Frontend

In another terminal:
```bash
cd frontend
npm install
npm run dev
```

### Step 5: View Dashboard

Open: **http://localhost:3000**

You should see:
- ✅ Stats cards with numbers
- ✅ Agent status showing "Running"
- ✅ Events table with sample CloudTrail events
- ✅ Anomalies table with sample cost anomalies

## 🎯 Quick API Tests

### Check Health
```bash
curl http://localhost:8000/health
```

### Inject More Data
```bash
curl -X POST http://localhost:8000/api/test/inject-sample-data \
  -H "Content-Type: application/json" \
  -d '{"cloudtrail_events_count": 20, "cost_anomalies_count": 10}'
```

### View Events
```bash
curl http://localhost:8000/api/cloudtrail/events?limit=5
```

### View Anomalies
```bash
curl http://localhost:8000/api/cost/anomalies?limit=5
```

### Clear All Data
```bash
curl -X POST http://localhost:8000/api/test/clear-all-data
```

## 📊 What You'll See

### Dashboard Stats
- **CloudTrail Events**: Number of suspicious events detected
- **Cost Anomalies**: Number of cost anomalies found
- **Active Alerts**: Total alerts requiring attention
- **Monitoring Status**: Overall system status

### Events Table
- Event name (e.g., "TerminateInstances")
- Timestamp
- User who performed the action
- Source IP address

### Anomalies Table
- Dimension (service/region/tag)
- Impact amount in USD
- Status (OPEN/CLOSED)

## 🔧 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is free

**No data showing?**
- Run: `python test_with_sample_data.py`
- Check: `curl http://localhost:8000/health`
- Verify agents are running

**Frontend not connecting?**
- Check backend is running on port 8000
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

## ✨ Next Steps

Once you see sample data working:
1. Test with real AWS credentials (remove TEST_MODE)
2. Customize detection rules
3. Configure alerting channels
4. Deploy to production

Happy testing! 🎉
