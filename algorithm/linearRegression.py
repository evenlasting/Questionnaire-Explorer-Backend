import numpy as np
import pandas as pd
import statsmodels.api as sm

def linearRegression(sourceQuestionList,targetQuestion,hyper):
    source_data=hyper.survey_data.data_list
    data_type_isnum=hyper.survey_data.answer_type_isnum
    all_question_list=hyper.survey_data.all_question_list
    if all(isnum for isnum in [data_type_isnum[questionId] for questionId in sourceQuestionList]) and data_type_isnum[targetQuestion]:
        source_question_list=source_data[[all_question_list[index] for index in sourceQuestionList]]
        source_question_list=source_question_list.replace('no_answer',np.nan)
        target_question=source_data[all_question_list[targetQuestion]]
        target_question=target_question.replace('no_answer',np.nan)
        X = sm.add_constant(source_question_list)
        Y = target_question
        est=sm.OLS(Y,X,missing="drop")
        result=est.fit()
        coefficientList = list(result.params)
        return True,[coefficientList[1:],result.rsquared]
    else:
        return False,[0,0]
    

