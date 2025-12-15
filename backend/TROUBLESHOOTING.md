# Backend Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'strands_agents'"

**Solution**: The code uses a stub for strands_agents. Make sure `strands_agents_stub.py` exists in the backend directory.

The backend automatically uses the stub if strands_agents is not installed. If you see this error:

1. Check that `strands_agents_stub.py` exists:
   ```bash
   ls backend/strands_agents_stub.py
   ```

2. The stub should be automatically loaded. If not, the import in `api/main.py` should handle it.

### Issue 2: "ImportError" or "ModuleNotFoundError"

**Solution**: Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Issue 3: Backend starts but crashes immediately

**Solution**: Run the health check:
```bash
cd backend
python check_backend.py
```

This will identify:
- Missing dependencies
- Import errors
- Configuration issues

### Issue 4: "Port 8000 already in use"

**Solution**: Either:
1. Stop the process using port 8000:
   ```bash
   lsof -ti:8000 | xargs kill
   ```

2. Or change the port in `.env`:
   ```env
   API_PORT=8001
   ```

### Issue 5: "AWS credentials not found" (in test mode)

**Solution**: This is OK in test mode! Set:
```env
TEST_MODE=true
USE_SAMPLE_DATA=true
```

AWS credentials are not needed when using sample data.

### Issue 6: Agents not starting

**Solution**: Check:
1. Agents start automatically on backend startup
2. Check logs for errors
3. Verify agents are initialized:
   ```bash
   curl http://localhost:8000/api/agents
   ```

## Step-by-Step Debugging

### Step 1: Check Python Version
```bash
python3 --version  # Should be 3.9+
```

### Step 2: Check Dependencies
```bash
cd backend
pip list | grep -E "fastapi|uvicorn|boto3|pydantic"
```

### Step 3: Run Health Check
```bash
python check_backend.py
```

### Step 4: Try Starting Backend
```bash
python run.py
```

### Step 5: Check for Errors
Look for error messages in the console output. Common errors:
- Import errors → Install missing packages
- Configuration errors → Check `.env` file
- Port conflicts → Change port or kill existing process

## Quick Fixes

### Reinstall Dependencies
```bash
cd backend
pip install --upgrade -r requirements.txt
```

### Create .env File
```bash
cd backend
cat > .env << EOF
TEST_MODE=true
USE_SAMPLE_DATA=true
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
FRONTEND_URL=http://localhost:3000
EOF
```

### Test API Endpoint
```bash
curl http://localhost:8000/health
```

## Getting Help

If the backend still won't start:

1. Run the health check and share the output
2. Check the error message in the console
3. Verify all files are in place:
   ```bash
   ls -la backend/
   ls -la backend/agents/
   ls -la backend/tools/
   ls -la backend/api/
   ```

4. Try running from the backend directory:
   ```bash
   cd backend
   python run.py
   ```
