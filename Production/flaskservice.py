#!/usr/bin/env python
# coding: utf-8

# ## Imports

# In[2]:


import logging
import os
import shutil
import numpy as np
import pandas as pd
import pickle
import statsmodels.api as sm
from datetime import datetime

from flask import Flask, request, jsonify
app = Flask(__name__)


# In[32]:


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("test")


# ## Variables

# In[33]:


file = "data.csv"
latest_pkl = "latest.pkl"


# ## Data Load/Transform

# In[34]:


def etl(file):
    df01 = pd.read_csv(file)
    df01['Transaction Date'] = pd.to_datetime(df01['Transaction Date'], infer_datetime_format=True)
    df01.rename(columns={'Transaction Date':'Transaction_Date'}, inplace=True)

    data = df01.drop(['Transaction_Date'], axis=1)
    data.index = df01.Transaction_Date

    data01 = data[(data["ATM Name"]==1)]
    data01 = data01.sort_index()

    train = data01.astype(np.float64)
    logging.info("ETL completed.")
    return train


# ## Train Model

# In[35]:


def VARMAX_Train_Model(train):
    exog = train[['Weekday','Festival Religion','Working Day','Holiday Sequence']]
    model= sm.tsa.VARMAX(train[['Total amount Withdrawn','Amount withdrawn XYZ Card']], order=(5,0), trend='c', exog=exog)
    model_result = model.fit(maxiter=1000, disp=False)
    logging.info("Model training completed.")
    return model_result


# ## Export Model

# In[36]:


def exportModel(model_result):
    import pickle 
    from datetime import datetime
    
    #latest time now
    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y-%H-%M-%S")
    
    filename = 'ATM_VARMAX01_' + timestamp + '.pkl'
    pickle.dump(model_result, open(filename, 'wb'))
    logging.info("Model exported.")
    
    return filename;

def handleNewVersion(latestFileName):
    try:
        os.remove('latest.pkl')
    except:
        logging.info("Existing latest.pkl not found. Proceeding...")
    
    newPath = shutil.copy(latestFileName, 'latest.pkl')
    logging.info("Latest pkl file updated.")
    return 0;


# ## Forecasting Function

# In[37]:


def forecast(Weekday,FestivalReligion,WorkingDay,HolidaySequence):
    # Use the loaded pickled model to make predictions 
    pkl_file = open(latest_pkl, 'rb')
    model_result = pickle.load(pkl_file) 
    params = []
#     test01 = test[['Weekday','Festival Religion','Working Day','Holiday Sequence']]
#     test01 = [[5.0,4.0,0.0,1.0]]
    test01 = [[Weekday,FestivalReligion,WorkingDay,HolidaySequence]]
    
    exog = test01
    pred = model_result.get_forecast(steps=1,exog=exog)
    pred_m = pred.predicted_mean
    logging.info("Prediction task completed.")
    
    totalAmount = pred_m["Total amount Withdrawn"] 
    XYZAmount = pred_m["Amount withdrawn XYZ Card"] 
    return [totalAmount,XYZAmount]


# ## Append New Data

# In[4]:


def appendNewData(newData):
    f= open(file,"a+")
    if(checkNewLine()):
        f.write(newData + '\n')
    else:
        f.write('\n' + newData + '\n')
    f.close()
    logging.info("Appended new row -> \n" + newData)
    return 0;

def checkNewLine():
    outcome = False
    with open(file, 'rb+') as f:
        f.seek(-1,2)
        lastByte = f.read().decode("utf-8")
    if(lastByte == '\n'):
        outcome = True
    return outcome


# ## Workflow

# In[38]:




# ## Helper Functions for Flask

# In[10]:


required_length = 4

def validateNewData(data):
    valid = False
    args = data.split(',')
    if(len(args)) == required_length:
        valid = True
    return valid


# ## Flask Routes and Operations

# In[12]:


# configure Flask routes

@app.route('/')
def index():
  return 'Flask service is up and running!'

@app.route('/addrow')
def addRow():
    data = request.args['data']
    appendNewData(data)
    return jsonify({"operation": "addrow"},{"status": "success"},{"data":data}), 200

@app.route('/updatemodel')
def updateModel():
	processed_data = etl(file)
	model_output = VARMAX_Train_Model(processed_data)
	latestFileName = exportModel(model_output)
	handleNewVersion(latestFileName)
	return jsonify({"operation": "updatemodel"},{"status": "success"}), 200
	
@app.route('/forecast')
def handleForecastRequest():
	Weekday = request.args['Weekday']
	FestivalReligion = request.args['FestivalReligion']
	WorkingDay = request.args['WorkingDay']
	HolidaySequence = request.args['HolidaySequence']
	
	output = forecast(float(Weekday),float(FestivalReligion),float(WorkingDay),float(HolidaySequence))
	return jsonify({"operation": "forecast"},{"status": "success"},{"predictedTotalAmount":float(output[0].values)},{"predictedXYZAmount":float(output[1].values)}), 200

