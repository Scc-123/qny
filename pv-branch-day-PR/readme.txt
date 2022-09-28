（一）功能说明
标杆组串，组串PR相关算法
请求频次：1次/天
具体包含如下功能模块：
三.1.1	  cvIVcul	组串电流、电压离散率
三.1.2	  cvWcul	组串输出功率离散率
三.2.2.1  d_WScul	对各光伏组串与标杆组串输出功率间的欧氏距离进行计算。
三.2.2.2  cs_WScul	对各光伏组串与标杆组串输出功率间的余弦相似度进行计算。
四.1	  devide_class_onlyonebench	实时分级告警
四.2	  partile_diag	基于partile_setting数据最终输出故障类型
二.7	  CV_day	全站设备生产情况一致性分析
二.3	  prAcul	组串PR
五.3	  PR_deviation	组串PR与设计值偏差
五.4	  batch_bias_db 组串各自与动态基准值的PR偏差
五.6	  lift_evaluation_db 组串各自与动态基准值的功率偏差
（二）请求方式及示例说明
python3 /home/qny/pv_data_process/pv-branch-day-PR/main.py --station_id 491
python3 /home/qny/pv_data_process/pv-branch-day-PR/main.py --station_id 494

--station_id 场站id