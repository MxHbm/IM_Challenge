import json
from InputData import *
import os

class Solution:
    ''' 
    '''

    def __init__(self, route_plan:dict, data:InputData):
        ''' Define the attributes for solution'''

        self._totalProfit = -1
        self._totalTasks = -1
        self._route_plan = route_plan
        self._create_StartEndTimes(data)
        self._waitingTime = -1
        self._create_unused_tasks(data)

    def __str__(self):
        '''Base Function for printing out the results'''
        return "Solution:\n Route Plan: " + str(self.RoutePlan) + "\n Number of Tasks: " + str(self.TotalTasks) + "\n Total Profit: " + str(self.TotalProfit)
    
    
    def _create_StartEndTimes(self, data:InputData):
        ''' Calculate the start and the end times of the tasks of the given solution'''
        
        self._startTimes = {}
        self._endTimes = {}

        day_index = 0
        for day in self._route_plan.values():
            cohort_list_start = []
            cohort_list_end = []
            for cohort in day:
                route_list_start = [0]
                route_list_end = [0]

                if len(cohort) >= 0:
                    previous_t = cohort[0]

                end_time_previous = 0 # Needed to be added (Niklas)

                for t in cohort[1:]:


                    if t >= 1001:
                        start_time = data.allTasks[t].start_time
                    else: 
                        start_time = data.distances[previous_t][t] + end_time_previous


                    end_time = start_time + data.allTasks[t].service_time
                    end_time_previous = end_time
                    

                    previous_t = t
                    route_list_start.append(start_time)
                    route_list_end.append(end_time)
                
                cohort_list_start.append(route_list_start)
                cohort_list_end.append(route_list_end)
            
            self._startTimes[day_index] = cohort_list_start
            self._endTimes[day_index] = cohort_list_end
            day_index += 1
    

    def _create_unused_tasks(self, data:InputData) -> None: 
        ''' Create an initial set of all unused tasks'''

        self._unusedTasks = {task.no for task in data.allTasks}

        for day, cohorts in self._route_plan.items():
            for cohort in cohorts:
                for task in cohort:
                    self._unusedTasks.discard(task)

    def add_unused_Task(self, task_id:int) -> None:
        '''Adds one task id to the set of unused tasks'''

        self._unusedTasks.add(task_id)    

    def remove_unused_Task(self, task_id:int) -> None:
        '''Remove one task id to the set of unused tasks'''

        self._unusedTasks.discard(task_id)      

    def setRoutePlan(self, route_plan, data:InputData) -> None:
        ''' Sets a new route plan to the given solution'''
        self._route_plan = route_plan
        self._create_StartEndTimes(data)

    def setTotalProfit(self, new_profit) -> None:
        ''' Sets a new profit to the given solution'''
        self._totalProfit = new_profit

    def setTotalTasks(self, new_tasks) -> None:
        ''' Sets a new number of tasks to the given solution'''
        self._totalTasks = new_tasks

    def setWaitingTime(self, new_waiting_time) -> None:
        ''' Sets a new waiting time to the given solution'''
        self._waitingTime = new_waiting_time

    
    def WriteSolToJson(self, file_path:str, inputData: InputData):
        ''' Write the solution to a json file'''

        days = dict()
        
        for day in range(inputData.days):
            day_list = []

            for cohort in range(inputData.cohort_no):
                
                route_list = []
                profit_route = 0
                start_time = 0


                for i in self.RoutePlan[day][cohort]:

                    if i == self.RoutePlan[day][cohort][0]:
                        time = inputData.distances[0][i]
                        start_time += time
                    else:
                        j = self.RoutePlan[day][cohort][self.RoutePlan[day][cohort].index(i) - 1]                            
                        time = inputData.distances[j][i]
                        start_time += time
             
                    if i <= 1000:
                        profit_route += inputData.allTasks[i].profit
                    else:
                        start_time = inputData.allTasks[i].start_time


                    route_list.append({"StartTime" : start_time,
                        "SelectedDay" : day + 1,
                        "ID" : inputData.allTasks[i].ID})

                    start_time += inputData.allTasks[i].service_time
 
                    
                cohort_dict = {"CohortID"   : cohort,
                            "Profit"     : profit_route,
                            "Route"    : route_list}
                
                
                day_list.append(cohort_dict)


            days[str(day + 1)] = day_list



        results = {
            "Instance": inputData.main_tasks_path.split("/")[-1].split(".")[0],
            "Objective": self.TotalProfit,
            "NumberOfAllTasks": self.TotalTasks,
            "UseMainTasks" : True,
            "Days" : days
    }

        # Write the dictionary to a JSON file
        filename = f"solution_{inputData.main_tasks_path.split('/')[-1].split('.')[0]}.json"

        # Pfad zu der Datei im Ordner data/Results
        filepath = os.path.join(file_path, filename)

        # JSON-Datei erstellen und speichern
        with open(filepath, 'w') as json_file:
            json.dump(results, json_file, indent=2)

        print(f"JSON file has been created at {filepath}")


    @property
    def UnusedTasks(self) -> set[int]: 
        ''' Returns the set of unused tasks'''

        return self._unusedTasks

    @property
    def TotalProfit(self) -> int: 
        ''' Returns Total Profit of Tour'''

        return self._totalProfit
    
    @property
    def TotalTasks(self) -> int: 
        ''' Returns Total Number of Tasks'''

        return self._totalTasks
    
    @property
    def StartTimes(self) -> dict[str, list[list[int]]]: 
        ''' Returns Total Start Times of Tour'''

        return self._startTimes
    
    @property
    def WaitingTime(self) -> int: 
        """Retutns the waiting time of the solution"""

        return self._waitingTime
    
    @property
    def EndTimes(self) -> dict[str, list[list[int]]]: 
        ''' Returns Total End Times of Tour'''

        return self._endTimes
    
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

    def GetHighestProfitSolution(self) -> Solution:
        ''' Sort all the solutions in regard to their makespan and return the solution with the lowest makespan'''
        self.Solutions.sort(key = lambda solution: solution.TotalProfit) # sort solutions according to Profit

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