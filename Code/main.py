from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
from Solver import * 
import time
import cProfile
import pstats
import pandas as pd
import sys



# Choose Szenrio Type --> True = Szenario Operative, False = Szenario Flexi
main_tasks = False

# Choose the instances to run
if main_tasks:
    instances = ['7_2_1']
else:
    instances = ['7_5_1']

# List of all instances for the Operative Szenario and Flexi Szenario
operative_instances = ['7_2_1', '7_2_2', '7_5_1', '7_5_2', '7_8_1', '7_8_2', '7_10_1', '7_10_2']
flexi_instances = ['7_2_1', '7_5_1', '7_8_1', '7_10_1']


# Define the runTime per instance (in seconds)
runTime = 60

# Define the number of parameter combinations for constructive heuristic
paraCombo = 3

# Define if you ONLY want to run the constructive heuristic
only_constructive = False


# Main function for the project
def main():

    # Run the algorithm for all chosen instances
    for i in instances:

        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        # Initialize the solver
        solver = Solver(data, 1008)

        # Define the neighborhood search
        neighborhoodLocalSearch = IterativeImprovement(inputData=data,
                                neighborhoodEvaluationStrategy= 'BestImprovement',
                                neighborhoodTypes=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta','Insert','ReplaceProfit'])


        # Define the parameter for Iterated Local Search
        ILS = IteratedLocalSearch(inputData=data,
                                maxRunTime = runTime,
                                sublists_to_modify=2,
                                consecutive_to_remove=3,
                                threshold1 = 3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit'])
      
        # Define the parameter for Adaptive Iterated Local Search
        Adaptive_ILS = Adaptive_IteratedLocalSearch(inputData=data,
                                maxRunTime = runTime,
                                sublists_to_modify=2,
                                threshold1 = 3,
                                score_threshold= 1000,
                                consecutive_to_remove=3,
                                neighborhoodEvaluationStrategyDelta = 'FirstImprovement',
                                neighborhoodEvaluationStrategyProfit = 'BestImprovement',
                                neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                neighborhoodTypesProfit= ['Insert','ReplaceProfit'])


        # Define the parameter for Simulated Annealing Local Search
        SAILS_algorithm = SAILS(inputData=data,
                                maxRunTime = runTime,
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
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit'])

        # Define the parameter for Adaptive Simulated Annealing Local Search
        Adaptive_SAILS_algorithm = Adaptive_SAILS(inputData=data,
                                maxRunTime = runTime,
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
                                neighborhoodTypesProfit = ['Insert','ReplaceProfit'])


        # Define the parameter for Iterated Simulated Annealing Local Search
        ISA_LS = SimulatedAnnealingLocalSearch(inputData=data,
                                    start_temperature = 1000,
                                    min_temperature = 1e-20,
                                    temp_decrease_factor=0.95,
                                    maxRunTime=14400,
                                    maxRandomMoves=10000,
                                    neighborhoodTypesDelta=['SwapIntraRoute','SwapInterRoute','TwoEdgeExchange','ReplaceDelta'],
                                    neighborhoodTypesProfit= ['Insert','ReplaceProfit'])


        # Choose the algorithm to run
        algo = ILS

        if only_constructive:
            # Run ONLY the constructive heuristic
            solver.ConstructionPhase(
                numberParameterCombination= paraCombo, 
                main_tasks= main_tasks,
                )
        else:
            # Run the algorithm
            profit_over_time = solver.RunAlgorithm(
                numberParameterCombination= paraCombo,
                main_tasks=main_tasks,
                algorithm = algo
            )
       
        # Define the directory and file name
        output_directory = Path.cwd().parent / "Data" / "Testing" / "Flexi" / "ILS"

        # Save the solution to a json file to visualize the solution on streamlit website
        solver.SolutionPool.GetHighestProfitSolution().WriteSolToJson(output_directory, data, main_tasks)
    
        if only_constructive == False:
            # Save the profit over time for further analysis
            df = pd.DataFrame.from_dict(profit_over_time, orient='index', columns=['RunTime', 'Profit'])
            df = df.reset_index().rename(columns={'index': 'Iteration'})
            df = df[['Iteration', 'RunTime', 'Profit']]
            df.to_csv(output_directory/f"{i}_profit_over_time.csv", index=False)


main()




# For only running constructive heuristic
'''


'''

# Profile the main function
'''
if __name__ == '__main__':
    cProfile.run('main()', 'profiling_results.prof')
    p = pstats.Stats('profiling_results.prof')
    p.sort_stats('cumtime').print_stats(80)  # Sort by cumulative time and show the top 10 results
'''