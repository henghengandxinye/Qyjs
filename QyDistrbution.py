# -*- coding: utf-8 -*-
import time
import os
import pandas as pd
import numpy as np

os.chdir("C:\Workspace\PythonWS\QyjsCompare\Table") # 更改工作目录
# print(os.getcwd()) # 打印当前工作目录
start = time.time()
#————————————————————————————————————————————————————————————————————————————————————————————-
print("开始读取输入表格")
#读取输入表格
distance = pd.read_csv("85中心局之间的距离.csv",encoding = 'UTF-8')
hub_list = pd.read_csv("hub_list.csv",encoding = 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
#函数
def distribution(hub_list,distance):
    distri = pd.DataFrame()
    centers = ['北京', '上海', '广州', '沈阳', '西安', '成都', '武汉']
    hubs = list(hub_list['城市名称'])

    for hub in centers:
        hubs.remove(hub)
    hubs_dict = {}
    dis_dict = {}
    for hub in hubs:
        hubs_dict.update({hub: hub})
        dis_dict.update({hub: 100000})

    for key in hubs_dict.keys():

        for center in centers:
            temp_dis_1 = distance[distance.收寄城市 == key]
            temp_dis_1 = temp_dis_1[temp_dis_1.寄达城市 == center]
            temp_dis_1 = temp_dis_1.iloc[0,2]

            temp_dis_2 = distance[distance.收寄城市 == center]
            temp_dis_2 = temp_dis_2[temp_dis_2.寄达城市 == key]
            temp_dis_2 = temp_dis_2.iloc[0, 2]

            temp_dis = temp_dis_1 + temp_dis_2

            if(temp_dis < dis_dict[key]):
                dis_dict[key] = temp_dis
                hubs_dict[key] = center

    hublist = list(hub_list['城市名称'])
    for hub in hublist:
        temp_hub_list = hub_list[hub_list.城市名称 == hub]

        if(hub in centers):
            distri = distri.append([[hub,temp_hub_list.iloc[0,3],hub]])
        else:
            distri = distri.append([[hub, temp_hub_list.iloc[0, 3], hubs_dict[hub]]])


    distri = pd.DataFrame(np.array(distri), columns=['城市名称', '所属省会中心', '所属区域集散中心'])
    return distri

#————————————————————————————————————————————————————————————————————————————————————————————-
print("计算输出")
distri = distribution(hub_list,distance)
distri.to_csv("distribution.csv",index = 0, encoding = 'utf_8_sig')
end = time.time()
print("计算输出完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-








