# system_check.py
import requests
import json

print("🔍 SYSTEM HEALTH CHECK FOR PRESENTATION\n")
print("=" * 50)

# Check API
try:
    response = requests.get("http://localhost:8000/")
    print("✅ API Status: ONLINE")
    print(f"   Version: {response.json()['version']}")
except:
    print("❌ API is OFFLINE - Start it with: python main.py")
    exit(1)

# Check Metrics
try:
    metrics = requests.get("http://localhost:8000/api/metrics")
    data = metrics.json()
    print(f"\n✅ Database Status: ACTIVE")
    print(f"   Total Calls: {data['total_calls']:,}")
    print(f"   Avg Duration: {data['average_duration']/60:.1f} minutes")
    print(f"   Resolution Rate: {(data['calls_by_outcome'].get('resolved', 0) / data['total_calls'] * 100):.1f}%")
except:
    print("❌ Cannot fetch metrics")

# Check Agents
try:
    agents = requests.get("http://localhost:8000/api/agents")
    print(f"\n✅ Active Agents: {len(agents.json())}")
    print(f"   Agent IDs: {', '.join([a['agent_id'] for a in agents.json()[:5]])}...")
except:
    print("❌ Cannot fetch agents")

print("\n" + "=" * 50)
print("🎯 Ready for presentation! Open http://localhost:8501")