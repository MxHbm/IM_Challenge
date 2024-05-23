import gurobipy as gp
import os


### Here you can define other needed functions

def main():

    # Example TOP Vansteenwegen p.23 --> Szeanrio Flexi IM Challenge

    # Paramters

    N = list(range(6))      # Locations: First and Last Index --> Depot
    days = 5                            # Number of Days
                            # 4 Locations and 1 Depot

    P_i = [0,5,8,1,4,0]     # Profit for Locations
                            # Profit for Depot is 0


    M_m = list(range(2))    # Number of available Days or Teams --> Routes
    T_max = 15           # Time Units of one "Day"

    t_ij = [[0,3,6,6,3,0],
            [3,0,4,5,3,3],
            [6,4,0,3,5,6],
            [6,5,3,0,4,6],
            [3,3,5,4,0,3],
            [0,3,6,6,3,0]] # Travel duration between Locations
    
    # Model
    model = gp.Model()

    # Get the current working directory (cwd)
    cwd = os.getcwd() 
    # Define the output folder path relative to the script location
    outputFolder = cwd + "/Code"


    # Indices

    I = range(len(N))
    J = range(len(N))
    M = range(len(M_m))
    T = range(days)


    # Variablen

    x = model.addVars(I,J,M,T, name = "x", vtype=gp.GRB.BINARY)
    y = model.addVars(I,M,T, name = "y", vtype=gp.GRB.BINARY)
    u = model.addVars(I,M,T, name = "u", vtype=gp.GRB.INTEGER)

    # Objective Function

    model.setObjective(gp.quicksum(P_i[i] * y[i,m,t] for m in M for i in I[1:-1] for t in T), gp.GRB.MAXIMIZE)

    # Constraints
    for t in T:
        model.addConstr(gp.quicksum(x[0,j,m,t] for m in M for j in J[1:]) == gp.quicksum(x[i, J[-1], m, t] for m in M for i in I[:-1]), "Constraint 3.2a")
        model.addConstr(gp.quicksum(x[0,j,m,t] for m in M for j in J[1:]) == len(M), "Constraint 3.2b")
        model.addConstr(gp.quicksum(x[i, J[-1], m, t] for m in M for i in I[:-1]) == len(M), "Constraint 3.2c")

    ## Visit every node maximum once per Team and in the whole timespan  - Profit should be 18
    for k in I[1:-1]:
        model.addConstr(gp.quicksum(y[k,m,t] for m in M for t in T) <= 1, "Constraint 3.3")
    
    
    for m in M:
        for k in I[1:-1]:
            for t in T:
                model.addConstr(gp.quicksum(x[i,k,m,t] for i in I[:-1]) == gp.quicksum(x[k,j,m,t] for j in J[1:]), "Constraint 3.4a")
                model.addConstr(gp.quicksum(x[i,k,m,t] for i in I[:-1]) == y[k,m,t], "Constraint 3.4b")
                model.addConstr(gp.quicksum(x[k,j,m,t] for j in J[1:]) == y[k,m,t] , "Constraint 3.4c")

    for m in  M:
        for t in T:
            model.addConstr(gp.quicksum(t_ij[i][j]*x[i,j,m,t] for i in I[:-1] for j in J[1:]) <= T_max, "Constraint 3.5")

    for m in M:
        for i in I[1:]:
            for t in T:
                model.addConstr(u[i,m,t] >= 2, "Constraint 3.6a")
                model.addConstr(u[i,m,t] <= len(N), "Constraint 3.6b")

    for m in M:
        for i in I[1:]:
             for j in J[1:]:
                for t in T:
                    model.addConstr(u[i,m,t] - u[j,m,t] + 1 <= (len(N) - 1)*(1 - x[i,j,m,t]), "Constraint 3.7")

    
    model.optimize()

    model.printAttr(gp.GRB.Attr.ObjVal)
    model.printAttr(gp.GRB.Attr.X)

    

    model.write(os.path.join(outputFolder,"model.lp"))
    # You can now use the outputFolder path in your script
    print(f"Output folder created at: {outputFolder}")



main()