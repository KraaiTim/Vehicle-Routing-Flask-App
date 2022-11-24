"""Simple Vehicles Routing Problem (VRP).

   This is a sample using the routing library python wrapper to solve a VRP
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters.
"""

import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

real_dm = [[0, 36, 436, 934, 917, 1295, 634, 1299, 2541, 1964, 2490, 2331, 1649],
           [43, 0, 466, 909, 892, 1298, 668, 1266, 2545, 1938, 2493, 2449, 1616],
           [436, 456, 0, 1319, 1271, 1629, 459, 1916, 3009, 2476, 2824, 2004, 2075],
           [949, 915, 1338, 0, 32, 829, 1397, 1356, 1759, 1298, 1731, 1959, 1873],
           [910, 876, 1268, 27, 0, 824, 1359, 1362, 1754, 1318, 1726, 1954, 1879],
           [1298, 1298, 1617, 828, 828, 0, 1838,
               2125, 1235, 2062, 1280, 1438, 2616],
           [643, 631, 461, 1390, 1373, 1857, 0, 1544, 3448, 2420, 3024, 2442, 1671],
           [1268, 1234, 1917, 1340, 1371, 2117,
               1543, 0, 3047, 950, 3019, 3532, 742],
           [2541, 2541, 3031, 1759, 1759, 1204, 3031,
               3056, 0, 2993, 1363, 1424, 3573],
           [1972, 1938, 2471, 1208, 1241, 1972,
               2420, 953, 2902, 0, 2654, 3102, 1546],
           [2481, 2508, 2800, 1719, 1719, 1259, 2991,
               3016, 1348, 2664, 0, 2202, 3533],
           [2336, 2453, 2004, 1953, 1953, 1440, 2451,
               3296, 1425, 3188, 2213, 0, 3708],
           [1626, 1592, 2232, 1859, 1890, 2636, 1840, 720, 3566, 1531, 3538, 3868, 0]]

google_dm = [
    [
        0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354,
        468, 776, 662
    ],
    [
        548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674,
        1016, 868, 1210
    ],
    [
        776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164,
        1130, 788, 1552, 754
    ],
    [
        696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822,
        1164, 560, 1358
    ],
    [
        582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708,
        1050, 674, 1244
    ],
    [
        274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628,
        514, 1050, 708
    ],
    [
        502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856,
        514, 1278, 480
    ],
    [
        194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320,
        662, 742, 856
    ],
    [
        308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662,
        320, 1084, 514
    ],
    [
        194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388,
        274, 810, 468
    ],
    [
        536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764,
        730, 388, 1152, 354
    ],
    [
        502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114,
        308, 650, 274, 844
    ],
    [
        388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194,
        536, 388, 730
    ],
    [
        354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0,
        342, 422, 536
    ],
    [
        468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536,
        342, 0, 764, 194
    ],
    [
        776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274,
        388, 422, 764, 0, 798
    ],
    [
        662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730,
        536, 194, 798, 0
    ],
]


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = real_dm
    data['num_vehicles'] = 1
    data['depot'] = 0

    data['distance_matrix'] = np.array(data['distance_matrix']).astype(int)
    return data


penalty = 100


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    dropped_nodes = 'Dropped nodes:'
    dropped_cost = 0
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if solution.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}'.format(manager.IndexToNode(node))
            dropped_cost += penalty
    print(f'Dropped cost: {dropped_cost}')
    print(dropped_nodes)
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    # distance_dimension = routing.GetDimensionOrDie(dimension_name)
    # distance_dimension.SetGlobalSpanCostCoefficient(100)

    for node in range(1, len(data['distance_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print('No solution found !')


if __name__ == '__main__':
    main()
