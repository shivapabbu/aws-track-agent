# Quick Fix for Backend Not Running

## Issue Found

The health check shows one missing dependency: `python-dotenv`

## Quick Fix (30 seconds)

Run this command:

```bash
cd backend
pip install python-dotenv
```

Or install all dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Then Start Backend

```bash
python3 run.py
```

Or use the startup script:

```bash
./start_backend.sh
```

## Verify It's Working

Once started, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Then test:
```bash
curl http://localhost:8000/health
```

## If Still Not Working

1. **Check for errors in console** - Look for red error messages

2. **Run health check again**:
   ```bash
   python3 check_backend.py
   ```

3. **Check .env file exists**:
   ```bash
   ls -la .env
   ```

4. **Try starting with debug**:
   ```bash
   API_DEBUG=true python3 run.py
   ```

## Common Issues

- **Port 8000 in use**: Change port in `.env` or kill process: `lsof -ti:8000 | xargs kill`
- **Import errors**: Run `pip install -r requirements.txt`
- **Permission errors**: Make sure you're in the backend directory

## Success Indicators

✅ Backend starts without errors
✅ You see "Application startup complete"
✅ `curl http://localhost:8000/health` returns JSON
✅ Agents show as "running" in the response
