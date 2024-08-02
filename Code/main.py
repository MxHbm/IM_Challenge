from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
import time


instances = ['7_2_1']#,'7_2_2', '7_5_1', '7_5_2','7_8_1', '7_8_2', '7_10_1', '7_10_2']

print('______________________________________________________________________')


tryComibnations = True

if tryComibnations  == False:

    for i in instances:
        #print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        pool = SolutionPool()
        evaluationLogic = EvaluationLogic(data)

        ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


        ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=3)

        solution = pool.GetHighestProfitSolution()

        
        solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Greedy",data)

        print(solution)


        neighborhoodTypesDelta = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta']
        neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapIntraRoute','ReplaceDelta','Insert','SwapInterRoute','TwoEdgeExchange','ReplaceProfit', 'Insert'])

        iterativeImpro.Initialize(evaluationLogic,pool, rng = None)


        start_time = time.time()
        solution = iterativeImpro.Run(solution)
        end_time = time.time()
        
        runtime = end_time - start_time
        
        solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Iterative",data)

        print(f"Runtime: {round(runtime, 2)} seconds")
        print('THE END')
        print('_____________________________________________________________________________________________________________________________________')


else:

    for i in instances:
        #print(Path.cwd().parent) 
        print("Instance: ", i)
        data = InputData("Instance"+i+".json")

        pool = SolutionPool()
        evaluationLogic = EvaluationLogic(data)

        ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


        ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=3)

        solution = pool.GetHighestProfitSolution()

        
        solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Greedy",data)

        print(solution)


        neighborhoodTypesDelta = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta']
        neighborhoodTypesProfit = ['Insert','ReplaceProfit']
        iterativeImpro = [IterativeImprovement(data, neighborhoodEvaluationStrategy= 'FirstImprovement', neighborhoodTypes = ['SwapIntraRoute','ReplaceDelta']),
                        IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['Insert']),
                        IterativeImprovement(data, neighborhoodEvaluationStrategy= 'FirstImprovement', neighborhoodTypes = ['SwapInterRoute','TwoEdgeExchange']),
                        IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['ReplaceProfit', 'Insert'])]
                                              
                                              
                                              
                                              
        start_time = time.time()                                    
        for imp in iterativeImpro:
            imp.Initialize(evaluationLogic,pool, rng = None)
            solution = imp.Run(solution)
        
        end_time = time.time()
        runtime = end_time - start_time
        
        solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Iterative",data)

        print(f"Runtime: {round(runtime, 2)} seconds")
        print('THE END')
        print('_____________________________________________________________________________________________________________________________________')
