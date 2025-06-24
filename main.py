from project_name.network import TransportNetwork
from project_name.io import load_stops_from_csv, load_routes_from_csv
from project_name.algorithms import find_all_paths

def main():
    """
    Main function to run the transport network analysis.
    """
    # Create a transport network
    network = TransportNetwork()

    # Load data from CSV files
    # Make sure the data files are in a 'data' directory relative to where this script is run
    try:
        load_stops_from_csv(network, 'data/stops.csv')
        load_routes_from_csv(network, 'data/routes.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure you are running this from the 'efrei2025' directory and the 'data' directory exists.")
        return

    # Define start and end points
    start_stop_id = 2
    end_stop_id = 7

    # Find all paths between start and end points
    all_paths = find_all_paths(network, start_stop_id, end_stop_id)

    # Print the results
    if not all_paths:
        print(f"No path found from stop {start_stop_id} to {end_stop_id}.")
        return

    # Find the shortest distance among all paths
    min_distance = min(dist for _, dist in all_paths)

    print(f"All paths from stop {start_stop_id} to {end_stop_id}:")
    for path, dist in all_paths:
        # Add a marker for the shortest path
        mark = " <--- shortest" if abs(dist - min_distance) < 1e-9 else ""
        print(f"Path: {path}, Distance: {dist:.2f}{mark}")

if __name__ == '__main__':
    main()
