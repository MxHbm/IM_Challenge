from ConstructiveHeuristic import * 
from EvaluationLogic import *
from ImprovementAlgorithm import * 


#mainTaskPlanner = ['OnePerDay', 'MIP']
mainTaskPlanner = ['OnePerDay']#, 'MIP']zzz

print('______________________________________________________________________')
for mainTaskPlanner in mainTaskPlanner:
    data = InputData("Data/Instanzen/Instance7_2_1.json")

    pool = SolutionPool()
    evaluationLogic = EvaluationLogic(data)

    ConstructiveHeuristic = ConstructiveHeuristics(pool, evaluationLogic)


    ConstructiveHeuristic.Run(data, 'Greedy', mainTaskPlanner = mainTaskPlanner, attractivenessFunction='WithDistanceToMainTask')
    solution = pool.GetHighestProfitSolution()

    print("Waiting Time" , solution.WaitingTime)

    iterativeImpro = IterativeImprovement(data)
    iterativeImpro.Initialize(evaluationLogic,pool, rng = None)
    solution = iterativeImpro.Run(solution)
    solution.WriteSolToJson("Data/IterativeImprovement.json")
    
    print(solution)
    print('______________________________________________________________________')

