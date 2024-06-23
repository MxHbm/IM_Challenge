import numpy 
from copy import deepcopy
from InputData import InputData
from OutputData import Solution

class EvaluationLogic:
    ''' Evalution Objects to calculate objectives of the given solutions'''

    def __init__(self, inputData:InputData):
        ''' Initialize by addinbg data'''
        self._data = inputData      


    def setProfit(self, currentSolution:Solution) -> None:
        ''' Calculates the profit of the given solution'''
        
        sum_profit = 0

        for day in range(self._data.days):
            for cohort in range(self._data.cohort_no):
                for task_no in currentSolution.RoutePlan[day][cohort]:
                    sum_profit += self._data.allTasks[task_no].profit

        currentSolution.setTotalProfit(sum_profit) 