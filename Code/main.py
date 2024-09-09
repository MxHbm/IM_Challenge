from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
import time


main_tasks = True
algorithm = 'ILS' #Iterative or ILS

if main_tasks:
    instances = ['7_2_1', '7_2_2']#, '7_5_1', '7_5_2', '7_8_1', '7_8_2']#, '7_10_1', '7_10_2']
else:
    instances = ['7_2_1', '7_5_1']#, '7_8_1', '7_10_1']

print('______________________________________________________________________')

runtimes = dict()

for i in instances:
    print(Path.cwd().parent) 
    print("Instance: ", i)
    data = InputData("Instance"+i+".json")

    pool = SolutionPool()
    evaluationLogic = EvaluationLogic(data)


    ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


    ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=3, main_tasks = main_tasks)

    solution = pool.GetHighestProfitSolution()

    main_tasks_string = str(main_tasks) 
    solution.WriteSolToJson(Path.cwd().parent / "Data" / ("Main_Tasks = " + main_tasks_string) /"Results_Greedy",data, main_tasks)

    print(solution)


    neighborhoodTypesDelta = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta']
    neighborhoodTypesProfit = ['Insert','ReplaceProfit']

    if algorithm == 'ILS':
        iteratedLocalSearch = IteratedLocalSearch(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta','Insert','ReplaceProfit'])
        iteratedLocalSearch.Initialize(evaluationLogic,pool, rng = None)
        start_time = time.time()
        solution = iteratedLocalSearch.Run(solution)
        end_time = time.time()

    elif algorithm == 'Iterative':
        iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['TwoEdgeExchange','Insert'])   
        iterativeImpro.Initialize(evaluationLogic,pool, rng = None)
        start_time = time.time()
        solution = iterativeImpro.Run(solution)
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

