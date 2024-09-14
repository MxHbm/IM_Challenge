from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import cProfile
import pstats


main_tasks = True

main_tasks_string = str(main_tasks) 
algorithm = 'Iterative' #Iterative or ILS

if main_tasks:
    instances = ['7_2_1']#, '7_5_1', '7_5_2', '7_8_1', '7_8_2']#, '7_10_1', '7_10_2']
else:
    instances = ['7_2_1']#, '7_8_1', '7_10_1']


print('______________________________________________________________________')

runtimes = dict()

def main():

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        '''
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
        '''
        solver = Solver(data, 1008)

        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'FirstImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute'])
        

        neighborhoodLocalSearch2 = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = 100,
                                jobs_to_remove=3,
                                sublists_to_modify=3,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategy= 'BestImprovement',
                                neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        
        SA_LS = SimulatedAnnealingLocalSearch(
            inputData=data,
            start_temperature = 1000,
            min_temperature = 1e-50,
            temp_decrease_factor=0.99,
            maxRunTime=120,
            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
            neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        )

        SAILS_algorithm = SAILS(inputData=data,
                                maxRunTime = 100,
                                jobs_to_remove=3,
                                sublists_to_modify=3,
                                consecutive_to_remove=3,
                                start_temperature = 1000,
                                min_temperature = 1e-50,
                                temp_decrease_factor=0.99,
                                maxInnerLoop = 10,
                                maxIterationsWithoutImprovement = 2,
                                neighborhoodEvaluationStrategy= 'BestImprovement',
                                neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit']

        )
        solver.RunAlgorithm(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm = neighborhoodLocalSearch2
        )

        #Iterated Local Search
        '''
        solver.RunIteratedLocalSearch(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm_LS=neighborhoodLocalSearch,
            algorithm_ILS=ILS
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
        '''
        ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


        ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=1, main_tasks = main_tasks)


        solution = pool.GetHighestProfitSolution()

        main_tasks_string = str(main_tasks) 
        solution.WriteSolToJson(Path.cwd().parent / "Data" / ("Main_Tasks = " + main_tasks_string) /"Results_Greedy",data, main_tasks)

        print(solution)


        neighborhoodTypesDelta = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta']
        neighborhoodTypesProfit = ['Insert','ReplaceProfit']

        if algorithm == 'ILS':
            iteratedLocalSearch = IteratedLocalSearch(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['Insert','TwoEdgeExchange','SwapInterRoute','Insert','ReplaceProfit'])

            iteratedLocalSearch.Initialize(evaluationLogic,pool, rng = None)
            start_time = time.time()
            solution = iteratedLocalSearch.Run(solution)
            end_time = time.time()


        elif algorithm == 'SAILS':
            sails = SAILS(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
            sails.Initialize(evaluationLogic,pool, rng = None)
            start_time = time.time()
            solution = sails.Run(solution)
            end_time = time.time()
        


        elif algorithm == 'Iterative':
            iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['TwoEdgeExchange','Insert'])   
            iterativeImpro.Initialize(evaluationLogic,pool, rng = None)
            start_time = time.time()
            solution = iterativeImpro.Run(solution)
            end_time = time.time()



        elif algorithm == 'SimulatedAnnealingLocalSearch':
            simulatedAnnealingLocalSearch = SimulatedAnnealingLocalSearch(data)
            simulatedAnnealingLocalSearch.Initialize(evaluationLogic,pool, rng = None)
            start_time = time.time()
            solution = simulatedAnnealingLocalSearch.Run(solution)
            end_time = time.time()

    
        
        runtime = end_time - start_time
        
        solution.WriteSolToJson(Path.cwd().parent / "Data" / ("Main_Tasks = " + main_tasks_string) / ("Results_" + algorithm) ,data, main_tasks)

        runtimes[i] = round(runtime, 2)

        print(f"Runtime: {round(runtime, 2)} seconds")
        print('THE END')
        print('______________________________________________________________________')


    # Create a file with the runtimes
    with open(Path.cwd().parent / "Data" / ("Main_Tasks = " + main_tasks_string) / ("Results_" + algorithm) / "runtimes.txt", 'w') as f:
        for key, value in runtimes.items():
            f.write('%s:%s\n' % (key, value))

    '''

# Profile the main function
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(240)  # Sort by cumulative time and show the top 10 results

