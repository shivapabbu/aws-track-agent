"""Test script to verify backend can start."""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing backend startup...")
print("=" * 60)

try:
    # Test imports
    print("1. Testing imports...")
    from api.main import app, orchestrator
    print("   ✅ All imports successful")
    
    # Test app creation
    print("2. Testing app creation...")
    assert app is not None
    print("   ✅ FastAPI app created")
    
    # Test orchestrator
    print("3. Testing orchestrator...")
    assert orchestrator is not None
    print(f"   ✅ Orchestrator created: {orchestrator.name}")
    
    # Test agents
    print("4. Testing agents...")
    cloudtrail_agent = orchestrator.get_agent("cloudtrail")
    cost_agent = orchestrator.get_agent("cost")
    assert cloudtrail_agent is not None
    assert cost_agent is not None
    print(f"   ✅ CloudTrail agent: {cloudtrail_agent.name}")
    print(f"   ✅ Cost agent: {cost_agent.name}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Backend is ready to run.")
    print("=" * 60)
    print("\nTo start the backend:")
    print("  python3 run.py")
    print("\nOr:")
    print("  uvicorn api.main:app --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
