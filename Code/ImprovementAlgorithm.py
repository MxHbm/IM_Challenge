from Neighborhood import *
import math
from copy import deepcopy
import numpy
import time

class ImprovementAlgorithm:
    """ Base class for several types of improvement algorithms. """ 

    def __init__(self, inputData:InputData, neighborhoodEvaluationStrategy:str = 'BestImprovement', neighborhoodTypes:list[str] = ['Swap']):
        self.InputData = inputData

        self.EvaluationLogic = {}
        self.SolutionPool = {}
        self.RNG = {}

        self.NeighborhoodEvaluationStrategy = neighborhoodEvaluationStrategy
        self.NeighborhoodTypes = neighborhoodTypes
        self.Neighborhoods = {}

    def Initialize(self, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, rng = None) -> None:
        ''' Initializes empty variables'''

        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng

    def CreateNeighborhood(self, neighborhoodType:str): #-> BaseNeighborhood:
        """ Creates a new neighborhood based on the current best Solution and the chosen neighborhood type.
            Similar to the so-called factory concept in software design. """
        
        ### NEEDS TO BE ADJUSTED FOR ORIENTEERING PROBLEMLocalSearch

        if neighborhoodType == 'SwapIntraRoute':
            return SwapIntraRouteNeighborhood(self.InputData, self.EvaluationLogic, self.SolutionPool, self.RNG)
        elif neighborhoodType == 'SwapInterRoute':
            return SwapInterRouteNeighborhood(self.InputData, self.EvaluationLogic, self.SolutionPool, self.RNG)
        elif neighborhoodType == 'TwoEdgeExchange':
            return TwoEdgeExchangeNeighborhood(self.InputData , self.EvaluationLogic, self.SolutionPool, self.RNG)
        elif neighborhoodType == 'Insert':
            return InsertNeighborhood(self.InputData, self.EvaluationLogic, self.SolutionPool, self.RNG)
        elif neighborhoodType == 'ReplaceProfit':
            return ReplaceProfitNeighborhood(self.InputData, self.EvaluationLogic, self.SolutionPool, self.RNG)
        elif neighborhoodType == 'ReplaceDelta':
            return ReplaceDeltaNeighborhood(self.InputData, self.EvaluationLogic, self.SolutionPool, self.RNG)
        else:
            raise Exception(f"Neighborhood type {neighborhoodType} not defined.")


    def InitializeNeighborhoods(self, neighborhoodtypes=None, neighborhoods_dict=None) -> None:
        ''' Create several neighborhoods for every neighborhood in the list neighborhoodTypes'''
        
        # If no neighborhood types are passed, default to self.NeighborhoodTypes
        if neighborhoodtypes is None:
            neighborhoodtypes = self.NeighborhoodTypes

        # If no neighborhoods dict is passed, default to self.Neighborhoods
        if neighborhoods_dict is None:
            neighborhoods_dict = self.Neighborhoods

        # Iterate over the neighborhood types and create neighborhoods
        for neighborhoodType in neighborhoodtypes:
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            neighborhoods_dict[neighborhoodType] = neighborhood




class IterativeImprovement(ImprovementAlgorithm):
    """ Iterative improvement algorithm through sequential variable neighborhood descent. 
        Local Search with itereative steps through many different neighborhoods.
    """

    def __init__(self,  inputData:InputData, neighborhoodEvaluationStrategy:str = 'BestImprovement', neighborhoodTypes:list[str] = ['SwapWaiting']):
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)

    def Run(self, solution:Solution) -> Solution:
        ''' Run local search with given solutions and iterate through all given neighborhood types'''

        self.InitializeNeighborhoods()    

        # According to "Hansen et al. (2017): Variable neighorhood search", this is equivalent to the 
        # sequential variable neighborhood descent with a pipe neighborhood change step.

        usedTypes = []

        for neighborhoodType in self.NeighborhoodTypes:
            usedTypes.append(neighborhoodType)
            print(f'\nRunning neighborhood {neighborhoodType}')
            neighborhood = self.Neighborhoods[neighborhoodType]

            solution = neighborhood.LocalSearch(self.NeighborhoodEvaluationStrategy, solution)
            print(f'Best solution after {usedTypes}: {solution}')
        
        return solution



class IteratedLocalSearch(ImprovementAlgorithm):
    """ Iterative local search with perturbation to escape local optima.
        Local Search with iterative steps through many different neighborhoods.
    """

    def __init__(self, inputData: InputData, maxRunTime:int, jobs_to_remove:int, sublists_to_modify:int,consecutive_to_remove:int, threshold1:int = 2,
                    neighborhoodEvaluationStrategyDelta: str = 'BestImprovement', neighborhoodEvaluationStrategyProfit: str = 'BestImprovement', neighborhoodTypesDelta: list[str] = ['SwapWaiting'], neighborhoodTypesProfit: list[str] = ['SwapWaiting']):
        super().__init__(inputData)

        self.maxRunTime = maxRunTime
        self.jobsToRemove = jobs_to_remove 
        self.sublists_to_modify = sublists_to_modify
        self.consecutive_to_remove = consecutive_to_remove
        self.NeighborhoodEvaluationStrategyDelta = neighborhoodEvaluationStrategyDelta
        self.NeighborhoodEvaluationStrategyProfit = neighborhoodEvaluationStrategyProfit
        self.NeighborhoodTypesDelta = neighborhoodTypesDelta
        self.NeighborhoodTypesProfit = neighborhoodTypesProfit
        self.NeighborhoodTypes = neighborhoodTypesDelta + neighborhoodTypesProfit
        self.Threshold1 = threshold1

    def Run(self, currentSolution: Solution) -> Solution:
        ''' Run local search with given solutions and iterate through all given neighborhood types '''

        self.InitializeNeighborhoods()
        
        print('\nStarting Iterated Local Search')

        iteration = 1
        iterationsWithoutImprovement = 0
        bestIteration = 'initial local search'
        bestSolution = self.SolutionPool.GetHighestProfitSolution()
        
        startTime = time.time()
        usedTime = 0

        while self.maxRunTime > usedTime:
            print(f'\nStarting iteration {iteration}')
            print(f' Running perturbation')
            currentSolution = self.Perturbation(currentSolution)
            print(f' Solution after perturbation in iteration {iteration}: \n {currentSolution}')
            
            print(f'\n Running local search after perturbation')
            
            for neighborhoodType in self.NeighborhoodTypesProfit:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)
            
            for neighborhoodType in self.NeighborhoodTypesDelta:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyDelta, currentSolution)

            for neighborhoodType in self.NeighborhoodTypesProfit:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)

            print(f' Solution after local search in iteration {iteration}:\n {currentSolution}')

            
            if currentSolution.TotalProfit > bestSolution.TotalProfit:
                iterationsWithoutImprovement = 0
                bestIteration = iteration
            else:
                iterationsWithoutImprovement += 1

            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            print(f'\n Overall best solution found in iteration {bestIteration}: \n {bestSolution}')

            print(f' Iterations without improvement: {iterationsWithoutImprovement}')
            
            if iterationsWithoutImprovement == self.Threshold1:
                print(f"The threshold of {self.Threshold1} iterations without improvement has been reached.")
                currentSolution = bestSolution
                iterationsWithoutImprovement = 0
            
            iteration += 1

            usedTime = time.time() - startTime

        print(f'\n Iterated Local Search finished after {iteration} iterations and {usedTime} seconds')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution
    
    def Perturbation(self, solution: Solution, type = 'shake') -> Solution:
        ''' Perturbation to escape local optima '''


        # choose type of perturbation randomly
        types = ['remove', 'shake']
        type = self.RNG.choice(types, replace = False)

        print(f'\n Perturbation type: {type}')
        
        if type == 'remove': # Random removal of jobs
            valid_elements = [(key, sublist_idx, item_idx, item) 
                            for key, sublists in solution.RoutePlan.items()
                            for sublist_idx, sublist in enumerate(sublists) 
                            for item_idx, item in enumerate(sublist) 
                            if item <= 1000]

            newRoutePlan = deepcopy(solution.RoutePlan)
            if len(valid_elements) >= self.jobsToRemove :
                to_remove = self.RNG.choice(valid_elements, self.jobsToRemove, replace = False)
                for key, sublist_idx, item_idx, item in to_remove:
                    newRoutePlan[key][sublist_idx].remove(item)
            else:
                print('RoutePlan is faulty')

            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)


        elif type == 'shake': # random removal of consectitive jobs
            
            newRoutePlan = deepcopy(solution.RoutePlan)

            all_sublists = [(key, sublist) for key, sublists in newRoutePlan.items() for sublist in sublists]
            indices = self.RNG.choice(len(all_sublists), min(self.sublists_to_modify, len(all_sublists)), replace=False)
            selected_sublists = [all_sublists[i] for i in indices]  # Select sublists using the chosen indices

            for key, sublist in selected_sublists:
                valid_positions = [i for i in range(len(sublist) - self.consecutive_to_remove + 1)
                                    if all(sublist[i + j] <= 1000 for j in range(self.consecutive_to_remove))]

                if valid_positions:
                    start_pos = self.RNG.choice(a = valid_positions, replace = False)
                    del sublist[start_pos:start_pos + self.consecutive_to_remove]


            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)
        

        return currentSolution
    


class Adaptive_IteratedLocalSearch(ImprovementAlgorithm):
    """ Iterative local search with perturbation to escape local optima.
        Local Search with iterative steps through many different neighborhoods.
    """

    def __init__(self, inputData: InputData, maxRunTime:int, jobs_to_remove:int, sublists_to_modify:int,consecutive_to_remove:int, threshold1:int = 2, score_threshold:int = 1000,
                    neighborhoodEvaluationStrategyDelta: str = 'BestImprovement', neighborhoodEvaluationStrategyProfit: str = 'BestImprovement', neighborhoodTypesDelta: list[str] = ['SwapWaiting'], neighborhoodTypesProfit: list[str] = ['SwapWaiting']):
        super().__init__(inputData)

        self.maxRunTime = maxRunTime
        self.jobsToRemove = jobs_to_remove 
        self.sublists_to_modify = sublists_to_modify
        self.consecutive_to_remove = consecutive_to_remove
        self.NeighborhoodEvaluationStrategyDelta = neighborhoodEvaluationStrategyDelta
        self.NeighborhoodEvaluationStrategyProfit = neighborhoodEvaluationStrategyProfit
        self.NeighborhoodTypesDelta = neighborhoodTypesDelta
        self.NeighborhoodTypesProfit = neighborhoodTypesProfit
        self.NeighborhoodTypes = neighborhoodTypesDelta + neighborhoodTypesProfit
        self.Threshold1 = threshold1
        self.ScoreThreshold = score_threshold

    def Run(self, currentSolution: Solution) -> Solution:
        ''' Run local search with given solutions and iterate through all given neighborhood types '''

        self.InitializeNeighborhoods()
        
        print('\nStarting Adaptive Iterated Local Search')

        iteration = 1
        iterationsWithoutImprovement = 0
        bestIteration = 'initial local search'
        bestSolution = self.SolutionPool.GetHighestProfitSolution()
        
        startTime = time.time()
        usedTime = 0

        scores = [100/len(self.NeighborhoodTypesDelta)]* len(self.NeighborhoodTypesDelta)

        while self.maxRunTime > usedTime:
            
            print(f'Scores: {scores}')
            total_score = sum(scores)
            probabilities = [score / total_score for score in scores]
            neighborhoodTypeDelta = np.random.choice(self.NeighborhoodTypesDelta, p=probabilities, replace=False)

            take_first = np.random.choice([True, False], p=[0.5, 0.5])
            if take_first:
                neighborhoodTypesProfit = self.NeighborhoodTypesProfit[:1]
            else:
                neighborhoodTypesProfit = self.NeighborhoodTypesProfit


            print(f'\nStarting iteration {iteration}')
            print(f' Running perturbation')
            currentSolution = self.Perturbation(currentSolution)
            print(f' Solution after perturbation in iteration {iteration}: \n {currentSolution}')
            
            print(f'\n Running local search after perturbation')

            
            
            for neighborhoodType in neighborhoodTypesProfit:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)
            
            
            waitingTimeBeforeDelta = currentSolution.WaitingTime

            # Delta Neighborhoods with probability weight, if waiting time diff more than 1000 then raise score
            print(f' Running neighborhood {neighborhoodTypeDelta}')
            neighboorhood = self.Neighborhoods[neighborhoodTypeDelta]
            currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyDelta, currentSolution)

            waitingTimeDifference = currentSolution.WaitingTime - waitingTimeBeforeDelta

            if waitingTimeDifference > self.ScoreThreshold:
                scores[self.NeighborhoodTypesDelta.index(neighborhoodTypeDelta)] += 1

            for neighborhoodType in neighborhoodTypesProfit:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)

            print(f' Solution after local search in iteration {iteration}:\n {currentSolution}')

            
            if currentSolution.TotalProfit > bestSolution.TotalProfit:
                iterationsWithoutImprovement = 0
                bestIteration = iteration
            else:
                iterationsWithoutImprovement += 1

            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            print(f'\n Overall best solution found in iteration {bestIteration}: \n {bestSolution}')

            print(f' Iterations without improvement: {iterationsWithoutImprovement}')
            
            if iterationsWithoutImprovement == self.Threshold1:
                print(f"The threshold of {self.Threshold1} iterations without improvement has been reached.")
                currentSolution = bestSolution
                iterationsWithoutImprovement = 0
            
            iteration += 1

            usedTime = time.time() - startTime

        print(f'\n Iterated Local Search finished after {iteration} iterations and {usedTime} seconds')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution
    
    def Perturbation(self, solution: Solution, type = 'shake') -> Solution:
        ''' Perturbation to escape local optima '''


        # choose type of perturbation randomly
        types = ['remove', 'shake']
        type = self.RNG.choice(types, replace = False)

        print(f'\n Perturbation type: {type}')
        
        if type == 'remove': # Random removal of jobs
            valid_elements = [(key, sublist_idx, item_idx, item) 
                            for key, sublists in solution.RoutePlan.items()
                            for sublist_idx, sublist in enumerate(sublists) 
                            for item_idx, item in enumerate(sublist) 
                            if item <= 1000]

            newRoutePlan = deepcopy(solution.RoutePlan)
            if len(valid_elements) >= self.jobsToRemove :
                to_remove = self.RNG.choice(valid_elements, self.jobsToRemove, replace = False)
                for key, sublist_idx, item_idx, item in to_remove:
                    newRoutePlan[key][sublist_idx].remove(item)
            else:
                print('RoutePlan is faulty')

            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)


        elif type == 'shake': # random removal of consectitive jobs
            
            newRoutePlan = deepcopy(solution.RoutePlan)

            all_sublists = [(key, sublist) for key, sublists in newRoutePlan.items() for sublist in sublists]
            indices = self.RNG.choice(len(all_sublists), min(self.sublists_to_modify, len(all_sublists)), replace=False)
            selected_sublists = [all_sublists[i] for i in indices]  # Select sublists using the chosen indices

            for key, sublist in selected_sublists:
                valid_positions = [i for i in range(len(sublist) - self.consecutive_to_remove + 1)
                                    if all(sublist[i + j] <= 1000 for j in range(self.consecutive_to_remove))]

                if valid_positions:
                    start_pos = self.RNG.choice(a = valid_positions, replace = False)
                    del sublist[start_pos:start_pos + self.consecutive_to_remove]


            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)
        

        return currentSolution



class SAILS(IteratedLocalSearch):
    """ A combination of Simulated Annealing and Iterative local search.."""

    def __init__(self, inputData: InputData, 
                 maxRunTime: int,  # Add the missing parameter
                 jobs_to_remove: int,  # Add the missing parameter
                 sublists_to_modify: int,  # Add the missing parameter
                 consecutive_to_remove: int,  # Add the missing parameter
                 start_temperature: int,
                 min_temperature: float,
                 temp_decrease_factor: float,
                 maxInnerLoop: int,
                 maxIterationsWithoutImprovement: int,
                 neighborhoodEvaluationStrategyDelta: str = 'BestImprovement',
                 neighborhoodEvaluationStrategyProfit: str = 'BestImprovement',
                 neighborhoodTypesDelta: list[str] = ['SwapWaiting'],
                 neighborhoodTypesProfit: list[str] = ['SwapWaiting']):
        super().__init__(inputData, maxRunTime, jobs_to_remove, sublists_to_modify,consecutive_to_remove)

        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature
        self.maxInnerLoop = maxInnerLoop
        self.maxIterationsWithoutImprovement = maxIterationsWithoutImprovement
        self.NeighborhoodEvaluationStrategyDelta = neighborhoodEvaluationStrategyDelta
        self.NeighborhoodEvaluationStrategyProfit = neighborhoodEvaluationStrategyProfit
        self.NeighborhoodTypesDelta = neighborhoodTypesDelta
        self.NeighborhoodTypesProfit = neighborhoodTypesProfit
        self.NeighborhoodTypes = neighborhoodTypesDelta + neighborhoodTypesProfit


    def Run(self, solution: Solution) -> Solution:

        self.InitializeNeighborhoods()
        
        print('\nStarting SAILS (Simualted Annealing Iterated Local Search)')
        print(f'\n Running initial local search')

        for neighborhoodType in self.NeighborhoodTypesDelta + self.NeighborhoodTypesProfit:    
            print(f' Running neighborhood {neighborhoodType}')
            neighboorhood = self.Neighborhoods[neighborhoodType]
            solution = neighboorhood.LocalSearch('BestImprovement', solution)

        currentSolution = solution
        lineSolution = solution
        print(f' Solution after initial local search:\n {currentSolution}')

        iteration = 1
        iterationsWithoutImprovement = 0
        bestIteration = 'initial local search'
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        temperature = self.startTemperature
        
        startTime = time.time()
        usedTime = 0


        while self.maxRunTime  > usedTime:
            print(f'\nStarting iteration {iteration}')

            innerLoop = 1
            while innerLoop < self.maxInnerLoop:

                print(f'\n Iteration.InnerLoop {iteration}.{innerLoop}')
                print(f' Running perturbation')
                currentSolution = self.Perturbation(currentSolution)
                print(f' Solution after perturbation in iteration {iteration}.{innerLoop}: \n {currentSolution}')
                
                print(f'\n Running local search after perturbation')

                for neighborhoodType in self.NeighborhoodTypesProfit:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)


                for neighborhoodType in self.NeighborhoodTypesDelta:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyDelta, currentSolution)


                for neighborhoodType in self.NeighborhoodTypesProfit:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)

                print(f' Solution after local search in iteration {iteration}.{innerLoop}:\n {currentSolution}')

                if currentSolution.TotalProfit > lineSolution.TotalProfit:
                    lineSolution = currentSolution
                    if currentSolution.TotalProfit > bestSolution.TotalProfit:
                        bestSolution = currentSolution
                        iterationsWithoutImprovement = 0
                        bestIteration = iteration
                    else:
                        iterationsWithoutImprovement += 1
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature)):
                        lineSolution = currentSolution   
                    else:
                        currentSolution = lineSolution

                    iterationsWithoutImprovement += 1
                
                innerLoop += 1

            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            print(f'\n Overall best solution found in iteration {bestIteration}: \n {bestSolution}')

            print(f' Iterations without improvement: {iterationsWithoutImprovement}')
            
            temperature = temperature * self.tempDecreaseFactor

            if iterationsWithoutImprovement >= self.maxIterationsWithoutImprovement:
                print(f"The limit of {self.maxIterationsWithoutImprovement} iterations without improvement has been reached.")
                currentSolution = bestSolution
                lineSolution = currentSolution
                iterationsWithoutImprovement = 0
            
            iteration += 1

            usedTime = time.time() - startTime

        print(f'\n SAILS finished after {iteration} iterations and {usedTime} seconds')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution
    
    
    def Perturbation(self, solution: Solution, types:list[str] = ['remove', 'shake']) -> Solution:
        ''' Perturbation to escape local optima '''


        # choose type of perturbation randomly
        self.Types = types
        type = self.RNG.choice(self.Types, replace = False)

        print(f'\n Perturbation type: {type}')
        
        if type == 'remove': # Random removal of jobs
            valid_elements = [(key, sublist_idx, item_idx, item) 
                            for key, sublists in solution.RoutePlan.items()
                            for sublist_idx, sublist in enumerate(sublists) 
                            for item_idx, item in enumerate(sublist) 
                            if item <= 1000]

            newRoutePlan = deepcopy(solution.RoutePlan)
            if len(valid_elements) >= self.jobsToRemove :
                to_remove = self.RNG.choice(valid_elements, self.jobsToRemove, replace = False)
                for key, sublist_idx, item_idx, item in to_remove:
                    newRoutePlan[key][sublist_idx].remove(item)

            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)


        elif type == 'shake': # random removal of consectitive jobs
            
            newRoutePlan = deepcopy(solution.RoutePlan)

            all_sublists = [(key, sublist) for key, sublists in newRoutePlan.items() for sublist in sublists]
            indices = self.RNG.choice(len(all_sublists), min(self.sublists_to_modify, len(all_sublists)), replace=False)
            selected_sublists = [all_sublists[i] for i in indices]  # Select sublists using the chosen indices

            for key, sublist in selected_sublists:
                valid_positions = [i for i in range(len(sublist) - self.consecutive_to_remove + 1)
                                    if all(sublist[i + j] <= 1000 for j in range(self.consecutive_to_remove))]

                if valid_positions:
                    start_pos = self.RNG.choice(a = valid_positions, replace = False)
                    del sublist[start_pos:start_pos + self.consecutive_to_remove]


            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)
        

        return currentSolution



class Adaptive_SAILS(IteratedLocalSearch):
    """ A combination of Simulated Annealing and Iterative local search.."""

    def __init__(self, inputData: InputData, 
                 maxRunTime: int,  # Add the missing parameter
                 jobs_to_remove: int,  # Add the missing parameter
                 sublists_to_modify: int,  # Add the missing parameter
                 consecutive_to_remove: int,  # Add the missing parameter
                 start_temperature: int,
                 min_temperature: float,
                 temp_decrease_factor: float,
                 maxInnerLoop: int,
                 maxIterationsWithoutImprovement: int,
                 score_threshold: int = 1000,
                 neighborhoodEvaluationStrategyDelta: str = 'BestImprovement',
                 neighborhoodEvaluationStrategyProfit: str = 'BestImprovement',
                 neighborhoodTypesDelta: list[str] = ['SwapWaiting'],
                 neighborhoodTypesProfit: list[str] = ['SwapWaiting']):
        super().__init__(inputData, maxRunTime, jobs_to_remove, sublists_to_modify,consecutive_to_remove)

        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature
        self.maxInnerLoop = maxInnerLoop
        self.maxIterationsWithoutImprovement = maxIterationsWithoutImprovement
        self.ScoreThreshold = score_threshold
        self.NeighborhoodEvaluationStrategyDelta = neighborhoodEvaluationStrategyDelta
        self.NeighborhoodEvaluationStrategyProfit = neighborhoodEvaluationStrategyProfit
        self.NeighborhoodTypesDelta = neighborhoodTypesDelta
        self.NeighborhoodTypesProfit = neighborhoodTypesProfit
        self.NeighborhoodTypes = neighborhoodTypesDelta + neighborhoodTypesProfit


    def Run(self, solution: Solution) -> Solution:

        self.InitializeNeighborhoods()
        
        print('\nStarting Adaptive SAILS (Simualted Annealing Iterated Local Search)')
        print(f'\n Running initial local search')

        for neighborhoodType in self.NeighborhoodTypesDelta + self.NeighborhoodTypesProfit:    
            print(f' Running neighborhood {neighborhoodType}')
            neighboorhood = self.Neighborhoods[neighborhoodType]
            solution = neighboorhood.LocalSearch('BestImprovement', solution)

        currentSolution = solution
        lineSolution = solution
        print(f' Solution after initial local search:\n {currentSolution}')

        iteration = 1
        iterationsWithoutImprovement = 0
        bestIteration = 'initial local search'
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        temperature = self.startTemperature
        
        startTime = time.time()
        usedTime = 0

        scores = [100/len(self.NeighborhoodTypesDelta)]* len(self.NeighborhoodTypesDelta)

        while self.maxRunTime  > usedTime:
            print(f'\nStarting iteration {iteration}')

            innerLoop = 1
            while innerLoop < self.maxInnerLoop:

                print(f'Scores: {scores}')
                total_score = sum(scores)
                probabilities = [score / total_score for score in scores]
                neighborhoodTypeDelta = np.random.choice(self.NeighborhoodTypesDelta, p=probabilities, replace=False)


                take_first = np.random.choice([True, False], p=[0.5, 0.5])
                if take_first:
                    neighborhoodTypesProfit = self.NeighborhoodTypesProfit[:1]
                else:
                    neighborhoodTypesProfit = self.NeighborhoodTypesProfit



                print(f'\n Iteration.InnerLoop {iteration}.{innerLoop}')
                print(f' Running perturbation')
                currentSolution = self.Perturbation(currentSolution)
                print(f' Solution after perturbation in iteration {iteration}.{innerLoop}: \n {currentSolution}')
                
                print(f'\n Running local search after perturbation')

                # Only Insert or Insert and ReplaceProfit 50/50% chance
                for neighborhoodType in neighborhoodTypesProfit:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)

                waitingTimeBeforeDelta = currentSolution.WaitingTime

                # Delta Neighborhoods with probability weight, if waiting time diff more than 1000 then raise score
                print(f' Running neighborhood {neighborhoodTypeDelta}')
                neighboorhood = self.Neighborhoods[neighborhoodTypeDelta]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyDelta, currentSolution)

                waitingTimeDifference = currentSolution.WaitingTime - waitingTimeBeforeDelta

                if waitingTimeDifference > self.ScoreThreshold:
                    scores[self.NeighborhoodTypesDelta.index(neighborhoodTypeDelta)] += 1


                # Only Insert or Insert and ReplaceProfit 50/50% chance
                for neighborhoodType in neighborhoodTypesProfit:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategyProfit, currentSolution)

                print(f' Solution after local search in iteration {iteration}.{innerLoop}:\n {currentSolution}')

                if currentSolution.TotalProfit > lineSolution.TotalProfit:
                    lineSolution = currentSolution
                    if currentSolution.TotalProfit > bestSolution.TotalProfit:
                        bestSolution = currentSolution
                        iterationsWithoutImprovement = 0
                        bestIteration = iteration
                    else:
                        iterationsWithoutImprovement += 1
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature)):
                        lineSolution = currentSolution   
                    else:
                        currentSolution = lineSolution

                    iterationsWithoutImprovement += 1
                
                innerLoop += 1

            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            print(f'\n Overall best solution found in iteration {bestIteration}: \n {bestSolution}')

            print(f' Iterations without improvement: {iterationsWithoutImprovement}')
            
            temperature = temperature * self.tempDecreaseFactor

            if iterationsWithoutImprovement >= self.maxIterationsWithoutImprovement:
                print(f"The limit of {self.maxIterationsWithoutImprovement} iterations without improvement has been reached.")
                currentSolution = bestSolution
                lineSolution = currentSolution
                iterationsWithoutImprovement = 0
            
            iteration += 1

            usedTime = time.time() - startTime

        print(f'\n SAILS finished after {iteration} iterations and {usedTime} seconds')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution
    
    
    def Perturbation(self, solution: Solution, types:list[str] = ['remove', 'shake']) -> Solution:
        ''' Perturbation to escape local optima '''


        # choose type of perturbation randomly
        self.Types = types
        type = self.RNG.choice(self.Types, replace = False)

        print(f'\n Perturbation type: {type}')
        
        if type == 'remove': # Random removal of jobs
            valid_elements = [(key, sublist_idx, item_idx, item) 
                            for key, sublists in solution.RoutePlan.items()
                            for sublist_idx, sublist in enumerate(sublists) 
                            for item_idx, item in enumerate(sublist) 
                            if item <= 1000]

            newRoutePlan = deepcopy(solution.RoutePlan)
            if len(valid_elements) >= self.jobsToRemove :
                to_remove = self.RNG.choice(valid_elements, self.jobsToRemove, replace = False)
                for key, sublist_idx, item_idx, item in to_remove:
                    newRoutePlan[key][sublist_idx].remove(item)

            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)


        elif type == 'shake': # random removal of consectitive jobs
            
            newRoutePlan = deepcopy(solution.RoutePlan)

            all_sublists = [(key, sublist) for key, sublists in newRoutePlan.items() for sublist in sublists]
            indices = self.RNG.choice(len(all_sublists), min(self.sublists_to_modify, len(all_sublists)), replace=False)
            selected_sublists = [all_sublists[i] for i in indices]  # Select sublists using the chosen indices

            for key, sublist in selected_sublists:
                valid_positions = [i for i in range(len(sublist) - self.consecutive_to_remove + 1)
                                    if all(sublist[i + j] <= 1000 for j in range(self.consecutive_to_remove))]

                if valid_positions:
                    start_pos = self.RNG.choice(a = valid_positions, replace = False)
                    del sublist[start_pos:start_pos + self.consecutive_to_remove]


            currentSolution = Solution(newRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(currentSolution)
        

        return currentSolution



class SimulatedAnnealingLocalSearch(ImprovementAlgorithm):
    """ Simulated Annealing algorithm with perturbation to escape local optima. """

    def __init__(self, inputData: InputData,
                 start_temperature:int,
                 min_temperature:float,
                 temp_decrease_factor:float,
                 maxRunTime:int,
                 #'SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'
                 #Replace Delta select tasks more than once! 
                 neighborhoodTypesDelta: list[str] = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute',"ReplaceDelta"],
                 neighborhoodTypesProfit: list[str] = ['Insert','ReplaceProfit']):
        super().__init__(inputData)

        self.neighborhoodTypesDelta = neighborhoodTypesDelta
        self.neighborhoodTypesProfit = neighborhoodTypesProfit
        self.maxRunTime = maxRunTime
        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature
        self.DeltaNeighborhoods = {}
        self.ProfitNeighborhoods = {}

    def Run(self, currentSolution: Solution) -> Solution:

        self.InitializeNeighborhoods(neighborhoodtypes = self.neighborhoodTypesDelta, neighborhoods_dict = self.DeltaNeighborhoods)
        self.InitializeNeighborhoods(neighborhoodtypes = self.neighborhoodTypesProfit, neighborhoods_dict = self.ProfitNeighborhoods)

        print('\nStarting Simulated Annealing Local Search Procedure')

        startTime = time.time()
        usedTime = 0

        bestLoop = 0
        temperature = self.startTemperature
        iteration = 1

        probabilities = [1/len(self.DeltaNeighborhoods) for i in range(len(self.DeltaNeighborhoods))]

        while self.maxRunTime > usedTime:
            
            #Update at beginning and before every iteration of Local Improvement
            bestSolutionWaitingTime = currentSolution.WaitingTime
            
            print(f'\nStarting iteration {iteration}')

            #SA mit Delta Nachbarschaften --> Wartezeit als Kriterium
            innerLoop = 0
            bestLoop = 0
                        
            print(f'\nRunning Simulated Annealing for Delta neighborhoods')
            temperature = self.startTemperature

            while temperature > self.minTemp:
          
                delta_neighborhood = self.RNG.choice(list(self.DeltaNeighborhoods.values()), p = probabilities)

                move = delta_neighborhood.SingleMove(currentSolution)

                if move.Delta  < 0:
                    completeRouteplan = delta_neighborhood.constructCompleteRoute(move,currentSolution)
                    
                    currentSolution.setRoutePlan(completeRouteplan, self.InputData)
                    if delta_neighborhood.Type != "ReplaceDelta":
                        currentSolution.remove_unused_Task(move.UnusedTask)
                    self.EvaluationLogic.evaluateSolution(currentSolution)
            
                    if currentSolution.WaitingTime > bestSolutionWaitingTime:
                        
                        #Create Best Known Solution
                        bestLoop = innerLoop
                        bestKnownSolution = Solution(deepcopy(completeRouteplan), self.InputData)
                        self.EvaluationLogic.evaluateSolution(bestKnownSolution) #Evaluate Sol
                        #self.SolutionPool.AddSolution(bestKnownSolution)
                        #Schauen ob die vorhergehenden Lösungen gleich bleiben -> Debug Modus 
                        bestSolutionWaitingTime = bestKnownSolution.WaitingTime
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp(-move.Delta / (temperature)):
                        completeRouteplan = delta_neighborhood.constructCompleteRoute(move,currentSolution)
                        currentSolution.setRoutePlan(completeRouteplan, self.InputData)
                        if delta_neighborhood.Type != "ReplaceDelta":
                            currentSolution.remove_unused_Task(move.UnusedTask)
                        self.EvaluationLogic.evaluateSolution(currentSolution)
                

                temperature = temperature * self.tempDecreaseFactor

                innerLoop += 1
            
            bestSolution = Solution(bestSolutionRoutePlan, self.InputData)
            self.EvaluationLogic.evaluateSolution(bestSolution)
            self.SolutionPool.AddSolution(bestSolution)
            #bestSolution = self.SolutionPool.GetHighestProfitSolution() # Need to update current solution since SA algorithm could result in a worse current solution


            #Overwrite before Local Search
            if bestLoop > 0:
                currentSolution = bestKnownSolution

                #print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
                print(f' Best solution after inner loop {bestLoop}/{innerLoop}, {bestKnownSolution}')
                
            else: 
                #print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
                print(f' Best solution after inner loop {bestLoop}/{innerLoop}, {currentSolution}')


            for profit_neighbor_name,profit_neighbor in self.ProfitNeighborhoods.items():

                print(f'\nRunning local search for {profit_neighbor_name} neighborhood')
                currentSolution = profit_neighbor.LocalSearch('BestImprovement', currentSolution)
            
                #print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
                print(f' Best solution after local search: {currentSolution}')
                

            usedTime = time.time() - startTime
 
            iteration += 1



        print(f'Number of total iterations: {iteration}')
        return self.SolutionPool.GetHighestProfitSolution()


# ------------------------------------------ PREVIOUS ATTEMPT # ------------------------------------------ 
'''
class SimulatedAnnealingLocalSearch(ImprovementAlgorithm):
    """ Simulated Annealing algorithm with perturbation to escape local optima. """

    def __init__(self, inputData: InputData,
                 start_temperature:int,
                 min_temperature:float,
                 temp_decrease_factor:float,
                 maxRunTime:int,
                 neighborhoodTypesDelta: list[str] = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'], neighborhoodTypesProfit: list[str] = ['Insert','ReplaceProfit']):
        super().__init__(inputData)

        self.neighborhoodTypesDelta = neighborhoodTypesDelta
        self.neighborhoodTypesProfit = neighborhoodTypesProfit
        self.NeighborhoodTypes = neighborhoodTypesDelta + neighborhoodTypesProfit
        self.maxRunTime = maxRunTime
        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature


    def Run(self, solution: Solution) -> Solution:

        self.InitializeNeighborhoods()

        print('\nStarting Simulated Annealing Local Search Procedure')

        startTime = time.time()
        usedTime = 0

        currentSolution = solution
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        
    
        
        iteration = 1
        number = 1/len(self.neighborhoodTypesDelta)
        probabilities = [number for i in range(len(self.neighborhoodTypesDelta))]
        

        while self.maxRunTime > usedTime:

            print(f'\nStarting iteration {iteration}')
            temperature = self.startTemperature


            #SA mit Delta Nachbarschaften --> Wartezeit als Kriterium
            innerLoop = 0
            bestLoop = 0
                        
            SAstartTime = time.time()
            print(f'\nRunning Simulated Annealing for Delta neighborhoods')
            while temperature > self.minTemp:
                
                
            

                neighborhoodType = self.RNG.choice(self.neighborhoodTypesDelta, p = probabilities)

                neighborhood = self.Neighborhoods[neighborhoodType]
                newSolution = neighborhood.SingleMove(currentSolution)

                objDifference = newSolution.WaitingTime - currentSolution.WaitingTime
                print(f'New Solution Waiting Time: {newSolution.WaitingTime}, Current Solution Waiting Time: {currentSolution.WaitingTime}')
                #objDifference2 = move.Delta
                print(f'ObjDifference: {objDifference}')


                if objDifference > 0:
                    currentSolution = newSolution
                    #print(f'New solution is better than current solution')
                    if newSolution.WaitingTime > bestSolution.WaitingTime:
                        #print(f'New best solution found!!!!')
                        bestSolution = newSolution
                        bestLoop = innerLoop
                        self.SolutionPool.AddSolution(bestSolution)
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp(objDifference / (temperature)):
                        currentSolution = newSolution
                        #print(f'Accepting worse solution with probability {math.exp(objDifference / (temperature))}')
                    #print(f'Rejecting worse solution with probability {math.exp(objDifference / (temperature))}')

                temperature = temperature * self.tempDecreaseFactor

                innerLoop += 1



            usedTime = time.time() - SAstartTime

            print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
            print(f' Best solution after inner loop {bestLoop}/{innerLoop}: {bestSolution}')

            # Lokale Suche mit Insert Nachbarschaft

            neighborhoodType = 'Insert'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.Neighborhoods[neighborhoodType]
            

            LSstartTime = time.time()
            currentSolution = neighborhood.LocalSearch('BestImprovement', bestSolution)
            usedTime = time.time() - LSstartTime
            
            print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
            print(f' Best solution after local search: {currentSolution}')


            # Lokale Suche mit ReplaceProfit Nachbarschaft
            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            neighborhoodType = 'ReplaceProfit'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.Neighborhoods[neighborhoodType]
            

            LSstartTime = time.time()
            currentSolution = neighborhood.LocalSearch('BestImprovement', bestSolution)
            usedTime = time.time() - LSstartTime
            
            print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
            print(f' Best solution after local search: {currentSolution}')


            usedTime = time.time() - startTime
            
            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            iteration += 1



        print(f'Number of total iterations: {iteration}')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution

'''

#### OLD STUFF

'''

         

            #SA mit ReplaceProfit Nachbarschaft --> Profit als Kriterium
            SAstartTime = time.time()
            temperature = 1000
            a = 0.99
            minTemperature = 1e-20
            innerLoop = 0
            bestLoop = 0

            print(f'\nRunning Simulated Annealing for ReplaceProfit neighborhood')
            while temperature > minTemperature:

                neighborhood = self.CreateNeighborhood('ReplaceProfit')

                newSolution = neighborhood.SingleMove(currentSolution)

                objDifference = newSolution.TotalProfit - currentSolution.TotalProfit

                if objDifference > 0:
                    currentSolution = newSolution
                    if newSolution.TotalProfit > bestSolution.TotalProfit:
                        bestSolution = newSolution
                        bestLoop = innerLoop
                        self.SolutionPool.AddSolution(bestSolution)
                        print('New best Solution found!!!!')
                else:
                    random_number = numpy.random.uniform(0,1)
                    if random_number < math.exp(objDifference / (temperature)):
                        currentSolution = newSolution

                temperature = temperature * a

                innerLoop += 1

            
            usedTime = time.time() - SAstartTime

            print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
            print(f' Best solution after inner loop {bestLoop}/{innerLoop}: {bestSolution}')

            iteration += 1        
            usedTime = time.time() - startTime

            currentSolution = self.SolutionPool.GetHighestProfitSolution()
        
        print(f'Number of total iterations: {iteration}')
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        return bestSolution








                
                




class IteratedGreedy(ImprovementAlgorithm):
    """ Iterated greedy algorithm with destruction and construction. """

    def __init__(self, inputData:InputData, numberJobsToRemove:int, baseTemperature:int, maxIterations:int, localSearchAlgorithm:IterativeImprovement = None,no_lots_boolean:bool = False):
        super().__init__(inputData, no_lots_boolean)

        self.NumberJobsToRemove = numberJobsToRemove
        self.BaseTemperature = baseTemperature
        self.MaxIterations = maxIterations

        if localSearchAlgorithm is not None:

            # Not defined here and can be selected! 
            self.LocalSearchAlgorithm = localSearchAlgorithm
        else:
            self.LocalSearchAlgorithm = IterativeImprovement(self.InputData, neighborhoodTypes=[]) # IterativeImprovement without a neighborhood does not modify the solution
    
    def Initialize(self, evaluationLogic:EvaluationLogic, solutionPool:SolutionPool, rng) -> None:
        """Initialize Iterated Greedy Algorithm and the local search algorithm"""

        self.EvaluationLogic = evaluationLogic
        self.SolutionPool = solutionPool
        self.RNG = rng

        self.LocalSearchAlgorithm.Initialize(self.EvaluationLogic, self.SolutionPool, self.RNG)
    
    def Destruction(self, currentSolution:Solution) -> (list[int],list[int]):
        """Randomly removes jobs from the current solution. Here, _numberJobsToRemove_ is a parameter of the Iterated Greedy.
           The result is the set of removed jobs _removedJobs_ and an incomplete solution _partialPermutation_.
        """
        
        removedJobs = self.RNG.choice(self.InputData.n_jobs, size=self.NumberJobsToRemove, replace = False).tolist()

        partialPermutation = [i for i in currentSolution.Permutation if i not in removedJobs]

        #Works even though that partial lotmatrix is just copied lot matrixx 
        partialLotMatrix = [i for i in currentSolution.lot_matrix if i not in removedJobs]

        return removedJobs, partialPermutation, partialLotMatrix

    def Construction(self, removedJobs:list[int], partial_permutation:list[int], partial_lotmatrix:list[list[int]]) -> Solution:
        """Add the _removedJobs_ to _partialPermutation_ again, observing the order at the best position (NEH) in each case, and return the new complete solution.
        """

        #Create a new Solution with the partial permutation
        completeSolution = Solution(self.InputData.InputJobs, self.InputData.InputStages, partial_permutation, partial_lotmatrix, )
        
        #Add jobs iteratively
        for i in removedJobs:
            self.EvaluationLogic.DetermineBestInsertion(completeSolution, i)

        return completeSolution

    def AcceptWorseSolution(self, currentObjectiveValue:int, newObjectiveValue:int) -> bool:
        """ Accept Worse Solution in regards to temperature: 
        
            In the Ruiz/Stützle method, pi represents the new solution , and pi´ represents the current solution .
            T is the second parameter of the Iterated Greedy algorithm. The higher T is, the more likely it is to accept worse solutions.
        """
        randomNumber = self.RNG.random()

        totalProcessingTime = sum(x.ProcessingTime(i) for x in self.InputData.InputJobs for i in range(len(x.Operations)))
        Temperature = self.BaseTemperature * totalProcessingTime / (self.InputData.n_jobs * self.InputData.n_stages * 10)
        probability = math.exp(-(newObjectiveValue - currentObjectiveValue) / Temperature)
        
        return randomNumber <= probability

    def Run(self, currentSolution:Solution) -> Solution:
        """ Accept a new solution as the current one if:
            1. The new solution is better than the current solution (always the case).
            2. The acceptance criterion is met (happens randomly).

            The new best solution is stored in the "SolutionPool".
        """
        currentSolution = self.LocalSearchAlgorithm.Run(currentSolution)

        currentBest = self.SolutionPool.GetLowestMakespanSolution().Makespan
        iteration = 0
        while(iteration < self.MaxIterations):
            removedJobs, partialPermutation, partialLotMatrix = self.Destruction(currentSolution)
            newSolution = self.Construction(removedJobs, partialPermutation,partialLotMatrix)

            newSolution = self.LocalSearchAlgorithm.Run(newSolution)
            
            if newSolution.Makespan < currentSolution.Makespan:
                currentSolution = newSolution

                if newSolution.Makespan < currentBest:
                    print(f'New best solution in iteration {iteration}: {currentSolution}')
                    self.SolutionPool.AddSolution(currentSolution)
                    currentBest = newSolution.Makespan

            elif self.AcceptWorseSolution(currentSolution.Makespan, newSolution.Makespan):
                currentSolution = newSolution

            iteration += 1

        return self.SolutionPool.GetLowestMakespanSolution()


'''