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

def get_service_times(tasks:list[OptionalTask]) -> list[int]:
    ''' List of service times of each task'''

    service_times = [task.service_time for task in tasks]

    #Value for depot
    service_times.append(0)

    return service_times

def get_N(tasks:list[OptionalTask]) -> list[int]:

    # Number of positions plus depot 
    number = len(tasks) + 1

    return list(range(number))


def main():

    for no_days in [2,5,8,10]: #[2,5,8,10]
        # One Instance is enough because basic values dont change! 
        for instance_no in [1]:
            for define_range in [50,200,500,1000]:

                ### SETUP FOLDER STRUCTURE ### 
                
                # Get the current working directory (cwd)
                cwd = os.getcwd() 
                # Define the output folder path relative to the script location
                outputFilePath_1 = cwd + "/Data/Results/solution7_"+str(no_days)+"_"+str(instance_no)+"_"+str(define_range)+".txt"
                outputFilePath_2 = cwd + "/Data/Results/solution7_"+str(no_days)+"_"+str(instance_no)+"_"+str(define_range)+".json"


                #### INITIALIZE DATA ####
                print("Initialize Data \n")
                main_tasks_path = "Data/Instanzen/Instance7_"+str(no_days)+"_"+str(instance_no)+".json"
                data = InputData(main_tasks_path)


                #### PARAMETERS ####
                print("Initialize Parameters \n")
                P = get_profits(data.optionalTasks[0:define_range])
                days = data.days
                T_max = 21600           # Time Units of one "Day" = 6 hours = 21600 seconds
                M_m = list(range(data.cohort_no))    # Number of available Teams --> Routes
                N = get_N(data.optionalTasks[0:define_range])
                d = get_distance_matrix(data.optionalTasks[0:define_range])
                s = get_service_times(data.optionalTasks[0:define_range])

                #### INDICES ####

                I = range(len(N))
                J = range(len(N))
                M = range(len(M_m))
                T = range(days)
                
                #### MODEL ####
                print("Start Model \n \n")
                model = gp.Model()


                #### VARIABLES ####

                x = model.addVars(T,M,I,J, name = "x", vtype=gp.GRB.BINARY)
                y = model.addVars(T,M,I, name = "y", vtype=gp.GRB.BINARY)
                u = model.addVars(T,M,I, name = "u", vtype=gp.GRB.INTEGER)

                #### OBJECTIVE FUNCTION ####

                model.setObjective(gp.quicksum(P[i] * y[t,m,i] for m in M for i in I[1:-1] for t in T), gp.GRB.MAXIMIZE)

                #### CONSTRAINTS ####

                for t in T:
                    model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in J[1:]) == gp.quicksum(x[t,m,i, J[-1]] for m in M for i in I[:-1]), "Constraint_3.2a")
                    model.addConstr(gp.quicksum(x[t,m,0,j] for m in M for j in J[1:]) == len(M), "Constraint_3.2b")
                    model.addConstr(gp.quicksum(x[t,m,i, J[-1]] for m in M for i in I[:-1]) == len(M), "Constraint_3.2c")

                
                for k in I[1:-1]:
                    model.addConstr(gp.quicksum(y[t,m,k] for m in M for t in T) <= 1, "Constraint_3.3")


                for k in I:
                    for t in T:
                        for m in M:
                            model.addConstr(gp.quicksum(x[t,m,k,j] for j in J) <= 1, "Constraint_new")
                
                
                for m in M:
                    for k in I[1:-1]:
                        for t in T:
                            model.addConstr(gp.quicksum(x[t,m,i,k] for i in I[:-1]) == gp.quicksum(x[t,m,k,j] for j in J[1:]), "Constraint 3.4a")
                            model.addConstr(gp.quicksum(x[t,m,i,k] for i in I[:-1]) == y[t,m,k], "Constraint 3.4b")
                            model.addConstr(gp.quicksum(x[t,m,k,j] for j in J[1:]) == y[t,m,k] , "Constraint 3.4c")


                for m in  M:
                    for t in T:
                        model.addConstr(gp.quicksum(d[i][j]*x[t,m,i,j] for i in I[:-1] for j in J[1:]) + gp.quicksum(y[t,m,i] * s[i] for i in I[1:])<= T_max, "Constraint_3.5")


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



                #### DEFINE OPTIMIZATION PARAMS ###
                model.Params.MIPGap = 0.01 # Gap is 1%! 
                model.Params.TimeLimit = 7200  # 2 hours

                #### OPTIMIZE MODEL ####
                model.optimize()

                #### EVALUATION ####
                model.printAttr(gp.GRB.Attr.ObjVal)
                model.printAttr(gp.GRB.Attr.X)

                write_txt_solution(model, y, x, u, data,d, outputFilePath_1, define_range)
                write_json_solution_mip(round(model.getAttr("ObjVal")), y,x,u, data,d, outputFilePath_2, define_range)

main()