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
start = time.time()

#(1)读取输入表格
print("开始读取输入表格")

#(1.1)85中心局之间的大件、集包件的流量流向
in_hub_flow = pd.read_csv("in_hub_flow.csv",encoding = 'UTF-8')
in_hub = pd.read_csv("in_hub.csv",encoding = 'UTF-8')
in_hub_flow['is_direct'] = 0
in_hub_flow['route_1'] = np.nan
#in_hub_flow['start_distribution_center'] = np.nan

#默认线路集合
distribution = pd.read_csv("distribution.csv",encoding = 'UTF-8')

center = list(set(distribution['所属区域集散中心']))

route_0 = []

for i in range(len(center)-1):
    for j in range(i+1,len(center)):
        route_0.extend([center[i]+'-'+center[j],center[j]+'-'+center[i]])

for i in range(distribution.shape[0]):
    if(distribution.loc[i,'城市名称'] not in center):
        route_0.extend([distribution.loc[i,'城市名称'] + '-' + distribution.loc[i,'所属区域集散中心'], distribution.loc[i,'所属区域集散中心'] + '-' + distribution.loc[i,'城市名称']])

#print(len(in_hub_flow))
#增加字典dict_hub_weight，存放85中i西南局之间的运量的重量，用于判断85中心局之间是否开直达线路
dict_hub_weight = {}
for i in range(0, len(in_hub_flow)):
    dict_hub_weight[in_hub_flow.loc[i,'start_trans_hub']+'-'+in_hub_flow.loc[i,'end_trans_hub']] \
        = in_hub_flow.loc[i, 'zb_num'] * par.zb_weight + in_hub_flow.loc[i, 'big_num'] * par.big_weight
#在表格in_hub_flow中增加字段start_distribution_center、end_distribution_center，分别表示start_trans_hub、end_trans_hub所属集散中心
in_hub_flow = pd.merge(in_hub_flow,in_hub,how = 'left',left_on = ['start_trans_hub'],right_on = ['hub'])
in_hub_flow.drop(columns=['prov_capital','hub'],inplace= True)
in_hub_flow = pd.merge(in_hub_flow,in_hub,how = 'left',left_on = ['end_trans_hub'],right_on = ['hub'])
in_hub_flow.drop(columns=['prov_capital','hub'],inplace= True)
in_hub_flow.rename(columns = {'distribution_center_x':'start_distribution_center','distribution_center_y':'end_distribution_center'},inplace=True)
#print(in_hub_flow)

hedui = pd.DataFrame()
#更新字段is_direct、route_1，确定85中心局之间是否开直达线路
route_1 = []
for i in range(0,len(in_hub_flow) ):

    #print(in_hub_flow.loc[i]['start_trans_hub'])
    hub_pair1 = in_hub_flow.loc[i,'start_trans_hub'] + '-' + in_hub_flow.loc[i,'end_trans_hub']
    hub_pair2 = in_hub_flow.loc[i,'end_trans_hub'] + '-' + in_hub_flow.loc[i,'start_trans_hub']

    if((in_hub_flow.loc[i,'start_trans_hub'] not in center) and (in_hub_flow.loc[i,'end_trans_hub'] not in center) and (in_hub_flow.loc[i,'start_trans_hub'] != in_hub_flow.loc[i,'end_trans_hub'])):
        weight1 = dict_hub_weight[hub_pair1] if hub_pair1 in dict_hub_weight.keys() else 0
        weight2 = dict_hub_weight[hub_pair2] if hub_pair2 in dict_hub_weight.keys() else 0
        if (weight1 >= par.r1 * par.loading_weight['40t'])\
                or (par.r2 * par.loading_weight['40t'] <= weight1 <= par.r1 * par.loading_weight['40t'] and weight2 >= par.r1 * par.loading_weight['40t']):
            in_hub_flow.loc[i, 'is_direct'] = 1
            in_hub_flow.loc[i, 'route_1'] = hub_pair1
            route_1.append(hub_pair1)

            hedui = hedui.append([[hub_pair1, weight1, weight2,'route_1']])
        else:
            hedui = hedui.append([[hub_pair1, weight1, weight2, np.nan]])




#计算每个集散中心与其余6个集散中心下中心局之间的zb_num、big_num
in_hub_flow_2 = pd.DataFrame()
for i in range(0, len(in_hub_flow)):
    if in_hub_flow.loc[i,'is_direct'] == 0 and in_hub_flow.loc[i,'start_distribution_center'] != in_hub_flow.loc[i,'end_distribution_center']\
            and in_hub_flow.loc[i,'start_trans_hub'] != in_hub_flow.loc[i,'start_distribution_center']\
            and in_hub_flow.loc[i,'end_trans_hub'] != in_hub_flow.loc[i,'end_distribution_center']:
        start_trans_hub = in_hub_flow.loc[i, 'start_trans_hub']
        end_trans_hub = in_hub_flow.loc[i, 'end_trans_hub']
        zb_num = in_hub_flow.loc[i, 'zb_num']
        big_num = in_hub_flow.loc[i, 'big_num']
        start_distribution_center = in_hub_flow.loc[i, 'start_distribution_center']
        end_distribution_center = in_hub_flow.loc[i, 'end_distribution_center']
        in_hub_flow_2 = in_hub_flow_2.append([[start_trans_hub, end_trans_hub, zb_num, big_num, start_distribution_center, end_distribution_center]])
in_hub_flow_2 = pd.DataFrame(np.array(in_hub_flow_2), columns=['start_trans_hub', 'end_trans_hub', 'zb_num', 'big_num', 'start_distribution_center', 'end_distribution_center'])
#print(in_hub_flow_2.head())
#计算每个集散中心与其余6个集散中心下中心局之间的zb_num、big_num
center_hub_num = in_hub_flow_2.groupby(['start_distribution_center','end_trans_hub'],as_index = False)['zb_num', 'big_num'].sum()
#计算每个中心局与其余6个集散中心之间的zb_num、big_num
hub_center_num = in_hub_flow_2.groupby(['start_trans_hub','end_distribution_center'],as_index = False)['zb_num', 'big_num'].sum()
hub_center_num.rename(columns = {'start_trans_hub':'start_distribution_center','end_distribution_center':'end_trans_hub'},inplace = True)
hub_and_center_flow = pd.concat([center_hub_num,hub_center_num],ignore_index=True)
#print(hub_and_center_flow)

#增加字典dict_hub_and_center_weight，存放每个集散中心与其余6个集散中心下中心局之间的重量/每个中心局与其余6个集散中心之间的重量，用于判断中心局与集散中心之间是否开直达线路
dict_hub_and_center_weight = {}
for i in range(0, len(hub_and_center_flow)):
    dict_hub_and_center_weight[hub_and_center_flow.loc[i,'start_distribution_center']+'-'+hub_and_center_flow.loc[i,'end_trans_hub']] \
        = hub_and_center_flow.loc[i, 'zb_num'] * par.zb_weight + hub_and_center_flow.loc[i, 'big_num'] * par.big_weight


hub_and_center_flow['is_direct'] = 0
hub_and_center_flow['route_2'] = np.nan


#更新字段is_direct、route_2，确定中心局与集散中心之间是否开直达线路
# route_2 = []
# route_0_1 = route_0 + route_1
# for i in range(0,len(hub_and_center_flow) ):
#
#     hub_pair1 = hub_and_center_flow.loc[i,'start_distribution_center'] + '-' + hub_and_center_flow.loc[i,'end_trans_hub']
#     hub_pair2 = hub_and_center_flow.loc[i,'end_trans_hub'] + '-' + hub_and_center_flow.loc[i,'start_distribution_center']
#     #print(i,hub_pair1,hub_pair2 )
#     if ((hub_pair1 not in route_0_1) and (hub_pair2 not in route_0_1) and (in_hub_flow.loc[i,'start_trans_hub'] != in_hub_flow.loc[i,'end_trans_hub'])):
#         weight1 = dict_hub_and_center_weight[hub_pair1] if hub_pair1 in dict_hub_and_center_weight.keys() else 0
#         weight2 = dict_hub_and_center_weight[hub_pair2] if hub_pair2 in dict_hub_and_center_weight.keys() else 0
#
#         if (weight1 >= par.r1 * par.loading_weight['40t'])\
#                 or (par.r2 * par.loading_weight['40t'] <= weight1 <= par.r1 * par.loading_weight['40t'] and weight2 >= par.r1 * par.loading_weight['40t']):
#             hub_and_center_flow.loc[i, 'is_direct'] = 1
#             hub_and_center_flow.loc[i, 'route_2'] = hub_pair1
#             route_2.append(hub_pair1)
#
#             hedui = hedui.append([[hub_pair1,weight1,weight2,'route_2']])
#         else:
#             hedui = hedui.append([[hub_pair1, weight1, weight2, np.nan]])

hub_and_center_flow.rename(columns = {'start_distribution_center':'start_trans_hub'},inplace = True)
zhida_route = pd.merge(in_hub_flow,hub_and_center_flow,how = 'left',on = ['start_trans_hub','end_trans_hub'])
# in_hub_flow.to_csv("1_in_hub_flow.csv", encoding = 'utf-8-sig')
# hub_and_center_flow.to_csv("2_hub_and_center_flow.csv", encoding = 'utf-8-sig')
# zhida_route.to_csv("3_zhida_route.csv", encoding = 'utf-8-sig')
final_route = zhida_route[['start_trans_hub','end_trans_hub','start_distribution_center', 'end_distribution_center','route_1','route_2']]

final_route.replace(np.nan,0,inplace = True)

final_route['经转次数'] = 0
final_route['路线'] = np.nan
final_route['路线类型'] = np.nan
distribution_center = list(set(in_hub['distribution_center']))  #集散中心清单

for i in range(0,final_route.shape[0]):
    #print(final_route.shape[0],i)
    if(final_route.loc[i,'start_trans_hub'] != final_route.loc[i,'end_trans_hub']):
        print(final_route.shape[0],i)
        if(final_route.loc[i, 'route_1'] != 0 ):

            final_route.loc[i, '路线'] = final_route.loc[i, 'route_1']
            final_route.loc[i, '经转次数'] = 0
            final_route.loc[i, '路线类型'] = 'route_1'

        elif(final_route.loc[i, 'route_2'] != 0 ):

            final_route.loc[i, '路线'] = final_route.loc[i, 'route_2']
            final_route.loc[i, '经转次数'] = 0
            final_route.loc[i, '路线类型'] = 'route_2'

        elif((final_route.loc[i,'start_trans_hub'] in distribution_center) & (final_route.loc[i,'end_trans_hub'] in distribution_center)):
            final_route.loc[i, '路线'] = final_route.loc[i,'start_trans_hub'] +'-'+final_route.loc[i,'end_trans_hub']
            final_route.loc[i, '经转次数'] = 0
            final_route.loc[i, '路线类型'] = 'route_0'


        elif(final_route.loc[i,'start_distribution_center'] == final_route.loc[i,'end_trans_hub']):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 0
            final_route.loc[i, '路线类型'] = 'route_0'


        elif(final_route.loc[i, 'end_distribution_center'] == final_route.loc[i, 'start_trans_hub']):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 0
            final_route.loc[i, '路线类型'] = 'route_0'

        elif(final_route.loc[i,'start_trans_hub'] == final_route.loc[i,'start_distribution_center']):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'end_distribution_center'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 1


        elif(final_route.loc[i,'end_trans_hub'] == final_route.loc[i,'end_distribution_center']):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'start_distribution_center'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 1

        elif((final_route.loc[i, 'start_distribution_center'] + '-' + final_route.loc[i,'end_trans_hub']) in list(final_route['route_2'])):
            final_route.loc[i, '路线'] = final_route.loc[i,'start_trans_hub'] + '-' + final_route.loc[i, 'start_distribution_center'] + '-' +final_route.loc[i,'end_trans_hub']
            final_route.loc[i, '经转次数'] = 1

        elif((final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i,'end_distribution_center']) in list(final_route['route_2'])):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'end_distribution_center'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 1

        elif(final_route.loc[i, 'start_distribution_center'] == final_route.loc[i, 'end_distribution_center']):
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'start_distribution_center'] + '-'  + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 1

        else:
            final_route.loc[i, '路线'] = final_route.loc[i, 'start_trans_hub'] + '-' + final_route.loc[i, 'start_distribution_center'] +'-'+ final_route.loc[i, 'end_distribution_center'] + '-' + final_route.loc[i, 'end_trans_hub']
            final_route.loc[i, '经转次数'] = 2

hedui.to_csv("hedui_40_80%_40%_无route2.csv", index = 0 , encoding = 'utf-8-sig')

final_route = final_route[['start_trans_hub','end_trans_hub','经转次数','路线','路线类型']]
final_route.rename(columns = {'start_trans_hub':'收寄城市','end_trans_hub':'寄达城市'}, inplace = True)
final_route = final_route.loc[final_route['收寄城市'] != final_route['寄达城市']]
final_route.to_csv("route_层级集散_40_80%_40%_无route2.csv", index = 0 , encoding = 'utf-8-sig')