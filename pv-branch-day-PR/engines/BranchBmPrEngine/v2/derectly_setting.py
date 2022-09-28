##直接阈值法诊断分析故障
##使用该函数前需要检查函数内参数定义是否符合所需
##输入：待测试的电流Ytest_cur；待测试的电压Ytest_vol;待测时刻辐照度Radiation；待测试时刻温度Temperature
##输出：故障类型type,故障表现behavior,故障原因和建议reason；
import numpy as np
import numpy.matlib
import pandas as pd


def derectly_setting(Ytest_cur,Ytest_vol,Radiation,Temperature):
    Ytest_cur = np.array(Ytest_cur)
    Ytest_vol = np.array(Ytest_vol)
    Radiation = np.array(Radiation)
    Temperature = np.array(Temperature)
    ##
    #定义参数
    #大气质量AM1.5、辐照度1000W/m2、电池工作温度25℃下的标称参数：
    n_series = 16
    
    I_mppt = 8.22
    
    V_mppt = 36.5
    
    I_sc = 8.79
    
    #太阳电池组件温度系数：
    a = 0.0004
    
    b = - 0.0033
    
    T0 = 47
    
    #设定阈值设定系数
    k1 = 0.25
    w1 = 0.8
    
    k2 = 0.85
    w2 = 0.14
    
    ##
    #计算电流阈值
    low1 = np.multiply(k1,I_mppt)
    
    upp1 = I_sc + I_sc * w1
    
    #计算电压阈值
    low2 = V_mppt * n_series * k2
    
    upp2 = V_mppt * n_series + V_mppt * n_series * w2
    
    ##
    #测试的电流电压数据转换成STC条件
    Ytest_cur = np.multiply(Ytest_cur,(1000.0 / Radiation)) + a * (T0 - Temperature)
    
    Ytest_vol = Ytest_vol - 0.0031 * (T0 - Temperature)
    
    ##
    #输出每个时刻的阈值
    # low_current = np.matlib.repmat(low1,len(Ytest_cur),1)
    
    # upp_current = np.matlib.repmat(upp1,len(Ytest_cur),1)
    
    # low_voltage = np.matlib.repmat(low2,len(Ytest_vol),1)
    
    # upp_voltage = np.matlib.repmat(upp2,len(Ytest_vol),1)

    low_current = [low1] * len(Ytest_cur)
    upp_current = [upp1] * len(Ytest_cur)
    low_voltage = [low2] * len(Ytest_vol)
    upp_voltage = [upp2] * len(Ytest_vol)
    
    
    type_ = [' '] * len(Ytest_cur)
    ##判断故障类型
    for i in np.arange(0,len(Ytest_cur),1):
        if (Ytest_cur[i] > low_current[i]) and (Ytest_cur[i] < upp_current[i]):
            if (Ytest_vol[i] > low_voltage[i]) and (Ytest_vol[i] < upp_voltage[i]):
                type_[i] = '无故障'
            else:
                if Ytest_vol[i] < low_voltage[i]:
                    type_[i] = '短路'
                elif Ytest_vol[i] > upp_voltage[i]:
                    type_[i] = '短路'
        else:
            if (Ytest_vol[i] > low_voltage[i]) and (Ytest_vol[i] < upp_voltage[i]):
                if Ytest_cur[i] < low_current[i]:
                    type_[i] = '开路'
                elif Ytest_cur[i] == 0:
                    type_[i] = '开路'
                elif Ytest_cur[i] > upp_current[i]:
                    type_[i] = '支路电流偏高'
                else:
                    type_[i] = '开路'
            else:
                if Ytest_cur[i] > upp_current[i] and (Ytest_vol[i] > upp_voltage[i]):
                    type_[i] = '电流电压偏高'
                elif np.isnan(Ytest_cur[i]) or np.isnan(Ytest_vol[i]):
                    type_[i] = '开路'
                elif np.isnan(Ytest_vol[i]):
                    type_[i] = '电压显示为空'
                else:
                    type_[i] = '阴影遮挡'
    
    type_ = np.transpose(type_)

    behavior = [' '] * len(Ytest_cur)
    #故障表现
    for j in np.arange(0,len(Ytest_cur),1):
        if (Ytest_cur[j] > low_current[j]) and (Ytest_cur[j] < upp_current[j]):
            if (Ytest_vol[j] > low_voltage[j]) and (Ytest_vol[j] < upp_voltage[j]):
                behavior[j] = '无故障'
            elif Ytest_vol[j] < low_voltage[j]:
                behavior[j] = '支路电压偏低'
            elif Ytest_vol[j] > upp_voltage[j]:
                behavior[j] = '支路电压过高'
        else:
            if (Ytest_vol[j] > low_voltage[j]) and (Ytest_vol[j] < upp_voltage[j]):
                if Ytest_cur[j] < low_current[j]:
                    behavior[j] = '支路电流偏低'
                elif Ytest_cur[j] == 0:
                    behavior[j] = '支路电流为0'
                elif Ytest_cur[j] > upp_current[j]:
                    behavior[j] = '支路电流偏高'
                else:
                    behavior[j] = '支路电流显示为空'
            else:
                if Ytest_cur[j] > upp_current[j] and (Ytest_vol[j] > upp_voltage[j]):
                    behavior[j] = '电流电压偏高'
                elif np.isnan(Ytest_cur[j]) or np.isnan(Ytest_vol[j]):
                    behavior[j] = '支路电流显示为空'
                elif np.isnan(Ytest_vol[j]):
                    behavior[j] = '支路电压显示为空'
                else:
                    behavior[j] = '支路电流电压均异常'
    
    behavior = np.transpose(behavior)

    reason = [' '] * len(behavior)
    #故障原因和建议
    for k in np.arange(0,len(behavior),1):
        if behavior[k] == '支路电流偏低':
            reason[k] = '①接线盒内二极管击穿；建议：若二极管接线盒可以更换，则更换二极管或接线盒；若无法更换，则更换光伏组件。②组件内部电池短路；建议：若有备件，则更换光伏组件。③支路连线错搭短路；建议：重新布置连接线路。④部分组件破损；建议：更换光伏组件。⑤组件被遮挡：A.雪覆盖，B.树木或建筑物的阴影，C.前后排遮挡；D.被杂草或鸟粪遮挡;建议：对遮挡物进行清理。'
        elif behavior[k] == '支路电流为0':
            reason[k] = '①测控模块诵讯异常导致显示错误；建议：检查通讯设备。②光伏组件掉落；建议：若光伏组件完好，重新固定，否则更换光伏组件。③接线盒线缆掉出或烧毁；建议：若有备件，则更换接线盒或光伏组件。④光伏组件MC插头未插紧或者烧断；建议：重新插拔或更换MC插头。⑤导线断开或腐蚀；建议：更换导线。⑥支路正负极的保险丝烧毁；建议：更换保险丝。'
        elif behavior[k] == '支路电流显示为空':
            reason[k] = '处于夜间或采集器、通讯故障;建议：若非夜间，检查通讯设备，重新设置通讯模块的参数'
        elif (behavior[k] == '支路电流显示为空') or (behavior[k] == '支路电压显示为空'):
            reason[k] = '处于夜间或采集器、通讯故障;建议：若非夜间，检查通讯设备，重新设置通讯模块的参数'
        elif behavior[k] == '支路电压偏低':
            reason[k] = '①光伏组件短路或被击穿;建议：若有备件，则更换光伏组件。②旁路二极管损坏或组件损坏;建议：若光伏组件完好，则检测旁路二极管，有问题及时更换；若光伏组件输出存在问题，则更换组件。③电缆接头接触不良或电缆过长、线径过细;建议：更换电缆型号。④组件被遮挡：A.雪覆盖,B.树木或建筑物的阴影,C.前后排遮挡,D.被杂草或鸟粪遮挡;建议：对遮挡物进行清理。'
        elif behavior[k] == '支路电压过高':
            reason[k] = '①组件损毁；建议：更换光伏组件。②电缆绝缘层损坏导致了接地故障；建议：检查组件的连接线，找出与支架连接的导线。'
        elif behavior[k] == '支路电流电压均异常':
            reason[k] = '①组件性能退化或损坏；建议：若有备件，则更换光伏组件。②组件被遮挡：A.雪覆盖，B.树木或建筑物的阴影，C.前后排遮挡,D.被杂草或鸟粪遮挡;建议：对遮挡物进行清理。'
        else:
            reason[k] = ''
    
    reason = np.transpose(reason)
    return type_,behavior,reason


def demo():
    Ytest_cur = [1,2,3]
    Ytest_vol = [10,11,12]
    Radiation = [1000,1100,1050]
    Temperature = [20,23,25]
    result = derectly_setting(Ytest_cur,Ytest_vol,Radiation,Temperature)
    print(result)


if __name__ == '__main__':
    demo()
 