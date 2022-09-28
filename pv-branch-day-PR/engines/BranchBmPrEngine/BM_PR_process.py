import os
import glob

import pandas as pd
import traceback
import time
import numpy as np
from .data_clearning import DataClearning
# import re
from .v2.PR_deviation import PR_deviation
from .functional_module import Function_process
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")


def bm_pr_process(oripath,savepath,dstpath,stationurl,stationid,dsttime,nowtime,iscenterlized,midpath):
    # ---------------------------------------step1:路径整合-----------------------------------------------------------
    try:
        stationid = int(stationid)
        # 场站信息csv-(装机容量和全站组串总量)
        df_station = pd.read_excel(stationurl)
        # 获取辐照度csv url
        radianceurls = list(glob.glob(os.path.join(oripath, '*_radiation.csv')))
        radianceurl = radianceurls[0]
        # 获取汇流箱电流csv url
        currenturls = list(glob.glob(os.path.join(oripath, '*_current.csv')))
        currenturl = currenturls[0]
        # 获取汇流箱电压csv url
        voltagaurls = list(glob.glob(os.path.join(oripath, '*_voltage.csv')))
        voltagaurl = voltagaurls[0]
        # 获取json
        path_jz = list(glob.glob(os.path.join(oripath, 'boxes.json')))
        path_zc = list(glob.glob(os.path.join(oripath, 'inverters.json')))
        # 获取标杆组串和组串
        path1_PR = os.path.join(midpath, "mid_data", str(stationid), 'branch_peak.csv')
        partile_path = os.path.join(midpath, "mid_data", str(stationid), 'branch_partile_setting.csv')

    except:
        logger.error(traceback.format_exc())
        raise Exception("step1: Path fusion error!")
    # -------------------------------------------------step2:数据读取清洗-------------------------------------------
    try:
        print('--step2：Data clearning...')
        DC = DataClearning(dstime=dsttime, nowtime=nowtime)
        radiance = DC.df_clearn(radianceurl)
        voltage = DC.df_clearn(voltagaurl)
        current = DC.df_clearn(currenturl)
        partile = pd.read_csv(partile_path, encoding='gbk')
        BR1 = pd.read_csv(path1_PR, encoding='gbk')
    except:
        BR1 = pd.DataFrame(data=None, columns=['time', 'device_code', 'peak'])
        partile = pd.DataFrame(data=None, columns=['time', 'device_code', 'F1_cur', 'F2_cur', 'F1_vol', 'F2_vol'])
        logger.error(traceback.format_exc())
        raise Exception("step2: Data clearning error!")
    # -------------------------------------------------step3:标杆组串选取-------------------------------------------
    print('--step3：Data calculation...')
    loss_predict = 0.37
    loss_abnormal = 0.64
    F_c = Function_process(current, voltage, radiance, df_station, stationid, BR1, partile, loss_predict, loss_abnormal, dsttime, nowtime, savepath)

    t = time.time()
    t1 = time.time()
    if iscenterlized:
        # # # # # # # # # # # 集中式 # # # # # # # # # # # # # #
        F_c.dispersion_rate()
    else:
        # # # # # # # # # # # 组串式 # # # # # # # # # # # # # #
        F_c.dispersion_rate_zc()
    t2 = time.time()
    print('step3-1 Data calculate ：%f s' % (t2 - t1))

    lim1 = 0.05
    lim2 = 0.1
    lim3 = 0.2
    try:
        t3 = time.time()
        if iscenterlized:
            # # # # # # # # # # # 集中式 # # # # # # # # # # # # # #
            F_c.cv_days(iscenterlized, path_jz, lim1, lim2, lim3)
        else:
            # # # # # # # # # # # 组串式 # # # # # # # # # # # # # #
            F_c.cv_days(iscenterlized, path_zc, lim1, lim2, lim3)
        t4 = time.time()
        print('step3-2 calculate time ：%f s' % (t4 - t3))
    except:
        logger.error(traceback.format_exc())
        raise Exception("step3: Equipment Consistency Analysis error!")

    try:
        BR_s_v = 0.85
        path2_PRS = list(glob.glob(os.path.join(savepath, 'branch_PR_stationid_*.csv')))
        path2_PR = path2_PRS[0]
        PR_deviation(path1_PR, path2_PR, BR_s_v, savepath, stationid, nowtime)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step3: String Deviation calculate error!")
    ts = time.time()
    print('step3 data calculate ：%f s' % (ts - t))

    # -------------------------------------------------step3:组串PR统计性计算，可靠性描述标杆-------------------------------------------

