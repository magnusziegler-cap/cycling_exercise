import pandas as pd
import numpy as np
import os
import gpxpy
import gpxpy.gpx
import gpxcsv
import json
import pprint as pp

## STATICS
EARTH_RADIUS = 6378.137
ONE_DEGREE = (2*np.pi*EARTH_RADIUS)/360 #km/deg
ONE_DEGREE_M = (2*np.pi*EARTH_RADIUS*1000)/360 #m/deg

def _calculate_speed(d,t):
    return d/t

def _calculate_distance(lat_start, long_start, ele_start, lat_end, long_end, ele_end):

    #basic euclidean because the distances should be short
    dx = ((lat_end - lat_start)*ONE_DEGREE_M)**2 #should be in metres
    dy = ((long_end - long_start)*ONE_DEGREE_M)**2 #should be in metres
    dz = (ele_end - ele_start)**2 #metres

    # print(dx,dy,dz)

    d = np.sqrt(dx+dy+dz)

    return d
    
def _calculate_elapsed_time(time_start, time_end):

    t = time_end-time_start
    t = t.seconds

    return float(t) 

def _calculate_gradient(lat_start, long_start, ele_start, lat_end, long_end, ele_end):
    
    dx = ((lat_end - lat_start)*ONE_DEGREE_M)**2 #should be in metres
    dy = ((long_end - long_start)*ONE_DEGREE_M)**2 #should be in metres

    dxy = np.sqrt(dx+dy)

    dz = ele_end - ele_start
    
    if dz==0:
        gradient = 0
        return gradient
    else:
        gradient = np.degrees(np.arctan(dz/dxy))
    
    return gradient

def set_track_origin(df, lat_origin:int=0, lon_origin:int=0, ele_origin:int=0):
    #shift the start of the track to (0,0)
    df["lon"] = df["lon"]-(df.iloc[0].lon-lon_origin)
    df["lat"] = df["lat"]-(df.iloc[0].lat-lat_origin)
    df["ele"] = df["ele"]-(df.iloc[0].ele-ele_origin)

    return df

def update_df(df:pd.DataFrame)->pd.DataFrame:

    (rows, cols) = df.shape

    d = np.zeros(shape=(rows,1))
    g = np.zeros(shape=(rows,1))
    dt = np.zeros(shape=(rows,1))
    s = np.zeros(shape=(rows,1))

    for row in range(1,rows):
        start_lat = df.iloc[row-1].lat
        start_lon = df.iloc[row-1].lon
        start_ele = df.iloc[row-1].ele
        stop_lat = df.iloc[row].lat
        stop_lon = df.iloc[row].lon
        stop_ele = df.iloc[row].ele

        d[row] = _calculate_distance(start_lat,start_lon,start_ele,stop_lat,stop_lon,stop_ele)
        g[row] = _calculate_gradient(start_lat,start_lon,start_ele,stop_lat,stop_lon,stop_ele)
        dt[row] = _calculate_elapsed_time(df.iloc[row-1].time, df.iloc[row].time)

    s = np.divide(d,dt)
    s[np.isnan(s)] = 0

    df["distance"] = d
    df["cumulative_distance"] = df["distance"].cumsum().divide(1000)
    df["gradient"] = g
    df["speed"]= s*3.6
    df['dt'] = dt

    if not "power" in df.columns:
        (r,c) = df.shape
        df.insert(loc=0,column="power",value=np.zeros(shape=(r,1)))

    return df

def scale_hr(df, resting_hr=55):
    
    df["hr_resting_multiple"] = df["hr"]/resting_hr
    
    return df

def update_time(df):

    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%dT%H:%M:%SZ" )
    df["elapsed_time"] = df["time"] - df.iloc[0].time
    df["elapsed_time_s"] = df["elapsed_time"]/np.timedelta64(1,'s')

    return df

def apply_base_transforms(df, resting_hr=55, origin:tuple=(58.4108,15.6214,45)):

    df = update_time(df)
    df = update_df(df)
    df = scale_hr(df, resting_hr)

    (lat_origin, lon_origin, ele_origin) = origin
    df = set_track_origin(df,lat_origin, lon_origin, ele_origin)

    ## round some data
    df["gradient"] = df["gradient"].round(decimals=3)
    df = _calculate_uphill_downhill(activity=df)
    df["hr_resting_multiple"] = df["hr_resting_multiple"].round(decimals=3)

    return df

def apply_smoothing(activity, key, window=5, method='mean'):
    if method=="mean":
        df_out = activity[key].rolling(window, min_periods=1, center=True, axis=0).mean()
    elif method=="median":
        df_out = activity[key].rolling(window, min_periods=1, center=True, axis=0).median()
    
    return df_out

def _calculate_uphill_downhill(activity, smoothing=True):
    if smoothing:
        gradient = activity["gradient"].rolling(window=5, min_periods=1, center=True, axis=0).mean()
        activity.insert(loc=0, column="up_or_down", value=gradient.apply(lambda x: ("uphill" if x>0 else "downhill")))
        activity.insert(loc=0, column="up_or_down_bin", value=gradient.apply(lambda x: (True if x>0 else False)))
    else:
        activity.insert(loc=0, column="up_or_down", value=gradient.apply(lambda x: ("uphill" if x>0 else "downhill")))
        activity.insert(loc=0, column="up_or_down_bin", value=gradient.apply(lambda x: (True if x>0 else False)))

    return activity