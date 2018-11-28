# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 15:42:50 2018

@author: o.richardson
"""

import nltk
import operator
from nltk.corpus import wordnet as wn 
lemmatizer=nltk.WordNetLemmatizer() 

#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')


mybigrams=[('red','wine'),('customer','service'),('personal','details')]
mytagfixes={('provide','n'):('provide','v')}
punctuation={'.',',',';','-',':'}
stops=set(nltk.corpus.stopwords.words('english'))
stops.update(punctuation)
#stemmer=nltk.PorterStemmer()

ch_grammar=r""" 
    CH: {<DT|PP\$>?<JJ.*>*<NN.*>+} 
    CH: {<V.*> <JJ.*>*<NN.*>+} 
    CH: {<V.*> <TO> <V.*>} 
    CH: {<N.*> <CC> <N.*>} 
    CH: {<NNP>+} 
        """ 
        
cp=nltk.RegexpParser(ch_grammar) 


def my_bigram_tokens(tokens): 
     bigs=list(nltk.bigrams(tokens)) 
     indices=[i for i,j in enumerate(bigs) if j in mybigrams] 
     indices=map(operator.sub, indices, (range(len(indices)))) 
     for index in indices: 
         tokens[index:index+2]=[(tokens[index]+' '+tokens[index+1])] 
     return tokens 

def override_tag(lemma,mytagfixes): 
     if lemma in mytagfixes: 
         lemma=mytagfixes[lemma] 
     return lemma 


def convert_tag_to_wordnet(brown_tag): 
     if brown_tag.startswith('J'): 
         return wn.ADJ 
     elif brown_tag.startswith('V'): 
         return wn.VERB 
     elif brown_tag.startswith('N'): 
         return wn.NOUN 
     elif brown_tag.startswith('R'): 
         return wn.ADV 
     else: 
         return 'X' 

def lemma_with_default(tagged_token,mytagfixes): 
     wntag=convert_tag_to_wordnet(tagged_token[1])
     #wntag=tagged_token[1]
     if wntag=='X': 
         lemma = lemmatizer.lemmatize(tagged_token[0])  
     else: 
         lemma = lemmatizer.lemmatize(tagged_token[0], pos=wntag) 
     q=(lemma.lower(),wntag) 
     return override_tag(q,mytagfixes) 

def get_synset(lemm_state): 
     if lemm_state[1] == 'X': 
         return wn.synsets(lemm_state[0]) 
     else: 
         return wn.synsets(lemm_state[0],lemm_state[1]) 
     
def get_condensed_synset(lemm_state): 
     if lemm_state[1] == 'X': 
         return lemm_state[0] 
     else: 
         return wn.synsets(lemm_state[0],lemm_state[1]) 

def remove_stops_puncs(word_tag,stops): 
     A=word_tag 
     z=list(i.lower() for (i,j) in A) 
     indices=[m for m,n in list(enumerate(z)) if n in stops] 
     for index in list(reversed(indices)): 
         del A[index]  
     return A 

def clean_chunks(chunk_state):
    outter=[]
    for count in range(len(chunk_state)):
        if chunk_state[count][2][0]=='B':
            inner=[chunk_state[count][0]] 
            if count+1==len(chunk_state): 
                outter.append(inner) 
                inner=[]
            elif chunk_state[count+1][2][0]=='O' or chunk_state[count+1][2][0]=='B': 
                 outter.append(inner) 
                 inner=[] 
        elif chunk_state[count][2][0]=='I':
            inner.append(chunk_state[count][0]) 
            if count+1==len(chunk_state):
                outter.append(inner) 
                inner=[]
            elif chunk_state[count+1][2][0]=='O' or chunk_state[count+1][2][0]=='B': 
                outter.append(inner) 
                inner=[] 
        else:
            chunk_state[count][2][0]=='O' 
            inner=[chunk_state[count][0]] 
            outter.append(inner) 
            inner=[]
    return outter 


def process_language(phrase):
    processedPhrase=list(my_bigram_tokens(nltk.word_tokenize(phrase)))
    processedPhrase=list(nltk.pos_tag(processedPhrase))
    #lemmas=list([lemma_with_default(T,mytagfixes) for T in processedPhrase])
    chunks=clean_chunks(list(nltk.tree2conlltags(cp.parse(processedPhrase))))
    processedPhrase=remove_stops_puncs(processedPhrase,stops)
    
    lemmas=list([lemma_with_default(T,mytagfixes) for T in processedPhrase])
    #synons=list([get_synset(lemm) for lemm in lemmas])
    #return {'keywords':processedPhrase, 'lemmas':lemmas, 'synsets':synons}
    return {'keywords':processedPhrase,'short_chunks':chunks}
    #antonyms?


    
    #processedPhrase=list(lemma_with_default(T,mytagfixes) for T in processedPhrase)


#phrase="I want to change the personal details on my account I want to change my subscription"
#diction=(phrase_to_synomymous_lemmas(phrase))


#Clean_Chunks=list(mn.clean_chunks(c,n) for n,c in enumerate(Chunk_States)) 
#Chunk_Strings=list(mn.make_strings(c) for c in Clean_Chunks) 
