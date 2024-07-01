from functions_MIP import *


def main():

    for no_days in [2]: #[2,5,8,10]
        # One Instance is enough because basic values dont change! 
        for instance_no in [1]:
            for define_range in [50]: #[50,200,500,1000]

                ### SETUP FOLDER STRUCTURE ### 
                
                # Get the current working directory (cwd)
                cwd = Path.cwd()
                
                # Define the output folder path relative to the script location
                outputFilePath_1 = cwd / "Data" / "Results_Main_MIP" / f"solution7_{no_days}_{instance_no}_{define_range}.txt"
                outputFilePath_2 = cwd / "Data" / "Results_Main_MIP" / f"solution7_{no_days}_{instance_no}_{define_range}.json"


                #### INITIALIZE DATA ####
                print("Initialize Data \n")
                main_tasks_path = cwd / "Data" / "Instanzen" / f"Instance7_{no_days}_{instance_no}.json"
                data = InputData(main_tasks_path)

                #### CREATE UNION OPTIONAL TASKS AND DEPOT ####
                all_tasks = data.optionalTasks[0:define_range] + [data.optionalTasks[0]]


                #### PARAMETERS ####
                print("Initialize Parameters \n")
                P = get_profits(all_tasks)
                T_max = data.maxRouteDuration            # Time Units of one "Day" = 6 hours = 21600 seconds
                M_no = data.cohort_no                    # Number of available Teams --> Routes
                N_no = len(all_tasks)
                d = get_distance_matrix(all_tasks)
                s = get_service_times(all_tasks)

                #### INDICES ####

                N = range(N_no)
                M = range(M_no)
                T = range(data.days)
                
                #### MODEL ####
                print("Start Model \n \n")
                model = gp.Model()


                #### VARIABLES ####

                x = model.addVars(T,M,N,N, name = "x", vtype=gp.GRB.BINARY)
                y = model.addVars(T,M,N, name = "y", vtype=gp.GRB.BINARY)
                u = model.addVars(T,M,N, name = "u", vtype=gp.GRB.INTEGER)

                #### OBJECTIVE FUNCTION ####

                model.setObjective(gp.quicksum(P[i] * y[t,m,i] for m in M for i in N[1:-1] for t in T), gp.GRB.MAXIMIZE)

                #### CONSTRAINTS ####

                for t in T:
                    model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in N[1:]) == gp.quicksum(x[t,m,i, N[-1]] for m in M for i in N[:-1]), "Constraint_3.2a")
                    model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in N[1:]) == len(M), "Constraint_3.2b")
                    model.addConstr(gp.quicksum(x[t,m,i, N[-1]] for m in M for i in N[:-1]) == len(M), "Constraint_3.2c")

                
                for k in N[1:-1]:
                    model.addConstr(gp.quicksum(y[t,m,k] for m in M for t in T) <= 1, "Constraint_3.3")


                for k in N:
                    for t in T:
                        for m in M:
                            model.addConstr(gp.quicksum(x[t,m,k,j] for j in N) <= 1, "Constraint_new")
                
                
                for m in M:
                    for k in N[1:-1]:
                        for t in T:
                            model.addConstr(gp.quicksum(x[t,m,i,k] for i in N[:-1]) == gp.quicksum(x[t,m,k,j] for j in N[1:]), "Constraint 3.4a")
                            model.addConstr(gp.quicksum(x[t,m,i,k] for i in N[:-1]) == y[t,m,k], "Constraint 3.4b")
                            model.addConstr(gp.quicksum(x[t,m,k,j] for j in N[1:]) == y[t,m,k] , "Constraint 3.4c")


                for m in  M:
                    for t in T:
                        model.addConstr(gp.quicksum(d[i][j]*x[t,m,i,j] for i in N[:-1] for j in N[1:]) + gp.quicksum(y[t,m,i] * s[i] for i in N[1:])<= T_max, "Constraint_3.5")


                for m in M:
                    for i in N[1:]:
                        for t in T:
                            model.addConstr(u[t,m,i] >= 2, "Constraint 3.6a")
                            model.addConstr(u[t,m,i] <= len(N), "Constraint 3.6b")


                for m in M:
                    for i in N[1:]:
                        for j in N[1:]:
                            for t in T:
                                model.addConstr(u[t,m,i] - u[t,m,j] + 1 <= (len(N) - 1)*(1 - x[t,m,i,j]), "Constraint 3.7")



                #### DEFINE OPTIMIZATION PARAMS ###
                model.Params.MIPGap = 0.01 # Gap is 1%! 
                model.Params.TimeLimit = 10800 # 3 hours
                model.Params.Threads = 32
                model.Params.PrePasses = 1000000

                #### OPTIMIZE MODEL ####
                model.optimize()

                #### EVALUATION ####
                model.printAttr(gp.GRB.Attr.ObjVal)
                model.printAttr(gp.GRB.Attr.X)

                write_txt_solution_flexi(model, y, x, u, data,d, outputFilePath_1, define_range)
                write_json_solution_mip_flexi(round(model.getAttr("ObjVal")), y,x,u, data,d, outputFilePath_2, define_range)

main()