from ConstructiveHeuristic import * 
from EvaluationLogic import *


data = InputData("Data/Instanzen/Instance7_2_1.json")

pool = SolutionPool()

ConstructiveHeuristic = ConstructiveHeuristics(pool)
Evaluations = EvaluationLogic(data)

ConstructiveHeuristic.Run(data, "Greedy")

sol = pool.GetLowestMakespanSolution()

print(sol.RoutePlan)

print(sol.StartTimes)

print(sol.EndTimes)

Evaluations.setProfit(sol)

print(sol.TotalProfit)