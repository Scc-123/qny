# -*-coding:utf-8 -*-
import sys
import numpy as np

def deltaINVcul(wac,wdc):
    '''
    逆变器损耗率
    :param wac:当日每隔10分钟的单台逆变器交流输出功率，一维numpy数组
    :param wdc:当日每隔10分钟的单台逆变器直流输入功率，一维numpy数组
    :return: 同一逆变器当日逆变器损耗率, float数值
    '''

    t = 15/60
    edc = sum(wdc)*t
    eac = sum(wac)*t
    if edc == 0:
        return ['0']
    
    deltaINV = (edc-eac)/edc
    return deltaINV

def demo():
    wac = np.array([1,2,3])
    wdc = np.array([4,5,6])

    result = deltaINVcul(wac,wdc)
    print(result)

if __name__ == '__main__':
    demo()


