# -*- coding: utf-8 -*-
"""
for each sub-element (e.g. chunk) in the universe of processed of ontology leaf strings,
    TF: [count the occurence of the sub-element in the input string / total number of sub-elements in the input string]
    IDF: log[total number of leaf strings in the ontology / number of leaf strings that contain the sub-element]
    TFIDF=TF*IDF
OUTPUT: a vector of TFIDF, each scalar value is the TFIDF for one unique sub-element from the ontology 
"""
import math
import numpy as np
from scipy import spatial

def softmax(x):
    v=np.exp(x)/np.sum(np.exp(x),axis=0)
    return v

def cosine_distance(u,v):
    d=1-spatial.distance.cosine(u,v)
    if np.isnan(d):
        return 0
    else:
        return d
        

def tfidf(processed_input_string,processed_ontology_leaf_strings):
    universe=[]
    for i in range(len(processed_ontology_leaf_strings)):
        for j in range(len(processed_ontology_leaf_strings[i])):
            universe.append(list(processed_ontology_leaf_strings[i][j]))
    universe=list(set(map(tuple,universe)))
    TF=np.zeros(len(universe))
    IDF=np.zeros(len(universe))
    N=len(processed_ontology_leaf_strings)
    for index,i in enumerate(universe):
        count1=0
        count2=0
        for j in processed_input_string:
            if j==i:
                count1+=1
        for k in processed_ontology_leaf_strings:
            for m in k:
                if (m==i):
                    count2+=1
        TF[index]=count1/len(processed_input_string)
        IDF[index]=math.log(N/count2)
    return (TF*IDF)

def ontology_fvs(processed_ontology_leaf_strings):
    out=list(tfidf(i,processed_ontology_leaf_strings) for i in processed_ontology_leaf_strings)
    return out


def liklihood(processed_input_string,o_fvs,candidate_mask,processed_ontology_leaf_strings):
    feature_vector=tfidf(processed_input_string,processed_ontology_leaf_strings)
    #co_d=candidate_mask['Liklihood']
    for i,item in enumerate(o_fvs):
        candidate_mask.loc[i,'Liklihood']=cosine_distance(item,feature_vector)
    candidate_mask['Liklihood']=softmax(np.array(candidate_mask['Liklihood']))
    return candidate_mask, True

def prob(dataLemmas,o_fvs,cand_adj,ontology):
    feature_vector=tfidf(dataLemmas,ontology)
    for i,item in enumerate(o_fvs):
        cand_adj.loc[i,'Prob']=cosine_distance(item,feature_vector)
    cand_adj['Prob']=softmax(np.array(cand_adj['Prob']))
    return cand_adj

test_dict = {'I would like to check the amount and due date on my account': [1,0,0,0,0,0,0,0,0,0,1,1],
             'I want to change my address': [0,0,0,0,1,0,0,0,0,0,0,0],
             'Both': [0,0,0,0,0,1,1,0,0,0,0,0],
             'both': [0,0,0,0,0,1,1,0,0,0,0,0],
             'my home address':[0,0,0,0,0,1,0,0,0,0,0,0],
             'my billing address':[0,0,0,0,0,0,1,0,0,0,0,0],
             'I want to check my personal details':[0,0,1,0,0,0,0,0,0,0,0,0],
             'I want to check my personal details and discuss my subscription':[0,0,1,1,0,0,0,0,0,0,0,0],
             'can I change the type?':[0,0,0,0,0,0,0,0,0,1,0,0]}


def test(cand_adj,customer):
    cand_adj['Prob']=softmax(test_dict[customer])
    return cand_adj

def null(cand_adj):
    cand_adj['Prob']=0
    return cand_adj
"""

an input sentence is judged 'similar' to a concept if the cosine similarities of their respective vectors is large.


INPUTS
ontology: format is list(processed_language(ontology_leaves))
input_phrase: (chunked): format is list(processed_language(input))


"""




        