# -*-coding:utf-8 -*-

import numpy as np
import numpy.matlib
import pandas as pd
import sys


def CV_day(Current_combiner,n_point):
    #输入：按天输入某个汇流箱下的所有支路电流数据矩阵Current_combiner、每天所取的数据点数目n_point；
    #输出：输出该汇流箱每天的离散率cv
    Current_apart = Current_combiner
    Current_apart[Current_apart < 0.0001] = 0.001
    Current_apart = np.transpose(Current_apart)
    m1 = np.mean(Current_apart,axis=1)
    s1 = np.std(Current_apart,axis=1,ddof=1)
    CV = s1 / m1
    Q = np.reshape(CV, (int(n_point),int(len(CV)/n_point)), order='F')
    qq = np.mean(Q)
    return qq


def demo():
    Current355=[0.550000000000000,0.586776859504000,
    0.624132231405000,0.674545454545000,
    0.715619834711000,0.785289256198000,
    0.819917355372000,0.913471074380000]
    Current356=[0.587107438017000,0.548925619835000,
    0.673884297521000,0.630000000000000,
    0.777603305785000,0.729090909091000,
    0.902561983471000,0.843471074380000]
    Current357 = [0.587107438017000, 0.548925619835000,
                  0.673884297521000, 0.630000000000000,
                  0.777603305785000, 0.729090909091000,
                  0.902561983471000, 0.843471074380000]
    c1 = np.reshape(Current355,(4,2))
    print(c1)
    print(c1.shape)
    c2 = np.reshape(Current356,(4,2))
    c3 = np.reshape(Current357, (4, 2))
    Current_combiner=np.array([c1,c2,c3])
    print(Current_combiner)
    print(Current_combiner.shape)
    n_point=4;
    lim1=0.05;
    lim2=0.1;
    lim3=0.2;
    [cv,ss_day]=CV_day(Current_combiner,n_point,lim1,lim2,lim3);
    print(cv,ss_day)


if __name__ == '__main__':
    demo()