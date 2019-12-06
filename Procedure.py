import pandas as pd
import numpy as np
import Parameters as pa
import math

#运量及处理量计算函数
def yunliang(flow,route,hub_list):
    '''
    :param flow: 流量表
    :param route: 路由表
    :param prohub_list: 城市信息清单
    :return: 运量表+处理量表
    '''
    hub_num = 85
    hubs = hub_list['城市名称']   #提取85个中心局
    hubs = list(hubs)     #列表化
    yunliang_matrix =  [[0 for col in range(hub_num)] for row in range(hub_num)]  #初始化运量矩阵
    yunliang = pd.DataFrame()    #初始化运量表
    #chuliliang_list = [0] * hub_num        #初始化处理量列表
    #chuliliang = pd.DataFrame()    #初始化处理量表

    route_row = route.shape[0]    #统计路由行数
    for i in range(0,route_row):
        print(i)
        flow_value = float(flow.loc[(flow['收寄城市'] == route.iloc[i,0]) & (flow['寄达城市'] == route.iloc[i,1])]['流量'])

        cflist = route.iloc[i,3].split('-')   #将路由按‘-’拆分为数组
        cflist_length = len(cflist)   #统计该数组长度
        for j in range(0,cflist_length-1):
            yunliang_matrix[hubs.index(cflist[j])][hubs.index(cflist[j+1])] += flow_value   #从0-倒数第二个元素，逐一添加城市对的运量
            #chuliliang_list[hubs.index(cflist[j])] += flow_value #从0-倒数第二个元素，逐一添加城市的处理量

        #chuliliang_list[hubs.index(cflist[cflist_length-1])] += flow_value  #循环结束，补充添加最后一个元素城市的处理量

    for i in range(0,hub_num):
        # temp_tongcheng = flow[flow.收寄城市 == hubs[i]]     #筛选同城处理量
        # temp_tongcheng = temp_tongcheng[temp_tongcheng.寄达城市 == hubs[i]]   #筛选同城处理量
        # if(temp_tongcheng.shape[0]!=0):
        #     chuliliang_list[i] += temp_tongcheng.iloc[0,2]    #添加同城处理量
        #
        # chuliliang = chuliliang.append([[hubs[i],chuliliang_list[i]]])
        for j in range(0,hub_num):
            yunliang = yunliang.append([[hubs[i],hubs[j],yunliang_matrix[i][j]]])
    return yunliang


#集包件与大件运量的总重量计算
def weight(yunliang_big,yunliang_jibao):
    '''
    
    :param yunliang_big: 大件运量
    :param yunliang_jibao: 集包件运量
    :return: 总运量（重量）表
    '''
    weight = pd.merge(yunliang_big,yunliang_jibao,how = 'outer', on = ['收寄城市','寄达城市'])
    weight.replace(np.nan,0,inplace = True)
    weight['运量（重量）'] = weight.apply(lambda x: (pa.GL_PERW[0]*x.大件运量 + pa.GL_PERW[1]*x.集包件运量),axis = 1 )
    weight.drop(columns = ['大件运量','集包件运量'],inplace = True)

    return weight


#计算各种车型组合清单
def truck_list(MAX):
    '''
    
    :param MAX: 最大车辆数
    :return: 各种车型组合清单
    '''
    initial_truck_list = []
    for i in range(0, MAX + 1):
        for j in range(0, MAX + 1):
            for k in range(0, MAX + 1):
                if i + j + k <= MAX:
                    initial_truck_list.append([i, j, k, i * pa.GL_CAP[2] + j * pa.GL_CAP[1] + k * pa.GL_CAP[0]])
    return initial_truck_list


def initial_truck(initial_truck_list, flow):
    '''
    
    :param initial_truck_list: 各种车型组合清单
    :param flow: 运量
    :return: 初始车辆使用情况
    '''
    final_truck = initial_truck_list[0]   #初始化车辆使用为[0,0,0]
    temp_cap = max([p[3] for p in initial_truck_list])   #初始化当前装载量为最大值
    temp_truck_num = pa.GL_MAX   #初始化当前车辆数为最大值

    for n in range(len(initial_truck_list)):   #循环所有车辆组合
        if ((initial_truck_list[n][3] >= flow) and (initial_truck_list[n][3] <= temp_cap) and (initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2] <= temp_truck_num)):    #若该车辆组合装载量大于等于运量,且该组合装载量小于等于当前装载量，且该组合车辆数小于等于当前车辆数
            temp_cap = initial_truck_list[n][3]
            #更新当前装载量为该组合装载量
            temp_truck_num = initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2]           #更新当前车辆数为该组合车辆数
            final_truck = [initial_truck_list[n][0], initial_truck_list[n][1], initial_truck_list[n][2]]
            #更新车辆使用为该组合

    return final_truck

# 得出初始的输出表格
def link_route(hub_list):
    '''
    
    :param hub_list: 85中心局城市信息表
    :return: 车辆成本空表，包含列'收寄城市', '寄达城市'
    '''
    hub_list = list(hub_list['城市名称'])

    cost_detail = pd.DataFrame()
    for i in range(0, len(hub_list)):
        for j in range(0, len(hub_list)):
            start = hub_list[i]
            end = hub_list[j]
            cost_detail = cost_detail.append([[start, end]])
    cost_detail = pd.DataFrame(np.array(cost_detail), columns=['收寄城市', '寄达城市'])
    return cost_detail



#以成本最低原则确定车型

# 计算单条线路运输成本（尾量委办）
def transport(final_truck_list, distance_1, distance_2, driver_num_1, driver_num_2):
    '''
    
    :param final_truck_list: 车辆使用数组：[[x_1,x_2,x_3],[y_1,y_2,y_3],[z_1,z_2,z_3]]
    :param distance_1: 去边距离
    :param distance_2: 返边距离
    :param driver_num_1: 去边司机数
    :param driver_num_2: 返边司机数
    :return: 运输成本
    '''
    #自办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用
    temp_distance = distance_1 + distance_2
    driver_num = max(driver_num_1,driver_num_2)
    truck_cost_1= temp_distance * ((final_truck_list[2][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2])+ (final_truck_list[2][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) + (final_truck_list[2][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0])) + \
                  temp_distance * (final_truck_list[2][0] * pa.GL_OIL[2] + final_truck_list[2][1] * pa.GL_OIL[1] + final_truck_list[2][2] *pa.GL_OIL[0]) + \
                  ((temp_distance / pa.GL_V[2]) * driver_num * pa.GL_LABOR[2] * final_truck_list[2][0]) + \
                  ((temp_distance / pa.GL_V[1]) * driver_num * pa.GL_LABOR[1] * final_truck_list[2][1]) + \
                  ((temp_distance / pa.GL_V[0]) * driver_num * pa.GL_LABOR[0] * final_truck_list[2][2])
    #去边运量委办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用（各类车型分别乘对应系数）
    truck_cost_2 = distance_1 * ((final_truck_list[0][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) * pa.GL_K[2]+ (final_truck_list[0][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) * pa.GL_K[1]+ (final_truck_list[0][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]) * pa.GL_K[0]) + \
                   distance_1 * (final_truck_list[0][0] * pa.GL_OIL[2] * pa.GL_K[2] + final_truck_list[0][1] * pa.GL_OIL[1] * pa.GL_K[1] + final_truck_list[0][2] * pa.GL_OIL[0]* pa.GL_K[0])  + \
                   ((distance_1 / pa.GL_V[2]) * driver_num_1 * pa.GL_LABOR[2] * final_truck_list[0][0] * pa.GL_K[2]) + \
                   ((distance_1 / pa.GL_V[1]) * driver_num_1 * pa.GL_LABOR[1] * final_truck_list[0][1] * pa.GL_K[1]) + \
                   ((distance_1 / pa.GL_V[0]) * driver_num_1 * pa.GL_LABOR[0] * final_truck_list[0][2] * pa.GL_K[0])
    #回边运量委办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用（各类车型分别乘对应系数）
    truck_cost_3 = distance_2 * ((final_truck_list[1][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) * pa.GL_K[0]+ (final_truck_list[1][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) * pa.GL_K[1]+ (final_truck_list[1][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]) * pa.GL_K[2]) + \
                   distance_2 * (final_truck_list[1][0] * pa.GL_OIL[2] * pa.GL_K[0] + final_truck_list[1][1] * pa.GL_OIL[1] * pa.GL_K[1] + final_truck_list[1][2] * pa.GL_OIL[0] * pa.GL_K[2]) + \
                   ((distance_2 / pa.GL_V[2]) * driver_num_2 * pa.GL_LABOR[2] * final_truck_list[1][0] * pa.GL_K[2]) + \
                   ((distance_2 / pa.GL_V[1]) * driver_num_2 * pa.GL_LABOR[1] * final_truck_list[1][1] * pa.GL_K[1]) + \
                   ((distance_2 / pa.GL_V[0]) * driver_num_2 * pa.GL_LABOR[0] * final_truck_list[1][2] * pa.GL_K[0])
    truck_cost = truck_cost_1 + truck_cost_2 + truck_cost_3
    return  truck_cost
def transport_cost(hub_list, weight, distance):
    '''
    :param hub_list: 85中心局城市信息表。四列，按顺序分别为：城市名称、所属省份、所属中心局、所属省市中心
    :param weight: 运量（重量）表。三列，按顺序分别为：收寄城市、寄达城市、运量（重量）
    :param distance: 距离表。三列，按顺序分别为：收寄城市、寄达城市、距离
    :return: 未格式化输出的运输成本表。11列
    '''
    m_2 = 1
    m_3 = 1
    while (m_2 * pa.GL_CAP[2] < (m_2 + 1) * pa.GL_CAP[1]):
        m_2 += 1
    while (m_3 * pa.GL_CAP[2] < (m_3 + 1) * pa.GL_CAP[0]):
        m_3 += 1
    print(m_2, m_3)

    hubs = list(hub_list['城市名称'])
    hubs_pair = []
    trans_cost = pd.DataFrame()
    #城市对列表
    for y_2 in range(0,len(hubs)-1):
        for j in range(y_2+1,len(hubs)):
            hubs_pair.append([hubs[y_2],hubs[j]])

    pair_dui = 0
    for pair in hubs_pair:#循环每一对城市对
        pair_dui += 1
        print(pair_dui,pair)
        weight_1 = float(weight.loc[(weight['收寄城市'] == pair[0]) & (weight['寄达城市']== pair[1])]['运量（重量）'])
        weight_2 = float(weight.loc[(weight['收寄城市'] == pair[1]) & (weight['寄达城市'] == pair[0])]['运量（重量）'])
        #查询往返运量（重量）
        weight_min = min(weight_1,weight_2)
        weight_max = max(weight_1, weight_2)
        k_1 = math.ceil(weight_1 / pa.GL_CAP[2]) + 1  #计算去边所需最大车辆数

        k_2 = math.ceil(weight_2 / pa.GL_CAP[2]) + 1  # 计算回边所需最大车辆数

        # 查询往返距离
        distance_1 = float(distance.loc[(distance['收寄城市'] == pair[0]) & (distance['寄达城市']== pair[1])]['距离'])
        distance_2 = float(distance.loc[(distance['收寄城市'] == pair[1]) & (distance['寄达城市']== pair[0])]['距离'])

        # 查询司机人数
        driver_num_1 = 2 if distance_1 >= pa.GL_DSP else 1
        driver_num_2 = 2 if distance_2 >= pa.GL_DSP else 1
        # 双向无直达邮路或运量为0
        if(weight_max == 0):
            trans_cost = trans_cost.append([[pair[0], pair[1], np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]])
            trans_cost = trans_cost.append([[pair[1], pair[0], np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]])
        # 如果某一边无直达邮路或无运量，直接委办
        elif(weight_min == 0):
            initial_truck_list = truck_list(pa.GL_MAX)
            if weight_1 != 0:
                final_truck_list = [initial_truck(initial_truck_list, weight_1),[0,0,0],[0,0,0]]
                final_cost = transport(final_truck_list, distance_1, 0, driver_num_1, 0)
                trans_cost = trans_cost.append([[pair[0], pair[1], final_truck_list[0][0], final_truck_list[0][1], final_truck_list[0][2],final_truck_list[2][0], final_truck_list[2][1], final_truck_list[2][2], distance_1,final_cost, np.nan]])
            else:
                final_truck_list = [[0,0,0],initial_truck(initial_truck_list, weight_2),[0,0,0]]
                final_cost = transport(final_truck_list, 0, distance_2, 0, driver_num_2)
                trans_cost = trans_cost.append([[pair[1], pair[0], final_truck_list[1][0], final_truck_list[1][1],final_truck_list[1][2], final_truck_list[2][0], final_truck_list[2][1],final_truck_list[2][2], distance_2, final_cost, np.nan]])
        # 往返都有直达邮路且运量都大于0
        else:
            final_truck_list = []
            final_cost = 1000000000
            k_min = min(k_1,k_2)
            for z_1 in range(0,int(k_min)):
                for z_2 in range(min(m_2,int(k_min) - z_1)):
                    for z_3 in range(min(m_3,int(k_min) - z_1 - z_2)):
                        for x_1 in range(max(0,k_1-1-z_1-m_2-m_3),int(k_1) - z_1 - z_2 - z_3):
                            for x_2 in range(min(m_2,int(k_1) - z_1 - z_2 - z_3 - x_1)):
                                for x_3 in range(min(m_3,int(k_1) - z_1 - z_2 - z_3 - x_1 - x_2)):
                                    for y_1 in range(max(0,k_2-1-z_1-m_2-m_3),int(k_2) - z_1 - z_2 - z_3):
                                        for y_2 in range(min(m_2,int(k_2) - z_1 - z_2 - z_3 - y_1)):
                                            for y_3 in range(min(m_3,int(k_2) - z_1 - z_2 - z_3 - y_1 - y_2)):
                                                #print([[x_1,x_2,x_3],[y_1,y_2,y_3],[z_1,z_2,z_3]])
                                                temp_truck_list = [[x_1,x_2,x_3],[y_1,y_2,y_3],[z_1,z_2,z_3]]
                                                if (((x_1 + z_1) * pa.GL_CAP[2] + (x_2 + z_2) * pa.GL_CAP[1] + (x_3 + z_3) * pa.GL_CAP[0]) >= weight_1) & \
                                                     (((y_1 + z_1) * pa.GL_CAP[2] + (y_2 + z_2) * pa.GL_CAP[1] + (y_3 + z_3) * pa.GL_CAP[0]) >= weight_2):

                                                    temp_cost = transport(temp_truck_list, distance_1, distance_2, driver_num_1, driver_num_2)
                                                    if temp_cost < final_cost:

                                                        final_cost = temp_cost

                                                        final_truck_list = temp_truck_list

            final_truck_list_1 = [final_truck_list[0],[0,0,0],final_truck_list[2]]
            final_cost_1 = transport(final_truck_list_1, distance_1, 0, driver_num_1, 0)

            trans_cost = trans_cost.append([[pair[0], pair[1], final_truck_list_1[0][0], final_truck_list_1[0][1], final_truck_list_1[0][2], final_truck_list_1[2][0], final_truck_list_1[2][1], final_truck_list_1[2][2], distance_1, final_cost_1,'大' if weight_1 > weight_2 else '小']])

            final_truck_list_2 = [[0,0,0],final_truck_list[1],final_truck_list[2]]
            final_cost_2 = transport(final_truck_list_2, 0, distance_2, 0, driver_num_2)

            trans_cost = trans_cost.append([[pair[1], pair[0],  final_truck_list_2[1][0], final_truck_list_2[1][1], final_truck_list_2[1][2], final_truck_list_2[2][0], final_truck_list_2[2][1], final_truck_list_2[2][2], distance_2, final_cost_2,'大' if weight_2 > weight_1 else '小']])
    trans_cost = pd.DataFrame(np.array(trans_cost), columns = ['收寄城市', '寄达城市', '委办_40t','委办_20t','委办_12t', '自办_40t','自办_20t','自办_12t','城市间距离','车辆成本','大小边标记'])
    return trans_cost

def output(hub_list,trans_cost):
    '''
    
    :param hub_list: 85中心局城市信息表。
    :param trans_cost: 未格式化输出的运输成本表。 
    :return: 格式化输出的运输成本表。 13列
    '''
    cost_detail = link_route(hub_list)
    cost_detail = pd.merge(cost_detail,trans_cost,how = 'left',on = ['收寄城市','寄达城市'])

    cost_detail['邮路总条数'] = np.nan
    cost_detail['邮路总条数'] = np.nan

    for i in range(cost_detail.shape[0]):
        if(cost_detail.loc[i,'车辆成本'] is not np.nan):
            cost_detail.loc[i, '邮路总条数'] = cost_detail.loc[i,'委办_40t'] + cost_detail.loc[i,'委办_20t'] +cost_detail.loc[i,'委办_12t']+ cost_detail.loc[i,'自办_40t'] +cost_detail.loc[i,'自办_20t'] +cost_detail.loc[i,'自办_12t']
            cost_detail.loc[i,'邮路总长度'] = cost_detail.loc[i,'城市间距离'] * (
            (cost_detail.loc[i,'委办_40t'] + cost_detail.loc[i,'委办_20t'] + cost_detail.loc[i,'委办_12t']) + (cost_detail.loc[i,'自办_40t'] + cost_detail.loc[i,'自办_20t'] + cost_detail.loc[i,'自办_12t']))

    cost_detail = cost_detail[['收寄城市', '寄达城市', '委办_40t','委办_20t','委办_12t', '自办_40t','自办_20t','自办_12t','邮路总条数','邮路总长度','城市间距离','车辆成本','大小边标记']]

    return cost_detail


#处理成本计算
def handle_cost(chuliliang_big,chuliliang_jibao):
    cost_handle = pd.merge(chuliliang_big,chuliliang_jibao,how = 'outer', on = ['中心局'])
    cost_handle.replace(np.nan,0,inplace = True)
    cost_handle['处理成本'] = cost_handle.apply(lambda x: (pa.GL_HANDLEC[0]*x.大件处理量 + pa.GL_HANDLEC[1]*x.集包件处理量),axis = 1 )


    cost_handle.drop(columns = ['大件处理量','集包件处理量'],inplace = True)

    return cost_handle






