# -*-coding:utf-8 -*-
import sys



def ECO_cul(e):
    '''
    发电量减少NOX排放
    :param e: 主变高压侧1101开关正向有功底表差*33
    :return:
    “t_gce”：光伏场站交流累计发电量换算标准煤质量（大于0，吨，double类型，单数值）；
    “m_trees”：光伏场站交流累计发电量换算减少树木砍伐数量（大于0，颗，double类型，单数值）；
    “t_so2”：光伏场站交流累计发电量换算减少SO2排放质量（大于0，吨，double类型，单数值）；
    “t_co2”：光伏场站交流累计发电量换算减少CO2排放质量（大于0，吨，double类型，单数值）；
    “t_nox”：光伏场站交流累计发电量换算减少NOX排放质量（大于0，吨，double类型，单数值）。

    '''
    # E = e/10000
    E = e
    t_gce = E*0.4*10
    m_trees = E*0.977/1.8
    t_so2 = E*0.03*10
    t_co2 = E*0.997*10
    t_nox = E*0.015*10
    return t_gce,m_trees,t_so2,t_co2,t_nox


# if __name__ == "__main__":
    # run(sys.argv)
    # e = 1000
    # print(ECO_cul(e))