# Authors:
# Kevin Grondin
# Daniel Wall
# Cael Shoop

import numpy as np
import pandas as pd


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
        self.val = None
    
    def addParent(self, name, parent):
        # Maybe check here to make sure we don't create cyclic graph?
        self.parentNodes[name] = parent


def enumerationAsk(query, observed, bayesNet):
    X # intialized as empty distribution

    for Xquery in query:
        Xobserved = observed.append(Xquery)
        Xresult = enumerateAll(bayesNet.nodes, Xobserved)
        result.append(Xresult)
    
    # Normalize result
    norm = np.linalg.norm(X)
    Xnorm = X/norm

    return Xnorm

def enumerateAll(bayesNetVars, observed):
    if not bayesNetVars:
        return 1
    
    Ynode = bayesNetVars[0]
    Yvar = list(bayesNetVars)[0]

    if Yvar in observed:
        restVars = bayesNetVars[1:]
        P_y = Ynode.prob if observed.get(Yvar) is True else 1 - Ynode.prob

        return P_y * enumerateAll(restVars, observed)

    else:
        Yobserved = observed

        Yobserved[Y] = True
        Ytrue = Ynode.prob * enumerateAll(restVars, Yobserved)

        Yobserved[Y] = False
        Yfalse = (1 - Ynode.prob) * enumerateAll(restVars, Yobserved)
        
        return Ytrue + Yfalse


def main():

    alphabet = "ABCDEFGHIJ"

    try:
        df = pd.read_csv('input.csv', header=None)
    except:
        print('Input Error: Please enter inputs in input.csv.\nSee input_example.csv for help.')
        quit()


    # Getting prob tables
    probTables = []
    numNodes = len(df.columns)
    for ii in range(numNodes):
        probTable = df.iloc[5:,ii]
        probTable = probTable.dropna().tolist()

        for prob in probTable:
            prob = float(prob)
            if prob < 0 or prob > 1:
                print('Probabilities must be between 0 and 1')
        
        probTables.append(probTable)


    # Initializing Bayes Net
    names = alphabet[:numNodes]
    BayesNet = Network(names, probTables)


    # Implementing connections
    connections = df.iloc[0,1]
    connections = connections.split()
    print(f'Connections: {connections}')

    if len(connections) < 7 or len(connections) > 15:
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

    for node in list(BayesNet.nodes.values()):
        print(f"{node.name} parents: {list(node.parentNodes)}")


    # Getting observed values
    observedInput = df.iloc[1,1]
    observedInput = observedInput.split()
    print(f"Observed Input: {observedInput}")
    observed = {}
    
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
    query = df.iloc[2,1]
    query = query.split()


    # Performing Query
    #enumerateAsk(query, observed, BayesNet)












if __name__ == "__main__":
    main()