# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 10:35:26 2015

@author: pwongcha
"""
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
from confidence import keydb_marginal_load
from collections import defaultdict
st = LancasterStemmer()


def sortKey(keydata):
# collect and sort keydata (in a tuple and string format)
    tup = []
    string = []
    singleToken = []
    for k in keydata.keys():
        if type(k)==tuple:
            if len(k)==1:
                singleToken.append(k[0])
            s = ''
            for k2 in k:
                s = s+k2+"+"
            tup.append(k)
            string.append(s)
        else:
            del keydata[k]
                
    tup = sorted(tup)
    string = sorted(string)
    return tup,string,singleToken

def similarKey(tup,threshold = 0.1):
    # find similar keys based on distance between two keys (after applying stemming to each token)
    # threshold = distance threshold to determine the similarity
    simstring = {}
    simorder = {}
    i=0
    while i<len(tup):
    #    print i
        s_orig_list = []
        j_list = []
        key = tup[i]
        s_curr_orig = ''
        s_curr = ''
        for k in key:
            s_curr_orig = s_curr_orig+k+"+"
            s_curr = s_curr+st.stem(k)+"+"
        j=i+1
        while j<len(tup):
            key2 = tup[j]
            s_orig = ''
            s = ''
            for k2 in key2:
                s_orig = s_orig+k2+"+"
                s = s+st.stem(k2)+"+"
            lev = nltk.metrics.distance.edit_distance(s_curr,s)
            avg = np.mean([len(s_curr),len(s)])
            distance = float(lev)/float(avg)
            if distance<threshold:
                s_orig_list.append(s_orig)
                j_list.append(j)
            j+=1
            simstring[s_curr_orig] = s_orig_list
            simorder[i] = j_list
        if i==len(tup)-1:
            simstring[s_curr_orig] = s_orig_list
            simorder[i] = j_list
        i+=1
    return simstring,simorder

def combineKey(keydata,simorder):
    # combine value for similar key (the distance is between two keys are small)
    combine_key = {}
    i = 0
    while i<len(tup):
    #    print i
        if simorder[i]!=[]:
            keydata[tup[i]] = int(keydata[tup[i]]) + int(keydata[tup[simorder[i][0]]])
            keydata[tup[simorder[i][0]]] = "NA"
    
        i+=1
    return combine_key

def cleanKey(singleToken,keydata):
    clean_key = {}
    equivalent_key = {}
    
    for item in singleToken:
        eq_key_list = []
        base_token = defaultdict(list)
        for t in tup:
            if item in t and keydata[t]!="NA":
                base_token[keydata[t]].append(t)
        for k,v in base_token.items():
            # k is frequency and v is a list of tuples
            max_len = 0
            # find the final key that has the longest length among same frequency ones
            for sub_v in v:
                if len(sub_v)>max_len:
                    max_len = len(sub_v)
                    final_key = sub_v
            # collect equivalent key (same frequency) but not the final key in eq_key_list 
            for sub_v in v:
                if sub_v!=final_key:
                    eq_key_list.append(sub_v)
            # add eq_key_list to equivalent_key dictionary 
            # clean key is the dictionary that collects the final key and its frequency
            equivalent_key[final_key] = eq_key_list
            clean_key[final_key] = k
    return clean_key,equivalent_key
            
if __name__ == '__main__':
    # load key frequency data (tuples of elements in key)
    keydata = keydb_marginal_load('breast.data')
    keydata_orig = keydb_marginal_load('breast.data') # keydata_orig is just for checking (not used)
    # string is just for checking/debugging (not used)
    tup,string,singleToken = sortKey(keydata)
    simstring,simorder = similarKey(tup)
    combine_key=combineKey(keydata,simorder)
    clean_key,equivalent_key = cleanKey(singleToken,keydata)
      
        
    



        
       



        