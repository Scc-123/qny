# -*-coding:utf-8 -*-
import sys
import os
import numpy as np
import scipy.stats as stats
import json



def corcul(r, w):
    '''
    # 输入变量：r-当日每隔15分钟的倾斜面辐照度，numpy一维；
    # w-当日每隔15分钟的电站总输出功率，numpy一维；
    return 当日倾斜面辐照度与输出功率的相关系数, float
    '''
    re = ''

    #%标准化
    R = (r - min(r)) / (max(r) - min(r))
    W = (w - min(w)) / (max(w) - min(w))
    # % 计算辐照量与输出功率的相关系数
    cor = stats.pearsonr(W, R)
    re = cor[0]
    return re


def demo():
    r = np.array([33.5553719,2102.993802,2508.864959,3487.539256,5126.398678])
    w = np.array([1467.651322,13669.68455,15701.03992,21898.07521,30547.58298])

    result = corcul(r,w)
    print(result)


if __name__ == "__main__":
    demo()
