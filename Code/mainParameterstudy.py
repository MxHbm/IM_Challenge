from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import pstats
import pandas as pd
import argparse


main_tasks = True

if main_tasks:

    instances = ['7_2_1',]
else:
    instances = ['7_5_1']


def main_parameterstudy_SAILS():
     

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



def main_parameterstudy_SA_LS():


    runtimePerParameterCombination = 60*15

    # Full parameter study
    results = []
    start_temperature_list = [100]#[100,1000,10000]
    min_temperature_list = [1e-10]#[1e-10, 1e-20, 1e-40]
    temp_decrease_factor_list= [0.99]#[0.9, 0.95, 0.99]

    combinations_not_run_yet = [(100, 1e-10, 0.9),
                            (100, 1e-10, 0.95),
                            (100, 1e-10, 0.99),
                            (100, 1e-20, 0.9),
                            (100, 1e-40, 0.9),
                            (1000, 1e-10, 0.9),
                            (1000, 1e-10, 0.95),
                            (1000, 1e-10, 0.99),
                            (1000, 1e-20, 0.9),
                            (1000, 1e-40, 0.9),
                            (10000, 1e-10, 0.9),
                            (10000, 1e-10, 0.95),
                            (10000, 1e-10, 0.99),
                            (10000, 1e-20, 0.9),
                            (10000, 1e-40, 0.9)]

    # Reduced parameter study

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
                        'Instance': i,
                        'start_temperature': temp,
                        'min_temperature': minTemp,
                        'temp_decrease_factor': factor,
                        'TotalProfit': total_profit,
                        'WaitingTime': waiting_time,
                        'TotalTasks': total_tasks,
                        'Iterations' : iterations,
                        'RunTime' : round(solver.RunTime,4),
                        'TimeLimit': runtimePerParameterCombination
                    })

    df = pd.DataFrame(results)

    df.to_csv('sa_ls_results_3.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run parameter study scripts.")
    parser.add_argument(
        "--function", 
        choices=["SAILS", "SA_LS"], 
        required=True, 
        help="Specify which parameter study function to run: 'SAILS' or 'SA_LS'"
    )
    args = parser.parse_args()

    if args.function == "SAILS":
        main_parameterstudy_SAILS()
    elif args.function == "SA_LS":
        main_parameterstudy_SA_LS()