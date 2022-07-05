import pandas as pd
import numpy as np
import os
import gpxpy
import gpxpy.gpx
import gpxcsv
import json
import pprint as pp
import utils_fx

## load, and convert GPX to xml, save, return if requested
def gpx_to_xml(input_path:str, activity_name:str, output_path:str=None) -> str:

    activity = gpxpy.parse(open(os.path.join(input_path,activity_name)))
    xml = activity.to_xml()

    if output_path!=None:
        output_fname = os.path.join(output_path,os.path.splitext(activity_name)[0]) + '.xml'

        with open(output_fname,'w') as output:
            output.write(xml)
            
        print("Created: " + output_fname)
    return xml

## load, and convert GPX to json, save, return if requested
def gpx_to_json(input_path:str, activity_name:str, output_path:str=None) -> str:

    activity = gpxcsv.gpxtolist(os.path.join(input_path,activity_name))
    
    if output_path!=None:
        output_fname = os.path.join(output_path,os.path.splitext(activity_name)[0]) + '.json'
    
        with open(output_fname, 'w') as fn:
            json.dump(activity, fn, ensure_ascii=False, indent=4, sort_keys=True)
    
        print("Created: " + output_fname)

    return activity

## load, and convert GPX to csv, save, return if requested
def gpx_to_csv(input_path:str, activity_name:str, output_path:str=None) -> str:

    activity = gpxcsv.gpxtolist(os.path.join(input_path,activity_name))
    activity = pd.DataFrame(activity)
    
    if output_path!=None:
        output_fname = os.path.join(output_path,os.path.splitext(activity_name)[0]) + '.csv'

        activity.to_csv(output_fname)

        print("Created: " + output_fname)

    return activity.to_csv()

## load and parse gpx, return it
def read_gpx(input_path:str, activity_name:str) -> str:

    activity = gpxpy.parse(open(os.path.join(input_path,activity_name)))

    return activity

## load and parse gpx, convert to pandas dataframe
def gpx_to_df(input_path:str, activity_name:str)-> object:

    activity = gpx_to_json(input_path, activity_name, output_path=None)
    df = pd.DataFrame(activity)
    
    return df

# find all activities in a folder of certain format, return as dict 
def get_activities(input_path:str, format:str) -> dict:
    
    activities = {"path":[], "name":[], "format":[]}

    dir_list = os.listdir(input_path)

    for file in dir_list:
        name, ext = os.path.splitext(file)
        if ext == ('.' + format):
            activities["name"].append(name)
            activities["path"].append(input_path)
            activities["format"].append(format)

    return activities

#converts an entire folder of .gpx to selected output format
def batch_convert(input_path:str, output_format:str, output_path:str) -> None:

    activities_list = get_activities(input_path, format='gpx')
    
    print("Activities List: \n")
    pp.pprint(activities_list)
    print("Begin Batch Conversion")

    for nm, fmt in zip(activities_list["name"], activities_list["format"]):
        
        if output_format == 'xml':
            gpx_to_xml(input_path=input_path, activity_name=(nm + '.' + fmt), output_path=output_path)
        elif output_format == 'json':
            gpx_to_json(input_path=input_path, activity_name=(nm + '.' + fmt), output_path=output_path)
        elif (output_format == 'csv'):
            gpx_to_csv(input_path=input_path, activity_name=(nm + '.' + fmt), output_path=output_path)

def load(input_path):

    if os.path.isdir(input_path):
        activities = get_activities(input_path=input_path, format='gpx')
        return activities
    else:
        path, fname =  os.path.split(input_path)
        fn, ext = fname.split('.')
        if ext=='gpx':
            activity = gpx_to_df(input_path=path, activity_name=fname)
        elif ext=='json':
            activity = json.load(open(os.path.join(path,fname)))
            activity = pd.DataFrame(activity)
        elif ext=='csv':
            activity = pd.read_csv(os.path.join(path,fname))

        print(f"Read {ext} Activity: {fname} from {input_path}.")
        activity = utils_fx.apply_base_transforms(activity)

        return activity