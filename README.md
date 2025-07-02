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
## 3. The overall design

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

### 3.2 analysis 分析包

- **network_path_analyzer.py**
  - 设计了路径分析器，结合图结构与算法输出，便于综合分析多条路径。
  - Implements a path analyzer that integrates graph structure and algorithm outputs for comprehensive multi-path analysis.

- **stop_utilization_analyzer.py**
  - 采用字典统计站点利用率和停靠时长，结构简单高效，便于后续可视化和优化建议。
  - Uses dictionaries to count stop utilization and dwell times, providing a simple and efficient structure for visualization and optimization.

### 3.3 core 核心包

- **csv_network_data_manager.py**
  - 采用面向对象方式管理CSV数据，内部用邻接表（字典+列表）存储网络结构，便于高效查找和遍历。
  - Manages CSV data in an object-oriented way, using adjacency lists (dict + list) to store the network structure for efficient lookup and traversal.

### 3.4 data_structures 数据结构包

- **stop_entity.py**
  - 设计了站点实体类，封装站点属性（ID、类型、坐标等），便于统一管理和扩展。
  - Defines a stop entity class encapsulating stop attributes (ID, type, coordinates, etc.) for unified management and extensibility.

- **transport_network_structure.py**
  - 采用邻接表（字典嵌套）实现有向图结构，支持高效的增删查改和遍历操作，是路径算法的基础。
  - Implements a directed graph using adjacency lists (nested dictionaries), supporting efficient add/delete/search/traverse operations, serving as the foundation for path algorithms.

### 3.5 gui 图形界面包

- **interactive_graphics_view.py**
  - 设计自定义视图类，采用面向对象方式管理图形元素，便于实现交互和动态更新。
  - Custom graphics view class using OOP to manage graphical elements for interactive and dynamic updates.

- **main_window_gui_builder.py**
  - 采用模块化设计，分离主窗口与各功能组件，提升可维护性和扩展性。
  - Modular design separates main window and functional components, improving maintainability and extensibility.

- **network_visualization_drawing.py**
  - 采用图形项列表和字典管理可视化元素，便于高效渲染和状态同步。
  - Manages visualization elements with lists and dictionaries for efficient rendering and state synchronization.

- **path_analysis_result_display.py**
  - 设计结果展示面板，采用表格和列表结构，便于多路径对比。
  - Result display panel uses tables and lists for easy multi-path comparison.

- **station_interaction_event_handler.py**
  - 事件处理采用信号与槽机制，结构清晰，便于扩展。
  - Event handling uses signal-slot mechanism for clear structure and easy extension.

- **stop_and_route_dialogs_gui.py**
  - 采用对话框类封装数据输入，提升用户体验。
  - Dialog classes encapsulate data input for better user experience.

- **stop_utilization_display.py**
  - 采用图表结构展示站点利用率，便于直观分析。
  - Uses chart structures to display stop utilization for intuitive analysis.

- **traffic_period_selector.py**
  - 采用下拉菜单和字典映射实现时段选择，结构简洁。
  - Dropdown menus and dictionary mapping for time period selection, with simple structure.

### 3.6 analysis 数据分析包

- **network_path_analyzer.py**、**stop_utilization_analyzer.py**
  - 见上文，均采用字典、列表等高效结构，便于统计和分析。
  - See above; both use efficient structures like dictionaries and lists for statistics and analysis.

> 以上设计均以高效、可扩展、易维护为目标，充分利用Python内置数据结构（如列表、字典、堆）和面向对象思想，确保系统在大规模数据下依然具备良好性能和可读性。

All designs aim for efficiency, scalability, and maintainability, leveraging Python's built-in data structures (lists, dicts, heaps) and OOP principles to ensure good performance and readability even with large-scale data.

## 4.Implementation
## 5.Project results
## 6.Division of the project

*   **Wang Tianyi**: Responsible for designing data structures and algorithms, writing the majority of code including algorithms, unit tests, frontend, and the main program. Collaborates on reports and presentations, and assigns tasks to others.
*   **Dong Che**: Primarily responsible for writing frontend interface code, designing test cases, conducting coverage testing, and collaborating on algorithm design and analysis. Also collaborates on reports and presentations.
*   **Shao Liangyu**: Tasked with researching algorithms and primarily responsible for writing reports and presentations.

## 7.Summary of the experiment
