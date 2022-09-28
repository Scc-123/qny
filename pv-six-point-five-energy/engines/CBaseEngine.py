# -*- coding: UTF-8 -*-
import configparser
import os
import traceback
import json
import logging
from logging.handlers import QueueHandler
## 日志等级
logging.basicConfig(level=logging.INFO)
## 日志系统
logger = logging.getLogger("INSTANCE")
## 日志格式
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(name)s:%(levelname)s: %(message)s"
)

## CBaseEngine 算法引擎基类
#
# This is a base engine class for implementing higher level CV engines
# Only a few methods need to be implemented, including
# 1. __config_validate(self, configs) checks the input configs
# 2. __init_engine(self, configs) initializes engines using the parameters in configs
# 3. process(self, *inputs) core function to solve some problems or realize applications
# 4. post_process(self, *input) post-processing to the output of process
# 5. prepare(self) the first function to run when thread starts
#
class CBaseEngine:
    ## 构造函数
    def __init__(self):
        pass

    ## 初始化函数
    # 根据配置文件初始化算法引擎
    #
    # @param    config_file_path    配置文件路径
    # @param    device_id           GPU编号，如果为负数，则使用CPU
    def init(self, config_file_path: str = None, device_id: int = None):


        if config_file_path is not None:
            ## 配置解析
            # self.configs = configparser.ConfigParser()
            # self.configs.read(config_file_path)
            with open(config_file_path, 'r') as load_f:
                self.configs =json.load(load_f)
            # config parameter checking
            try:
                self.__config_validate__(self.configs, device_id)
            except:
                raise RuntimeError
            logpath = self.configs["logpath"]
            logpath =os.path.join(logpath,"log.log")
            file_handler = logging.handlers.RotatingFileHandler(
                logpath, mode="a", maxBytes=50 * 1024 * 1024
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)

        # engine initialization
        try:
            self.__init_engine__()
        except:
            raise RuntimeError
    ## 配置合法性检查函数
    # 检查配置项是否符合期望，需继承重载
    # 
    # @param    configs     配置项字典
    # @param    device_id   GPU编号，如果为负数，则使用CPU
    def __config_validate__(self, configs: dict, device_id: int):
        raise NotImplementedError

    ## 引擎初始化
    # 该函数用于初始化底层算法。所有算法相关的初始化都在该函数内实现，
    # 例如模型初始化、超参数初始化等等。其中的初始化参数应来自self.configs。
    # 需继承重载
    def __init_engine__(self):
        raise NotImplementedError

    ## 预处理
    # 该函数用于一些偏工程的算法引擎准备。
    # 例如，在多线程环境下，MxNet 往 GPU 分配资源的时候，必须在线程函数内进行，此过程就需要放在该函数内。
    # 需继承重载
    def prepare(self):
        raise NotImplementedError

    ## 算法处理
    # 需继承重载
    # 该函数用于实现数据的处理。
    # 例如图像分类、目标检测等。返回值应为初始处理结果。目前，其输入为图像文件流。
    # @param    inputs  输入数据
    # @return   算法输出结果
    def process(self, *inputs):
        raise NotImplementedError

    ## 后处理
    # 需继承重载
    # 该函数用于实现后处理，其输入应为process函数的输出。
    # 例如结果的格式化等，目前推荐该函数的输出为一个字典。
    # @param    inputs  输入数据
    # @return   后处理输出结果
    def post_process(self, *input):
        raise NotImplementedError
