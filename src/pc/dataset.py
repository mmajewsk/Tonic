import pandas as pd
import os
import json

def steering_df(directory, jsonfilename='steering.json',to_letters_dict=None):
    to_letters_dict = {87:'w', 83:'s', 68:'d', 65:'a'} if to_letters_dict is None else to_letters_dict
    jdata = None
    with open(os.path.join(directory,jsonfilename),'r') as f:
        jdata = json.load(f)
    dictdata = dict(w=[],a=[],s=[],d=[],time=[])
    for d,t in jdata:
        for number, letter in to_letters_dict.items():
            dictdata[letter].append(d[str(number)])
        dictdata['time'].append(t)
    df2 = pd.DataFrame(dictdata)
    return df2

def pics_df(directory):
    files = os.listdir(directory)
    files = list(filter(lambda x: x[-4:] == '.jpg', files))
    pictimes = list(map(lambda x: float(x.split("_")[1][:-4]), files))
    emptycol = [None]*len(pictimes)
    df = pd.DataFrame(dict(filenames=files, pictimes=pictimes,a=emptycol,w=emptycol,s=emptycol,d=emptycol))
    return df

def imu_df(directory):
    imu = 'imu.csv'
    imu_path = os.path.join(directory, imu)
    idf = pd.read_csv(imu_path)
    idf['imutime'] = idf['time']
    del idf['time']
    idf = idf.drop_duplicates('imutime')
    return idf

def combine(idf, vsdf):
    alltimes= pd.concat([idf.imutime,vsdf.time])
    xdf = pd.DataFrame({'alltimes':alltimes.sort_values()})
    xdf = pd.merge(xdf,vsdf,how='left',left_on='alltimes', right_on='time')
    xdf = pd.merge(xdf,idf,how='left',left_on='alltimes', right_on='imutime')
    xdf = xdf.fillna(method='pad')
    #xdf = xdf[xdf['filenames'].notnull()]
    return xdf

def conevert_dump_to_dataset(dumps_path):
    dfp = pics_df(dumps_path)
    dfs = steering_df(dumps_path)
    joind = pd.merge_asof(dfp, dfs, left_on='pictimes', right_on='time', suffixes=['video', 'steer'])
    joind = joind[joind['time'].notnull()]
    del joind['avideo']
    del joind['dvideo']
    del joind['wvideo']
    del joind['svideo']
    del joind['time']
    joind = joind.rename(str, {'asteer': 'a', 'wsteer': 'w', 'ssteer': 's', 'dsteer': 'd', 'pictimes': 'time'})
    return joind

def dump_dataframe(dumps_path, imu=False):
    df = conevert_dump_to_dataset(dumps_path)
    df.to_csv(os.path.join(dumps_path, 'steering_v1.csv'), index=False)

def join_imu(dumps_path):
    df = pd.read_csv(os.path.join(dumps_path, 'steering_v1.csv'))
    idf = imu_df(dumps_path)
    xdf = combine(idf, df)
    xdf.to_csv(os.path.join(dumps_path, 'vis_v1.csv'), index=False)