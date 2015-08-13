# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 12:20:59 2015

@author: lliu5
"""
from get_data_breast import checkAllcancer,get_section
from flask import Flask,request,render_template
from flask_restful import Resource,Api,reqparse
import json
import traceback
from confidence_value import getScore
from confidence import keydb_marginal_load,keydb_marginal_newkey,keydb_clean
app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return render_template('home.html')
@app.route('/confidence')
def confidence():
    return render_template('confidence.html')
    

@app.route('/cleaner')
def cleaner():
    return render_template('cleaner.html')

@app.route('/note',methods=['GET', 'POST'])
def Extract():
    #print request.form
    args = parser.parse_args()
    note = args['data']
    if note == None:
        note = request.form.get('data')
    if note == None:
        return 'No info'
    else:
        result = {}
        try:
            result = checkAllcancer(note)
            result_confidence= result.copy()
            for cancer in result.keys():
                marginaldbname = cancer.split()[0].lower()+'.data'
                print 'marginaldbname: ',marginaldbname
                               
                marginaldb = keydb_marginal_load(marginaldbname)
                ########################################
                # the below code is for getting confidence score. 
                #########################################                
                for k,v in result[cancer].items():
                    #note that v is a list contains value and original value. 
                    value = v[0]
                    #now we can do value processing. 
                    #put your code here
                    
                    #now we can do key confidence processing. 
                    #it needs a library indicating which unverse it belongs to. 
                    #in here we will just try to use our pre-existing libraries. 
                    #namely, if you have breast cancer as cancer, then
                    #your splited cancer will have the name as the first value. 
                    
                    result_confidence[cancer][k].append(keydb_marginal_newkey(value,marginaldb))
                    value_score = getScore(k,value,keydb_marginal_load('Valdb.data'))
                    result_confidence[cancer][k].append(' '.join([str(item) for item in value_score.values()]))
                
            result['specimens']=get_section(note)
        except Exception, err:
            print '*'*80
            print err
            print traceback.format_exc()
        return json.dumps(result)
    print '*'*80,'note','['+str(note)+']'
    if request.method == 'POST':
        return 'post method received'
            
    return 'extraction in progress'    
parser =reqparse.RequestParser()
parser.add_argument('data')

if __name__=='__main__':
    app.run(debug=True)
