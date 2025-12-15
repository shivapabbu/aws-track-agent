"""
Script to fix imports - adds strands_agents stub if package not available.
Run this before starting the backend.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import strands_agents, if not available, use stub
try:
    import strands_agents
    print("✅ Using strands_agents package")
except ImportError:
    print("⚠️  strands_agents not found, using stub...")
    import strands_agents_stub
    sys.modules['strands_agents'] = strands_agents_stub
    print("✅ Using strands_agents stub")

# Now import the rest
from config import settings
print("✅ Configuration loaded")
