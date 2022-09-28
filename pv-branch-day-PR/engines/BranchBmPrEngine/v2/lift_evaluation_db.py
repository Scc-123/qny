# -*-coding:utf-8 -*-
import numpy as np

def lift_evaluation_db(Pm,Cm,Vm,P,C,V):
    '''
    一个组串的功率和基准值偏差、电流和基准值值偏差、电压与基准值偏差计算
    Pm:基准组串一天144个时刻的功率
    Cm:基准组串一天144个时刻的电流
    Vm:基准组串一天144个时刻的电压
    P:待测组串一天144个时刻的功率
    C:待测组串一天144个时刻的电流
    V:待测组串一天144个时刻的电压
    return:
    dP:待测组串功率偏差值
    dC:待测组串电流偏差值
    dV:待测组串电压偏差值
    '''
    numP = Pm.shape[0]
    dP = sum(np.nan_to_num((Pm - P) / Pm)) / numP
    numC = Cm.shape[0]
    dC = sum(np.nan_to_num((Cm - C) / Cm)) / numC
    numV = Vm.shape[0]
    dV = sum(np.nan_to_num((Vm - V) / Vm)) / numV
    return dP,dC,dV





def demo():
    Pm = np.array([33.5553719, 2102.993802, 2508.864959, 3487.539256, 5126.398678])
    Cm= np.array([1467.651322, 13669.68455, 15701.03992, 21898.07521, 30547.58298])
    Vm =np.array( [1467.651322, 13669.68455, 15701.03992, 21898.07521, 30547.58298])

    P = np.array([30.5550719, 2100.993802, 2500.864059, 3480.539256, 5120.398078])
    C = np.array([1460.651322, 13660.68455, 15700.03092, 21988.07521, 30550.58098])
    V = np.array([1460.651322, 13660.68455, 15700.03092, 21890.07521, 30540.58098])

    dP,dC,dV = lift_evaluation_db(Pm, Cm, Vm, P, C, V)
    print(dP)
    print(dC)
    print(dV)



if __name__ == "__main__":
    demo()
