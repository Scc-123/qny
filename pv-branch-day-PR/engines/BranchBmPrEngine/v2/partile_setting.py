import numpy as np
import numpy.matlib
import pandas as pd
import sys


def partile_setting(Xtrain_cur,Xtrain_vol,Xtrain_Radi):
    '''
     ##四分位法获得阈值
    （1）历史电流数据： Xtrain_cur（数组类型），范围为：[0 20] A；
    （2）历史电压数据： Xtrain_vol（数组类型），范围为：[0 2000] V；
    （3）历史辐照度数据： Xtrain_Radi（数组类型），范围为：[0 1500] W/m2；

    ##输出：电流表征量的下界F1_cur（数值类型）、上界F2_cur（数值类型），范围为：[0 20] A.m2/W；
            电压表征量的下界F1_vol（数值类型）、上界F2_vol（数值类型），范围为：[0 2000] V。
    '''

    Xtrain_cur = np.array(Xtrain_cur)
    Xtrain_cur = Xtrain_cur.reshape((len(Xtrain_cur), 1))

    Xtrain_vol = np.array(Xtrain_vol)
    Xtrain_vol = Xtrain_vol.reshape((len(Xtrain_vol), 1))

    Xtrain_Radi = np.array(Xtrain_Radi)
    Xtrain_Radi = Xtrain_Radi.reshape((len(Xtrain_Radi), 1))
    '''
    ''' 
    len1,wei1 = Xtrain_cur.shape
    # rr = 100
    rr = 200
    R1 = np.matlib.repmat(Xtrain_Radi,1,wei1)
    
    x1 = Xtrain_cur
    
    # x1[np.any[np.isnan[x1],2],:] = 888
    x1[np.any(np.isnan(x1)),:] = 888

    if np.size(x1[np.where(R1 < rr)]):
        x1[np.where(R1 < rr)] = np.nan
    # x1[np.where(R1 < rr)] = np.nan
    
    # x1[np.any[np.isnan[x1],2],:] = []
    x1 = x1[~np.isnan(x1)]

    if np.size(x1[x1 == 888]):
        x1[x1==888] = np.nan
    
    #辐照度清洗
    R1[np.any(np.isnan(R1)),:] = 888
    
    if np.size(R1[R1<rr]):
        R1[R1<rr] = np.nan
    
    # R1[np.any[np.isnan[R1],2],:] = []
    R1 = R1[~np.isnan(R1)]
    
    if np.size(R1[R1==888]):
        R1[R1==888] = np.nan
    
    ##
    #电流除以辐照度为新的电流出力表征量y1_cur
    #y1_cur=Xtrain_cur./Xtrain_Radi;
    y1_cur = x1 / R1
    ##
    #用四分位法计算电流表征量的分位数
    A = y1_cur
    
    Q1 = np.percentile(A,25)
    
    Q3 = np.percentile(A,75)
    
    Q = Q3 - Q1
    
    F2_cur = Q3 + 1.5 * Q
    
    F1_cur = Q1 - 1.5 * Q
    
    ##
    ##
    #电压的训练数据的清洗，剔除辐照度100以下时的数据
    len2,wei2 = Xtrain_vol.shape
    
    R2 = np.matlib.repmat(Xtrain_Radi,1,wei2)
    
    x2 = Xtrain_vol
    
    # x2[np.any[np.isnan[x2],2],:] = 888
    x2[np.any(np.isnan(x2)),:] = 888
    
    if np.size(x2[R2 < rr]):
        x2[R2 < rr] = np.nan
    
    # x2[np.any[np.isnan[x2],2],:] = []
    x2 = x2[~np.isnan(x2)]
    
    if np.size(x2[x2 == 888]):
        x2[x2 == 888] = np.nan
    
    #电流除以辐照度为新的电流出力表征量y1_cur
    y1_vol = x2
    
    #用四分位法计算电压表征量的分位数
    A = y1_vol
    
    Q1 = np.percentile(A,25)
    
    Q3 = np.percentile(A,75)
    
    Q = Q3 - Q1
    
    F2_vol = Q3 + 1.5 * Q
    
    F1_vol = Q1 - 1.5 * Q
    
    return F1_cur,F2_cur,F1_vol,F2_vol


if __name__ == '__main__':   

    Xtrain_cur = [1000,1100,1050]
    Xtrain_vol = [20,23,25]
    Xtrain_Radi = [1000,1100,1050]
    re = partile_setting(Xtrain_cur, Xtrain_vol, Xtrain_Radi)
    print(re)