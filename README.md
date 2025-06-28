# Transport Network Analysis

This project provides a comprehensive Python-based transport network analysis system with a graphical user interface built using PyQt5. The system allows users to visualize, analyze, and optimize transport networks with various algorithms including Dijkstra's shortest path and DFS (Depth-First Search).

## Features

- **Interactive Network Visualization**: Real-time graphical representation of transport networks with stations and connections
- **Multiple Path Finding Algorithms**: 
  - Dijkstra's algorithm for shortest path calculation
  - DFS for alternative path exploration
- **Network Management**: Add, remove, and modify stations and connections
- **Zone-based Analysis**: Different station types (Residential, Commercial, Industrial, Mixed) with varying wait times
- **Efficiency Analysis**: Compare different path options based on distance and efficiency metrics
- **User-friendly GUI**: Intuitive interface with color-coded visualizations and interactive controls

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

