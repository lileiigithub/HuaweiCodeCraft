# -*- coding: UTF-8 -*-

from feature_extraction import one_line_input,get_date_freq_dict,date_object,date_str
import datetime

def get_X_y(date_freq_dict):
    # 获取输入 X,y
    X,y = [],[]
    _data_nums = count_data_nums(date_freq_dict)
    date_list = list(date_freq_dict.keys())
    date_list = date_list[10:] # 从第某天开始获取X
    for date in date_list:
        #print(date,one_line_input(date,date_freq_dict))
        X.append(one_line_input(date,date_freq_dict,_data_nums))
        y.append([date_freq_dict[date]])
    return X,y,_data_nums

def get_predict_X(_date_str,date_freq_dict,_data_nums):
    # 获取用于预测的X
    return one_line_input(_date_str, date_freq_dict,_data_nums)

def get_date_freq_pair(_flavor_name,ecs_array,predict_time):
    # 获取用于 预测的 日期 频数对
    return get_date_freq_dict(_flavor_name,ecs_array,predict_time)

def add_date_freq_dict(_date_str,_flavor_nums,_date_freq_dict):
    # 增加 预测的 日期 频数对
    _date_freq_dict[_date_str] = _flavor_nums

def get_predicting_date_list(predict_time):
    # 获得需要预测的日期列表
    predicting_date_list = []
    predict_begin_date = date_object(predict_time[0].split(' ')[0])
    predict_end_date = date_object(predict_time[1].split(' ')[0])
    for i in range((predict_end_date - predict_begin_date).days+1):
        predicting_date_list.append(date_str(predict_begin_date+datetime.timedelta(days=i)))
    return predicting_date_list

def count_data_nums(_ecs_array):
    # 计算数据量以确定特征数量
    return len(_ecs_array)













