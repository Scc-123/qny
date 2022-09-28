# -*-coding:utf-8 -*-
import sys
import numpy as np


def cvIVcul(varargin):
    '''
    组串电流、电压离散率
    将各待统计组串当日每隔15分钟的电压/电流值进行合并
    :param varargin:  
    :return: 当日各组串间电压/电流离散率 float
    '''

    p,q = np.shape(varargin)
    Z = np.zeros([p,q])
    # varargin[np.isnan(varargin)] = 0.001
    # 按列归一化
    for j in np.arange(0,q):
        y = varargin[:,j]
        Y = (y-np.min(y))/(np.max(y)-np.min(y))
        Z[:,j] = Y
    # 求和
    Z[np.isnan(Z)] = 0
    a = np.sum(Z,axis=0)
    b = np.mean(a)
    c = np.std(a)
    # das
    # 样本均值/标准差
    cv = c/b
    return cv


# def demo():
#     r = [147.651322, 1369.68455, 1571.03992, 2188.07521]
#     w = [1467.651322, 13669.68455, 15701.03992, 21898.07521]
#     tt = np.array([r,w])
#     print(tt)
#     result = cvIVcul(tt)
#     print(result)
#
#
# if __name__=='__main__':
#     demo()
    