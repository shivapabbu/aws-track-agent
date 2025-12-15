# AWS Track Agent - Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- AWS Account with appropriate permissions
- PostgreSQL (optional, for production)
- Redis (optional, for caching)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials and configuration:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
CLOUDTRAIL_S3_BUCKET=your-cloudtrail-bucket
CLOUDTRAIL_LOG_PREFIX=CloudTrail/
```

### 3. AWS Permissions Required

Your AWS credentials need the following permissions:

- `cloudtrail:GetTrail`
- `cloudtrail:GetInsightSelectors`
- `cloudtrail:GetEventSelectors`
- `s3:GetObject` (for CloudTrail log bucket)
- `s3:ListBucket` (for CloudTrail log bucket)
- `ce:GetCostAndUsage`
- `ce:GetAnomalyMonitors`
- `ce:GetAnomalies`
- `ce:CreateAnomalyMonitor`
- `ce:CreateAnomalySubscription`
- `sns:Publish` (for alerts)
- `ses:SendEmail` (for email alerts, if using)

### 4. Run Backend

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Frontend

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Running the System

1. **Start Backend**: The agents will automatically start when the backend starts
2. **Start Frontend**: Open the dashboard in your browser
3. **Monitor**: The agents will continuously monitor AWS activity and costs

## Agent Configuration

### CloudTrail Monitoring Agent

- **Check Interval**: Default 60 seconds (configurable via `CLOUDTRAIL_CHECK_INTERVAL_SECONDS`)
- **Monitors**: CloudTrail logs for suspicious activity
- **Alerts**: Sends alerts for high-risk events and policy violations

### Cost Anomaly Detection Agent

- **Check Interval**: Default 3600 seconds (1 hour, configurable via `COST_CHECK_INTERVAL_SECONDS`)
- **Monitors**: AWS Cost Anomaly Detection service
- **Alerts**: Sends alerts for cost spikes and anomalies

## API Endpoints

- `GET /health` - Health check and agent status
- `GET /api/agents` - Get all agent statuses
- `GET /api/agents/{agent_name}` - Get specific agent status
- `GET /api/cloudtrail/events` - Get CloudTrail events
- `GET /api/cost/anomalies` - Get cost anomalies
- `GET /api/dashboard/stats` - Get dashboard statistics

## Troubleshooting

### Agents Not Starting

- Check AWS credentials are correctly configured
- Verify AWS permissions
- Check CloudTrail S3 bucket is accessible
- Review backend logs for errors

### No Events/Anomalies Detected

- Verify CloudTrail is enabled and logging to S3
- Check Cost Anomaly Detection monitors are configured
- Ensure time ranges are appropriate
- Review agent logs for issues

### Frontend Not Connecting

- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Review browser console for CORS errors
- Ensure backend CORS settings include frontend URL

## Production Deployment

### Backend

1. Use a production WSGI server (e.g., gunicorn)
2. Set up proper database (PostgreSQL)
3. Configure Redis for caching
4. Set up proper logging
5. Use environment variables for all secrets
6. Enable HTTPS

### Frontend

1. Build for production: `npm run build`
2. Deploy to Vercel, Netlify, or similar
3. Configure production API URL
4. Enable HTTPS

## Monitoring the Agents

The agents run continuously and can be monitored via:

1. **Dashboard**: Real-time status in the frontend
2. **API**: `/health` and `/api/agents` endpoints
3. **Logs**: Backend console output
4. **Alerts**: SNS, Slack, or Email notifications

## Next Steps

- Configure alerting channels (SNS, Slack, Email)
- Set up CloudTrail organization trail
- Configure Cost Anomaly Detection monitors
- Customize suspicious event detection rules
- Set up automated reports
