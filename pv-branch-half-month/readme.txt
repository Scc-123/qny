本工程中实现逆变器相关算法，具体包括：
逆变器转换率，--输出：inverter_efficiency_%s_%s.csv
逆变器损耗率，--输出：inverter_loss_rate_%s_%s.csv
逆变器转换率离散率，--输出：inverter_efficiency_cv_day_%s_%s.csv
光伏电站标准化输出功率和辐照量间相关系数，
光伏电站标准化输出功率和辐照量间欧氏距离，
光伏电站标准化输出功率和辐照量间余弦相似度--输出：station_DIST_%s_%s.csv
----------------------------------------------------------------------------------------------
（1）请求命令：python3 /home/qny/pv_data_process/pv-inverter-day/main.py --station_id 494
	其中参数:
	--station_id 是场站id
（2）结果csv保存路径
	结果csv保存路径配置在/configs/config.json中，可更改

（3）csv输出错误码：
    -1:原数据问题
    'Null'：原数据为空
	