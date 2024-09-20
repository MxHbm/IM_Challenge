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

        
    def Run(self, inputData: InputData, numberOfParameterComb=3, main_tasks=True) -> None:
        ''' Choose one of the constructive heuristics and get a first solution due to the chosen heuristic '''

        print('Generating an initial solution according to Greedy.')

        # Rewriting any present solution
        solution = None

        # Prepare a list of tasks (combinations of parameters) for sequential execution
        tasks = []

        if main_tasks:
            if numberOfParameterComb == 3:
                tasks = [
                    ('OnePerDay', 'WithDistanceToMainTask', 1.0, 0),
                    ('MIP', 'WithDistanceToMainAndCloseTasks', 0.5, 100),
                    ('OnePerDay', 'WithDistanceToMainAndCloseTasks', 2.0, 20),
                ]
            elif numberOfParameterComb == 2:
                tasks = [
                    ('OnePerDay', 'WithDistanceToMainTask', 1.0, 0),
                    ('OnePerDay', 'WithDistanceToMainAndCloseTasks', 1.0, 100),
                ]
            elif numberOfParameterComb == 1:
                solution = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainTask', 1.0, 0)
            elif numberOfParameterComb == 'Test':
                solution = self._Greedy(inputData, 'MIP', 'OnlyDistanceToNextTask', 1.0, 0)
        else:
            solution = self._Greedy(inputData, None, 'OnlyDistanceToNextTask', 1.0, 0)

        # If we have tasks to run, execute them sequentially
        if tasks:
            solutions = []
            for task in tasks:
                task_solution = self._Greedy(inputData, task[0], task[1], task[2], task[3])
                solutions.append(task_solution)

            # Select the solution with the maximum profit
            solution = max(solutions, key=lambda x: x.TotalProfit)

        # Add the first solution to the solution pool
        if solution:
            self._SolutionPool.AddSolution(solution)


    def _Greedy(self, inputData:InputData, mainTaskPlanner, attractivenessFunction, a, b) -> Solution:
        ''' Greedy heuristic to create a first feasible solution - fills blank spots between main tasks with optional tasks'''
        

        if attractivenessFunction == 'WithDistanceToMainAndCloseTasks' or attractivenessFunction == 'WithDistanceToCloseTasks':
            inputData._CreateScoreboard()


        ''' Assign main tasks to days and cohorts'''
        prefilled_route_plan = self._assign_main_tasks(inputData, mainTaskPlanner)

        depot = 0
        planned_tasks = set() # Save the tasks that are already planned --> List of planned task IDs
        unplanned_tasks = {task.no for task in inputData.optionalTasks[1:]} # without depot!
        distances = inputData.distances

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
                    mainT_list = [main_task for main_task in prefilled_route_plan[day][cohort]] # Main task(s) list for the respective cohort on the respective day
                    nextMainT = mainT_list.pop(0) # Already remove the next main task from the main taks list and save it
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

                    for unplanned_task in unplanned_tasks:
                        if unplanned_task not in planned_tasks:
                                    #TODO: Adapt Calculate Attractiveness function
                                    attractiveness[unplanned_task] = self._CalculateAttractiveness(inputData,attractivenessFunction,previousT,unplanned_task, nextMainT, main_task_visited, a, b)
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
                            potentialTime = distances[previousT][nextT] + inputData.allTasks[nextT].service_time + distances[nextT][nextMainT]
                            
                            
                            ''' 3 Cases: 
                                1. Next Task can be inserted before the main task accroding to the start time of the main task and the potential time
                                2. Check for the next attractive task(s) to be inserted before the main task
                                3. No tasks can be inserted before the main task: Main Task is visited'''
                            
                            if totalTime + potentialTime <= inputData.allTasks[nextMainT].start_time:
                                realTime = potentialTime - distances[nextT][nextMainT]
                                totalTime += realTime

                                #TODO Check if this function needs to be updated! 
                                self._UpdateScoreboard(nextT, inputData, attractivenessFunction)

                                #Overwrite Next to previous
                                previousT = nextT
                                #TODO Check this function
                                self._InsertTaskBeforeMainTask(prefilled_route_plan[day][cohort], nextT, nextMainT)
                                next_task_planned = True
                                planned_tasks.add(nextT)
                                unplanned_tasks.discard(nextT)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                next_task_planned = True
                                previousT = nextMainT
                                totalTime = inputData.allTasks[nextMainT].start_time + inputData.allTasks[nextMainT].service_time # Total time is now the end of the main task

                                if mainT_list != []:
                                    nextMainT = mainT_list.pop(0)
                                else:
                                    main_task_visited = True
                                    
         
                        elif main_task_visited == True:
                            
                            ''' Calculate the potential time to insert the task to the route plan before the end of the day'''
                            potentialTime = distances[previousT][nextT] + inputData.allTasks[nextT].service_time + distances[nextT][depot]

                            ''' 3 Cases: 
                                1. Next Task can be inserted to the route plan according to the end of the day and the potential time
                                2. Check for the next attractive task(s) to be inserted to the route plan
                                3. No tasks can be inserted to the route plan: Route is planned'''

                            if totalTime + potentialTime <= inputData.maxRouteDuration:
                                realTime = potentialTime - distances[nextT][depot]
                                totalTime += realTime

                                self._UpdateScoreboard(nextT, inputData, attractivenessFunction)

                                previousT = nextT
                                prefilled_route_plan[day][cohort].append(nextT)
                                next_task_planned = True
                                planned_tasks.add(nextT)
                                unplanned_tasks.discard(nextT)

                            elif len(attractiveness) > index + 1: # Only raise the index if there are more tasks to check
                                index += 1

                            else:
                                next_task_planned = True
                                route_planned = True

        tmpSolution = Solution(prefilled_route_plan, inputData)

        self.EvaluationLogic.evaluateSolution(tmpSolution)

        return tmpSolution
    
    
    def _assign_main_tasks(self, inputData, mainTaskPlanner):
        ''' Helper function to assign main tasks based on the planner '''
        if mainTaskPlanner:
            print(f'Assigning main tasks to days and cohorts according to {mainTaskPlanner}.')
            if mainTaskPlanner == 'MIP':
                return self._create_initial_route_plan_with_MIP(inputData)
            elif mainTaskPlanner == 'OnePerDay':
                return self._create_initial_route_plan(inputData)
        # Default to empty plan if no main task planner
        return {day: [[] for _ in range(inputData.cohort_no)] for day in range(inputData.days)}


    def _UpdateScoreboard(self, task ,inputData:InputData, attractivenessFunction):
        
        if attractivenessFunction == 'WithDistanceToMainAndCloseTasks':
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
        


    def _CalculateAttractiveness(self,inputData:InputData, attractivenessFunction ,previousTask, nextTask, mainTask, mainTaskVisited,  a , b ):
        ''' Calculate the attractiveness of a nextTask based on profit, service time and distance to the previous task'''

        distance = inputData.distances[previousTask][nextTask]
        nextTaskProfitWeighted = inputData.allTasks[nextTask].profit ** a
        nextTaskServiceTime = inputData.allTasks[nextTask].service_time
        

        if attractivenessFunction == 'OnlyDistanceToNextTask':
            attractiveness = (nextTaskProfitWeighted)/(nextTaskServiceTime + distance)

        
        elif attractivenessFunction == 'WithDistanceToCloseTasks':
            closeProfitScore = len(inputData.scoreboard[nextTask])/b
            attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTaskServiceTime + distance)


        elif attractivenessFunction == 'WithDistanceToMainTask':

            if mainTaskVisited == False:
                distanceToMainTask = inputData.distances[nextTask][mainTask]
                attractiveness = (nextTaskProfitWeighted)/(nextTaskServiceTime + distance + distanceToMainTask)
            else:
                attractiveness = (nextTaskProfitWeighted)/(nextTaskServiceTime + distance)

        elif attractivenessFunction == 'WithDistanceToMainAndCloseTasks':
            
            closeProfitScore = len(inputData.scoreboard[nextTask])/b


            if mainTaskVisited == False:
                distanceToMainTask = inputData.distances[nextTask][mainTask]
                attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTaskServiceTime + distance + distanceToMainTask)
            else:
                attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTaskServiceTime + distance)
            
        else:
            raise Exception('Unknown attractiveness function: ' + attractivenessFunction + '.')
        

        return attractiveness
    
