import json
import csv
import math
import os


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

    def __init__(self, main_tasks_path: str, optional_tasks_path: str = "../Data/OptionalTasks.csv") -> None:
        '''
        Initialize the InputData object with paths to the optional tasks and main tasks files.

        :param optional_tasks_path: Path to the CSV file containing optional tasks
        :param main_tasks_path: Path to the JSON file containing main tasks
        '''

        print(os.getcwd())
        self.__optional_tasks_path = optional_tasks_path
        self.__main_tasks_path = main_tasks_path 

        # Load and create task objects from file paths
        self.__Load_OptionalTasks()
        self.__Load_MainTasks()

        # Create List with all Tasks
        self.__allTasks = self.__mainTasks + self.__optionalTasks

        # Create list with distances
        self.__distances = self.__CreateDistances()


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
        self.__instance_ID = data["ID"]
        self.__cohort_no = int(data["Cohorts"])
        self.__days = int(data["Days"])
        self.__maxRouteDuration = int(data["MaxRouteDuration"])

        # Create MainTask objects for each task in the JSON data
        for task in data["MainTasks"]:
            self.__mainTasks.append(MainTask(task))

    def __CalculateDistance(self, task_1, task_2) -> float:
        ''' Calculate the distance between two tasks using the euclidean distance formula
            and return the time it takes to travel between them in seconds
        '''

        distance = math.sqrt((task_1.latitude - task_2.latitude)**2 + (task_1.longitude - task_2.longitude)**2)

        time = int(round(distance * 17100)) # time in seconds

        return time

    def __CreateDistances(self) -> list[list[int]]:
        ''' Create a two-dimensional list with distances between all tasks '''

        # Calculate the distances between all tasks
        distances = [[0 for i in range(len(self.__allTasks))] for j in range(len(self.__allTasks))]

        for task_i_id in range(len(self.__allTasks)):
            for task_j_id in range(task_i_id): 
                # Calculate the distance between the two tasks
                    distances[task_i_id][task_j_id] = distances[task_j_id][task_i_id] = self.__CalculateDistance(self.__allTasks[task_i_id], self.__allTasks[task_j_id])

        return distances

    @property
    def allTasks(self) -> list:
        ''' Property to get the list of all available tasks '''
        return self.__allTasks

    @property
    def optionalTasks(self)-> list[OptionalTask]:
        ''' Property to get the list of optional tasks '''
        return self.__optionalTasks

    @property
    def mainTasks(self) -> list[MainTask]:
        ''' Property to get the list of main tasks '''
        return self.__mainTasks
    
    @property
    def distances(self) -> list[list[int]]:
        ''' Get Two dimensional list with distances between all tasks'''
        return self.__distances
    
    @property
    def optional_tasks_path(self) -> str:
        ''' Property to get the path to the optional tasks file '''
        return self.__optional_tasks_path
    
    @property
    def main_tasks_path(self) -> str:  
        ''' Property to get the path to the main tasks file '''
        return self.__main_tasks_path

    @property
    def instance_ID(self) -> str:
        ''' Property to get the ID of instance of main tasks'''
        return self.__instance_ID

    @property
    def cohort_no(self) ->  int:
        ''' Property to get the number of cohorts '''
        return self.__cohort_no

    @property
    def days(self) -> int:
        ''' Property to get the number of days '''
        return self.__days

    @property
    def maxRouteDuration(self) -> int:
        ''' Property to get the maximum route duration '''
        return self.__maxRouteDuration
