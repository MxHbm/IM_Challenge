from functions_MIP import *

def main():

    for no_days in [2,5,8,10]: #[2,5,8,10]
        # One Instance is enough because basic values dont change! 
        for instance_no in [1,2]:
            for define_range in [50,100,200,500,1000]: #[50,200,500,1000]

                # Get the current working directory (cwd)
                cwd = Path.cwd()

                # Define the output folder path relative to the script location
                outputFilePath_1 = cwd / "Data" / "Results_Main_MIP" / f"solution7_{no_days}_{instance_no}_{define_range}.txt"
                outputFilePath_2 = cwd / "Data" / "Results_Main_MIP" / f"solution7_{no_days}_{instance_no}_{define_range}.json"


                #### INITIALIZE DATA ####
                print("Initialize Data \n")
                main_tasks_path = cwd / "Data" / "Instanzen" / f"Instance7_{no_days}_{instance_no}.json"
                data = InputData(main_tasks_path)
                #for main_task in data.mainTasks:
                #    main_task.setProfit(1000)

                #### CREATE UNION MAIN TASKS AND OPTIONAL TASKS ####
                all_tasks = data.optionalTasks[0:define_range] + data.mainTasks + [data.optionalTasks[0]]


                #### PARAMETERS ####
                print("Initialize Parameters \n")
                P = get_profits(all_tasks)        
                M_no = data.cohort_no     # Number of available Teams --> Routes
                N_no = len(all_tasks)
                s = get_service_times(all_tasks)
                dt = get_distance_service_time_matrix(all_tasks)
                O, C = get_mandatory_end_and_start_times(data, all_tasks)

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
                model.setObjective(gp.quicksum(P[i] * y[t,m,i] for m in M for i in N[1:define_range] for t in T), gp.GRB.MAXIMIZE)

                #### CONSTRAINTS ####
                # Ensure that each route starts from node 1 and ends in node |N|.
                for t in T:
                    model.addConstr(gp.quicksum(x[t, m, 0, j] for m in M for j in N[1:]) == gp.quicksum(x[t, m, i, N[-1]] for m in M for i in N[:-1]), "Constraint_3.2a")
                    model.addConstr(gp.quicksum(x[t, m, 0, j] for m in M for j in N[1:]) == len(M), "Constraint_3.2b")
                    model.addConstr(gp.quicksum(x[t, m, i, N[-1]] for m in M for i in N[:-1]) == len(M), "Constraint_3.2c")

                # Every optional task can be in one tour of one cohort
                for k in N[1:define_range]:
                    model.addConstr(gp.quicksum(y[t, m, k] for m in M for t in T) <= 1, "Constraint_3.3")

                # Every main task needs to be in one tour of one cohort
                for k in N[define_range:-1]:
                    model.addConstr(gp.quicksum(y[t, m, k] for m in M for t in T) == 1, "Constraint_3.3")

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
                                    model.addConstr(s[t, m, i] + dt[i][j] - s[t, m, j] <= L * (1 - x[t, m, i, j]), "Constraint 3.7")

                # Restrict start and end times:
                for t in T:
                    for m in M:
                        for i in N:
                            model.addConstr(O[t][i] * y[t, m, i] <= s[t, m, i], "Constraint 3.8a")
                            model.addConstr(s[t, m, i] <= C[t][i] * y[t, m, i], "Constraint 3.8b")

                
                #### DEFINE OPTIMIZATION PARAMS ###
                model.Params.MIPGap = 0.01 # Gap is 1%! 
                model.Params.TimeLimit = 10800  # 3 hours
                #model.Params.Threads = 32
                model.Params.PrePasses = 10000

                #### OPTIMIZE MODEL ####
                model.optimize()

                #### EVALUATION ####
                model.printAttr(gp.GRB.Attr.ObjVal)
                model.printAttr(gp.GRB.Attr.X)
                
                write_txt_solution(model, x, data, all_tasks, outputFilePath_1)
                write_json_solution(model,s,x,data,all_tasks,outputFilePath_2)

main()