from OutputData import *
from copy import deepcopy
from EvaluationLogic import EvaluationLogic
import random

# Dummy class to have one class where all Moves are inheriting --> Potential to implement more funtionalities here! 
class BaseMove: 
    ''' Base Move Class, that all specific Move classes can inherit from! '''

    def __init__(self):
        pass

    def setDelta(self,delta:int) -> None: 
        ''' Set the Delta of the Move'''
        self.Delta = delta

    def setExtraTime(self,extraTime:int) -> None: 
        ''' Set the ExtraTime of the Move'''
        self.ExtraTime = extraTime


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
    
    def SingleRouteFeasibilityCheck(self, route: list[int], inputData: InputData) -> bool:
        """
        Checks the feasibility of a single route considering service times, travel distances, and main task constraints.

        Parameters:
        -----------
        route : list[int]
            A list of task IDs representing the sequence of tasks in the route. Task IDs greater than 1000 are considered main tasks.
        
        inputData : InputData
            An object containing necessary input data such as distances, task details, and constraints.

        Returns:
        --------
        bool
            Returns True if the route is feasible, otherwise returns False.
        """
        
        feasible = True
        serviceDuration = 0
        previousTask = 0  # Start at depot


        mainTasks = [task for task in route if task > 1000]  # Identify all main tasks in the route

        if mainTasks:
            mainIndices = [i for i, task in enumerate(route) if task in mainTasks]  # Find the indices of all main tasks
            previousTask = 0  # Reset to depot at the start
            current_index = 0
            for mainIndex in mainIndices:
                tasksBeforeMain = route[:(mainIndex - current_index)]  # Get all tasks before the current main task
                mainTask = route[(mainIndex - current_index)]
                tasksAfterMain = route[(mainIndex - current_index)+1:]  # Get all tasks after the current main task

                # Process tasks before the main task
                for task in tasksBeforeMain:
                    serviceDuration += inputData.distances[previousTask][task] + inputData.optionalTasks[task].service_time
                    previousTask = task

                serviceDuration += inputData.distances[previousTask][mainTask]  # Add travel time to main task

                # Check if the main task can be started at the earliest start time
                if serviceDuration > inputData.allTasks[mainTask].start_time:
                    feasible = False
                    return feasible

                # Reset the service duration to the main task's start time and process the main task
                serviceDuration = inputData.allTasks[mainTask].start_time + inputData.allTasks[mainTask].service_time
                previousTask = mainTask

                # Process tasks after the main task
                route = tasksAfterMain
                current_index += (mainIndex + 1) 

            # Process remaining tasks after the last main task
            for task in route:
                serviceDuration += inputData.distances[previousTask][task] + inputData.optionalTasks[task].service_time
                previousTask = task

            serviceDuration += inputData.distances[previousTask][0]  # Add travel time to depot

            if serviceDuration > inputData.maxRouteDuration:
                feasible = False
                return feasible

        else:  # Route consists of optional tasks only
            for task in route:
                serviceDuration += inputData.distances[previousTask][task] + inputData.optionalTasks[task].service_time
                previousTask = task

            serviceDuration += inputData.distances[previousTask][0]  # Add travel time to depot
            
            if serviceDuration > inputData.maxRouteDuration:
                feasible = False
                return  feasible

        return feasible


class ProfitNeighborhood(BaseNeighborhood):

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)

    def EvaluateMove(self, move: BaseMove) -> Solution:
        raise Exception('EvaluateMove() is not implemented for the abstract ProfitNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        
        if self.Type == 'Insert':
            self.MoveSolutions.sort(key=lambda move: (-move.Profit, move.ExtraTime))  # sort solutions according to profit and extra time
        elif self.Type == 'ReplaceProfit':
            self.MoveSolutions.sort(key=lambda move: (-move.ProfitDelta, move.Delta))  
        else:
            raise Exception('MakeBestMove() is not implemented for this neighborhood type.')
        
        feasibleFound = False
        number_to_check = 0

        while feasibleFound == False:
            if number_to_check <= len(self.MoveSolutions)-1:
                day = self.MoveSolutions[number_to_check].Day
                cohort = self.MoveSolutions[number_to_check].Cohort
                if self.SingleRouteFeasibilityCheck(self.MoveSolutions[number_to_check].Route[day][cohort], self.InputData):
                    feasibleFound = True
                    bestNeighborhoodSolution = self.MoveSolutions[number_to_check]
                else:
                    number_to_check += 1
            else:
                return None
        
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
            

            # Sets Algorithm back!
            self.Update(temp_sol.RoutePlan) 
            self.DiscoverMoves(temp_sol)
            self.EvaluateMoves(neighborhoodEvaluationStrategy)

            bestNeighborhoodMove = self.MakeBestMove()


            if bestNeighborhoodMove is not None:
                #print(f"\nIteration {iterator} in neighborhood {self.Type}")
                #print("New best solution has been found!")
                bestNeighborhoodSolution = Solution(bestNeighborhoodMove.Route, self.InputData)
                self.EvaluationLogic.evaluateSolution(bestNeighborhoodSolution)
                #print("New Profit:" , bestNeighborhoodSolution.TotalProfit)
                #print("New Waiting Time:" , bestNeighborhoodSolution.WaitingTime)

                if self.Type == 'Insert':
                    #print("Extra Time:" , bestNeighborhoodMove.ExtraTime)
                    pass
                elif self.Type == 'ReplaceProfit':
                    #print("Profit Delta:", bestNeighborhoodMove.ProfitDelta)
                    #print("Time Delta:" , bestNeighborhoodMove.Delta)
                    pass

                self.SolutionPool.AddSolution(bestNeighborhoodSolution)
                temp_sol = bestNeighborhoodSolution
            else:
                #print(f"\nReached local optimum of {self.Type} neighborhood in Iteration {iterator}. Stop local search.\n")
                hasSolutionImproved = False
            iterator += 1
            

        return temp_sol  

class DeltaNeighborhood(BaseNeighborhood):
    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)

    def EvaluateMove(self, move: BaseMove) -> Solution:
        raise Exception('EvaluateMove() is not implemented for the abstract DeltaNeighborhood class.')

    def MakeBestMove(self) -> Solution:
        self.MoveSolutions.sort(key=lambda move: move.Delta)

        feasibleFound = False
        number_to_check = 0

        while feasibleFound == False:
            if number_to_check <= len(self.MoveSolutions)-1:
                if self.Type == 'SwapIntraRoute' or self.Type == 'TwoEdgeExchange' or self.Type == 'ReplaceDelta':
                    day = self.MoveSolutions[number_to_check].Day
                    cohort = self.MoveSolutions[number_to_check].Cohort
                    if self.SingleRouteFeasibilityCheck(self.MoveSolutions[number_to_check].Route[day][cohort], self.InputData):
                        feasibleFound = True
                        bestNeighborhoodSolution = self.MoveSolutions[number_to_check]
                    else:
                        number_to_check += 1
                elif self.Type == 'SwapInterRoute':
                    dayA = self.MoveSolutions[number_to_check].DayA
                    cohortA = self.MoveSolutions[number_to_check].CohortA
                    dayB = self.MoveSolutions[number_to_check].DayB
                    cohortB = self.MoveSolutions[number_to_check].CohortB
                    if self.SingleRouteFeasibilityCheck(self.MoveSolutions[number_to_check].Route[dayA][cohortA], self.InputData) and self.SingleRouteFeasibilityCheck(self.MoveSolutions[number_to_check].Route[dayB][cohortB], self.InputData):
                        feasibleFound = True
                        bestNeighborhoodSolution = self.MoveSolutions[number_to_check]
                    else:
                        number_to_check += 1
                else:
                    raise Exception('MakeBestMove() is not implemented for this neighborhood type.')
            else:
                return None

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
            
            self.Update(temp_sol.RoutePlan)
            if self.Type == 'ReplaceDelta':
                self.DiscoverMoves(temp_sol)
            else:
                self.DiscoverMoves()
            self.EvaluateMoves(neighborhoodEvaluationStrategy)
            bestNeighborhoodMove = self.MakeBestMove()

            if bestNeighborhoodMove is not None and bestNeighborhoodMove.Delta < 0:
                #print(f"\nIteration: {iterator} in neighborhood {self.Type}")
                #print("New best solution has been found!")
                #print("Time Delta:" , bestNeighborhoodMove.Delta)
                bestNeighborhoodSolution = Solution(bestNeighborhoodMove.Route, self.InputData)
                self.EvaluationLogic.evaluateSolution(bestNeighborhoodSolution)
                #print("New Waiting Time:" , bestNeighborhoodSolution.WaitingTime)
                self.SolutionPool.AddSolution(bestNeighborhoodSolution)
                temp_sol = bestNeighborhoodSolution
            else:
                #print(f"\nReached local optimum of {self.Type} neighborhood in iteration {iterator}. Stop local search.\n")
                hasSolutionImproved = False
            iterator += 1
        return temp_sol

#_______________________________________________________________________________________________________________________

class SwapIntraRouteMove(BaseMove):
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

class SwapIntraRouteNeighborhood(DeltaNeighborhood):
    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData,  evaluationLogic, solutionPool)

        self.Type = 'SwapIntraRoute'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """


        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        index_i = self.RoutePlan[day][cohort].index(task_i)
                        index_j = self.RoutePlan[day][cohort].index(task_j)
                        if index_i < index_j: # Hier könenn viele doppelte Swqap movesd vermieden weden
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                swapMove = SwapIntraRouteMove(self.RoutePlan,day,cohort, task_i, task_j)

               
                                
                                self.Moves.append(swapMove)


    def EvaluateMove(self, move:SwapIntraRouteMove) -> SwapIntraRouteMove:
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        move.setDelta(self.EvaluationLogic.CalculateSwapIntraRouteDelta(move))

        return move

class SwapInterRouteMove(BaseMove):
    """ Represents the swap of tasks between different routes possibly on the same or different days. """

    def __init__(self, initialRoutePlan, dayA:int, cohortA:int, taskA:int, dayB:int, cohortB:int, taskB:int):
        self.Route = deepcopy(initialRoutePlan)  # create a copy of the route plan
        self.TaskA = taskA
        self.TaskB = taskB
        self.DayA = dayA
        self.CohortA = cohortA
        self.DayB = dayB
        self.CohortB = cohortB
        self.Delta = None

        # Get the indices
        self.indexA = self.Route[dayA][cohortA].index(self.TaskA)
        self.indexB = self.Route[dayB][cohortB].index(self.TaskB)

        # Swap the tasks between routes
        self.Route[dayA][cohortA][self.indexA] = self.TaskB
        self.Route[dayB][cohortB][self.indexB] = self.TaskA

class SwapInterRouteNeighborhood(DeltaNeighborhood):
    """ Contains all moves for swapping tasks between different routes possibly on the same or different days. """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData, evaluationLogic, solutionPool)
        self.Type = 'SwapInterRoute'

    def DiscoverMoves(self):
        """ Generate all possible swaps between tasks in different routes. """


        # Choose 2 random days to include in the neighborhood, otherwise the neighborhood is too large
        days = random.sample(range(len(self.RoutePlan)), 2)

        # Choose 4 random cohorts to include in the neighborhood, otherwise the neighborhood is too large
        cohorts = random.sample(range(len(self.RoutePlan[days[0]])), 4)

                
        for dayA in days:
            for cohortA in cohorts:
                for taskA in self.RoutePlan[dayA][cohortA]:
                    if taskA > 1000:
                        continue
                    for dayB in days:
                        for cohortB in cohorts:
                            if dayA == dayB and cohortA == cohortB:
                                continue
                            for taskB in self.RoutePlan[dayB][cohortB]:
                                if taskB > 1000:
                                    continue
                                swapMove = SwapInterRouteMove(self.RoutePlan, dayA, cohortA, taskA, dayB, cohortB, taskB)
                                self.Moves.append(swapMove)

    def EvaluateMove(self, move:SwapInterRouteMove) -> SwapInterRouteMove:
        move.setDelta(self.EvaluationLogic.CalculateSwapInterRouteDelta(move))
        return move
    
class TwoEdgeExchangeMove(BaseMove):
    """ Represents the swap of the element at IndexA with the element at IndexB for a given permutation (= solution). """

    def __init__(self, initialRoutePlan, day:int, cohort:int, taskA:int, taskB:int):
        self.Route = deepcopy(initialRoutePlan) # create a copy of the permutation
        self.Day = day
        self.Cohort = cohort
        self.TaskA = taskA
        self.TaskB = taskB

        # Get the indices
        self.indexA = self.Route[day][cohort].index(self.TaskA)
        self.indexB = self.Route[day][cohort].index(self.TaskB)

        #Reverse the order
        self.Route[day][cohort] = []
        self.Route[day][cohort].extend(initialRoutePlan[day][cohort][:self.indexA])
        self.Route[day][cohort].extend(reversed(initialRoutePlan[day][cohort][self.indexA:self.indexB+1]))
        self.Route[day][cohort].extend(initialRoutePlan[day][cohort][self.indexB+1:])

class TwoEdgeExchangeNeighborhood(DeltaNeighborhood):         

    """ Contains all $n choose 2$ swap moves for a given permutation (= solution). """

    def __init__(self, inputData:InputData, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool):
        super().__init__(inputData,  evaluationLogic, solutionPool)

        self.Type = 'TwoEdgeExchange'

    def DiscoverMoves(self):
        """ Generate all $n choose 2$ moves. """


        for day in range(len(self.RoutePlan)):
            for cohort in range(len(self.RoutePlan[day])):
                for task_i in self.RoutePlan[day][cohort]:
                    for task_j in self.RoutePlan[day][cohort]:
                        index_i = self.RoutePlan[day][cohort].index(task_i)
                        index_j = self.RoutePlan[day][cohort].index(task_j)
                        if index_i < index_j: 
                            if task_i <= 1000 and task_j <= 1000:
                                #Create Swap Move Objects with different permutations
                                twoEdgeExchangeMove = TwoEdgeExchangeMove(self.RoutePlan,day,cohort, task_i, task_j)

                 
                                self.Moves.append(twoEdgeExchangeMove)


    def EvaluateMove(self, move):
        ''' Calculates the MakeSpan of thr certain move - adds to recent Solution'''

        move.setDelta(self.EvaluationLogic.CalculateTwoEdgeExchangeDelta(move))

        return move

class ReplaceDeltaNeighborhood(DeltaNeighborhood):
    """
    Represents a neighborhood of Swap moves in the context of profit optimization.

    Attributes:
        Type (str): The type of the neighborhood, which is 'ReplaceDelta'.
    """

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        """
        Initializes the ReplaceDeltaNeighborhood instance.

        Args:
            inputData (InputData): The input data required for the neighborhood.
            evaluationLogic (EvaluationLogic): The logic used to evaluate solutions.
            solutionPool (SolutionPool): The pool of solutions.

        Returns:
            None
        """
        super().__init__(inputData, evaluationLogic, solutionPool)

        self.Type = 'ReplaceDelta'

    def DiscoverMoves(self, actual_Solution: Solution):
        """
        Discovers all possible swap moves for unused tasks in the current solution.

        Args:
            actual_Solution (Solution): The current solution from which unused tasks are identified.

        Returns:
            None
        """
        unusedTasks = actual_Solution.UnusedTasks

        # Only consider a subset of all unused tasks to reduce the number of moves

        max_number_to_consider = 200
        if len(unusedTasks) > max_number_to_consider:
            unusedTasks = random.sample(unusedTasks, max_number_to_consider)

        allowedSwaps = 0

        for unusedTask in unusedTasks:
            for day in range(len(self.RoutePlan)):
                for cohort in range(len(self.RoutePlan[day])):
                    for taskInRoute in self.RoutePlan[day][cohort]:
                        if taskInRoute > 1000:
                            continue
                        # Only swap if profit stays the same to reduce number of moves --> Only Target is to lower the waiting time
                        if self.InputData.allTasks[taskInRoute].profit != self.InputData.allTasks[unusedTask].profit:
                            continue
                        else:
                            allowedSwaps += 1
                        swapMove = SwapExtMove(self.RoutePlan, day, cohort, taskInRoute, unusedTask, self.InputData)  
                        self.Moves.append(swapMove)


    def EvaluateMove(self, move):
        """
        Evaluates a given move by creating a temporary solution and using the evaluation logic.

        Args:
            move (InsertMove): The move to be evaluated.

        Returns:
            Solution: The evaluated solution based on the move.
        """
        move.setDelta(self.EvaluationLogic.CalculateReplaceDelta(move))

        return move

#_______________________________________________________________________________________________________________________

class InsertMove(BaseMove):
    """
    Represents a move that inserts a task into various positions within a route.

    Attributes:
        Route (dict): A deep copy of the initial route plan after attempting to insert the task.
    """

    def __init__(self, initialRoutePlan, task: int, day:int, cohort:int, index: int, inputData):
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
        self.Task = task
        self.Day = day
        self.Cohort = cohort
        self.Index = index
        self.Profit = inputData.allTasks[task].profit

        self.Route[day][cohort].insert(index, task)

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
        
        # Only consider a subset of all unused tasks to reduce the number of moves
        max_number_to_consider = 50
        if len(unusedTasks) > max_number_to_consider:
            unusedTasks = random.sample(unusedTasks, max_number_to_consider)
        
        
        for task in unusedTasks:
            for day in range(len(self.RoutePlan)):
                for cohort in range(len(self.RoutePlan[day])):
                    for index in range(len(self.RoutePlan[day][cohort]) + 1):
                        insertMove = InsertMove(self.RoutePlan, task, day, cohort, index, self.InputData)
                        self.Moves.append(insertMove)


    def EvaluateMove(self, move):
        """
        Evaluates a given move by creating a temporary solution and using the evaluation logic.

        Args:
            move (InsertMove): The move to be evaluated.

        Returns:
            Solution: The evaluated solution based on the move.
        """

        
        #tmpSolution = Solution(move.Route, self.InputData)
        #self.EvaluationLogic.evaluateSolution(tmpSolution)

        move.setExtraTime(self.EvaluationLogic.CalculateInsertExtraTime(move))

        return move

class SwapExtMove(BaseMove):
    def __init__(self, initialRoutePlan, day:int, cohort:int, taskInRoute:int, unusedTask:int, inputData):
        """
        Initializes the SwapExtMove instance.

        Args:
            initialRoutePlan (list): The initial route plan.
            day (int): The day on which the swap is made.
            cohort (int): The cohort that drives the route.
            taskInRoute (int): The task currently in the route.
            unusedTask (int): The unused task to be swapped in.
        """
        self.Route = deepcopy(initialRoutePlan)  # create a copy of the route plan
        self.TaskInRoute = taskInRoute
        self.UnusedTask = unusedTask
        self.Day = day
        self.Cohort = cohort
        self.Delta = None
        self.ProfitDelta = inputData.allTasks[unusedTask].profit - inputData.allTasks[taskInRoute].profit

        # Get the index of the task in the route
        self.indexInRoute = self.Route[day][cohort].index(self.TaskInRoute)

        # Perform the swap: replace the task in the route with the unused task
        self.Route[day][cohort][self.indexInRoute] = self.UnusedTask

class ReplaceProfitNeighborhood(ProfitNeighborhood):
    """
    Represents a neighborhood of Swap moves in the context of profit optimization.

    Attributes:
        Type (str): The type of the neighborhood, which is 'ReplaceProfit'.
    """

    def __init__(self, inputData: InputData, evaluationLogic: EvaluationLogic, solutionPool: SolutionPool):
        """
        Initializes the ReplaceProfitNeighborhood instance.

        Args:
            inputData (InputData): The input data required for the neighborhood.
            evaluationLogic (EvaluationLogic): The logic used to evaluate solutions.
            solutionPool (SolutionPool): The pool of solutions.

        Returns:
            None
        """
        super().__init__(inputData, evaluationLogic, solutionPool)

        self.Type = 'ReplaceProfit'

    def DiscoverMoves(self, actual_Solution: Solution):
        """
        Discovers all possible swap moves for unused tasks in the current solution.

        Args:
            actual_Solution (Solution): The current solution from which unused tasks are identified.

        Returns:
            None
        """
        unusedTasks = actual_Solution.UnusedTasks

        allowedSwaps = 0

        for unusedTask in unusedTasks:
            for day in range(len(self.RoutePlan)):
                for cohort in range(len(self.RoutePlan[day])):
                    for taskInRoute in self.RoutePlan[day][cohort]:
                        if taskInRoute > 1000:
                            continue
                        if self.InputData.allTasks[taskInRoute].profit >= self.InputData.allTasks[unusedTask].profit: # Only swap if profit of unused task is higher to reduce number of moves, needs to be adjusted for simulated annealing
                            continue
                        else:
                            allowedSwaps += 1
                        swapMove = SwapExtMove(self.RoutePlan, day, cohort, taskInRoute, unusedTask, self.InputData)  
                        self.Moves.append(swapMove)

    def EvaluateMove(self, move):
        """
        Evaluates a given move by creating a temporary solution and using the evaluation logic.

        Args:
            move (InsertMove): The move to be evaluated.

        Returns:
            Solution: The evaluated solution based on the move.
        """
        move.setDelta(self.EvaluationLogic.CalculateReplaceDelta(move))

        return move


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
