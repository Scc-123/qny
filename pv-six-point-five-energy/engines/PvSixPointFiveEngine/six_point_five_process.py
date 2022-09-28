import os
import glob

# from .calculate import Calculate
# from .calculate_zc import CalculateZC
# from .data_clearning import DataClearning
from calculate import Calculate
from calculate_zc import CalculateZC
from data_clearning import DataClearning
import pandas as pd
import traceback
import time
import logging
import json
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")


def six_five_process(oripath,savepath,stationurl,stationid,dsttime,nowtime,power_no,iscenterlized=1):
    #---------------------------------------step1:路径整合-----------------------------------------------------------
    try:
        stationid = int(stationid)
        dsttimename = str(dsttime).replace('-','')
        nowtimename = str(nowtime).replace('-', '')
        savename_station = os.path.join(savepath, 'result_station_%s_%s.csv' % (str(stationid), str(nowtimename)))
        savename_energy = os.path.join(savepath, 'result_energy_%s_%s.csv' % (str(stationid), str(nowtimename)))
        savename_device = os.path.join(savepath, 'result_device_%s_%s.csv' % (str(stationid), str(nowtimename)))
        #获取辐照度csv url
        radianceurls = list(glob.glob(os.path.join(oripath,'*_radiation.csv')))
        radianceurl =  radianceurls[0]
        #获取汇流箱电流csv url
        currenturls = list(glob.glob(os.path.join(oripath, '*_current.csv')))
        currenturl = currenturls[0]
        #获取汇流箱电压csv url
        voltagaurls = list(glob.glob(os.path.join(oripath,'*_voltage.csv')))
        voltagaurl =voltagaurls[0]
        #获取逆变器交流输出功率csv url
        ACpowerurls = list(glob.glob(os.path.join(oripath, '*_power.csv')))
        ACpowerurl =ACpowerurls[0]
        #获取逆变器直流输入功率csv url
        DCpowerurls = list(glob.glob(os.path.join(oripath,'*_dcpower.csv')))
        DCpowerurl =DCpowerurls[0]
        #获取逆变器工作效率csv url
        # efficiencyurls = list(glob.glob(os.path.join(oripath, '*_efficiency.csv')))
        # efficiencyurl =efficiencyurls[0]
        # 获取汇流箱json url
        boxesurls = list(glob.glob(os.path.join(oripath, '*boxes.json')))
        with open(boxesurls[0], 'r', encoding='UTF-8') as load_f:
            boxejson = json.load(load_f)
        # 获取逆变器json url
        inverterurls = list(glob.glob(os.path.join(oripath, '*inverters.json')))
        with open(inverterurls[0], 'r', encoding='UTF-8') as load_f:
            inverterjson = json.load(load_f)
        # 获取电站类型的json(组串式？or集中式？)
        transformersurls = list(glob.glob(os.path.join(oripath, '*transformers.json')))
        with open(transformersurls[0], 'r', encoding='UTF-8') as load_f:
            transformerjson = json.load(load_f)
        arrtype = transformerjson[0]["arrayType"]
        if arrtype == '组串式':
            iscenterlized = 0
        # 场站信息csv
        df_station = pd.read_excel(stationurl)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step1: Path fusion error!")
    # -------------------------------------------------step2:数据清洗-------------------------------------------
    try:
        print('--step2：Data clearning...')
        DC = DataClearning(dstime=dsttime, nowtime=nowtime)
        df_radiance = DC.df_clearn(radianceurl)
        df_current = DC.df_clearn(currenturl)
        df_voltaga = DC.df_clearn(voltagaurl)
        df_acpower = DC.df_clearn(ACpowerurl)
        df_dcpower = DC.df_clearn(DCpowerurl)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step2: Data clearning error!")
    # --------------------------------------------step3:各点电量计算--------------------------------------------------
    try:
        scol = ["calculation_date", "energy", "point_id", "station_id"]
        df_station_out = pd.DataFrame(data=None, columns=scol)
        CE = Calculate()
        CEZC = CalculateZC()
        print('--step3-1：Inverter DC,AC energy calculate...')
        t1 = time.time()
        # ----------------------------step3-1:逆变器直流输入总电量，每一个逆变器直流输入电量-------------------------------
        energy_DC, energy_3 = CE.powers(df_dcpower)
        df_energyDC = pd.DataFrame(energy_DC.items(), columns=['inverter_id', 'energy_DC'])
        d = {scol[0]: dsttime, scol[1]: energy_3, scol[2]: 3, scol[3]: stationid}
        df_station_out = df_station_out.append(d, ignore_index=True)
        # -----------------------------step3-2:逆变器交流输出总电量，每一个逆变器交流输出电量------------------------------
        energy_AC, energy_4 = CE.powers(df_acpower)
        d = {scol[0]: dsttime, scol[1]: energy_4, scol[2]: 4, scol[3]: stationid}
        df_station_out = df_station_out.append(d, ignore_index=True)
        df_energyAC = pd.DataFrame(energy_AC.items(), columns=['inverter_id', 'energy_AC'])
        energy_DC_AC = df_energyDC.merge(df_energyAC, on='inverter_id', how='outer')
        # -----------------------------step3-3:场站，汇流箱，组串，理论和实际发电量计算--------------------------------------
        # energy_1(场站实际发电量), energy_c(汇流箱实际发电量), energy_b(组串实际发电量),
        # energy_2(场站理论发电量)，theory_energy_b(汇流箱理论发电量), theory_energy_c(汇流箱理论发电量)
        print('--step3-2：PV string ,combinerbox energy calculate about 40s...')
        #20220817-增加区分集中式和组串式电量计算的方法
        if iscenterlized:
            energy_1, energy_c, energy_b, energy_2, theory_energy_b, theory_energy_c = \
                CE.Actual_power(df_current, df_voltaga, stationid, df_dcpower, inverterurls[0], power_no)
        else:
            energy_1, energy_c, energy_b, energy_2, theory_energy_b, theory_energy_c = \
                CEZC.Actual_power(df_current, df_voltaga, stationid, df_dcpower, inverterurls[0], power_no)
        # starion_enery = CE.Theory_station_energy(df_dcpower, inverterurls[0], power_no, station_id)
        t2 = time.time()
        print('Energy calculate ：%f s' % (t2 - t1))
        # ------------------------------电站各点总电量结果整理-------------------------------------------------------------
        d = {scol[0]: dsttime, scol[1]: energy_1["station_id"], scol[2]: 1, scol[3]: stationid}
        df_station_out = df_station_out.append(d, ignore_index=True)
        d = {scol[0]: dsttime, scol[1]: energy_2["theory_energy_result"], scol[2]: 2, scol[3]: stationid}
        df_station_out = df_station_out.append(d, ignore_index=True)
        df_station_out.to_csv(savename_station, index=False)
        # ------------------------------电站各点每个构件电量整理-----------------------------------------------------------
        df_date = pd.DataFrame(data=[[dsttime]], columns=['calculation_date'])  # 日期
        # 组串
        df_theory_b = pd.DataFrame(theory_energy_b.items(), columns=['branch_id', 'energy_theory_branch'])
        df_b = pd.DataFrame(energy_b.items(), columns=['branch_id', 'energy_branch'])
        df_branch_out = df_theory_b.merge(df_b, on='branch_id', how='outer')  # 各个组串的理论，实际发电量
        # 汇流箱
        df_theory_c = pd.DataFrame(theory_energy_c.items(), columns=['combinerbox_id', 'energy_theory_combinerbox'])
        df_c = pd.DataFrame(energy_c.items(), columns=['combinerbox_id', 'energy_combinerbox'])
        df_c_out = df_theory_c.merge(df_c, on='combinerbox_id', how='outer')
        df_energy_out = pd.concat([df_date, df_branch_out, df_c_out, energy_DC_AC], axis=1)
        df_energy_out.to_csv(savename_energy, index=False)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step3: Energy calculate error!")
    # --------------------------------------------step4:汇流箱数据采集设备故障分析--------------------------------------------------
    #仅针对集中式电站进行分析
    try:
        if iscenterlized:
            print('--step4：Fault Analysis of combinerbox data collection ...')
            path =boxesurls[0]
            path1 = inverterurls[0]
            df_boxfailur_out = CE.Failure_Analysis(path, path1, energy_DC, energy_c, stationid, dsttime)
            df_boxfailur_out.to_csv(savename_device, index=False)
    except:
        logger.error(traceback.format_exc())
        raise Exception("step4:combinerbox fault Analysis error!")


# if __name__ == "__main__":
#     flag_quality = 1
#     if flag_quality:
#         oripath = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\920\536'
#         savepath = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\920\536\output'
#         stationcsvurl = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\pv-six-point-five-energy\configs\pv_station.xlsx'
#         powercsvurl = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\pv-six-point-five-energy\configs\station_inverter_no.xlsx'
#         station_id = 536
#         iscenterlized = 0
#         dsttime = '2022-08-17'
#         nowtime = '2022-08-18'
#         six_five_process(oripath, savepath, stationcsvurl, station_id, dsttime, nowtime,powercsvurl,iscenterlized)
if __name__ == "__main__":
    flag_quality = 1
    if flag_quality:
        oripath = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\920\591'
        savepath = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\920\591\output'
        stationcsvurl = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\pv-six-point-five-energy\configs\pv_station.xlsx'
        powercsvurl = r'D:\Desktop\qny_work\qny\final\pv-six_gengxin\pv-six-point-five-energy\configs\station_inverter_no.xlsx'
        station_id = 591
        iscenterlized = 1
        dsttime = '2022-08-23'
        nowtime = '2022-08-24'
        six_five_process(oripath, savepath, stationcsvurl, station_id, dsttime, nowtime, powercsvurl, iscenterlized)