import json
import csv
from typing import List, Dict, Union, Tuple
from classes_MIP import *
import math


def get_distance_matrix(tasks:list[Union[MainTask, OptionalTask]]) -> list[list[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    distances = [[0 for i in range(len(tasks))] for j in range(len(tasks))]

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

    distances_service_time = [[0 for i in range(len(internal_tasks))] for j in range(len(internal_tasks))]

    print("Calculate Distance plus Service Times")

    for task_i_id in range(len(internal_tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distance = calculate_distance(internal_tasks[task_i_id], internal_tasks[task_j_id])
                distances_service_time[task_i_id][task_j_id] =  distance + internal_tasks[task_i_id].service_time
                distances_service_time[task_j_id][task_i_id] =  distance + internal_tasks[task_j_id].service_time

    return distances_service_time


def create_all_tasks(data: InputData, define_range: int) -> List[Union[MainTask, OptionalTask]]:
    """
    Creates a combined list of tasks from the main tasks and the depot.

    Parameters:
    - data (InputData): An InputData object containing lists of main and optional tasks.
    - define_range (int): The number of optional tasks to include from the start of the optional tasks list.

    Returns:
    - List[Union[MainTask, OptionalTask]]: A combined list of tasks containing the specified range of optional tasks, 
      all main tasks, and the first optional task.
    """
    
    # Combine the specified range of optional tasks, all main tasks, and the first optional task
    tasks = data.optionalTasks[0:define_range] + data.mainTasks + [data.optionalTasks[0]]
    
    return tasks

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
        "Instance": data.main_tasks_path.split("/")[-1].split(".")[0],
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


######## OUTPUT FUNCTIONS  SZENARIO Main #########



def write_json_solution_mip(objVal:int, var_y, var_x, var_u, data:InputData, distances, filepath:str, number_tasks:int):

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

            for i in range(1,len(data.optionalTasks[0:number_tasks])):
                #for j in range(1,len(data.optionalTasks[0:10])):
                    if var_y[day,cohort,i].X == 1:

                        number_all_tasks += 1
                        pre_selected_nodes.append(i)
                        u_nodes.append(var_u[day,cohort,i].X)

                        profit_route += data.optionalTasks[i].profit
                        #start_time += distances[i][j]

            if len(pre_selected_nodes) > 0:
                # Pair the lists together
                paired_lists = list(zip(u_nodes, pre_selected_nodes))

                # Sort the pairs based on the first list
                sorted_pairs = sorted(paired_lists, key=lambda x: x[0])

                # Separate the pairs back into two lists
                sorted_u_nodes, sorted_nodes = zip(*sorted_pairs)

                start_node = 0
                for i in sorted_nodes:
                    start_time += distances[start_node][i]            
                    route_list.append({"StartTime" : start_time,
                                            "SelectedDay" : day + 1,
                                            "ID" : data.optionalTasks[i].ID})
                    
                    start_node = i
                    start_time += data.optionalTasks[i].service_time
                
            cohort_dict = {"CohortID"   : cohort,
                           "Profit"     : profit_route,
                           "Route"    : route_list}
            
            
            day_list.append(cohort_dict)


        days[str(day + 1)] = day_list
        
                
    
    results = {
        "Instance": data.main_tasks_path.split("/")[-1].split(".")[0],
        "Objective": objVal,
        "NumberOfAllTasks": number_all_tasks,#len(res.vars.y),
        "UseMainTasks" : False,
        "Days" : days
    }

    # Write the dictionary to a JSON file
    with open(filepath, 'w') as json_file:
        json.dump(results, json_file, indent=2)

    print(f"JSON file has been created at {filepath}")

def write_txt_solution(gp_model, var_y, var_x, var_u, data:InputData, distances, file_path:str, number_tasks:int):
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