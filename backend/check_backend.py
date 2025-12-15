"""Script to check backend setup and diagnose issues."""
import sys
import os

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'boto3',
        'python-dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_imports():
    """Check if backend modules can be imported."""
    print("\nChecking imports...")
    try:
        from config import settings
        print("✅ config.py imports successfully")
    except Exception as e:
        print(f"❌ Error importing config: {e}")
        return False
    
    try:
        # Try importing with stub
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import strands_agents_stub
        sys.modules['strands_agents'] = strands_agents_stub
        print("✅ Using strands_agents stub")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    
    try:
        from agents.orchestrator_agent import OrchestratorAgent
        print("✅ OrchestratorAgent imports successfully")
    except Exception as e:
        print(f"❌ Error importing OrchestratorAgent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from api.main import app
        print("✅ API app imports successfully")
    except Exception as e:
        print(f"❌ Error importing API: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def check_env_file():
    """Check if .env file exists."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"✅ .env file exists at {env_path}")
        return True
    else:
        print(f"⚠️  .env file not found at {env_path}")
        print("   Creating example .env file...")
        try:
            with open(env_path, 'w') as f:
                f.write("""# AWS Configuration (optional for test mode)
AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=

# Test Mode
TEST_MODE=true
USE_SAMPLE_DATA=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Frontend URL
FRONTEND_URL=http://localhost:3000
""")
            print("   ✅ Created .env file")
            return True
        except Exception as e:
            print(f"   ❌ Could not create .env: {e}")
            return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("AWS Track Agent - Backend Health Check")
    print("=" * 60)
    
    all_ok = True
    
    print("\n1. Python Version:")
    if not check_python_version():
        all_ok = False
    
    print("\n2. Dependencies:")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"\n   Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        all_ok = False
    
    print("\n3. Environment File:")
    check_env_file()
    
    print("\n4. Module Imports:")
    if not check_imports():
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ All checks passed! Backend should run successfully.")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  python run.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
