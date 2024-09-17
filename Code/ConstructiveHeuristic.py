from itertools import permutations
import time
import numpy
from OutputData import *
from MIP_initial_routeplan import * # MIP for initial route plan in in the same folder
from EvaluationLogic import *
from concurrent.futures import ThreadPoolExecutor

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

    
    def Run(self, inputData:InputData, numberOfParameterComb = 3, main_tasks = True) -> None:
        ''' Choose one of the constructive heuristics and get a first solutiuon due to the chosen heuristic'''

        print('Generating an initial solution according to Greedy.')

        #Rewrite any present solution
        solution = None
            
        if main_tasks == True:
            if numberOfParameterComb == 3:
                solution1 = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainTask', 1.0, 0)
                solution2 = self._Greedy(inputData, 'MIP', 'WithDistanceToMainAndCloseTasks', 0.5, 100)
                solution3 = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainAndCloseTasks', 2.0, 20)
                solution = max([solution1, solution2, solution3], key=lambda x: x.TotalProfit)
            elif numberOfParameterComb == 2:
                solution1 = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainTask', 1.0, 0)
                solution2 = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainAndCloseTasks', 1.0, 100)
                solution = max([solution1, solution2], key=lambda x: x.TotalProfit)  
            elif numberOfParameterComb == 1:
                solution = self._Greedy(inputData, 'OnePerDay', 'WithDistanceToMainTask', 1.0, 0)
            elif numberOfParameterComb == 'Test':
                solution = self._Greedy(inputData, 'MIP', 'OnlyDistanceToNextTask', 1.0, 0) ### TEST

        else:
            solution = self._Greedy(inputData, None, 'OnlyDistanceToNextTask', 1.0, 0)
            #solution = self._Greedy(inputData, None, 'WithDistanceToCloseTasks', 1.0, 100) ### Different Possibility
   

        #Add the first solution to the solution pool to proceed further with the algorithm
        self._SolutionPool.AddSolution(solution)

    def _Greedy(self, inputData:InputData, mainTaskPlanner, attractivenessFunction, a, b) -> Solution:
        ''' Greedy heuristic to create a first feasible solution - fills blank spots between main tasks with optional tasks'''
        

        if attractivenessFunction == 'WithDistanceToMainAndCloseTasks' or attractivenessFunction == 'WithDistanceToCloseTasks':
            inputData._CreateScoreboard()


        ''' Assign main tasks to days and cohorts'''
        if mainTaskPlanner is not None:
            print('Assigning main tasks to days and cohorts according to ' + mainTaskPlanner + '.')
        if mainTaskPlanner == 'MIP':
            prefilled_route_plan = self._create_initial_route_plan_with_MIP(inputData)
        elif mainTaskPlanner == 'OnePerDay':
            prefilled_route_plan = self._create_initial_route_plan(inputData)
        elif mainTaskPlanner == None:
                prefilled_route_plan = {}
                for day in range(inputData.days):
                    day_list = []
                    for cohort in range(inputData.cohort_no):
                        day_list.append([])
                    prefilled_route_plan[day] = day_list     
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

                    for t in range(len(inputData.optionalTasks)):
                        if inputData.allTasks[t] != previousT and inputData.allTasks[t] != depot and inputData.allTasks[t].ID not in planned_tasks:
                                    attractiveness[t] = self._CalculateAttractiveness(inputData,attractivenessFunction,previousT,inputData.allTasks[t], inputData.allTasks[nextMainT] ,main_task_visited, a, b)
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
                            previosTIndex = previousT.no
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
                                    nextMainT = mainT_list.pop(0)
                                else:
                                    main_task_visited = True
                                    
         
                        elif main_task_visited == True:
                            
                            ''' Calculate the potential time to insert the task to the route plan before the end of the day'''
                            previosTIndex = previousT.no
                            depotIndex = depot.no
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

        distance = inputData.distances[previousTask.no][nextTask.no]
        nextTaskProfitWeighted = nextTask.profit ** a

        if attractivenessFunction == 'OnlyDistanceToNextTask':
            attractiveness = (nextTaskProfitWeighted)/(nextTask.service_time + distance)

        
        elif attractivenessFunction == 'WithDistanceToCloseTasks':
            nextTaskIndex = inputData.optionalTasks.index(nextTask)
            closeProfitScore = len(inputData.scoreboard[nextTaskIndex])/b
            attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTask.service_time + distance)


        elif attractivenessFunction == 'WithDistanceToMainTask':

            if mainTaskVisited == False:
                distanceToMainTask = inputData.distances[nextTask.no][mainTask.no]
                attractiveness = (nextTaskProfitWeighted)/(nextTask.service_time + distance + distanceToMainTask)
            else:
                attractiveness = (nextTaskProfitWeighted)/(nextTask.service_time + distance)

        elif attractivenessFunction == 'WithDistanceToMainAndCloseTasks':
            

            nextTaskIndex = inputData.optionalTasks.index(nextTask)
            closeProfitScore = len(inputData.scoreboard[nextTaskIndex])/b


            if mainTaskVisited == False:
                distanceToMainTask = inputData.distances[nextTask.no][mainTask.no]
                attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTask.service_time + distance + distanceToMainTask)
            else:
                attractiveness = (nextTaskProfitWeighted + closeProfitScore)/(nextTask.service_time + distance)
            
        else:
            raise Exception('Unknown attractiveness function: ' + attractivenessFunction + '.')
        

        return attractiveness
    

    """

      def _Greedy(self, inputData: InputData, mainTaskPlanner, attractivenessFunction, a, b) -> Solution:
        ''' Greedy heuristic to create a first feasible solution - fills blank spots between main tasks with optional tasks'''

        # Initialize scoreboard if applicable
        if attractivenessFunction in ['WithDistanceToMainAndCloseTasks', 'WithDistanceToCloseTasks']:
            inputData._CreateScoreboard()

        # Assign main tasks to days and cohorts based on the planner
        prefilled_route_plan = self._assign_main_tasks(inputData, mainTaskPlanner)
        depot = inputData.allTasks[0].no
        planned_tasks = set()  # Using a set for faster lookups
        unplanned_tasks = set(task for task in inputData.optionalTasks.no)

        # Flag to stop the loop if all tasks are planned
        breakFlag = False 

        for day in range(inputData.days):
            if breakFlag:
                break

            for cohort in range(inputData.cohort_no):
                if breakFlag:
                    break

                route_planned = False
                previousT = depot  # Start with depot at the beginning of each route
                
                # Get the main tasks for this day and cohort, or set a default
                nextMainT, main_task_visited = self._initialize_main_task(prefilled_route_plan, day, cohort)

                totalTime = 0  # Start of the day

                while not route_planned:
                    if breakFlag:
                        break

                    # Calculate attractiveness of potential next tasks based on the previous task
                    attractiveness = self._calculate_attractiveness_for_tasks(inputData, attractivenessFunction, previousT, nextMainT, main_task_visited,unplanned_tasks, a, b)

                    # Try to plan the next task
                    next_task_planned, totalTime, previousT = self._plan_next_task(inputData, day, cohort, previousT, nextMainT, main_task_visited, planned_tasks, totalTime, depot, prefilled_route_plan, attractiveness)

                    if next_task_planned is None:
                        # If no task could be planned and all tasks are finished
                        route_planned = True
                        if len(planned_tasks) == len(inputData.optionalTasks) - 1:
                            print('All optional tasks are planned.')
                            breakFlag = True
                            break

            # Create the solution
        tmpSolution = Solution(prefilled_route_plan, inputData)
        self.EvaluationLogic.evaluateSolution(tmpSolution)

        print('Initial Solution found.')
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
    
    def _initialize_main_task(self, prefilled_route_plan, day, cohort):
        ''' Initialize the main task list for a given day and cohort '''
        if prefilled_route_plan[day][cohort]:
            mainT_list = list(prefilled_route_plan[day][cohort])
            return mainT_list.pop(0), False
        return 0, True  # No main task
    
    def _calculate_attractiveness_for_tasks(self, inputData, attractivenessFunction, previousT, nextMainT, main_task_visited,unplanned_tasks, a, b):
        ''' Calculate attractiveness for each optional task '''
        attractiveness = {}
        depot = inputData.allTasks[0].no
        for task_no in unplanned_tasks:
            if task_no != previousT and task_no != depot:
                attractiveness[task_no] = self._CalculateAttractiveness(inputData, attractivenessFunction, previousT, task_no, nextMainT, main_task_visited, a, b)
        return dict(sorted(attractiveness.items(), key=lambda item: item[1], reverse=True))  # Sort tasks by attractiveness

    def _plan_next_task(self, inputData, day, cohort, previousT, nextMainT, main_task_visited, planned_tasks, totalTime, depot, prefilled_route_plan, attractiveness):
        ''' Plan the next task based on attractiveness '''
        index = 0
        next_task_planned = False
        while not next_task_planned:
            if index >= len(attractiveness):
                return None, totalTime, previousT

            nextT = list(attractiveness.keys())[index]
            nextT_task = inputData.allTasks[nextT]

            # Insert task based on whether the main task is visited or not
            if not main_task_visited:
                next_task_planned, totalTime, previousT = self._insert_before_main(inputData, day, cohort, nextT, nextT_task, nextMainT, previousT, planned_tasks, prefilled_route_plan, totalTime,attractiveness)
            else:
                next_task_planned, totalTime, previousT = self._insert_after_main(inputData, day, cohort, nextT, nextT_task, previousT, depot, planned_tasks, prefilled_route_plan, totalTime, attractiveness)

            index += 1
        return next_task_planned, totalTime, previousT
    
    def _insert_before_main(self, inputData, day, cohort, nextT, nextT_task, nextMainT, previousT, planned_tasks, prefilled_route_plan, totalTime, attractivenessFunction):
        ''' Try to insert a task before the main task '''
        previosTIndex = inputData.allTasks.index(previousT)
        potentialTime = inputData.distances[previosTIndex][nextT] + nextT_task.service_time + inputData.distances[nextT][nextMainT]
        
        if totalTime + potentialTime <= inputData.allTasks[nextMainT].start_time:
            realTime = potentialTime - inputData.distances[nextT][nextMainT]
            totalTime += realTime

            self._UpdateScoreboard(nextT, inputData, attractivenessFunction)
            previousT = nextT_task
            self._InsertTaskBeforeMainTask(prefilled_route_plan[day][cohort], nextT, nextMainT)
            planned_tasks.add(nextT_task.ID)

            return True, totalTime, previousT
        return False, totalTime, previousT
    
    def _insert_after_main(self, inputData, day, cohort, nextT, nextT_task, previousT, depot, planned_tasks, prefilled_route_plan, totalTime, attractivenessFunction):
        ''' Try to insert a task after the main task '''
        previosTIndex = inputData.allTasks.index(previousT)
        depotIndex = inputData.allTasks.index(depot)
        potentialTime = inputData.distances[previosTIndex][nextT] + nextT_task.service_time + inputData.distances[nextT][depotIndex]

        if totalTime + potentialTime <= inputData.maxRouteDuration:
            realTime = potentialTime - inputData.distances[nextT][depotIndex]
            totalTime += realTime

            self._UpdateScoreboard(nextT, inputData, attractivenessFunction)
            previousT = nextT_task
            prefilled_route_plan[day][cohort].append(nextT)
            planned_tasks.add(nextT_task.ID)

            return True, totalTime, previousT
        return False, totalTime, previousT
    
    def _UpdateScoreboard(self, task, inputData: InputData, attractivenessFunction):
        if attractivenessFunction == 'WithDistanceToMainAndCloseTasks':
            for key, values in inputData.scoreboard.items():
                if task in values:
                    values.remove(task)

    def _InsertTaskBeforeMainTask(self, current_route_plan, task_to_insert, main_task):
        ''' Insert a task before the main task in the current route plan '''
        if main_task in current_route_plan:
            index = current_route_plan.index(main_task)
            current_route_plan.insert(index, task_to_insert)
        else:
            print('Main task not in route plan')

    
    def _CalculateAttractiveness(self, inputData: InputData, attractivenessFunction, previousTask, nextTask, mainTask, mainTaskVisited, a, b):
        ''' Calculate the attractiveness of a nextTask based on profit, service time, and distance to the previous task '''
        
        # Calculate distance between previous task and next task
        distance = inputData.distances[previousTask][nextTask]

        # Different attractiveness functions based on user input
        if attractivenessFunction == 'OnlyDistanceToNextTask':
            # Attractiveness based only on distance and service time
            attractiveness = (nextTask.profit ** a) / (nextTask.service_time + distance)

        elif attractivenessFunction == 'WithDistanceToCloseTasks':
            # Include score based on how many close tasks are left
            nextTaskIndex = inputData.optionalTasks.index(nextTask)
            closeProfitScore = len(inputData.scoreboard[nextTaskIndex]) / b
            attractiveness = (nextTask.profit ** a + closeProfitScore) / (nextTask.service_time + distance)

        elif attractivenessFunction == 'WithDistanceToMainTask':
            # Include distance to the main task if it hasn't been visited yet
            if not mainTaskVisited:
                distanceToMainTask = inputData.distances[nextTask.no][mainTask.no]
                attractiveness = (nextTask.profit ** a) / (nextTask.service_time + distance + distanceToMainTask)
            else:
                attractiveness = (nextTask.profit ** a) / (nextTask.service_time + distance)

        elif attractivenessFunction == 'WithDistanceToMainAndCloseTasks':
            # Combination of close tasks and main task distance if not visited
            nextTaskIndex = inputData.optionalTasks.index(nextTask)
            closeProfitScore = len(inputData.scoreboard[nextTaskIndex]) / b

            if not mainTaskVisited:
                distanceToMainTask = inputData.distances[nextTask.no][mainTask.no]
                attractiveness = (nextTask.profit ** a + closeProfitScore) / (nextTask.service_time + distance + distanceToMainTask)
            else:
                attractiveness = (nextTask.profit ** a + closeProfitScore) / (nextTask.service_time + distance)

        else:
            # Raise an error if the attractiveness function is unknown
            raise Exception(f'Unknown attractiveness function: {attractivenessFunction}')

        return attractiveness







"""