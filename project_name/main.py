import unittest
from efrei2025.project_name.data_structures import Stop, ZoneType
from efrei2025.project_name.network import TransportNetwork
from efrei2025.project_name.test_transport_network import TestStop, TestTransportNetwork

def main():
    # 1. Create a transport network
    network = TransportNetwork()

    # 2. Create and add stops
    stop1 = Stop("S1", "Central", 48.85, 2.35, ZoneType.COMMERCIAL)
    stop2 = Stop("S2", "Suburb", 48.80, 2.30, ZoneType.RESIDENTIAL)
    stop3 = Stop("S3", "Industrial Park", 48.90, 2.40, ZoneType.INDUSTRIAL)
    stop4 = Stop("S4", "Downtown", 48.86, 2.34, ZoneType.MIXED)


    network.add_stop(stop1)
    network.add_stop(stop2)
    network.add_stop(stop3)
    network.add_stop(stop4)

    # 3. Add routes
    network.add_route(stop1, stop2, 10.5)
    network.add_route(stop1, stop4, 5.2)
    network.add_route(stop2, stop3, 15.0)
    network.add_route(stop4, stop3, 8.8)
    network.add_route(stop4, stop1, 5.0)


    # 4. Display network structure
    print("--- Transport Network ---")
    print(f"Stops: {len(network.stops)}")
    for stop in network.stops:
        print(f"- {stop}")

    print("\nRoutes:")
    for start_stop, connections in network.routes.items():
        if connections:
            print(f"From {start_stop.name}:")
            for end_stop, distance in connections:
                print(f"  -> {end_stop.name} (Distance: {distance} km)")
    print("------------------------\n")

    # 5. Run unit tests
    print("--- Running Unit Tests ---")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStop))
    suite.addTest(unittest.makeSuite(TestTransportNetwork))
    
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    print("------------------------")
    
    return result

if __name__ == '__main__':
    main() 