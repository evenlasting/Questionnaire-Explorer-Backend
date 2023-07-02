# -*- coding: utf-8 -*-
import functools
import numpy as np
import json
from tqdm import *
from data.Data import Data 
from algorithm.graph_cut import Graph
import math

class Mem:
    """
    a mem pool to record people's answers. So as to calculate wheter a combination of questions is a hyperedge.


    """
    def __init__(self):
        self.mem={}
        self.mem2id_list={}

    def append(self,string,id):
        if not(string in self.mem):
            self.mem[string]=1
            self.mem2id_list[string]=[id]
        else:
            self.mem[string]+=1
            self.mem2id_list[string].append(id)

    def get_id_list(self,string):
        return self.mem2id_list[string]

    
    def sort(self):
        return sorted(self.mem.items(),key=lambda d: d[1],reverse=True)


class Hypergraph:
    """
    construst a hypergraph model from the survey data

    Attibute:
        hyperedges_arr: a array of hyperedges

    methods:
    """

    def __init__(self,survey_data,threshold=0.6,max_category=0.3):
        """
        init
        :param survey_data
        :param threshold there is a set of people, the number of them is large than threshold of the sum and their answer of the questionnaire is less than max_category
        :param max_category please refer to threshold
        """
        self.data=np.array(survey_data.get_data_list_num())
        self.people_num=survey_data.get_people_num()
        self.question_num=survey_data.get_question_num()
        self.answer2string_list=survey_data.answer_array_map_num2string
        self._dict={}
        self._hyperedge_num=0
        self.threshold=threshold
        self.threshold_num=self.people_num*self.threshold
        self.max_category=max_category
        self.data_set=[]
        self.parse_data()
        self.question_id_array=[]
        self.hyper_edge_question_id_array=[]
        self.hyper_edge_option_array=[]
        self.hyper_edge_num_array=[]
        self.hyper_edge_option_num_array=[]
        self.hyper_edge_participants_id_array=[]
        self.solve_hyperedge_list=list(range(self.question_num))
        self.hyper_edges_groupby_dimension={}
        self.survey_data=survey_data

    def solve_hyperedge(self,dimension,node_list=None):
        if node_list != None:
            self.solve_hyperedge_list=node_list
        self.dimension=dimension
        self.question_id_array=[]
        self.hyper_edge_question_id_array=[]
        self.hyper_edge_num_array=[]
        self.hyper_edge_option_num_array=[]
        self.hyper_edge_option_array=[]
        hyperedge_num=len(self.hyper_edge_question_id_array)
        self._solve_combination(self.dimension,0)# first question is useless(agree to anwser the survey)
        self.solve_hyperedge_list=list(range(self.question_num))# init the self.solve_hyperedge_list, cuz node_list can be None
        if len(self.hyper_edge_question_id_array)==hyperedge_num:
            return False
        else:
            self.hyper_edges_groupby_dimension[self.dimension]={
                'id':self.hyper_edge_question_id_array.copy(),
                'id_num':self.hyper_edge_num_array.copy(),
                'option':self.hyper_edge_option_array.copy(),
                'option_num':self.hyper_edge_option_num_array.copy(),
                'participants':self.hyper_edge_participants_id_array.copy()}
            return True

    def _solve_combination(self,left_dimension,question_id):
        """
        return the possible question combinations

        :param left_dimension  how many more questions do we need
        :param question_id biggest question_id in the question_id_array
        """
        # if left_dimension==1 and self.dimension>2 and not(self.question_id_array in self.hyper_edges_groupby_dimension[self.dimension-1]['id']):
        #     # print(self.question_id_array)
        #     return
        if left_dimension==0:
            self.check_question_id_array()
        else:
            _range=range(question_id,len(self.solve_hyperedge_list))
            if left_dimension==self.dimension:
                _range=tqdm(_range)
            for index in _range:
                self.question_id_array.append(self.solve_hyperedge_list[index])
                self._solve_combination(left_dimension-1,index+1)
                self.question_id_array.pop()


    def rise_dimension(self):
        self.dimension=self.dimension+1

    def parse_data(self):
        print('data',self.data)
        for i in range(len(self.data[0])):
            option_set=set(self.data[:,i].tolist())
            self.data_set.append(option_set)

    def check_question_id_array(self):
        """
        check the questions in question_id_array satisfy constraints or not
        """
        mem=Mem()
        if len(self.question_id_array)!=self.dimension:
            return False
        for i in range(len(self.data)):
            string_arr=[]
            for question_id in self.question_id_array:
                string_arr.append(str(self.data[i][question_id]))
            if any([x!='-1' for x in string_arr]):
                mem.append("+".join(string_arr),i)
            #     print(string_arr)
            # else:
            #     print(string_arr)
        sort_ans=mem.sort()
        top_ans=sort_ans[0:math.ceil(math.pow(self.max_category,self.dimension-1)*len(sort_ans))]
        # option_array=map(lambda d: d[0],top_ans)
        number_array=list(map(lambda d: d[1],top_ans))

        if (sum(number_array)<self.threshold_num):
            return False
        else:
            self.hyper_edge_option_array.append(list(map(lambda d: [self.answer2string_list[self.question_id_array[x_index]][int(x)] if x!='-1' else 'no_answer' for x_index,x in enumerate(d[0].split('+'))],top_ans)))
            self.hyper_edge_option_num_array.append(number_array)
            self.hyper_edge_num_array.append(sum(number_array))
            self.hyper_edge_question_id_array.append(self.question_id_array.copy())
            # participants_id_array=list(map(lambda d: [[mem.get_id_list(x)] for x in (d[0].split('+'))],top_ans))
            participants_id_array=list(map(lambda d: [mem.get_id_list(d[0])] ,top_ans))
            self.hyper_edge_participants_id_array.append(functools.reduce(lambda x,y: x+y, participants_id_array))
            return True

    # def solve_hyperedge_sankey(self,sankey_name_arr):
        # mem=Mem()
        # sankey_arr=list(map(lambda x: nodes.index(x),sankey_name_arr))
        # for i in range(len(self.data)):
        #     string_arr=[]
        #     for question_id in sankey_arr:
        #         string_arr.append(nodes[question_id]+":"+self.data[i][question_id])
        #     mem.append("+".join(string_arr))
        # sort_ans=mem.sort()
        # top_ans=sort_ans[0:self.max_category]
        # option_array=list(map(lambda d: d[0],top_ans))
        # number_array=list(map(lambda d: d[1],top_ans))
        # hyper_edge_ans=[]
        # for i in range(self.max_category):
        #     hyper_edge_ans.append({
        #         "value":number_array[i],
        #         "hyperedge":option_array[i].split("+")
        #     })
        # return hyper_edge_ans


    def save_file(self):
        print(len(self.hyper_edge_num_array))
        with open('data.txt','w') as f:
            f.write(json.dumps(self.hyper_edge_question_id_array))

    def check_potential(self,hyper_edge_list):
        dimension=len(hyper_edge_list[0])
        

    def transfer2graph(self):
        i_dimension=2
        nodes=self.solve_hyperedge_list
        edges=np.zeros((self.question_num,self.question_num))
        while i_dimension in self.hyper_edges_groupby_dimension:
            data_this_dimension=self.hyper_edges_groupby_dimension[i_dimension]
            hyperedges_id=data_this_dimension['id']
            hyperedges_num=data_this_dimension['id_num']
            for i_hyperedges in range(len(hyperedges_id)):
                num=hyperedges_num[i_hyperedges]
                node_arr=hyperedges_id[i_hyperedges]
                for i_first_node in range(len(node_arr)):
                    for j_sec_node in range(i_first_node+1,len(node_arr)):
                        first_node_id=node_arr[i_first_node]
                        sec_node_id=node_arr[j_sec_node]
                        edges[first_node_id][sec_node_id]+=num
            i_dimension+=1
            self.graph_nodes=nodes
            self.graph_edges=edges
        return nodes,edges

    def graphcut(self,nodes,edges,pieces_num=6):
        nodes_cut=[nodes]
        G=Graph(nodes,edges)
        while True:
            biggest_index=np.argmax(np.array([len(x) for x in nodes_cut]))
            biggest_group=nodes_cut[biggest_index]
            if len(biggest_group)<self.question_num/pieces_num:
                break
            cost_arr=[]
            new_group=[]
            while True:
                G=Graph(biggest_group,edges)
                cost,cutted_group=G.cut()#cutted_group[0]:smaller cutted_group[1]:bigger
                new_group.extend(cutted_group[0])
                if len(cost_arr)>1 and cost>3*(cost_arr[-1]):
                    del nodes_cut[biggest_index]
                    nodes_cut.append(new_group)
                    nodes_cut.append(cutted_group[1])
                    # print(nodes_cut)
                    break
                biggest_group=cutted_group[1]
                cost_arr.append(cost)
                if len(biggest_group)<self.question_num/pieces_num:
                    del nodes_cut[biggest_index]
                    nodes_cut.append(new_group)
                    nodes_cut.append(cutted_group[1])
                    break
        # print(nodes_cut)
        for i in range(len(nodes_cut)-1,-1,-1):
            if len(nodes_cut[i])<self.question_num/pieces_num/2:
                print(i,len(nodes_cut))
                nodes_cut[i+1].extend(nodes_cut[i])
                del nodes_cut[i]
        return nodes_cut


