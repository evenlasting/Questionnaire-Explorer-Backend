import pandas as pd
import numpy as np
from pandas.core.reshape.pivot import crosstab
from scipy.stats import chi2_contingency
from tqdm import *

def read_csv(file_url,question_list=[],people_list=[]):
    df=pd.read_csv(file_url)
    all_question_list=list(df.columns)
    print(question_list)
    if people_list!=[]:
        df=df.loc[df[all_question_list[people_list[0]]]==people_list[1]]
    if question_list!=[]:
        if (type(question_list[0])==int):
            question_list=[all_question_list[x] for x in question_list]
        df=df[question_list]
        # df=df.iloc[people_list]
    print('dddddddddfffffffffffff----------',df)
    df=df.replace('NA',np.nan)
    df=df.replace(-99,np.nan)
    df=df.replace('N/A',np.nan)
    df=df.replace('-99',np.nan)
    question_num=len(df.columns)
    question_index=list(df.columns)
    answer_name_arr=[]
    answer_count_arr=[]
    answer_type_arr_isnum=[]
    for index in question_index:
        answer_type_arr_isnum.append(df[index].dtypes=='float64' or df[index].dtypes=='int64')
    df=df.fillna('no_answer')
    for index in question_index:
        # answer_unique=sorted(df[index].dropna().unique())
        # answer_unique=sorted(df[index].dropna().unique())
        # answer_name_arr.append(answer_unique)
        answer_count_arr.append(df[index].value_counts(dropna=False))#.rename(index={np.nan:'no_answer'}))
    chi_square_arr=np.ones((question_num,question_num))
    for idx,first_question_index in tqdm(enumerate(question_index)):
        for jdx,sec_question_index in enumerate(question_index):
            if (jdx<=idx):
                continue
            try:
                crosstab=pd.crosstab(df[first_question_index],df[sec_question_index])
                chi_square=chi2_contingency(crosstab,correction=True)
                chi_square_arr[idx][jdx]=chi_square[1]
                chi_square_arr[jdx][idx]=chi_square[1]
            except:
                chi_square_arr[idx][jdx]=1
                chi_square_arr[jdx][idx]=1
    return{
        'df':df,
        'num':question_num,
        'index':question_index,
        'answer_name':[list(x.index) for x in answer_count_arr],
        'answer_count':answer_count_arr,
        'answer_type_isnum':answer_type_arr_isnum,
        'chi_square_arr':chi_square_arr,
        'all_question_list':all_question_list
    }


if __name__=='__main__':
    a=read_csv('./survey_source.csv',[1,2])
    print(a)