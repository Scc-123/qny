# -*-coding:utf-8 -*-
import sys
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
from functools import wraps
import json
import statsmodels.api as sm


def output_json(*var_name):
    '''
    参考https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p04_define_decorator_that_takes_arguments.html
    带参数的装饰器，在函数执行后将结果转为json格式
    :param var_name: json字典的变量名
    :return:
    '''
    keys_json = []
    for vn in var_name:
        keys_json.append(vn)

    def decorate(func):
        # print("Decorater Runing...")
        @wraps(func)
        def wrapper(*args,**kwargs):
            result_dict = {}
            result = func(*args,**kwargs)
            for ii,rt in enumerate(result):
                result_dict[keys_json[ii]] = rt
                result_dict_output = json.dumps(result_dict)
            return result_dict_output
        return wrapper
    return decorate


def run(*args, **kwargs):
    w = args[0][1]
    r = args[0][2]

    if len(r) == 0 or len(w) == 0:
        print("args is empty")
    else:
        re = EP(w, r)
        print(re)
        return re

@output_json('k','wt','R')
def EP(w,r):
	r = np.array(json.loads(r))
	w = np.array(json.loads(w))

	model = sm.OLS(w, r).fit()

	# 回归系数
	k = model.params
	# 残值
	R = model.resid

	wt = k * r
	return [json.dumps(list(k)),json.dumps(list(wt)),json.dumps(list(R))]


if __name__ == "__main__":
	run(sys.argv)
