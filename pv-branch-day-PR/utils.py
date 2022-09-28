import json
import getopt


## 参数解析函数
#   * station_id:        场站id
#   * is_centerlized:    是否是集中式，1位集中式,0为分布式
#   * log_path:             日志存储路径
#   * device_id:            GPU编号，如果为负数，则使用CPU
def parseInstanceConfig(argv):
    station_id = ""
    is_centerlized = 1
    try:
        opts, args = getopt.getopt(
            argv,
            "hc:s:d:",  # 短选项
            [
                "station_id=",
                "is_centerlized=",
            ],  # 长选项
        )
    except getopt.GetoptError:
        print("runInstance.py -s <station_id> -c <is_centerlized> ")
        raise RuntimeError("params in argv is wrong\n [[%s]]" % argv)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "runInstance.py -s <station_id> -c <is_centerlized>"
            )
            raise RuntimeError("params in config is wrong\n [[%s]]" % argv)
        elif opt in ("-s", "--station_id"):
            station_id = arg
        elif opt in ("-c", "--is_centerlized"):
            is_centerlized = arg

    configs = {
        "station_id": station_id,
        "is_centerlized": is_centerlized,
    }
    for key in configs.keys():
        if configs[key] is None or configs[key] == "":
            raise RuntimeError(
                "params in argv is wrong\n [[%s]]\n key:%s\n" % (argv, key)
            )
    return configs
