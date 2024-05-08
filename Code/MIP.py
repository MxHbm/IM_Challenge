
### Here you can define other needed functions

def main():

    # Example TOP p.23 --> Szeanrio Flexi IM Challenge

    # Paramters

    N = list(range(6))      # Locations: First and Last Index --> Depot
                            # 4 Locations and 1 Depot

    P_i = [0,5,8,4,1,0]     # Profit for Locations
                            # Profit for Depot is 0


    M_m = list(range(2))    # Number of available Days
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


    # Indices

    I = range(len(N))
    J = range(len(N))
    M = range(len(M_m))


    # Variablen

    x = model.addVars(I,J,M, name = "x", vtype=gb.GRB.BINARY)
    y = model.addVars(I,M, name = "y", vtype=gb.GRB.BINARY)
    u_im = model.addVars(I,M, name = "u_im", vtype=gb.GRB.BINARY)
    u_jm = model.addVars(J,M, name = "u_jm", vtype=gb.GRB.BINARY)

    # Objective Function

    model.setObjective(sum(P_i[i] * y[i,m] for i in I for m in M), gb.GRB.MAXIMIZE)

    # Constraints

    # Space for Constraint 3.2

    for k in I[1:-1]:
        model.addConstr(sum(y[k,m] for m in M) <= 1, "Constraint 3.3")




main()