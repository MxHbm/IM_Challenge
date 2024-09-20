from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import pstats
import pandas as pd
import argparse
import itertools

def main_parameterstudy_SAILS():
     
    main_tasks = True
    instances = ['7_2_1', '7_5_1', '7_8_1']
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


    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")
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
                                        main_tasks=main_tasks,
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