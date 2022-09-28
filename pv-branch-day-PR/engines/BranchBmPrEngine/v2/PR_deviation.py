import numpy as np
import pandas as pd
import re
import os


def format(x):
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

def PR_deviation(path1_PR, path2_PRS, BR_s_v,savepath,stationid,datatime):
    """
    计算PR与设计值偏差、PR与动态基准值偏差
    :param path1_PR: 标准PR csv路径
    :param path2_PRS: PR csv路径
    :param BR_s_v: PR设计值
    :param savepath: 输出保存路径
    :param stationid: 场站id
    :param datatime: 日期
    :return:
    """
    datatime = str(datatime).replace('-', '')

    BR = pd.read_csv(path1_PR, encoding='gbk')
    BR_C = pd.read_csv(path2_PRS, encoding='gbk')

    results = BR_C.copy()
    results_prs = results.drop('value', axis=1, inplace=False)
    results_pr = results_prs.copy()

    BR_C['branch_ids'] = BR_C["device_code"].astype('str')+"-"+BR_C["branch_no"].astype('str')
    BR_n = BR['device_code'].values
    BR_v = BR_C.iloc[:, :][BR_C.branch_ids == str(BR_n[0])]['value'].apply(format).values  # PR动态基准值 即标杆PR值
    BR_v = BR_v[0]
    BR_C_v = BR_C['value'].apply(format).values   # PR待测值
    # BR_s_v = 0.85  # PR设计值
    PR_s = (BR_s_v - BR_C_v) / BR_s_v  # PR与设计值偏差（直接利用公式）
    PR_b = (BR_v - BR_C_v) / BR_v  # PR与动态基准值偏差
    PR_s = np.around(PR_s, 2)
    PR_b = np.around(PR_b, 2)
    results_pr['values'] = PR_b
    results_prs['values'] = PR_s

    savenamef_pr = os.path.join(savepath, 'batch_bias_db_stationid_%s_%s.csv' % (str(stationid), str(datatime)))
    savenamef_prs = os.path.join(savepath, 'batch_bias_design_stationid_%s_%s.csv' % (str(stationid), str(datatime)))
    results_pr.to_csv(savenamef_pr, index=False, encoding="utf_8_sig")
    results_prs.to_csv(savenamef_prs, index=False, encoding="utf_8_sig")


if __name__ == '__main__':
    path1_PR = r"D:\Desktop\清能院\final\ronghe\pv-branch-BM-PR\engines\BranchBmPrEngine\536\branch_peak_stationid_536_20220818.csv"
    path2_PRS = r"D:\Desktop\清能院\final\ronghe\pv-branch-BM-PR\engines\BranchBmPrEngine\536\output\branch_PR_stationid_536_1.csv"
    savepath = r'D:\Desktop\清能院\final\ronghe\pv-branch-BM-PR\engines\BranchBmPrEngine\536\output'
    BR_s_v = 0.85  # PR设计值
    stationid = 536
    datatime = "2022"
    PR_deviation(path1_PR, path2_PRS, BR_s_v, savepath,stationid,datatime)

