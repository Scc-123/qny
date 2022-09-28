from engines.PvBranchMonthEngine.pv_branch_month_engine import  PvBranchMonthEngine
import logging
import sys
import traceback
from utils import parseInstanceConfig
import os
path = r"/home/qny/pv_data_process/pv-branch-half-month/"
retval = os.getcwd()
print ("run path now: %s" % retval)
os.chdir( path )
retval = os.getcwd()
print ("run path modified: %s" % retval)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(pathname)s:%(lineno)s:%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger("INSTANCE")

engine =PvBranchMonthEngine()
def main(argv):
    try:
        configs = parseInstanceConfig(argv)
        logger.info("parseInstanceConfig finished!")
    except:
        logger.error("parseInstanceConfig failed\n%s" % traceback.format_exc())
    try:
        configpath = './configs/config.json'
        engine.init(config_file_path=configpath, device_id=-1)
        engine.prepare()
        logger.info("init finished!")
    except:
        logger.error("init failed\n%s" % traceback.format_exc())
        raise Exception(traceback.format_exc())
    try:
        logging.info("start")
        result = engine.process(stationid = str(configs["station_id"]))
        if result["code"]==0:
            logger.info("process finished!")
        else:
            logger.error("process failed!! code:%d",result["code"])
    except:
        logger.error("process failed\n%s" % traceback.format_exc())


if __name__ == "__main__":
    main(sys.argv[1:])
