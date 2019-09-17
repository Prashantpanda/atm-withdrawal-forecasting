#!/usr/bin/env python
# coding: utf-8

# ## Variables

# In[10]:


file = "data.csv"
latest_pkl = "latest.pkl"


# ## Imports

# In[6]:


def doImports():
    import logging
    import os
    import shutil
    import pandas as pd
    import numpy as np
    import pickle


# ## Data Load/Transform

# In[8]:


def etl(file):
    df01 = pd.read_csv(file)
    df01['Transaction Date'] = pd.to_datetime(df01['Transaction Date'], infer_datetime_format=True)
    df01.rename(columns={'Transaction Date':'Transaction_Date'}, inplace=True)

    data = df01.drop(['Transaction_Date'], axis=1)
    data.index = df01.Transaction_Date

    data01 = data[(data["ATM Name"]==1)]
    data01 = data01.sort_index()

    train = data01.astype(np.float64)
    return train


# ## Train Model

# In[ ]:


def VARMAX_Train_Model(train):
    exog = train[['Weekday','Festival Religion','Working Day','Holiday Sequence']]
    model= sm.tsa.VARMAX(train[['Total amount Withdrawn','Amount withdrawn XYZ Card']], order=(5,0), trend='c', exog=exog)
    model_result = model.fit(maxiter=1000, disp=False)
    return model_result


# ## Export Model

# In[ ]:


def Persist_M(model_result):
    import pickle 
    from datetime import datetime
    
    #latest time now
    dateTimeObj = datetime.now()
    
    timestamp = "dateTimeObj"
    filename = 'ATM_VARMAX01_' + timestamp + '.pkl'
    pickle.dump(model_result, open(filename, 'wb'))
    
    return filename;

def handleNewVersion(latestfileName):
    os.remove('latest.pkl')
    newPath = shutil.copy(latestfileName, 'latest.pkl')


# ## Forecasting Function

# In[ ]:


def VARMAX_f(train):
    # Use the loaded pickled model to make predictions 
    model_result = pickle.loads(latest_pkl) 
    test01 = test[['Weekday','Festival Religion','Working Day','Holiday Sequence']]
    exog = test01
    pred = model_result.get_forecast(steps=1,exog=exog)
    pred_m = pred.predicted_mean
    return pred_m

