import math
import numpy as np

# Import API call functions
from ORSrequests import directions, matrix

# Function to split the matrix if over N locations
# Input is a list of long, lat lists

# Max number of locations per API request
N = 50


def route(locations: list, api_key: str, mot: str):
    coordinates = []

    if locations == []:
        return coordinates
    else:
        # If there are more than N locations, multiple API requests have to be created and combined
        if len(locations) > N:
            for i in range(math.ceil(len(locations) / N)):
                begin = i * N
                end = min(N * (i+1), len(locations))
                api_result = directions(api_key, locations[begin:end])
                # If the route back to the depot is left
                if end-begin == 1:
                    api_result = directions(
                        api_key, locations[(begin-1):end], mot)

                # If api_result is not empty, append it otherwise add an empty list.
                if api_result:
                    coordinates = coordinates + api_result
                else:
                    coordinates = coordinates + []
        else:
            api_result = directions(api_key, locations, mot)
            if api_result == []:
                return []
            else:
                coordinates = coordinates + api_result

        return coordinates

# TODO set max of 300 locations due to routing and matrix calls per minute


def distancematrix(locations: list, api_key: str, mot: str):
    # List with indexes of locations
    locations_indexes = list(range(len(locations)))

    # If there are more than N locations, multiple API requests have to be created and combined
    if len(locations) > N:
        # Initilize empty distance matrix
        distance_matrix = np.empty((0, len(locations)), int)
        # Initialize empty array with size (0, length locations) to store whole distance matrix
        rows_cols = math.ceil(len(locations) / N)
        for row in range(rows_cols):
            # Initialize empty array of size (N, 0) to store distances
            rows_size = N if (
                (row + 1) * N) <= len(locations) else (len(locations) - (N * row))
            rows = np.empty((rows_size, 0), int)
            for col in range(rows_cols):
                # if the row number is equal to column number, the source and destinations are the same
                if row == col:
                    # Start is the first element in row N (column = row)
                    start = int(row * N)
                    # End is minimum of the first element of the N+1th row and the length of locations (in case this is the last row)
                    end = int(min((row + 1) * N, len(locations)))
                    source = locations_indexes[start:end]
                    dest = locations_indexes[start:end]
                # if the row number is not equal to the column, source and destinations are different
                else:
                    # Start is the first element in row N
                    row_start = row*N
                    # End is minimum of the first element of the N+1th row and the length of locations (in case this is the last row)
                    row_end = min(row * N + N, len(locations))
                    # Sources are the locations from start of the row til end of the row
                    source = locations_indexes[row_start:row_end]
                    # Start is the first element in column N
                    col_start = col*N
                    # End is minimum of the first element of the N+1th column and the length of locations (in case this is the last column)
                    col_end = min(col * N + N, len(locations))
                    # Destinations are the locations from start of the column till end of the column
                    dest = locations_indexes[col_start:col_end]

                # Call ORS Matrix API function with specific sources and destinations
                api_result = matrix(api_key, locations, source, dest, mot)
                # Select the distances of the API results, convert to np.array, round and change to int and convert back to list
                api_result = np.round(np.array(api_result["distances"]).astype(
                    np.double), 0).astype(int).tolist()

                # Append results of current matrix to the row
                rows = np.append(rows, api_result, axis=1)
            distance_matrix = np.append(distance_matrix, rows, axis=0)
    else:
        # Call ORS Matrix API function with all locations as sources and destinations
        api_result = matrix(
            api_key, locations, locations_indexes, locations_indexes, mot)
        print("api_result", api_result)
        # Select the distances of the API results, convert to np.array, round and change to int and convert back to list
        distance_matrix = np.round(np.array(api_result["distances"]).astype(
            np.double), 0).astype(int).tolist()

    return distance_matrix
