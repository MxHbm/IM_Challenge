from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
import time


instances = ['7_2_1']#, '7_2_2', '7_5_1', '7_5_2']#, '7_8_1', '7_8_2', '7_10_1', '7_10_2']

print('______________________________________________________________________')

for i in instances:
    print(Path.cwd().parent) 
    data = InputData("Instance"+i+".json")

    pool = SolutionPool()
    evaluationLogic = EvaluationLogic(data)

    ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


    ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb="Test")
    solution = pool.GetHighestProfitSolution()


    solution.WriteSolToJson(Path.cwd().parent / "IM_Challenge" / "Data" / "Results_Greedy",data)

    print("Waiting Time after Constructive" , solution.WaitingTime)



    iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapDelta'])#,'Insert'])#,'SwapWaiting','TwoEdgeExchange','Insert'])
    iterativeImpro.Initialize(evaluationLogic,pool, rng = None)

    
    start_time = time.time()
    solution = iterativeImpro.Run(solution)
    end_time = time.time()
    
    runtime = end_time - start_time
    
    solution.WriteSolToJson(Path.cwd().parent / "IM_Challenge" / "Data" / "Results_Iterative",data)


    evaluationLogic.evaluateSolution(solution)
    print(f"Waiting Time after Iterative Impro = {solution.WaitingTime}")
    print(f"Profit after Iterative Impro = {solution.TotalProfit}")
    
    print(solution)
    print(f"Runtime: {round(runtime, 2)} seconds")
    print('______________________________________________________________________')

