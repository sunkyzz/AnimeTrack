# ------------- 文件路径部分 ------------- #
# keyword文件地址
anime_config_path = './keywords.txt'
# magnets文件地址
magnet_config_path = './magnets.txt'
# aria2配置文件地址, 用于更新trakcers
aria2_config_path = './aria2_x64/aria2.conf'

# ------------- Be careful ------------- #
# 检查周期
check_frequence = 1800
# 输出函数
logout = print
# aria2 rpc地址
aria_rpc_url = "http://localhost:6800/jsonrpc"
# aria2 toekn 请确保与aria2.conf内 rpc-secret 一项一致 不一致的token会导致任务添加失败
aria_token = "ANIME_TRACK"
# trackers更新源
tracker_url = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt'