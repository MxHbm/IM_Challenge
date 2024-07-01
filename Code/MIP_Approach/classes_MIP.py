import json
import csv
from typing import List, Dict

class MainTask:
    ''' Class for the attributes of a main task '''

    def __init__(self, json_data):
        # Convert and assign each attribute with explicit data type conversion and make them private
        self._ID = str(json_data.get('ID', ''))
        self._day = int(json_data.get('Day', 0))
        self._service_time = int(json_data.get('ServiceTime', 0))
        self._start_time = int(json_data.get('StartTime', 0))
        self._end_time = int(json_data.get('EndTime', 0))
        self._location_id = int(json_data.get('LocationID', 0))
        self._latitude = float(json_data.get('Latitude', 0.0))
        self._longitude = float(json_data.get('Longitude', 0.0))
        self._profit = 0

    def __str__(self):
        ''' This method makes it easier to print the object's attributes as a string '''
        return (f"ID: {self.ID}, Day: {self.day}, Service Time: {self.service_time}, "
               f"Start Time: {self.start_time}, End Time: {self.end_time}, "
               f"Location ID: {self.location_id}, Latitude: {self.latitude}, Longitude: {self.longitude}")

    def setProfit(self, profit):
        ''' Set the profit of the task '''
        self._profit = profit

    @property
    def ID(self) -> str:
        ''' Return Task ID '''
        return self._ID

    @property
    def day(self) -> int:
        ''' Return Day Number '''
        return self._day
    
    @property
    def profit(self) -> int:
        ''' Return Profit '''
        return self._profit

    @property
    def service_time(self) -> int:
        ''' Return Service Time '''
        return self._service_time

    @property
    def start_time(self) -> int:
        ''' Return Start Time '''
        return self._start_time

    @property
    def end_time(self) -> int:
        ''' Return End Time '''
        return self._end_time

    @property
    def location_id(self) -> int:
        ''' Return Location ID '''
        return self._location_id

    @property
    def latitude(self) -> float:
        ''' Return Latitude '''
        return self._latitude

    @property
    def longitude(self) -> float:
        ''' Return Longitude '''
        return self._longitude

    def _str_(self):
        # This method makes it easier to print the object's attributes as a string
        return (f"ID: {self.ID}, Day: {self.day}, Service Time: {self.service_time}, "
               f"Start Time: {self.start_time}, End Time: {self.end_time}, "
               f"Location ID: {self.location_id}, Latitude: {self.latitude}, Longitude: {self.longitude}")

class OptionalTask:
    ''' Class for the attributes of an optional task '''

    def __init__(self, json_data):
        # Initialize attributes from a CSV row with explicit data type conversion
        self._ID = str(json_data.get('ID', ''))
        self._street = str(json_data.get("Street",""))
        self._number = str(json_data.get("Number",""))
        self._address = str(json_data.get("Address",""))
        self._location_id = int(json_data.get('LocationID', 0))
        self._latitude = float(json_data.get('Latitude', 0.0))
        self._longitude = float(json_data.get('Longitude', 0.0))
        self._location_id = int(json_data.get('LocationID',0))
        self._description = str(json_data.get('Description'))
        self._category = str(json_data.get('Category'))
        self._service_time = int(json_data.get('ServiceTime',0))
        self._profit = int(json_data.get('Profit',0))
        self._start_time = 0
        self._end_time = 0

    def __str__(self):
        # This method provides a string representation of the object
        return (f"ID: {self.ID}, Street: {self.street}, Number: {self.number}, Address: {self.address}, "
                f"Latitude: {self.latitude}, Longitude: {self.longitude}, Location ID: {self.location_id}, "
                f"Description: {self.description}, Category: {self.category}, Service Time: {self.service_time}, "
                f"Profit: {self.profit}")

    @property
    def ID(self):
        ''' Return Task ID '''
        return self._ID
    
    @property
    def start_time(self):
        ''' Return Start Time '''
        return self._start_time
    
    @property
    def end_time(self):
        ''' Return Start Time '''
        return self._end_time

    @property
    def street(self):
        ''' Return Street '''
        return self._street

    @property
    def number(self):
        ''' Return Number '''
        return self._number

    @property
    def address(self):
        ''' Return Address '''
        return self._address

    @property
    def latitude(self):
        ''' Return Latitude '''
        return self._latitude

    @property
    def longitude(self):
        ''' Return Longitude '''
        return self._longitude

    @property
    def location_id(self):
        ''' Return Location ID '''
        return self._location_id

    @property
    def description(self):
        ''' Return Description '''
        return self._description

    @property
    def category(self):
        ''' Return Category '''
        return self._category

    @property
    def service_time(self):
        ''' Return Service Time '''
        return self._service_time

    @property
    def profit(self):
        ''' Return Profit '''
        return self._profit


class InputData:
    '''Class for creating Data objects based on formatted Json Files containing the information of the regarding jobs and machines'''

    def __init__(self, main_task_path: str, optional_tasks_path: str = "Data/OptionalTasks.csv"):
        '''
        Initialize the InputData object with paths to the optional tasks and main tasks files.

        :param optional_tasks_path: Path to the CSV file containing optional tasks
        :param main_tasks_path: Path to the JSON file containing main tasks
        '''
        self._optional_tasks_path = optional_tasks_path
        self._main_tasks_path = main_task_path 

        # Load and create task objects from file paths
        self._Load_MainTasks()
        self._Load_OptionalTasks()

    def _Load_OptionalTasks(self) -> None:
        ''' Initialize the creation of a list of optional tasks based on the CSV file path'''

        # Initialize the list to store optional tasks
        self._optionalTasks = list()

        # Open the CSV file and read its contents
        with open(self._optional_tasks_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Create OptionalTask objects for each row in the CSV file
            for row in reader: 
                task = OptionalTask(row)
                task._end_time = self._maxRouteDuration
                self._optionalTasks.append(task)

    def _Load_MainTasks(self) -> None:
        ''' Initialize the creation of a list of main tasks based on the JSON file path'''

        # Initialize the list to store main tasks
        self._mainTasks = list()

        # Opening JSON file
        json_file = open(self._main_tasks_path)
        data = json.load(json_file)  # Load JSON data as a dictionary

        # Extract and store the attributes from the JSON data
        self._main_ID = data["ID"]
        self._cohort_no = int(data["Cohorts"])
        self._days = int(data["Days"])
        self._maxRouteDuration = int(data["MaxRouteDuration"])

        # Create MainTask objects for each task in the JSON data
        for task in data["MainTasks"]:
            self._mainTasks.append(MainTask(task))

    

    @property
    def optionalTasks(self):
        ''' Property to get the list of optional tasks '''
        return self._optionalTasks

    @property
    def mainTasks(self):
        ''' Property to get the list of main tasks '''
        return self._mainTasks
    
    @property
    def optional_tasks_path(self):
        ''' Property to get the path to the optional tasks file '''
        return self._optional_tasks_path
    
    @property
    def main_tasks_path(self):  
        ''' Property to get the path to the main tasks file '''
        return self._main_tasks_path

    @property
    def main_ID(self):
        ''' Property to get the main ID '''
        return self._main_ID

    @property
    def cohort_no(self):
        ''' Property to get the number of cohorts '''
        return self._cohort_no

    @property
    def days(self):
        ''' Property to get the number of days '''
        return self._days

    @property
    def maxRouteDuration(self):
        ''' Property to get the maximum route duration '''
        return self._maxRouteDuration