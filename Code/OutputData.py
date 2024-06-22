import json
import csv
from InputData import *


'''class OutputNode(DataJob):
    ''Inherits DataJob Attributes and adds the necessary start and end times to calculate the makespan''
    def __init__(self, dataJob:DataJob):
        #Same Attributes as for DataJob
        super().__init__(dataJob.JobId, [dataJob.ProcessingTime(i) for i in range(len(dataJob.Operations))], dataJob.setup_time_between_lots)
        
        # Define a list with all the necessary Start and End times for the jobs tio calculate the makespan with a given permutation
        self.selectedMachines = ["M0"]*len(self.Operations)
        self.lotNumber = dataJob.lotNumber
        
        self.lots = [DataLot(x,self.JobId, len(self.selectedMachines)) for x in range(self.lotNumber)]
'''

class Solution:
    ''' Creates an object with a list for the Outpout Jobs and an given permutation following the sequence
        Additionally dummy results for Makespan, TotalTardiness and TotalWeightedTardiness are implemented.
        '''
    def __init__(self, route_plan:dict, data:InputData):
        ''' Define the attributes for solution'''

        self._totalProfit = -1
        self._route_plan = route_plan

    def __str__(self):
        '''Base Function for printing out the results'''
        return "The permutation " + str(self.Permutation) + " and the "+ str(self.lot_matrix) +" results in a Makespan of " + str(self.Makespan)

    def setRoutePlan(self, permutation:list[int]) -> None:
        ''' Sets a new permutation to the given solution'''
        self.Permutation = permutation

    @property
    def TotalProfit(self) -> int: 
        ''' Returns Total Profit of Tour'''

        return self._totalProfit
    
    @property
    def RoutePlan(self) -> dict[str, list[list[int]]]: 
        ''' Returns Total Profit of Tour'''

        return self._route_plan


class SolutionPool:
    ''' Class for creating lits objects containing solution objects'''

    def __init__(self):
        ''' Create an empty list for the solutions'''
        self.Solutions = []

    def AddSolution(self, newSolution:Solution) -> None:
        ''' Add a new solution to the solution pool'''
        self.Solutions.append(newSolution)

    def GetLowestMakespanSolution(self) -> Solution:
        ''' Sort all the solutions in regard to their makespan and return the solution with the lowest makespan'''
        self.Solutions.sort(key = lambda solution: solution.TotalProfit) # sort solutions according to makespan

        return self.Solutions[0]

'''
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

'''