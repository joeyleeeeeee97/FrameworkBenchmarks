# -*- coding: UTF-8 -*-
import sys
import json as js
import os, getopt, argparse
from prettytable import PrettyTable
import hashlib
import time

workload_lists = ["fortune", "plaintext", "db", "update", "json", "query"]
result_dict = {}
connection_level = []
pipeline = []
queryIntervals = []

def parse_argument():
    parser = argparse.ArgumentParser(
        description = "Analyse json resluts from FrameWork BenchMark.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )    
    parser.add_argument(
        '--files',
        default = None,
        nargs='+',
        help='json result files'
    )
    parser.add_argument(
        '--datas',
        default=['latencyAvg'],
        nargs='+',
        help='interested datas'
    )
    args = parser.parse_args()
    return args

def read_files(args):
    global connection_level
    global queryIntervals
    global pipeline
    for f in args.files:
        result = open(f)
        json_text = result.read()
        json_obj = js.loads(json_text)
        raw_data = json_obj["rawData"]
        connection_level  = json_obj["concurrencyLevels"]
        queryIntervals = json_obj["queryIntervals"]
        pipeline = json_obj["pipelineConcurrencyLevels"]
        for workload in workload_lists:
            if (raw_data[workload]):
                for test_name,test_result in raw_data[workload].items():
                    update_result(test_name, f, workload, test_result);

def update_result(test_name, file_name, workload, test_result):
    if test_name not in result_dict:
        result_dict[test_name] = {}
    if workload not in result_dict[test_name]:
        result_dict[test_name][workload] = {}
    if file_name not in result_dict[test_name][workload]:
        result_dict[test_name][workload][file_name] = test_result

def print_table(args):
    for interested_data in args.datas:
        for k,workload_results in result_dict.items():
            for workload in workload_results:
                pt = PrettyTable()
                pt.title = "Test:" + k + ", Type: " + workload + ", Result: " + interested_data
                pt.field_names = [map_workload_to_field(workload)] + list(workload_results[workload].keys())
                for i in range(len(workload_results[workload][args.files[0]])):
                    data_row = [v[i].get(interested_data) for v in workload_results[workload].values()]
                    pt.add_row([map_workload_to_value(workload)[i]] + data_row)
                print(pt)

def map_workload_to_field(workload):
    if (workload == 'query'):
        return 'queryIntervals'
    elif (workload == 'plaintext'):
        return 'pipeline'
    else:
        return 'concurrencyLevel'

def map_workload_to_value(workload):
    if (workload == 'query'):
        return queryIntervals
    elif (workload == 'plaintext'):
        return pipeline
    else:
        return connection_level

def toms(s):
    if s is None:
        return '0';
    elif s.find('ms') != -1:
        return str(s.replace('ms', ''))
    elif s.find('us') != -1:
        return str(float(s.replace('us','')) / 1000)
    elif s.find('s') != -1:
        return str(float(s.replace('s', "")) * 1000)

if __name__ == "__main__":
    args = parse_argument()
    files = args.files
    interested_datas = args.datas
    read_files(args)
    print_table(args)