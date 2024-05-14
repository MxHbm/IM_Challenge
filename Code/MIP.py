
### Here you can define other needed functions

def main():

    # Example TOP Vansteenwegen p.23 --> Szeanrio Flexi IM Challenge

    # Paramters

    N = list(range(6))      # Locations: First and Last Index --> Depot
                            # 4 Locations and 1 Depot

    P_i = [0,5,8,1,4,0]     # Profit for Locations
                            # Profit for Depot is 0


    M_m = list(range(2))    # Number of available Days or Teams --> Routes
    T_max = 15              # Time Units of one "Day"

    t_ij = [[0,3,6,6,3,0],
            [3,0,4,5,3,3],
            [6,4,0,3,5,6],
            [6,5,3,0,4,6],
            [3,3,5,4,0,3],
            [0,3,6,6,3,0]] # Travel duration between Locations
    
    # Model


    import gurobipy as gb
    model = gb.Model()
    import os
    outputFolder = "/Users/niklas/Desktop/10. Semester/IM_Challenge/Code"
    os.makedirs(outputFolder, exist_ok=True)



    # Indices

    I = range(len(N))
    J = range(len(N))
    M = range(len(M_m))


    # Variablen

    x = model.addVars(I,J,M, name = "x", vtype=gb.GRB.BINARY)
    y = model.addVars(I,M, name = "y", vtype=gb.GRB.BINARY)
    u_im = model.addVars(I,M, name = "u_im", vtype=gb.GRB.INTEGER)
    u_jm = model.addVars(J,M, name = "u_jm", vtype=gb.GRB.INTEGER)

    # Objective Function

    model.setObjective(sum(P_i[i] * y[i,m] for m in M for i in I[1:-1]), gb.GRB.MAXIMIZE)

    # Constraints
    
    model.addConstr(sum(x[0,j,m] for m in M for j in J[1:]) == sum(x[i, J[-1], m] for m in M for i in I[:-1]), "Constraint 3.2a")
    model.addConstr(sum(x[0,j,m] for m in M for j in J[1:]) == len(M), "Constraint 3.2b")
    model.addConstr(sum(x[i, J[-1], m] for m in M for i in I[:-1]) == len(M), "Constraint 3.2c")

    for k in I[1:-1]:
        model.addConstr(sum(y[k,m] for m in M) <= 1, "Constraint 3.3")
    
    for m in M:
        for k in I[1:-1]:
             model.addConstr(sum(x[i,k,m] for i in I[:-1]) == sum(x[k,j,m] for j in J[1:]), "Constraint 3.4a")
             model.addConstr(sum(x[i,k,m] for i in I[:-1]) == y[k,m], "Constraint 3.4b")
             model.addConstr(sum(x[k,j,m] for j in J[1:]) == y[k,m] , "Constraint 3.4c")

    for m in  M:
        model.addConstr(sum(t_ij[i][j]*x[i,j,m] for i in I[:-1] for j in J[1:]) <= T_max, "Constraint 3.5")

    for m in M:
        for i in I[1:]:
             model.addConstr(u_im[i,m] >= 2, "Constraint 3.6a")
             model.addConstr(u_im[i,m] <= len(N), "Constraint 3.6b")

    for m in M:
        for i in I[1:]:
             for j in J[1:]:
                model.addConstr(u_im[i,m] - u_jm[j,m] + 1 <= (len(N) - 1)*(1 - x[i,j,m]), "Constraint 3.7")

    
    model.optimize()

    model.printAttr(gb.GRB.Attr.ObjVal)
    model.printAttr(gb.GRB.Attr.X)

    

    model.write(os.path.join(outputFolder,"model.lp"))



main()