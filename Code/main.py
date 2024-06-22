from ConstructiveHeuristic import * 



data = InputData("../../Data/instances/instance1.txt")

ConstructiveHeuristic = ConstructiveHeuristics(SolutionPool())

ConstructiveHeuristics.Run(data, "Greedy")
