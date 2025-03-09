import random
import time
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging
from datetime import datetime

# Set up logging with a simpler format
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'  # Simplified format: no timestamp
)
logger = logging.getLogger("disaster_response_system")

# Base Agent Class
class Agent(ABC):
    def __init__(self, agent_id: str, name: str, message_broker):
        self.agent_id = agent_id
        self.name = name
        self.message_broker = message_broker
        self.logger = logging.getLogger(f"disaster_response_system.{self.agent_id}")
        self.messages = []
        
    def send_message(self, to_agent_id: str, message_content: Dict[str, Any]) -> None:
        message = {
            "from": self.agent_id,
            "to": to_agent_id,
            "timestamp": datetime.now().isoformat(),
            "content": message_content
        }
        self.messages.append(message)
        self.logger.debug(f"Message sent to {to_agent_id}: {message_content}")  # Debug level for details
        self.message_broker.publish_message(message)
        
    def receive_message(self, message: Dict[str, Any]) -> None:
        self.messages.append(message)
        self.logger.debug(f"Message received from {message['from']}: {message['content']}")
        self.process_message(message)
        
    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass


# Message Broker
class MessageBroker:
    def __init__(self):
        self.subscribers = {}
        self.logger = logging.getLogger("disaster_response_system.message_broker")
        
    def subscribe(self, agent_id: str, callback):
        self.subscribers[agent_id] = callback
        self.logger.debug(f"Agent {agent_id} subscribed")  # Debug level
        
    def publish_message(self, message: Dict[str, Any]):
        recipient = message["to"]
        if recipient in self.subscribers:
            self.subscribers[recipient](message)
            self.logger.debug(f"Message delivered to {recipient}")
        else:
            self.logger.warning(f"No subscriber for {recipient}")


# Disaster Context
class DisasterContext:
    def __init__(self, disaster_type: str, location: str, severity: int):
        self.disaster_type = disaster_type
        self.location = location
        self.severity = severity
        self.affected_areas = []
        self.victims = {}
        self.resources = {}
        self.volunteers = {}
        self.rescue_teams = {}
        self.current_tasks = {}
        self.data_sources = {}
        self.logger = logging.getLogger("disaster_response_system.disaster_context")


# Relief Coordinator Agent
class ReliefCoordinatorAgent(Agent):
    def __init__(self, agent_id: str, name: str, disaster_context: DisasterContext, message_broker):
        super().__init__(agent_id, name, message_broker)
        self.disaster_context = disaster_context
        self.resource_allocation_plan = {}
        self.priority_areas = []
        
    def process_message(self, message: Dict[str, Any]) -> None:
        content = message["content"]
        if content.get("type") == "need_assessment":
            self.update_priority_areas(content["area_data"])
            self.optimize_resource_allocation()
            
    def update_priority_areas(self, area_data: List[Dict[str, Any]]) -> None:
        self.priority_areas = sorted(area_data, key=lambda x: (x["severity"] * x["population"]), reverse=True)
        self.logger.info(f"Prioritized {len(self.priority_areas)} areas")
    
    def update_resources(self, resources: Dict[str, int]) -> None:
        self.disaster_context.resources.update(resources)
        self.logger.info(f"Resources initialized: {self.disaster_context.resources}")
    
    def optimize_resource_allocation(self) -> None:
        allocation_plan = {}
        remaining_resources = self.disaster_context.resources.copy()
        for area in self.priority_areas:
            area_name = area["name"]
            allocation_plan[area_name] = {}
            total_priority_weight = sum(a["severity"] * a["population"] for a in self.priority_areas)
            area_weight = (area["severity"] * area["population"]) / total_priority_weight if total_priority_weight > 0 else 0
            for resource_type, total_quantity in remaining_resources.items():
                allocated_quantity = int(total_quantity * area_weight)
                if allocated_quantity > 0:
                    allocation_plan[area_name][resource_type] = allocated_quantity
                    remaining_resources[resource_type] -= allocated_quantity
        self.resource_allocation_plan = allocation_plan
        self.logger.info(f"Created allocation plan for {len(allocation_plan)} areas")
        self.send_message("volunteer_coordinator", {"type": "new_allocation_plan", "plan": allocation_plan})
    
    def run(self) -> None:
        self.logger.info(f"{self.name} started")
        initial_resources = {"food": 1000, "water": 5000, "medical_supplies": 500, "shelter_kits": 200, "blankets": 1000}
        self.update_resources(initial_resources)
        self.send_message("analytics", {"type": "request_area_assessment", "disaster_type": self.disaster_context.disaster_type, "location": self.disaster_context.location})


# Volunteer Coordinator Agent
class VolunteerCoordinationAgent(Agent):
    def __init__(self, agent_id: str, name: str, disaster_context: DisasterContext, message_broker):
        super().__init__(agent_id, name, message_broker)
        self.disaster_context = disaster_context
        self.available_volunteers = {}
        self.skills_registry = {}
        self.task_assignments = {}
        self.pending_tasks = []
    
    def process_message(self, message: Dict[str, Any]) -> None:
        content = message["content"]
        if content.get("type") == "new_allocation_plan":
            self.generate_distribution_tasks(content["plan"])
    
    def register_volunteer(self, volunteer: Dict[str, Any]) -> None:
        volunteer_id = volunteer["id"]
        self.available_volunteers[volunteer_id] = volunteer
        for skill in volunteer["skills"]:
            if skill not in self.skills_registry:
                self.skills_registry[skill] = []
            self.skills_registry[skill].append(volunteer_id)
        self.logger.debug(f"Registered volunteer {volunteer_id}")
    
    def generate_distribution_tasks(self, allocation_plan: Dict[str, Dict[str, int]]) -> None:
        tasks_created = 0
        for area, resources in allocation_plan.items():
            for resource_type, quantity in resources.items():
                task = {
                    "id": f"dist_{area}_{resource_type}_{int(time.time())}",
                    "type": "resource_distribution",
                    "description": f"Distribute {quantity} {resource_type} to {area}",
                    "location": area,
                    "resources": {resource_type: quantity},
                    "required_skills": ["logistics"],
                    "priority": 3
                }
                self.pending_tasks.append(task)
                tasks_created += 1
        self.logger.info(f"Generated {tasks_created} distribution tasks")
    
    def run(self) -> None:
        self.logger.info(f"{self.name} started")
        demo_volunteers = [
            {"id": f"vol_{i}", "name": f"Volunteer {i}", "skills": random.sample(["medical", "logistics", "rescue", "communication", "engineering"], k=random.randint(1, 3)), "location": "Base Camp", "available": True}
            for i in range(1, 21)
        ]
        for volunteer in demo_volunteers:
            self.register_volunteer(volunteer)
        self.logger.info(f"Registered {len(demo_volunteers)} volunteers")
        self.send_message("communication", {"type": "volunteer_status", "total_volunteers": len(self.available_volunteers)})


# Communication Agent
class CommunicationAgent(Agent):
    def __init__(self, agent_id: str, name: str, disaster_context: DisasterContext, message_broker):
        super().__init__(agent_id, name, message_broker)
        self.disaster_context = disaster_context
        self.victim_requests = {}
        self.rescue_team_locations = {}
        self.message_log = []
        self.priority_messages = []
    
    def process_message(self, message: Dict[str, Any]) -> None:
        content = message["content"]
        if content.get("type") == "alert":
            self.broadcast_alert(content)
    
    def update_team_location(self, team_id: str, location: Dict[str, float]) -> None:
        self.rescue_team_locations[team_id] = location
        self.logger.debug(f"Updated team {team_id} location")
    
    def broadcast_alert(self, alert: Dict[str, Any]) -> None:
        alert_message = {
            "type": "emergency_alert",
            "alert_type": alert["alert_type"],
            "message": alert["message"],
            "areas_affected": alert.get("areas_affected", []),
            "recommended_actions": alert.get("recommended_actions", [])
        }
        for team_id in self.rescue_team_locations:
            self.send_message(f"rescue_team_{team_id}", alert_message)
        self.send_message("volunteer_coordinator", alert_message)
        self.logger.info(f"Broadcasted {alert['alert_type']} alert")
    
    def run(self) -> None:
        self.logger.info(f"{self.name} started")
        demo_teams = {f"team_{i}": {"lat": 34.0522 + (random.random() - 0.5) * 0.1, "lon": -118.2437 + (random.random() - 0.5) * 0.1} for i in range(1, 6)}
        for team_id, location in demo_teams.items():
            self.update_team_location(team_id, location)
        self.logger.info(f"Initialized {len(demo_teams)} rescue teams")
        self.send_message("analytics", {"type": "communication_system_status", "status": "operational", "teams_connected": len(self.rescue_team_locations)})


# Analytics & Prediction Agent
class AnalyticsPredictionAgent(Agent):
    def __init__(self, agent_id: str, name: str, disaster_context: DisasterContext, message_broker):
        super().__init__(agent_id, name, message_broker)
        self.disaster_context = disaster_context
        self.data_sources = {}
        self.predictions = {}
    
    def process_message(self, message: Dict[str, Any]) -> None:
        content = message["content"]
        if content.get("type") == "request_area_assessment":
            area_assessment = self.assess_affected_areas(content["disaster_type"], content["location"])
            self.send_message(message["from"], {"type": "need_assessment", "area_data": area_assessment})
        elif content.get("type") == "new_data":
            self.process_new_data(content["source"], content["data"])
    
    def process_new_data(self, source: str, data: Dict[str, Any]) -> None:
        if source not in self.data_sources:
            self.data_sources[source] = []
        self.data_sources[source].append({"timestamp": datetime.now().isoformat(), "data": data})
        self.logger.info(f"New {source} data received")
        if self.detect_significant_change(source, data):
            prediction = self.generate_prediction({"source": source})
            if prediction["risk_level"] >= 7:
                self.send_alert(prediction)
    
    def detect_significant_change(self, source: str, data: Dict[str, Any]) -> bool:
        if source == "weather" and data.get("wind_speed", 0) > 50:
            return True
        return False
    
    def generate_prediction(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        source = parameters.get("source", "all")
        if source == "weather":
            recent_data = self.get_recent_data("weather", 5)
            avg_wind_speed = sum(d["data"].get("wind_speed", 0) for d in recent_data) / max(len(recent_data), 1)
            avg_rainfall = sum(d["data"].get("rainfall", 0) for d in recent_data) / max(len(recent_data), 1)
            prediction = {
                "id": f"pred_{int(time.time())}",
                "type": "weather_impact",
                "risk_level": min(10, int(avg_wind_speed / 10)),
                "areas_affected": ["Area A", "Area B"],
                "recommended_actions": ["Evacuate high-risk areas", "Deploy additional rescue teams"]
            }
        else:
            prediction = {"id": f"pred_{int(time.time())}", "type": "general", "risk_level": self.disaster_context.severity, "areas_affected": [], "recommended_actions": []}
        self.predictions[prediction["id"]] = prediction
        self.logger.info(f"Generated prediction: Risk level {prediction['risk_level']}")
        return prediction
    
    def get_recent_data(self, source: str, count: int) -> List[Dict[str, Any]]:
        if source not in self.data_sources or not self.data_sources[source]:
            return []
        all_source_data = sorted(self.data_sources[source], key=lambda x: datetime.fromisoformat(x.get("timestamp", "1970-01-01T00:00:00")), reverse=True)
        return all_source_data[:min(count, len(all_source_data))]
    
    def assess_affected_areas(self, disaster_type: str, location: str) -> List[Dict[str, Any]]:
        areas = [
            {"name": f"{location}_Area_{i}", "severity": random.randint(1, 10), "population": random.randint(100, 10000), "needs": ["food", "water", "medical_supplies"]}
            for i in range(1, 4)
        ]
        self.logger.info(f"Assessed {len(areas)} affected areas")
        return areas
    
    def send_alert(self, prediction: Dict[str, Any]) -> None:
        self.send_message("communication", {
            "type": "alert",
            "alert_type": prediction["type"],
            "message": f"High risk detected: {prediction['risk_level']}/10",
            "areas_affected": prediction["areas_affected"],
            "recommended_actions": prediction["recommended_actions"]
        })
    
    def run(self) -> None:
        self.logger.info(f"{self.name} started")


# Main execution
def main():
    message_broker = MessageBroker()
    disaster_context = DisasterContext("earthquake", "Los Angeles", 8)
    
    relief_coordinator = ReliefCoordinatorAgent("relief_coordinator", "Relief Coordinator", disaster_context, message_broker)
    volunteer_coordinator = VolunteerCoordinationAgent("volunteer_coordinator", "Volunteer Coordinator", disaster_context, message_broker)
    communication = CommunicationAgent("communication", "Communication Agent", disaster_context, message_broker)
    analytics = AnalyticsPredictionAgent("analytics", "Analytics Agent", disaster_context, message_broker)
    
    message_broker.subscribe("relief_coordinator", relief_coordinator.receive_message)
    message_broker.subscribe("volunteer_coordinator", volunteer_coordinator.receive_message)
    message_broker.subscribe("communication", communication.receive_message)
    message_broker.subscribe("analytics", analytics.receive_message)
    
    logger.info("System initialized")
    relief_coordinator.run()
    volunteer_coordinator.run()
    communication.run()
    analytics.run()
    
    communication.send_message("analytics", {"type": "new_data", "source": "weather", "data": {"wind_speed": 60, "rainfall": 5}})
    logger.info("Simulation completed")

if __name__ == "__main__":
    main()