# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, '/usr/lib/python2.7/site-packages')
import json as js
import os, getopt, argparse, requests
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
    parser.add_argument(
        '--post',
        default='http://localhost:7001',
        help='where to post test results'
    )
    parser.add_argument(
        '--output',
        default=False,
        help='whether result as table or not'
    )
    parser.add_argument(
        '--env',
        default='default',
        help='test running envirment'
    )
    parser.add_argument(
        '--version',
        default='latest',
        help='whether result as table or not'
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
    if False == result_dict.has_key(test_name):
        result_dict[test_name] = {}
    if False == result_dict[test_name].has_key(workload):
        result_dict[test_name][workload] = {}
    if False == result_dict[test_name][workload].has_key(file_name):
        result_dict[test_name][workload][file_name] = test_result

def print_table(args):
    if (args.output==False):
        return;
    for interested_data in args.datas:
        for k,workload_results in result_dict.items():
            print "BechMarking " + k  + "\n"
            for workload in workload_results:
                print "Workload " + workload + "\n"
                pt = PrettyTable()
                pt.field_names = [map_workload_to_field(workload)] + workload_results[workload].keys()
                for i in range(len(workload_results[workload][args.files[0]])):
                    data_row = [v[i].get(interested_data) for v in workload_results[workload].values()]
                    pt.add_row([map_workload_to_value(workload)[i]] + data_row)
                print pt

def post_result(args):
    for k,workload_results in result_dict.items():
        for workload in workload_results:
            keyvalues = []
            throught_list = [v.get('totalRequests') for v in  workload_results[workload]['latest.json']]
            rt_list = [v.get('latencyAvg') for v in  workload_results[workload]['latest.json']]
            for i in range(len(throught_list)):
                kvpair = {}
                kvpair['stressLevel'] = str(map_workload_to_value(workload)[i])
                kvpair['keyName'] = 'througput'
                kvpair['value'] = str(throught_list[i])
                keyvalues.append(kvpair)
            for i in range(len(rt_list)):
                kvpair = {}
                kvpair['stressLevel'] = str(map_workload_to_value(workload)[i])
                kvpair['keyName'] = 'responseTime'
                kvpair['value'] = toms(rt_list[i])
                keyvalues.append(kvpair)
            headers={'Content-type':'application/json', 'Accept':'application/json'}
            post_json_key = ['testName', 'buildName', 'env', 'ciResults']
            post_json_val = [k + "-" + workload , args.version, args.env, keyvalues]
            post_json = dict(zip(post_json_key, post_json_val))
            token='8aosidnalknzfaasflkasmsdlaklknf'
            data=time.strftime("%y%m%d%H", time.localtime())+token
            hash_md5 = hashlib.md5(data)
            response = requests.post(args.post+'/openapi/testResult.json?token='+hash_md5.hexdigest(), json=post_json, headers=headers)
            print response.text
    
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
    post_result(args)
