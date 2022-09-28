import pandas as pd
import copy
import logging
import glob
import os
import numpy as np
import datetime
import math
import re
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")

def insert_branch_id(df_current):
    df_current['device_code'] = df_current['device_code'].apply(str)
    df_current['branch_no'] = df_current['branch_no'].apply(str)
    df_current.insert(loc=len(df_current.columns), column='branch_id', value=df_current['device_code'])
    index4 = df_current.index[df_current['branch_id'].str.len() > 0]
    df_current.loc[index4, ['branch_id']] = df_current.loc[index4, ['branch_id']] + '-'
    df_current.loc[index4, 'branch_id'] = df_current['branch_id'].str.cat(df_current['branch_no'])
    # 加入一列，组串名字
    return df_current

class DataClearning(object):
    def __init__(self,dstime,nowtime):
        df = pd.DataFrame()
        self.res = {"code":0,"df":df}
        self.dstime = dstime
        self.nowtime = nowtime
    def df_dropna(self,df:pd.DataFrame):
        df = df.replace(r'\N', np.nan)
        df = df.dropna(how='all', axis=0)
        df = df.replace(np.nan, 0)
        return df


    def df_clearn(self,dfurl):
        # ---1 判断读取csv是否成功
        try:
            dfori = pd.read_csv(dfurl, encoding='gbk')
        except:
            dfout = pd.DataFrame()
            return dfout
        df = self.df_dropna(dfori)
        df['time'] = pd.to_datetime(df['time'])
        dfout = df[(df["time"] >= self.dstime) & (df["time"] < self.nowtime)]
        return dfout

