# -*-coding:utf-8 -*-
import numpy as np
import numpy.matlib
import pandas as pd
import sys


def smooth(x,window_len=11,window='hanning'):
    '''
        params:
            x: signal for filtering
            window_len: length of window
            window: window type
        return:
            numpy.array
    '''
    if type(x) is not np.array:
        x=np.array(x)
    if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")
    if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")
    if window_len<3:
            return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
            w=np.ones(window_len,'d')
    else:
            w=eval('np.'+window+'(window_len)')
    y=np.convolve(w/w.sum(),s,mode='same')
    return y[window_len:-window_len+1]


def partile_diag(F1_cur,F2_cur,F1_vol,F2_vol,Ytest_cur,Ytest_vol,Ytest_Radi):
    '''
    ##四分位法诊断分析故障
    ##输入：训练得到的电流表征量的下界F1_cur、上界F2_cur、电压表征量的下界F1_vol、上界F2_vol;待测试的电流Ytest_cur、电压Ytest_vol、辐照度Ytest_Radi；
    ##输出：故障类型type,故障表现behavior,故障原因和建议reason；
    '''
    F1_cur = float(F1_cur)
    F2_cur = float(F2_cur)
    F1_vol = float(F1_vol)
    F2_vol = float(F2_vol)

    Ytest_cur = list(Ytest_cur)
    Ytest_vol = list(Ytest_vol)
    Ytest_Radi = list(Ytest_Radi)

    #计算电流阈值
    upp_current = np.multiply(F2_cur,Ytest_Radi)
    low_current = np.multiply(F1_cur,Ytest_Radi)
    
    #计算电压阈值
    # upp_voltage = np.matlib.repmat(F2_vol,len(Ytest_vol),1)
    # low_voltage = np.matlib.repmat(F1_vol,len(Ytest_vol),1)
    upp_voltage = [F2_vol] * len(Ytest_vol)
    low_voltage = [F1_vol] * len(Ytest_vol)

    Ytest_cur_smooth = smooth(Ytest_cur,3)
    Ytest_vol_smooth = smooth(Ytest_vol,3)
    upp_current_smooth = smooth(upp_current,3)
    low_current_smooth = smooth(low_current,3)
    upp_voltage_smooth = smooth(upp_voltage,3)
    low_voltage_smooth = smooth(low_voltage,3)


    
    type_ = [' '] * len(Ytest_cur)
    behavior = [' '] * len(Ytest_cur)
    ##判断故障类型
    for i in np.arange(0,len(Ytest_cur_smooth)):
        if (Ytest_cur_smooth[i] > 0) and (Ytest_cur_smooth[i] < low_voltage_smooth[i]) and Ytest_Radi[i] > 200:
            if Ytest_vol_smooth[i] < low_voltage_smooth[i]:
                type_[i] = "阴影遮挡"
                behavior[i] = "支路电流偏低且电压偏低"
            elif (Ytest_vol_smooth[i] > low_voltage_smooth[i]) and (Ytest_vol_smooth[i] < upp_voltage_smooth[i]):
                type_[i] = "开路或阴影遮挡"
                behavior[i] = "支路电流偏低"

            if (Ytest_cur_smooth[i] > upp_current_smooth[i]) and (Ytest_Radi[i] > 200):
                type_[i] = "通讯故障或其它异常"
                behavior[i] = "支路电流过高"

    for j in np.arange(0, len(Ytest_vol_smooth)):
        if (Ytest_vol_smooth[j] > 0) and (Ytest_vol_smooth[j] < low_voltage_smooth[j]) and (Ytest_Radi[j] > 200):
            if Ytest_cur_smooth[j] > low_current_smooth[j]:
                type_[j] = "短路"
                behavior[j] = "支路电压偏低且电流过高或正常"

        if (Ytest_vol_smooth[j] > upp_voltage_smooth[j]) and (Ytest_Radi[j] > 200):
                type_[j] = "通讯故障或其它异常"
                behavior[j] = "支路电压过高"

        if Ytest_Radi[j] > 200:
            if (Ytest_vol_smooth[j] > low_voltage_smooth[j]) and (Ytest_vol_smooth[j] < upp_voltage_smooth[j]) and (Ytest_cur_smooth[j] > low_current_smooth[j]) and (Ytest_cur_smooth[j] < upp_current_smooth[j]):
                type_[j] = " "
                behavior[j] = " "
            else:
                type_[j] = " "
                behavior[j] = " "

    for k in np.arange(0, len(Ytest_cur)):
        if (Ytest_cur[k] < 0) and (Ytest_Radi[k] > 200):
            type_[k] = "开路或通讯故障"
            behavior[k] = "支路电流小于0"

        if (Ytest_cur[k] == 0) and (Ytest_Radi[k] > 200):
            type_[k] = "开路或通讯故障"
            behavior[k] = "支路电流为0"

        if np.isnan(Ytest_cur[k]) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障"
            behavior[k] = "支路电流显示为空"

        if (Ytest_vol[k] < 0) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障或其它异常"
            behavior[k] = "支路电压小于0"

        if (Ytest_vol[k] == 0) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障或其它异常"
            behavior[k] = "支路电压为0"

        if np.isnan(Ytest_vol[k]) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障"
            behavior[k] = "支路电压显示为空"

        if (Ytest_vol[k] == 0) and (Ytest_cur[k] == 0) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障或其它异常"
            behavior[k] = "支路电压和电流均为0"

        if (np.isnan(Ytest_vol[k])) and np.isnan(Ytest_cur[k]) and (Ytest_Radi[k] > 200):
            type_[k] = "通讯故障"
            behavior[k] = "支路电压和电流均显示为空"
    
    type_ = np.transpose(type_)
    behavior = np.transpose(behavior)

    reason = [' '] * len(behavior)
    #故障原因和建议
    for k in np.arange(0,len(behavior)):
        if behavior[k] == '支路电压偏低且电流过高或正常':
            reason[k] = '①光伏组件短路或被击穿。建议：更换光伏组件。②旁路二极管或组件损坏。建议：若光伏组件完好，则检测旁路二极管，有问题及时更换；若光伏组件输出存在问题，则更换组件。③电缆接头接触不良或电缆过长、线径过细。建议：更换电缆型号。'
        elif behavior[k] == '支路电流偏低且电压偏低':
            reason[k] = '①组件性能退化或损坏。建议：更换光伏组件。②组件被覆盖或遮挡：A.雪覆盖；B.树木或建筑物的阴影；C.前后排遮挡；D.被杂草或鸟粪遮挡。建议：对遮挡物进行清理。'
        elif behavior[k] == '支路电流偏低':
            reason[k] = '①接线盒内二极管击穿。建议：若二极管接线盒可以更换，则更换二极管或接线盒；若无法更换，则更换光伏组件。②组件内部电池损坏。建议：更换光伏组件。③支路连线错搭。建议：重新布置连接线路。④组件被覆盖或遮挡：A.雪覆盖；B.树木或建筑物的阴影；C.前后排遮挡；D. 被杂草或鸟粪遮挡。建议：对遮挡物进行清理。'
        elif behavior[k] == '支路电流过高':
            reason[k] = '①支路测控模块的地址、波特率等参数设置错误。建议：重新设置通讯模块的参数。②电流过高异常。建议：待巡检。'
        elif (behavior[k] == '支路电流显示为空') or (behavior[k] == '支路电压显示为空') or (behavior[k] == '支路电压和电流均显示为空'):
            reason[k] = '①数据传输中断。建议：检查通讯设备。②支路测控模块的地址、波特率等参数设置错误。建议：重新设置通讯模块的参数。'
        elif (behavior[k]=="支路电流为0") and (behavior[k]=="支路电流小于0"):
            reason[k] = "①光伏组件掉落。建议：若光伏组件完好，重新固定；否则更换光伏组件。②接线盒线缆掉出或烧毁。建议：更换接线盒或光伏组件。③光伏组件MC插头未插紧或者烧断。建议：重新插拔或更换MC插头。④导线断开或腐蚀。建议：更换导线。⑤支路正负极的保险丝烧毁。建议：更换保险丝。⑥测控模块诵讯异常导致显示错误。建议：检查通讯设备。"
        elif behavior[k] == "支路电压偏低且电流过高":
            reason[k]="①光伏组件短路或被击穿。建议：更换光伏组件。②旁路二极管或组件损坏。建议：若光伏组件完好，则检测旁路二极管，有问题及时更换；若光伏组件输出存在问题，则更换组件。③电缆接头接触不良或电缆过长、线径过细。建议：更换电缆型号。"
        elif behavior[k] == '支路电压过高':
            reason[k]="①支路测控模块的地址、波特率等参数设置错误。建议：重新设置通讯模块的参数。②电压过高异常。建议：待巡检。"
        elif (behavior[k]=="支路电压为0") and (behavior[k]=="支路电压小于0"):
            reason[k] = "①测控模块诵讯异常导致显示错误。建议：检查通讯设备。②其它异常。建议：待巡检。"
        elif behavior[k]=="支路电压和电流均为0":
            reason[k]="①测控模块诵讯异常导致显示错误。建议：检查通讯设备。②其它异常。建议：待巡检。"
        elif behavior[k] == ' ':
            reason[k] = ''
    
    reason = np.transpose(reason)
    return type_.tolist(),behavior.tolist(),reason.tolist()

if __name__ == '__main__':
    F1_cur=0.0051
    F2_cur=0.0112
    F1_vol=514.2279
    F2_vol=566.0808
    Xtrain_cur = [1000,1100,1050]
    Xtrain_vol = [20,23,25]
    Xtrain_Radi = [1000,1100,1050]
    re = partile_diag(F1_cur,F2_cur,F1_vol,F2_vol,Xtrain_cur,Xtrain_vol,Xtrain_Radi)
    print(re)
