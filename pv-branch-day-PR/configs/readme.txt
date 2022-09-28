本工程中实现逆变器相关算法，具体包括:
二.3 组串PR，--输出:branch_PR_stationid_%s_%s.csv

二.7 全站设备生产情况一致性分析，--输出:cbb_CV_day_stationid_%s_%s.csv、cbb_ss_day_stationid_%s_%s.csv

三.1.1 组串电流、电压离散率，--输出:branch_current_cv_stationid_%s_%s.csv、branch_voltage_cv_stationid_%s_%s.csv
三.1.2 组串输出功率离散率 ，--输出:branch_power_efficiency_cv_stationid_%s_%s.csv
三.2.2.1 对各光伏组串与标杆组串输出功率间的欧氏距离进行计算 --输出:branch_DIST_d_stationid_%s_%s.csv
三.2.2.1 对各光伏组串与标杆组串输出功率间的余弦相似度进行计算--输出:branch_DIST_cs_stationid_%s_%s.csv
四.1 实时分级告警 --输出:branch_warning_stationid_%s_%s.csv

四.2 基于partile_setting数据最终输出故障类型 --输出:station DIST %s %s.csv

五.3 组串PR与设计值偏差 --输出:batch_bias_db_stationid_%s_%s.csv
五.4 PR与动态基准值偏差 --输出:batch_bias_design_stationid_%s_%s.csv

五.6 全寿命周期评估 --输出:batch_bias _power_stationid_%s_%s.csv、batch_bias _current_stationid_%s_%s.csv、batch_bias _vol_stationid_%s_%s.csv

(1)请求命令:python3/home/qny/pvdata process/pv-inverter-day/main.py--station id 494
其中参数:
--station_id 是场站id
(2)结果csv保存路径
结果csV保存路径配置在/configs/config.json中，可更改

