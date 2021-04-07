# Authors:
# Kevin Grondin
# Daniel Wall
# Cael Shoop


import numpy as np
import pandas as pd


# Probability Table Indexing ##################################################################
#[0, 1, 0]
#[[[1,1], [1,1]], [[1,1], [1,1]]]
# |        0        |       1        |
# |    0   |   1    |   0   |    1   |
# |  0 | 1 | 0 | 1  | 0 | 1 |  0 | 1 |
# [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
# [0, 1, 1] = 4
def recursive_index(indices, table):
    if not indices and type(table) == type([]):
        return table[0]
    if indices:
        return recursive_index(indices[1:], table[abs(indices[0]-1)])
    return table
  
def recursive_pt_gen(depth, seed, lst, vals):
    if depth == 1:
        return vals[seed]
    else:
        lst.append([])
        lst.append([])
        lst[0] = recursive_pt_gen(depth/2, seed, lst[0], vals)
        lst[1] = recursive_pt_gen(depth/2, int(seed+depth/2), lst[1], vals)
        return lst
###############################################################################################


# Bayes Net ###################################################################################
class Network:
    def __init__(self, names, probTables):
        self.nodes = {} # Dictionary with key being node name and value being node

        numNodes = len(probTables)
        for ii in range(numNodes):
            self.nodes[names[ii]] = Node(names[ii], probTable=probTables[ii])

class Node:
    def __init__(self, name='', probTable=[]):
        self.name = name
        self.parentNodes = {}
        self.probTable = probTable
        self.probCalc = -1
        self.val = None
    
    def addParent(self, name, parent):
        # Maybe check here to make sure we don't create cyclic graph?
        self.parentNodes[name] = parent
###############################################################################################


# Enumeration Probability Calculation Method ##################################################
def enumerationAsk(query, observed, bayesNet):
    dist = []

    # Finding probability that the query is true
    observedTrue = observed.copy()
    observedTrue[query] = 1
    queryTrue = enumerateAll(list(bayesNet.nodes.values()), observedTrue)
    dist.append(queryTrue)

    # Finding probability that the query is false
    observedFalse = observed.copy()
    observedFalse[query] = 0
    queryFalse = enumerateAll(list(bayesNet.nodes.values()), observedFalse)
    dist.append(queryFalse)
    
    # Normalize distribution
    norm = np.linalg.norm(dist, ord=1)
    distNorm = dist/norm

    return distNorm

def enumerateAll(nodes, observed):
    # nodes input must be in topological parent-child order

    if not nodes:
        return 1

    Y = nodes[0]
    restOfNodes = nodes[1:]
    
    if Y.name in observed:
      	# If observed as false, get 1 - P(Y|A,B), otherwise, get P(Y|A,B)
        probYtrue = recursive_index([observed[parent] for parent in Y.parentNodes], Y.probTable)
        prob = abs((1 - observed[Y.name]) - probYtrue)
        return prob * enumerateAll(restOfNodes, observed)
    else:
        # If y is True
        observedTrue = observed.copy()
        observedTrue[Y.name] = 1
        probYtrue = recursive_index([observed[parent] for parent in Y.parentNodes], Y.probTable) * enumerateAll(restOfNodes, observedTrue)

        # If y is False
        observedFalse = observed.copy()
        observedFalse[Y.name] = 0
        probYfalse = (1 - recursive_index([observed[parent] for parent in Y.parentNodes], Y.probTable)) * enumerateAll(restOfNodes, observedFalse)
        
        # Returns the result of all possible parent combinations on this branch.
        return probYtrue + probYfalse

###############################################################################################

      
def main():

    alphabet = "ABCDEFGHIJ"

    try:
        df = pd.read_csv('../Downloads/input.csv', header=None)
    except:
        print('Input Error: Could not open input.csv.\nSee input_example.csv for help.')
        quit()


    # Getting prob tables
    probTables = []
    numRows = df.shape[0]
    numNodes = numRows - 4
    for ii in range(numNodes):
        probTable = pd.to_numeric(df.iloc[4+ii,1:], downcast="float")
        probTable = probTable.dropna().tolist()

        for prob in probTable:
            if prob < 0 or prob > 1:
                print('Probabilities must be between 0 and 1')
                quit()
        
        if len(probTable) > 1:
            probTable = recursive_pt_gen(len(probTable), 0, [], probTable)
        probTables.append(probTable)


    # Initializing Bayes Net
    names = alphabet[:numNodes]
    BayesNet = Network(names, probTables)


    # Implementing connections
    connections = df.iloc[0,1]
    connections = connections.split()

    if len(connections) < 4 or len(connections) > 15:
        print('Connections Error: Please use 7 to 15 connections.')

    for pair in connections:
        if pair[0] not in alphabet or pair[1] not in alphabet:
            print('Connections Error: Please use letters A-J corresponding with nodes 0-9.\nSee input_example.csv for help.')
            quit()

        try:
            child = BayesNet.nodes[pair[1]]
            parent = BayesNet.nodes[pair[0]]
            child.addParent(pair[0], parent)
        except:
            print('Connections Error: Please only use letters which correspond with a node described by the number of nodes.\nSee input_example.csv for help.')
            quit()
            

    # Getting observed values
    observedInput = df.iloc[1,1]
    observedInput = str(observedInput).split()
    observed = {}
    
    if observedInput != ['nan']:
        for pair in observedInput:
            nodeName = pair[0]
            if nodeName not in alphabet:
                print('Observed Error: Please use letters A-J corresponding with nodes 0-9.\nSee input_example.csv for help.')
                quit()

            val = int(pair[1])
            if val != 0 and val != 1:
                print('Observed Error: Please use 0 or 1 after each letter corresponding to Boolean value.\nSee input_example.csv for help.')
                quit()

            observed[nodeName] = val

    
    # Getting Query:
    queries = df.iloc[2,1]
    queries = queries.split()


    # Printing input info
    nodes = list(BayesNet.nodes.values())

    print("Probability Tables:")
    for node in nodes:
        print(f"{node.name}: {list(node.probTable)}")
    print()

    print("Parent Nodes:")
    for node in nodes:
        print(f"{node.name}: {list(node.parentNodes)}")
    print()

    print("Observations:")
    for node in observed:
        print(f"{node}: {bool(observed[node])}")
    print()


    print("Performing Queries (by Enumeration):")
    for query in queries:
        result = enumerationAsk(query, observed, BayesNet)
        #result = BayesNet.nodes[query].probCalc
        print(f"{query}: {result}")

        
if __name__ == "__main__":
    main()
