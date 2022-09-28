# -*- coding:utf-8 -*-

import pandas as pd
import sys
import numpy as np


def itaINVcul(wac,wdc):
    '''
    计算当日每隔10分钟的逆变器交流输出电量和直流输入电量
    :param wac:交流电,二维矩阵
    :param wdc:直流电，二维矩阵
    :return:itaINV :同一逆变器当日转换效率，二维矩阵
    '''

    t = 10/60
    edc = sum(wdc)*t
    
    # 按公式计算逆变器转换效率
    itaINV = wac*1000/edc
    return itaINV


def demo():
    wac = np.array([[1,2,3],[2,3,4]])
    wdc = np.array([[1,2,3],[2,3,4]])
    result = itaINVcul(wac,wdc)
    print(result)

if __name__ == '__main__':
    demo()

