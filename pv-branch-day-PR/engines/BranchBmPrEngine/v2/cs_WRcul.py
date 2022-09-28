# -*-coding:utf-8 -*-

import os
import sys
import numpy as np
import json


def cs_WRcul(r, w):
    '''
    光伏电站资源适应性分析
    # %输入变量：r-当日每隔15分钟的倾斜面辐照度，一列数值；
    # %w-当日每隔15分钟的电站总输出功率，一列数值；
    return 当日倾斜面辐照度与输出功率的欧氏距离，float
    '''

    R = (r - min(r)) / (max(r) - min(r))
    W = (w - min(w)) / (max(w) - min(w))
    # % 计算余弦相似度
    csr = np.dot(R, W) / (np.linalg.norm(R) * np.linalg.norm(W))
    return csr


def demo():
    r = [33.5553719,2102.993802,2508.864959,3487.539256,5126.398678]
    w = [1467.651322,13669.68455,15701.03992,21898.07521,30547.58298]
    re = cs_WRcul(np.array(r), np.array(w))
    print(re)


if __name__ == "__main__":
    demo()
    