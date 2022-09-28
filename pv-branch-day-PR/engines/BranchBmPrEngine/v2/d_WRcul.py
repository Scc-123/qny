# -*-coding:utf-8 -*-
import sys
import os
import numpy as np
import scipy.stats as stats


def d_WRcul(r, w):
    '''
    光伏电站标准化输出功率和辐照量间的欧氏距离进行计算，执行周期为日
    r：当日每隔15分钟的倾斜面辐照度，[0,1500],单位：kW/m2，一列数值；
    w：当日每隔15分钟的电站总输出功率，[大于0],单位：kW，一列数值；
    return 当日倾斜面辐照度与输出功率的欧氏距离 float
    '''
    re = ''

    r = np.array(r)
    w = np.array(w)
    # %标准化
    R = (r - min(r)) / (max(r) - min(r))
    W = (w - min(w)) / (max(w) - min(w))
    # %计算欧式距离
    dr = np.linalg.norm(R-W)
    return dr


def demo():
    r = [33.5553719, 2102.993802, 2508.864959, 3487.539256, 5126.398678]
    w = [1467.651322, 13669.68455, 15701.03992, 21898.07521, 30547.58298]
    re = d_WRcul(r, w)
    print(re)


if __name__ == "__main__":
    demo()
