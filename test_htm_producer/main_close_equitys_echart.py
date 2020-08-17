import os
import series_result_echart as Base

def main():
    cur_path = os.getcwd()
    #在根目录下寻找策略名和目标数据文件
    result_file_info = Base.find_test_result_file(cur_path, "close_equity")
    policy = result_file_info[0]
    map_test_file = result_file_info[1]
    for contract in map_test_file:
        test_result_files = map_test_file[contract]
        if len(test_result_files) == 0:
            continue

        #获取时间戳集合，获取所有利润数据集合，利润数据集合是根据最后一个值从大到小排序
        time_set = []
        contract_all_datas = []
        for item in test_result_files.items():
            datas_margin = Base.read_close_equity(item[1])
            Base.merge_datas(time_set, contract_all_datas, item[0], datas_margin)

        #生成目标网页
        print contract
        web_path = Base.get_web_path(cur_path, policy, contract, "close_equity")
        Base.create_result_web(web_path, contract, time_set, "平仓盈亏", contract_all_datas)

if __name__ == '__main__':
    main()