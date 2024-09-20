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
    instances = ['7_2_1', '7_2_2','7_5_1' ,'7_5_2','7_8_1' ,'7_8_2','7_10_1' ,'7_10_2']
    #instances = ['7_5_1' ,'7_5_2'] 
    #instances = ['7_8_1', '7_8_2']
else:
    instances = ['7_2_1', '7_5_1','7_8_1' ,'7_10_1']
    
import sys



print('______________________________________________________________________')

results = []

# Define your instance pairs
all_instance_pairs = [
    ['7_2_1', '7_2_2'],
    ['7_5_1', '7_5_2'],
    ['7_8_1', '7_8_2'],
    ['7_2_1', '7_5_1']
]

def main_Constructive():
    results = []
    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        solver = Solver(data, 1008)

      
        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute', 'SwapInterRoute','TwoEdgeExchange','ReplaceDelta','Insert','ReplaceProfit'])
        

        solver.ConstructionPhase(
        numberParameterCombination= 'Test', 
        main_tasks= main_tasks,
        )
        
        
        #Erstelle einen dataframe mit den ergebnissen für jede instanz
        
        results.append(
            {'Instance' :i, 
            'Profit':solver.SolutionPool.GetHighestProfitSolution().TotalProfit,
            'WaitingTime':solver.SolutionPool.GetHighestProfitSolution().WaitingTime,
            'TotalTasks':solver.SolutionPool.GetHighestProfitSolution().TotalTasks,
            #'Iterations':iteration,
            'RunTime': round(solver.RunTime,4)
            })
    
def main():
    if len(sys.argv) > 1:
        # Accept a pair index argument from the command line
        try:
            pair_index = int(sys.argv[1])
            if 0 <= pair_index <= len(all_instance_pairs) - 1:
                print(f"Running pair {pair_index}...")
                instances = all_instance_pairs[pair_index]
                main_tasks = True
                if pair_index > 2:
                    main_tasks = False
            else:
                print(f"Please provide a pair index between 1 and {len(all_instance_pairs)}.")
        except ValueError:
            print("Invalid pair index. Please provide a number.")
    else:
        print(f"No pair index provided. Running the first pair by default.")
        instances = all_instance_pairs[0]
        main_tasks = True



        #print(f'Anzahl Iterationen: {iteration}')

        # Define the directory and file name
        output_directory = Path.cwd().parent / "Data" / "Final Results" / "Constructive" / "Test"

        #solver.SolutionPool.GetHighestProfitSolution().WriteSolToJson(output_directory, data, main_tasks)
    
    df = pd.DataFrame(results, columns=['Instance', 'Profit','WaitingTime','TotalTasks', 'RunTime'])

    print(df)

    df.to_csv(output_directory.joinpath(f'full_results{instances}.csv'), index=False)



def main_SAILS():
    results = []
    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        solver = Solver(data, 1008)

      
        SAILS_algorithm = SAILS(inputData=data,
                                maxRunTime = 7200,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                start_temperature = 1000,
                                min_temperature = 1e-5,
                                temp_decrease_factor=0.95,
                                maxInnerLoop = 10,
                                maxIterationsWithoutImprovement = 3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta =['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        )



        iteration = solver.RunAlgorithm(
            numberParameterCombination=3,
            main_tasks=main_tasks,
            algorithm = SAILS_algorithm
        )
        
        
        #Erstelle einen dataframe mit den ergebnissen für jede instanz
        
        results.append(
            {'Instance' :i, 
            'Profit':solver.SolutionPool.GetHighestProfitSolution().TotalProfit,
            'WaitingTime':solver.SolutionPool.GetHighestProfitSolution().WaitingTime,
            'TotalTasks':solver.SolutionPool.GetHighestProfitSolution().TotalTasks,
            'Iterations':iteration,
            'RunTime': round(solver.RunTime,4)
            })
    



        #print(f'Anzahl Iterationen: {iteration}')

        # Define the directory and file name
        output_directory = Path.cwd().parent / "Data" / "Final Results" / "SAILS" / "Flexi"

        solver.SolutionPool.GetHighestProfitSolution().WriteSolToJson(output_directory, data, True)
    
    df = pd.DataFrame(results, columns=['Instance', 'Profit','WaitingTime','TotalTasks' ,'Iterations', 'RunTime'])

    print(df)

    df.to_csv(output_directory.joinpath(f'full_results{instances}.csv'), index=False)


def main_ILS():
    results = []
    for i in instances:
        print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")


        solver = Solver(data, 1008)

      
        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute', 'SwapInterRoute','TwoEdgeExchange','ReplaceDelta','Insert','ReplaceProfit'])
        

        
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = 7200,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                threshold1 = 3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )



        iteration = solver.RunIteratedLocalSearch(
            numberParameterCombination=3,
            main_tasks=main_tasks,
            algorithm_LS=neighborhoodLocalSearch,
            algorithm_ILS=ILS
        )

        
        
        #Erstelle einen dataframe mit den ergebnissen für jede instanz
        
        results.append(
            {'Instance' :i, 
            'Profit':solver.SolutionPool.GetHighestProfitSolution().TotalProfit,
            'WaitingTime':solver.SolutionPool.GetHighestProfitSolution().WaitingTime,
            'TotalTasks':solver.SolutionPool.GetHighestProfitSolution().TotalTasks,
            'Iterations':iteration,
            'RunTime': round(solver.RunTime,4)
            })
    



        #print(f'Anzahl Iterationen: {iteration}')

        # Define the directory and file name
        output_directory = Path.cwd().parent / "Data" / "Final Results" / "ILS" / "Operative"

        solver.SolutionPool.GetHighestProfitSolution().WriteSolToJson(output_directory, data, True)
    
    df = pd.DataFrame(results, columns=['Instance', 'Profit','WaitingTime','TotalTasks' ,'Iterations', 'RunTime'])

    print(df)

    df.to_csv(output_directory.joinpath(f'full_results{instances}.csv'), index=False)


main_Constructive()


# Profile the main function
'''
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(80)  # Sort by cumulative time and show the top 10 results
'''


#Algorithm
'''
solver.RunAlgorithm(
    numberParameterCombination=1,
    main_tasks=True,
    algorithm = SAILS_algorithm
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
def allAlgorithms():

      
        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        

        neighborhoodLocalSearch2 = IterativeImprovement(inputData=data,
                                                    neighborhoodEvaluationStrategy= 'BestImprovement',
                                                    neighborhoodTypes=['ReplaceDelta'])
        
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = 7200,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                threshold1 = 3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )
        

        Adaptive_ILS = Adaptive_IteratedLocalSearch(inputData=data,
                                maxRunTime = 60,
                                sublists_to_modify=2,
                                threshold1 = 3,
                                score_threshold= 1000,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit'])
        
        SA_LS = SimulatedAnnealingLocalSearch(
            inputData=data,
            start_temperature = 1000,

            min_temperature = 1e-20,
            temp_decrease_factor=0.95,
            maxRunTime=14400,
            maxRandomMoves=10000,
            neighborhoodTypesDelta=['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'],
            neighborhoodTypesProfit= ['Insert','ReplaceProfit']
        )


        Adaptive_SAILS_algorithm = Adaptive_SAILS(inputData=data,
                                maxRunTime = 10,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                start_temperature = 1000,
                                min_temperature = 1e-5,
                                temp_decrease_factor=0.95,
                                maxInnerLoop = 10,
                                score_threshold = 1000,
                                maxIterationsWithoutImprovement = 3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta =['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        )


'''
        iterations = solver.RunAlgorithm(
            numberParameterCombination=3,
            main_tasks=main_tasks,
            algorithm = SA_LS
        )


        #print(f'Anzahl Iterationen: {iteration}')

        # Define the directory and file name
        if pair_index <= 2: 
            output_directory = Path.cwd().parent / "Data" / "SA_LS"
            csv_name = f"sa_ls_finals_results_{pair_index}.csv"
        else: 
            output_directory = Path.cwd().parent / "Data" / "SA_LS_Flexi"
            csv_name = f"sa_ls_finals_results_flexi_{pair_index}.csv"

        solver.SolutionPool.GetHighestProfitSolution()

        highest_profit_solution = solver.SolutionPool.GetHighestProfitSolution()
        highest_profit_solution.WriteSolToJson(output_directory, data, main_tasks=main_tasks)

        total_profit = highest_profit_solution.TotalProfit
        waiting_time = highest_profit_solution.WaitingTime
        total_tasks = highest_profit_solution.TotalTasks

        results.append({
            'Instance': i,
            'TotalProfit': total_profit,
            'WaitingTime': waiting_time,
            'TotalTasks': total_tasks,
            'RunTime' : round(solver.RunTime,4),
            'Iterations' : iterations,
            'MainTask': main_tasks
        })

    df = pd.DataFrame(results)
    df.to_csv(csv_name, index=False)

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
if __name__ == "__main__":
    main()

'''
# Profile the main function
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(80)  # Sort by cumulative time and show the top 10 results
'''


