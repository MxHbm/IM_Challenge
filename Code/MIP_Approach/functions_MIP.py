import json
import csv
from typing import List, Dict, Union, Tuple
import math
import sys, os
import gurobipy as gp
from pathlib import Path

# Get the current file's directory
current_dir = os.path.dirname(__file__)

# Go up one level to reach the parent directory of MIP_Approach
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Add the parent directory to sys.path
sys.path.append(parent_dir)

from InputData import OptionalTask, MainTask, InputData


def get_distance_matrix(tasks:list[Union[MainTask, OptionalTask]]) -> list[list[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    distances = [[100000 if i == j else 0 for i in range(len(tasks))] for j in range(len(tasks))]

    print("Calculate Distances")

    for task_i_id in range(len(tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distances[task_i_id][task_j_id] = distances[task_j_id][task_i_id] = calculate_distance(tasks[task_i_id], tasks[task_j_id])

    return distances

def get_service_times(tasks:List[Union[MainTask, OptionalTask]]) -> list[int]:
    ''' List of service times of each task'''

    service_times = [task.service_time for task in tasks]

    return service_times


def get_profits(tasks: List[Union[MainTask, OptionalTask]]) -> list[int]:
    ''' Get the profit of the tasks in the data and add zeros for the depots to run the model'''

    # Fill profits vector
    print("Get Profits")
    profits = [task.profit for task in tasks]

    return profits

def calculate_distance(task_1:Union[MainTask, OptionalTask], task_2:Union[MainTask, OptionalTask]) -> float:
    ''' Calculate the distance between two tasks using the euclidean distance formula
        and return the time it takes to travel between them in seconds
    '''

    distance = math.sqrt((task_1.latitude - task_2.latitude)**2 + (task_1.longitude - task_2.longitude)**2)

    time = int(round(distance * 17100,0)) # time in seconds

    return time

def get_distance_service_time_matrix(tasks:List[Union[MainTask, OptionalTask]]) -> List[List[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    # Add the depot again to the tasks at the end
    internal_tasks = tasks.copy()

    distances_service_time = [[100000 if i == j else 0 for i in range(len(internal_tasks))] for j in range(len(internal_tasks))]

    print("Calculate Distance plus Service Times")

    for task_i_id in range(len(internal_tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distance = calculate_distance(internal_tasks[task_i_id], internal_tasks[task_j_id])
                distances_service_time[task_i_id][task_j_id] =  distance + internal_tasks[task_i_id].service_time
                distances_service_time[task_j_id][task_i_id] =  distance + internal_tasks[task_j_id].service_time

    return distances_service_time


def get_mandatory_end_and_start_times(data:InputData, tasks: List[Union[MainTask, OptionalTask]]) -> Tuple[List[List[int]], List[List[int]]]:
    ''' List of mandatory start times of each task, integrates also factor at which day main tasks can only be executed'''
    
    start_times  = []
    end_times = []

    #Need to specify
    depot = tasks[0]

    for day in range(data.days):
        start_times_day = []
        end_times_day = []
        for task in tasks:
            if task.ID[0] == "M": 
                if (day + 1) == task.day:
                    start_times_day.append(task.start_time)
                    end_times_day.append(task.start_time)
                else: 
                    start_times_day.append(-1)
                    end_times_day.append(-1)
            else: 
                ### HERE IT NEEDS TO BE CHECKED IF THE END TIMES NEEDS TO BE SUBVSTRACTED WITH SERVICE TIMES! 
                start_times_day.append(task.start_time + calculate_distance(depot, task))
                end_times_day.append(task.end_time - calculate_distance(depot, task) - task.service_time)
        
        start_times.append(start_times_day)
        end_times.append(end_times_day)

    return start_times, end_times

######## OUTPUT FUNCTIONS  SZENARIO FLEXI #########

def write_json_solution_mip_flexi(objVal: int, var_y, var_x, var_u, data: InputData, distances: List[List[int]], filepath: str, number_tasks: int):
    """
    Writes the solution of the Mixed Integer Programming (MIP) problem to a JSON file.

    Parameters:
    - objVal (int): The objective value of the solved MIP problem.
    - var_y (gp.Var): The binary variable indicating if a task is selected on a given day by a cohort.
    - var_x (gp.Var): The binary variable indicating the sequence of tasks.
    - var_u (gp.Var): The continuous variable indicating the start time of a task.
    - data (InputData): The input data containing task and cohort information.
    - distances (List[List[int]]): The distance matrix between tasks.
    - filepath (str): The path where the JSON file will be saved.
    - number_tasks (int): The number of tasks considered in the solution.
    """
    
    number_all_tasks = 0
    days = {}

    for day in range(data.days):
        day_list = []

        for cohort in range(data.cohort_no):
            route_list = []
            profit_route = 0
            start_time = 0
            pre_selected_nodes = []
            u_nodes = []

            # Collect tasks selected by the cohort on the given day
            for i in range(1, len(data.optionalTasks[0:number_tasks])):
                if var_y[day, cohort, i].X == 1:
                    number_all_tasks += 1
                    pre_selected_nodes.append(i)
                    u_nodes.append(var_u[day, cohort, i].X)
                    profit_route += data.optionalTasks[i].profit

            if len(pre_selected_nodes) > 0:
                # Pair and sort the nodes based on start times
                paired_lists = list(zip(u_nodes, pre_selected_nodes))
                sorted_pairs = sorted(paired_lists, key=lambda x: x[0])
                sorted_u_nodes, sorted_nodes = zip(*sorted_pairs)

                # Create the route list for the cohort
                start_node = 0
                for i in sorted_nodes:
                    start_time += distances[start_node][i]
                    route_list.append({
                        "StartTime": start_time,
                        "SelectedDay": day + 1,
                        "ID": data.optionalTasks[i].ID
                    })
                    start_node = i
                    start_time += data.optionalTasks[i].service_time
                
            cohort_dict = {
                "CohortID": cohort,
                "Profit": profit_route,
                "Route": route_list
            }
            
            day_list.append(cohort_dict)

        days[str(day + 1)] = day_list
    
    results = {
        "Instance": data.main_tasks_path.stem,
        "Objective": objVal,
        "NumberOfAllTasks": number_all_tasks,
        "UseMainTasks": False,
        "Days": days
    }

    # Write the dictionary to a JSON file
    with open(filepath, 'w') as json_file:
        json.dump(results, json_file, indent=2)

    print(f"JSON file has been created at {filepath}")


def write_txt_solution_flexi(gp_model, var_y, var_x, var_u, data:InputData, distances, file_path:str, number_tasks:int):
    """
    Writes optimization gap, runtime, number of constraints, and number of variables 
    from a solved Gurobi model into a text file.

    Parameters:
    model (gurobipy.Model): The Gurobi model to extract information from.
    y, x, u, data, d, define_range: Additional parameters (usage can be defined as needed).
    file_path (str): The path to the output text file.
    """
    
    # Retrieve optimization metrics
    gap = gp_model.MIPGap
    runtime = round(gp_model.Runtime,2)
    num_constraints = gp_model.NumConstrs
    num_variables = gp_model.NumVars
    obj = round(gp_model.getAttr("ObjVal"))
    
    # Write the metrics to the output file
    with open(file_path, 'w') as file:
        file.write(str(obj) + "\t" + str(gap) + "\t" + str(runtime) + "\t" + str(num_constraints) + "\t" + str(num_variables) + "\n")
        file.write(str(data.days) + " " + str(data.cohort_no) + " " + str(number_tasks) + "\n \n")

        for day in range(data.days):

            file.write(str(day)+"\n")

            for cohort in range(data.cohort_no):
                
                file.write("\t" +str(cohort) + " ")

                route_list = []
                profit_route = 0
                start_time = 0
                pre_selected_nodes = []
                u_nodes = []

                for i in range(1,len(data.optionalTasks[0:number_tasks])):
                    if var_y[day,cohort,i].X == 1:

                        pre_selected_nodes.append(i)
                        u_nodes.append(var_u[day,cohort,i].X)

                        profit_route += data.optionalTasks[i].profit

                file.write("("+str(profit_route) + "): ")

                if len(pre_selected_nodes) > 0:
                    # Pair the lists together
                    paired_lists = list(zip(u_nodes, pre_selected_nodes))

                    # Sort the pairs based on the first list
                    sorted_pairs = sorted(paired_lists, key=lambda x: x[0])

                    # Separate the pairs back into two lists
                    sorted_u_nodes, sorted_nodes = zip(*sorted_pairs)

                    sorted_nodes = list(sorted_nodes)

                    start_node = 0
                    sorted_nodes.append(start_node)
                    sorted_nodes.insert(start_node, start_node)
                    for i in sorted_nodes:
                        
                        file.write(str(i) +" ")

                file.write("\n")
                
    print(f"Text file has been created at {file_path}")


######## OUTPUT FUNCTIONS  SZENARIO Main ######### - ###### MAIN APPROACH #####

def sort_tuples(tuples) -> List[Tuple[int,int]]:
    # Sort tuples by the first element
    tuples.sort()

    # Initialize the sorted list with the starting tuple (the one with 0 as the first element)
    sorted_tuples = [t for t in tuples if t[0] == 0]

    # Remove the starting tuple from the original list
    tuples = [t for t in tuples if t[0] != 0]

    # Iterate and find the correct order
    while tuples:
        for i, t in enumerate(tuples):
            if t[0] == sorted_tuples[-1][1]:
                sorted_tuples.append(t)
                tuples.pop(i)
                break

    return sorted_tuples

def create_subtours(list_of_tuples: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """
    Creates subtours from a list of tuples representing connections between nodes.

    Parameters:
    list_of_tuples (List[Tuple[int, int]]): List of tuples where each tuple represents a connection between two nodes.

    Returns:
    List[List[Tuple[int, int]]]: A list of subtours, where each subtour is a list of tuples.
    """
    if not list_of_tuples:
        return []

    # Create a copy of the list to avoid modifying the original list
    tour_tuples = list_of_tuples[:]
    subtours = []
    super_control = True

    while super_control:
        super_control = False
        for element in tour_tuples:
            if element[0] == 0:  # Start a new subtour if the starting node is 0
                subtour = [element]
                last_elem = element[1]
                tour_tuples.remove(element)
                control = True

                while control:
                    control = False
                    for item in tour_tuples:
                        if item[0] == last_elem:  # Continue the subtour if the next node matches
                            subtour.append(item)
                            last_elem = item[1]
                            tour_tuples.remove(item)
                            control = True
                            break

                subtours.append(subtour)
                super_control = True

    return subtours


def write_txt_solution(gp_model, var_s, var_x, data: InputData, allTasks: List[Union[OptionalTask, MainTask]], file_path: str) -> None:
    """
    Writes optimization gap, runtime, number of constraints, and number of variables 
    from a solved Gurobi model into a text file.

    Parameters:
    gp_model : gurobipy.Model
        The Gurobi model to extract information from.
    var_s : dict
        Dictionary containing the start times of tasks for each day and cohort.
    var_x : dict
        Dictionary indicating whether a task is selected by a cohort on a given day.
    data : InputData
        The input data for the model.
    allTasks : List[Union[OptionalTask, MainTask]]
        A list of all tasks (both optional and main tasks).
    file_path : str
        The path to the output text file.
    """
    
    # Retrieve optimization metrics
    gap = gp_model.MIPGap
    runtime = round(gp_model.Runtime, 2)
    num_constraints = gp_model.NumConstrs
    num_variables = gp_model.NumVars
    obj = round(gp_model.getAttr("ObjVal")) #- (data.mainTasks[0].profit * len(data.mainTasks))
    
    # Write the metrics to the output file
    try:
        with open(file_path, 'w') as file:
            # Write the objective value, gap, runtime, number of constraints, and number of variables
            file.write(f"{obj}\t{gap}\t{runtime}\t{num_constraints}\t{num_variables}\n")
            # Write the number of days and cohorts
            file.write(f"{data.days} {data.cohort_no}\n\n")

            for day in range(data.days):
                # Write the current day
                file.write(f"{day}\n")

                routes = []
                unique_nodes_sets = []

                for cohort in range(data.cohort_no):
                    # Write the current cohort
                    all_tuples = []

                    # Collect tasks selected by the cohort on the given day
                    for i in range(len(allTasks)):
                        for j in range(len(allTasks)):
                            if var_x[day, cohort, i, j].X > 0:
                                all_tuples.append((i, j))
                    subtours = create_subtours(all_tuples)
                    if len(subtours) >= 1: 
                        for i in range(len(subtours)):
                            routes.append(subtours[i])
                            unique_nodes_sets.append(set([node for tup in subtours[i] for node in tup]))

                number_cohort = 0
                for r in range(len(routes)):

                    profit_route = 0
                    # Write the current cohort
                    file.write(f"\t{number_cohort} ")

                    # Calculate profit per route
                    for node in unique_nodes_sets[r]:
                        profit_route += allTasks[node].profit

                    # Write the profit of the route
                    file.write(f" ({profit_route}): ")

                    # Sort and write the selected nodes in order
                    sorted_tuples = routes[r]
                    startelem = sorted_tuples[0][0]
                    file.write(f"{startelem} ")

                    for tuple in sorted_tuples:
                        for element in tuple:
                            if element == startelem:
                                continue
                            else:
                                file.write(f"{element} ")
                                startelem = element
                    
                    number_cohort += 1

                    file.write("\n")
        print(f"Text file has been created at {file_path}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")



def write_json_solution(gp_model, var_s, var_x, data: InputData, allTasks: List[Union[OptionalTask, MainTask]], file_path: str):
    """
    Write the solution of the optimization model to a JSON file.

    Parameters:
    gp_model : Gurobi model object
        The optimization model containing the solution.
    var_s : dict
        Dictionary containing the start times of tasks for each day and cohort.
    var_x : dict
        Dictionary indicating whether a task is selected by a cohort on a given day.
    data : InputData
        The input data for the model.
    allTasks : List[Union[OptionalTask, MainTask]]
        A list of all tasks (both optional and main tasks).
    file_path : str
        The file path where the JSON file will be saved.
    """
    
    number_all_tasks = 0
    days = {}
    objVal = round(gp_model.getAttr("ObjVal")) #- (data.mainTasks[0].profit * len(data.mainTasks))

    for day in range(data.days):
        day_list = []
        routes = []
        unique_nodes_sets = []

        original_cohort_numbers = []
        for cohort in range(data.cohort_no):
            all_tuples = []

            # Collect tasks selected by the cohort on the given day
            for i in range(len(allTasks)):
                for j in range(len(allTasks)):
                    if var_x[day, cohort, i, j].X > 0:
                        all_tuples.append((i, j))
            subtours = create_subtours(all_tuples)
            if len(subtours) >= 1: 
                for i in range(len(subtours)):
                    routes.append(subtours[i])
                    unique_nodes_sets.append(set([node for tup in subtours[i] for node in tup]))
                original_cohort_numbers += [cohort for i in range(len(subtours))]

        number_cohort = 0
        for r in range(len(routes)):
            route_list = []
            profit_route = 0
            # Calculate profit per route
            for node in unique_nodes_sets[r]:
                number_all_tasks += 1
                profit_route += allTasks[node].profit
            
            # Subtract depot and end node (depot)
            number_all_tasks -= 2
                
            # Pair and sort the nodes based on start times
            sorted_tuples = routes[r]
            startelem = sorted_tuples[0][0]


            # Create the route list for the cohort
            startelem = sorted_tuples[0][0]
            for tuple in sorted_tuples:
                for element in tuple: 
                    if element == startelem:
                        continue
                    else:
                        id = allTasks[element].ID
                        if id != "PE-FWI-5-5985":  # Exclude specific ID -> Depot
                            route_list.append({
                                "StartTime": round(var_s[day, original_cohort_numbers[r], element].X),
                                "SelectedDay": day + 1,
                                "ID": allTasks[element].ID
                            })
                            startelem = element
                
            cohort_dict = {
                "CohortID": number_cohort,
                "Profit": profit_route,
                "Route": route_list
            }
            number_cohort += 1
            
            day_list.append(cohort_dict)

        days[str(day + 1)] = day_list
    
    results = {
        "Instance": data.main_tasks_path.stem,
        "Objective": objVal,
        "NumberOfAllTasks": number_all_tasks,
        "UseMainTasks": True,
        "Days": days
    }

    # Write the dictionary to a JSON file
    try:
        with open(file_path, 'w') as json_file:
            json.dump(results, json_file, indent=2)
        print(f"JSON file has been created at {file_path}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
