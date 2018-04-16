# -*- coding: UTF-8 -*-
import datetime
from collections import OrderedDict
import copy

def date_object(_date_str):
    return datetime.date(int(_date_str.split('-')[0]),int(_date_str.split('-')[1]),int(_date_str.split('-')[2]))

def date_str(_date_obj):
    return _date_obj.strftime("%Y-%m-%d")

# 计算日期间隔
def calc_preid(_begin_date_obj,_end_date_obj):
    return (_end_date_obj - _begin_date_obj).days

# 计算某天前的日期
def calc_somedate_str(_date_str,_days_before_int):
    return date_str(date_object(_date_str)-datetime.timedelta(days=_days_before_int))

def get_date_freq_dict(_flavor_name,ecs_array,predict_time):
    # 计算每天某种型号出现的频数,输出 日期,频数对 为有序字典
    date_list = []  # 解析的日期字符
    ecs_begin_date = date_object(ecs_array[0][2].split(' ')[0])
    predict_begin_date = date_object(predict_time[0].split(' ')[0])
    date_freq_pair = OrderedDict()  # 有序字典
    for i in range((predict_begin_date-ecs_begin_date).days):
        date_freq_pair[date_str(ecs_begin_date+datetime.timedelta(days=i))] = 0
    for item in ecs_array:
        falvor = item[1]
        if falvor == _flavor_name:
            date = item[2].strip().split(' ')[0]
            date_list.append(date)
    for date in date_list:
        date_freq_pair[date] += 1
    remove_excptional_dot(date_freq_pair) # 去除异常点
    return date_freq_pair

def print_num(_date_freq_pair):
    num = []
    for item in _date_freq_pair:
        num.append(_date_freq_pair[item])
    print num

def remove_excptional_dot(_date_freq_pair):
    sorted_date_list = sorted(_date_freq_pair,key=lambda x:_date_freq_pair[x],reverse = True)
    exception_day = sorted_date_list[0]
    #print "exception_day: ", exception_day
    mean_num = (_date_freq_pair[sorted_date_list[1]]+_date_freq_pair[sorted_date_list[2]])/2.0
                # _date_freq_pair[sorted_date_list[3]]+_date_freq_pair[sorted_date_list[4]])/4.0
    _date_freq_pair[exception_day] = mean_num

def get_week_day(_date_str):
    return date_object(_date_str).weekday()

#对星期几进行独热编码  # 输入 0-6
def week_one_hot(_week_int):
    hot = (2**6)>>_week_int
    return bin(hot).split('0b')[-1].zfill(7)

#是否是周末
def is_weekend(_date_str):
    return int(get_week_day(_date_str) < 5)

#前一天是否有申请
def is_one_before(_date_str,_dict):
    return int(_dict[calc_somedate_str(_date_str,1)] == 0)

#前2天是否有申请
def is_two_before(_date_str,_dict):
    return int(_dict[calc_somedate_str(_date_str,2)] == 0)

def is_three_before(_date_str,_dict):
    return int(_dict[calc_somedate_str(_date_str,3)] == 0)
#前两周的总申请数
def two_weeks_flavor(_date_str,_dict):
    sum = 0
    for i in range(1,15):
        day = calc_somedate_str(_date_str,i)
        if day in _dict:
            sum = sum + _dict[day]
    return sum/14.0

def normalization(line):
    # 0-1 归一化
    max_num,min_num = 0,100
    for num in line:
        if num>max_num:
            max_num = num
        if num<min_num:
            min_num = num
    line = [(float((i-min_num))/(max_num-min_num)) for i in line]
    #print　line
    return line

def somday_before_num(_someday,_date_str,_dict):
    # _someday为大于１的正值
    day = calc_somedate_str(_date_str,_someday)
    return _dict[day]

def someday_before_sum(_days,_date_str,_dict):
    # days 取值
    sum = 0
    for i in range(1,_days+1):
        day = calc_somedate_str(_date_str,i)
        if day in _dict:
            sum = sum + _dict[day]
    return sum#/float(_days)

def calc_diff(_date_freq_pair):
    # 计算申请数的一阶微分
    freq = _date_freq_pair.values()
    diff = [0]
    for i in range(len(freq)):
        if i + 1 < len(freq):
            diff.append(freq[i] - freq[i + 1])
    date_diff_pair = copy.deepcopy(_date_freq_pair)
    if len(diff) != len(date_diff_pair.values()):
        print "列表长度不符"
        raise ValueError
    index = 0
    for key in date_diff_pair:
        date_diff_pair[key] = diff[index]
        index += 1
    return date_diff_pair

def calc_peak(_date_diff_pair):
    old_freq = 0
    peak_date = []
    old_day = ""
    for key in _date_diff_pair:
        new_freq = _date_diff_pair[key]
        if old_freq<0 and new_freq >0:  # 定义波峰
            peak_date.append(old_day)
        old_freq = new_freq
        old_day = key
    return peak_date

def calc_real_peak(_peak_date,_date_freq_pair):
    real_peak = []
    peak_freq_list = []  #
    for _date in _peak_date:
        peak_freq_list.append((_date,_date_freq_pair[_date]))
    print  peak_freq_list
    peak_freq_list = sorted(peak_freq_list,key=lambda x:x[1],reverse = True)
    if len(peak_freq_list) >= 2:
        _mean = peak_freq_list[len(peak_freq_list)//2][1]
        print "_mean: ",_mean
    else:
        return _peak_date
    print "peak_freq_list: ",peak_freq_list
    for _date in _peak_date:
        if _date_freq_pair[_date] >= _mean:
            real_peak.append(_date)
    return real_peak

def calc_peak_period(_real_peak):
    period_list = []
    for i in range(len(_real_peak)):
        if i+1<len(_real_peak):
            period = calc_preid(date_object(_real_peak[i]),date_object(_real_peak[i+1]))
            period_list.append(period)
    period_list.sort()
    print "period_list: ",period_list
    if len(period_list)>=2:
        return period_list[len(period_list)//2]  # +1
    else: return 5

def previous_peak_info(_date_str,_peak_date,_date_freq_pair):
    previous_date = ""
    from_peak_days = 0 # 波峰日期距离现在的天数
    for date_str in _peak_date:
        if date_object(date_str)<date_object(_date_str):
            previous_date = date_str
        else:
            break
    if previous_date!="":
        from_peak_days = calc_preid(date_object(previous_date),date_object(date_str))
    else:
        return 0,0
    return from_peak_days,_date_freq_pair[previous_date]  # 波峰日期距离现在的天数,和其申请数量

def count_peak(_date_str,_peak_date):
    sum = 0
    for date_str in _peak_date:
        if date_object(date_str) < date_object(_date_str):
            sum += 1
    return sum

def one_line_input(_date_str,date_freq,_data_nums):
    # peak_date =calc_peak(calc_diff(date_freq))
    #
    # print "peak_date1: ",peak_date
    # peak_date = calc_real_peak(peak_date,date_freq)
    # print "peak_date2: ", peak_date
    # period = calc_peak_period(peak_date)
    #
    # if period < 5:
    #     period = 5
    #     print "period < 5"
    # print "period: " , period
    line = []
    # line.append(is_one_before(_date_str,date_freq))
    # line.append(is_two_before(_date_str,date_freq))
    # line.append(is_three_before(_date_str, date_freq))
    line.append(is_weekend(_date_str))
    line.append(somday_before_num(1,_date_str, date_freq))
    # line.append(somday_before_num(2, _date_str, date_freq))
    # line.append(somday_before_num(3, _date_str, date_freq))
    # line.append(somday_before_num(4,_date_str, date_freq))
    # line.append(somday_before_num(5, _date_str, date_freq))
    # line.append(somday_before_num(6, _date_str, date_freq))
    # line.append(somday_before_num(7,_date_str, date_freq)) #
    # line.append(somday_before_num(8, _date_str, date_freq))
    # line.append(somday_before_num(9, _date_str, date_freq))
    line.append(somday_before_num(10, _date_str, date_freq))
    # line.append(someday_before_sum(2,_date_str, date_freq))
    # line.append(someday_before_sum(3,_date_str, date_freq)) #
    # line.append(someday_before_sum(4,_date_str, date_freq))
    # line.append(someday_before_sum(5,_date_str, date_freq))
    # line.append(someday_before_sum(6,_date_str, date_freq))
    # line.append(someday_before_sum(7,_date_str, date_freq))
    # line.append(someday_before_sum(8, _date_str, date_freq))
    line.append(someday_before_sum(9, _date_str, date_freq))
    # line.append(someday_before_sum(10, _date_str, date_freq))
    # one_hot_list = list(week_one_hot(get_week_day(_date_str)))
    # # one_hot_list = [int(i) for i in one_hot_list]
    # # line.extend(one_hot_list)
    #
    # line = normalization(line)
    # line.append(somday_before_num(period-1, _date_str, date_freq))
    # line.append(somday_before_num(period, _date_str, date_freq))
    # line.append(somday_before_num(period+1, _date_str, date_freq))
    # previous_peak_info(_date_str,peak_date,date_freq)[0]
    # previous_peak_info(_date_str, peak_date, date_freq)[1]
    return line



