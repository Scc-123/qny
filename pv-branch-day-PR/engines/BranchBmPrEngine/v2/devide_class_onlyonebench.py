# -*-coding:utf-8 -*-
import numpy as np
import sys


def devide_class_onlyonebench(P,Voltage,Current,Radiation,loss_predict,loss_abnormal,capacity):
    '''
    （1）标杆组串的实时功率P（数组类型），范围为：[大于等于0] W；
    （2）待测组串的实时电流Current, 范围为：[0 20] A；待测组串的实时电压Voltage, 范围为：[0 2000] V,数组类型；
    （3）实时辐照度Radiation（数组类型），范围为：[0 1500] W/m2。
    （4）预警界限值loss_predict（数值类型）, 范围为：[0 1]，可设定为0.37; 
    （5）报警界限值loss_abnormal（数值类型）, 范围为：[0 1]，可设定为0.64;
    :return: 故障等级result（string类型，内容为文本）
    '''
    loss_predict = float(loss_predict)
    loss_abnormal = float(loss_abnormal)
    capacity = float(capacity) * 1000

    reference_power = P
    test_popower = Voltage*Current
    reference_power[reference_power==0]=0.001
    # PPloss = (reference_power-test_popower)/reference_power
    PPloss = (reference_power-test_popower)/capacity
    PPloss = np.array(PPloss)
    # print(PPloss)
    try:
        len1,wei1 = np.shape(PPloss)
    except:
        len1 = np.shape(PPloss)[0]
        wei1 = 1
    classs = np.ones([len1,wei1])
    PPloss = np.reshape(PPloss,[len1,1])
    Radiation = np.reshape(Radiation,[len1,1])
    y = np.empty([len1,wei1])

    classs[np.where((PPloss<loss_predict) & (Radiation>200))]=1
    classs[np.where((PPloss>loss_predict) & (PPloss<loss_abnormal) & (Radiation>200))]=2
    classs[np.where((PPloss>loss_abnormal) & (Radiation>200))]=3
    
    result = []
    for j in range(0,len(classs)):
        if classs[j]==1:
            result.append("正常")
        elif classs[j]==3:
            result.append("报警！严重故障")
        else:
            result.append("组串低效，请关注")

    return result


def demo():
    # P = np.array([[37544.57667,37550.57667],
    #      [33257.82625,33260.82625],
    #      [32874.07667,32880.07667],
    #      [35767.74111,35750.74111],
    #      [31052.79511,31000.79511],
    #      [30206.79,30306.79],
    #      [26786.32223,26886.32223],
    #      [44372.46708,44302.46708],
    #      [42506.55583,42406.55583],
    #      [40181.85292,40281.85292]
    #      ])
    #
    # n = 16

    # P = np.array([[37544.57667],
    #               [37544.57667]])
    # Voltage = np.array([[541.4666667],
    #                     [541.4666667]])
    # Current = np.array([[3.925],
    #                    [3.925]])
    # Radiation = np.array([[449.975],
    #                      [449.975]])
    P = np.array([37544.57667,37544.57667]).T
    Voltage = np.array([541.4666667,541.4666667]).T
    Current = np.array([3.925, 3.925]).T
    Radiation = np.array([449.975,449.975]).T
    print(Radiation.shape)
    loss_predict = 0.4
    loss_abnormal = 0.4
    capacity = 27.82
    result = devide_class_onlyonebench(P,Voltage,Current,Radiation,loss_predict,loss_abnormal,capacity)
    print(result)


if __name__ == "__main__":
    demo()
    