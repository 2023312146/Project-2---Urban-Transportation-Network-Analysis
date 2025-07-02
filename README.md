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

#### Features

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

## 2.Quick Start
### 2.1 Project Structure

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
### 2.2 Prerequisites

- Python 3.7+
- PyQt5

### 2.3 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd efrei2025
```

2. Install required dependencies:
```bash
pip install PyQt5
```

### 2.4 Running the Analysis

To start the transport network analysis application:

```bash
python main.py
```

The application will open with a graphical interface showing:
- A control panel on the left with various network management options
- A main visualization area showing the transport network
- Color-coded stations based on zone types
- Interactive path finding capabilities

### 2.5 Running Tests

To run the test suite:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m pytest tests/test_algorithms.py
python -m pytest tests/test_network.py
```
## 3. The Overall Design

This section presents the overall architecture, detailing the design ideas, rationale, and advantages of key algorithms and data structures in each package and file under /project. 

### 3.1 Algorithm packages

- **coordinate_utils.py**
  - Designed utility functions for coordinate transformation and distance calculation, using basic math and vector operations for easy reuse in path algorithms.

- **dfs_all_paths_algorithm.py**
  - Implements Depth-First Search (DFS) using stack to enumerate all possible paths. Each stack element holds the current node, path, and cumulative distance, so that paths that cannot be reached or exceed the maximum distance can be ejected in time. DFS is suitable for path enumeration, and stack structure makes it easy to backtrack the state when the maximum distance is exceeded.

- **dijkstra_shortest_path_algorithm.py**
  - Implements Dijkstra's algorithm using a priority queue (min-heap via heapq). At each step, the node with the smallest distance is extracted from the heap, ensuring optimal path expansion. Distances and predecessors are stored in dictionaries for easy path reconstruction and distance updates. The heap structure greatly improves efficiency.

- **path_efficiency_analysis.py**
  - An efficiency analysis method was designed to combine distance and time to evaluate the advantages and disadvantages of the shortest path.

- **traffic_condition_manager.py**
  - Manages traffic conditions for peak-hour simulation, using dictionaries to map time periods to traffic factors for dynamic adjustment.

### 3.2 Analysis Package

- **network_path_analyzer.py**
  - The path analyzer is designed, which combines the graph structure and dictionary, which is convenient for the comprehensive analysis of multiple paths, the shortest path and the most efficient path, and the point with the highest centrality.

- **stop_utilization_analyzer.py**
  - The dictionary is used to count the site utilization rate and stop time during peak periods, including the analysis and calculation of the utilization rate, which is simple and efficient, and is convenient for subsequent visualization and optimization suggestions.

### 3.3 Core Package

- **csv_network_data_manager.py**
  - Manages CSV data in an object-oriented way. Contains a method for reading underlying stop and route information from a CSV file, using adjacency lists (dict + list) to store the network structure for efficient lookup.

### 3.4 Data_structures Package

- **stop_entity.py**
  - Defines a stop entity class encapsulating stop attributes (ID, type, coordinates, etc.) for unified management and extensibility.A comparison of stop information is also provided

- **transport_network_structure.py**
  - Implements a directed graph using adjacency lists (nested dictionaries), supporting efficient add/delete/search/traverse operations, serving as the foundation for path algorithms.

### 3.5 Gui Package

- **interactive_graphics_view.py**
  - Design custom view classes to manage graphical elements in an object-oriented manner for easy interaction and dynamic updates.

- **main_window_gui_builder.py**
  - Modular design separates main window and functional components, improving maintainability and extensibility.

- **network_visualization_drawing.py**
  - Manages visualization elements with lists and dictionaries for efficient rendering and state synchronization.

- **path_analysis_result_display.py**
  - Result display panel uses tables and lists for easy multi-path comparison.

- **station_interaction_event_handler.py**
  - Implements an event handler class to manage all user interactions with stations, such as hover, click, add, and remove. Uses object-oriented design to encapsulate interaction logic. Provides real-time feedback (e.g., tooltips, selection, info panel updates).

- **stop_and_route_dialogs_gui.py**
  - Dialog classes encapsulate data input for better user experience.

- **stop_utilization_display.py**
  - Uses chart structures to display stop utilization for intuitive analysis.

- **traffic_period_selector.py**
  - Dropdown menus and dictionary mapping for time period selection, with simple structure.

All designs aim for efficiency, scalability, and maintainability, leveraging Python's built-in data structures (lists, dicts, heaps) to ensure good performance.

## 4.Implementation
## 5.Project results

### 5.1 Main Interface

![Main Interface](report_pic/Main%20interface.png)

The main interface of the Bus Network Path Planning System provides an intuitive and interactive visualization of the urban transport network. Users can manage stops and connections, analyze paths, and view real-time information through a user-friendly GUI.

### 5.2 Route Recommendation

<div align="center">
    <img src="report_pic/Route%20Recommendation-1.png">
</div>

<div align="center">
    <img src="report_pic/Route%20Recommendation-2.png">
</div>

<div align="center">
    <img src="report_pic/Route%20Recommendation-3.png">
</div>

The system provides comprehensive route recommendation and analysis features. When a user selects a start and end stop, the system enumerates all reachable paths (within a maximum distance of 80km; paths exceeding this threshold are excluded even if technically reachable). For each query, the shortest path (red) and the most efficient path (green, considering both distance and time) are highlighted and compared. All possible paths, their distances, and efficiency metrics are listed for user reference. This is a visual representation of "the shortest path is not the most efficient path", and supports informed decision-making for urban transit planning.

### 5.3 Stop management
This system supports flexible management of stops in the bus network, including adding, removing, and updating stop types, greatly enhancing the flexibility of network modeling and user experience.

#### 5.3.1 Add Stop
<div align="center">
    <img src="report_pic/Add%20stop-1.png">
</div>
<div align="center">
    <img src="report_pic/Add%20stop-2.png">
</div>

- Users can enter add mode by clicking the "Add Station" button, then click any blank area on the main interface to pop up a dialog, input the stop name and select the type (Residential, Commercial, Industrial, Mixed). The system automatically assigns the wait time.
- In the code, `station_interaction_event_handler.py` handles click events, dialog input, and data validation to ensure new stops do not overlap with existing ones.

#### 5.3.2 Remove Stop
- After clicking the "Remove Station" button, users can remove a stop by clicking on it; related connections are updated automatically.
- The code detects the click position via the event handler, calls the data manager to remove the stop and its edges, and refreshes the interface.

#### 5.3.3 Update Stop Type
<div align="center">
    <img src="report_pic/Update%20stop%20type-1.png">
</div>
<div align="center">
    <img src="report_pic/Update%20stop%20type-2.png">
</div>
<div align="center">
    <img src="report_pic/Update%20stop%20type-3.png">
</div>

- Users can update the type of any stop via the "Update Station Type" button; the system automatically adjusts its wait time and visualization color.
- The relevant code obtains user selection via dialog, updates stop attributes, and reflects changes in the network graph in real time.

### 5.4 Connection management / 连接管理

This system supports flexible management of connections between stops in the bus network, including adding and removing connections, making it easy to dynamically adjust the network structure as needed.

#### 5.4.1 Add Connection / 添加连接
<div align="center">
    <img src="report_pic/Add%20connection-1.png">
</div>

- After clicking the "Add Connection" button, users select the start and end stops in sequence. A dialog pops up to input distance and other information, and a directed edge is added to the network upon confirmation.
- The code captures user selections via the event handler, updates the adjacency list in the data manager, and refreshes the visualization.

#### 5.4.2 Remove Connection / 删除连接
<div align="center">
    <img src="report_pic/Remove%20connection-2.png">
</div>
<div align="center">
    <img src="report_pic/Remove%20connection-1.png">
</div>

- After clicking the "Remove Connection" button, users select the start and end stops to disconnect, and the system automatically removes the corresponding directed edge.
- The event handler recognizes user actions, the data manager updates the adjacency list, and the interface is synchronized.










## 6.Division of the project

*   **Tianyi Wang**: Responsible for designing data structures and algorithms, writing the majority of code including algorithms, unit tests, frontend, and the main program. Collaborates on reports and presentations, and assigns tasks to others.
*   **Che Dong**: Primarily responsible for writing frontend interface code, designing test cases, conducting coverage testing, and collaborating on algorithm design and analysis. Also collaborates on reports and presentations.
*   **Liangyu Shao**: Tasked with researching algorithms and primarily responsible for writing reports and presentations.
*   **Yixiao Wang**:Actually I don't konw...

## 7.Summary of the experiment
