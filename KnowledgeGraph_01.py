# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import py2neo as py2
import pandas as pd
import numpy as np
import os

### data process

ontol=os.path.expanduser("~\Documents\KnowledgeGraph\MockOntology1.csv")
ontol=pd.read_csv(ontol,encoding='latin-1')

### talk to Neo4j 
 
 
py2.authenticate("127.0.0.1:7474", user='neo4j',password='_tXui58_1') 
gr = py2.Graph("http://127.0.0.1:7474/db/data")  

#institutions=colleges.Institution.unique()
#states=colleges.State.unique()


# Choose a dataframe and define a graph schema
df=ontol
node_types=['Module','Class','Object','Property']
#join_types=[['in','classified',False],[False,False,False],[False,False,False]] 

# Reset
gr.delete_all() 

# Make Nodes
tx = gr.begin() 
for nt in node_types:
    for num,item in enumerate(df[nt].unique()): 
        string="CREATE (n:"+nt+"{ref:{ref},name:{name}})"
        tx.evaluate(string,ref=num,name=item) 
tx.commit()

modules=set(df['Module'])
classes=list(set(df['Class']))
objects=set(df['Object'])
properties=set(df['Property'])




# Make Joins
#Ad hoc joins for presentation
tx=gr.begin()
a=py2.Node('Module',ref=0)
tx.merge(a)
for i,j in enumerate(classes):
    b=py2.Node('Class',ref=i) 
    tx.merge(b)
    ab=py2.Relationship(a,'on',b) 
    tx.create(ab) 
tx.commit()


tx=gr.begin()
a=py2.Node('Class',ref=0)
tx.merge(a)
for i in range(len(objects)-1):
    b=py2.Node('Object',ref=i) 
    tx.merge(b)
    ab=py2.Relationship(a,'on',b) 
    tx.create(ab) 
tx.commit()

tx=gr.begin()
a=py2.Node('Object',ref=0)
tx.merge(a)
for i in range(2):
    b=py2.Node('Property',ref=i) 
    tx.merge(b)
    ab=py2.Relationship(a,'Change',b) 
    tx.create(ab) 
tx.commit()

tx=gr.begin()
a=py2.Node('Object',ref=0)
tx.merge(a)
for i in range(2):
    b=py2.Node('Property',ref=i) 
    tx.merge(b)
    ab=py2.Relationship(a,'Check',b) 
    tx.create(ab) 
tx.commit()


# schematic joins, requires join_types (line 30)
tx=gr.begin() 
for p in range(len(node_types)-1):
    first_node=node_types[p]
    for q in range(len(node_types)-1):
        second_node=node_types[q+1]
        if join_types[p][q]:
            for num,item in enumerate(df[first_node].unique()): 
                 a=py2.Node(first_node,ref=num) 
                 tx.merge(a) 
                 neighbour_of_a=df[second_node].iloc[num]
                 try:
                     b=py2.Node(second_node,ref=int(np.where(df[second_node].unique()==neighbour_of_a)[0])) 
                 except (TypeError,ValueError):
                     pass
                 tx.merge(b) 
                 ab=py2.Relationship(a,join_types[p][q],b) 
                 ab
                 tx.create(ab) 
tx.commit()




pswd=getpass.getpass(prompt='Password: ')

