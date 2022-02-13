#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 12:16:46 2020

@author: lizbeard
@changes to make callable: vsvaidya
"""

import numpy as np
import pandas as pd
import h5py
import re,os

def find_events(hf, event_location):
    events = hf[event_location]
    #print(np.array(events))
    array = np.array(events)
    df = pd.DataFrame(array)
    #df['text']=df['text'].str.decode('UTF-8')
    return(df)

def convert_byte_cols(df):
    for col, dtype in df.dtypes.items():
        if dtype == np.object:  # Only process byte object columns.
            df[col] = df[col].str.decode('utf-8')
    print("Done converting byte columns to string!")
    return df

def convert_hdf5(input_filename,output_filename):
    # first lets read in our HDF5 five
    # okay so we know this works, but that's pretty much it
    # This will probably need to change to \ on mac and linux machines
    m = input_filename.rfind('\\') 
    directory = input_filename[0:m+1]
    print("Directory is ",directory)
    hf = h5py.File(input_filename, 'r')
    # what 'keys' are in the file?
    # we can see it here
    # an easier way to view this is to open the hdf5 file in hdf5 viewer
    # (the windows version has a known bug which means that you will need to open the program
    # by running the batch file at C:\Users\CARD\AppData\Local\HDF_Group\HDFView instead of the executable file

    # First extract the location of the required data from the class table mapping in the hdf5
    # We need 
    # 1. message events
    # 2. Keyboard press events
    # 3. Mouse Buttong events
    # 4. BinocularEyeSampleEvent
    all_events = list(hf['class_table_mapping'])
    # The third column of all_events elements have the type of event
    # we simply cycle through the entire mapping and push the locations to the respective variables
    message_event_location =''
    eyetracking_event_location =''
    mouse_press_event_location =''
    keyboard_press_event_location =''
    for event in all_events:
        #print(event)
        if event[2].decode('UTF-8') == 'MessageEvent' :
            message_event_location = event[3].decode('UTF-8')
            
        if event[2].decode('UTF-8') == 'BinocularEyeSampleEvent' :
            eyetracking_event_location = event[3].decode('UTF-8')
            
        if event[2].decode('UTF-8') == 'MouseButtonPressEvent' :
            mouse_press_event_location = event[3].decode('UTF-8')
            
        if event[2].decode('UTF-8') == 'KeyboardPressEvent' :
            keyboard_press_event_location = event[3].decode('UTF-8')
          
    # There is a pandas function for this but its really buggy so we're going to not use it
    # pd.read_hdf(input_filename)
    
    # find all message events
    if message_event_location == '':
        print("No Message events found! \n. Ignoring during processing")
    else :
        message_events = find_events(hf, message_event_location)
        print("Message events found : ", len(message_events.index))
        message_events = convert_byte_cols(message_events)
        message_events.to_csv(os.path.join(directory,"message_events.csv"), index=False)
        print("Saved in NOW", os.path.join(directory,"message_events.csv"),"\n")
    
    # find all eyetracking events
    if eyetracking_event_location == '':
        print("No Eyetracking events found! \n. Ignoring during processing")
    else :
        eyetracking_events = find_events(hf, eyetracking_event_location)
        print("Eyetracking events found : ", len(eyetracking_events.index))
        eyetracking_events = convert_byte_cols(eyetracking_events)
        eyetracking_events.to_csv(directory+"eyetracking_events.csv", index=False)
        print("Saved in ", directory,"eyetracking_events.csv \n")
    
    if mouse_press_event_location == '':
        print("No Mouse events found! \n. Ignoring during processing")
    else :
        mouse_press_events = find_events(hf, mouse_press_event_location)
        print("Mouse press events found : " , len(mouse_press_events.index))
        mouse_press_events = convert_byte_cols(mouse_press_events)
        mouse_press_events.to_csv(directory+"mouse_press_events.csv", index=False)
        print("Saved in ", directory,"mouse_press_events.csv \n")
    
    if keyboard_press_event_location == '':
        print("No Keyboard Press events found! \n. Ignoring during processing")
    else :
        keyboard_press_events = find_events(hf, keyboard_press_event_location)
        print("Keyboard press events found : " , len(keyboard_press_events.index))
        keyboard_press_events = convert_byte_cols(keyboard_press_events)
        keyboard_press_events.to_csv(directory+"keyboard_press_events.csv", index=False)
        print("Saved in ", directory,"keyboard_press_events.csv \n")
    
if __name__ == "__main__":
    input_filename = 'C:/Users/CARD/VSVOnedrive/OneDrive - Temple University/Year II/Honesty/Scripts/logs/2/2_eyetracker_20211019-143216.hdf5'
    output_filename = 'C:/Users/CARD/VSVOnedrive/OneDrive - Temple University/Year II/Honesty/Scripts/logs/2_eyetracker_20211019-143216.csv'
    convert_hdf5(input_filename,output_filename)