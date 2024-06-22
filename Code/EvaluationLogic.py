import numpy 
from copy import deepcopy
from InputData import InputData
from OutputData import Solution, OutputJob

class EvaluationLogic:
    ''' Evalution Objects to calculate objectives of the given solutions'''

    def __init__(self, inputData:InputData):
        ''' Initialize by addinbg data'''
        self.InputData = inputData      


    def DefineStartEnd(self,currentSolution:Solution):
        ''' Calculate the start and the end times of the jobs of the given solution'''


    def DetermineBestInsertion(self, solution:Solution, jobToInsert:int):
        ''' Insert an job at every possible position of the permutation and pick the best option to proceed further!
        