import json
import csv


class MainTask:
    ''' Class for the attributes of a main task '''


    def __init__(self, json_data):
        # Convert and assign each attribute with explicit data type conversion and make them private
        self.__ID = str(json_data.get('ID', ''))
        self.__day = int(json_data.get('Day', 0))
        self.__service_time = int(json_data.get('ServiceTime', 0))
        self.__start_time = int(json_data.get('StartTime', 0))
        self.__end_time = int(json_data.get('EndTime', 0))
        self.__location_id = int(json_data.get('LocationID', 0))
        self.__latitude = float(json_data.get('Latitude', 0.0))
        self.__longitude = float(json_data.get('Longitude', 0.0))

    def __str__(self):
        ''' This method makes it easier to print the object's attributes as a string '''
        return (f"ID: {self.ID}, Day: {self.day}, Service Time: {self.service_time}, "
               f"Start Time: {self.start_time}, End Time: {self.end_time}, "
               f"Location ID: {self.location_id}, Latitude: {self.latitude}, Longitude: {self.longitude}")

    @property
    def ID(self) -> str:
        ''' Return Task ID '''
        return self.__ID

    @property
    def day(self) -> int:
        ''' Return Day Number '''
        return self.__day

    @property
    def service_time(self) -> int:
        ''' Return Service Time '''
        return self.__service_time

    @property
    def start_time(self) -> int:
        ''' Return Start Time '''
        return self.__start_time

    @property
    def end_time(self) -> int:
        ''' Return End Time '''
        return self.__end_time

    @property
    def location_id(self) -> int:
        ''' Return Location ID '''
        return self.__location_id

    @property
    def latitude(self) -> float:
        ''' Return Latitude '''
        return self.__latitude

    @property
    def longitude(self) -> float:
        ''' Return Longitude '''
        return self.__longitude

    def __str__(self):
        # This method makes it easier to print the object's attributes as a string
        return (f"ID: {self.ID}, Day: {self.day}, Service Time: {self.service_time}, "
               f"Start Time: {self.start_time}, End Time: {self.end_time}, "
               f"Location ID: {self.location_id}, Latitude: {self.latitude}, Longitude: {self.longitude}")

class OptionalTask:
    ''' Class for the attributes of an optional task '''

    def __init__(self, json_data):
        # Initialize attributes from a CSV row with explicit data type conversion
        self.__ID = str(json_data.get('ID', ''))
        self.__street = str(json_data.get("Street",""))
        self.__number = str(json_data.get("Number",""))
        self.__address = str(json_data.get("Address",""))
        self.__location_id = int(json_data.get('LocationID', 0))
        self.__latitude = float(json_data.get('Latitude', 0.0))
        self.__longitude = float(json_data.get('Longitude', 0.0))
        self.__location_id = int(json_data.get('LocationID',0))
        self.__description = str(json_data.get('Description'))
        self.__category = str(json_data.get('Category'))
        self.__service_time = int(json_data.get('ServiceTime',0))
        self.__profit = int(json_data.get('Profit',0))

    @property
    def ID(self):
        ''' Return Task ID '''
        return self.__ID

    @property
    def street(self):
        ''' Return Street '''
        return self.__street

    @property
    def number(self):
        ''' Return Number '''
        return self.__number

    @property
    def address(self):
        ''' Return Address '''
        return self.__address

    @property
    def latitude(self):
        ''' Return Latitude '''
        return self.__latitude

    @property
    def longitude(self):
        ''' Return Longitude '''
        return self.__longitude

    @property
    def location_id(self):
        ''' Return Location ID '''
        return self.__location_id

    @property
    def description(self):
        ''' Return Description '''
        return self.__description

    @property
    def category(self):
        ''' Return Category '''
        return self.__category

    @property
    def service_time(self):
        ''' Return Service Time '''
        return self.__service_time

    @property
    def profit(self):
        ''' Return Profit '''
        return self.__profit

    def __str__(self):
        # This method provides a string representation of the object
        return (f"ID: {self.ID}, Street: {self.street}, Number: {self.number}, Address: {self.address}, "
                f"Latitude: {self.latitude}, Longitude: {self.longitude}, Location ID: {self.location_id}, "
                f"Description: {self.description}, Category: {self.category}, Service Time: {self.service_time}, "
                f"Profit: {self.profit}")


class InputData:
    '''Class for creating Data objects based on formatted Json Files containing the information of the regarding jobs and machines'''

    def __init__(self, main_tasks_path: str, optional_tasks_path: str = "Data/OptionalTasks.csv") -> None:
        '''
        Initialize the InputData object with paths to the optional tasks and main tasks files.

        :param optional_tasks_path: Path to the CSV file containing optional tasks
        :param main_tasks_path: Path to the JSON file containing main tasks
        '''
        self.__optional_tasks_path = optional_tasks_path
        self.__main_tasks_path = main_tasks_path 

        # Load and create task objects from file paths
        self.__Load_OptionalTasks()
        self.__Load_MainTasks()

    def __Load_OptionalTasks(self) -> None:
        ''' Initialize the creation of a list of optional tasks based on the CSV file path'''

        # Initialize the list to store optional tasks
        self.__optionalTasks = list()

        # Open the CSV file and read its contents
        with open(self.__optional_tasks_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Create OptionalTask objects for each row in the CSV file
            for row in reader: 
                self.__optionalTasks.append(OptionalTask(row))

    def __Load_MainTasks(self) -> None:
        ''' Initialize the creation of a list of main tasks based on the JSON file path'''

        # Initialize the list to store main tasks
        self.__mainTasks = list()

        # Opening JSON file
        json_file = open(self.__main_tasks_path)
        data = json.load(json_file)  # Load JSON data as a dictionary

        # Extract and store the attributes from the JSON data
        self.__main_ID = data["ID"]
        self.__cohort_no = int(data["Cohorts"])
        self.__days = int(data["Days"])
        self.__maxRouteDuration = int(data["MaxRouteDuration"])

        # Create MainTask objects for each task in the JSON data
        for task in data["MainTasks"]:
            self.__mainTasks.append(MainTask(task))

    @property
    def optionalTasks(self):
        ''' Property to get the list of optional tasks '''
        return self.__optionalTasks

    @property
    def mainTasks(self):
        ''' Property to get the list of main tasks '''
        return self.__mainTasks
    
    @property
    def optional_tasks_path(self):
        ''' Property to get the path to the optional tasks file '''
        return self.__optional_tasks_path
    
    @property
    def main_tasks_path(self):  
        ''' Property to get the path to the main tasks file '''
        return self.__main_tasks_path

    @property
    def main_ID(self):
        ''' Property to get the main ID '''
        return self.__main_ID

    @property
    def cohort_no(self):
        ''' Property to get the number of cohorts '''
        return self.__cohort_no

    @property
    def days(self):
        ''' Property to get the number of days '''
        return self.__days

    @property
    def maxRouteDuration(self):
        ''' Property to get the maximum route duration '''
        return self.__maxRouteDuration


def write_json_solution_mip(objVal:int, var_y, var_x, var_u, data:InputData, distances, filepath:str, number_tasks:int):

    number_all_tasks = 0
    days = {}
    for day in range(data.days):
        day_list = []

        for cohort in range(data.cohort_no):
            
            route_list = []
            profit_route = 0
            start_time = 0
            pre_selected_nodes = []
            u_nodes = []

            for i in range(1,len(data.optionalTasks[0:number_tasks])):
                #for j in range(1,len(data.optionalTasks[0:10])):
                    if var_y[day,cohort,i].X == 1:

                        number_all_tasks += 1
                        pre_selected_nodes.append(i)
                        u_nodes.append(var_u[day,cohort,i].X)

                        profit_route += data.optionalTasks[i].profit
                        #start_time += distances[i][j]

            if len(pre_selected_nodes) > 0:
                # Pair the lists together
                paired_lists = list(zip(u_nodes, pre_selected_nodes))

                # Sort the pairs based on the first list
                sorted_pairs = sorted(paired_lists, key=lambda x: x[0])

                # Separate the pairs back into two lists
                sorted_u_nodes, sorted_nodes = zip(*sorted_pairs)

                start_node = 0
                for i in sorted_nodes:
                    start_time += distances[start_node][i]            
                    route_list.append({"StartTime" : start_time,
                                            "SelectedDay" : day + 1,
                                            "ID" : data.optionalTasks[i].ID})
                    
                    start_node = i
                    start_time += data.optionalTasks[i].service_time
                
            cohort_dict = {"CohortID"   : cohort,
                           "Profit"     : profit_route,
                           "Route"    : route_list}
            
            
            day_list.append(cohort_dict)


        days[str(day + 1)] = day_list
        
                
    
    results = {
        "Instance": data.main_tasks_path.split("/")[-1].split(".")[0],
        "Objective": objVal,
        "NumberOfAllTasks": number_all_tasks,#len(res.vars.y),
        "UseMainTasks" : False,
        "Days" : days
    }

    # Write the dictionary to a JSON file
    with open(filepath, 'w') as json_file:
        json.dump(results, json_file, indent=2)

    print(f"JSON file has been created at {filepath}")

def write_txt_solution(gp_model, var_y, var_x, var_u, data:InputData, distances, file_path:str, number_tasks:int):
    """
    Writes optimization gap, runtime, number of constraints, and number of variables 
    from a solved Gurobi model into a text file.

    Parameters:
    model (gurobipy.Model): The Gurobi model to extract information from.
    y, x, u, data, d, define_range: Additional parameters (usage can be defined as needed).
    file_path (str): The path to the output text file.
    """
    
    # Retrieve optimization metrics
    gap = gp_model.MIPGap
    runtime = round(gp_model.Runtime,2)
    num_constraints = gp_model.NumConstrs
    num_variables = gp_model.NumVars
    obj = round(gp_model.getAttr("ObjVal"))
    
    # Write the metrics to the output file
    with open(file_path, 'w') as file:
        file.write(str(obj) + "\t" + str(gap) + "\t" + str(runtime) + "\t" + str(num_constraints) + "\t" + str(num_variables) + "\n")
        file.write(str(data.days) + " " + str(data.cohort_no) + " " + str(number_tasks) + "\n \n")

        for day in range(data.days):

            file.write(str(day)+"\n")

            for cohort in range(data.cohort_no):
                
                file.write("\t" +str(cohort) + " ")

                route_list = []
                profit_route = 0
                start_time = 0
                pre_selected_nodes = []
                u_nodes = []

                for i in range(1,len(data.optionalTasks[0:number_tasks])):
                    if var_y[day,cohort,i].X == 1:

                        pre_selected_nodes.append(i)
                        u_nodes.append(var_u[day,cohort,i].X)

                        profit_route += data.optionalTasks[i].profit

                file.write("("+str(profit_route) + "): ")

                if len(pre_selected_nodes) > 0:
                    # Pair the lists together
                    paired_lists = list(zip(u_nodes, pre_selected_nodes))

                    # Sort the pairs based on the first list
                    sorted_pairs = sorted(paired_lists, key=lambda x: x[0])

                    # Separate the pairs back into two lists
                    sorted_u_nodes, sorted_nodes = zip(*sorted_pairs)

                    sorted_nodes = list(sorted_nodes)

                    start_node = 0
                    sorted_nodes.append(start_node)
                    sorted_nodes.insert(start_node, start_node)
                    for i in sorted_nodes:
                        
                        file.write(str(i) +" ")

                file.write("\n")
                


    print(f"Text file has been created at {file_path}")