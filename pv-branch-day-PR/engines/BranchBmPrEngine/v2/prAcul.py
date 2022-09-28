# -*-coding:utf-8 -*-
import sys
import numpy as np



def prAcul(w, r, tpower):
    '''
    组串PR计算
    :param U: 每10分钟总电压,一维numpy数组
    :param I: 每10分钟电流,一维numpy数组
    W = U * I
    :param R: 每10分钟总辐照度,一维numpy数组
    :param tpower: 装机容量, float类型
    :return: 该组串当日PR值, float类型
    '''
    if tpower == 0:
        return 0
    
    t = 10/60.0
    R = np.array(r)
    FH = sum(R)*t/1000
    # W = U * I
    W = np.array(w)
    # print(W)
    # print(R)
    # print(W.shape)
    # print(R.shape)
    PDR = sum(W)*t
    PT = FH*(tpower*1000)
    pr = PDR/PT
    # sad
    return pr


def demo():
    U = np.array([1,2,3])
    I = np.array([1,2,3])
    W = U * I
    R = np.array([100,200,150])
    tpower = 10
    result = prAcul(W,R,tpower)
    print(result)


if __name__ == "__main__":
    demo()
