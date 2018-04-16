# coding=utf-8
import math
import input_mat
from regression import Regression


def predict_algorithm(_flavor_name,_ecs_array,_predict_time,_alpha,_beta):
    predict_result = []
    # 获取日期,频数对
    date_freq_dict = input_mat.get_date_freq_pair(_flavor_name, _ecs_array, _predict_time)
    print _flavor_name," date_freq_dict：\n",date_freq_dict
    # 获取 输入
    X, y, train_data_nums = input_mat.get_X_y(date_freq_dict)
    print _flavor_name, "X,y: ",X,y
    # 获取 模型
    reg_obj = Regression(X,y)  #_alpha
    # 预测
    predict_date_list = input_mat.get_predicting_date_list(_predict_time)
    for date in predict_date_list:
        predict_X = input_mat.get_predict_X(date, date_freq_dict,train_data_nums)
        predict_X = [predict_X]
        predict_num_a_day = reg_obj.predict_ridge(predict_X)#predict_kernal_ridge(predict_X)#
        if reg_obj.isError == True:
            sum_p = 0
            for item in predict_X[0]:
                sum_p += item
            predict_num_a_day= sum_p/len(predict_X[0])
        else:
            predict_num_a_day = predict_num_a_day[0][0]
        predict_result.append(predict_num_a_day)
        input_mat.add_date_freq_dict(date, predict_num_a_day, date_freq_dict)  # predict_num_a_day[0][0]
        #print "date_freq_dict",date_freq_dict
    print '\n'+_flavor_name+' predict_result: ', predict_result
    # 对预测的每天数量累加
    predict_flavors_sum = 0 # add---
    for flavor in predict_result:
        # predict_flavors_sum += max(float(flavor[0][0]),0)
        predict_flavors_sum += float(flavor)  # flavor[0][0]
    predict_flavors_sum = max(predict_flavors_sum,0)
    return math.ceil(predict_flavors_sum)

