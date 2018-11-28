# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Wed Feb 28 09:44:25 2018

@author: o.richardson
"""

"""
Main script for the KG Virtual Agent PoC

SETUP

(1) Save modules kgNLP, ontology and similarity_measures into a local directory
(2) Set variables:
    localdir: the local directory where modules kgNLP, ontology and similarity_measures are saved
    data_location: file path for customer data modelled as per the ontology (note Name and Category)
    ontology_location: file path for the ontology (note Name and Category)
    test: if test==True the script takes test cases from similarity_measures and otherwise performs the full NLP stage
    

"""
############################################ SET VARIABLES
localdir='C:\\repos\knowledgegraph\kg_runtime'
data_location="C:\\repos\knowledgegraph\data\Database2.csv"
ontology_location="C:\\repos\knowledgegraph\data\MockOntology4.csv"
test=True

############################################


import os
os.chdir(localdir)
import kgNLP as kgl
import ontology as onto
import similarity_measures as similarity
import pandas as pd
import argparse
# the first time of running with test=False will require nltk resources
#nltk.download('punkt')
#nltk.download('stopwords')



parser = argparse.ArgumentParser()
parser.add_argument('--flag',default=1,type=int,help='...')


# call to the NLP layer. customer is latest input utterance, dataLemmas & dataChunks are the processed data
def combine_data(customer,dataLemmas,dataChunks):
    l,c=kgl.process_language(customer)
    for i in l:
        dataLemmas.append(i)
    dataLemmas=list(set(dataLemmas))
    for i in c:
        dataChunks.append(i)
    dataChunks=[list(x) for x in set(tuple(x) for x in dataChunks)]
    return dataLemmas,dataChunks

        

def A(customer,ontology,o_fvs,cand_adj,record_objects,itinerary=pd.DataFrame([]),navigate=pd.DataFrame([]),action=False,test=True,flag='top'):
    # obtain a probability of the customer referring to each of the nodes in the ontology
    if customer=='exit':
        return
    if customer==[]:
        cand_adj=similarity.null(cand_adj)
    elif test:
        cand_adj=similarity.test(cand_adj,customer)
    else:
        dataLemmas,dataChunks=combine_data(customer,dataLemmas,dataChunks)
        cand_adj=similarity.prob(dataLemmas,o_fvs,cand_adj,ontology)
        
    # cand_adj is a dataframe representing the ontology and the probilities from above. 
    # Here two states are set, the Active column defines the itinerary of services the client requires
    # the status column identifies nodes that are candidate to add to itinerary but where further customer input is needed    
    cand_adj,itinerary=onto.active_state(cand_adj,itinerary)
    cand_adj,navigate=onto.navigate(cand_adj,navigate,itinerary)
    if not(action):
        action=onto.what_action(customer)

    # carry out the actions on the itinerary
    while not(itinerary.empty):
        act=action[0]
        switch=True
        for i in range(len(itinerary)):
            for k,j in enumerate(record_objects['Records']):
                if j.name==itinerary.iloc[i]['Category']:
                    target=j
                    continue
            switch=itinerary.iloc[i]['Nodes'].Action(target,act,switch)
        action=action[1:]
        itinerary=pd.DataFrame([])            

    # organise the candidate nodes and navigate the ontology to generate a prompt consistent with whatever additional information is required to move them to itinerary    
    while not(navigate.empty):
        act=action[0]
        if navigate.iloc[0]['Index']==navigate.iloc[0]['Category']:
            leafLevel=cand_adj[cand_adj['Category']==navigate.iloc[0]['Category']]['Level'].max()
            do_these_instead=cand_adj[cand_adj['Category']==navigate.iloc[0]['Index']]
            do_these_instead=do_these_instead[do_these_instead['Level']==leafLevel]
            if not(itinerary.empty):
                itinerary=do_these_instead+itinerary
            else:
                itinerary=do_these_instead
            customer=[]
        else:
            navigate.iloc[0]['Nodes'].Choose(navigate.iloc[0]['Nodes'].a_c,cand_adj['Nodes'],act)
            customer=str(input('You: '))
        navigate=navigate[1:]
        flag, navigate, itinerary=A(customer,ontology,o_fvs,cand_adj,record_objects,itinerary,navigate,action,test=True,flag='sub')
    return flag, navigate, itinerary


    ###################################

def main():
    
    customer_record=data_location
    customer_record=pd.read_csv(customer_record,encoding='latin-1')
    customer_record=customer_record.set_index('Index')
    record_objects=onto.create_record_objects(customer_record)
    
    ontology_path=ontology_location
    ontology,cand_adj=onto.processed_adj(ontology_path)
    cand_adj['Nodes']=onto.build_nodes(cand_adj)
    o_fvs=similarity.ontology_fvs(ontology)
    k=1
    while k<12:
        customer=str(input('Hello, how can I help?: '))
        if customer=='exit':
            break
        flag,navigate,itinerary=A(customer,ontology,o_fvs,cand_adj,record_objects,itinerary=pd.DataFrame([]),navigate=pd.DataFrame([]),action=[],test=True,flag='top')
        if flag=='top':
            k+=1
            
        
    args = parser.parse_args()
    result=args.flag
    with open("Output.txt", "w") as text_file:
        print((str(result)), file=text_file)


#########################################
if __name__=='__main__':
    main()
    
    

