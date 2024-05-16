# IM_Challenge
Git Repo for cracking the IM Challenge

## Data Description

### Main Tasks
One main task per day per cohort for the planning horizont, which has to be in the time limtiations [start_time, start_time+service_time]

### Optional Tasks
 List of thousand extra maintenance visits, which are optional and increase the profit, when visited for each tour

## Solution Approach

### Constructive Heuristic

1. First plan one main task to each day to each cohort
2. Use adapted greedy algorithm to add optional tasks around the main task or on the way from the depot
3. Every route is split into two subtour one before and one after the main task, starting ending at the depot/ main task location respectively
4. Order optional tasks with c_1 and c_2 respectively the min_time and max_profit algorithm
5. Consider the stochastic selection of possible optional tasks with algorithm from Vansteenwegen2019_OrienteeringProblems

### Iterative Improvement / SA 

1. Define Neigborhoods
2. Change solution and check for feasibility!
3. Change until no improvements possible!

## :construction: What needs to be implemented 

1. Constructive Heuristic
2. Solution class
3. Class to assess solution
4. Output class


