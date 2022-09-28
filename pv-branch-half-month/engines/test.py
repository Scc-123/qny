from PvBranchMonthEngine.branch_month_process import branch_month_process
import json

if __name__ == "__main__":
    # oripath = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\591_集中式'
    # savepath = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\591_集中式'
    # transformersurl = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\591_集中式\transformers.json'
    # stationcsvurl = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\591_集中式\pv_station.xlsx'
    # station_id =591
    # dsttime = '2022-08-15'
    # nowtime = '2022-08-16'

    oripath = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\536'
    savepath = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\536'
    transformersurl = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\536\transformers.json'
    stationcsvurl = r'D:\Desktop\清能院\final\ronghe\pv-branch-day-PR_0825\engines\BranchBmPrEngine\536\pv_station.xlsx'
    station_id = 536
    dsttime = '2022-08-17'
    nowtime = '2022-08-18'

    oripaths = []
    dsttimes = []
    for i in range(0,2):#30
        oripaths.append(oripath)
        dsttimes.append(dsttime)
    with open(transformersurl, 'r', encoding='UTF-8') as load_f:
        transformerjson = json.load(load_f)
    arrtype = transformerjson[0]["arrayType"]
    if arrtype == '组串式':
        iscenterlized = 0
    elif arrtype == '集中式':
        iscenterlized = 1
    # iscenterlized = 0
    branch_month_process(oripaths, savepath, stationcsvurl, station_id, dsttimes, nowtime,iscenterlized)
