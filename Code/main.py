from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import cProfile
import pstats
import pandas as pd


main_tasks = True

if main_tasks:

    instances = ['7_8_1']#, '7_5_1', '7_5_2', '7_8_1', '7_8_2']#, '7_10_1', '7_10_2']
else:
    instances = ['7_2_1']#, '7_8_1', '7_10_1']


print('______________________________________________________________________')

runtimes = dict()

def main():

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        solver = Solver(data, 1008)

        
        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        

        neighborhoodLocalSearch2 = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['ReplaceDelta'])
        
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = 60*10,
                                jobs_to_remove=6,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                threshold1 = 2,
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )
        

        Adaptive_ILS = Adaptive_IteratedLocalSearch(inputData=data,
                                maxRunTime = 60,
                                jobs_to_remove=3,
                                sublists_to_modify=3,
                                threshold1 = 2,
                                score_threshold= 1000,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit'])
        
        SA_LS = SimulatedAnnealingLocalSearch(
            inputData=data,
            start_temperature = 1000,
            min_temperature = 1e-40,
            temp_decrease_factor=0.99,
            maxRunTime=60*60*4,
            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
            neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )


      
        SAILS_algorithm = SAILS(inputData=data,
                                maxRunTime = 60*5,
                                jobs_to_remove=5,
                                sublists_to_modify=2,
                                consecutive_to_remove=63,
                                start_temperature = 1000,
                                min_temperature = 1e-5,
                                temp_decrease_factor=0.95,
                                maxInnerLoop = 10,
                                maxIterationsWithoutImprovement = 4,
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta =['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        )


        Adaptive_SAILS_algorithm = Adaptive_SAILS(inputData=data,
                                maxRunTime = 60*5,
                                jobs_to_remove=5,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                start_temperature = 1000,
                                min_temperature = 1e-5,
                                temp_decrease_factor=0.95,
                                maxInnerLoop = 10,
                                score_threshold = 1000,
                                maxIterationsWithoutImprovement = 4,
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta =['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        )

        solver.RunAlgorithm(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm = SAILS_algorithm
        )

        #print(f'Anzahl Iterationen: {iteration}')

        # Define the directory and file name
        output_directory = Path.cwd().parent / "Data" / "Debug"

        solver.SolutionPool.GetHighestProfitSolution().WriteSolToJson(output_directory, data, True)

        #Algorithm
        '''
        solver.RunAlgorithm(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm = ILS
        )

        '''
        #Iterated Local Search
        '''
        solver.RunIteratedLocalSearch(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm_LS=neighborhoodLocalSearch,
            algorithm_ILS=Adaptive_ILS
        )
        '''
        #Local Search
        '''
        solver.RunAlgorithm(
            numberParameterCombination= 3, 
            main_tasks= main_tasks,
            algorithm= neighborhoodLocalSearch)
        '''

        #Construction Heuristic
        '''
        solver.ConstructionPhase(
            numberParameterCombination= 3, 
            main_tasks= main_tasks,
            )
        
        '''



# Profile the main function
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(80)  # Sort by cumulative time and show the top 10 results

