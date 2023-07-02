import networkx as nx

# G=nx.Graph()
# G.add_nodes_from([0,1,3])
# G.add_edges_from([(1,3,{'weight':2}),(1,0,{'weight':0}),(3,0,{'weight':1.5})])

# print(nx.stoer_wagner(G))
# print(list(G.edges),G.edges[1,2])
# print(G.edges[0,1])

class Graph:
    """
    this class contains a method of graph cutting(SW algorithm: the edges have weight and don't have direction) and a prop of networkx
    """

    def __init__(self,nodes_arr,edges_arr) -> None:
        """
        we init a nx class by node_arr and edges_arr in this method.

        :param nodes_arr a 1d array,like [1,2,3]
        :param edges_arr a 2d array, and the elements are the weight of the indexes
        """
        self.G=nx.Graph()
        self.G.add_nodes_from(nodes_arr)
        for i in range(len(nodes_arr)):
            for j in range(i+1,len(nodes_arr)):
                node_i=nodes_arr[i]
                node_j=nodes_arr[j]
                self.G.add_edges_from([(node_i,node_j,{'weight':edges_arr[node_i][node_j]})])
    
    def cut(self):
        """
        cut the graph into 2 pieces by nx.stoer_wagner

        :return ans[0]: the cost of this cut
        :return ans[1]: (the first part, the second part)
        """
        ans=nx.stoer_wagner(self.G)
        (bigger,smaller)=ans[1]
        if (len(smaller)>len(bigger)):
            (bigger,smaller)=(smaller,bigger)
        return ans[0],(smaller,bigger)
