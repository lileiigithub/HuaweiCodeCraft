# -!- coding: utf-8 -!-
from __future__ import division
from collections import OrderedDict

def order_vmformat(vmformat,serverlist,reverse):
    if vmformat=='CPU':
        serverlist = sorted(serverlist,key=lambda x:x[1],reverse=reverse)
    else:
        serverlist = sorted(serverlist,key=lambda x:x[2],reverse=reverse)
    return serverlist
def get_value_vmname(vminfo,vmname):
    for item in vminfo:
        i = item.split(' ')
        if i[0]==vmname:
            return int(i[1]),int(i[2])
def IscheckOrderDict(myorder_dict):
    _sum = 0
    for key in myorder_dict:
        _sum += myorder_dict[key]
    if _sum != 0:
        return True
    else:
        return False
def IslastNonZeroKey(myorder_dict,key):
    result = ""
    for key_item in myorder_dict:
        if myorder_dict[key_item]>0:
            result = key_item
    if result == key:
        return True
    else:
        return False
#按照CPU或者MEM的顺序由大到小排序
def order_by_CPUOrMEM(vmFormat,vm_info,predict_result):
    if vmFormat[0] == "CPU":
         ordered_predict_result = sorted(predict_result,key=lambda key:get_value_vmname(vm_info,key[0])[0],reverse=True)
    else:
        ordered_predict_result = sorted(predict_result,key=lambda key:get_value_vmname(vm_info,key[0])[1],reverse=True)
    return ordered_predict_result
def get_server_params(server_params):
    server_params_string = server_params[0].split(" ")
    remainCPUCoreNum = int(server_params_string[0])
    remainMemoryNum = int(server_params_string[1])*1024
    return remainCPUCoreNum,remainMemoryNum
def list_to_orderdict(end_serverlist):
    end_order_dict = OrderedDict()
    for newitem in end_serverlist:
        for i in range(len(newitem[3])):
            if newitem[3][i] in end_order_dict:
                # value_num+=1
                end_order_dict[newitem[3][i]] += 1
            else:
                end_order_dict[newitem[3][i]] = 1
    return end_order_dict
#新的最佳适应算法
def best_fit(server_params,vmFormat,vm_info,predict_result):
    vmFormat[0].upper()
    #首先进行排序（由大到小）
    ordered_predict_result = order_by_CPUOrMEM(vmFormat,vm_info,predict_result)
    #获取服务器规格参数
    remainCPUCoreNum = get_server_params(server_params)[0]
    remainMemoryNum = get_server_params(server_params)[1]
    #初始化服务器存放列表
    serverlist=[]
    #有序数组存放去13、14、15规格的虚拟机之后的虚拟机字典形式为{["flavor12,2"],[],[]}
    order_dict = OrderedDict()
    if len(predict_result)>0:
        if vmFormat[0] == "CPU":
            #有多少个16核的虚拟机，就首先创建多少个服务器
            count_high_cpu = 0
            remove_high_predict_result = []
            for item in ordered_predict_result:
                #首先创建多个服务器
                if item[1] >0.0:
                    if item[0] == "flavor15" or item[0] == "flavor12":
                        for num in range(int(item[1])):
                            vmhighcpucores = get_value_vmname(vm_info,item[0])[0]
                            vmhighmemorynums = get_value_vmname(vm_info,item[0])[1]#计算每一个虚拟机规格对应的CPU和MEM
                            count_high_cpu+=1
                            serverlist.append([count_high_cpu,remainCPUCoreNum,remainMemoryNum,[]])
                            serverlist[count_high_cpu-1][1]-=int(vmhighcpucores)
                            serverlist[count_high_cpu-1][2]-=int(vmhighmemorynums)
                            serverlist[count_high_cpu-1][3].append(item[0])
                    else:
                        remove_high_predict_result.append((item[0],item[1]))
            for item in remove_high_predict_result:
                order_dict[item[0]] = item[1]
            i = 0
            server_id = count_high_cpu
            #外层循环判断当前字典是否还有没有放的虚拟机（判断所有value之和是否大于0）
            while IscheckOrderDict(order_dict):
                #标志位，跳出循环
                flag = True
                #遍历每一个字典
                for key in order_dict:
                    # value = order_dict[key]
                    #根据key得到CPU和内存
                    vmcpucores = get_value_vmname(vm_info,key)[0]
                    vmmemorynums = get_value_vmname(vm_info,key)[1]#计算每一个虚拟机规格对应的CPU和MEM
                    #内层循环处理每一个key
                    while order_dict[key] > 0:
                        #判断当前key是否是value非0的最后一个元素----避免进入死循环
                        last_nonzero_key_vmcpucores = 0.0
                        last_nonzero_keyvmmemorynums = 0.0
                        if IslastNonZeroKey(order_dict,key):
                            last_nonzero_key = key
                            last_nonzero_key_vmcpucores = get_value_vmname(vm_info,last_nonzero_key)[0]
                            last_nonzero_keyvmmemorynums = get_value_vmname(vm_info,last_nonzero_key)[1]#计算每一个虚拟机规格对应的CPU和MEM
                        if serverlist[i][1]>=int(vmcpucores) and serverlist[i][2]>=int(vmmemorynums):
                            serverlist[i][1]-=int(vmcpucores)
                            serverlist[i][2]-=int(vmmemorynums)
                            serverlist[i][3].append(key)
                            # value-=1
                            order_dict[key] -= 1
                        elif serverlist[i][1]>int(last_nonzero_key_vmcpucores) and serverlist[i][2]>int(last_nonzero_keyvmmemorynums):
                            break
                        #该型号没有放置完，但是当前已经使用的服务器放不下该种型号的
                        #放置下一个型号的,直到把该服务器放满
                        #重新创建一台服务器
                        else:
                            i+=1
                            if i >= server_id:
                                server_id+=1
                                serverlist.append([server_id,remainCPUCoreNum,remainMemoryNum,[]])
                                flag = False
                                break
                    if flag==False:
                        break
        else:
            i = 0
            server_id = 1
            serverlist.append([server_id,remainCPUCoreNum,remainMemoryNum,[]])
            for item in predict_result:
                order_dict[item[0]] = item[1]
            while IscheckOrderDict(order_dict):
                flag = True
                for key in order_dict:
                    # value = order_dict[key]
                    vmcpucores = get_value_vmname(vm_info,key)[0]
                    vmmemorynums = get_value_vmname(vm_info,key)[1]#计算每一个虚拟机规格对应的CPU和MEM
                    while order_dict[key] > 0:
                        last_nonzero_key_vmcpucores = 0.0
                        last_nonzero_keyvmmemorynums = 0.0
                        if IslastNonZeroKey(order_dict,key):
                            last_nonzero_key = key
                            last_nonzero_key_vmcpucores = get_value_vmname(vm_info,last_nonzero_key)[0]
                            last_nonzero_keyvmmemorynums = get_value_vmname(vm_info,last_nonzero_key)[1]#计算每一个虚拟机规格对应的CPU和MEM
                        if serverlist[i][1]>=int(vmcpucores) and serverlist[i][2]>=int(vmmemorynums):
                            serverlist[i][1]-=int(vmcpucores)
                            serverlist[i][2]-=int(vmmemorynums)
                            serverlist[i][3].append(key)
                            # value-=1
                            order_dict[key] -= 1
                        elif serverlist[i][1]>int(last_nonzero_key_vmcpucores) and serverlist[i][2]>int(last_nonzero_keyvmmemorynums):
                            break
                        #该型号没有放置完，但是当前服务器已经放不下该种型号的
                        #放置下一个型号的,直到把该服务器放满
                        #重新创建一台服务器
                        else:
                            i+=1
                            server_id+=1
                            serverlist.append([server_id,remainCPUCoreNum,remainMemoryNum,[]])
                            flag = False
                            break
                    if flag==False:
                        break
        print serverlist
        start_serverlist = []
        end_serverlist = []
        for server_pre in serverlist:
            if int(server_pre[1])>=16 and int(server_pre[2])>=16*1024:
                 end_serverlist.append(server_pre)
            else:
                start_serverlist.append(server_pre)
        end_order_dict = list_to_orderdict(end_serverlist)
        final_end_serverlist = []
        end_server_id = 1
        final_end_serverlist.append([end_server_id,remainCPUCoreNum,remainMemoryNum,[]])
        while IscheckOrderDict(end_order_dict):
            for end_key in end_order_dict:
                end_server_cpu = get_value_vmname(vm_info,end_key)[0]
                end_server_mem = get_value_vmname(vm_info,end_key)[1]
                while end_order_dict[end_key] > 0:
                    if final_end_serverlist[end_server_id-1][1]>=int(end_server_cpu) and final_end_serverlist[end_server_id-1][2]>=int(end_server_mem):
                        final_end_serverlist[end_server_id-1][1]-=int(end_server_cpu)
                        final_end_serverlist[end_server_id-1][2]-=int(end_server_mem)
                        final_end_serverlist[end_server_id-1][3].append(end_key)
                        end_order_dict[end_key] -= 1
                    else:
                        end_server_id+=1
                        final_end_serverlist.append([end_server_id,remainCPUCoreNum,remainMemoryNum,[]])

        myfinalserverlist=[]
        for ssl in start_serverlist:
            myfinalserverlist.append(ssl)
        for esl in final_end_serverlist:
            if len(esl[3])>0:
                esl[0] = len(myfinalserverlist)+1
                myfinalserverlist.append(esl)
        new_serverlist = myfinalserverlist
        alloction_list = []
        alloction_list.append(len(new_serverlist))
        finalserverlist = sorted(new_serverlist, key=lambda x: x[0])
        for server in finalserverlist:
            new_list = []
            new_list.append(str(server[0])),
            mydict = count_value(server[3])
            mydict = sorted(mydict.items(), key=lambda x: x[0])
            for item in mydict:
                new_list.append(item[0] + ' ' + str(item[1]))
            mystr = ''
            for newitem in new_list:
                mystr += (newitem+" ")
            if len(mystr)>0:
                mystr1 = mystr[:-1]
                alloction_list.append(mystr1)
            else:
                alloction_list.append(mystr)
        return alloction_list
    else:
        return None
#统计列表中所有元素的个数
def count_value(list):
    # list = sorted(list)
    new_dict = {}
    for item in list:
        new_dict[item] = list.count(item)
    return new_dict
#分配完成后，计算服务器总的资源利用率
#serverlist参数为服务器集合,server_params为服务器规格参数56 128 1200,vmFormat:CPU
# finalserverlist:[[1, 1, 3072, ['flavor1', 'flavor2', 'flavor2', 'flavor3']], [2, 1, 6144, ['flavor4', 'flavor5']], [3, 1, 4096, ['flavor5', 'flavor5']], [4, 3, 8192, ['flavor5']]]
def cal_resource_nonuse(server_params,vmFormat,finalserverlist):
    server_params_string = server_params[0].split(" ")
    cpu_sum = int(server_params_string[0])*len(finalserverlist)#CPU资源总量
    mem_sum = int(server_params_string[1])*1024*len(finalserverlist)#MEM资源总量
    cpu_used = 0#使用的CPU资源总量
    mem_used = 0#使用的MEM资源总量
    for i in range(0,len(finalserverlist)):
        #计算所有服务器剩余CPU容量
        cpu_used += finalserverlist[i][1]
        #计算所有服务器剩余mem容量
        mem_used += finalserverlist[i][2]
    if vmFormat[0] == 'CPU':
        return float(cpu_used)/cpu_sum
    else:
        return float(mem_used)/mem_sum
