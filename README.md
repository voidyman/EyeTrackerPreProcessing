# EyeTrackerPreProcessing
Takes a list of hdf5 files, splits them, cleans them up and down-samples them as needed


The Generic script requires the python script hdf5_csv_conversion.py.
Everything else is pretty straightforward. Feel free to suggest changes as required.

I use the Tobi XL-60 and psychopy to run the experimental setup.

I send all my data to the ET as message_events. This allows me to line up the data with the eyetracking events seamlessly.
