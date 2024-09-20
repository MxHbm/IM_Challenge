from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import pstats
import pandas as pd



def main_parameterstudy_ILS():

    runTimePerParameterCombination = 60*6
     
    results = []
    sublists_to_modify_list = [2]
    consecutive_to_remove_list = [3]
    threshold_list = [3]
    neighborhoodEvaluationStrategyDelta_list = 'FirstImprovement'

    main_tasks = [True, False]

    for main_tasks in main_tasks:
        if main_tasks:
            instances = ['7_2_1', '7_5_1', '7_8_1']
        else:
            instances = ['7_5_1']
        for i in instances:
            for sublist in sublists_to_modify_list:
                for consecutive in consecutive_to_remove_list:
                            for threshold in threshold_list:


                                    print("Instance: ", i)
                                    print("Main Tasks: ", main_tasks)
                                    print("Sublists to modify: ", sublist)
                                    print("Consecutive to remove: ", consecutive)
                                    print("Threshold: ", threshold)

                                    data = InputData("Instance"+i+".json")
                                    solver = Solver(data, 1008)

                                    neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                            neighborhoodEvaluationStrategy= 'BestImprovement',
                                                            neighborhoodTypes=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta','Insert','ReplaceProfit'])

                                    ILS = IteratedLocalSearch(  inputData=data,
                                                                maxRunTime = runTimePerParameterCombination,
                                                                sublists_to_modify=sublist,
                                                                consecutive_to_remove=consecutive,
                                                                threshold1 = threshold,
                                                                neighborhoodEvaluationStrategyDelta = neighborhoodEvaluationStrategyDelta_list,
                                                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                                                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
                                                            )


                                    itertion = solver.RunIteratedLocalSearch(
                                        numberParameterCombination=1,
                                        main_tasks=main_tasks,
                                        algorithm_LS=neighborhoodLocalSearch,
                                        algorithm_ILS=ILS
                                    )   
                                    highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                                    total_profit = highest_profit_solution.TotalProfit
                                    waiting_time = highest_profit_solution.WaitingTime
                                    total_tasks = highest_profit_solution.TotalTasks

                                    results.append({
                                        'Instance': i,
                                        'MainTasks': main_tasks,
                                        'sublists_to_modify': sublist,
                                        'consecutive_to_remove': consecutive,
                                        'threshold': threshold,
                                        'neighborhoodEvaluationStrategyDelta': neighborhoodEvaluationStrategyDelta_list,
                                        'TotalProfit': total_profit,
                                        'WaitingTime': waiting_time,
                                        'TotalTasks': total_tasks,
                                        'Iterations': itertion,
                                        'RunTime': round(solver.RunTime, 4),
                                        'TimeLimit': runTimePerParameterCombination
                                        
                                })
    df = pd.DataFrame(results)

    print(df)

    df.to_csv('ils_results_FirstImprovement.csv', index=False)

def main_parameterstudy_SAILS():
     
    runTimePerParameterCombination = 60*15
    
    results = []
    sublists_to_modify_list = [2]
    consecutive_to_remove_list = [3]
    start_temperature_list = [1000]
    temp_decrease_factor_list = [0.95]
    maxInnerLoop_list = [10]

    main_tasks = [True]

    for main_tasks in main_tasks:
        if main_tasks:
            instances = ['7_2_1', '7_5_1', '7_8_1']
        for i in instances:
            for sublist in sublists_to_modify_list:
                for consecutive in consecutive_to_remove_list:
                    for start_temp in start_temperature_list:
                        for temp_decrease in temp_decrease_factor_list:
                            for maxInnerLoop in maxInnerLoop_list:
                                maxIterationsWithoutImprovement = 0.3 * maxInnerLoop

                                
                                print("Instance: ", i)
                                print("Main Tasks: ", main_tasks)
                                print("Sublists to modify: ", sublist)
                                print("Consecutive to remove: ", consecutive)
                                print("Start temperature: ", start_temp)
                                print("Temp decrease factor: ", temp_decrease)
                                print("Max Inner Loop: ", maxInnerLoop)
                                print("Max Iterations Without Improvement: ", maxIterationsWithoutImprovement)

                                data = InputData("Instance"+i+".json")
                                solver = Solver(data, 1008)

                                SAILS_algorithm = SAILS(
                                    inputData=data,
                                    maxRunTime=runTimePerParameterCombination,
                                    sublists_to_modify=sublist,
                                    consecutive_to_remove=consecutive,
                                    start_temperature=start_temp,
                                    min_temperature=1e-5,
                                    temp_decrease_factor=temp_decrease,
                                    maxInnerLoop=maxInnerLoop,
                                    maxIterationsWithoutImprovement=maxIterationsWithoutImprovement,
                                    neighborhoodEvaluationStrategyDelta='FirstImprovement',
                                    neighborhoodEvaluationStrategyProfit='BestImprovement',
                                    neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute', 'TwoEdgeExchange', 'ReplaceDelta'],
                                    neighborhoodTypesProfit=['Insert', 'ReplaceProfit']
                                )

                                itertaion = solver.RunAlgorithm(
                                    numberParameterCombination=3,
                                    main_tasks=main_tasks,
                                    algorithm=SAILS_algorithm
                                )

            
                                highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                                total_profit = highest_profit_solution.TotalProfit
                                waiting_time = highest_profit_solution.WaitingTime
                                total_tasks = highest_profit_solution.TotalTasks

                                results.append({
                                    'Instance': i,
                                    'MainTasks': main_tasks,
                                    'sublists_to_modify': sublist,
                                    'consecutive_to_remove': consecutive,
                                    'start_temperature': start_temp,
                                    'temp_decrease_factor': temp_decrease,
                                    'maxInnerLoop': maxInnerLoop,
                                    'maxIterationsWithoutImprovement': maxIterationsWithoutImprovement,
                                    'neighborhoodEvaluationStrategyDelta': 'FirstImprovement',
                                    'TotalProfit': total_profit,
                                    'WaitingTime': waiting_time,
                                    'TotalTasks': total_tasks,
                                    'Iterations': itertaion,
                                    'RunTime': round(solver.RunTime, 4),
                                    'TimeLimit': runTimePerParameterCombination

                                })

    df = pd.DataFrame(results)

    print(df)

    df.to_csv('sails_results_non_adaptive.csv', index=False)

def main_parameterstudy_Adaptive_SAILS():
     
    runTimePerParameterCombination = 60*15
    
    results = []
    sublists_to_modify_list = [2]
    consecutive_to_remove_list = [3]
    start_temperature_list = [1000]
    temp_decrease_factor_list = [0.95]
    maxInnerLoop_list = [10]

    main_tasks = [True]

    for main_tasks in main_tasks:
        if main_tasks:
            instances = ['7_2_1', '7_5_1', '7_8_1']
        for i in instances:
            for sublist in sublists_to_modify_list:
                for consecutive in consecutive_to_remove_list:
                    for start_temp in start_temperature_list:
                        for temp_decrease in temp_decrease_factor_list:
                            for maxInnerLoop in maxInnerLoop_list:
                                maxIterationsWithoutImprovement = 0.3 * maxInnerLoop

                                
                                print("Instance: ", i)
                                print("Main Tasks: ", main_tasks)
                                print("Sublists to modify: ", sublist)
                                print("Consecutive to remove: ", consecutive)
                                print("Start temperature: ", start_temp)
                                print("Temp decrease factor: ", temp_decrease)
                                print("Max Inner Loop: ", maxInnerLoop)
                                print("Max Iterations Without Improvement: ", maxIterationsWithoutImprovement)

                                data = InputData("Instance"+i+".json")
                                solver = Solver(data, 1008)

                                Adaptive_SAILS_algorithm = Adaptive_SAILS(
                                    inputData=data,
                                    maxRunTime=runTimePerParameterCombination,
                                    sublists_to_modify=sublist,
                                    consecutive_to_remove=consecutive,
                                    start_temperature=start_temp,
                                    min_temperature=1e-5,
                                    temp_decrease_factor=temp_decrease,
                                    maxInnerLoop=maxInnerLoop,
                                    maxIterationsWithoutImprovement=maxIterationsWithoutImprovement,
                                    neighborhoodEvaluationStrategyDelta='FirstImprovement',
                                    neighborhoodEvaluationStrategyProfit='BestImprovement',
                                    neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute', 'TwoEdgeExchange', 'ReplaceDelta'],
                                    neighborhoodTypesProfit=['Insert', 'ReplaceProfit']
                                )

                                itertaion = solver.RunAlgorithm(
                                    numberParameterCombination=1,
                                    main_tasks=main_tasks,
                                    algorithm=Adaptive_SAILS_algorithm
                                )

            
                                highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                                total_profit = highest_profit_solution.TotalProfit
                                waiting_time = highest_profit_solution.WaitingTime
                                total_tasks = highest_profit_solution.TotalTasks

                                results.append({
                                    'Instance': i,
                                    'MainTasks': main_tasks,
                                    'sublists_to_modify': sublist,
                                    'consecutive_to_remove': consecutive,
                                    'start_temperature': start_temp,
                                    'temp_decrease_factor': temp_decrease,
                                    'maxInnerLoop': maxInnerLoop,
                                    'maxIterationsWithoutImprovement': maxIterationsWithoutImprovement,
                                    'neighborhoodEvaluationStrategyDelta': 'FirstImprovement',
                                    'TotalProfit': total_profit,
                                    'WaitingTime': waiting_time,
                                    'TotalTasks': total_tasks,
                                    'Iterations': itertaion,
                                    'RunTime': round(solver.RunTime, 4),
                                    'TimeLimit': runTimePerParameterCombination

                                })

    df = pd.DataFrame(results)

    print(df)

    df.to_csv('sails_results_adaptive.csv', index=False)



def main_parameterstudy_SAILS5():
     
    runTimePerParameterCombination = 60*6
    
    results = []
    sublists_to_modify_list = [1,2,3]
    consecutive_to_remove_list = [2,3,4]
    start_temperature_list = [100]
    temp_decrease_factor_list = [0.975, 0.99]
    maxInnerLoop_list = [5,10]

    main_tasks = [True, False]

    for main_tasks in main_tasks:
        if main_tasks:
            instances = ['7_8_1']
        else:
            instances = ['7_5_1']
        for i in instances:
            for sublist in sublists_to_modify_list:
                for consecutive in consecutive_to_remove_list:
                    for start_temp in start_temperature_list:
                        for temp_decrease in temp_decrease_factor_list:
                            for maxInnerLoop in maxInnerLoop_list:
                                maxIterationsWithoutImprovement = 0.3 * maxInnerLoop

                                if sublist == 2 and consecutive == 3:
                                    continue
                                if sublist == 2 and start_temp == 100:
                                    continue
                                if sublist == 2 and temp_decrease == 0.99:
                                    continue
                                if sublist == 2 and maxInnerLoop == 10:
                                    continue
                                if consecutive == 3 and start_temp == 100:
                                    continue
                                if consecutive == 3 and temp_decrease == 0.99:
                                    continue
                                if consecutive == 3 and maxInnerLoop == 10:
                                    continue
                                if start_temp == 100 and temp_decrease == 0.99:
                                    continue
                                if start_temp == 100 and maxInnerLoop == 10:
                                    continue
                                if temp_decrease == 0.99 and maxInnerLoop == 10:
                                    continue

                                
                                print("Instance: ", i)
                                print("Main Tasks: ", main_tasks)
                                print("Sublists to modify: ", sublist)
                                print("Consecutive to remove: ", consecutive)
                                print("Start temperature: ", start_temp)
                                print("Temp decrease factor: ", temp_decrease)
                                print("Max Inner Loop: ", maxInnerLoop)
                                print("Max Iterations Without Improvement: ", maxIterationsWithoutImprovement)
                                data = InputData("Instance"+i+".json")
                                solver = Solver(data, 1008)

                                SAILS_algorithm = SAILS(
                                    inputData=data,
                                    maxRunTime=runTimePerParameterCombination,
                                    sublists_to_modify=sublist,
                                    consecutive_to_remove=consecutive,
                                    start_temperature=start_temp,
                                    min_temperature=1e-5,
                                    temp_decrease_factor=temp_decrease,
                                    maxInnerLoop=maxInnerLoop,
                                    maxIterationsWithoutImprovement=maxIterationsWithoutImprovement,
                                    neighborhoodEvaluationStrategyDelta='BestImprovement',
                                    neighborhoodEvaluationStrategyProfit='BestImprovement',
                                    neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute', 'TwoEdgeExchange', 'ReplaceDelta'],
                                    neighborhoodTypesProfit=['Insert', 'ReplaceProfit']
                                )

                                itertaion = solver.RunAlgorithm(
                                    numberParameterCombination=1,
                                    main_tasks=main_tasks,
                                    algorithm=SAILS_algorithm
                                )

            
                                highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                                total_profit = highest_profit_solution.TotalProfit
                                waiting_time = highest_profit_solution.WaitingTime
                                total_tasks = highest_profit_solution.TotalTasks

                                results.append({
                                    'Instance': i,
                                    'MainTasks': main_tasks,
                                    'sublists_to_modify': sublist,
                                    'consecutive_to_remove': consecutive,
                                    'start_temperature': start_temp,
                                    'temp_decrease_factor': temp_decrease,
                                    'maxInnerLoop': maxInnerLoop,
                                    'maxIterationsWithoutImprovement': maxIterationsWithoutImprovement,
                                    'TotalProfit': total_profit,
                                    'WaitingTime': waiting_time,
                                    'TotalTasks': total_tasks,
                                    'Iterations': itertaion,
                                    'RunTime': round(solver.RunTime, 4),
                                    'TimeLimit': runTimePerParameterCombination

                                })

    df = pd.DataFrame(results)

    print(df)

    df.to_csv('sails_results5.csv', index=False)

def main_parameterstudy_SA_LS():


    runtimePerParameterCombination = 60*15

    # Full parameter study
    results = []
    start_temperature_list = [100,1000,10000]
    min_temperature_list = [1e-20, 1e-40, 1e-60]
    temp_decrease_factor_list=[0.9, 0.95, 0.99]

    # Reduced parameter study


    start_temperature_list = [100,1000]
    min_temperature_list = [1e-50, 1e-80]
    temp_decrease_factor_list=[0.999]
    

    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        for temp in start_temperature_list:
            for minTemp in min_temperature_list:
                for factor in temp_decrease_factor_list:

                    solver = Solver(data, 1008)
             
                    SA_LS = SimulatedAnnealingLocalSearch(
                            inputData=data,
                            start_temperature = temp,
                            min_temperature = minTemp,
                            temp_decrease_factor=factor,
                            maxRunTime= runtimePerParameterCombination,
                            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                            neighborhoodTypesProfit= ['Insert','ReplaceProfit']
                            )


                    solver.RunAlgorithm(
                        numberParameterCombination=1,
                        main_tasks=main_tasks,
                        algorithm=SA_LS
                    )


                    highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
                    total_profit = highest_profit_solution.TotalProfit
                    waiting_time = highest_profit_solution.WaitingTime
                    total_tasks = highest_profit_solution.TotalTasks

                    results.append({
                        'Instance': i,
                        'start_temperature': temp,
                        'min_temperature': minTemp,
                        'temp_decrease_factor': factor,
                        'TotalProfit': total_profit,
                        'WaitingTime': waiting_time,
                        'TotalTasks': total_tasks,
                        'RunTime': runtimePerParameterCombination
                    })
    df = pd.DataFrame(results)

    print(df)

    df.to_csv('sa_ls_results.csv', index=False)


main_parameterstudy_SAILS()