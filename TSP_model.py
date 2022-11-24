# Import solver from Google OR-Tools
import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Import Distance matrix function
from distance_matrix import distancematrix

# Data for TSP model
# Using Google OR-Tools https://developers.google.com/optimization/routing/tsp


def TSPmodel(locations, api_key, objective, num_vehicles, mot, price_km=None, penalty=None):

    def create_data_model(locations: list):
        """Stores the distance matrix, depot and number of vehicles."""
        data = {}
        # Call distance matrix function on locations
        data['distance_matrix'] = distancematrix(
            locations, api_key, objective, mot, price_km)
        data['num_vehicles'] = num_vehicles
        # TODO implement the different start points of vehicles, remove depot
        #data['starts'] = [1, 2, 15, 16]
        #data['ends'] = [0, 0, 0, 0]
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
        3000,  # vehicle maximum capacity
        True,  # start cumul to zero
        dimension_name)

    # Dimension to push the model to create evenly long routes between vehicle. Use for multi vehicle
    # distance_dimension = routing.GetDimensionOrDie(dimension_name)
    # # A large coefficient (100) for the global span of the routes, which is the maximum of the distances of the routes, makes the global span the predominant factor in the objective function, so the program minimizes the length of the longest route.
    # distance_dimension.SetGlobalSpanCostCoefficient(1)

    # If penalty is defined, allow to drop nodes.
    penalty = round(penalty * 1000)
    if penalty:
        for node in range(1, len(data['distance_matrix'])):
            # Multiply the penalty input to scale it like the price per km
            routing.AddDisjunction(
                [manager.NodeToIndex(node)], penalty)

    # Search parameters and heuristic for initial solution
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve and print solution
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print('Solution found!')
    else:
        print('No solution found!')

    def routes_info(solution, routing, manager):
        """Get vehicle routes from a solution and store them in an list of dictionaries."""
        # Get vehicle routes and store them in a dictionary. In the list of dictionaries
        # vehicle i visits location j.
        print(f'Objective: {solution.ObjectiveValue()}')
        dropped_nodes = []
        dropped_cost = 0
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                dropped_nodes.append(manager.IndexToNode(node))
                dropped_cost += penalty
        print(f'Dropped cost: {dropped_cost / 1000}')
        print(dropped_nodes)
        routes = []
        for route_nbr in range(routing.vehicles()):
            route_info = {}
            route_info["id"] = route_nbr
            index = routing.Start(route_nbr)
            route = [manager.IndexToNode(index)]
            route_distance = []
            total_route_distance = 0
            while not routing.IsEnd(index):
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_cost = routing.GetArcCostForVehicle(
                    previous_index, index, route_nbr)
                total_route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, route_nbr)
                route_distance.append(route_cost)
                route.append(manager.IndexToNode(index))
            route_info["route"] = route
            route_info["route_cost"] = route_distance
            route_info["cost"] = total_route_distance
            routes.append(route_info)
        return dropped_nodes, routes

    # Display route
    dropped_nodes, routes = routes_info(solution, routing, manager)

    # Display the routes.
    for i, route in enumerate(routes):
        print('Route', i, route["route"], route["cost"])

    return dropped_nodes, routes
