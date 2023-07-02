import numpy as numpy
import pandas as pd
from scipy.stats import chi2_contingency
from data.file import read_csv

class Data:
    """save the data of questionnaire

    transform the string answer to numbers

    Attributes:
        data_list: pd
        data_list_num:
        size:[people_num,question_num]
        question_list: the titles of some questions in the data_list, like [str] not [id]
        answer_list:
        answer_array_map_num2string:


    """
    def __init__(self,data_url,question_list=[],answer_list=[],people_list=[]):
        survey=read_csv(data_url,question_list,people_list)
        self.data_list=survey['df']
        self.chi=survey['chi_square_arr']
        self.data_list_num=[]
        self.size=[len(survey['df']),survey['num']]
        self.all_question_list=survey['all_question_list']
        self.question_list=survey['index']
        self.answer_list=answer_list
        self.answer_array_map_num2string=survey['answer_name']
        self.answer_type_isnum=survey['answer_type_isnum']
        self.answer_count=survey['answer_count']
        # self._transfer_answer2num()
        self._transfer_data_list_string2num()
        # self._solve_chi()

    # def _solve_chi(self):
    #     pass

    def _transfer_answer2num(self):
        for i_question in range(self.size[1]):
            answer_map_num2string={}
            answer_tail=0
            for j_people in range(self.size[0]):
                answer_i_j=self.data_list[j_people][i_question]
                if (answer_i_j in answer_map_num2string):
                    continue
                answer_map_num2string.update({answer_i_j:answer_tail})
                answer_tail+=1
            self.answer_array_map_num2string.append(answer_map_num2string)
    
    def _transfer_data_list_string2num(self):
        for i_people in range(self.size[0]):
            answer_list_num=[]
            for j_question in range(self.size[1]):
                if self.data_list.iloc[i_people][j_question]!='no_answer': #np.nan is not in the answer list
                    answer_list_num.append(self.answer_array_map_num2string[j_question].index(self.data_list.iloc[i_people][j_question]))
                else:
                    answer_list_num.append(-1)
            self.data_list_num.append(answer_list_num)
        # with open('data_list_num.txt','w') as f:
        #     import json
        #     f.write(11)
        #     f.close()

    def get_size(self):
        return self.size
    
    def get_people_num(self):
        return self.size[0]

    def get_question_num(self):
        return self.size[1]

    def get_answer_map_arr(self):
        return self.answer_array_map_num2string

    def get_data_list_num(self):
        return self.data_list_num

    def cut(self,k=4):
        """
        cut the hypergraph into k pieces
        :param k
        :return: a array of Class Data
        """
        pass

    def solve_hyperedges(self):
        """
        solve all hyperedges in the graph
        :return
        """
        pass

    
    
# a=Data()
# print(a.get_data_list_num())