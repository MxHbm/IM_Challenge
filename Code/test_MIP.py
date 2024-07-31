from InputData import * 
from MIP_initial_routeplan import *

data = InputData("Instance7_2_2.json")

route_plan = find_inital_main_task_allocation(data)

print(route_plan)