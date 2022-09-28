# -*-coding:utf-8 -*-
import sys
import numpy as np


def itaPcul(r,pac,m):
    '''
    电站综合效率
    :param r:每10分钟辐照度，一维numpy数组
    :param pac: 主变高压侧1101开关正向有功两天底表差*33，一维numpy数组
    :param m:组件面积之和，float数值
    :return: 当日光伏电站综合效率，float数值
    '''
    
    if m == 0:
        return 0
    
    a = sum(r)*(10/60.0)/1000
    b = m*a
    eac = (np.max(pac) - np.min(pac))*330*1000
    ita = eac/b
    return ita

def demo():
    r = np.array([1,2,3])
    pac = np.array([1.2,1.3,1.9])
    m = 10.0
    result = itaPcul(r,pac,m)
    print(result)


if __name__ == "__main__":
    demo()
