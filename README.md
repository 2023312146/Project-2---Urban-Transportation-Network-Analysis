## 1. Description of Project
### 1.1 Project Introduction

This project develops an urban bus network analysis system: modeling stops (nodes) and routes (directed edges) via graph theory to enable dynamic network construction, multi-route travel time prediction (weighted by zone types), Dijkstra's shortest path algorithm, and route efficiency optimization (Efficiency=Distance/Time). Key innovation validates "shortest path ≠ most efficient path", with extensions for peak-hour traffic simulation and stop utilization analytics, delivering a decision-making tool for smart transit.

### 1.2 Design Requirements & Analysis  
This project aims to develop an urban bus network analysis system to meet the following core requirements:
1. **Dynamic Network Modeling & Management**  
   - Support dynamic construction of the bus network using graph theory, with stops as nodes and routes as edges. The system allows flexible addition, deletion, and modification of stops and routes to adapt to real-world network changes.
2. **Multi-path & Efficiency Analysis**  
   - Implements multiple path-finding algorithms (e.g., Dijkstra's shortest path, DFS all paths), enabling not only shortest path calculation but also efficiency analysis (Efficiency = Distance/Time), validating that "shortest path ≠ most efficient path" in practice.
3. **Zoning & Peak-hour Simulation**   
   - Stops are categorized (residential, commercial, industrial, mixed), each with different waiting times. The system supports peak-hour traffic simulation to analyze the impact of congestion on path selection and efficiency.
4. **Visualization & Interactive Experience**   
   - Provides an intuitive, interactive graphical interface for real-time display of the network structure, paths, and stop types, facilitating user operation and decision-making.
5. **Data Analysis & Optimization Suggestions**   
   - Supports stop utilization analysis, dwell time statistics, and route optimization suggestions to assist in system optimization and management decisions.
6. **Scalability & Real-time Capability**  
   - The architecture supports large-scale networks (millions of stops and routes) and can integrate real-time bus data for future expansion and practical application needs.

## Features

- **Interactive Network Visualization**: Real-time graphical representation of transport networks with stations and connections
- **Multiple Path Finding Algorithms**: 
  - Dijkstra's algorithm for shortest path calculation
  - DFS for alternative path exploration
- **Network Management**: Add, remove, and modify stations and connections
- **Zone-based Analysis**: Different station types (Residential, Commercial, Industrial, Mixed) with varying wait times
- **Efficiency Analysis**: Compare different path options based on distance and efficiency metrics
- **User-friendly GUI**: Intuitive interface with color-coded visualizations and interactive controls
- **Dynamic Path Visualization**: Show travel time and distance on selected path
- **Path Comparison**: Highlight and compare multiple paths for optimal selection
- **Peak-Hour Simulation**: Extend path analysis to simulate traffic congestion
- **Stop Utilization Insights**: Analyze and visualize stop dwell times and frequencies
- **Route Optimization**: Suggest modifications to existing routes based on travel demand
- **Scalability**: Handle large networks with millions of stops and routes

## Project Structure

```
efrei2025/
├── main.py                          # Main application entry point
├── data/                            # Data files directory
│   ├── urban_transport_network_routes.csv
│   └── urban_transport_network_stops.csv
├── project/                         # Main project package
│   ├── algorithms/                  # Path finding algorithms
│   │   ├── __init__.py
│   │   ├── dijkstra.py             # Dijkstra's shortest path algorithm
│   │   └── dfs.py                  # Depth-First Search algorithm
│   └── module/                     # Core application modules
│       ├── __init__.py
│       ├── NetworkDataManager.py   # Data management and network operations
│       ├── gui_builder.py          # Main GUI window and layout
│       ├── custom_view.py          # Custom graphics view for network display
│       ├── drawing_module.py       # Network visualization and drawing
│       ├── interaction_handler.py  # User interaction handling
│       ├── path_display.py         # Path information display
│       ├── data_dialogs.py         # Dialog boxes for data input
│       ├── RouteAnalyzer.py        # Path analysis and optimization
│       ├── network.py              # Network data structures
│       └── stop.py                 # Stop/station class definitions
├── tests/                          # Test suite
│   ├── test_algorithms.py
│   ├── test_csv.py
│   ├── test_custom_view.py
│   ├── test_data_dialogs.py
│   ├── test_drawing_module.py
│   ├── test_gui_builder.py
│   ├── test_interaction_handler.py
│   ├── test_network_data_manager.py
│   ├── test_network.py
│   ├── test_path_display.py
│   ├── test_route_analyzer.py
│   └── test_stop.py
└── README.md                       # Project documentation
```

## Quick Start

### Prerequisites

- Python 3.7+
- PyQt5

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd efrei2025
```

2. Install required dependencies:
```bash
pip install PyQt5
```

### Running the Analysis

To start the transport network analysis application:

```bash
python main.py
```

The application will open with a graphical interface showing:
- A control panel on the left with various network management options
- A main visualization area showing the transport network
- Color-coded stations based on zone types
- Interactive path finding capabilities

### Running Tests

To run the test suite:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m pytest tests/test_algorithms.py
python -m pytest tests/test_network.py
```
### Project Division

*   **Wang Tianyi**: Responsible for designing data structures and algorithms, writing the majority of code including algorithms, unit tests, frontend, and the main program. Collaborates on reports and presentations, and assigns tasks to others.
*   **Dong Che**: Primarily responsible for writing frontend interface code, designing test cases, conducting coverage testing, and collaborating on algorithm design and analysis. Also collaborates on reports and presentations.
*   **Shao Liangyu**: Tasked with researching algorithms and primarily responsible for writing reports and presentations.
