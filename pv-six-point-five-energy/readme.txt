六点五段算法,各点电量的计算，包括：
组串理论电量、实际电量
汇流箱理论电量、实际电量
逆变器理论电量、实际电量
计算每个逆变器输入、输出电量
calculate.py:集中式计算代码
calculate_zc.py:组串式计算代码
-------------------------------------------------------------------------------------------------
（1）请求命令：python3 /home/qny/pv_data_process/pv-six-point-five/main.py --station_id 494
	其中参数:
	--station_id 是场站id
（2）结果csv保存路径
	结果csv保存路径配置在/configs/config.json中，可更改

	