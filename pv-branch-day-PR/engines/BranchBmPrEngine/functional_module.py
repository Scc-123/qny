# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import re
import os
import json
import math
import timeit
from .data_clearning import insert_branch_id
from .v2.cvIVcul import cvIVcul
from .v2.cvWcul import cvWcul
from .v2.prAcul import prAcul
from .v2.CV_day import CV_day
from .v2.d_WScul import d_WScul
from .v2.cs_WScul import cs_WScul
from .v2.devide_class_onlyonebench import devide_class_onlyonebench
from .v2.partile_diag import partile_diag
from .v2.lift_evaluation_db import lift_evaluation_db
import warnings
warnings.filterwarnings("ignore")
import logging
import traceback
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")


def pa_time(dd):
    colkeys_time = ['time']
    df_out_time = pd.DataFrame(data=None, columns=colkeys_time)
    start_time = '%s 00:00:00' % dd
    end_time = '%s 23:50:00' % dd
    start_times = pd.date_range(start=pd.Timestamp(start_time).round('10T'),
                                end=pd.Timestamp(end_time).round('10T'),
                                freq="10T")
    start_times_list = start_times.strftime('%Y-%m-%d %H:%M:%S').tolist()
    time_pd = pd.DataFrame(start_times_list, columns=colkeys_time)
    df_out_time = df_out_time.append(time_pd)
    return df_out_time
def pa_time_b(dd,sss):
    colkeys_time = ['time','branch_no']
    df_out_time = pd.DataFrame(data=None, columns=colkeys_time)
    start_time = '%s 00:00:00' % dd
    end_time = '%s 23:50:00' % dd
    start_times = pd.date_range(start=pd.Timestamp(start_time).round('10T'),
                                end=pd.Timestamp(end_time).round('10T'),
                                freq="10T")


    start_times_list = start_times.strftime('%Y-%m-%d %H:%M:%S').tolist()
    for i in sss:
        l = [i]*144
        time_pd = pd.DataFrame([[start_times_list1,l1] for start_times_list1,l1 in zip(start_times_list,l)], columns=colkeys_time)
        df_out_time = df_out_time.append(time_pd)
    return df_out_time

class Function_process(object):
    def __init__(self, current, voltage, radiance, df_station, stationid, BR1, partile, loss_predict, loss_abnormal, nowtime, dsttime, savepath):
        self.stationid = stationid
        self.current = current
        self.voltage = voltage
        self.df_station = df_station
        self.radiance = radiance
        self.station_cap = df_station.loc[(df_station['id'] == stationid), ['capacity']].values  # 场站容量
        self.n_point = 144
        self.BR = BR1['device_code'].values
        self.partile = partile
        self.loss_predict = loss_predict
        self.loss_abnormal = loss_abnormal
        # dsttime\nowtime互调, dsttime=2022-9-6\nowtime=2022-9-5
        self.dsttime = dsttime
        self.nowtime = nowtime
        self.dsttimename = str(dsttime).replace('-', '')
        self.savepath = savepath
        self.df_out_time = pa_time(nowtime)

    def format(self, x):
        """
        把NAN和str替换为0
        :param x:
        :return:
        """
        value = re.compile(r'^\s*[-+]*[0-9]+\.*[0-9]*\s*$')
        if value.match(str(x)):  # 不是数字
            return float(x)
        else:
            return 0

    def dispersion_rate(self):
        '''
        集中式
        组串电流离散率，组串输出功率离散率
        :return:组串电流离散率lsl_i,  组串输出功率离散率lsl_p
        '''
        df_melted = pd.melt(self.voltage, id_vars=["time"], var_name="device_code", value_name="current")
        c_merge_o = self.current.merge(df_melted, on=['time', 'device_code'], how='left')
        c_merge_o['power'] = c_merge_o['current_x'].apply(self.format) * c_merge_o['current_y'].apply(
            self.format)
        c_merge_o = c_merge_o.merge(self.radiance, on=['time'], how='left')

        c_merge_o['radiance'] = c_merge_o['value']  # 统一辐照度名字
        c_merge_o.drop('value', axis=1, inplace=True)  # 删除一列
        head_list = list(set(c_merge_o["device_code"].values.tolist()))
        # savepath = r'D:\Desktop\清能院\final\ronghe\pv-branch-BM-PR\engines\BranchBmPrEngine\591_集中式\output'

        c_merge_o = insert_branch_id(c_merge_o)
        head_list1 = list(set(c_merge_o["branch_id"].values.tolist()))
        branch_num = len(head_list1)
        station_caps = (self.station_cap * 1000) / branch_num

        try:
            # 标杆信息
            cn, bri = self.BR[0].split('-')
            c_box = c_merge_o.iloc[:, :][c_merge_o.device_code == cn]
            if isinstance(c_box.branch_no.values[0], str):
                BM_R = c_box.iloc[:, :][c_box.branch_no == bri]
            else:
                BM_R = c_box.iloc[:, :][c_box.branch_no == int(bri)]  # 取出组串所有信息
            if len(BM_R) != 144:
                dy = BM_R['time'].dtypes
                self.df_out_time['time'] = self.df_out_time['time'].astype(dy)
                BM_R = self.df_out_time.merge(BM_R, on=['time'], how='left')
            BM_R_I = BM_R['current_x'].apply(self.format).values
            BM_R_U = BM_R['current_y'].apply(self.format).values
            BM_R_P = BM_R['power'].apply(self.format).values
        except:
            logger.error(traceback.format_exc())
            raise Exception("step2: Benchmark data acquisition error!")

        # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #
        colkeys_bw = ["time", "device_code"]
        for i in range(144):
            colkeys_bw.append(str(i + 1))
        df_out_bw = pd.DataFrame(data=None, columns=colkeys_bw)
        savenamef_bw = os.path.join(self.savepath, 'branch_warning_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        colkeys = ["time", "device_code", "branch_no", "value"]
        # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_d = pd.DataFrame(data=None, columns=colkeys)
        savenamef_d = os.path.join(self.savepath, 'branch_DIST_d_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_cs = pd.DataFrame(data=None, columns=colkeys)
        savenamef_cs = os.path.join(self.savepath, 'branch_DIST_cs_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_pr = pd.DataFrame(data=None, columns=colkeys)
        savenamef_pr = os.path.join(self.savepath, 'branch_PR_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_bp = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bp = os.path.join(self.savepath, 'batch_bias _power_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        df_out_bc = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bc = os.path.join(self.savepath, 'batch_bias _current_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        df_out_bv = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bv = os.path.join(self.savepath, 'batch_bias _vol_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        colkeys_ip = ["time", "device_code", "value"]
        # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_i = pd.DataFrame(data=None, columns=colkeys_ip)
        savenamef_i = os.path.join(self.savepath, 'branch_current_cv_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_p = pd.DataFrame(data=None, columns=colkeys_ip)
        savenamef_p = os.path.join(self.savepath, 'branch_power_efficiency_cv_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        for comb_name in head_list:
            combiner_box = c_merge_o.iloc[:, :][c_merge_o.device_code == comb_name]
            b_list = list(set(combiner_box["branch_no"].values.tolist()))
            s_i = []
            s_p = []
            for b_i in b_list:
                if isinstance(combiner_box.branch_no.values[0], str):
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == str(b_i)]
                else:
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == b_i]  # 取出组串所有信息
                if len(branch_i) != 144:
                    dy = branch_i['time'].dtypes
                    self.df_out_time['time'] = self.df_out_time['time'].astype(dy)
                    branch_i = self.df_out_time.merge(branch_i, on=['time'], how='left')
                I = branch_i['current_x'].apply(self.format).values
                U = branch_i['current_y'].apply(self.format).values
                P = branch_i['power'].apply(self.format).values
                R = branch_i['radiance'].apply(self.format).values
                s_i.append(I)
                s_p.append(P)
                zc_name = '{}-{}'.format(comb_name, b_i)

                # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    error_b = devide_class_onlyonebench(np.array(BM_R_P), np.array(U), np.array(I), np.array(R),
                                                        self.loss_predict, self.loss_abnormal, station_caps)
                    error_b.insert(0, zc_name)
                    error_b.insert(0, self.dsttime)

                    df_bw = pd.DataFrame([[e_b for e_b in error_b]], columns=colkeys_bw)
                    df_out_bw = df_out_bw.append(df_bw)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Real-time classification alarm error!")
                # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # 数据最终输出故障类型 # # # # # # # # # # # # # # # # # # # # # #
                try:
                    if "报警！严重故障" in error_b:
                        # partiles = self.partile.iloc[:, :][self.partile.device_code == str(self.BR[0])]
                        F1_cur = self.partile['F1_cur'].apply(format).values[0]
                        F2_cur = self.partile['F2_cur'].apply(format).values[0]
                        F1_vol = self.partile['F1_vol'].apply(format).values[0]
                        F2_vol = self.partile['F2_vol'].apply(format).values[0]
                        d1, d2, d3 = partile_diag(F1_cur, F2_cur, F1_vol, F2_vol, np.array(I), np.array(U), np.array(R))
                        for a1, a2, a3 in zip(d1, d2, d3):
                            if a1 != ' ' or a2 != ' ' or a3 != '':
                                T = branch_i['time'].values
                                colkeys_pd = ['time', 'radiation', 'I_%s' % zc_name, 'U_%s' % zc_name, 'Type',
                                              'behavior', 'reason']
                                df_out_pd = pd.DataFrame(data=None, columns=colkeys_pd)
                                savenamef_pd = os.path.join(self.savepath,
                                                            'XNYMD_%s_partile_diag__stationid_%s_%s.csv' % (
                                                                str(zc_name), str(self.stationid),
                                                                str(self.dsttimename)))
                                for i in range(len(d1)):
                                    dfpd = pd.DataFrame([[T[i], R[i], I[i], U[i], d1[i], d2[i], d3[i]]],
                                                        columns=colkeys_pd)
                                    df_out_pd = df_out_pd.append(dfpd)
                                df_out_pd.to_csv(savenamef_pd, index=False, encoding="utf_8_sig")
                                break
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Data final output fault type error!")
                # # # # # # # # # # # # # # # # # # # # # 数据最终输出故障类型 # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    dP, dC, dV = lift_evaluation_db(np.array(BM_R_P),np.array(BM_R_I),np.array(BM_R_U),np.array(P),np.array(I),np.array(U))
                    if np.isnan(dP) or np.isinf(dP):
                        dP = str(dP)
                    else:
                        dP = round(dP, 2)
                    if np.isnan(dC) or np.isinf(dC):
                        dC = str(dC)
                    else:
                        dC = round(dC, 2)
                    if np.isnan(dV) or np.isinf(dV):
                        dV = str(dV)
                    else:
                        dV = round(dV, 2)
                    df_bp = pd.DataFrame([[self.dsttime, comb_name, b_i, dP]], columns=colkeys)
                    df_out_bp = df_out_bp.append(df_bp)

                    df_bc = pd.DataFrame([[self.dsttime, comb_name, b_i, dC]], columns=colkeys)
                    df_out_bc = df_out_bc.append(df_bc)

                    df_bv = pd.DataFrame([[self.dsttime, comb_name, b_i, dV]], columns=colkeys)
                    df_out_bv = df_out_bv.append(df_bv)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: full life cycle assessment error!")
                # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    E_d = d_WScul(np.array(BM_R_P),np.array(P))
                    if np.isnan(E_d):
                        E_d = str(E_d)
                    else:
                        E_d = round(E_d, 2)
                    df_d = pd.DataFrame([[self.dsttime,comb_name, b_i, E_d]], columns=colkeys)
                    df_out_d = df_out_d.append(df_d)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate Euclidean distance error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    C_s = cs_WScul(np.array(BM_R_P),np.array(P))
                    if np.isnan(C_s):
                        C_s = str(C_s)
                    else:
                        C_s = round(C_s, 2)
                    df_cs = pd.DataFrame([[self.dsttime, comb_name, b_i, C_s]], columns=colkeys)
                    df_out_cs = df_out_cs.append(df_cs)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate cosine similarity error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    zc_pr_result = prAcul(P, R, station_caps)
                    if np.isnan(zc_pr_result[0][0]):
                        pr = str(zc_pr_result[0][0])
                    else:
                        pr = round(zc_pr_result[0][0], 2)
                    df_pr = pd.DataFrame([[self.dsttime, comb_name, b_i, pr]], columns=colkeys)
                    df_out_pr = df_out_pr.append(df_pr)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate string PR error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #

            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
            try:
                tt_i = np.array(s_i)
                cvs_i = cvIVcul(tt_i)
                if np.isnan(cvs_i):
                    cvs_i = str(cvs_i)
                else:
                    cvs_i = round(cvs_i,2)
                df_i = pd.DataFrame([[self.dsttime, comb_name, cvs_i]], columns=colkeys_ip)
                df_out_i = df_out_i.append(df_i)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Calculate the current dispersion rate error!")
            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #

            # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
            try:
                tt_p = np.array(s_p)
                cvs_p = cvWcul(tt_p)
                if np.isnan(cvs_p):
                    cvs_p = str(cvs_p)
                else:
                    cvs_p = round(cvs_p,2)
                df_p = pd.DataFrame([[self.dsttime, comb_name, cvs_p]], columns=colkeys_ip)
                df_out_p = df_out_p.append(df_p)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Calculate the power dispersion rate error!")
            # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_bw.to_csv(savenamef_bw, index=False, encoding="utf_8_sig")
        df_out_d.to_csv(savenamef_d, index=False, encoding="utf_8_sig")
        df_out_cs.to_csv(savenamef_cs, index=False, encoding="utf_8_sig")
        df_out_pr.to_csv(savenamef_pr, index=False, encoding="utf_8_sig")
        df_out_i.to_csv(savenamef_i, index=False, encoding="utf_8_sig")
        df_out_p.to_csv(savenamef_p, index=False, encoding="utf_8_sig")
        df_out_bp.to_csv(savenamef_bp, index=False, encoding="utf_8_sig")
        df_out_bc.to_csv(savenamef_bc, index=False, encoding="utf_8_sig")
        df_out_bv.to_csv(savenamef_bv, index=False, encoding="utf_8_sig")

    def dispersion_rate_zc(self):
        """
        组串式
        组串电流、电压离散率，组串输出功率离散率
        :return: 组串电流lsl_i、电压离散率lsl_u，组串输出功率离散率lsl_p
        """
        df = pd.merge(self.current, self.voltage, on=['time', 'branch_no', 'device_code'], how='left')
        head_list = list(set(df["device_code"].values.tolist()))
        df['power'] = df['current_x'].apply(self.format) * df['current_y'].apply(self.format)
        df = df.merge(self.radiance, on=['time'], how='left')

        df['radiance'] = df['value']  # 统一辐照度名字
        df.drop('value', axis=1, inplace=True)  # 删除一列
        # savepath = r'D:\Desktop\清能院\final\ronghe\pv-branch-BM-PR\engines\BranchBmPrEngine\536\output'

        df = insert_branch_id(df)
        head_list1 = list(set(df["branch_id"].values.tolist()))
        branch_num = len(head_list1)
        station_caps = (self.station_cap * 1000) / branch_num

        try:
            # 标杆信息
            cn, bri = self.BR[0].split('-')
            c_box = df.iloc[:, :][df.device_code == cn]
            if isinstance(c_box.branch_no.values[0], str):
                BM_R = c_box.iloc[:, :][c_box.branch_no == bri]
            else:
                BM_R = c_box.iloc[:, :][c_box.branch_no == int(bri)]  # 取出组串所有信息
            if len(BM_R) != 144:
                dy = BM_R['time'].dtypes
                self.df_out_time['time'] = self.df_out_time['time'].astype(dy)
                BM_R = self.df_out_time.merge(BM_R, on=['time'], how='left')
            BM_R_I = BM_R['current_x'].apply(self.format).values
            BM_R_U = BM_R['current_y'].apply(self.format).values
            BM_R_P = BM_R['power'].apply(self.format).values
        except:
            logger.error(traceback.format_exc())
            raise Exception("step2: Benchmark data acquisition error!")

        # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #
        colkeys_bw = ["time", "device_code"]
        for i in range(144):
            colkeys_bw.append(str(i + 1))
        df_out_bw = pd.DataFrame(data=None, columns=colkeys_bw)
        savenamef_bw = os.path.join(self.savepath, 'branch_warning_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        colkeys = ["time", "device_code", "branch_no", "value"]
        # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_d = pd.DataFrame(data=None, columns=colkeys)
        savenamef_d = os.path.join(self.savepath, 'branch_DIST_d_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #
        # colkeys_cs = ["time", "device_code","branch_no","value"]
        df_out_cs = pd.DataFrame(data=None, columns=colkeys)
        savenamef_cs = os.path.join(self.savepath, 'branch_DIST_cs_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_pr = pd.DataFrame(data=None, columns=colkeys)
        savenamef_pr = os.path.join(self.savepath, 'branch_PR_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_bp = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bp = os.path.join(self.savepath, 'batch_bias_power_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        df_out_bc = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bc = os.path.join(self.savepath, 'batch_bias_current_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))
        df_out_bv = pd.DataFrame(data=None, columns=colkeys)
        savenamef_bv = os.path.join(self.savepath, 'batch_bias_vol_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        colkeys_ip = ["time", "device_code", "value"]
        # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_i = pd.DataFrame(data=None, columns=colkeys_ip)
        savenamef_i = os.path.join(self.savepath, 'branch_current_cv_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电压离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_u = pd.DataFrame(data=None, columns=colkeys_ip)
        savenamef_u = os.path.join(self.savepath, 'branch_voltage_cv_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_p = pd.DataFrame(data=None, columns=colkeys_ip)
        savenamef_p = os.path.join(self.savepath,'branch_power_efficiency_cv_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        for comb_name in head_list:
            combiner_box = df.iloc[:, :][df.device_code == comb_name]
            b_list = list(set(combiner_box["branch_no"].values.tolist()))
            s_i = []
            s_u = []
            s_p = []
            for b_i in b_list:
                if isinstance(combiner_box.branch_no.values[0], str):
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == str(b_i)]
                else:
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == b_i]  # 取出组串所有信息
                if len(branch_i) != 144:
                    dy = branch_i['time'].dtypes
                    self.df_out_time['time'] = self.df_out_time['time'].astype(dy)
                    branch_i = self.df_out_time.merge(branch_i, on=['time'], how='left')
                I = branch_i['current_x'].apply(self.format).values
                U = branch_i['current_y'].apply(self.format).values
                P = branch_i['power'].apply(self.format).values
                R = branch_i['radiance'].apply(self.format).values
                s_i.append(I)
                s_u.append(U)
                s_p.append(P)
                zc_name = '{}-{}'.format(comb_name, b_i)
                # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    error_b = devide_class_onlyonebench(np.array(BM_R_P), np.array(U), np.array(I), np.array(R),
                                                        self.loss_predict, self.loss_abnormal, station_caps)
                    error_b.insert(0, zc_name)
                    error_b.insert(0, self.dsttime)
                    df_bw = pd.DataFrame([[e_b for e_b in error_b]], columns=colkeys_bw)
                    df_out_bw = df_out_bw.append(df_bw)

                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Real-time classification alarm error!")
                # # # # # # # # # # # # # # # # # # # # # # # # 实时分级告警 # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # 数据最终输出故障类型 # # # # # # # # # # # # # # # # # # # # # #
                try:
                    if "报警！严重故障" in error_b:
                        # partiles = self.partile.iloc[:, :][self.partile.device_code == str(self.BR[0])]
                        F1_cur = self.partile['F1_cur'].apply(format).values[0]
                        F2_cur = self.partile['F2_cur'].apply(format).values[0]
                        F1_vol = self.partile['F1_vol'].apply(format).values[0]
                        F2_vol = self.partile['F2_vol'].apply(format).values[0]
                        d1, d2, d3 = partile_diag(F1_cur, F2_cur, F1_vol, F2_vol, np.array(I), np.array(U), np.array(R))
                        for a1, a2, a3 in zip(d1, d2, d3):
                            if a1 != ' ' or a2 != ' ' or a3 != '':
                                T = branch_i['time'].values
                                colkeys_pd = ['time', 'radiation', 'I_%s' % zc_name, 'U_%s' % zc_name, 'Type', 'behavior',
                                              'reason']
                                df_out_pd = pd.DataFrame(data=None, columns=colkeys_pd)
                                savenamef_pd = os.path.join(self.savepath, 'XNYMD_%s_partile_diag__stationid_%s_%s.csv' % (
                                    str(zc_name), str(self.stationid), str(self.dsttimename)))
                                for i in range(len(d1)):
                                    dfpd = pd.DataFrame([[T[i], R[i], I[i], U[i], d1[i], d2[i], d3[i]]],
                                                        columns=colkeys_pd)
                                    df_out_pd = df_out_pd.append(dfpd)
                                df_out_pd.to_csv(savenamef_pd, index=False, encoding="utf_8_sig")
                                break
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Data final output fault type error!")
                # # # # # # # # # # # # # # # # # # # # 数据最终输出故障类型 # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    dP, dC, dV = lift_evaluation_db(np.array(BM_R_P), np.array(BM_R_I), np.array(BM_R_U), np.array(P),
                                                    np.array(I), np.array(U))
                    if np.isnan(dP) or np.isinf(dP):
                        dP = str(dP)
                    else:
                        dP = round(dP, 2)
                    if np.isnan(dC) or np.isinf(dC):
                        dC = str(dC)
                    else:
                        dC = round(dC, 2)
                    if np.isnan(dV) or np.isinf(dV):
                        dV = str(dV)
                    else:
                        dV = round(dV, 2)
                    df_bp = pd.DataFrame([[self.dsttime, comb_name, b_i, dP]], columns=colkeys)
                    df_out_bp = df_out_bp.append(df_bp)

                    df_bc = pd.DataFrame([[self.dsttime, comb_name, b_i, dC]], columns=colkeys)
                    df_out_bc = df_out_bc.append(df_bc)

                    df_bv = pd.DataFrame([[self.dsttime, comb_name, b_i, dV]], columns=colkeys)
                    df_out_bv = df_out_bv.append(df_bv)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: full life cycle assessment error!")
                # # # # # # # # # # # # # # # # # # # # # # # # 全寿命周期评估 # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    E_d = d_WScul(np.array(BM_R_P), np.array(P))
                    if np.isnan(E_d):
                        E_d = str(E_d)
                    else:
                        E_d = round(E_d, 2)
                    df_d = pd.DataFrame([[self.dsttime, comb_name, b_i, E_d]], columns=colkeys)
                    df_out_d = df_out_d.append(df_d)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate Euclidean distance error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算欧式距离 # # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    C_s = cs_WScul(np.array(BM_R_P), np.array(P))
                    if np.isnan(C_s):
                        C_s = str(C_s)
                    else:
                        C_s = round(C_s, 2)
                    df_cs = pd.DataFrame([[self.dsttime, comb_name, b_i, C_s]], columns=colkeys)
                    df_out_cs = df_out_cs.append(df_cs)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate cosine similarity error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算余弦相似度 # # # # # # # # # # # # # # # # # # # # # # # # #

                # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #
                try:
                    zc_pr_result = prAcul(P, R, station_caps)
                    if np.isnan(zc_pr_result[0][0]):
                        pr = str(zc_pr_result[0][0])
                    else:
                        pr = round(zc_pr_result[0][0], 2)
                    df_pr = pd.DataFrame([[self.dsttime, comb_name, b_i, pr]], columns=colkeys)
                    df_out_pr = df_out_pr.append(df_pr)
                except:
                    logger.error(traceback.format_exc())
                    raise Exception("step2: Calculate string PR error!")
                # # # # # # # # # # # # # # # # # # # # # # # # # 计算组串PR # # # # # # # # # # # # # # # # # # # # # # # # #

            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
            try:
                tt_i = np.array(s_i)
                cvs_i = cvIVcul(tt_i)
                # lsl_i[comb_name] = round(cvs_i, 2)
                if np.isnan(cvs_i):
                    cvs_i = str(cvs_i)
                else:
                    cvs_i = round(cvs_i, 2)
                df_i = pd.DataFrame([[self.dsttime, comb_name, cvs_i]], columns=colkeys_ip)
                df_out_i = df_out_i.append(df_i)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Calculate the current dispersion rate error!")
            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电流离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #

            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电压离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
            try:

                t_u = np.array(s_u)
                cvs_u = cvIVcul(t_u)
                if np.isnan(cvs_u):
                    cvs_u = str(cvs_u)
                else:
                    cvs_u = round(cvs_u, 2)
                df_u = pd.DataFrame([[self.dsttime, comb_name, cvs_u]], columns=colkeys_ip)
                df_out_u = df_out_u.append(df_u)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Calculate the voltage dispersion rate error!")
            # # # # # # # # # # # # # # # # # # # # # # # # # # # 计算电压离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #

            # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #
            try:
                tt_p = np.array(s_p)
                cvs_p = cvWcul(tt_p)
                if np.isnan(cvs_p):
                    cvs_p = str(cvs_p)
                else:
                    cvs_p = round(cvs_p, 2)
                df_p = pd.DataFrame([[self.dsttime, comb_name, cvs_p]], columns=colkeys_ip)
                df_out_p = df_out_p.append(df_p)
                # lsl_p[comb_name] = round(cvs_p, 2)
            except:
                logger.error(traceback.format_exc())
                raise Exception("step2: Calculate the power dispersion rate error!")
            # # # # # # # # # # # # # # # # # # # # # # # # # # 计算功率离散率 # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        df_out_bw.to_csv(savenamef_bw, index=False, encoding="utf_8_sig")
        df_out_d.to_csv(savenamef_d, index=False, encoding="utf_8_sig")
        df_out_cs.to_csv(savenamef_cs, index=False, encoding="utf_8_sig")
        df_out_pr.to_csv(savenamef_pr, index=False, encoding="utf_8_sig")
        df_out_i.to_csv(savenamef_i, index=False, encoding="utf_8_sig")
        df_out_u.to_csv(savenamef_u, index=False, encoding="utf_8_sig")
        df_out_p.to_csv(savenamef_p, index=False, encoding="utf_8_sig")
        df_out_bp.to_csv(savenamef_bp, index=False, encoding="utf_8_sig")
        df_out_bc.to_csv(savenamef_bc, index=False, encoding="utf_8_sig")
        df_out_bv.to_csv(savenamef_bv, index=False, encoding="utf_8_sig")

    def cv_days(self,iscenterlized,path,lim1,lim2,lim3):
        """
        全站设备生产情况一致性分析
        :param iscenterlized:是集中式还是组串式
        :param path:汇流箱或逆变器json文件
        :param lim1:取值范围
        :param lim2:取值范围
        :param lim3:取值范围
        :return:
        """
        colkeys_cv = ['time', 'device_code', 'value']
        df_out_cv = pd.DataFrame(data=None, columns=colkeys_cv)
        savenamef_cv = os.path.join(self.savepath, 'cbb_CV_day_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        colkeys_ss = ['time', 'dev_code', '1','2','3','4']
        df_out_ss = pd.DataFrame(data=None, columns=colkeys_ss)
        savenamef_ss = os.path.join(self.savepath, 'cbb_ss_day_stationid_%s_%s.csv' % (str(self.stationid), str(self.dsttimename)))

        if iscenterlized:
            # # # # # # # # # # # 集中式 # # # # # # # # # # # # # #
            devcode_name = "combinerCode"
        else:
            # # # # # # # # # # # 组串式 # # # # # # # # # # # # # #
            devcode_name = "inverterCode"

        colkeys = ['device_code', 'phalanx_id']
        df_out = pd.DataFrame(data=None, columns=colkeys)
        with open(path[0], 'rb') as f:
            combiner_box = json.load(f)
            for c_b in combiner_box:
                dftmp_re = pd.DataFrame([[c_b[devcode_name], c_b["boxTransformerId"]]], columns=colkeys)
                df_out = df_out.append(dftmp_re)
        c_merge_o = self.current.merge(df_out, on=['device_code'], how='left')
        grouped = c_merge_o.groupby(['phalanx_id'])  # 通过key分组
        for dtype, group in grouped:
            group1 = group.groupby(['device_code'])
            c_s1 = dict()
            for dtype2, group2 in group1:
                s_n = len(group2["current"]) % 144
                if s_n != 0:
                    b_l = list(set(group2["branch_no"].values.tolist()))
                    df_time_t = pa_time_b(self.nowtime, b_l)
                    dy = group2['time'].dtypes
                    df_time_t['time'] = df_time_t['time'].astype(dy)
                    group2 = df_time_t.merge(group2, on=['time','branch_no'], how='left')
                n = len(group2["current"]) // 144
                I = group2['current'].apply(self.format).values
                I = np.reshape(I,(n,144))
                I = np.array(I)
                cs = CV_day(I, 144)
                dftmp_cv = pd.DataFrame([[self.dsttime, dtype2, cs]], columns=colkeys_cv)
                df_out_cv = df_out_cv.append(dftmp_cv)
                c_s1[dtype2] = cs
            num1 = 0
            num2 = 0
            num3 = 0
            num4 = 0
            for k,v in c_s1.items():
                if v < lim1:
                    num1 = num1 + 1
                elif (v > lim1) and (v < lim2):
                    num2 = num2 + 1
                elif (v > lim2) and (v < lim3):
                    num3 = num3 + 1
                else:
                    num4 = num4 + 1
            dftmp_ss = pd.DataFrame([[self.dsttime, dtype, num1,num2,num3,num4]], columns=colkeys_ss)
            df_out_ss = df_out_ss.append(dftmp_ss)
        df_out_cv.to_csv(savenamef_cv, index=False, encoding="utf_8_sig")
        df_out_ss.to_csv(savenamef_ss, index=False, encoding="utf_8_sig")
