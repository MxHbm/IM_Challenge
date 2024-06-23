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
    def __init__(self, inputData:InputData, seed:int, no_lots_boolean:bool = False):
        self.InputData = inputData
        self.Seed = seed
        self.RNG = numpy.random.default_rng(self.Seed)
        self.EvaluationLogic = EvaluationLogic(inputData)
        self.SolutionPool = SolutionPool()
        self.runTime = {}
        self.no_lots = no_lots_boolean
        
        self.ConstructiveHeuristic = ConstructiveHeuristics(self.EvaluationLogic, self.SolutionPool, self.no_lots)      

    def Initialize(self, OptimizationAlgorithm: ImprovementAlgorithm):
        ''' Probably Alternative to other two algorithms by calling an optimization algorithm'''
        
        self.OptimizationAlgorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
    
    def ConstructionPhase(self, constructiveSolutionMethod:str) -> Solution:
        ''' Find one start solution by using the chosen constructive heuristic'''

        self.ConstructiveHeuristic.Run(self.InputData, constructiveSolutionMethod)

        bestInitalSolution = self.SolutionPool.GetLowestMakespanSolution()
        self.EvaluationLogic.DefineStartEnd(bestInitalSolution)
        print("Constructive solution found.")
        print(bestInitalSolution)

        return bestInitalSolution

    def ImprovementPhase(self, startSolution:Solution, algorithm:ImprovementAlgorithm) -> None:
        ''' Start the improvement phase by choosing a algorithm'''

        starttime = time.time()

        algorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
        bestSolution = algorithm.Run(startSolution)

        self.EvaluationLogic.DefineStartEnd(bestSolution)
        print("Best found Solution.")
        print(bestSolution)

        endtime = time.time()
        self.RunTime = endtime - starttime

    def RunLocalSearch(self, constructiveSolutionMethod:str, algorithm:ImprovementAlgorithm) -> None:
        ''' Run local search with chosen algorithm and neighborhoods'''

        starttime = time.time()
        startSolution = self.ConstructionPhase(constructiveSolutionMethod)

        self.ImprovementPhase(startSolution, algorithm)

        endtime = time.time()
        self.RunTime = endtime - starttime

    def EvalPFSP(self, individual:list[int]) -> int:
        ''' Get the makespan of an indivual chosen permutation'''

        solution = Solution(self.InputData.InputJobs, individual)
        self.EvaluationLogic.DefineStartEnd(solution)
        return solution.Makespan



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
    
