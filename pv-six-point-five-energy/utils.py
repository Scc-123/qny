import json
import getopt


## 参数解析函数
#   * station_id:        场站id
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
            ],  # 长选项
        )
    except getopt.GetoptError:
        print("runInstance.py -s <station_id>")
        raise RuntimeError("params in argv is wrong\n [[%s]]" % argv)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "runInstance.py -s <station_id>"
            )
            raise RuntimeError("params in config is wrong\n [[%s]]" % argv)
        elif opt in ("-s", "--station_id"):
            station_id = arg

    configs = {
        "station_id": station_id,
    }
    for key in configs.keys():
        if configs[key] is None or configs[key] == "":
            raise RuntimeError(
                "params in argv is wrong\n [[%s]]\n key:%s\n" % (argv, key)
            )
    return configs
