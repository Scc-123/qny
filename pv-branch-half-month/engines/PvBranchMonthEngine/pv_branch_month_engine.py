# -*- coding: UTF-8 -*-
import logging
from engines.CBaseEngine import CBaseEngine
import os
from .branch_month_process import branch_month_process
import datetime
import glob
import json

import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")

class PvBranchMonthEngine(CBaseEngine):
    def __config_validate__(self,configs,device_id=-1):
        self.csvpath = os.path.join(configs["csvpath"])
        self.dstpath =os.path.join(configs["dstpath"])
        self.stationurl = os.path.join(configs["stationid_url"])
        self.midpath = os.path.join(configs["midpath"])
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
            now_time = datetime.datetime.now()
            # now_time = datetime.datetime.now() + datetime.timedelta(days=-4)
            nowtime = now_time.strftime('%Y-%m-%d')
            nowtimename = nowtime.replace('-', '')
            #获取前半个月的日期
            dsttimes = []
            half_time = []
            dsttimenames = []
            for i in range(-1,-15,-1):
                yes_time = now_time + datetime.timedelta(days=i)
                dsttime_later = now_time + datetime.timedelta(days=i + 1)
                dsttime = yes_time.strftime('%Y-%m-%d')
                # h_t = yes_time.strftime('%Y-%m-%d')
                half_time.append(dsttime)
                dsttimes.append(dsttime)
                dsttime_later = dsttime_later.strftime('%Y-%m-%d')
                dsttimename = dsttime_later.replace('-','')
                dsttimenames.append(dsttimename)
            logger.info("dsttime :%s"%(dsttimes))
        except:
            logger.error(traceback.format_exc())
            raise Exception("step0: get dsttime error!")
        res = {"code":0,"des":''}
        # ---------------------------------------step1:路径整合-----------------------------------------------------------
        try:
            oripaths =[]
            for dsttimename in dsttimenames:
                oripath = os.path.join(self.csvpath, str(dsttimename), str(stationid))
                oripaths.append(oripath)
                if not os.path.exists(oripath):
                    # res["code"] = 2000
                    logger.info('result:' + str(res))
                    logger.error('%s is not exists !!'%(oripath))
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
        # ---------------------------------------step2:算法部分-----------------------------------------------------------
        try:
            #判断是集中式or组串式电站？？
            iscenterlized = -1
            for oripath in oripaths:
                transformersurls = list(glob.glob(os.path.join(oripath, '*transformers.json')))
                if len(transformersurls) == 0:
                    continue
                with open(transformersurls[0], 'r', encoding='UTF-8') as load_f:
                    transformerjson = json.load(load_f)
                arrtype = transformerjson[0]["arrayType"]
                if arrtype == '组串式':
                    iscenterlized = 0
                    break
                elif arrtype == '集中式':
                    iscenterlized = 1
                    break
            if iscenterlized==-1:
                raise Exception("step2:judge iscenterlized error!")
            else:
                branch_month_process(oripaths, savepath, self.dstpath, self.stationurl, stationid, dsttimes, nowtime,iscenterlized,half_time,self.midpath)

        except:
            logger.error(traceback.format_exc())
            raise Exception("step2: pv_branch_half_process error!")

        return res

    def post_process(self):
        logger.info("start post process")
        pass