from itertools import permutations
import time
import numpy
from OutputData import *
#from EvaluationLogic import EvaluationLogic

class ConstructiveHeuristics:
    ''' Class for creating objects to run different constructive heuristics'''

    def __init__(self,  solutionPool:SolutionPool):

        #self.EvaluationLogic = evaluationLogic
        self._SolutionPool = solutionPool

    def _create_initial_route_plan(self, inputData:InputData) -> dict[str, list[list[int]]]:
        ''' Prefilles every day with one repsective main task for each cohort'''

        #Empty route plan
        routeplan = {}
        
        #Iterate over all days and cohorts and add the respective main task to the route plan
        for day in range(inputData.days):
            routeplan[day] = []
            for t in range(1001,len(inputData.allTasks)):
                if inputData.allTasks[t].day == (day + 1):
                    routeplan[day].append([0,t,0])

        #Return the prefilled route plan
        return routeplan

    def Run(self, inputData:InputData, solutionMethod:str) -> None:
        ''' Choose one of the constructive heuristics and get a first solutiuon due to the chosen heuristic'''

        print('Generating an initial solution according to ' + solutionMethod + '.')

        #Rewrite any present solution
        solution = None 
        
        # Decision tree for choosing constructive heuristic 
        if solutionMethod == 'Greedy':
            solution = self._Greedy(inputData)
        else:
            print('Unkown constructive solution method: ' + solutionMethod + '.')

        #Add the first solution to the solution pool to proceed further with the algorithm
        self._SolutionPool.AddSolution(solution)

    def _Greedy(self, inputData:InputData) -> Solution:
        ''' Greedy heuristic to create a first solution - fills blank spots between main tasks with optional tasks'''

        prefilled_route_plan = self._create_initial_route_plan(inputData)

        tmpSolution = Solution(prefilled_route_plan, inputData)

        #self.EvaluationLogic.DefineStartEnd(tmpSolution)

        return tmpSolution

    """ 
    def ROS(self, jobList:list[OutputJob],stagelist:list[DataStage], x:int, seed:int) -> Solution:
        '''Create a random permutation x times for finding the best permutation''''''

        # Create dummy solution
        numpy.random.seed(seed)
        tmpSolution = Solution(jobList,stagelist,0)
        bestCmax = numpy.inf

        #Repeat x times 
        for i in range(x):
            tmpPermutation = numpy.random.permutation(len(jobList))
            # initialize Solution            
            tmpSolution.Permutation = tmpPermutation

            self.EvaluationLogic.DefineStartEnd(tmpSolution)

            if(tmpSolution.Makespan < bestCmax):
                bestCmax = tmpSolution.Makespan
                bestPermutation = tmpPermutation

        # Take best solution from x random permuations as return object 
        bestRandomSolution = Solution(jobList, stagelist,bestPermutation, no_lots=self.no_lots)
        self.EvaluationLogic.DefineStartEnd(bestRandomSolution)

        return bestRandomSolution

    def CheckAllPermutations(self, jobList:list[OutputJob],stagelist:list[DataStage]) -> Solution:
        ''' Create a set with all possible permutations and find the one with lowest makespan'''

        allPerms = set(permutations(range(len(jobList))))
        bestCmax = numpy.inf
        tmpSolution = Solution(jobList,stagelist,0)

        for tmpPerm in allPerms:
            tmpSolution.SetPermutation(tmpPerm)
            self.EvaluationLogic.DefineStartEnd(tmpSolution)  

            if(tmpSolution.Makespan < bestCmax):
                bestCmax = tmpSolution.Makespan
                bestPerm = tmpPerm

        bestSol = Solution(jobList,stagelist, bestPerm, no_lots=self.no_lots)
        self.EvaluationLogic.DefineStartEnd(bestSol)

        return bestSol 

    def FirstComeFirstServe(self, jobList:list[OutputJob],stagelist:list[DataStage] ) -> Solution:
        ''' Sorts jobs from 0 to x. job and calculates makespan'''

        tmpPermutation = [*range(len(jobList))]

        tmpSolution = Solution(jobList, stagelist,tmpPermutation, no_lots=self.no_lots)

        #Calculate makespan for FIFO solution
        self.EvaluationLogic.DefineStartEnd(tmpSolution)

        return tmpSolution
    
    def createTuple_Processing_Times(self, jobList:list[OutputJob], allMachines:bool) -> list: 
        ''' Creates a list of tuples with the job id and either the processing time of one machine or all machines (allMachines = True)'''

        jobPool = []

        # Creates a list of tuples with the jobIds and the sum of the processing times 
        for i in range(len(jobList)):
            if(allMachines):
                jobPool.append((i,sum(jobList[i].ProcessingTime(x) for x in range(len(jobList[i].Operations)))))
            else: 
                jobPool.append((i,jobList[i].ProcessingTime(0)))

        return jobPool

    def ShortestProcessingTime(self, jobList:list[OutputJob],stagelist:list[DataStage], allMachines:bool = False ) -> Solution:
        ''' Sorts the jobs from jobPool in ascending order of the processing times'''
        
        jobPool = self.createTuple_Processing_Times(jobList, allMachines)

        #Sort tuple list by the processing time 
        jobPool.sort(key=lambda x: x[1])

        #Get permutation list from the sorted tuple list
        tmpPermutation = [x[0] for x in jobPool]
        tmpSolution = Solution(jobList,stagelist, tmpPermutation, no_lots=self.no_lots)

        #Calculate Makespan
        self.EvaluationLogic.DefineStartEnd(tmpSolution)

        return tmpSolution  
    
    def LongestProcessingTime(self, jobList:list[OutputJob],stagelist:list[DataStage], allMachines:bool = False) -> Solution:
        ''' Sorts the jobs from jobPool in descending order of the processing times'''

        jobPool = self.createTuple_Processing_Times(jobList, allMachines)

        #Sort tuple list descending by the processing time 
        jobPool.sort(key=lambda x: x[1], reverse=True)

        #Get permutation list from the sorted tuple list
        tmpPermutation = [x[0] for x in jobPool]
        tmpSolution = Solution(jobList,stagelist, tmpPermutation, no_lots=self.no_lots)

        self.EvaluationLogic.DefineStartEnd(tmpSolution)

        return tmpSolution   

    def NEH(self, jobList:list[DataJob],stagelist:list[DataStage]) -> Solution:
        '''
        NEH heuristic (according to Nawaz, Enscore and Ham) -> Very good constructive heuristic for flow shop problems 
        Field of application: Minimization of the cycle time for general permutation flow store problems (F|prmtn|Cmax)

        1. order orders according to monotonically decreasing sum of processing times.
        2. set j = 2. take the first two orders and determine the cycle time for the sequences 1-2 and 2-1. fix the sequence with the lowest cycle time.
        3. set j = j + 1. create j new sequences by scheduling the order at position j at each position. Choose the permutation with the shortest cycle time.
        4. if j := n STOP, otherwise go to step 3.
                
        '''
        #Create lists for possible solutions and permutations
        jobPool = []
        tmpPerm = []

        # Calculate sum of processing times and sort descending (highest first!)
        for i in range(len(jobList)):

            jobPool.append((jobList[i].JobId,sum(jobList[i].ProcessingTime(x) for x in range(len(jobList[i].Operations)))))

        jobPool.sort(key=lambda x: x[1], reverse=True)

        # Initalize input
        tmpNEHOrder = [x[0] for x in jobPool]

        #add the first job of the sorted list to the permutation
        tmpPerm.append(tmpNEHOrder[0])

        #Create Solution
        tmpSolution = Solution(jobList,stagelist,tmpPerm, no_lots=self.no_lots)

        # Add next jobs in a loop and check all permutations
        for i in range(1,len(tmpNEHOrder)):
            # add next job to end and calculate makespan
            
                self.EvaluationLogic.DetermineBestInsertion(tmpSolution, tmpNEHOrder[i])
        
        return tmpSolution

    def Run(self, inputData:InputData, solutionMethod:str, no_lots:bool = False) -> None:
        ''' Choose one of the constructive heuristics and get a first solutiuon due to the chosen heuristic'''

        print('Generating an initial solution according to ' + solutionMethod + '.')

        #Rewrite any present solution
        solution = None 
        
        # Decision tree for choosing constructive heuristic 
        if solutionMethod == 'FCFS':
            solution = self.FirstComeFirstServe(inputData.InputJobs, inputData.InputStages)
        elif solutionMethod == 'SPT':
            solution = self.ShortestProcessingTime(inputData.InputJobs,inputData.InputStages)
        elif solutionMethod == 'LPT':
            solution = self.LongestProcessingTime(inputData.InputJobs,inputData.InputStages)
        elif solutionMethod == 'ROS':
            solution = self.ROS(inputData.InputJobs,inputData.InputStages, self.RandomRetries, self.RandomSeed)
        elif solutionMethod == 'NEH':
            solution = self.NEH(inputData.InputJobs,inputData.InputStages)
        elif solutionMethod == "BruteForce": 
            solution = self.CheckAllPermutations(inputData.InputJobs,inputData.InputStages)
        else:
            print('Unkown constructive solution method: ' + solutionMethod + '.')

        #Add the first solution to the solution pool to proceed further with the algorithm
        self.SolutionPool.AddSolution(solution)

        """