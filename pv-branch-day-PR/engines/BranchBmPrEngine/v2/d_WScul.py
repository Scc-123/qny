# -*-coding:utf-8 -*-

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats



def d_WScul(ws,w):
    '''
    # % 输入参数：ws - 当日每隔15分钟的标杆组串输出功率，一列数值；
    # % w - 待计算组串当日每隔15分钟的输出功率，一列数值；
    # return 待计算组串与标杆组串日功率的欧氏距离，float
    '''

    WS = (ws - min(ws)) / (max(ws) - min(ws))
    W = (w - min(w)) / (max(w) - min(w))

    d = np.linalg.norm(W - WS)
    return d

def demo():
    ws = [33.5553719,2102.993802,2508.864959,3487.539256,5126.398678]
    w = [446.8017355,2479.179752,2769.919174,3760.295868,5298.205124]
    re = d_WScul(np.array(ws), np.array(w))
    print(re)


if __name__ == "__main__":
    demo()
    
