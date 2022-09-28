# -*- coding: UTF-8 -*-
import logging
from engines.CBaseEngine import CBaseEngine
import os
from .six_point_five_process import six_five_process
import datetime

import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")

class PvSixPointFiveEngine(CBaseEngine):
    def __config_validate__(self,configs,device_id=-1):
        self.csvpath = os.path.join(configs["csvpath"])
        self.dstpath =os.path.join(configs["dstpath"])
        self.stationurl = os.path.join(configs["stationid_url"])
        self.powerurl = os.path.join(configs["dcpower_url"])
    def __init_engine__(self):
        logger.info("Initialization complete！")
        pass

    def prepare(self):
        logger.info("prepare is done!")
        pass

    def process(self,stationid):
        logger.info("start process")
        # ---------------------------------------step0:获取当前日期和目标日期-----------------------------------------------------------
        try:
            now_time = datetime.datetime.now()+ datetime.timedelta(days=-2)
            yes_time = now_time + datetime.timedelta(days=-1)
            print("ssssssssssssssssssssssssssssss")
            print(now_time)
            print(yes_time)
            dsttime = yes_time.strftime('%Y-%m-%d')
            dsttimename = dsttime.replace('-','')
            nowtime = now_time.strftime('%Y-%m-%d')
            nowtimename = nowtime.replace('-', '')
            logger.info("dsttime :%s"%(dsttime))
        except:
            logger.error(traceback.format_exc())
            raise Exception("step0: get dsttime error!")
        res = {"code":0,"des":''}
        # ---------------------------------------step1:路径整合-----------------------------------------------------------
        try:
            oripath = os.path.join(self.csvpath, str(nowtimename), str(stationid))
            if not os.path.exists(oripath):
                res["code"] = 2000
                logger.info('result:' + str(res))
                logger.error('%s is not exists !!'%(oripath))
                return res
            #结果保存路径生成
            if not os.path.exists(self.dstpath) :
                os.mkdir(self.dstpath)
            savepath = os.path.join(self.dstpath,str(nowtimename))
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            savepath = os.path.join(savepath, str(stationid))
            if not os.path.exists(savepath):
                os.mkdir(savepath)
        except:
            logger.error(traceback.format_exc())
            raise Exception("step1: Path fusion error!")
        # ---------------------------------------step2:六点五段电量计算算法部分-----------------------------------------------------------
        try:
            six_five_process(oripath, savepath, self.stationurl, stationid, dsttime, nowtime, self.powerurl)
        except:
            logger.error(traceback.format_exc())
            raise Exception("step2: six_five_process error!")
        return res

    def post_process(self):
        logger.info("start post process")
        pass