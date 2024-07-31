from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import * 


instances = ['7_2_2']#, '7_2_2', '7_5_1', '7_5_2']#, '7_8_1', '7_8_2', '7_10_1', '7_10_2']

print('______________________________________________________________________')

for i in instances:
    print(Path.cwd().parent) 
    data = InputData("Instance"+i+".json")

    pool = SolutionPool()
    evaluationLogic = EvaluationLogic(data)

    ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


    ConstructiveHeuristic.Run(data, 'Greedy', numberOfParameterComb=3)
    solution = pool.GetHighestProfitSolution()


    solution.WriteSolToJson(Path.cwd().parent / "IM_Challenge" / "Data" / "Results_Greedy",data)

    print("Waiting Time after Constructive" , solution.WaitingTime)

    iterativeImpro = IterativeImprovement(data, neighborhoodEvaluationStrategy= 'BestImprovement', neighborhoodTypes = ['SwapWaiting','TwoEdgeExchange','Insert'])#,'SwapWaiting','TwoEdgeExchange','Insert'])
    iterativeImpro.Initialize(evaluationLogic,pool, rng = None)
    solution = iterativeImpro.Run(solution)
    solution.WriteSolToJson(Path.cwd().parent / "IM_Challenge" / "Data" / "Results_Iterative",data)

    evaluationLogic.evaluateSolution(solution)
    print(f"Waiting Time after Iterative Impro = {solution.WaitingTime}")
    print(f"Profit after Iterative Impro = {solution.TotalProfit}")
    
    print(solution)
    print('______________________________________________________________________')

