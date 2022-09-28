# -*-coding:utf-8 -*-
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats


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


def Rel(P,R,tpower,num):
    '''
    %R过去半个月全站组串功率组成的矩阵
    %P过去半个月辐照度组成的矩阵
    %tpower为所有组串的装机容量，列向量（tpower=4800.*ones(12,1);)
    %num为组串总数目，如12
    %bench为标杆组串编号
    :return: Reliability:各组串的可靠性，一维数组；
            PKSbench：标杆峰值，float类型
    '''

    R = np.array(R, dtype=float).reshape([len(R), 1])  # [m,1] m个时间点
    tpower = np.array([tpower]) * np.ones([num, 1])

    R[np.where(R < 30.0)] = np.nan
    # tmp = np.dot(R / 1000, tpower.T)
    tmp = np.dot(R,tpower.T)
    PR = P/tmp
    PR = PR.astype(np.float)
    # print(PR)
    pks = []
    CCF = []
    for i in range(num):
        data = PR[:,i]
        data = data[~np.isnan(data)]
        u,sigma,r1,r2 = normfit(data)
        if u < 0.3:
            pks.append(0)
        else:
            m = sigma * (np.sqrt(2*np.pi))
            pks.append(1/m)
    PKSbench = np.max(pks)
    Reliability = pks / PKSbench
    return [PKSbench, Reliability]


def demo():
    R = np.array([100, 200])
    P = np.array([[100,101],[200,205]])
    tpower = 4800
    num = 2
    result = Rel(P,R,tpower,num)
    print(result)




if __name__=="__main__":
    demo()
