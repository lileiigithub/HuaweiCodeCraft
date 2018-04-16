# coding=utf-8
import implement
import allocation
import math
import copy

def predict_vm(ecs_lines, input_lines,realflavor_lines):
    # Do your work from here#
    predict_flavors_num = []
    result = []
    ecs_array = []
    server = []
    predict_flavors = []
    vm_format = []
    predict_time = []

    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result

    for item in ecs_lines:
        item = item.strip()
        if item.count('\t') == 2:
            values = item.strip().split("\t")
            uuid = values[0]
            flavorName = values[1]
            createTime = values[2]
            ecs_array.append((uuid,flavorName,createTime))

    for i in range(input_lines.count('\r\n')):
        input_lines.remove('\r\n')
    print input_lines
    for i in range(input_lines.count('\n')):
        input_lines.remove('\n')
    print input_lines

    server.append(input_lines[0].strip())
    flavor_num = int(input_lines[1].strip())
    for index in range(flavor_num):
        index = index+2
        flavor_line = input_lines[index].strip()
        predict_flavors.append(flavor_line)
    vm_format.append(input_lines[flavor_num+2].strip())
    predict_time.append(input_lines[flavor_num+3].strip())
    predict_time.append(input_lines[flavor_num+4].strip())

    print server,predict_flavors,vm_format,predict_time

    # parse parament over : ecs_array,server,predict_flavors,predict_time
    ## begin prediction ##
    #predict_a_flavor(ecs_array,predict_time,'flavor1')
    #assert 0
    for flavor in predict_flavors:
        flavor_name = flavor.split(' ')[0]
        flavor_nums = predict_a_flavor(ecs_array,predict_time,flavor_name)#+10
        predict_flavors_num.append((flavor_name,flavor_nums))

    print 'predict flavors num: ',predict_flavors_num
    realflavor_dict = get_real_flavor_dict(realflavor_lines)
    pre_score = calc_error(realflavor_dict,predict_flavors_num)

    ## begin assignment###
    allocation_list = allocation.best_fit(server,vm_format,predict_flavors,predict_flavors_num)
    print "allocation_list:\n", allocation_list
    all_score = allocation_score(allocation_list,vm_format)

    score = pre_score*all_score
    print "-----------------------------------------"
    print "总分数: ", score
    print "预测分数 ,分配比率  ", pre_score,all_score

    # assert 0
    count_flavors = 0
    predict_flavor_list = []
    for item in predict_flavors_num:
        count_flavors += item[1]
        predict_flavor_list.append(item[0]+' '+str(int(item[1])))
    predict_flavor_list.insert(0,str(int(count_flavors)))
    result = predict_flavor_list+['']+allocation_list  #+['\n']
    return result


def predict_a_flavor(_ecs_array,_predict_time,_flavor_name,):
    # predict a type of flavor
    return implement.predict_algorithm(_flavor_name,_ecs_array,_predict_time,_alpha=1.0,_beta=0)

def get_real_flavor_dict(_realflavor_lines):
    real_flavor_dict = {}
    for item in _realflavor_lines:
        key,value = eval(item)[0],eval(item)[1]
        real_flavor_dict[key] = value
    return real_flavor_dict

def calc_error(_realflavor_dict,_predict_flavors_num):
    predict_real = []
    for item in _predict_flavors_num:
        predict_real.append((item[0],int(item[1]),_realflavor_dict[item[0]]))
    print "predict_real:",predict_real
    predict_sub_real = []
    for item in predict_real:
        predict_sub_real.append(item[1]-item[2])

    error_sub = temp_error(predict_sub_real)
    error_predict = temp_error([i[1] for i in predict_real])
    error_real = temp_error([i[2] for i in predict_real])
    score = 1 - error_sub/(error_predict+error_real)
    print "predict score: ", score*100
    return score*100

def temp_error(_num_list):
    sum = 0.0
    for item in _num_list:
        sum += item**2
    return math.sqrt(float(sum)/len(_num_list))

def allocation_score(the_allocation_list,_vm_format):
    _allocation_list = copy.deepcopy(the_allocation_list)
    print "_allocation_list:",_allocation_list
    _flavor_info = {} # {"falvor1":(1,1024),...}
    _format = ["flavor1 1 1024","flavor2 1 2048","flavor3 1 4096","flavor4 2 2048","flavor5 2 4096","flavor6 2 8192",
               "flavor7 4 4096","flavor8 4 8192","flavor9 4 16384","flavor10 8 8192","flavor11 8 16384","flavor12 8 32768",
               "flavor13 16 16384","flavor14 16 32768","flavor15 16 65536"]

    server_cpu,server_mem = 56,128
    for line in _format:
        line = line.strip()
        name,cpu,mem = line.split(" ")[0],line.split(" ")[1],line.split(" ")[2]
        _flavor_info[name] = (int(cpu),int(mem))

    server_nums = _allocation_list[0]
    server_cpus = server_cpu*server_nums
    server_mems = server_mem*server_nums*1024

    allo_info = {} # 实际的分配 {"flavor1":35,...}
    del _allocation_list[0]
    for line in _allocation_list:
        line = line.strip()
        line_list = line.split(" ")
        del line_list[0]  # 去掉主机编号
        if len(line_list)%2 !=0:
            raise ValueError
        for i in range(len(line_list)/2):
            f_name = line_list[2*i]
            f_num = int(line_list[2*i+1])
            if f_name in allo_info:
                allo_info[f_name] +=  f_num
            else:
                allo_info[f_name] = f_num

    print allo_info

    used_sum = 0
    for key in allo_info:
        if _vm_format[0] == "CPU":
            used_sum += allo_info[key]*_flavor_info[key][0] # 0 : cpu
        else:
            used_sum += allo_info[key] * _flavor_info[key][1]  # 0 : mem
    if _vm_format[0] == "CPU":
        print used_sum, server_cpus
        _score = float(used_sum)/server_cpus
    else:
        print used_sum, server_mems
        _score = float(used_sum) / server_mems
    return _score


