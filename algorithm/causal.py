from pycausal import prior as p
import re

def solve_causal(pc,tetrad,df,r,f,temp):
    
    import sys,os
    sys.stdout = open(os.devnull, 'w')
    pc.start_vm()
    print('rf------------------------------------',r,f)
    prior=p.knowledge(requiredirect = r,forbiddirect=f,addtemporal=temp)
    tetrad.run(algoId = 'fges',  dfs = df,dataType='mixed', 
            priorKnowledge = prior, maxDegree = 3, faithfulnessAssumed = True, 
            symmetricFirstStep = True, verbose = True,# penaltyDiscount=0.5,
            numberResampling = 5, resamplingEnsemble = 1)
    edges=tetrad.edges
    nodes=tetrad.getTetradGraph().getNodes()
    edges_ans=[]
    for i in edges:
        edge_part=re.match('.*?\[',i).group()[:-2]# -2 means delete ' [' in '13 --> 5 [13 --> 5]:0.4545;[13 <-- 5]:0.1818;[no edge]:0.3636;'
        i_arr=edge_part.split(' --> ')
        if (len(i_arr)>1):
            score_all=[float(x[1:-1]) for x in re.findall(':\d+\.?\d*;',i)]
            score=max(score_all)
            edges_ans.append({'target':int(i_arr[1]),'source':int(i_arr[0]),'score':score})
        i_arr=edge_part.split(' --- ')
        if (len(i_arr)>1):
            score_all=[float(x[1:-1]) for x in re.findall(':\d+\.?\d*;',i)]
            score=max(score_all)
            edges_ans.append({'target':int(i_arr[1]),'source':int(i_arr[0]),'score':score/2})
    ans={
        'nodes':list(map(lambda x:int(x),tetrad.nodes)),
        'links':edges_ans
    }
    return ans