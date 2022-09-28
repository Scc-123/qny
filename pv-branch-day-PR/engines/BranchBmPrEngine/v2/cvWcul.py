# -*-coding:utf-8 -*-
import sys
import numpy as np


def cvWcul(varargin):
    '''
    组串输出功率离散率
    :param varargin: 各待统计组串（数量不定）当日每隔15分钟的功率数据
    :return: 当日输出功率离散率 float
    '''
    cv = ''
    varargin = np.array(varargin)
    p, q = np.shape(varargin)
    W = np.zeros([p, q])
    for j in np.arange(0, q):
        y = varargin[:, j]
        Y = (y - np.min(y)) / (np.max(y) - np.min(y))
        W[:, j] = Y

    W = W.astype(np.float)
    W = np.nan_to_num(W)
    c = np.sum(W, axis=0)
    d = np.mean(c)
    e = np.std(c)
    cv = e/d
    return cv

def demo():
    r = [33.5553719, 2102.993802, 2508.864959, 3487.539256]
    w = [1467.651322, 13669.68455, 15701.03992, 21898.07521]
    tt = np.array([r,w])
    cv = cvWcul(tt)
    print(cv)


if __name__ == "__main__":
    demo()
