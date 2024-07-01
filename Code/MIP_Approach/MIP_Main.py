import gurobipy as gp
import os
from classes_MIP import *
from functions_MIP import *
import math
from typing import List, Union, Tuple



def main():

    #for no_days in [2]: #[2,5,8,10]
        # One Instance is enough because basic values dont change! 
        #for instance_no in [1]:
            #for define_range in [50]: #[50,200,500,1000]

    ### SETUP FOLDER STRUCTURE ### 
    no_days = 2
    instance_no = 1
    define_range = 50

    # Get the current working directory (cwd)
    cwd = os.getcwd() 
    # Define the output folder path relative to the script location
    outputFilePath_1 = cwd + "/Data/Results_Main_MIP/solution7_"+str(no_days)+"_"+str(instance_no)+"_"+str(define_range)+".txt"
    outputFilePath_2 = cwd + "/Data/Results_Main_MIP/solution7_"+str(no_days)+"_"+str(instance_no)+"_"+str(define_range)+".json"


    #### INITIALIZE DATA ####
    print("Initialize Data \n")
    main_tasks_path = cwd + "/Data/Instanzen/Instance7_"+str(no_days)+"_"+str(instance_no)+".json"
    for main_task in data.mainTasks:
        main_task.setProft(1000000)
    data = InputData(main_tasks_path)

    #### CREATE UNION MAIN TASKS AND OPTIONAL TASKS ####
    all_tasks = create_all_tasks(data, define_range)


    #### PARAMETERS ####
    print("Initialize Parameters \n")
    P = get_profits(all_tasks)
    T_max = data.maxRouteDuration            # Time Units of one "Day" = 6 hours = 21600 seconds
    M_no = data.cohort_no     # Number of available Teams --> Routes
    N_no = len(all_tasks)
    s = get_service_times(all_tasks)
    dt = get_distance_service_time_matrix(all_tasks)
    O, C = get_mandatory_end_and_start_times(data, all_tasks)

    print("O", O)
    print("C", C)

    # Big Number for binary constraints
    L = 1000000

    #### INDICES ####
    N = range(N_no)
    M = range(M_no)
    T = range(data.days)

    #### MODEL ####
    print("Start Model \n \n")
    model = gp.Model()

    #### VARIABLES ####
    x = model.addVars(T, M, N, N, name="x", vtype=gp.GRB.BINARY)  # 1, if in route m, a visit to node i is followed by a visit to node j, and 0 otherwise at t
    y = model.addVars(T, M, N, name="y", vtype=gp.GRB.BINARY)  # yim = 1, if vertex i is visited in route m, and 0 otherwise
    s = model.addVars(T, M, N, name="s", vtype=gp.GRB.CONTINUOUS)  # the start of the service at node i in route m

    #### OBJECTIVE FUNCTION ####
    model.setObjective(gp.quicksum(P[i] * y[t,m,i] for m in M for i in N[1:-1] for t in T), gp.GRB.MAXIMIZE)

    #### CONSTRAINTS ####
    # Ensure that each route starts from node 1 and ends in node |N|.
    for t in T:
        model.addConstr(gp.quicksum(x[t, m, 0, j] for m in M for j in N[1:]) == gp.quicksum(x[t, m, i, N[-1]] for m in M for i in N[:-1]), "Constraint_3.2a")
        model.addConstr(gp.quicksum(x[t, m, 0, j] for m in M for j in N[1:]) == len(M), "Constraint_3.2b")
        model.addConstr(gp.quicksum(x[t, m, i, N[-1]] for m in M for i in N[:-1]) == len(M), "Constraint_3.2c")

    # Every main task needs to be in one tour of one cohort
    for k in N[1:-1]:
        model.addConstr(gp.quicksum(y[t, m, k] for m in M for t in T) <= 1, "Constraint_3.3")

    # No self visits:
    for t in T:
        for m in M:
            for i in N:
                model.addConstr(x[t, m, i, i] == 0, "Constraint 3.5")

    # Ensure each node can only be visited at most once.
    for m in M:
        for k in N[1:-1]:  # only valid for main tasks
            for t in T:
                model.addConstr(gp.quicksum(x[t, m, i, k] for i in N[:-1]) == gp.quicksum(x[t, m, k, j] for j in N[1:]), "Constraint 3.4a")
                model.addConstr(gp.quicksum(x[t, m, i, k] for i in N[:-1]) == y[t, m, k], "Constraint 3.4b")
                model.addConstr(gp.quicksum(x[t, m, k, j] for j in N[1:]) == y[t, m, k], "Constraint 3.4c")

    # Ensure the connectivity and timeline of each route.
    for t in T:
        for m in M:
            for i in N:
                for j in N:
                    if i != j:
                        model.addConstr(s[t, m, i] + dt[i][j] - s[t, m, j] <= L * (1 - x[t, m, i, j]), "Constraint 3.7")

    # Restrict start and end times:
    for t in T:
        for m in M:
            for i in N:
                model.addConstr(O[t][i] * y[t, m, i] <= s[t, m, i], "Constraint 3.8a")
                model.addConstr(s[t, m, i] <= C[t][i] * y[t, m, i], "Constraint 3.8b")

    # Don't start several tours from one node
    for k in N:
        for t in T:
            for m in M:
                model.addConstr(gp.quicksum(x[t, m, k, j] for j in N) <= 1, "Constraint_new")


    #### DEFINE OPTIMIZATION PARAMS ###
    model.Params.MIPGap = 0.01 # Gap is 1%! 
    model.Params.TimeLimit = 10#10800  # 3 hours
    model.Params.Threads = 32
    model.Params.PrePasses = 1000000

    #### OPTIMIZE MODEL ####
    model.optimize()

    #### EVALUATION ####
    model.printAttr(gp.GRB.Attr.ObjVal)
    model.printAttr(gp.GRB.Attr.X)

    #write_txt_solution(model, y, x, u, data,d, outputFilePath_1, define_range)

    #write_json_solution_mip(round(model.getAttr("ObjVal")), y,x,u, data,d, outputFilePath_2, define_range)

main()