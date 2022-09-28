import os
import glob

import pandas as pd
import traceback
import time
import numpy as np
# import re
from v2.PR_deviation import PR_deviation
from functional_module import Function_process
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")
# bm_pr_process(oripath, savepath, self.stationurl, stationid, dsttime, nowtime, iscenterlized)

def bm_pr_process(oripath,savepath,stationurl,stationid,dsttime,nowtime,iscenterlized):
    # ---------------------------------------step1:路径整合-----------------------------------------------------------
    try:
        stationid = int(stationid)
        dsttimename = str(nowtime).replace('-', '')
        nowtimename = str(nowtime).replace('-', '')

        #--------------------------------结果csv路径整合----------------------------------------------------
        #标杆组串结果csv
        savename_BM = os.path.join(savepath, 'branch_peak_%s_%s.csv' % (str(stationid), str(dsttimename)))
        # 组串PR统计性计算，可靠性描述标杆结果csv
        savename_PR = os.path.join(savepath, 'branch_PR _reliability_by_15d_%s_%s.csv' % (str(stationid), str(dsttimename)))
        #--------------------------------(半个月)原始数据获取---------------------------------------------------------
        # 获取辐照度csv url
        radianceurls = list(glob.glob(os.path.join(oripath, '*_radiation.csv')))
        # 获取汇流箱电流csv url
        currenturls = list(glob.glob(os.path.join(oripath, '*_current.csv')))

        # 获取汇流箱电压csv url
        voltagaurls = list(glob.glob(os.path.join(oripath, '*_voltage.csv')))

        # 获取json
        path_jz = list(glob.glob(os.path.join(oripath, 'boxes.json')))
        path_zc = list(glob.glob(os.path.join(oripath, 'inverters.json')))

        # 获取标杆组串和组串
        path_data = os.path.join(savepath, "mid_data", str(stationid), 'branch_peak.csv')
        path_data1 = os.path.join(savepath, "mid_data", str(stationid), 'branch_partile_setting.csv')

        path1_PR = list(glob.glob(os.path.join(savepath, path_data, 'branch_peak_stationid_*.csv')))
        partile_path = list(glob.glob(os.path.join(savepath, path_data1, 'branch_partile_setting_*.csv')))

        mid_path = str(nowtimename) + "/" + str(stationid)
        path2_PRS = list(glob.glob(os.path.join(savepath, mid_path, 'branch_PR_stationid_*.csv')))

        # 场站信息csv-(装机容量和全站组串总量)
        df_station = pd.read_excel(stationurl)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step1: Path fusion error!")
    # -------------------------------------------------step2:标杆组串选取-------------------------------------------
    current = pd.read_csv(currenturls[0], encoding='gbk')  # 读取电流数据  # 参数获取
    current = current[(current["time"] >= dsttime) & (current["time"] < nowtime)]
    voltage = pd.read_csv(voltagaurls[0], encoding='gbk')  # 参数获取
    voltage = voltage[(voltage["time"] >= dsttime) & (voltage["time"] < nowtime)]
    radiance = pd.read_csv(radianceurls[0], encoding='gbk')
    radiance = radiance[(radiance["time"] >= dsttime) & (radiance["time"] < nowtime)]
    partile = pd.read_csv(partile_path, encoding='gbk')
    BR1 = pd.read_csv(path1_PR, encoding='gbk')

    loss_predict = 0.37
    loss_abnormal = 0.64
    F_c = Function_process(current, voltage, radiance, df_station, stationid, BR1, partile, loss_predict, loss_abnormal, nowtime, savepath)

    t = time.time()
    if iscenterlized:
        # # # # # # # # # # # 集中式 # # # # # # # # # # # # # #
        t1 = time.time()
        F_c.dispersion_rate()
        t2 = time.time()
        print('Energy calculate ：%f s' % (t2 - t1))
    else:
        # # # # # # # # # # # 组串式 # # # # # # # # # # # # # #
        t3 = time.time()
        F_c.dispersion_rate_zc()
        t4 = time.time()
        print('Energy calculate ：%f s' % (t4 - t3))

    lim1 = 0.05
    lim2 = 0.1
    lim3 = 0.2
    try:
        if iscenterlized:
            # # # # # # # # # # # 集中式 # # # # # # # # # # # # # #
            t1 = time.time()
            F_c.cv_days(iscenterlized, path_jz, lim1, lim2, lim3)
            t2 = time.time()
            print('Energy calculate ：%f s' % (t2 - t1))
        else:
            # # # # # # # # # # # 组串式 # # # # # # # # # # # # # #
            t3 = time.time()
            F_c.cv_days(iscenterlized, path_zc, lim1, lim2, lim3)
            t4 = time.time()
            print('Energy calculate ：%f s' % (t4 - t3))
    except:
        logger.error(traceback.format_exc())
        raise Exception("step2: 全站设备生产情况一致性分析 error!")

    try:
        BR_s_v = 0.85
        PR_deviation(path1_PR, path2_PRS, BR_s_v, savepath, stationid, nowtime)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step2: 组串PR与设计值偏差 error!")
    ts = time.time()
    print('Energy calculate ：%f s' % (ts - t))

    # -------------------------------------------------step3:组串PR统计性计算，可靠性描述标杆-------------------------------------------


if __name__ in "__main__":
    # oripath = r'536/'
    # savepath = r'536/output/'
    # stationcsvurl = r'pv_station.xlsx'
    # station_id = 536
    # iscenterlized = 0
    # dsttime = '2022-08-17'
    # nowtime = '2022-08-18'
    # bm_pr_process(oripath, savepath, stationcsvurl, station_id, dsttime, nowtime,iscenterlized)

    oripath = r'591_集中式/'
    savepath = r'591_集中式/output/'
    stationcsvurl = r'pv_station.xlsx'
    station_id = 591
    iscenterlized = 1
    dsttime = '2022-08-15'
    nowtime = '2022-08-16'
    bm_pr_process(oripath, savepath, stationcsvurl, station_id, dsttime, nowtime, iscenterlized)




