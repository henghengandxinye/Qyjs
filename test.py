
#导入使用包
import time
import os
import pandas as pd
import numpy as np
import parametersb as par
import warnings

warnings.filterwarnings("ignore")

os.chdir("C:\\Users\hengh\Desktop\QyjsCompare\Table")   # 更改工作目录
#print(os.getcwd()) # 打印当前工作目录
distribution = pd.read_csv("distribution.csv",encoding = 'UTF-8')

center = list(set(distribution['所属区域集散中心']))

route_0 = []
print(center)

for i in range(len(center)-1):
    for j in range(i+1,len(center)):
        route_0.extend([center[i]+'-'+center[j],center[j]+'-'+center[i]])

for i in range(distribution.shape[0]):
    if(distribution.loc[i,'城市名称'] not in center):
        route_0.extend([distribution.loc[i,'城市名称'] + '-' + distribution.loc[i,'所属区域集散中心'], distribution.loc[i,'所属区域集散中心'] + '-' + distribution.loc[i,'城市名称']])

print(len(set(route_0)))

a = ['d','e','b']
b = [1,2]
c =a+b
print(c)