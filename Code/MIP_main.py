import gurobipy as gp
import os
from InputData import *
import math

def calculate_distance(task_1:OptionalTask, task_2:OptionalTask) -> float:
    ''' Calculate the distance between two tasks using the euclidean distance formula
        and return the time it takes to travel between them in seconds
    '''

    distance = math.sqrt((task_1.latitude - task_2.latitude)**2 + (task_1.longitude - task_2.longitude)**2)

    time = int(round(distance * 17100,0)) # time in seconds

    return time

def get_distance_matrix(tasks:list[MainTask],depot:OptionalTask) -> list[list[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    # Add the depot again to the tasks at the end
    internal_tasks = tasks.copy()
    internal_tasks.insert(0,depot)
    internal_tasks.append(depot)

    distances = [[0 for i in range(len(internal_tasks))] for j in range(len(internal_tasks))]

    print("Calculate Distances")

    for task_i_id in range(len(internal_tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distances[task_i_id][task_j_id] =  distances[task_j_id][task_i_id] =  calculate_distance(internal_tasks[task_i_id], internal_tasks[task_j_id])

    return distances

def get_distance_service_time_matrix(tasks:list[MainTask],depot:OptionalTask) -> list[list[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    # Add the depot again to the tasks at the end
    internal_tasks = tasks.copy()
    internal_tasks.insert(0,depot)
    internal_tasks.append(depot)

    distances_service_time = [[0 for i in range(len(internal_tasks))] for j in range(len(internal_tasks))]

    print("Calculate Distance plus Service Times")

    for task_i_id in range(len(internal_tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distance = calculate_distance(internal_tasks[task_i_id], internal_tasks[task_j_id])
                distances_service_time[task_i_id][task_j_id] =  distance + internal_tasks[task_i_id].service_time
                distances_service_time[task_j_id][task_i_id] =  distance + internal_tasks[task_j_id].service_time

    return distances_service_time

def get_N(tasks:list[MainTask]) -> list[int]:

    # Number of positions plus two times depot 
    number = len(tasks) + 2

    return list(range(number))

def get_mandatory_end_and_start_times(data:InputData, tmax:int) -> tuple[list[list[int]], list[list[int]]]:
    ''' List of mandatory start times of each task, integrates also factor at which day main tasks can only be executed'''
    
    start_times  = []
    end_times = []

    for day in range(data.days):
        start_times_day = [task.start_time if task.day == day + 1 else -1 for task in data.mainTasks]
        end_times_day = [task.start_time if task.day == day + 1 else -1 for task in data.mainTasks]

        #Value for depot
        start_times_day.insert(0,0)
        start_times_day.append(0)
        end_times_day.insert(0,tmax)
        end_times_day.append(tmax)
    
        start_times.append(start_times_day)
        end_times.append(end_times_day)

    return start_times, end_times

def sort_tuples(tuples):
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


def write_txt_solution(gp_model, var_y, var_s, var_x, data:InputData, file_path:str):
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
        file.write(str(data.days) + " " + str(data.cohort_no)+ "\n \n")

        for day in range(data.days):

            file.write(str(day)+"\n")

            for cohort in range(data.cohort_no):
                
                file.write("\t" +str(cohort) + " ")

                profit_route = 0
                pre_selected_nodes = []

                for i in range(0,len(data.mainTasks)+2):
                    for j in range(0,len(data.mainTasks)+2):
                        if var_x[day,cohort,i,j].X > 0:


                            pre_selected_nodes.append((i,j))

                file.write(": ")

                sorted_tuples = sort_tuples(pre_selected_nodes)

                startelem = sorted_tuples[0][0]
                file.write(str(startelem) + " ")

                for tuple in sorted_tuples:
                    for element in tuple: 

                        if(element == startelem):
                            continue
                        else:
                            file.write(str(element) +" ("+str(var_s[day,cohort,element].X)+") ")
                            startelem = element

                file.write("\n")
                


    print(f"Text file has been created at {file_path}")


def find_inital_main_task_allocation(data:InputData):

    #### PARAMETERS ####
    print("Initialize Parameters \n")
    T_max = data.maxRouteDuration           # Time Units of one "Day" = 6 hours = 21600 seconds
    M_no = list(range(data.cohort_no))    # Number of available Teams --> Routes
    N_no = get_N(data.mainTasks)
    d = get_distance_matrix(data.mainTasks, data.optionalTasks[0])
    dt = get_distance_service_time_matrix(data.mainTasks, data.optionalTasks[0])
    O,C = get_mandatory_end_and_start_times(data, T_max)

    print(O)
    print(C)

    print("Distances Matrix")
    for line in d:
        print(line)

    # Big Number for binary constraints
    L = 1000000

    #### INDICES ####

    N = range(len(N_no))
    M = range(len(M_no))
    T = range(data.days)

    for n in N[1:-1]:
        print(str(n) +":  Start Time: ", data.mainTasks[n-1].start_time, "\t Service Time: ", data.mainTasks[n-1].service_time)

    #### MODEL ####
    print("Start Model \n \n")
    model = gp.Model()

    #### VARIABLES ####

    x = model.addVars(T,M,N,N, name = "x", vtype=gp.GRB.BINARY) #  1, if in route m, a visit to node i is followed by a visit to node j, and 0 otherwise at t
    y = model.addVars(T,M,N, name = "y", vtype=gp.GRB.BINARY) # yim = 1, if vertex i is visited in route m, and 0 otherwise
    s = model.addVars(T,M,N, name = "s", vtype=gp.GRB.CONTINUOUS) # the start of the service at node i in route m

    #### OBJECTIVE FUNCTION ####

    model.setObjective(gp.quicksum(gp.quicksum(d[i][j] * x[t,m,i,j] for i in N for j in N) for m in M for t in T), gp.GRB.MINIMIZE)

    #### CONSTRAINTS ####

    #ensure that each route starts from node 1 and ends in node |N|.
    for t in T:
        model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in N[1:]) == gp.quicksum(x[t,m,i, N[-1]] for m in M for i in N[:-1]), "Constraint_3.2a")
        model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in N[1:]) == len(M), "Constraint_3.2b")
        model.addConstr(gp.quicksum(x[t,m,i, N[-1]] for m in M for i in N[:-1]) == len(M), "Constraint_3.2c")


    #Every main task needs to be in one tour of one cohort
    for k in N[1:-1]:
        model.addConstr(gp.quicksum(y[t,m,k] for m in M for t in T) == 1, "Constraint_3.3")

    
    # No self visits:
    for t in T:
        for m in M: 
            for i in N:
                model.addConstr(x[t,m,i,i] == 0, "Constraint 3.5")

    #ensure each node can only be visited at most once.
    for m in M:
        for k in N[1:-1]: # only valid for main tasks
            for t in T:
                model.addConstr(gp.quicksum(x[t,m,i,k] for i in N[:-1]) == gp.quicksum(x[t,m,k,j] for j in N[1:]), "Constraint 3.4a")
                model.addConstr(gp.quicksum(x[t,m,i,k] for i in N[:-1]) == y[t,m,k], "Constraint 3.4b")
                model.addConstr(gp.quicksum(x[t,m,k,j] for j in N[1:]) == y[t,m,k] , "Constraint 3.4c")

    #) ensure the connectivity and timeline of each route.
    for t in T: 
        for m in M: 
            for i in  N:
                for j in  N:
                    if i != j:
                        model.addConstr(s[t,m,i] + dt[i][j]  - s[t,m,j] <= L * (1 - x[t,m,i,j]), "Constraint 3.7")

    # Restrict start and end times: 
    for t in T: 
        for m in M:
            for i in N:
                model.addConstr(O[t][i] * y[t,m,i] <= s[t,m,i], "Constraint 3.8a")
                model.addConstr(s[t,m,i] <= C[t][i] * y[t,m,i], "Constraint 3.8b")


    #Dont start several tours from one mode
    for k in N:
        for t in T:
            for m in M:
                model.addConstr(gp.quicksum(x[t,m,k,j] for j in N) <= 1, "Constraint_new")


    #### DEFINE OPTIMIZATION PARAMS ###
    model.Params.MIPGap = 0.01 # Gap is 1%! 
    model.Params.TimeLimit = 34  # 2 hours
    model.Params.Threads = 8
    #model.Params.PrePasses = 1000000

    #### OPTIMIZE MODEL ####
    model.optimize()

    #### EVALUATION ####
    model.printAttr(gp.GRB.Attr.ObjVal)
    model.printAttr(gp.GRB.Attr.X)

    #### WRITE SOLUTION ####
    write_txt_solution(model, y, s, x, data, "Data/Results_Main/Task_Allocation.txt")


data = InputData("Data/Instanzen/Instance7_2_1.json")
find_inital_main_task_allocation(data)