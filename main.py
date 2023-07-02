
# -*- coding: utf-8 -*-
from algorithm.Hyperedge import Hypergraph
from data.Data import Data
from operator import attrgetter,itemgetter
# from algorithm.reorder import Parts_2D
import pandas as pd
from pycausal.pycausal import pycausal
from pycausal import search as s
from algorithm.causal import solve_causal
import pickle
from algorithm.linearRegression import linearRegression
import hashlib
import os

debug=False
hyper=None
cut=None
pc=pycausal()
pc.start_vm()
tetrad=s.tetradrunner()

threshold=0.6
max_category=0.4
question_num=17
people_num=450#481

# if debug:
#     f=open('hyper40.txt','rb')
#     hyper=pickle.load(f)
#     # pickle.dump(hyper,f)
#     f.close()

from flask import Flask,request
app = Flask(__name__)

import json

from flask_cors import CORS,cross_origin

# from algorithm.Hyperedge import Hypergraph

# hyper=Hypergraph(threshold=0.5)
cors = CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/datainput',methods=['POST'])
def solve_hypedge():
    obj = request.files.get('file')
    file_name=obj.filename
    print(file_name)
    obj.save(str(file_name))
    # hyperedge_dimension=request.form['d']
    return  json.dumps(1)

@app.route('/group',methods=['POST'])
def solve_group():
    data=request.get_json()
    question_arr=data['question']
    people_arr=data['people']
    # people_arr is a set of constraints
    # data=Data('./data/survey_source.csv',people_list=people_arr,question_list=question_arr)
    data=Data('./data/StudentPerformance.csv',people_list=people_arr,question_list=question_arr)
    if question_arr==[]:
        question_arr=list(range(0,question_num))
    hyper=Hypergraph(data,threshold=threshold,max_category=max_category)
    i=2
    ans=[]
    while hyper.solve_hyperedge(i):
        for hyperedge_id in range(len(hyper.hyper_edges_groupby_dimension[i]['id'])):
            ans.append({
                'question':[question_arr[order] for order in hyper.hyper_edges_groupby_dimension[i]['id'][hyperedge_id]],
                'num':hyper.hyper_edges_groupby_dimension[i]['id_num'][hyperedge_id],
                'dimension':i,
                'option':hyper.hyper_edges_groupby_dimension[i]['option'][hyperedge_id][0:3],
                'option_num':hyper.hyper_edges_groupby_dimension[i]['option_num'][hyperedge_id][0:3],
                'participants':hyper.hyper_edges_groupby_dimension[i]['participants'][hyperedge_id]
            })
        i+=1
        if i>3:
            break
    ans.sort(key=itemgetter('dimension','num'),reverse=True)
    if (len(people_arr)==0): people_arr=list(range(people_num))
    # bicluster_matrix=Parts_2D(question_arr,people_arr)
    # bicluster_index=[]
    # for index,bicluster in enumerate(ans):
    #     if (bicluster_matrix.check_and_insert(bicluster['question'],bicluster['participants'][0])):
    #         bicluster_index.append(index)
    # ans[0]['bicluster']=bicluster_matrix.to_json()
    # ans[0]['bi_index']=bicluster_index
    return json.dumps(ans)

def check_overlap(hyperedge1,hyperedge2):
    q_overlap=len(list(set(hyperedge1['question']).intersection(set(hyperedge2['question']))))>0
    r_overlap=len(list(set(hyperedge1['participants'][0]).intersection(set(hyperedge2['participants'][0]))))>0
    return q_overlap and r_overlap




@app.route('/survey',methods=['POST'])
def update_survey():
    global cut
    global hyper
    data=request.get_json()
    m2 = hashlib.md5()
    m2.update(json.dumps(data).encode())
    file_name=m2.hexdigest()
    # question_arr=data['question']
    question_arr=list(range(0,question_num))
    people_arr=data['people']
    if debug and os.path.isfile(file_name):#people_arr==[]:
        # hyper=Hypergraph(data,threshold=0.65,max_category=0.3)
        # i=2
        # while i<=3 and hyper.solve_hyperedge(i):
        #     print(hyper.hyper_edge_question_id_array)
        #     i+=1
        #     print(i)
        print(file_name)
        f=open(file_name,'rb')
        hyper=pickle.load(f)
        data=hyper.survey_data
        question_arr=data.question_list
        f.close()
    else:
        # data=Data('./data/survey_source.csv',people_list=people_arr,question_list=question_arr)
        data=Data('./data/StudentPerformance.csv',people_list=people_arr,question_list=[])
        question_arr=data.question_list
        hyper=Hypergraph(data,threshold=0.50,max_category=0.4)
        i=2
        while i<=3 and hyper.solve_hyperedge(i):
            print(hyper.hyper_edge_question_id_array)
            i+=1
            print(i)
        f=open(file_name,'wb')
        pickle.dump(hyper,f)
        f.close()
    nodes,edges=hyper.transfer2graph()
    cut=hyper.graphcut(nodes,edges,pieces_num=6)
    cut=[[0,1,2,3,5,6,7],[9,10,11,12,15],[4,8,13,14,16]]
    # cut= [list(range(17))]
    # cut.append([32,1,34,3,33,36,37,41,42,50,47,60,61,4,16,30])
    newNodes=['Q'+str(data.all_question_list.index(x)) for x in question_arr]
    newQuestion={}
    for i in range(len(question_arr)):
        newQuestion[newNodes[i]]=question_arr[i]
    return  json.dumps({
        'newCHIGroup':[[[node,0] for node in x] for x in cut],
        'newNODE':newNodes,
        'newQuestion':newQuestion,
        'newTypeList':[1 for x in question_arr],
        'newNodesConnections':(edges/data.get_people_num()).tolist(),
        'newPeopleNumber':data.get_people_num(),
        'newCHI':data.chi.tolist(),
        'newOption':[list(x.index) for x in data.answer_count],
        'newOptionNum':[list(x) for x in data.answer_count],
        # 'bicluster':generate_init_matrix(cut)
    })


@app.route('/cause',methods=['POST'])
@cross_origin()
def solve_causal_constrain():
    pc.start_vm() # for unknown reason of java_bridge, the vm must restart.
    global hyper
    df=pd.DataFrame(hyper.data)
    constraints=request.get_json()
    print('----------------------',constraints)
    ans=solve_causal(pc,tetrad,df,constraints['r'],constraints['f'],constraints['t'])
    
    return json.dumps(ans)

@app.route('/linear',methods=['POST'])
def solve_linear():
    data=request.get_json()
    targetQuestion=data['t']
    sourceQuestionList=data['s']
    global hyper
    success,ans=linearRegression(sourceQuestionList,targetQuestion,hyper)
    return json.dumps({
        "success":success,
        "coefficient":ans[0],
        "R":ans[1]
    })


if __name__ == '__main__':
   app.run(debug=False,host='0.0.0.0')
