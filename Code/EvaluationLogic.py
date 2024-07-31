import numpy 
from copy import deepcopy
from InputData import InputData
from OutputData import Solution

class EvaluationLogic:
    ''' Evalution Objects to calculate objectives of the given solutions'''

    def __init__(self, inputData:InputData):
        ''' Initialize by addinbg data'''
        self._data = inputData      


    def evaluateSolution(self, currentSolution:Solution) -> None:
        ''' Calculates the profit of the given solution'''
        
        sum_profit = 0
        sum_tasks = 0

        for day in range(self._data.days):
            for cohort in range(self._data.cohort_no):
                sum_tasks += len(currentSolution.RoutePlan[day][cohort])
                for task_no in currentSolution.RoutePlan[day][cohort]:
                    sum_profit += self._data.allTasks[task_no].profit

        currentSolution.setTotalProfit(sum_profit) 
        currentSolution.setTotalTasks(sum_tasks)

        self.calculateWaitingTime(currentSolution)

    def calculateWaitingTime(self, currentSolution:Solution) -> None: 
        ''' Calculates the waiting time of the given solution'''

        waiting_time = self._data.cohort_no * self._data.days * self._data.maxRouteDuration

        for day in range(self._data.days):
            for cohort in range(self._data.cohort_no):
                previous_task = 0
                for task_i in currentSolution.RoutePlan[day][cohort]:
                    waiting_time -= self._data.distances[previous_task][task_i]
                    waiting_time -= self._data.allTasks[task_i].service_time
                    previous_task = task_i

                waiting_time -= self._data.distances[previous_task][0]

        currentSolution.setWaitingTime(waiting_time)


    def CalculateSwap1Delta(self, move): 
        '''Calculates the delta of the given swap move'''

        # Retrieve the route for the given day and cohort
        route = move.Route[move.Day][move.Cohort]
        precessors = []
        successors = []

        # List of indices to process
        indexes = [move.indexA, move.indexB]

        # Iterate over the indices to determine predecessors and successors
        for index in indexes:
            if index == 0:
                precessors.append(0)
                successors.append(route[index + 1])
            elif index == len(route) - 1:
                precessors.append(route[index - 1])
                successors.append(0)
            else: 
                precessors.append(route[index - 1])
                successors.append(route[index + 1])

        # Calculate the delta using the distance subtraction method
        delta = self.calclateDistanceSubtraction(move, successors, precessors)
        #print("Delta: ",delta)

        return delta
    
    def calclateDistanceSubtraction(self, move, successor_list, precessor_list):
        '''Calculates the distance subtraction of the given lists'''

        # Calculate the original distances
        distance_old = self._data.distances[precessor_list[0]][move.TaskA] + self._data.distances[move.TaskA][successor_list[0]] \
                        + self._data.distances[precessor_list[1]][move.TaskB] + self._data.distances[move.TaskB][successor_list[1]]
            
        # Calculate the new distances after swap
        distance_new = self._data.distances[precessor_list[1]][move.TaskA] + self._data.distances[move.TaskA][successor_list[1]] \
                        + self._data.distances[precessor_list[0]][move.TaskB] + self._data.distances[move.TaskB][successor_list[0]]
        
        difference = distance_new - distance_old + (self._data.allTasks[move.TaskB].service_time - self._data.allTasks[move.TaskA].service_time)

        # Return the difference between the new and original distances
        return difference
    

    def listUnusedTasks(self, routePlan):

        unused_tasks = []
        used_tasks = []
        for routes in routePlan.values():
            for route in routes:
                for task in route:
                    used_tasks.append(task)

        for task in range(len(self._data.optionalTasks)):
            if task not in used_tasks and task != 0:
                unused_tasks.append(task)

        return unused_tasks