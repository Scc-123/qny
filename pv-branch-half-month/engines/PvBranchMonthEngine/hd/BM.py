# -*-coding:utf-8 -*-

import os
import sys
import numpy as np
from scipy import stats
import pandas as pd
import re


# def format(x):
#     """
#     把NAN和str替换为0
#     :param x:
#     :return:
#     """
#     value = re.compile(r'^\s*[-+]*[0-9]+\.*[0-9]*\s*$')
#     if value.match(str(x)):  # 不是数字
#         return float(x)
#     else:
#         return float(0)
def normfit(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n - 1)
    var = np.var(data, ddof=1)
    varCI_upper = var * (n - 1) / (stats.chi2.ppf((1-confidence) / 2, n - 1))
    varCI_lower = var * (n - 1) / (stats.chi2.ppf(1-(1-confidence) / 2, n - 1))
    sigma = np.sqrt(var)
    sigmaCI_lower = np.sqrt(varCI_lower)
    sigmaCI_upper = np.sqrt(varCI_upper)

    return m, sigma, [m - h, m + h], [sigmaCI_lower, sigmaCI_upper]


def BM(P,R,tpower,num):
    '''
    标杆组串选取
    :param P:过去半个月全站组串功率组成的矩阵，numpy二维数组
    :param R:过去半个月辐照度组成的矩阵，numpy二维数组
    :param tpower:组串的装机容量，numpy一维数组
    :param num:全站组串总数，int数值
    :return:
        bench：标杆组串编号，int
        peak：标杆组串峰值，float
    '''
    np.set_printoptions(threshold=np.inf)

    R = np.array(R, dtype=float).reshape([len(R), 1])  # [m,1] m个时间点
    tpower = np.array([tpower]) * np.ones([num, 1])
    R[np.where(R < 30.0)] = np.nan
    # tmp = np.dot(R/1000,tpower.T)
    tmp = np.dot(R, tpower.T)
    PR = P/tmp
    PR = PR.astype(np.float)
    pks = []
    for i in range(num):
        data = PR[:,i]
        data = data[~np.isnan(data)]
        m0, sigma, r1, r2 = normfit(data)
        if m0 < 0.3:
            pks.append(0)
        else:
            m = sigma * (np.sqrt(2 * np.pi))
            pks.append(1 / m)
    peak = np.max(pks)
    # bench = np.nanargmax(pks) + 1  # 原始
    bench = np.nanargmax(pks)
    return [bench,peak]


def demo():
    R = np.array([10, 200, 300, 4])
    print(R.shape)  # (4,)

    P = np.array([[100, 101, 300], [200, 205, 300], [200, 205, 300], [200, 205, 300]])
    # P = np.array([[100,101,300,400],[200,205,300,400],[200,205,300,400],[200,205,300,400]])

    print(P.shape)  # (4, 3)
    tpower = 4800
    num = 3
    re = BM(P, R, tpower, num)
    print(re)



if __name__ == '__main__':
	demo()

