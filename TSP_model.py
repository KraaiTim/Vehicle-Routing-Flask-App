# Import solver from Google OR-Tools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Import Distance matrix function
from distance_matrix import distancematrix

# Data for TSP model
# Using Google OR-Tools https://developers.google.com/optimization/routing/tsp


def TSPmodel(locations, api_key, num_vehicles=1):

    def create_data_model(locs: list):
        """Stores the distance matrix, depot and number of vehicles."""
        data = {}
        # Call distance matrix function on locations
        data['distance_matrix'] = distancematrix(locs, api_key)
        data['num_vehicles'] = num_vehicles
        data['depot'] = 0
        return data

    # Set up model
    # Instantiate the data problem.
    data = create_data_model(locations)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Function to determine the distance between locations
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    distance_callback_index = routing.RegisterTransitCallback(
        distance_callback)

    # Cost of travel
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        distance_callback_index,
        0,  # no slack
        3000000,  # vehicle maximum travel distance in meters
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Search parameters and heuristic for initial solution
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solution printer
    def print_solution(data, manager, routing, solution):
        """Prints solution on console."""
        # Divide by 1000 to covert from m to km
        print(f'Objective: {solution.ObjectiveValue() / 1000} km')
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
            plan_output += 'Distance of the route: {}m\n'.format(
                route_distance)
            print(plan_output)
            max_route_distance = max(route_distance, max_route_distance)

            print('Maximum of the route distances: {}m'.format(max_route_distance))

    # Solve and print solution
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print('No solution found !')

    # Route function
    def get_routes(solution, routing, manager):
        """Get vehicle routes from a solution and store them in an array."""
        # Get vehicle routes and store them in a two dimensional array whose
        # i,j entry is the jth location visited by vehicle i along its route.
        routes = []
        for route_nbr in range(routing.vehicles()):
            index = routing.Start(route_nbr)
            route = [manager.IndexToNode(index)]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
            routes.append(route)
        return routes

    # Display route
    routes = get_routes(solution, routing, manager)

    # Display the routes.
    for i, route in enumerate(routes):
        print('Route', i, route)

    return routes
