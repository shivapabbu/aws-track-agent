"""Test script to inject sample data and verify the system."""
import asyncio
import requests
import time
from utils.sample_data import (
    generate_sample_cloudtrail_events,
    generate_sample_cost_anomalies
)

API_URL = "http://localhost:8000"


def test_inject_sample_data():
    """Inject sample data into the system."""
    print("=" * 60)
    print("AWS Track Agent - Sample Data Test")
    print("=" * 60)
    
    # Wait for API to be ready
    print("\n1. Checking API health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Make sure the backend is running.")
        print("   Run: cd backend && python run.py")
        return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Inject sample data
    print("\n2. Injecting sample data...")
    try:
        payload = {
            "cloudtrail_events_count": 15,
            "cost_anomalies_count": 8,
            "clear_existing": True
        }
        response = requests.post(
            f"{API_URL}/api/test/inject-sample-data",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Sample data injected successfully")
            print(f"   - CloudTrail events: {data.get('cloudtrail_events_injected')}")
            print(f"   - Cost anomalies: {data.get('cost_anomalies_injected')}")
            print(f"   - Total events: {data.get('total_cloudtrail_events')}")
            print(f"   - Total anomalies: {data.get('total_cost_anomalies')}")
        else:
            print(f"   ❌ Failed to inject data: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error injecting data: {e}")
        return
    
    # Check dashboard stats
    print("\n3. Checking dashboard statistics...")
    try:
        response = requests.get(f"{API_URL}/api/dashboard/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Dashboard stats retrieved")
            print(f"   - CloudTrail events: {stats.get('cloudtrail', {}).get('suspicious_events', 0)}")
            print(f"   - Cost anomalies: {stats.get('cost', {}).get('anomalies', 0)}")
            print(f"   - CloudTrail running: {stats.get('cloudtrail', {}).get('running', False)}")
            print(f"   - Cost running: {stats.get('cost', {}).get('running', False)}")
        else:
            print(f"   ❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")
    
    # Check CloudTrail events
    print("\n4. Checking CloudTrail events...")
    try:
        response = requests.get(f"{API_URL}/api/cloudtrail/events?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"   ✅ Retrieved {len(events)} events")
            if events:
                print("   Sample events:")
                for i, event in enumerate(events[:3], 1):
                    print(f"   {i}. {event.get('event_name', 'Unknown')} - {event.get('event_time', 'N/A')}")
        else:
            print(f"   ❌ Failed to get events: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting events: {e}")
    
    # Check cost anomalies
    print("\n5. Checking cost anomalies...")
    try:
        response = requests.get(f"{API_URL}/api/cost/anomalies?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            anomalies = data.get('anomalies', [])
            print(f"   ✅ Retrieved {len(anomalies)} anomalies")
            if anomalies:
                print("   Sample anomalies:")
                for i, anomaly in enumerate(anomalies[:3], 1):
                    impact = anomaly.get('impact', {}).get('TotalImpact', {}).get('Amount', '0')
                    print(f"   {i}. {anomaly.get('dimension_value', 'Unknown')} - ${impact}")
        else:
            print(f"   ❌ Failed to get anomalies: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting anomalies: {e}")
    
    # Check agent status
    print("\n6. Checking agent status...")
    try:
        response = requests.get(f"{API_URL}/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Agent status retrieved")
            agents = data.get('agents', {}).get('agents', {})
            for agent_name, agent_status in agents.items():
                running = agent_status.get('running', False)
                status_icon = "✅" if running else "❌"
                print(f"   {status_icon} {agent_name}: {'Running' if running else 'Stopped'}")
        else:
            print(f"   ❌ Failed to get agent status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting agent status: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser to view the dashboard")
    print("2. The dashboard should show the injected sample data")
    print("3. Try injecting more data: POST /api/test/inject-sample-data")
    print("4. Clear data: POST /api/test/clear-all-data")


if __name__ == "__main__":
    print("\nWaiting for API to be ready...")
    time.sleep(2)  # Give API a moment to start
    test_inject_sample_data()
