from OutputData import *
from copy import deepcopy
from EvaluationLogic import EvaluationLogic
from random import random

# Dummy class to have one class where all Moves are inheriting --> Potential to implement more funtionalities here! 
class BaseMove: 
    ''' Base Move Class, that all specific Move classes can inherit from! '''

    def __init__(self):
        pass

    def setDelta(self,delta:int) -> None: 
        ''' Set the Delta of the Move'''
        self.Delta = delta


    def SingleRouteFeasibilityCheck(self, route, inputData):

        feasible = True


        serviceDuration = 0
        previousTask = 0 # Start at depot

        if any(task > 1000 for task in route): # Check if a main task is included in the route
            
            mainIndex = next((i for i, task in enumerate(route) if task > 1000), len(route)) # Find the index of the first main task in the route
            tasksBeforeMain = route[:mainIndex] # Get all tasks before the main task
            tasksAfterMain = route[mainIndex+1:] # Get all tasks after the main task
            mainTask = route[mainIndex]


            for task in tasksBeforeMain:
                travelTime = inputData.distances[previousTask][task]
                serviceDuration += travelTime
                serviceDuration += inputData.optionalTasks[task].service_time
                previousTask = task

            serviceDuration += inputData.distances[previousTask][mainTask] # Add travel time to main task

            if serviceDuration > inputData.allTasks[mainTask].start_time:
                feasible = False
                

            previousTask = mainTask
            serviceDuration = inputData.allTasks[mainTask].start_time + inputData.allTasks[mainTask].service_time

            for task in tasksAfterMain:
                travelTime = inputData.distances[previousTask][task]
                serviceDuration += travelTime
                serviceDuration += inputData.optionalTasks[task].service_time
                previousTask = task

            serviceDuration += inputData.distances[previousTask][0] # Add travel time to depot

            if serviceDuration > inputData.maxRouteDuration:
                feasible = False



        else: # Route consists of optional tasks only, therefore only check if cohort reaches depot in time

            for task in route:
                travelTime = inputData.distances[previousTask][task]
                serviceDuration += travelTime
                serviceDuration += inputData.optionalTasks[task].service_time
                previousTask = task

            serviceDuration += inputData.distances[previousTask][0] # Add travel time to depot
            
            if serviceDuration > inputData.maxRouteDuration:
                feasible = False

            
        
        return feasible
        
        

        
    def CompleteRoutePlanFeasibilityCheck(self, routeplan, inputData): # Only accept moves that are feasible --> try to check as least as you can to minimize computing time
        
        feasible = True
        break_flag = False
        
        for day in routeplan.keys():
            if break_flag:
                break

            for route in routeplan[day]:
                if break_flag:
                    break

                feasible = self.SingleRouteFeasibilityCheck(route, inputData)

                if feasible == False:
                    break_flag = True
                    break



        return feasible




class BaseNeighborhood:
    ''' Framework for generally needed neighborhood functionalities'''

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        self.InputData = inputData
        self.RoutePlan = None
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        # Create empty lists for discovering different moves
        self.Moves = []
        self.MoveSolutions = []
        self.Type = 'None'

    def DiscoverMoves(self) -> None:
        ''' Find all possible moves for particular neighborhood and permutation'''
        raise Exception('DiscoverMoves() is not implemented for the abstract BaseNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy: str) -> None:
        ''' Define a strategy for the local search of the neighborhood and "activate" it'''

        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')

    def EvaluateMove(self, move: BaseMove) -> Solution:
        ''' Calculates the MakeSpan of the certain move - adds to recent Solution'''
        raise Exception('EvaluateMove() is not implemented for the abstract BaseNeighborhood class.')

    def EvaluateMovesBestImprovement(self) -> None:
        """ Evaluate all moves for best improvement and adds the calculated solutions to list MoveSolutions"""
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)
            self.MoveSolutions.append(moveSolution)

    def EvaluateMovesFirstImprovement(self) -> None:
        """ Evaluate all moves until the first one is found that improves the best solution found so far. """
        raise Exception('EvaluateMovesFirstImprovement() is not implemented for the abstract BaseNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        ''' Returns the best move found from the list Move Solutions'''
        raise Exception('MakeBestMove() is not implemented for the abstract BaseNeighborhood class.')

    def Update(self, new_routeplan) -> None:
        ''' Updates the actual permutation and deletes all saved Moves and Move Solutions'''
        self.Moves.clear()
        self.MoveSolutions.clear()
        self.RoutePlan = new_routeplan

    def LocalSearch(self, neighborhoodEvaluationStrategy: str, solution: Solution) -> None:
        ''' Tries to find a better solution from the start solution by searching the neighborhod'''
        raise Exception('LocalSearch() is not implemented for the abstract BaseNeighborhood class.')

 #_______________________________________________________________________________________________________________________   

class ProfitNeighborhood(BaseNeighborhood):

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)

    def EvaluateMove(self, move: BaseMove) -> Solution:
        raise Exception('EvaluateMove() is not implemented for the abstract ProfitNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        self.MoveSolutions.sort(key=lambda solution: (solution.TotalProfit, solution.WaitingTime), reverse=True)  # sort solutions according to profit and waiting time
        bestNeighborhoodSolution = self.MoveSolutions[0]
        print("Best Profit: ", bestNeighborhoodSolution.TotalProfit)
        return bestNeighborhoodSolution

    def EvaluateMovesFirstImprovement(self) -> None:
        bestObjective = self.SolutionPool.GetHighestProfitSolution().TotalProfit
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)
            self.MoveSolutions.append(moveSolution)
            if moveSolution.Makespan < bestObjective:
                return None

    def LocalSearch(self, neighborhoodEvaluationStrategy:str, solution:Solution) -> None:
        ''' Tries to find a better solution from the start solution by searching the neighborhod'''
        #bestCurrentSolution = self.SolutionPool.GetLowestMakespanSolution() ## TO.DO: Lösung übergeben?

        temp_sol = deepcopy(solution)
        hasSolutionImproved = True
        iterator = 1

        while hasSolutionImproved:
            print(f"Iteration: {iterator}")

            # Sets Algorithm back!
            self.Update(temp_sol.RoutePlan) 
            self.DiscoverMoves(temp_sol)
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodSolution = self.MakeBestMove()

            if bestNeighborhoodSolution.TotalProfit > temp_sol.TotalProfit:
                print("New best solution has been found!")
                print("New Profit:" , bestNeighborhoodSolution.TotalProfit, "\n")
                # -> Possible to better solution! 

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                temp_sol.setRoutePlan(bestNeighborhoodSolution.RoutePlan, self.InputData)
                temp_sol = bestNeighborhoodSolution

            else:
                print(f"Reached local optimum of {self.Type} neighborhood in Iteration {iterator}. Stop local search.")
                hasSolutionImproved = False
            iterator += 1

        return temp_sol  


class DeltaNeighborhood(BaseNeighborhood):
    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)

    def EvaluateMove(self, move: BaseMove) -> Solution:
        raise Exception('EvaluateMove() is not implemented for the abstract DeltaNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        self.MoveSolutions.sort(key=lambda move: move.Delta)  # sort solutions according to profit
        bestNeighborhoodSolution = self.MoveSolutions[0]
        print("Best Delta: ", bestNeighborhoodSolution.Delta)
        return bestNeighborhoodSolution

    def EvaluateMovesFirstImprovement(self) -> None:
        neutral_value = 0
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)
            self.MoveSolutions.append(moveSolution)
            if moveSolution.Delta < neutral_value:
                return None
            
    

    def LocalSearch(self, neighborhoodEvaluationStrategy: str, solution: Solution) -> Solution:
        hasSolutionImproved = True
        iterator = 1
        temp_sol = deepcopy(solution)


        while hasSolutionImproved:# and iterator < 50:
            print(f"Iteration: {iterator}")
            self.Update(temp_sol.RoutePlan)
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)
            bestNeighborhoodMove = self.MakeBestMove()

            if bestNeighborhoodMove.Delta < 0:
                print("New best solution has been found!")
                bestNeighborhoodSolution = Solution(bestNeighborhoodMove.Route, self.InputData)
                self.EvaluationLogic.evaluateSolution(bestNeighborhoodSolution)
                print("New Waiting Time:" , bestNeighborhoodSolution.WaitingTime, "\n")
                self.SolutionPool.AddSolution(bestNeighborhoodSolution)
                temp_sol = bestNeighborhoodSolution
            else:
                print(f"Reached local optimum of {self.Type} neighborhood in iteration {iterator}. Stop local search.")
                hasSolutionImproved = False
            iterator += 1
        return temp_sol


class WaitingNeighborhood(BaseNeighborhood):
    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)

    def EvaluateMove(self, move: BaseMove) -> Solution:
        raise Exception('EvaluateMove() is not implemented for the abstract DeltaNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        self.MoveSolutions.sort(key=lambda solution: solution.WaitingTime, reverse=True)  # sort solutions according to profit
        bestNeighborhoodSolution = self.MoveSolutions[0]
        return bestNeighborhoodSolution

    def EvaluateMovesFirstImprovement(self) -> None:
        currentSolution = self.SolutionPool.GetHighestProfitSolution()
        for moveSolution in self.MoveSolutions:
            if moveSolution.WaitingTime > currentSolution.WaitingTime:
                return None
            else:
                currentSolution = moveSolution
            

    def LocalSearch(self, neighborhoodEvaluationStrategy: str, solution: Solution) -> Solution:
        hasSolutionImproved = True
        iterator = 1
        temp_sol = deepcopy(solution)


        while hasSolutionImproved:# and iterator < 50:
            print(f"Iteration: {iterator}")
            self.Update(temp_sol.RoutePlan)
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)
            bestNeighborhoodSolution = self.MakeBestMove()

            if bestNeighborhoodSolution.WaitingTime > temp_sol.WaitingTime:
                print("New best solution has been found!")
                self.EvaluationLogic.evaluateSolution(bestNeighborhoodSolution)
                print("New Waiting Time:" , bestNeighborhoodSolution.WaitingTime, "\n")
                self.SolutionPool.AddSolution(bestNeighborhoodSolution)
                temp_sol = bestNeighborhoodSolution
            else:
                print(f"Reached local optimum of {self.Type} neighborhood in iteration {iterator}. Stop local search.")
                hasSolutionImproved = False
            iterator += 1
        return temp_sol

#_______________________________________________________________________________________________________________________


class SwapMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, initialRoutePlan, day:int, cohort:int, taskA:int, taskB:int):
        self.Route = deepcopy(initialRoutePlan) # create a copy of the permutation
        self.TaskA = taskA
        self.TaskB = taskB
        self.Delta = None
        self.Day = day
        self.Cohort = cohort

        # Get the indices
        self.indexA = self.Route[day][cohort].index(self.TaskA)
        self.indexB = self.Route[day][cohort].index(self.TaskB)

        #changes the index of two jobs! 
        self.Route[day][cohort][self.indexA] = self.TaskB
        self.Route[day][cohort][self.indexB] = self.TaskA

class SwapDeltaNeighborhood(DeltaNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData,  evaluationLogic, solutionPool)

        self.Type = 'SwapDelta'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        feasibilityCounter = 0
        infeasibilityCounter = 0

        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        index_i = self.RoutePlan[day][cohort].index(task_i)
                        index_j = self.RoutePlan[day][cohort].index(task_j)
                        if index_i < index_j: # Hier könenn viele doppelte Swqap movesd vermieden weden
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                swapMove = SwapMove(self.RoutePlan,day,cohort, task_i, task_j)

                                #feasible = swapMove.CompleteRoutePlanFeasibilityCheck(swapMove.Route, self.InputData) # Check if the whole route plan is feasible
                                feasible = swapMove.SingleRouteFeasibilityCheck(swapMove.Route[day][cohort], self.InputData)                    
                                
                                if feasible:
                                    self.Moves.append(swapMove)
                                    feasibilityCounter += 1
                                else:
                                    infeasibilityCounter += 1

        print(f"Feasible Solutions: {feasibilityCounter}, Infeasible Solutions: {infeasibilityCounter}")

    def EvaluateMove(self, move:SwapMove) -> SwapMove:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        move.setDelta(self.EvaluationLogic.CalculateSwap1Delta(move))

        return move
    

class SwapWaitingNeighborhood(WaitingNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData,  evaluationLogic, solutionPool)

        self.Type = 'SwapWaiting'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        feasibilityCounter = 0
        infeasibilityCounter = 0

        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        index_i = self.RoutePlan[day][cohort].index(task_i)
                        index_j = self.RoutePlan[day][cohort].index(task_j)
                        if index_i < index_j: # Hier könenn viele doppelte Swqap movesd vermieden weden
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                swapMove = SwapMove(self.RoutePlan,day,cohort, task_i, task_j)

                                #feasible = swapMove.CompleteRoutePlanFeasibilityCheck(swapMove.Route, self.InputData) # Check if the whole route plan is feasible
                                feasible = swapMove.SingleRouteFeasibilityCheck(swapMove.Route[day][cohort], self.InputData)                    
                                
                                if feasible:
                                    self.Moves.append(swapMove)
                                    feasibilityCounter += 1
                                else:
                                    infeasibilityCounter += 1

        print(f"Feasible Solutions: {feasibilityCounter}, Infeasible Solutions: {infeasibilityCounter}")

    def EvaluateMove(self, move:SwapMove) -> SwapMove:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        tmpSolution = Solution(move.Route, self.InputData)
        self.EvaluationLogic.calculateWaitingTime(tmpSolution)

        return tmpSolution



class TwoEdgeExchangeMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, initialRoutePlan, day:int, cohort:int, taskA:int, taskB:int):
        self.Route = deepcopy(initialRoutePlan) # create a copy of the permutation
        self.TaskA = taskA
        self.TaskB = taskB

        # Get the indices
        self.indexA = self.Route[day][cohort].index(self.TaskA)
        self.indexB = self.Route[day][cohort].index(self.TaskB)

        #Reverse the order
        self.Route[day][cohort] = []
        self.Route[day][cohort].extend(initialRoutePlan[day][cohort][:self.indexA])
        self.Route[day][cohort].extend(reversed(initialRoutePlan[day][cohort][self.indexA:self.indexB]))
        self.Route[day][cohort].extend(initialRoutePlan[day][cohort][self.indexB:])


class TwoEdgeExchangeNeighborhood(WaitingNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData,  evaluationLogic, solutionPool)

        self.Type = 'TwoEdgeExchange'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        feasibilityCounter = 0
        infeasibilityCounter = 0

        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        index_i = self.RoutePlan[day][cohort].index(task_i)
                        index_j = self.RoutePlan[day][cohort].index(task_j)
                        if index_i < index_j: # Hier könenn viele doppelte Swqap movesd vermieden weden
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                twoEdgeExchangeMove = TwoEdgeExchangeMove(self.RoutePlan,day,cohort, task_i, task_j)

                                #feasible = swapMove.CompleteRoutePlanFeasibilityCheck(swapMove.Route, self.InputData) # Check if the whole route plan is feasible
                                feasible = twoEdgeExchangeMove.SingleRouteFeasibilityCheck(twoEdgeExchangeMove.Route[day][cohort], self.InputData)                    
                                
                                if feasible:
                                    self.Moves.append(twoEdgeExchangeMove)
                                    feasibilityCounter += 1
                                else:
                                    infeasibilityCounter += 1

        print(f"Feasible Solutions: {feasibilityCounter}, Infeasible Solutions: {infeasibilityCounter}")

    def EvaluateMove(self, move):
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        tmpSolution = Solution(move.Route, self.InputData)
        self.EvaluationLogic.calculateWaitingTime(tmpSolution)

        return tmpSolution





#_______________________________________________________________________________________________________________________


class InsertMove(BaseMove):
    """
    Represents a move that inserts a task into various positions within a route.

    Attributes:
        Route (dict): A deep copy of the initial route plan after attempting to insert the task.
    """

    def __init__(self, initialRoutePlan, task: int, inputData):
        """
        Initializes the InsertMove instance by attempting to insert the given task into the route.

        Args:
            initialRoutePlan (dict): The initial route plan.
            task (int): The task to be inserted.
            inputData: Additional input data required for feasibility checks.

        Returns:
            None
        """
        self.Route = deepcopy(initialRoutePlan)

        currentRoutePlan = deepcopy(self.Route)

        oneFeasibleMove = False

        for routes in currentRoutePlan.values():
            for route in routes:
                for index in range(len(route) + 1):
                    new_route = route[:index] + [task] + route[index:]
                    if self.SingleRouteFeasibilityCheck(new_route, inputData):
                        route[:] = new_route
                        self.Route = currentRoutePlan
                        oneFeasibleMove = True
                        break

        return None


class InsertNeighborhood(ProfitNeighborhood):
    """
    Represents a neighborhood of insert moves in the context of profit optimization.

    Attributes:
        Type (str): The type of the neighborhood, which is 'Insert'.
    """

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        """
        Initializes the InsertNeighborhood instance.

        Args:
            inputData (InputData): The input data required for the neighborhood.
            evaluationLogic (EvaluationLogic): The logic used to evaluate solutions.
            solutionPool (SolutionPool): The pool of solutions.

        Returns:
            None
        """
        super().__init__(inputData, evaluationLogic, solutionPool)

        self.Type = 'Insert'

    def DiscoverMoves(self, actual_Solution: Solution):
        """
        Discovers all possible insert moves for unused tasks in the current solution.

        Args:
            actual_Solution (Solution): The current solution from which unused tasks are identified.

        Returns:
            None
        """
        unusedTasks = actual_Solution.UnusedTasks

        for task in unusedTasks:
            insertMove = InsertMove(self.RoutePlan, task, self.InputData)
            self.Moves.append(insertMove)

    def EvaluateMove(self, move):
        """
        Evaluates a given move by creating a temporary solution and using the evaluation logic.

        Args:
            move (InsertMove): The move to be evaluated.

        Returns:
            Solution: The evaluated solution based on the move.
        """
        tmpSolution = Solution(move.Route, self.InputData)
        self.EvaluationLogic.evaluateSolution(tmpSolution)

        return tmpSolution
    


#_______________________________________________________________________________________________________________________


#### ALL NEIGHBORHOODS BELOW NEED TO BE ADJUSTED! ####

class BlockMoveK3(BaseMove):
    """ Represents the extraction of the sequence of elements starting at IndexA and ending at IndexA + $k$, and the reinsertion at the new position IndexB for a given permutation (= solution) for $k = 3$. """

    def __init__(self, initialPermutation:list[int],initialLotMatrix:list[list[int]], indexA:int, indexB:int):
        self.Permutation = [] # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB
        self.Length = 3 # pass as parameter to constructor to obtain the general block move
        self.LotMatrix = initialLotMatrix

        for i in range(len(initialPermutation)):
            if i >= indexA and i < indexA + self.Length:  # if i in range(indexA, indexA + self.Length):
                continue

            self.Permutation.append(initialPermutation[i])

        for i in range(self.Length):
            self.Permutation.insert(indexB + i, initialPermutation[indexA + i])


class BlockNeighborhoodK3(ProfitNeighborhood):
    """ Contains all $(n - k + 1)(n - k) - \max(0, n - 2k + 1)$ block moves for a given permutation (= solution) for $k = 3$. """

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'BlockK3'
        self.Length = 3

    def DiscoverMoves(self) -> None:
        ''' Discover all possible moves for given nieghbood and permutation and saves moves in Moves list'''  
    
        for i in range(len(self.Permutation) - self.Length + 1):
            for j in range(len(self.Permutation) - self.Length + 1):
                # skip if: (the block would be reinserted at its initial position) or (the current block would be swapped with the preceding block to exclude symmetry) 
                if i == j or j == i - self.Length:
                    continue

                blockMove = BlockMoveK3(self.Permutation,self.LotMatrix, i, j)
                self.Moves.append(blockMove)


class OLDTwoEdgeExchangeMove(BaseMove):
    ''' Represent the move of extracting a sequence of jobs between index A and B and reinserting the reversed sequence at the same position (for len = 2 -> SWAP Move)'''

    def __init__(self, initialPermutation:list[int],initialLotMatrix:list[list[int]], indexA:int, indexB:int):
        self.Permutation = []

        self.Permutation.extend(initialPermutation[:indexA])
        self.Permutation.extend(reversed(initialPermutation[indexA:indexB]))
        self.Permutation.extend(initialPermutation[indexB:])
        self.LotMatrix = initialLotMatrix   

class OLDTwoEdgeExchangeNeighborhood(ProfitNeighborhood):
    ''' Neighborhood Class for Two Edge Exchange Move'''

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'OLDTwoEdgeExchange'
    
    def DiscoverMoves(self) -> None:
        ''' Discover all possible moves for given nieghbood and permutation and saves moves in Moves list''' 

        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if j < i + 1:
                    continue
                twoEdgeMove = TwoEdgeExchangeMove(self.Permutation,self.LotMatrix, i, j)
                self.Moves.append(twoEdgeMove)
