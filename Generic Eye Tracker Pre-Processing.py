#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
import os,re
import hdf5_csv_conversion as h5
from sklearn import preprocessing
pd.options.mode.chained_assignment = None


# In[5]:


# You will want this script to be in some sort of PATH/study/analysis folder
cur_dir = os.getcwd()
print(cur_dir)


# In[6]:


# You will want your data to be in some sort of PATH/study/logs folder (change it to whatever you like below)
rootdir = os.path.dirname(cur_dir) 
rootdir = os.path.join(rootdir,"logs")
print(rootdir)


# In[7]:


# You will need the hdf5_csv_conversion.py script. This script does the heavey lifting and converts your hdf5 files to 4 csvs

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if(re.search(".*\.hdf5$",file)):
            print(os.path.join(subdir, file))
            input_dummy = os.path.join(subdir, file)
            output_dummy = os.path.join(subdir,"dummy")
            h5.convert_hdf5(input_dummy,output_dummy)


# In[8]:


def data_cleanup(data):
    # Remove the rows where neither eye is captured well
    clean_data = data[data["status"]!=22]
    
    # When status is 02 --> left eye is good, right eye is invalid
    clean_data.loc[(clean_data["status"]==2),"gaze_x"] = clean_data.loc[(clean_data["status"]==2),"left_gaze_x"]
    clean_data.loc[(clean_data["status"]==2),"gaze_y"] = clean_data.loc[(clean_data["status"]==2),"left_gaze_y"]
    
    # When status is 20 --> right eye is good, left eye is invalid
    clean_data.loc[(clean_data["status"]==20),"gaze_x"] = clean_data.loc[(clean_data["status"]==20),"right_gaze_x"]
    clean_data.loc[(clean_data["status"]==20),"gaze_y"] = clean_data.loc[(clean_data["status"]==20),"right_gaze_y"]
    
    # When status is 0, both eyes are well captured
    clean_data.loc[(clean_data["status"]==0),"gaze_x"] = (clean_data.loc[(clean_data["status"]==0),"left_gaze_x"] + clean_data.loc[(clean_data["status"]==0),"right_gaze_x"] )/2
    clean_data.loc[(clean_data["status"]==0),"gaze_y"] = (clean_data.loc[(clean_data["status"]==0),"left_gaze_y"] + clean_data.loc[(clean_data["status"]==0),"right_gaze_y"])/2
    return clean_data


# In[9]:


def down_sample(clean_data,interval = 0.050):
    '''
    Description:
        We dont need all the time points for analysis.
        In this script we have set the sampling rate of the data to 50ms.
        This means that we will take the average gaze poistions in every 50ms window
        We average the event_id, time, and gaze positions in this interval window.
        This width is cofigurable using the interval variable
    '''
    min_time = clean_data["time"].min()
    max_time = clean_data["time"].max()
    x_gaze=[]
    y_gaze = []
    time_gaze=[]
    event_id=[]
    while(min_time <= max_time):
        #print(min_time)
        x_gaze.append(clean_data.loc[clean_data["time"].between(min_time, min_time+interval),"gaze_x"].mean())
        y_gaze.append(clean_data.loc[clean_data["time"].between(min_time, min_time+interval),"gaze_y"].mean())
        time_gaze.append(min_time+interval/2)
        event_id.append(clean_data.loc[clean_data["time"].between(min_time, min_time+interval),"event_id"].mean())
        #print(x_gaze)
        min_time = min_time+interval+.001
    
    x_gaze=pd.Series(x_gaze) 
    y_gaze=pd.Series(y_gaze) 
    time_gaze=pd.Series(time_gaze) 
    event_id=pd.Series(event_id)    
    
    sub_sampled_data = pd.DataFrame(dict(x_gaze = x_gaze, y_gaze = y_gaze,time_gaze=time_gaze,event_id = event_id))
    sub_sampled_data.dropna(inplace = True)
    return sub_sampled_data


# In[10]:


def getStartEndEventIDs(message_events):
    start_end_ids =  message_events[message_events['category'].str.contains('trial_start|trial_end')][['category','text','event_id']]
    '''
    #You could add more markers and code here if you want
    # For instance if you want to know which is the start and end id explicitly through a column you could do something like the below
    start_end_ids.loc[start_end_ids['cateogry']=="trial_start",'start_or_end']="Start"
    start_end_ids.loc[start_end_ids['cateogry']=="trial_end",'start_or_end']="End"
    '''
    
    return(start_end_ids)


# In[11]:


def eyetrackPreProcessing(OnlyStartEndIDS =0):
    Study_eyetracking=pd.DataFrame()
    Study_StartEndIDS = pd.DataFrame()
    for subdir, dirs, files in os.walk(rootdir):    
        for file in files:
            if(re.search(".*\.hdf5$",file)):
                print(os.path.join(subdir,"message_events.csv"))
                message_events_file = os.path.join(subdir, "message_events.csv")
                message_events = pd.read_csv(message_events_file)
                
                #get the subject ID
                pattern = "(.*)logs(.*?)message_events\.csv"
                substring = re.search(pattern, message_events_file).group(2)
                subj_id=substring.replace('\\','')
                
                #look for start and end event ids
                start_end_ids = getStartEndEventIDs(message_events)
                start_end_ids['id'] = subj_id
                start_end_ids.to_csv(os.path.join(subdir,"start_end_ids.csv"),index=False)
                
                Study_StartEndIDS = pd.concat([Study_StartEndIDS,start_end_ids])
                
                #cleanup the eyetracking data. Sometimes you want only want to get the start/end ids.
                # THe below code takes time to run.
                # So call the script with OnlyStartEndIDS set to 1 (anything apart from 0). This will bypass the below code
                if(OnlyStartEndIDS ==0):
                    eyetracking_events_file = os.path.join(subdir, "eyetracking_events.csv")
                    eyetracking_events = pd.read_csv(eyetracking_events_file)
                    eyetracking_events = data_cleanup(eyetracking_events)
                    # Changing the down sampling interval below.
                    eyetracking_events = down_sample(eyetracking_events)
                    eyetracking_events['id'] = subj_id
                    eyetracking_events.to_csv(os.path.join(subdir,"downsampled_eyetracking.csv"),index=False)
                    Study_eyetracking = pd.concat([Study_eyetracking,eyetracking_events])
    
    Study_StartEndIDS.to_csv(os.path.join(rootdir,"Study_StartEndIDS.csv"),index = False)
    
    if(OnlyStartEndIDS ==0):
        Study_eyetracking.to_csv(os.path.join(rootdir,"Study_eyetracking.csv"),index = False)


# In[ ]:


eyetrackPreProcessing(OnlyStartEndIDS=0)


# In[12]:


# Mostly you will also want to see what % of data you lost due to the clean up and downsampling processes
# The below bit of code tells you that
summary_eyes = []
for subdir, dirs, files in os.walk(rootdir):    
        for file in files:
            if(re.search(".*\.hdf5$",file)):
                eyetracking_events_file = os.path.join(subdir, "eyetracking_events.csv")
                eyetracking_events = pd.read_csv(eyetracking_events_file)
                full_length = len(eyetracking_events)
                
                eyetracking_events = data_cleanup(eyetracking_events)
                
                reduced_length = len(eyetracking_events)
                
                downsampled_eyetracking_file = os.path.join(subdir, "downsampled_eyetracking.csv")
                downsampled_eyetracking_events = pd.read_csv(downsampled_eyetracking_file)
                down_length = len(downsampled_eyetracking_events)
                
                pattern = "(.*)logs(.*?)message_events\.csv"
                
                message_events_file = os.path.join(subdir, "message_events.csv")
                message_events = pd.read_csv(message_events_file)
                substring = re.search(pattern, message_events_file).group(2)
                subj_id=substring.replace('\\','')
                summary_eyes.append([subj_id,full_length,reduced_length,down_length])

summary_eyes


# In[ ]:




