# -*-coding:utf-8 -*-
import sys
import numpy as np
import json


def cv_itaINVcul(varargin):
    '''
    逆变器转换效率离散率
    每两列输入一台逆变器当日每隔十五分钟的直流输入功率和交流输出功率
    :param varargin:二维数组，输入功率矩阵
    :return:cvitaINV 当日各逆变器发电量效率离散率 float
    '''
    
    #取出奇数列为直流输入功率
    wdc = varargin[:,0::2]
    #取出偶数列数列为交流输出功率
    wac = varargin[:,1::2]
    #外层循环计算逆变器转换效率离散率
    _, a = wdc.shape
    edc = np.zeros([a,1])
    eac = np.zeros([a,1])
    for i in range(0,a):
        edc[i] = sum(wdc[:,i])*0.25
        eac[i] = sum(wac[:,i])*0.25
    #按公式计算逆变器转换效率
    itaINV = eac/edc
    #按公式计算转换效率离散率
    miu = np.nanmean(itaINV)
    sigma = np.nanstd(itaINV)
    cvitaINV = sigma/miu
    return cvitaINV


def demo():
    r = [33.5553719, 2102.993802, 2508.864959, 3487.539256]
    w = [1467.651322, 13669.68455, 15701.03992, 21898.07521]
    tt = np.array([r,w])
    result = cv_itaINVcul(tt)
    print(result)



if __name__=='__main__':
    demo()
