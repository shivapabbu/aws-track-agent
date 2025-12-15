"""Orchestrator Agent that coordinates all monitoring agents."""
from typing import Dict, List
import asyncio
from strands_agents import Agent
from agents.cloudtrail_monitoring_agent import CloudTrailMonitoringAgent
from agents.cost_anomaly_agent import CostAnomalyDetectionAgent
from config import settings


class OrchestratorAgent(Agent):
    """
    Master agent that orchestrates all monitoring agents.
    Manages the lifecycle and coordination of specialized agents.
    """
    
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            description="Orchestrates all AWS monitoring agents"
        )
        
        # Initialize specialized agents
        self.cloudtrail_agent = CloudTrailMonitoringAgent()
        self.cost_agent = CostAnomalyDetectionAgent()
        
        self.agents = {
            "cloudtrail": self.cloudtrail_agent,
            "cost": self.cost_agent
        }
        
        self.running = False
        self.tasks = []
    
    async def start_all_agents(self):
        """Start all monitoring agents."""
        if self.running:
            print(f"[{self.name}] Agents already running")
            return
        
        self.running = True
        print(f"[{self.name}] Starting all monitoring agents...")
        
        # Start CloudTrail monitoring
        cloudtrail_task = asyncio.create_task(
            self.cloudtrail_agent.monitor_continuously()
        )
        self.tasks.append(cloudtrail_task)
        
        # Start Cost monitoring
        cost_task = asyncio.create_task(
            self.cost_agent.monitor_continuously()
        )
        self.tasks.append(cost_task)
        
        print(f"[{self.name}] All agents started")
    
    async def stop_all_agents(self):
        """Stop all monitoring agents."""
        if not self.running:
            return
        
        print(f"[{self.name}] Stopping all agents...")
        
        self.running = False
        
        # Stop individual agents
        self.cloudtrail_agent.stop()
        self.cost_agent.stop()
        
        # Cancel tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks = []
        print(f"[{self.name}] All agents stopped")
    
    def get_all_agent_status(self) -> Dict:
        """Get status of all agents."""
        return {
            "orchestrator": {
                "name": self.name,
                "running": self.running,
                "agents_count": len(self.agents)
            },
            "agents": {
                agent_name: agent.get_status()
                for agent_name, agent in self.agents.items()
            }
        }
    
    def get_agent(self, agent_name: str):
        """Get a specific agent by name."""
        return self.agents.get(agent_name)
