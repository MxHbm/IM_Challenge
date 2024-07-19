from itertools import permutations
import time
import numpy
from OutputData import *
from MIP_initial_routeplan import * # MIP for initial route plan in in the same folder
from EvaluationLogic import *

class ConstructiveHeuristics:
    ''' Class for creating objects to run different constructive heuristics'''

    def __init__(self,  solutionPool:SolutionPool, evaluationLogic:EvaluationLogic):

        self.EvaluationLogic = evaluationLogic
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
                    routeplan[day].append([t])

        #Return the prefilled route plan
        return routeplan
    
    def _create_initial_route_plan_with_MIP(self, inputData:InputData) -> dict[str, list[list[int]]]:
        ''' Prefilles every day with one repsective main task for each cohort'''
    
        routeplan = find_inital_main_task_allocation(inputData)

        #Return the prefilled route plan
        return routeplan

    def Run(self, inputData:InputData, solutionMethod = 'Greedy', mainTaskPlanner = 'OnePerDay', attractivenessFunction = 'WithDistanceToMainTask') -> None:
        ''' Choose one of the constructive heuristics and get a first solutiuon due to the chosen heuristic'''

        print('Generating an initial solution according to ' + solutionMethod + '.')

        #Rewrite any present solution
        solution = None

        # Decision tree for choosing constructive heuristic 
        if solutionMethod == 'Greedy':
            solution = self._Greedy(inputData, mainTaskPlanner, attractivenessFunction)
        else:
            raise Exception('Unkown constructive solution method: ' + solutionMethod + '.')

        #Add the first solution to the solution pool to proceed further with the algorithm
        self._SolutionPool.AddSolution(solution)





    def _Greedy(self, inputData:InputData, mainTaskPlanner, attractivenessFunction) -> Solution:
        ''' Greedy heuristic to create a first feasible solution - fills blank spots between main tasks with optional tasks'''
        

        if attractivenessFunction == 'WithDistanceToMainTaskAndCloseTasks':
            inputData._CreateScoreboard()


        ''' Assign main tasks to days and cohorts'''
        print('Assigning main tasks to days and cohorts according to ' + mainTaskPlanner + '.')
        if mainTaskPlanner == 'MIP':
            prefilled_route_plan = self._create_initial_route_plan_with_MIP(inputData)
        elif mainTaskPlanner == 'OnePerDay':
            prefilled_route_plan = self._create_initial_route_plan(inputData)
        else:
            raise Exception('Unknown main task planner: ' + mainTaskPlanner + '.')

        depot = inputData.allTasks[0]
        planned_tasks = [] # Save the tasks that are already planned --> List of planned task IDs

        breakFlag = False # Flag to break the loop if all tasks are planned

        for day in range(inputData.days):

            if breakFlag:
                break
                
            for cohort in range(inputData.cohort_no):

                if breakFlag:
                    break
                
                route_planned = False
                previousT = depot # Depot is the starting point for each day and cohort
                
                ''' Check if there are main tasks for the respective cohort on the respective day and create a list of main tasks'''
                if len(prefilled_route_plan[day][cohort]) > 0: # If there are main tasks for the respective cohort on the respective day
                    mainT_list = deepcopy(prefilled_route_plan[day][cohort]) # Main task(s) list for the respective cohort on the respective day
                    nextMainT = mainT_list[0] # Save the next main task to visit
                    mainT_list.pop(0) # Already remove the next main task from the main taks list
                    main_task_visited = False
                else:
                    nextMainT = 0 # Just set to zero if there are no main tasks for the respective cohort on the respective day
                    main_task_visited = True # If there are no main tasks this boolean is set to True

                totalTime = 0 # Start of the day


                while route_planned == False: # While the route of one cohort for one day is not fully planned yet

                    if breakFlag:
                        break
                    
                    ''' Calculate attractiveness of potential next tasks based on previous taks'''
                    attractiveness = dict() # Save the attractiveness in a dictionary and reset attractiveness after each task is planned
                    for t in range(0,len(inputData.optionalTasks)):
                        if inputData.allTasks[t] != previousT and inputData.allTasks[t] != depot and inputData.allTasks[t].ID not in planned_tasks:
                                    attractiveness[t] = self._CalculateAttractiveness(inputData,attractivenessFunction,previousT,inputData.allTasks[t], inputData.allTasks[nextMainT] ,main_task_visited)
                    attractiveness = dict(sorted(attractiveness.items(), key=lambda item: item[1], reverse=True)) # Sort the tasks by attractiveness

                    next_task_planned = False
                    index = 0 # First index for the attractiveness dictionary
                    
                    while next_task_planned == False: # While the next task in the sequence is not planned

                        if len(planned_tasks) == len(inputData.optionalTasks) - 1: # If all tasks are planned
                            print('All optional tasks are planned.')
                            breakFlag = True
                            break

                        nextT = list(attractiveness.keys())[index] # Try to insert the task with the highest attractiveness

                        ''' Check if the task can be added to the route plan, depending on the time slot for the Main Task or the end of the day'''
                        if main_task_visited == False:
                            
                            ''' Calculate the potential time to insert the task before the main task'''
                            previosTIndex = inputData.allTasks.index(previousT)
                            potentialTime = inputData.distances[previosTIndex][nextT] + inputData.allTasks[nextT].service_time + inputData.distances[nextT][nextMainT]
                            
                            
                            ''' 3 Cases: 
                                1. Next Task can be inserted before the main task accroding to the start time of the main task and the potential time
                                2. Check for the next attractive task(s) to be inserted before the main task
                                3. No tasks can be inserted before the main task: Main Task is visited'''
                            
                            if totalTime + potentialTime <= inputData.allTasks[nextMainT].start_time:
                                realTime = potentialTime - inputData.distances[nextT][nextMainT]
                                totalTime += realTime

                                self._UpdateScoreboard(nextT, inputData, attractivenessFunction)

                                previousT = inputData.allTasks[nextT]
                                self._InsertTaskBeforeMainTask(prefilled_route_plan[day][cohort], nextT, nextMainT)
                                next_task_planned = True
                                planned_tasks.append(inputData.allTasks[nextT].ID)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                next_task_planned = True
                                previousT = inputData.allTasks[nextMainT]
                                totalTime = inputData.allTasks[nextMainT].start_time + inputData.allTasks[nextMainT].service_time # Total time is now the end of the main task

                                if mainT_list != []:
                                    nextMainT = mainT_list[0]
                                    mainT_list.pop(0)
                                else:
                                    main_task_visited = True
                                    
         
                        elif main_task_visited == True:
                            
                            ''' Calculate the potential time to insert the task to the route plan before the end of the day'''
                            previosTIndex = inputData.allTasks.index(previousT)
                            depotIndex = inputData.allTasks.index(depot)
                            potentialTime = inputData.distances[previosTIndex][nextT] + inputData.allTasks[nextT].service_time + inputData.distances[nextT][depotIndex]

                            ''' 3 Cases: 
                                1. Next Task can be inserted to the route plan according to the end of the day and the potential time
                                2. Check for the next attractive task(s) to be inserted to the route plan
                                3. No tasks can be inserted to the route plan: Route is planned'''

                            if totalTime + potentialTime <= inputData.maxRouteDuration:
                                realTime = potentialTime - inputData.distances[nextT][depotIndex]
                                totalTime += realTime

                                self._UpdateScoreboard(nextT, inputData, attractivenessFunction)

                                previousT = inputData.allTasks[nextT]
                                prefilled_route_plan[day][cohort].append(nextT)
                                next_task_planned = True
                                planned_tasks.append(inputData.allTasks[nextT].ID)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                next_task_planned = True
                                route_planned = True

  
        tmpSolution = Solution(prefilled_route_plan, inputData)

        self.EvaluationLogic.evaluateSolution(tmpSolution)

        print('Initial Solution found.')

        return tmpSolution


    def _UpdateScoreboard(self, task ,inputData:InputData, attractivenessFunction):
        
        if attractivenessFunction == 'WithDistanceToMainTaskAndCloseTasks':
            for key, values in inputData.scoreboard.items():
                if task in values:
                    values.remove(task)
        else:
            pass




    def _InsertTaskBeforeMainTask(self, current_route_plan , task_to_insert, main_task):
        ''' Insert a task before the main task in the current route plan'''
        if main_task in current_route_plan:
            index = current_route_plan.index(main_task)
            current_route_plan.insert(index, task_to_insert)
        else:
            print('Main task not in route plan')
        




    def _CalculateAttractiveness(self,inputData:InputData, attractivenessFunction ,previousTask, nextTask, mainTask, mainTaskVisited, numberOfCloseHighProfit = None):
        ''' Calculate the attractiveness of a nextTask based on profit, service time and distance to the previous task'''
    
        distance = inputData._CalculateDistance(previousTask, nextTask)

        if attractivenessFunction == 'OnlyDistanceToNextTask':
            attractiveness = nextTask.profit/((nextTask.service_time + distance)/3600)


        elif attractivenessFunction == 'WithDistanceToMainTask':

            if mainTaskVisited == False:
                distanceToMainTask = inputData._CalculateDistance(nextTask, mainTask)
                attractiveness = ((nextTask.profit)/((nextTask.service_time + distance + distanceToMainTask)/3600))
            else:
                attractiveness = ((nextTask.profit)/((nextTask.service_time + distance)/3600))

        elif attractivenessFunction == 'WithDistanceToMainTaskAndCloseTasks':
            

            nextTaskIndex = inputData.optionalTasks.index(nextTask)
            numberOfCloseHighProfit = len(inputData.scoreboard[nextTaskIndex])


            if mainTaskVisited == False:
                distanceToMainTask = inputData._CalculateDistance(nextTask, mainTask)
                attractiveness = ((nextTask.profit + numberOfCloseHighProfit/10)/((nextTask.service_time + distance + distanceToMainTask)/3600))
            else:
                attractiveness = ((nextTask.profit + numberOfCloseHighProfit/10)/((nextTask.service_time + distance)/3600))
            
        else:
            raise Exception('Unknown attractiveness function: ' + attractivenessFunction + '.')
        


        return attractiveness




    """ 
    def _GreedyOldVersion(self, inputData:InputData, attractivenessFunction) -> Solution:
        ''' Greedy heuristic to create a first feasible solution - fills blank spots between main tasks with optional tasks'''

        prefilled_route_plan = self._create_initial_route_plan(inputData)

        depot = inputData.allTasks[0]
        planned_tasks = [] # Save the tasks that are already planned


        for day in range(inputData.days):

            for cohort in range(inputData.cohort_no):

                
                route_planned = False
                previousT = depot # Depot is the starting point for each day and cohort      
                mainT_list = prefilled_route_plan[day][cohort] # Main task(s) for the respective cohort on the respective day
                mainT = mainT_list[0] # Currently only one main task per cohort per day
                main_task_visited = False
                totalTime = 0 # Start of the day


                while route_planned == False: # While the route of one cohort for one day is not planned

                    ''' Calculate attractiveness of potential next tasks based on previous taks'''
                    attractiveness = dict() # Save the attractiveness in a dictionary and reset attractiveness after each task is planned
                    for t in range(0,len(inputData.optionalTasks)):
                        if inputData.allTasks[t] != previousT:
                            if inputData.allTasks[t] != depot:
                                if inputData.allTasks[t].ID not in planned_tasks:
                                    attractiveness[t] = self._CalculateAttractiveness(inputData,attractivenessFunction,previousT,inputData.allTasks[t], inputData.allTasks[mainT] ,main_task_visited)
                    attractiveness = dict(sorted(attractiveness.items(), key=lambda item: item[1], reverse=True)) # Sort the tasks by attractiveness


                    next_task_planned = False
                    index = 0 # Start with the best possible attractiveness
                    while next_task_planned == False: # While the next task in the sequence is not planned
                        
                        ''' Choose the task with the highest attractiveness as next task to visit'''                
                        nextT = list(attractiveness.keys())[index]

                        #print('Next Task: ', inputData.allTasks[nextT].ID, ' Attractiveness: ', attractiveness[nextT])

                        ''' Check if the task can be added to the route plan, depending on the time slot for the Main Task or the end of the day'''
                        

                        if main_task_visited == False:
                            potentialTime = inputData._CalculateDistance(previousT, inputData.allTasks[nextT]) + inputData.allTasks[nextT].service_time + inputData._CalculateDistance(inputData.allTasks[nextT], inputData.allTasks[mainT])
                            if totalTime + potentialTime <= inputData.allTasks[mainT].start_time: # Calculate distance+service time in matrix in InputData
                                totalTime += potentialTime
                                previousT = inputData.allTasks[nextT]
                                ''' Add Taks to route plan before Main Task'''
                                self._InsertTaskBeforeMainTask(prefilled_route_plan[day][cohort], nextT, mainT)
                                next_task_planned = True
                                planned_tasks.append(inputData.allTasks[nextT].ID)
                                #print(prefilled_route_plan)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                main_task_visited = True
                                next_task_planned = True
                                previousT = inputData.allTasks[mainT]
                                totalTime = inputData.allTasks[mainT].start_time + inputData.allTasks[mainT].service_time # Total time is now the end of the main task



                        elif main_task_visited == True:
                            potentialTime = inputData._CalculateDistance(previousT, inputData.allTasks[nextT]) + inputData.allTasks[nextT].service_time + inputData._CalculateDistance(inputData.allTasks[nextT], depot)
                            if totalTime + potentialTime <= inputData.maxRouteDuration:
                                totalTime += potentialTime
                                previousT = inputData.allTasks[nextT]
                                ''' Add Taks to route plan after Main Task'''
                                prefilled_route_plan[day][cohort].append(nextT)
                                next_task_planned = True
                                planned_tasks.append(inputData.allTasks[nextT].ID)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                next_task_planned = True
                                route_planned = True

                    #print(prefilled_route_plan)
        #print(prefilled_route_plan)
                    
                        
        
        tmpSolution = Solution(prefilled_route_plan, inputData)

        self.EvaluationLogic.evaluateSolution(tmpSolution)

        print('Initial Solution found.')

        return tmpSolution

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