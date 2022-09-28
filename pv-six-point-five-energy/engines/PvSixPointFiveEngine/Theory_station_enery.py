import json
import pandas as pd
def Theory_station_energy(power, power_josn_path, power_no, station_id):
    power_id = pd.read_excel(power_no)  # 读出标杆信息
    dno_id = power_id[station_id].values  # 取出对应场站标杆
    l_inverter = []  # 标杆逆变器
    with open(power_josn_path, 'rb') as f1:
        Inverter = json.load(f1)
        # Inverter_dict = dict()
        for d_id in dno_id:
            if str(d_id) == 'nan' or str(d_id) == 'NAN':
                continue
            for i in range(len(Inverter)):
                if Inverter[i]['inverterNo'] == str(d_id):
                    l_inverter.append(Inverter[i]['inverterCode'])
                    continue
        f1.close()
    power_list = list(power.columns)
    inverter_num = len(power_list) - 1  # 场站逆变器数量
    power_sum = 0  # 所有标杆逆变器电量之和
    s_num = 0  # 看标杆数据是否丢失
    for inver_id in l_inverter:
        if inver_id not in power_list:
            # 看标杆数据是否丢失,丢失不计算
            s_num = s_num + 0
            continue
        pow = power[inver_id].values.sum()
        power_sum = power_sum + pow
    br_num = len(l_inverter) - s_num
    power_mean = power_sum / br_num  # mean(标杆逆变器功率)
    station_energy = power_mean * inverter_num / 6  # 场站理论发电量
    return station_energy

