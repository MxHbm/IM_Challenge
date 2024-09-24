from InputData import *
from OutputData import *
from ConstructiveHeuristic import *
from ImprovementAlgorithm import *
from EvaluationLogic import *

import random
import time

class Solver:
    ''' Orchestrates all single pieces to form one strong algorithm to solve flowshop problems
    '''
    def __init__(self, inputData:InputData, seed:int):
        self.InputData = inputData
        self.Seed = seed
        self.RNG = numpy.random.default_rng(self.Seed)
        self.EvaluationLogic = EvaluationLogic(inputData)
        self.SolutionPool = SolutionPool()
        self.runTime = {}
        
        self.ConstructiveHeuristic = ConstructiveHeuristics(self.SolutionPool, self.EvaluationLogic)      

    def Initialize(self, OptimizationAlgorithm: ImprovementAlgorithm):
        ''' Probably Alternative to other two algorithms by calling an optimization algorithm'''
        
        self.OptimizationAlgorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
    
    def ConstructionPhase(self, numberParameterCombination:int = 3, main_tasks:bool = True) -> Solution:
        ''' Find one start solution by using the chosen constructive heuristic'''

        starttime = time.time()
        self.ConstructiveHeuristic.Run(self.InputData, numberParameterCombination, main_tasks)

        bestInitalSolution = self.SolutionPool.GetHighestProfitSolution()
        print("Constructive solution found.")
        print(bestInitalSolution)

        endtime = time.time()
        self.RunTime = endtime - starttime

        return bestInitalSolution

    def ImprovementPhase(self, startSolution:Solution, algorithm:ImprovementAlgorithm) -> Solution:
        ''' Start the improvement phase by choosing a algorithm'''

        algorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
        bestSolution = algorithm.Run(startSolution)

        return bestSolution

    def RunAlgorithm(self, numberParameterCombination, main_tasks, algorithm:ImprovementAlgorithm) -> None:
        ''' Run local search with chosen algorithm and neighborhoods'''

        starttime = time.time()
        startSolution = self.ConstructionPhase(numberParameterCombination, main_tasks)

        bestSolution = self.ImprovementPhase(startSolution, algorithm)


        print("Best found Solution.")
        print(bestSolution)

        endtime = time.time()
        self.RunTime = endtime - starttime




'''  
    def RunIteratedLocalSearch(self, numberParameterCombination, main_tasks, algorithm_LS:ImprovementAlgorithm, algorithm_ILS:ImprovementAlgorithm) -> None: 
        Run iterated local search with chosen algorithm and neighborhoods

        starttime = time.time()
        
        startSolution = self.ConstructionPhase(numberParameterCombination, main_tasks)

        LS_after_StartSolution, placeholder = self.ImprovementPhase(startSolution, algorithm_LS)

        final_Solution, profit_over_time = self.ImprovementPhase(LS_after_StartSolution,algorithm_ILS)

        print("Final best found Solution.")
        print(final_Solution)

        endtime = time.time()
        self.RunTime = endtime - starttime

        return profit_over_time



if __name__ == '__main__':

    data = InputData("TestInstancesJson/Large/VFR100_20_1_SIST.json") # TestInstances/Small/VFR40_10_3_SIST.txt 

    insertionLocalSearch = IterativeImprovement(data, 'FirstImprovement', ['Swap'])
    iteratedGreedy = IteratedGreedy(
    data, 
    numberJobsToRemove=2, 
    baseTemperature=1, 
    maxIterations=10, 
    localSearchAlgorithm=insertionLocalSearch
    )

    solver = Solver(data, 1008)

    print('Start IG\n')
    solver.RunLocalSearch(
        constructiveSolutionMethod='NEH',
        algorithm=iteratedGreedy)
    
'''