import json
from InputData import *
import os
import numpy as np


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
        self._waitingTimes = np.zeros((data.days, data.cohort_no))
        self._create_unused_tasks(data)

    def __str__(self):
        '''Base Function for printing out the results'''
        return "Solution:\n Route Plan: " + "\n Number of Tasks: " + str(self.TotalTasks) + "\n Total Profit: " + str(self.TotalProfit) + "\n Waiting Time: " + str(self.WaitingTime)
        ##+ str(self.RoutePlan)
    
    def _create_StartEndTimes(self, data: InputData):
        ''' Calculate the start and the end times of the tasks of the given solution'''
        
        self._startTimes = {}
        self._endTimes = {}

        day_index = 0
        for day in self._route_plan.values():
            cohort_list_start = []
            cohort_list_end = []
            for cohort in day:
                if len(cohort) > 0:  # Überprüfen, ob die Kohorte Aufträge enthält
                    route_list_start = [0]
                    route_list_end = [0]

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

            # Nur speichern, wenn die Liste nicht leer ist
            if cohort_list_start and cohort_list_end:
                self._startTimes[day_index] = cohort_list_start
                self._endTimes[day_index] = cohort_list_end
            
            day_index += 1
    


    def add_unused_Task(self, task_id:int) -> None:
        '''Adds one task id to the set of unused tasks'''

        self._unusedTasks.add(task_id)    

    def remove_unused_Task(self, task_id:int) -> None:
        '''Remove one task id to the set of unused tasks'''

        self._unusedTasks.remove(task_id)      

    def setRoutePlan(self, route_plan, data:InputData) -> None:
        ''' Sets a new route plan to the given solution'''
        self._route_plan = route_plan

    def setRoutePlanNewUnusedTasks(self, route_plan, data:InputData) -> None:
        ''' Sets a new route plan to the given solution'''
        self._route_plan = route_plan
        self._create_unused_tasks(data)

    def _create_unused_tasks(self, data: InputData) -> None:
        ''' Create an initial list of all unused tasks '''
        
        # Create a list of all task numbers
        self._unusedTasks = [task.no for task in data.allTasks]
        
        # Iterate through the route plan and remove used tasks
        for day, cohorts in self._route_plan.items():
            for cohort in cohorts:
                for task in cohort:
                    if task in self._unusedTasks:
                        self._unusedTasks.remove(task)  # Remove the task from the list if it's in the unused list

    def setTotalProfit(self, new_profit) -> None:
        ''' Sets a new profit to the given solution'''
        self._totalProfit = new_profit

    def setTotalTasks(self, new_tasks) -> None:
        ''' Sets a new number of tasks to the given solution'''
        self._totalTasks = new_tasks

    def setWaitingTime(self, new_waiting_time) -> None:
        ''' Sets a new waiting time to the given solution'''
        self._waitingTime = new_waiting_time

    
    def WriteSolToJson(self, file_path:str, inputData: InputData, main_tasks:bool) -> None:
        ''' Write the solution to a json file'''

        self._create_StartEndTimes(inputData)
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
 
                if self.RoutePlan[day][cohort] != []:    
                    cohort_dict = {"CohortID"   : cohort,
                                "Profit"     : profit_route,
                                "Route"    : route_list}
                
                
                    day_list.append(cohort_dict)


            days[str(day + 1)] = day_list



        results = {
            "Instance": inputData.main_tasks_path.split("/")[-1].split(".")[0],
            "Objective": self.TotalProfit,
            "NumberOfAllTasks": self.TotalTasks,
            "UseMainTasks" : main_tasks,
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
    def WaitingTimes(self) -> int: 
        """Retutns the waiting times of each route of the solution"""

        return self._waitingTimes
    
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
        self.Solutions.sort(key=lambda solution: (solution.TotalProfit, solution.WaitingTime), reverse=True) # sort solutions according to Profit and waiting time

        return self.Solutions[0]
    
    def GetHighestWaitingTimeSolution(self) -> Solution:
        ''' Sort all the solutions in regard to their makespan and return the solution with the lowest makespan'''
        self.Solutions.sort(key=lambda solution: (solution.WaitingTime), reverse=True) # sort solutions according to Profit and waiting time

        return self.Solutions[0]
