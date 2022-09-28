# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import re
import json
# from .Theory_station_enery import Theory_station_energy
from Theory_station_enery import Theory_station_energy

class Calculate(object):
    def __init__(self):
        pass

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

    def powers(self, power_data):
        """
        power_data:逆变器功率
        计算每个逆变器输出电量
        :return:result:每天每个逆变器输出电量,results:总电量
        """
        head_list = list(power_data.columns)  # 表头
        head_row_list = head_list[1:]  # 取出所有逆变器
        csv_result = power_data.iloc[:, 1:]
        row_list = csv_result.values.tolist()
        power = np.array(row_list)
        power[np.isnan(power)] = 0
        power_mid = power / 6
        powers = power_mid.sum(axis=0)
        results = round(powers.sum(), 2)
        result = dict()  # 一天每个逆变器输出电量
        for j, GS_XP in enumerate(head_row_list):
            result[GS_XP] = round(powers[j], 2)
        return result, results

    # def Theory_Energy(self, radiance, pv_station, branch_num, result_num, b_theory_result, station_id):
    #     """
    #     branch_num：组串总数
    #     result_num：汇流箱有多少组串
    #     计算整个场站的理论发电量, 组串、汇流箱理论发电量
    #     :return: 整个场站的理论发电量
    #     """
    #     radiance_sum = radiance[radiance.columns[1]].apply(self.format).values.sum()  # 辐照度总量
    #     capacity = pv_station.loc[(pv_station['id'] == station_id), ['capacity']].values  # 场站容量
    #     energy_theory = radiance_sum * capacity[0][0] / 6   # 场站理论发电量
    #     energy_theory = round(energy_theory, 2)
    #     theory_energy_result = {"theory_energy_result": energy_theory}
    #
    #     branch_theory_energy = energy_theory / branch_num  # 组串理论发电量
    #     branch_theory_energy = round(branch_theory_energy, 2)
    #     for k, v in b_theory_result.items():
    #         b_theory_result[k] = branch_theory_energy
    #     c_theory_energy_result = dict()  # 汇流箱论发电量
    #     for c_i, value in result_num.items():
    #         c_theory_energy_result[c_i] = round(branch_theory_energy * value, 2)
    #     return theory_energy_result, b_theory_result, c_theory_energy_result

    def Theory_Energy(self, branch_num, result_num, b_theory_result, station_id, power, power_josn_path, power_no):
        """
        branch_num：组串总数
        result_num：汇流箱有多少组串
        计算整个场站的理论发电量, 组串、汇流箱理论发电量
        :return: 整个场站的理论发电量
        """
        energy_theory = Theory_station_energy(power, power_josn_path, power_no, station_id)
        energy_theory = round(energy_theory, 2)
        theory_energy_result = {"theory_energy_result": energy_theory}
        branch_theory_energy = energy_theory / branch_num  # 组串理论发电量
        branch_theory_energy = round(branch_theory_energy, 2)
        for k, v in b_theory_result.items():
            b_theory_result[k] = branch_theory_energy
        c_theory_energy_result = dict()  # 汇流箱论发电量
        for c_i, value in result_num.items():
            c_theory_energy_result[c_i] = round(branch_theory_energy * value, 2)
        return theory_energy_result, b_theory_result, c_theory_energy_result

    def Actual_power(self, current, voltage, station_id, df_dcpower, inverterurls, power_no):
        """
        current：电流数据
        radiance：辐照度数据
        voltage：电压数据
        pv_station：场站容量
        计算理论、实际发电量
        :return: result(场站实际发电量), result_c(汇流箱实际发电量), result_b(组串实际发电量),
        theory_energy_result(场站理论发电量)，b_theory_energy_result(组串理论发电量), c_theory_energy_result(汇流箱理论发电量)
        """
        df_melted = pd.melt(voltage, id_vars=["time"], var_name="device_code", value_name="current")
        c_merge_o = current.merge(df_melted, on=['time', 'device_code'], how='left')
        c_merge_o['power'] = c_merge_o['current_x'].apply(self.format) * c_merge_o['current_y'].apply(self.format)
        head_list = list(set(c_merge_o["device_code"].values.tolist()))
        sums = 0
        result = dict()  # 整个场站发电量
        result_b = dict()  # 汇流箱发电量
        result_c = dict()  # 组串发电量
        result_num = dict()  # 组串数量（汇流箱）
        branch_num = 0
        for comb_name in head_list:
            # comb_name汇流箱名称
            sum_c = 0
            combiner_box = c_merge_o.iloc[:, :][c_merge_o.device_code == comb_name]  # 取出汇流箱（如取出GS_XP_13_001_01）所有信息
            b_list = list(set(combiner_box["branch_no"].values.tolist()))
            N = len(b_list)
            result_num[comb_name] = N
            branch_num = branch_num + N
            for i in b_list:
                if isinstance(combiner_box.branch_no.values[0], str):
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == str(i)]
                else:
                    branch_i = combiner_box.iloc[:, :][combiner_box.branch_no == i]  # 取出组串所有信息
                sum_b = branch_i['power'].sum() / 6000
                if i < 10:
                    s_d = '{}-0{}'.format(comb_name, i)
                else:
                    s_d = '{}-{}'.format(comb_name, i)
                sum_b = round(sum_b, 2)
                result_b[s_d] = sum_b
                sum_c = sum_c + sum_b  # 计算当前汇流箱发电量
            result_c[comb_name] = round(sum_c, 2)
            sums = sums + sum_c  # 计算整个场站发电量
        result["station_id"] = round(sums, 2)
        b_theory_result = result_b.copy()
        theory_energy_result, b_theory_energy_result, c_theory_energy_result = self.Theory_Energy(
            branch_num,result_num,b_theory_result,station_id,df_dcpower,inverterurls,power_no)
        return result, result_c, result_b, theory_energy_result, b_theory_energy_result, c_theory_energy_result

    def Failure_Analysis(self, path, path1, power_zhi, result_c, station_id, d_time):
        """
        :param path:汇流箱json
        :param path1:逆变器json
        :param power_zhi:逆变器直流发电量字典
        :param result_c:汇流箱发电量字典
        :param station_id:场站id
        :param d_time:日期（2022/7/27）
        :return:DataFrame 故障详情
        """
        combiner_dict = dict()
        with open(path, 'rb') as f:
            combiner_box = json.load(f)
            for i in range(len(combiner_box)):
                if combiner_box[i]['inverterId'] in combiner_dict.keys():
                    com_b = []
                    com_b.extend(combiner_dict[combiner_box[i]['inverterId']])
                    com_b.extend([combiner_box[i]['combinerCode'], combiner_box[i]['combinerBoxName']])
                    combiner_dict[combiner_box[i]['inverterId']] = com_b
                else:
                    combiner_dict[combiner_box[i]['inverterId']] = [combiner_box[i]['combinerCode'],
                                                                    combiner_box[i]['combinerBoxName']]
            f.close()
        with open(path1, 'rb') as f1:
            Inverter = json.load(f1)
            Inverter_dict = dict()
            for i in range(len(Inverter)):
                Inverter_dict[Inverter[i]['id']] = Inverter[i]['inverterCode']
            f1.close()
        Inverter_sum = dict()
        results = pd.DataFrame(columns=['d_time', 'details', 'dev_name', 'dev_no', 'dev_type', 'power', 'station_id'])
        for key_id, value in combiner_dict.items():
            sums = 0
            combiner_value = []
            for i in range(0, len(value), 2):
                if value[i] in result_c.keys():
                    sums = sums + result_c[value[i]]
                    combiner_value.append(result_c[value[i]])
                else:
                    sums = sums + 0
                    results = results.append(
                        pd.DataFrame({'d_time': [d_time], 'details': ['汇流箱未接入'], 'dev_name': [value[i + 1]],
                                      'dev_no': [value[i]], 'dev_type': ['汇流箱'], 'power': [-1],
                                      'station_id': [station_id]}), ignore_index=False)
                    combiner_value.append(-1)
            Inverter_sum[Inverter_dict[key_id]] = round(sums, 2)
            if abs(Inverter_sum[Inverter_dict[key_id]] - power_zhi[Inverter_dict[key_id]]) < 10:
                continue
            else:
                for j in range(len(combiner_value)):
                    if combiner_value[j] < 1 and combiner_value[j] != -1:
                        results = results.append(
                            pd.DataFrame({'d_time': [d_time], 'details': ['汇流箱采集器故障'], 'dev_name': [value[2*j + 1]],
                                          'dev_no': [value[2*j]], 'dev_type': ['汇流箱'], 'power': [combiner_value[j]],
                                          'station_id': [station_id]}), ignore_index=False)
        return results








