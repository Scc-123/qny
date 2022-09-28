import os
import glob
import numpy as np
from .data_clearning import DataClearning
from .branch_calculate import BranchMerge
from .hd.BM import BM
from .hd.Rel import Rel
import pandas as pd
import traceback
import time
import logging
import json
import re
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")

def branch_month_process(oripaths,savepath,dstpath,stationurl,stationid,dsttimes,nowtime,iscenterlized,half_time,midpath):
    # ---------------------------------------step1:半个月数据读取---------------------------------------------------------
    try:
        # # 场站信息csv
        df_station = pd.read_excel(stationurl)
        df = df_station[(df_station["id"] == int(stationid))]
        tpower = df["capacity"].iloc[0] * 1000  # 装机容量单位MW转换为W
        # ----获取输出csv路径
        stationid = int(stationid)
        dsttimename = str(nowtime).replace('-', '')
        df_months = []
        for i in range(0,len(oripaths)):
            # ---------------------------------------step1-1:路径整合-----------------------------------------------------------
            if i==0:
                pretime = nowtime
            else:
                pretime = dsttimes[i-1]
            oripath = oripaths[i]
            # print("pretimepretimepretimepretimepretimepretime",pretime)
            dsttime = dsttimes[i]
            #-----获取输入csv的路径
            #获取辐照度csv url
            radianceurls = list(glob.glob(os.path.join(oripath,'*_radiation.csv')))
            if len(radianceurls) ==0:
                continue
            radianceurl = radianceurls[0]
            # #获取汇流箱电流csv url
            currenturls = list(glob.glob(os.path.join(oripath, '*_current.csv')))
            if len(currenturls) ==0:
                continue
            currenturl = currenturls[0]
            # #获取汇流箱电压csv url
            voltagaurls = list(glob.glob(os.path.join(oripath,'*_voltage.csv')))
            if len(voltagaurls) ==0:
                continue
            voltagaurl = voltagaurls[0]
            # -----------------------------------step1-2:数据读取清洗-------------------------------------------
            try:
                print('--step2：%s Data clearning...'%(str(dsttime)))
                # nowtime
                DC = DataClearning(dstime=dsttime, nowtime=pretime)
                # DC = DataClearning(dstime=dsttime, nowtime=pretime)
                df_radiance = DC.df_clearn(radianceurl)
                df_current = DC.df_clearn(currenturl)
                df_voltaga = DC.df_clearn(voltagaurl)
                if df_voltaga.empty or df_current.empty or df_radiance.empty:
                    continue
                dictout = {"dfr":df_radiance,"dfc":df_current,"dfv":df_voltaga,"dstt":dsttime,"nowt":pretime}
                df_months.append(dictout)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Data clearning error!")
    except:
        logger.error(traceback.format_exc())
        raise Exception("step1: Path fusion error!")
    # ---------------------------------------step1:半个月数据merge,fusion----------------------------------------------
    try:
        print('--step3：Data merge about 200s..')
        B_M = BranchMerge(df_months)
        if iscenterlized:
            df_cvr_month = B_M.df_cvr_merge_jz()
            print('..')
        else:
            df_cvr_month = B_M.df_cvr_merge_zc()
    except:
        logger.error(traceback.format_exc())
        raise Exception("step1: Path fusion error!")
    #-----------------------------------------step2:BM,Rel计算-----------------------------------

    colkeys_re = ['time', 'device_code', 'branch_no','value']
    df_out_re = pd.DataFrame(data=None, columns=colkeys_re)
    savenamef_re = os.path.join(savepath, 'branch_PR _reliability_by_15d_%s_%s.csv' % (str(stationid), str(dsttimename)))

    colkeys = ['time', 'device_code', 'peak']
    df_out = pd.DataFrame(data=None, columns=colkeys)
    savenamef = os.path.join(savepath, 'branch_peak_%s_%s.csv' % (str(stationid), str(dsttimename)))

    mid_paths = os.path.join(midpath, "mid_data", str(stationid))
    if not os.path.exists(mid_paths):
        os.makedirs(mid_paths)
    mid_savepath = os.path.join(mid_paths, 'branch_peak.csv')
    if os.path.exists(mid_savepath):
        os.remove(mid_savepath)
    try:
        print('--step3: step2:BM,Rel...')

        def format(x):
            # 把NAN和str替换为0
            value = re.compile(r'^\s*[-+]*[0-9]+\.*[0-9]*\s*$')
            if value.match(str(x)):  # 不是数字
                return float(x)
            else:
                return float(0)

        colkeys_time = ['time']
        df_out_time = pd.DataFrame(data=None, columns=colkeys_time)
        for dd in half_time:
            start_time = '%s 00:00:00' % dd
            end_time = '%s 23:50:00' % dd
            start_times = pd.date_range(start=pd.Timestamp(start_time).round('10T'),
                                        end=pd.Timestamp(end_time).round('10T'),
                                        freq="10T")
            start_times_list = start_times.strftime('%Y-%m-%d %H:%M:%S').tolist()
            time_pd = pd.DataFrame(start_times_list, columns=colkeys_time)
            df_out_time = df_out_time.append(time_pd)
        grouped = df_cvr_month.groupby(['branch_id'])  # 通过key分组
        l_P = []
        l_R = []
        l_b = []
        df_time_len = df_out_time.shape[0]
        for dtype, group in grouped:
            dy = group['time'].dtypes
            df_out_time['time'] = df_out_time['time'].astype(dy)
            df_cv = df_out_time.merge(group, on=['time'], how='left')
            if (df_cv.shape[0] != df_time_len):
                df_cv.drop_duplicates('time', inplace=True)
            arr_c = df_cv['current_x'].apply(format).values
            arr_v = df_cv['current_y'].apply(format).values
            l_P.append(arr_v * arr_c)
            l_b.append(dtype)
            if len(l_R) == 0:
                arr_r = df_cv['radiance'].apply(format).values
                l_R.append(arr_r)
        # R = np.array(l_R[0],dtype=object)
        R = np.array(l_R[0])
        num = len(l_P)
        tpower = tpower / num
        if num < 4001:
            # P = np.array(l_P,dtype=object).T
            P = np.array(l_P).T
            x,y = BM(P, R, tpower, num)
            xx,yy = Rel(P, R, tpower, num)
            dftmp = pd.DataFrame([[nowtime, l_b[x], y]], columns=colkeys)
            df_out = df_out.append(dftmp)
            df_out.to_csv(savenamef, index=False, encoding="utf_8_sig")
            df_out.to_csv(mid_savepath, index=False, encoding="utf_8_sig")
            for zc_i, y_value in zip(l_b,yy):
                zc_n = zc_i.split('-')
                dftmp_re = pd.DataFrame([[nowtime, zc_n[0], zc_n[1], y_value]], columns=colkeys_re)
                df_out_re = df_out_re.append(dftmp_re)
            df_out_re.to_csv(savenamef_re, index=False, encoding="utf_8_sig")
        else:
            n_num = num // 2
            l_P1 = l_P[:n_num]
            l_P2 = l_P[n_num:]
            P1 = np.array(l_P1).T
            P2 = np.array(l_P2).T
            l_b1 = l_b[:n_num]
            l_b2 = l_b[n_num:]
            x1, y1 = BM(P1, R, tpower, n_num)
            x2, y2 = BM(P2, R, tpower, num - n_num)
            xx1, yy1 = Rel(P1, R, tpower, n_num)
            xx2, yy2 = Rel(P2, R, tpower, num - n_num)
            for zc_i, y_value in zip(l_b1, yy1):
                zc_n = zc_i.split('-')
                if np.isnan(y_value):
                    y_value = str(y_value)
                else:
                    y_value = round(y_value, 2)
                dftmp_re = pd.DataFrame([[nowtime, zc_n[0], zc_n[1], y_value]], columns=colkeys_re)
                df_out_re = df_out_re.append(dftmp_re)
            for zc_i, y_value in zip(l_b2, yy2):
                zc_n = zc_i.split('-')
                if np.isnan(y_value):
                    y_value = str(y_value)
                else:
                    y_value = round(y_value, 2)
                dftmp_re = pd.DataFrame([[nowtime, zc_n[0], zc_n[1], y_value]], columns=colkeys_re)
                df_out_re = df_out_re.append(dftmp_re)
            if y1>y2:
                dftmp = pd.DataFrame([[nowtime, l_b1[x1], y1]], columns=colkeys)
                df_out = df_out.append(dftmp)
                df_out.to_csv(savenamef, index=False, encoding="utf_8_sig")
                df_out.to_csv(mid_savepath, index=False, encoding="utf_8_sig")
            else:
                dftmp = pd.DataFrame([[nowtime, l_b2[x2], y2]], columns=colkeys)
                df_out = df_out.append(dftmp)
                df_out.to_csv(savenamef, index=False, encoding="utf_8_sig")
                df_out.to_csv(mid_savepath, index=False, encoding="utf_8_sig")
            df_out_re.to_csv(savenamef_re, index=False, encoding="utf_8_sig")
    except:
        df_out.to_csv(savenamef, index=False, encoding="utf_8_sig")
        df_out.to_csv(mid_savepath, index=False, encoding="utf_8_sig")
        logger.error(traceback.format_exc())
        raise Exception("step2:BM,Rel error!")
