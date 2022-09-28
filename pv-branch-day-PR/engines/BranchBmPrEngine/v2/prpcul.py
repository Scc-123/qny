# -*-coding:utf-8 -*-
import sys
import json
import numpy as np



def prpcul(r,pac,tpower):
    '''
    :param r: 10分钟总辐照度，numpy一维数组
    :param pac: 主变高压侧1101开关正向有功两天底表差*33，一维numpy数组
    :param tpower: 装机容量
    :return: 当日电站PR值，float数值
    '''
    eac = (np.max(pac) - np.min(pac)) * 330
    tpower = float(tpower)
    if tpower == 0:
        return ['0']
    
    yf = eac/tpower #单位转换
    # 10分钟
    yr = sum(r) * (10 / 60) / 1000
    prp = yf/yr
    return prp


def demo():
    r = np.array([1,2,5])
    pac = np.array([1.4,1.8,1.0])
    tpower = 20
    result = prpcul(r,pac,tpower)
    print(result)


if __name__ == "__main__":
    demo()
    