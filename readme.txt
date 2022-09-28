本工程中实现逆变器相关算法，具体包括：
标杆组串选取，--输出：branch_peak_%s_%s.csv
组串PR统计性计算，可靠性描述标杆，--输出：branch_PR _reliability_by_15d_%s_%s.csv
----------------------------------------------------------------------------------------------
（1）请求命令：python3 /home/qny/pv_data_process/pv-inverter-day/main.py --station_id 494
	其中参数:
	--station_id 是场站id
（2）结果csv保存路径
	结果csv保存路径配置在/configs/config.json中，可更改

（3）csv输出错误码：
    -1:原数据问题
    'Null'：原数据为空
	