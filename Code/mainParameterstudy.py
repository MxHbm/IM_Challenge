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
    
import argparse
import itertools

def main_parameterstudy_SAILS():
     
    main_tasks = True
    instances = ['7_2_1', '7_5_1', '7_8_1']
    # Full parameter study
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

def main_parameterstudy_SA_LS(pair_index):

    instances = ['7_2_1', '7_5_1', '7_8_1']
    start_temperature_list = [100,1000,10000]
    min_temperature_list = [1e-10, 1e-20, 1e-40]
    temp_decrease_factor_list= [0.9, 0.95, 0.99]
    maxRandomAttempts = [100,1000]

    # Create all combinations of parameters excluding maxRandomAttempts=10000
    parameter_combinations = list(itertools.product(instances,start_temperature_list, min_temperature_list, temp_decrease_factor_list, maxRandomAttempts))

    # Divide the list into 4 parts
    # Dynamically divide the list of combinations into 4 roughly equal parts
    part1 = parameter_combinations[:40]
    part2 = parameter_combinations[40:80]
    part3 = parameter_combinations[80:121]
    part4 = parameter_combinations[121:]
    parts = [part1,part2,part3,part4]

    # Ensure the provided pair_index is valid
    if pair_index < 0 or pair_index > 3:
        print("ERROR: Please provide a pair index between 0 and 3.")
        sys.exit(1)
    
    # Get the combinations for the specified part
    combinations = parts[pair_index]

    main_tasks = True
    runtimePerParameterCombination = 60 * 15  # 15 minutes

    print(f"Running part {pair_index}, {len(combinations)} combinations.")
    print(Path.cwd().parent)
    results = []

    for instance,temp, minTemp,factor, maxMoves in combinations:

        print("Instance: ", instance)
        data = InputData("Instance"+instance+".json")

        solver = Solver(data, 1008)

        SA_LS = SimulatedAnnealingLocalSearch(
                inputData=data,
                start_temperature = temp,
                min_temperature = minTemp,
                temp_decrease_factor=factor,
                maxRunTime= runtimePerParameterCombination,
                maxRandomMoves=maxMoves,
                neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )


        iterations = solver.RunAlgorithm(
            numberParameterCombination=1,
            main_tasks=main_tasks,
            algorithm=SA_LS
        )


        highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
        total_profit = highest_profit_solution.TotalProfit
        waiting_time = highest_profit_solution.WaitingTime
        total_tasks = highest_profit_solution.TotalTasks

        results.append({
            'Instance': instance,
            'start_temperature': temp,
            'min_temperature': minTemp,
            'temp_decrease_factor': factor,
            'TotalProfit': total_profit,
            'WaitingTime': waiting_time,
            'TotalTasks': total_tasks,
            'Iterations' : iterations,
            'RunTime' : round(solver.RunTime,4),
            'TimeLimit': runtimePerParameterCombination,
            'MaxRandomMoves': maxMoves
        })


    df = pd.DataFrame(results)

    df.to_csv(f'sa_ls_results_{pair_index}.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run parameter study scripts.")
    parser.add_argument(
        "--function", 
        choices=["SAILS", "SA_LS"], 
        required=True, 
        help="Specify which parameter study function to run: 'SAILS' or 'SA_LS'"
    )
    parser.add_argument(
        "--index", 
        type=int, 
        choices=range(0, 4), 
        required=True, 
        help="Specify the part index (0-3) to run the parameter study."
    )

    args = parser.parse_args()

    if args.function == "SAILS":
        main_parameterstudy_SAILS(args.index)
    elif args.function == "SA_LS":
        main_parameterstudy_SA_LS(args.index)

