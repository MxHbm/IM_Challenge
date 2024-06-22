from OutputData import *
from copy import deepcopy
from EvaluationLogic import EvaluationLogic
from random import random


# Dummy class to have one class where all Moves are inheriting --> Potential to implement more funtionalities here! 
class BaseMove: 
    ''' Base Move Class, that all specific Move classes can inherit from! '''

    def __init__(self): 
        pass

class BaseNeighborhood:
    ''' Framework for generally needed neighborhood functionalities'''

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]],evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        self.InputData = inputData
        self.Permutation = initialPermutation
        self.LotMatrix = initialLotMatrix
        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.no_lots = no_lots_boolean

        # Create empty lists for discovering different moves
        self.Moves = []
        self.MoveSolutions = []
        self.Type = 'None'

    def DiscoverMoves(self) -> None:
        ''' Find all possible moves for particular neighborhood and permutation'''

        raise Exception('DiscoverMoves() is not implemented for the abstract BaseNeighborhood class.')

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

        moveSolution = Solution(self.InputData.InputJobs,self.InputData.InputStages, move.Permutation,move.LotMatrix, self.no_lots)

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
        bestObjective = self.SolutionPool.GetLowestMakespanSolution().Makespan

        for move in self.Moves:
            moveSolution = self.EvaluateMove(move)

            self.MoveSolutions.append(moveSolution)

            if moveSolution.Makespan < bestObjective:
                # abort neighborhood evaluation because an improvement has been found
                return None

    def MakeBestMove(self) -> Solution:
        ''' Returns the best move found from the list Move Solutions'''

        self.MoveSolutions.sort(key = lambda solution: solution.Makespan) # sort solutions according to makespan

        bestNeighborhoodSolution = self.MoveSolutions[0]

        return bestNeighborhoodSolution

    def Update(self, permutation:list[int], lot_matrix:list[list[int]]) -> None:
        ''' Updates the actual permutation and deletes all saved Moves and Move Solutions'''

        self.Permutation = permutation
        self.LotMatrix = lot_matrix

        self.Moves.clear()
        self.MoveSolutions.clear()

    def LocalSearch(self, neighborhoodEvaluationStrategy:str, solution:Solution) -> None:
        ''' Tries to find a better solution from the start solution by searching the neighborhod'''
        #bestCurrentSolution = self.SolutionPool.GetLowestMakespanSolution() ## TO.DO: Lösung übergeben?

        hasSolutionImproved = True

        while hasSolutionImproved:
            
            # Sets Algorithm back! 
            self.Update(solution.Permutation, solution.lot_matrix)
            self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodSolution = self.MakeBestMove()

            if bestNeighborhoodSolution.Makespan < solution.Makespan:
                print("New best solution has been found!")
                print(bestNeighborhoodSolution)
                # -> Possible to better solution! 

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)

                solution.Permutation = bestNeighborhoodSolution.Permutation
                solution.lot_matrix = bestNeighborhoodSolution.lot_matrix
                solution.Makespan = bestNeighborhoodSolution.Makespan

            else:
                print(f"Reached local optimum of {self.Type} neighborhood. Stop local search.")
                hasSolutionImproved = False        

class SwapMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, initialPermutation:list[int],initialLotMatrix:list[list[int]], indexA:int, indexB:int):
        self.Permutation = list(initialPermutation) # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB
        self.LotMatrix = initialLotMatrix

        #changes the index of two jobs! 
        self.Permutation[indexA] = initialPermutation[indexB]
        self.Permutation[indexB] = initialPermutation[indexA]

class SwapNeighborhood(BaseNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'Swap'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        for i in range(len(self.Permutation)):
            for j in range(len(self.Permutation)):
                if i < j:
                    #Create Swap Move Objects with different permutations
                    swapMove = SwapMove(self.Permutation, self.LotMatrix, i, j)
                    self.Moves.append(swapMove)

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


class InsertionNeighborhood(BaseNeighborhood):
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


class BlockNeighborhoodK3(BaseNeighborhood):
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

class TwoEdgeExchangeNeighborhood(BaseNeighborhood):
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


class LotSwapMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, permutation:list[int],lot_matrix:list[int], job_id:int, indexA:int, indexB:int):

        self.LotMatrix = deepcopy(lot_matrix) # create a copy of the permutation
        self.IndexA = indexA
        self.IndexB = indexB
        self.job_ID = job_id
        self.Permutation = permutation

        #changes the index of two jobs! 
        self.LotMatrix[self.job_ID][self.IndexA],self.LotMatrix[self.job_ID][self.IndexB] = lot_matrix[self.job_ID][self.IndexB],lot_matrix[self.job_ID][self.IndexA]

class SwapLotNeighborhood(BaseNeighborhood):         
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, initialPermutation:list[int],initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialLotMatrix, initialPermutation, evaluationLogic, solutionPool, no_lots_boolean)

        self.Type = 'LotSwap'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """

        for job in range(len(self.LotMatrix)):
            if len(self.LotMatrix[job]) > 1: 
                for i in range(len(self.LotMatrix[job])):
                    for j in range(len(self.LotMatrix[job])):
                        if i < j:
                            #Create Swap Move Objects with different lot positions
                            swapLotMove = LotSwapMove(self.Permutation, self.LotMatrix,job, i, j)
                            self.Moves.append(swapLotMove)



class InsertionLotMove(BaseMove):
    """ Represents the insertion of the element at IndexA at the new position IndexB for a given permutation (= solution). """

    def __init__(self, permutation:list[int], initialLotMatrix:list[int], job_id:int, indexA:int, indexB:int):
        self.LotMatrix = []
        self.copy_lot_Matrix = deepcopy(initialLotMatrix)
        self.IndexA = indexA
        self.IndexB = indexB
        self.job_ID = job_id
        self.Permutation = permutation

        insert_row = self.copy_lot_Matrix [self.job_ID]
        insert_element = insert_row.pop(self.IndexA)
        insert_row.insert(self.IndexB, insert_element)

        for job in range(len(self.copy_lot_Matrix )):

            if job == self.job_ID: 

                self.LotMatrix.append(insert_row)
                continue
                
            self.LotMatrix.append(self.copy_lot_Matrix [job])

class InsertionLotNeighborhood(BaseNeighborhood):
    """ Contains all $(n - 1)^2$ insertion moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, initialPermutation:list[int], initialLotMatrix:list[list[int]],evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation,initialLotMatrix, evaluationLogic, solutionPool,no_lots_boolean)

        self.Type = 'LotInsertion'

    def DiscoverMoves(self):
        ''' Discover all possible moves for given nieghbood and permutation'''

        for job in range(len(self.LotMatrix)):
            if len(self.LotMatrix[job]) > 1: 
                for i in range(len(self.LotMatrix[job])):
                    for j in range(len(self.LotMatrix[job])):
                        if i == j:
                            continue

                        insertionMove = InsertionLotMove(self.Permutation, self.LotMatrix,job, i, j)
                        self.Moves.append(insertionMove)
                        

class SplitMutationMove(BaseMove):
    """ Shifts the proportion of two random lots for one job """

    def __init__(self, permutation: list[int], lot_matrix:list[int], job_id:int, indexA:int, indexB:int, given_proportion:float):
         # create a copy of the permutation
        self.LotMatrix = deepcopy(lot_matrix)
        self.job_ID = job_id
        self.proportion = given_proportion
        self.Permutation = permutation
        self.IndexA = indexA
        self.IndexB = indexB

        #changes the index of two jobs! 

        #Changes the proportions of the lots that the total proportion stays the same, but it changes!
        self.LotMatrix[self.job_ID][self.IndexA] -= self.proportion
        self.LotMatrix[self.job_ID][self.IndexB] += self.proportion
        

class SplitMutationNeighborhood(BaseNeighborhood):
    """ Contains all the posible adaptions for the Split Mutation Neigborhood """

    def __init__(self, inputData:InputData, initialPermutation:list[int], initialLotMatrix:list[list[int]], evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, rng, no_lots_boolean:bool = False):
        super().__init__(inputData, initialPermutation, initialLotMatrix, evaluationLogic, solutionPool,no_lots_boolean)

        self.Type = 'SplitMutation'
        self.RNG = rng

    def DiscoverMoves(self):
        ''' Discover all possible moves for given nieghbood and permutation'''

        for job in range(len(self.LotMatrix)):
            if len(self.LotMatrix[job]) > 1: 
                for i in range(len(self.LotMatrix[job])):
                    for j in range(len(self.LotMatrix[job])):
                        if i == j:
                            continue
                        for n in range(3):
                            proportion = (self.LotMatrix[job][i]/2) * self.RNG.random()
                            splitMutationMove = SplitMutationMove(self.Permutation, self.LotMatrix, job, i, j, proportion)
                            self.Moves.append(splitMutationMove)