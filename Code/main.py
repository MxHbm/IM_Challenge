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
                                maxRunTime = 60,
                                jobs_to_remove=4,
                                sublists_to_modify=3,
                                threshold1 = 2,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
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
                                neighborhoodEvaluationStrategyDelta = 'BestImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
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
            algorithm = SA_LS
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

'''
def main_parameterstudy_ILS():

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        

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
        jobs_to_remove_list = [2,4,6,8,10]
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
                                
                                    solver = Solver(data, 1008)

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
'''

def main_parameterstudy_SA_LS():

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        

        # Full parameter study
        results = []
        start_temperature_list = [100,1000,10000]
        min_temperature_list = [1e-20, 1e-40, 1e-60]
        temp_decrease_factor_list=[0.9, 0.95, 0.99]

        # Reduced parameter study


        start_temperature_list = [100,1000]
        min_temperature_list = [1e-50, 1e-80]
        temp_decrease_factor_list=[0.999]
    


        for temp in start_temperature_list:
            for minTemp in min_temperature_list:
                for factor in temp_decrease_factor_list:

                    solver = Solver(data, 1008)
             
                    SA_LS = SimulatedAnnealingLocalSearch(
                            inputData=data,
                            start_temperature = temp,
                            min_temperature = minTemp,
                            temp_decrease_factor=factor,
                            maxRunTime=60*60,
                            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                            neighborhoodTypesProfit= ['Insert','ReplaceProfit']
                            )


                    iterationen = solver.RunAlgorithm(
                        numberParameterCombination=1,
                        main_tasks=True,
                        algorithm=SA_LS
                    )


                    highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                    total_profit = highest_profit_solution.TotalProfit
                    waiting_time = highest_profit_solution.WaitingTime
                    total_tasks = highest_profit_solution.TotalTasks

                    results.append({
                        'start_temperature': temp,
                        'min_temperature': minTemp,
                        'temp_decrease_factor': factor,
                        'TotalIterations': iterationen,
                        'TotalProfit': total_profit,
                        'WaitingTime': waiting_time,
                        'TotalTasks': total_tasks
                    })
    df = pd.DataFrame(results)

    print(df)

    df.to_csv('sa_ls_2nd_results.csv', index=False)





# Profile the main function
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(80)  # Sort by cumulative time and show the top 10 results

