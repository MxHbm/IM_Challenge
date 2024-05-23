import gurobipy as gp
import os
from IO import *
import math

def get_profits(tasks:list[OptionalTask]) -> list[int]:
    ''' Get the profit of the tasks in the data and add zeros for the depots to run the model'''

    # Fill profits vector
    print("Get Profits")
    profits = [task.profit for task in tasks]

    # Last value = profit of depot again
    profits.append(profits[0])

    return profits

def calculate_distance(task_1:OptionalTask, task_2:OptionalTask) -> float:
    ''' Calculate the distance between two tasks using the euclidean distance formula
        and return the time it takes to travel between them in seconds
    '''

    distance = math.sqrt((task_1.latitude - task_2.latitude)**2 + (task_1.longitude - task_2.longitude)**2)

    time = int(round(distance * 17100,0)) # time in seconds

    return time

def get_distance_matrix(tasks:list[OptionalTask]) -> list[list[float]]:
    ''' Get the distance matrix of the tasks in the data and add zeros for the depots to run the model'''

    # Add the depot again to the tasks at the end
    tasks.append(tasks[0])

    distances = [[0 for i in range(len(tasks))] for j in range(len(tasks))]

    print("Calculate Distances")

    for task_i_id in range(len(tasks)):
        for task_j_id in range(task_i_id): 
            # Calculate the distance between the two tasks
                distances[task_i_id][task_j_id] = distances[task_j_id][task_i_id] = calculate_distance(tasks[task_i_id], tasks[task_j_id])

    return distances

def get_N(tasks:list[OptionalTask]) -> list[int]:

    # Number of positions plus depot 
    number = len(tasks) + 1

    return list(range(number))


def main():

    #### INITIALIZE DATA ####
    print("Initialize Data \n \n")
    main_tasks_path = "Data/Instanzen/Instance7_2_1.json"
    data = InputData(main_tasks_path)


    #### PARAMETERS ####
    print("Initialize Parameters \n \n")
    P = get_profits(data.optionalTasks[0:150])
    days = data.days
    T_max = 21600           # Time Units of one "Day" = 6 hours = 21600 seconds
    M_m = list(range(data.cohort_no))    # Number of available Teams --> Routes
    N = get_N(data.optionalTasks[0:150])
    d = get_distance_matrix(data.optionalTasks[0:150])
    
    # Model
    print("Start Model \n \n")
    model = gp.Model()

    # Get the current working directory (cwd)
    cwd = os.getcwd() 
    # Define the output folder path relative to the script location
    outputFolder = cwd + "/Code"


    # Indices

    I = range(len(N))
    J = range(len(N))
    M = range(len(M_m))
    T = range(days)


    # Variablen

    x = model.addVars(T,M,I,J, name = "x", vtype=gp.GRB.BINARY)
    y = model.addVars(T,M,I, name = "y", vtype=gp.GRB.BINARY)
    u = model.addVars(T,M,I, name = "u", vtype=gp.GRB.INTEGER)

    # Objective Function

    model.setObjective(gp.quicksum(P[i] * y[t,m,i] for m in M for i in I[1:-1] for t in T), gp.GRB.MAXIMIZE)


    # Constraints
    for t in T:
        model.addConstr(gp.quicksum(x[0,j,m,t] for m in M for j in J[1:]) == gp.quicksum(x[i, J[-1], m, t] for m in M for i in I[:-1]), "Constraint 3.2a")
        model.addConstr(gp.quicksum(x[0,j,m,t] for m in M for j in J[1:]) <= len(M), "Constraint 3.2b")
        model.addConstr(gp.quicksum(x[i, J[-1], m, t] for m in M for i in I[:-1]) <= len(M), "Constraint 3.2c")

    ## Visit every node maximum once per Team and in the whole timespan  - Profit should be 18
    for k in I[1:-1]:
        model.addConstr(gp.quicksum(y[k,m,t] for m in M for t in T) <= 1, "Constraint 3.3")
    
    for k in I:
      for t in T:
            for m in M:
               model.addConstr(gp.quicksum(x[k,j,m,t] for j in J) <= 1, "Constraint_new")
    
    
    for m in M:
        for k in I[1:-1]:
            for t in T:
                model.addConstr(gp.quicksum(x[t,m,i,k] for i in I[:-1]) == gp.quicksum(x[t,m,k,j] for j in J[1:]), "Constraint 3.4a")
                model.addConstr(gp.quicksum(x[t,m,i,k] for i in I[:-1]) == y[t,m,k], "Constraint 3.4b")
                model.addConstr(gp.quicksum(x[t,m,k,j] for j in J[1:]) == y[t,m,k] , "Constraint 3.4c")

    for m in  M:
        for t in T:
            model.addConstr(gp.quicksum(d[i][j] * x[i,j,m,t] for i in I[:-1] for j in J[1:]) <= T_max, "Constraint 3.5")

    for m in M:
        for i in I[1:]:
            for t in T:
                model.addConstr(u[t,m,i] >= 2, "Constraint 3.6a")
                model.addConstr(u[t,m,i] <= len(N), "Constraint 3.6b")

    for m in M:
        for i in I[1:]:
             for j in J[1:]:
                for t in T:
                    model.addConstr(u[t,m,i] - u[t,m,j] + 1 <= (len(N) - 1)*(1 - x[t,m,i,j]), "Constraint 3.7")

    
    model.optimize()

    model.printAttr(gp.GRB.Attr.ObjVal)
    model.printAttr(gp.GRB.Attr.X)

    

    model.write(os.path.join(outputFolder,"model.lp"))
    # You can now use the outputFolder path in your script
    print(f"Output folder created at: {outputFolder}")

    write_json_solution_mip(round(model.getAttr("ObjVal")),y,x,u,data,d, outputFolder + "/solution.json")

main()