# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from collections import defaultdict
import re
import numpy as np
from file_utilities import dict_add
from nltk.corpus import wordnet as wn
#
#def collectValue(inputDict):
#    value = defaultdict(list)
#    for k,v in inputDict.iteritems():
#        for k2,v2 in v.iteritems():
#            if k2!='content':
#                for k3,v3 in v2.iteritems():
#                    value[k3].append(v3[0])
#    return value
#
#    
#val = collectValue(result)

def Syn_Ant(word):
    syn = []
    an = {}
    for i in wn.synsets(word):
        for j in i.lemmas():
            syn.append(j.name())
            if j.antonyms():
                an[j.name()]=j.antonyms()[0].name()
    syn = list(set(syn))
    return syn,an
    
def valdb_destroy(dbName):
    '''
    This function destroys the given file. 
    Args:
        dbName: string of db file location
    Returns: 
        None
    '''
    import os,os.path
    if os.path.exists(dbName):
        os.remove(dbName)
        print 'db destroy',dbName,'succesful'
    else:
        print 'db destroy',dbName,'unsuccessful -- db not found'
        

def valdb_add(dbVal,dbName = 'Valdb.data'):
    import os.path,pickle
    if os.path.exists(dbName):
        db = pickle.load(open(dbName,'r'))
    else:
        db = {}
       
   
    db = dict_add(db,dbVal)

    pickle.dump(db,open(dbName,'w'))
#    print 'added to db: ',dbName
    return db

def valdb_wordcount_add(dbVal_wordcount,dbName = 'Valdb_wordcount.data'):
    import os.path,pickle
    if os.path.exists(dbName):
        db = pickle.load(open(dbName,'r'))
    else:
        db = []
       
   
    db = db + dbVal_wordcount

    pickle.dump(db,open(dbName,'w'))
#    print 'added to db: ',dbName
    return db

def getCount(v,lenCutoff = 0.8):
    label = ['total','num','num_text','text','num_text_short','num_text_long']        
    if v not in label:
        label.append(v)
        
    countDict = dict.fromkeys(label, 0)
    countDict['total']=1
    countDict[v]=1
    # process Type feature
    if bool(re.search(r'\d', v)):
        if bool(re.search(r'[a-z]',v.lower())): 
            countDict['num_text']=1
        else:
            countDict['num']=1
    else:
        countDict['text']=1
        
    # process Length feature (lenth of text in num_text)
    if countDict['num_text']==1:
        s = ''.join([i for i in v if not i.isdigit()])
        if len(s)/len(v)>lenCutoff:
            countDict['num_text_long']=1
        else:
            countDict['num_text_short']=1
    return countDict
    
def getWordcount(countdict,v):
    # process Wordcount feature
    wordcount = []
    if countdict['text']==1:
        v = v.split(" ")  
        wordcount.append(len(v))         
        
    return wordcount      

def getScore(v,dbVal,dbVal_wordcount,countdict):
    score = {}
    # Type feature: calculate proportion of a particular type of v with respect to the total frequency
    score['Type'] = float((countdict['num']*dbVal['num'] + countdict['num_text']*dbVal['num_text'] + countdict['text']*dbVal['text']))/float(dbVal['total'])
  
    # Length feature: only apply to num_text type (let score of other types to be 1)
    # calculate proportaion of long or short text with respect to total number of num_text type
    if countdict['num_text']==1:
        score['Length'] = float((countdict['num_text_long']*dbVal['num_text_long'] + countdict['num_text_short']*dbVal['num_text_short']))/float(dbVal['num_text'])
    else:
        score['Length'] = 1
    
    c = np.array(dbVal_wordcount) # c is a vector of word count
    dbVal_wordcount.sort()
    med = dbVal_wordcount[len(dbVal_wordcount)/2] # median of a vector containing word count
    # If std.dev(c) which is the denominator is not 0, calculate the score 
    # score = absolute value of (word count for v - med and then divided by std.dev of c)
    if c.std()!=0:
        score['Wordcount']=abs(float((len(v.split(" "))-med))/float(c.std()))
    # If std.dev(c) is 0: 
    #   check if word count of v is equal to med then set score to 0 (good case)
    #   otherwise, set score to be 100 (bad case)
    else: 
        if len(v.split(" "))==med:
            score['Wordcount']=0
        else:
            score['Wordcount'] = 100
            
    label = ['total','num','num_text','text','num_text_short','num_text_long']
    # token of v 
    token = list(set(dbVal.keys())-set(label))
    token_combine = {}   # combine synonym and antonym with original word
    for k in token:       
        flag = 0
        syn,an = Syn_Ant(k)
        # If any item in token is synonym or antonym of k, combine frequency and remove that word from the token list.
        # Collect the new frequency in a token_combine dictionary
        for s in syn:
            if str(s) in token and str(s)!=k:
                token_combine[k]=dbVal[k]+dbVal[str(s)]
                token.remove(str(s))
                flag = 1
        for key,val in an.iteritems():
            if str(val) in token:
                token_combine[k]=dbVal[k]+dbVal[str(val)]  
                token.remove(str(val))
                flag = 1
        # If there is no synonym or antonym of k contained in token list, collect the frequency from dbVal
        if flag==0:
            token_combine[k]=dbVal[k]
    
    # Calculate the score for each element in the original token list
    for k in list(set(dbVal.keys())-set(label)):     
        if k==v:    
            # If v is antonym of k, collect combined frequency
            if v in an.itervalues():
                for key,val in an.iteritems():
                    if str(val)==v:
                        num_token = token_combine[key]
            else:
                num_token = token_combine[v]
            
            eq_portion = float(1)/float(len(token_combine))
            percentage = float(num_token)/float(dbVal['total'])
            score['Token'] = float(percentage-eq_portion)
        
           
    return score    

def valdb_add_result(val):
    dbVal = {}
    dbVal_wordcount = []
    score = defaultdict(list)
      
    i=0
    while i<len(val):
        v = val[i]        
        # get frequency count (multiple values of them) for value v and add to database dbVal
        countdict = getCount(v)
        dbVal = valdb_add(countdict)
        # get wordcount for value v and add to database dbVal_wordcount
        dbVal_wordcount = valdb_wordcount_add(getWordcount(countdict,v))
        score[i] = getScore(v,dbVal,dbVal_wordcount,countdict)
        i+=1
      
    
    return dbVal,dbVal_wordcount,score
            
if __name__ == '__main__':
    # val is a list of value corresponding to each key
    valdb_destroy('Valdb.data')    
    valdb_destroy('Valdb_wordcount.data')
    val = ['yes','no','yes','no','accept2','not accept'] #just for testing
    dbVal,dbVal_wordcount,score = valdb_add_result(val)
    
    '''
     score detail:
     Type:       [0,1] the larger, the better
     Length:     [0,1] the larger, the better
     Wordcount:  [0, ] the smaller, the better
     Token:      [-, ] the larger, the better
    '''
    
        