# -*- coding: utf-8 -*-
import time
import os
import pandas as pd
import numpy as np

os.chdir("C:\\Users\hengh\Desktop\QyjsCompare\Table") # 更改工作目录
# print(os.getcwd()) # 打印当前工作目录
start = time.time()
#————————————————————————————————————————————————————————————————————————————————————————————-
print("开始读取输入表格")
#读取输入表格
flow = pd.read_csv("flow.csv",encoding = 'UTF-8')
route = pd.read_csv("route_层级集散_40_80%_40%_无route2.csv",encoding = 'UTF-8')
distance = pd.read_csv("85中心局之间的距离.csv",encoding = 'UTF-8')
cost_detail = pd.read_csv("cost_detail_层级集散_40_80%_40%.csv",encoding = 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
#函数
def statistics(flow,route,distance,cost_detail):
    statistics = pd.DataFrame()
    route['总距离'] = 0 #初始化距离列
    for i in range(0,route.shape[0]):
        temp_route = route.loc[i,'路线'].split('-') #拆路线
        print(i)
        for m in range(0,(len(temp_route) - 1)):
            route.loc[i,'总距离'] += float(distance.loc[(distance['收寄城市'] == temp_route[m]) & (distance['寄达城市'] == temp_route[m+1])]['距离'])  #单个提取距离并累加

    total_data = pd.merge(route, flow, how='left', on=['收寄城市', '寄达城市'])  #连接总流量
    total_flow = total_data['总流量'].sum()
    total_data['加权距离'] = total_data.apply(lambda x: x['总距离'] * x['总流量'] / total_flow,axis = 1 )
    total_data['加权经转次数'] =  total_data.apply(lambda x:x['经转次数']*x['总流量']/total_flow,axis = 1 )

    transport_cost = cost_detail['车辆成本'].sum()
    statistics = statistics.append([['运输成本', transport_cost]])

    per_yunj =  total_data['加权距离'].sum()
    statistics = statistics.append([['平均运距',per_yunj]])
    per_jingz = total_data['加权经转次数'].sum()
    statistics = statistics.append([['平均经转次数', per_jingz]])

    xianlu_num = route[route['经转次数'] == 0]['经转次数'].count()
    statistics = statistics.append([['线路数', xianlu_num]])

    youlu_num = cost_detail['邮路总条数'].sum()
    statistics = statistics.append([['邮路数', youlu_num]])

    ziban_40 = cost_detail['自办_40t'].sum()
    ziban_20 = cost_detail['自办_20t'].sum()
    ziban_12 = cost_detail['自办_12t'].sum()
    ziban_num = ziban_40 + ziban_20 + ziban_12

    statistics = statistics.append([['自办占比','{:.2%}'.format(ziban_num / youlu_num)]])
    statistics = statistics.append([['其中：12t车占比', '{:.2%}'.format(ziban_12 / youlu_num)]])
    statistics = statistics.append([['          20t车占比', '{:.2%}'.format(ziban_20 / youlu_num)]])
    statistics = statistics.append([['          40t车占比', '{:.2%}'.format(ziban_40 / youlu_num)]])
    
    weiban_40 = cost_detail['委办_40t'].sum()
    weiban_20 = cost_detail['委办_20t'].sum()
    weiban_12 = cost_detail['委办_12t'].sum()
    weiban_num = weiban_40 + weiban_20 + weiban_12

    statistics = statistics.append([['委办占比','{:.2%}'.format(weiban_num / youlu_num)]])
    statistics = statistics.append([['其中：12t车占比', '{:.2%}'.format(weiban_12 / youlu_num)]])
    statistics = statistics.append([['          20t车占比', '{:.2%}'.format(weiban_20 / youlu_num)]])
    statistics = statistics.append([['          40t车占比', '{:.2%}'.format(weiban_40 / youlu_num)]])

    statistics = pd.DataFrame(np.array(statistics),columns = ['统计项','结果'])


    return statistics,total_data

#————————————————————————————————————————————————————————————————————————————————————————————-
print("计算输出")
statis,total_data = statistics(flow,route,distance,cost_detail)
statis.to_csv("统计结果_层级集散_40_80%_40%_无route2.csv",index = 0, encoding = 'utf_8_sig')
total_data.to_csv("统计总表_层级集散_40_80%_40%_无route2.csv",index = 0, encoding = 'utf_8_sig')
end = time.time()
print("计算输出完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-








