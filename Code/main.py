from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import *
import time


instances = ['7_2_1']#, '7_2_2', '7_5_1', '7_5_2']#, '7_8_1', '7_8_2', '7_10_1', '7_10_2']

print('______________________________________________________________________')

for i in instances:
    #print(Path.cwd().parent) 
    print("Instance: ", i)
    data = InputData("Instance"+i+".json")

    pool = SolutionPool()
    evaluationLogic = EvaluationLogic(data)

    ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)

    ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=1)
    solution = pool.GetHighestProfitSolution()

    
    print("Profit after Constructive" , solution.TotalProfit)
    print("Waiting Time after Constructive" , solution.WaitingTime)
    print("Length of unused Tasks after Constructive" , len(solution.UnusedTasks))

    solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Greedy",data)



    iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapInterRoute'])#,'SwapInterRoute'])#,'TwoEdgeExchange' ,'Insert'])
    iterativeImpro.Initialize(evaluationLogic,pool, rng = None)


    #print("Unused Tasks after Constructive" , solution.UnusedTasks)

    
    start_time = time.time()
    solution = iterativeImpro.Run(solution)
    end_time = time.time()
    
    runtime = end_time - start_time
    
    solution.WriteSolToJson(Path.cwd().parent / "Data" / "Results_Iterative",data)


    evaluationLogic.evaluateSolution(solution)
    print(f"Waiting Time after Iterative Impro = {solution.WaitingTime}")
    print(f"Profit after Iterative Impro = {solution.TotalProfit}")
    
    print(solution)
    print(f"Runtime: {round(runtime, 2)} seconds")
    print('______________________________________________________________________')

