# Multi-Agent Disaster Response System
The Multi-Agent Disaster Response System is a Python-based simulation designed to demonstrate how multiple autonomous agents can collaborate to manage disaster scenarios effectively. The system leverages a message-passing architecture to coordinate efforts among agents, each with specialized roles, to enhance disaster response effectiveness, optimize resource allocation, support victim communication, and provide predictive measures to minimize damage.
### Agents
- Relief Coordinator Agent: Optimizes the distribution of relief resources (e.g., food, water, medical supplies) based on real-time need assessments and disaster severity.
- Volunteer Coordination Agent: Organizes and directs volunteer efforts, assigning tasks based on skills and urgency.
- Communication Agent: Facilitates rapid and clear communication between victims and rescue teams, prioritizing rescue efforts.
- Analytics & Prediction Agent: Analyzes data (e.g., weather, seismic activity) to predict disaster impacts and recommend proactive measures.
-### Potential Impact
- Enhance disaster response effectiveness through coordinated agent actions.
- Improve resource allocation by dynamically responding to assessed needs.
- Support victim communication by bridging information between victims and responders.
- Offer predictive measures to anticipate and mitigate disaster impacts.

## Prerequisites
- Python: Version 3.7 or higher
- Operating System: Windows, macOS, or Linux
- Dependencies: No external libraries are required beyond the Python standard library.

## Installation
1. Clone or Download the Repository:
If using Git:
- git clone <repository-url>
- cd multi-agent-disaster-response-system
- Alternatively, download the source code as a ZIP file and extract it.
- Verify Python Installation:
- Ensure Python is installed by running:
- python --version
- If not installed, download it from python.org.
- No Additional Dependencies:
- The project uses only the Python standard library (logging, random, time, datetime, typing, abc).

## Usage
1. Save the Code:
- Copy the provided Python script into a file named main.py in your project directory.
- Run the Simulation:
- Open a terminal in the project directory and execute:
- python main.py
2. Understand the Output:
- The system logs key events to the console using the logging module. Example output:
- disaster_response_system - INFO - System initialized
- disaster_response_system.relief_coordinator - INFO - Relief Coordinator started
- disaster_response_system.relief_coordinator - INFO - Resources initialized: {'food': 1000, 'water': 5000, ...}
- disaster_response_system.analytics - INFO - Assessed 3 affected areas
- disaster_response_system.volunteer_coordinator - INFO - Assigned Distribute 454 food to Los Angeles_Area_3 to volunteer vol_3
- disaster_response_system.analytics - INFO - Generated prediction: Risk level 10
- disaster_response_system.communication - INFO - Broadcasted weather_impact alert
- disaster_response_system - INFO - Simulation completed

- Logs show agent actions like resource allocation, task assignments, and alerts.

3. Customize the Simulation:
- Modify the main() function in main.py to simulate different scenarios (e.g., change disaster type, location, or data inputs).
- Example: Add a victim request:
- communication.send_message("communication", {"type": "victim_request", "id": "v1", "location": {"lat": 34.05, "lon": -118.24}, "description": "Trapped, need medical help", "reported_urgency": 8})

## Project Structure
- main.py: The main script containing all agent classes, the message broker, and the simulation logic.
- No additional files are required for this basic implementation.

## How It Works
- Initialization:
- A MessageBroker facilitates communication between agents.
- A DisasterContext stores shared disaster information (e.g., type, location, severity).
- Agent Collaboration:
- Relief Coordinator: Requests area assessments, allocates resources, and sends plans to the Volunteer Coordinator.
- Volunteer Coordinator: Registers volunteers, generates tasks from allocation plans, and assigns them based on skills.
- Communication: Manages rescue team locations, processes victim requests, and broadcasts alerts.
- Analytics: Analyzes data, predicts impacts, and sends proactive alerts.
- Simulation:
- The main() function sets up agents, subscribes them to the message broker, and runs a test scenario (e.g., an earthquake in Los Angeles with weather data).

## License
- This project is unlicensed and provided as-is for educational and demonstration purposes. You are free to use, modify, and distribute it as needed.

