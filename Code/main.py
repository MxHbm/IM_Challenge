from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import cProfile
import pstats
import pandas as pd


main_tasks = True

main_tasks_string = str(main_tasks) 

if main_tasks:

    instances = ['7_8_1']#, '7_5_1', '7_5_2', '7_8_1', '7_8_2']#, '7_10_1', '7_10_2']
else:
    instances = ['7_2_1']#, '7_8_1', '7_10_1']


print('______________________________________________________________________')

runtimes = dict()

def main_single_run():

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
                                                    neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        

        neighborhoodLocalSearch2 = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['ReplaceDelta'])
        
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = 60,
                                jobs_to_remove=4,
                                sublists_to_modify=3,
                                threshold1 = 2,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'FirstImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )
        

        Adaptive_ILS = Adaptive_IteratedLocalSearch(inputData=data,
                                maxRunTime = 60,
                                jobs_to_remove=3,
                                sublists_to_modify=3,
                                threshold1 = 2,
                                score_threshold= 1000,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'FirstImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit'])
        
        SA_LS = SimulatedAnnealingLocalSearch(
            inputData=data,
            start_temperature = 1000,
            min_temperature = 1e-50,
            temp_decrease_factor=0.99,
            maxRunTime=60*60,
            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute'],
            neighborhoodTypesProfit = ['Insert','ReplaceProfit']
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
       
        solver.RunIteratedLocalSearch(
            numberParameterCombination=1,
            main_tasks=True,
            algorithm_LS=neighborhoodLocalSearch2,
            algorithm_ILS=Adaptive_ILS
        )

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
            algorithm_LS=neighborhoodLocalSearch2,
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


def main_parameterstudy():

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        solver = Solver(data, 1008)

        # Full parameter study
        results = []
        jobs_to_remove_list = [3,9]
        sublists_to_modify_list = [2,5]
        consecutive_to_remove_list = [3 ,6]
        start_temperature_list = [250,1000]
        temp_decrease_factor_list = [0.95]
        maxInnerLoop_list = [9,45]
        maxIterationsWithoutImprovement_list = [4, 14]
        neighborhoodEvaluationStrategyDelta_list = ['FirstImprovement', 'BestImprovement']

        # Reduced parameter study
        results = []
        jobs_to_remove_list = [9]
        sublists_to_modify_list = [5]
        consecutive_to_remove_list = [3 ,6]
        start_temperature_list = [250,1000]
        temp_decrease_factor_list = [0.95]
        maxInnerLoop_list = [9,45]
        maxIterationsWithoutImprovement_list = [3, 15]
        neighborhoodEvaluationStrategyDelta_list = ['FirstImprovement', 'BestImprovement']


        for jobs in jobs_to_remove_list:
            for sublist in sublists_to_modify_list:
                for consecutive in consecutive_to_remove_list:
                    for start_temp in start_temperature_list:
                        for temp_decrease in temp_decrease_factor_list:
                            for maxInnerLoop in maxInnerLoop_list:

                                if maxInnerLoop == 9:
                                    maxIterationsWithoutImprovement = 3
                                elif maxInnerLoop == 45:
                                    maxIterationsWithoutImprovement = 15

                                for neighborhoodEvaluationStrategyDelta in neighborhoodEvaluationStrategyDelta_list:

                                    SAILS_algorithm = SAILS(
                                        inputData=data,
                                        maxRunTime=60*15,
                                        jobs_to_remove=jobs,
                                        sublists_to_modify=sublist,
                                        consecutive_to_remove=consecutive,
                                        start_temperature=start_temp,
                                        min_temperature=1e-5,
                                        temp_decrease_factor=temp_decrease,
                                        maxInnerLoop=maxInnerLoop,
                                        maxIterationsWithoutImprovement=maxIterationsWithoutImprovement,
                                        neighborhoodEvaluationStrategyDelta=neighborhoodEvaluationStrategyDelta,
                                        neighborhoodEvaluationStrategyProfit='BestImprovement',
                                        neighborhoodTypesDelta=['SwapIntraRoute', 'TwoEdgeExchange', 'SwapInterRoute', 'ReplaceDelta'],
                                        neighborhoodTypesProfit=['Insert', 'ReplaceProfit']
                                    )

                                    solver.RunAlgorithm(
                                        numberParameterCombination=1,
                                        main_tasks=True,
                                        algorithm=SAILS_algorithm
                                    )

                   
                                    highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                                    total_profit = highest_profit_solution.TotalProfit
                                    waiting_time = highest_profit_solution.WaitingTime
                                    total_tasks = highest_profit_solution.TotalTasks

                                    results.append({
                                        'jobs_to_remove': jobs,
                                        'sublists_to_modify': sublist,
                                        'consecutive_to_remove': consecutive,
                                        'start_temperature': start_temp,
                                        'temp_decrease_factor': temp_decrease,
                                        'maxInnerLoop': maxInnerLoop,
                                        'maxIterationsWithoutImprovement': maxIterationsWithoutImprovement,
                                        'neighborhoodEvaluationStrategyDelta': neighborhoodEvaluationStrategyDelta,
                                        'TotalProfit': total_profit,
                                        'WaitingTime': waiting_time,
                                        'TotalTasks': total_tasks
                                    })
        df = pd.DataFrame(results)

        print(df)

        df.to_csv('sails_results.csv', index=False)







# Run single run or parameter study
main_single_run()

'''
# Profile the main function
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(240)  # Sort by cumulative time and show the top 10 results
'''
