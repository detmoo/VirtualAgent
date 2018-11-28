# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 16:18:07 2018

@author: o.richardson
"""

import os
import pandas as pd
import numpy as np
import kgNLP as kgl
import nltk

def processed_onto(ontology_path):
    O=os.path.expanduser(ontology_path)
    O=pd.read_csv(O,encoding='latin-1')
    lang=list(map(kgl.process_language,O['Description']))
    lang_lemmas=[]
    lang_chunks=[]
    for i in range(len(lang)):
        lang_lemmas.append(lang[i][0])
        lang_chunks.append(lang[i][1])
    L=pd.DataFrame(lang_lemmas)
    L['3']=lang_chunks
    o_tree=O[['Module','Class','Object','Property','Method']]
    o_tree['Liklihood']=np.ones(len(o_tree))
    return lang_lemmas, o_tree


def processed_adj(ontology_path):
    O=os.path.expanduser(ontology_path)
    O=pd.read_csv(O,encoding='latin-1')
    O.set_index('Index')
    lang=list(map(kgl.process_language,O['Description']))
    lang_lemmas=[]
    lang_chunks=[]
    for i in range(len(lang)):
        lang_lemmas.append(lang[i][0])
        lang_chunks.append(lang[i][1])
    L=pd.DataFrame(lang_lemmas)
    L['3']=lang_chunks
    return lang_lemmas, O


class node:
    def __init__(self,name,actions="all",adjacent_candidates=1,category='default'):
        self.name=name
        self.actions=actions
        self.a_c=adjacent_candidates
        self.category=category
    def Choose(self,a_c,Nodes,action):
        choices=[]
        k=0
        for i,j in enumerate(a_c):
            if j:
                choices.append(Nodes[i].name)
                choices.append(' or ')
                k+=1
        if k!=0:
            choices=choices[:-1]
        if k==0:
            choices='nothing'
        print("\n")
        print('Regarding your '+self.name)
        print('You can '+action)
        print(choices)
        return choices
    def Action(self,targetRecord,act='check',switch=True):
        print("\n")
        if act=='check':
            targetRecord.GetData(self.name)
        elif act=='change':
            targetRecord.Update(self.name)
        elif act=='discuss':
            if switch:
                print('Regarding your '+self.category)
                switch=False
            targetRecord.GetData(self.name)
        else:
            print('misunderstood')
        return switch
                

        
class record:
    def __init__(self,name,database,data={}):
        for leaf in database.index:
            data.update({leaf:database.loc[leaf,'Value']})#[0]
        self.name=name
        self.data=data
    def GetData(self,node_name):
        print('The '+node_name+' of your '+self.name+' is '+self.data[node_name])
    def Update(self,node_name):
        self.GetData(node_name)
        print("\n")
        print('Enter the new '+node_name)
        self.data[node_name]=str(input('New '+node_name+': '))


def build_nodes(cand_adj):
    cols=cand_adj['Index']
    adjs=[]
    for count,name in enumerate(cols):
        adj=list(cand_adj.iloc[count][cols])
        adjs.append(node(name,"all",adj,cand_adj['Category'][count]))
    return adjs

def create_record_objects(customer_record):
    records=[]
    for cat in set(customer_record['Cat']):
        records.append(record(cat,customer_record[customer_record['Cat']==cat],data={}))
    df=pd.DataFrame([])#,columns={'Records'})
    df['Records']=records
    q=[]
    for i in range(len(records)):
        q.append(records[i].name)
    df['Index']=q
    df=df.set_index(['Index'])
    return df
    

def findroot(candidate_nodes,net):
    those=candidate_nodes.loc[candidate_nodes['Liklihood'].nlargest(net).index.values,:]
    if len(set(those['Class']))==1:
        root=2
    elif len(set(those['Module']))==1:
        root=1
    else:
        root=0
    return root, those

    

def navigate(cand_adj,navigate,itinerary):
    oldNavigate=navigate
    actProb=np.array([cand_adj['Prob']>cand_adj['Prob'].mean()])
    if all(n==False for n in actProb[0]) and oldNavigate.empty and itinerary.empty:
        actProb[0][0]=True
        return 
    probMaxes=cand_adj.groupby('Category')['Prob'].max()
    actLevel=[]
    for i,j in enumerate(cand_adj['Category']):
        if cand_adj['Prob'][i]==probMaxes.loc[j] and cand_adj['Active'][i]==False:
            actLevel.append(True)
        else:
            actLevel.append(False)
    actLevel=np.array(actLevel)
    cand_adj['Status']=pd.Series(actLevel*actProb[0])
    if sum(cand_adj['Status'])>1 or sum(cand_adj['Active'])>0:
        cand_adj.loc[0,'Status']=False
    normal=cand_adj['Prob'][cand_adj['Status']==True].sum()
    if normal>0:
        cand_adj['Status']=cand_adj['Prob']*cand_adj['Status']/normal
    navigate=cand_adj[cand_adj['Status']>0]
    if not(oldNavigate.empty) and not(navigate.empty):
        navigate=oldNavigate.append(navigate)
    elif not(oldNavigate.empty):
        navigate=oldNavigate
    navigate=navigate.sort_values('Prob')
    navigate=navigate[~navigate.index.duplicated(keep='first')]
    return cand_adj,navigate 
    

def active_state(cand_adj,itinerary):
    oldItinerary=itinerary
    actProb=np.array([cand_adj['Prob']>cand_adj['Prob'].mean()])
    levelMaxes=cand_adj.groupby('Category')['Level'].max()
    actLevel=[]
    for i,j in enumerate(cand_adj['Category']):
        if i==0:
            actLevel.append(False)
        elif cand_adj['Level'][i]==levelMaxes.loc[j]:
            actLevel.append(True)
        else:
            actLevel.append(False)
    actLevel=np.array(actLevel)
    cand_adj['Active']=pd.Series(actLevel*actProb[0])
    if sum(cand_adj['Active'])>1:
        cand_adj.loc[0,'Active']=False   
    normal=cand_adj['Prob'][cand_adj['Active']==True].sum()    
    if normal>0:
        cand_adj['Active']=cand_adj['Prob']*cand_adj['Active']/normal
    itinerary=cand_adj[cand_adj['Active']>0]
    if not(oldItinerary.empty) and not(itinerary.empty):
        itinerary=oldItinerary+itinerary
    elif not(oldItinerary.empty):
        itinerary=oldItinerary
    itinerary=itinerary.sort_values('Prob')
    return cand_adj,itinerary    
    

def what_action(customer):
    act=[]
    if any(n=='check' for n in nltk.word_tokenize(customer)):
        act.append('check')
    if any(n=='change' for n in nltk.word_tokenize(customer)):
        act.append('change')
    if any(n=='discuss' for n in nltk.word_tokenize(customer)):
        act.append('discuss')
    return act