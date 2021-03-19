# Authors:
# Kevin Grondin
# Daniel Wall
# Cael Shoop

import numpy as np
import pandas as pd


def recursive_pt_gen(depth, seed, lst, vals):
    if depth == 1:
        return vals[seed]
    else:
        lst.append([])
        lst.append([])
        lst[0] = recursive_pt_gen(depth/2, seed, lst[0], vals)
        lst[1] = recursive_pt_gen(depth/2, int(seed+depth/2), lst[1], vals)
        return lst

# Probability tables stored as [[FF, FT], [TF, TT]]
      
class Node:
    def __init__(self, pt=[], val=0):
        self.value = val
        self.i_nodes = []
        self.prob_table = pt
        self.prob = 0
        
    def add_parent(self, parent):
        self.i_nodes.append(parent)
        
    def feed_forward(self):
        pos = self.prob_table
        for ii in range(len(self.i_nodes)):
            pos = pos[self.i_nodes[ii].value]
        self.prob = pos
    
    def print_node(self):
      	print(self, self.value, self.i_nodes)
    
    def init_pt(self, pt):
        res = pt[::-1]
        self.prob_table = recursive_pt_gen(2**len(self.i_nodes), 0, [], res)
        


class DAG:
    def __init__(self, num, bool_vals):
        self.num_nodes = num
        self.nodes = []
        for ii in range(self.num_nodes):
            self.nodes.append(Node(val=bool_vals[ii]))

    def feed_forward(data):
        pass

def main():
    alphabet = "ABCDEFGHIJ"

    try:
        df = pd.read_csv('input.csv')
    except:
        print('Please enter inputs in input.csv. See format.csv for help.')
        quit()

    num_nodes = int(df.iloc[0,0])
    print('Number of Nodes:', num_nodes)
    if num_nodes < 5 or num_nodes > 10:
        print('Please use 7 to 10 nodes.\nEx. input: "7 1101011"')
        quit()
    
    boolean_values = df.iloc[1,0]
    print('Boolean Values:', boolean_values)
    if len(boolean_values) != num_nodes:
        print('Please input the same number of Boolean values as the number of nodes.\nEx. input: "7 1101011"')
        quit()
    
    node_values = [0]*num_nodes
    for ii in range(len(boolean_values)):
        if boolean_values[ii] not in "01":
            print('Please use 0 (false) or 1 (true) when assigning boolean values.\nEx. input: "7 1101011"')
            quit()
        node_values[ii] = int(boolean_values[ii])

    our_dag = DAG(num_nodes, node_values)

    connection_list = df.iloc[2,0]
    connection_list = connection_list.split()
    print('Connection List:', connection_list)
    if len(connection_list) < 7 or len(connection_list) > 15:
        print('Please use 7 to 15 arcs.')
        quit()

    for pair in connection_list:
        if pair[0] not in alphabet or pair[1] not in alphabet:
            print('Please use letters A-J corresponding with nodes 0-9.\nEx. input: "AC BC CD CE DF DG EG"')
            quit()
        try:
            our_dag.nodes[alphabet.index(pair[1])].add_parent(our_dag.nodes[alphabet.index(pair[0])])
        except:
            print('Please only use letters which correspond with a node described by the number of nodes.\nEx. 7 nodes => only use letters A-G')
            quit()

    if len(df.columns) != num_nodes + 1:
      	print('Please input number of columns corresponding to the number of nodes')
      	quit()
                                
    print('Probability tables:')                 
    for ii in range(num_nodes):
        pt = df.iloc[:,ii+1]
        pt = pt.dropna().tolist()

        for p in pt:
            if p < 0 or p > 1:
                print('Probabilities must be between 0 and 1')

        our_dag.nodes[ii].init_pt(pt)
        print(str(df.columns[ii+1]) + ':', our_dag.nodes[ii].prob_table)

  
if __name__ == "__main__":
    main()