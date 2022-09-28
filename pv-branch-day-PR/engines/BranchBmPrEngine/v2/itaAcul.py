# -*-coding:utf-8 -*-

import sys
import numpy as np


def itaAcul(U,I,r,m):
    '''
    组串转换效率
    :param U:当日汇流箱每隔10分钟的汇流总电压，numpy一维矩阵
    :param I:当日同一汇流箱中各组串每隔10分钟的电流，numpy一维矩阵
    :param r:与输出功率相同时间点的倾斜面总辐照度，numpy一维矩阵
    :param m:组串中各组件面积之和，float数值
    :return: 该汇流箱中各组串当日转换效率，float数值
    '''
    m = float(m)
    if m == 0:
        return ['0']

    a = sum(r)
    b = a*m
    w = U*I
    c = sum(w)
    ita = c/b
    return ita


def demo():
    U = np.array([1,2,3])
    I = np.array([2,3,4])
    r = np.array([9,8,3])
    m = 20
    re = itaAcul(U,I,r,m)
    print(re)


if __name__ == "__main__":
    demo()
