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

    def InitializeNeighborhoods(self, solution: Solution) -> None:
        ''' Create several neighborhoods for every neighborhood in the list neighborhoodTypes'''

        for neighborhoodType in self.NeighborhoodTypes:
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            self.Neighborhoods[neighborhoodType] = neighborhood


class IterativeImprovement(ImprovementAlgorithm):
    """ Iterative improvement algorithm through sequential variable neighborhood descent. 
        Local Search with itereative steps through many different neighborhoods.
    """

    def __init__(self,  inputData:InputData, neighborhoodEvaluationStrategy:str = 'BestImprovement', neighborhoodTypes:list[str] = ['SwapWaiting']):
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)

    def Run(self, solution:Solution) -> Solution:
        ''' Run local search with given solutions and iterate through all given neighborhood types'''

        self.InitializeNeighborhoods(solution)    

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

    def __init__(self, inputData: InputData, maxRunTime:int, jobs_to_remove:int, sublists_to_modify:int,consecutive_to_remove:int,
                    neighborhoodEvaluationStrategy: str = 'BestImprovement', neighborhoodTypes: list[str] = ['SwapWaiting']):
        super().__init__(inputData, neighborhoodEvaluationStrategy, neighborhoodTypes)

        self.maxRunTime = maxRunTime
        self.jobsToRemove = jobs_to_remove 
        self.sublists_to_modify = sublists_to_modify
        self.consecutive_to_remove = consecutive_to_remove

    def Run(self, currentSolution: Solution) -> Solution:
        ''' Run local search with given solutions and iterate through all given neighborhood types '''

        self.InitializeNeighborhoods(currentSolution)
        
        print('\nStarting Iterated Local Search')
        print(f' Solution after initial local search:\n {currentSolution}')

        iteration = 1
        threshold1 = 2
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
            for neighborhoodType in self.NeighborhoodTypes:
                print(f' Running neighborhood {neighborhoodType}')
                neighboorhood = self.Neighborhoods[neighborhoodType]
                currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategy, currentSolution)
            print(f' Solution after local search in iteration {iteration}:\n {currentSolution}')

            
            if currentSolution.TotalProfit > bestSolution.TotalProfit:
                iterationsWithoutImprovement = 0
                bestIteration = iteration
            else:
                iterationsWithoutImprovement += 1

            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            print(f'\n Overall best solution found in iteration {bestIteration}: \n {bestSolution}')

            print(f' Iterations without improvement: {iterationsWithoutImprovement}')
            
            if iterationsWithoutImprovement == threshold1:
                print(f"The threshold of {threshold1} iterations without improvement has been reached.")
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
                 neighborhoodEvaluationStrategy: str = 'BestImprovement', 
                 neighborhoodTypes: list[str] = ['SwapWaiting']):
        super().__init__(inputData, maxRunTime, jobs_to_remove, sublists_to_modify,consecutive_to_remove,neighborhoodEvaluationStrategy, neighborhoodTypes)

        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature
        self.maxInnerLoop = maxInnerLoop
        self.maxIterationsWithoutImprovement = maxIterationsWithoutImprovement


    def Run(self, solution: Solution) -> Solution:

        self.InitializeNeighborhoods(solution)
        
        print('\nStarting SAILS (Simualted Annealing Iterated Local Search)')
        print(f'\n Running initial local search')

        initialNeighborhoodTypes = ['SwapIntraRoute', 'SwapInterRoute', 'TwoEdgeExchange', 'ReplaceDelta', 'Insert', 'ReplaceProfit']

        for neighborhoodType in initialNeighborhoodTypes:    
            print(f' Running neighborhood {neighborhoodType}')
            neighboorhood = self.Neighborhoods[neighborhoodType]
            solution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategy, solution)

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

        profitNeighborhoods = ['Insert', 'ReplaceProfit']
        deltaNeighborhoods = ['SwapIntraRoute', 'TwoEdgeExchange', 'SwapInterRoute', 'ReplaceDelta']


        while self.maxRunTime  > usedTime:
            print(f'\nStarting iteration {iteration}')

            innerLoop = 0
            while innerLoop < self.maxInnerLoop:

                print(f'\n Iteration.InnerLoop {iteration}.{innerLoop}')
                print(f' Running perturbation')
                currentSolution = self.Perturbation(currentSolution)
                print(f' Solution after perturbation in iteration {iteration}.{innerLoop}: \n {currentSolution}')
                
                print(f'\n Running local search after perturbation')

                for neighborhoodType in profitNeighborhoods:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategy, currentSolution)


                for neighborhoodType in deltaNeighborhoods:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch('FirstImprovement', currentSolution)


                for neighborhoodType in profitNeighborhoods:
                    print(f' Running neighborhood {neighborhoodType}')
                    neighboorhood = self.Neighborhoods[neighborhoodType]
                    currentSolution = neighboorhood.LocalSearch(self.NeighborhoodEvaluationStrategy, currentSolution)

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
                    print(f'Line solution: {lineSolution.TotalProfit}, Current solution: {currentSolution.TotalProfit}')
                    print(f"Temperature: {temperature}")
                    print(f"Random number: {random_number}")
                    print(f"Exponential: {math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature))}")
                    if random_number < math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature)):
                        print(f'Accepting worse solution with probability {math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature))}')
                        lineSolution = currentSolution   
                    else:
                        print(f'Rejecting worse solution with probability {math.exp((currentSolution.TotalProfit - lineSolution.TotalProfit) / (temperature))}')
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
        self.maxRunTime = maxRunTime
        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature


    def Run(self, currentSolution: Solution) -> Solution:

        #self.InitializeNeighborhoods(solution)

        print('\nStarting Simulated Annealing Local Search Procedure')

        startTime = time.time()
        usedTime = 0

        
        bestLoop = 0
        temperature = self.startTemperature
        iteration = 1

        neighborhoods = [self.CreateNeighborhood(neighborhood_type) for neighborhood_type in self.neighborhoodTypesDelta]
        number = 1/len(self.neighborhoodTypesDelta)
        probabilities = [number for i in range(len(self.neighborhoodTypesDelta))]
        
        neighborhood = self.CreateNeighborhood('SwapIntraRoute') 

        while self.maxRunTime > usedTime:

            bestSolutionWaitingTime = self.SolutionPool.GetHighestProfitSolution().WaitingTime
            print(f'\nStarting iteration {iteration}')


            #SA mit Delta Nachbarschaften --> Wartezeit als Kriterium
            innerLoop = 0
            bestLoop = 0
                        
            SAstartTime = time.time()
            print(f'\nRunning Simulated Annealing for Delta neighborhoods')
            temperature = self.startTemperature

            while temperature > self.minTemp:
          
                #neighborhood = self.RNG.choice(neighborhoods, p = probabilities)

                move = neighborhood.SingleMove(currentSolution)

                if move.Delta  < 0:
                    completeRouteplan = neighborhood.constructCompleteRouteFromSolution(move,currentSolution)
                    currentSolution.setRoutePlan(completeRouteplan, self.InputData)
                    self.EvaluationLogic.evaluateSolution(currentSolution)

                    if currentSolution.WaitingTime > bestSolutionWaitingTime:

                        bestLoop = innerLoop
                        self.SolutionPool.AddSolution(currentSolution)
                        bestSolutionWaitingTime = currentSolution.WaitingTime
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp(-move.Delta / (temperature)):
                        completeRouteplan = neighborhood.constructCompleteRouteFromSolution(move,currentSolution)
                        currentSolution.setRoutePlan(completeRouteplan, self.InputData)
                        self.EvaluationLogic.evaluateSolution(currentSolution)
                

                temperature = temperature * self.tempDecreaseFactor

                innerLoop += 1



            usedTime = time.time() - SAstartTime

            print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
            print(f' Best solution after inner loop {bestLoop}/{innerLoop}, {currentSolution}')

            # Lokale Suche mit Insert Nachbarschaft
            currentSolution = self.SolutionPool.GetHighestProfitSolution()

            neighborhoodType = 'Insert'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            

            LSstartTime = time.time()
            currentSolution = neighborhood.LocalSearch('BestImprovement', currentSolution)
            usedTime = time.time() - LSstartTime
            
            print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
            print(f' Best solution after local search: {currentSolution}')


            # Lokale Suche mit ReplaceProfit Nachbarschaft

            neighborhoodType = 'ReplaceProfit'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            

            LSstartTime = time.time()
            currentSolution = neighborhood.LocalSearch('BestImprovement', currentSolution)
            usedTime = time.time() - LSstartTime
            
            print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
            print(f' Best solution after local search: {currentSolution}')


            usedTime = time.time() - startTime
        

            iteration += 1



        print(f'Number of total iterations: {iteration}')
        return  self.SolutionPool.GetHighestProfitSolution()


# ------------------------------------------ PREVIOUS ATTEMPT # ------------------------------------------ 
'''
class SimulatedAnnealingLocalSearch(ImprovementAlgorithm):
    """ Simulated Annealing algorithm with perturbation to escape local optima. """

    def _init_(self, inputData: InputData,
                 start_temperature:int,
                 min_temperature:float,
                 temp_decrease_factor:float,
                 maxRunTime:int,
                 neighborhoodTypesDelta: list[str] = ['SwapIntraRoute','TwoEdgeExchange','SwapInterRoute','ReplaceDelta'], neighborhoodTypesProfit: list[str] = ['Insert','ReplaceProfit']):
        super()._init_(inputData)

        self.neighborhoodTypesDelta = neighborhoodTypesDelta
        self.neighborhoodTypesProfit = neighborhoodTypesProfit
        self.maxRunTime = maxRunTime
        self.startTemperature = start_temperature
        self.tempDecreaseFactor = temp_decrease_factor
        self.minTemp = min_temperature


    def Run(self, solution: Solution) -> Solution:

        #self.InitializeNeighborhoods(solution)

        print('\nStarting Simulated Annealing Local Search Procedure')

        startTime = time.time()
        usedTime = 0

        currentSolution = solution
        bestSolution = self.SolutionPool.GetHighestProfitSolution()

        
        
        bestLoop = 0
        temperature = self.startTemperature
        iteration = 1
        

        while self.maxRunTime > usedTime:

            print(f'\nStarting iteration {iteration}')


            #SA mit Delta Nachbarschaften --> Wartezeit als Kriterium
            innerLoop = 0
            bestLoop = 0
                        
            SAstartTime = time.time()
            print(f'\nRunning Simulated Annealing for Delta neighborhoods')
            while temperature > self.minTemp:
                
                number = 1/len(self.neighborhoodTypesDelta)
                probabilities = [number for i in range(len(self.neighborhoodTypesDelta))]
                selected_neighborhood = self.RNG.choice(self.neighborhoodTypesDelta, p = probabilities)

                neighborhood = self.CreateNeighborhood(selected_neighborhood)
                newSolution = neighborhood.SingleMove(currentSolution)

                objDifference = newSolution.WaitingTime - currentSolution.WaitingTime

                if objDifference > 0:
                    currentSolution = newSolution
                    if newSolution.WaitingTime > bestSolution.WaitingTime:
                        bestSolution = newSolution
                        bestLoop = innerLoop
                        self.SolutionPool.AddSolution(bestSolution)
                else:
                    random_number = self.RNG.random()
                    if random_number < math.exp(objDifference / (temperature)):
                        currentSolution = newSolution

                temperature = temperature * self.tempDecreaseFactor

                innerLoop += 1



            usedTime = time.time() - SAstartTime

            print(f'\n Time needed to find simulated annealing solution: {round(usedTime,2)} seconds')
            print(f' Best solution after inner loop {bestLoop}/{innerLoop}: {bestSolution}')

            # Lokale Suche mit Insert Nachbarschaft

            neighborhoodType = 'Insert'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            

            LSstartTime = time.time()
            currentSolution = neighborhood.LocalSearch('BestImprovement', bestSolution)
            usedTime = time.time() - LSstartTime
            
            print(f'\n Time to find local search solution: {round(usedTime,2)} seconds')
            print(f' Best solution after local search: {currentSolution}')


            # Lokale Suche mit ReplaceProfit Nachbarschaft
            bestSolution = self.SolutionPool.GetHighestProfitSolution()

            neighborhoodType = 'ReplaceProfit'

            print(f'\nRunning local search for {neighborhoodType} neighborhood')
            neighborhood = self.CreateNeighborhood(neighborhoodType)
            

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