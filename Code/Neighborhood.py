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

class ProfitNeighborhood:
    ''' Framework for generally needed neighborhood functionalities'''

    def __init__(self, inputData:InputData, initialRoutePlan, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        self.InputData = inputData
        self.RoutePlan = initialRoutePlan
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        # Create empty lists for discovering different moves
        self.Moves = []
        self.MoveSolutions = []
        self.Type = 'None'

    def DiscoverMoves(self) -> None:
        ''' Find all possible moves for particular neighborhood and permutation'''

        raise Exception('DiscoverMoves() is not implemented for the abstract ProfitNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy:str) -> None:
        ''' Define a strategy for the local search of the neighborhood and "activate" it'''

        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')

    def EvaluateMove(self, move:BaseMove) -> Solution:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        moveSolution = Solution(move, self.InputData)

        self.EvaluationLogic.DefineStartEnd(moveSolution)

        return moveSolution

    def EvaluateMovesBestImprovement(self) -> None:
        """ Evaluate all moves for best improvement and adds the calculated solutions to list MoveSolutions"""
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)

            self.MoveSolutions.append(moveSolution)

    def EvaluateMovesFirstImprovement(self) -> None:
        """ Evaluate all moves until the first one is found that improves the best solution found so far. """

        # Retrieve best solution from Solution Pool
        bestObjective = self.SolutionPool.GetHighestProfitSolution().TotalProfit

        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)

            self.MoveSolutions.append(moveSolution)

            if moveSolution.Makespan < bestObjective:
                # abort neighborhood evaluation because an improvement has been found
                return None

    def MakeBestMove(self) -> Solution:
        ''' Returns the best move found from the list Move Solutions'''

        self.MoveSolutions.sort(key = lambda solution: solution.TotalProfit) # sort solutions according to profit

        bestNeighborhoodSolution = self.MoveSolutions[0]

        return bestNeighborhoodSolution

    def Update(self, new_routeplan) -> None:
        ''' Updates the actual permutation and deletes all saved Moves and Move Solutions'''

        self.Moves.clear()
        self.MoveSolutions.clear()
        self.RoutePlan = new_routeplan

    def LocalSearch(self, neighborhoodEvaluationStrategy:str, solution:Solution) -> None:
        ''' Tries to find a better solution from the start solution by searching the neighborhod'''
        #bestCurrentSolution = self.SolutionPool.GetLowestMakespanSolution() ## TO.DO: Lösung übergeben?

        hasSolutionImproved = True

        while hasSolutionImproved:
            
            # Sets Algorithm back!
            self.Update(solution.RoutePlan) 
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodSolution = self.MakeBestMove()

            if bestNeighborhoodSolution.Makespan < solution.Makespan:
                print("New best solution has been found!")
                print(bestNeighborhoodSolution)
                # -> Possible to better solution! 

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.setRoutePlan(bestNeighborhoodSolution.RoutePlan, self.InputData)

            else:
                print(f"Reached local optimum of {self.Type} neighborhood. Stop local search.")
                hasSolutionImproved = False       

class DeltaNeighborhood:
    ''' Framework for generally needed neighborhood functionalities'''

    def __init__(self, inputData:InputData, initialRoutePlan, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        self.InputData = inputData
        self.RoutePlan = initialRoutePlan
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool

        # Create empty lists for discovering different moves
        self.Moves = []
        self.MoveSolutions = []
        self.Type = 'None'

    def DiscoverMoves(self) -> None:
        ''' Find all possible moves for particular neighborhood and permutation'''

        raise Exception('DiscoverMoves() is not implemented for the abstract DeltaNeighborhood class.')

    def EvaluateMoves(self, evaluationStrategy:str) -> None:
        ''' Define a strategy for the local search of the neighborhood and "activate" it'''

        if evaluationStrategy == 'BestImprovement':
            self.EvaluateMovesBestImprovement()
        elif evaluationStrategy == 'FirstImprovement':
            self.EvaluateMovesFirstImprovement()
        else:
            raise Exception(f'Evaluation strategy {evaluationStrategy} not implemented.')
        
    def EvaluateMove(self, move:BaseMove) -> Solution:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        raise Exception('DiscoverMoves() is not implemented for the abstract DeltaNeighborhood class.')

    def EvaluateMovesBestImprovement(self) -> None:
        """ Evaluate all moves for best improvement and adds the calculated solutions to list MoveSolutions"""
        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)

            self.MoveSolutions.append(moveSolution)

    def EvaluateMovesFirstImprovement(self) -> None:
        """ Evaluate all moves until the first one is found that improves the best solution found so far. """

        # No Profit changes will be happening here -> Eihter better or wors -> Has to be checked if this is neuighborhood specific
        neutral_value = 0

        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)

            self.MoveSolutions.append(moveSolution)

            if moveSolution.Delta < neutral_value:
                # abort neighborhood evaluation because an improvement has been found -> sort move solutions and start over
                return None

    def MakeBestMove(self) -> Solution:
        ''' Returns the best move found from the list Move Solutions'''

        self.MoveSolutions.sort(key = lambda move: move.Delta) # sort solutions according to profit

        bestNeighborhoodSolution = self.MoveSolutions[0]
        print("Best Delta: ",bestNeighborhoodSolution.Delta)

        return bestNeighborhoodSolution
        
    def LocalSearch(self, neighborhoodEvaluationStrategy:str, solution:Solution) -> None:
        ''' Tries to find a better solution from the start solution by searching the neighborhod'''
        #bestCurrentSolution = self.SolutionPool.GetLowestMakespanSolution() ## TO.DO: Lösung übergeben?

        hasSolutionImproved = True
        iterator = 0

        while hasSolutionImproved and iterator < 10:
             
            # Sets Algorithm back!
            self.Update(solution.RoutePlan) 
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodMove = self.MakeBestMove()

            if bestNeighborhoodMove.Delta < 0:
                print("New best solution has been found!")
                bestNeighborhoodSolution = Solution(bestNeighborhoodMove.Route, self.InputData)
                self.EvaluationLogic.evaluateSolution(bestNeighborhoodSolution)
                print(bestNeighborhoodSolution.WaitingTime)
                # -> Possible to better solution! 

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.setRoutePlan(bestNeighborhoodSolution.RoutePlan, self.InputData)

            else:
                print(f"Reached local optimum of {self.Type} neighborhood. Stop local search.")
                hasSolutionImproved = False   


            iterator += 1   

    def Update(self, new_routePlan) -> None:
        ''' Updates the actual permutation and deletes all saved Moves and Move Solutions'''

        self.Moves.clear()
        self.MoveSolutions.clear()
        self.RoutePlan = new_routePlan  

class SwapMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, initialRoutePlan, day:int, cohort:int, taskA:int, taskB:int):
        self.Route = initialRoutePlan # create a copy of the permutation
        self.TaskA = taskA
        self.TaskB = taskB
        self.Delta = np.inf
        self.Day = day
        self.Cohort = cohort

        # Get the indices
        self.indexA = self.Route[day][cohort].index(self.TaskA)
        self.indexB = self.Route[day][cohort].index(self.TaskB)

        #changes the index of two jobs! 
        self.Route[day][cohort][self.indexA] = self.TaskB
        self.Route[day][cohort][self.indexB] = self.TaskA

class SwapNeighborhood(DeltaNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, initialRoutePlan, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData, initialRoutePlan, evaluationLogic, solutionPool)

        self.Type = 'Swap'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        if task_i != task_j: # Hier könenn vielel foppelte Swqap movesd vermieden weden
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                swapMove = SwapMove(self.RoutePlan,day,cohort, task_i, task_j)
                                self.Moves.append(swapMove)

    def EvaluateMove(self, move:SwapMove) -> SwapMove:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        move.setDelta(self.EvaluationLogic.CalculateSwap1Delta(move))

        return move

class InsertionMove(BaseMove):
    """ Represents the insertion of the element at IndexA at the new position IndexB for a given permutation (= solution). """

    def __init__(self, initialPermutation:list[int],initialLotMatrix:list[list[int]], indexA:int, indexB:int):
        self.Permutation = [] # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB
        self.LotMatrix = initialLotMatrix

        for k in range(len(initialPermutation)):
            if k == indexA:
                continue

            self.Permutation.append(initialPermutation[k])

        self.Permutation.insert(indexB, initialPermutation[indexA])


class InsertionNeighborhood(ProfitNeighborhood):
    """ Contains all $(n - 1)^2$ insertion moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'Insertion'

    def DiscoverMoves(self):
        ''' Discover all possible moves for given nieghbood and permutation'''

        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if i == j or i == j + 1:
                    continue

                insertionMove = InsertionMove(self.Permutation,self.LotMatrix, i, j)
                self.Moves.append(insertionMove)
                

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


class TwoEdgeExchangeMove(BaseMove):
    ''' Represent the move of extracting a sequence of jobs between index A and B and reinserting the reversed sequence at the same position (for len = 2 -> SWAP Move)'''

    def __init__(self, initialPermutation:list[int],initialLotMatrix:list[list[int]], indexA:int, indexB:int):
        self.Permutation = []

        self.Permutation.extend(initialPermutation[:indexA])
        self.Permutation.extend(reversed(initialPermutation[indexA:indexB]))
        self.Permutation.extend(initialPermutation[indexB:])
        self.LotMatrix = initialLotMatrix   

class TwoEdgeExchangeNeighborhood(ProfitNeighborhood):
    ''' Neighborhood Class for Two Edge Exchange Move'''

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'TwoEdgeExchange'
    
    def DiscoverMoves(self) -> None:
        ''' Discover all possible moves for given nieghbood and permutation and saves moves in Moves list''' 

        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if j < i + 1:
                    continue
                twoEdgeMove = TwoEdgeExchangeMove(self.Permutation,self.LotMatrix, i, j)
                self.Moves.append(twoEdgeMove)
