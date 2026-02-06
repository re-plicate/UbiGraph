import pandas as pd
import numpy as np

"""  取经纬度，并将经纬度追加到excel表的后两列  """
data = pd.read_csv('./dataset/merge_poi_clusterred.csv')

point = data.iloc[:, 4]
Longitude, Latitude = [], []
for i in point:
    temp = i[6:-1].split(" ")
    Longitude.append(temp[0])
    Latitude.append(temp[1])

Longitude = pd.DataFrame(Longitude, columns=['Longitude'])
Latitude = pd.DataFrame(Latitude, columns=['Latitude'])
Coordinate = pd.concat([Longitude, Latitude], axis=1)
data = pd.concat([data, Coordinate], axis=1)
# repeatIndex = []
# hashtable = dict()
# for i in range(0, len(data)):
#     aa = hashtable.get(data.iloc[i, 1])
#     if hashtable.get(data.iloc[i, 1]) is None:
#         hashtable[data.iloc[i, 1]] = 1
#     else:
#         repeatIndex.append(i)
# data_drop = data.drop(index=data.index[repeatIndex])
data.to_csv("./dataset/clusterred_data.csv", index=None)
a = []

""" 按cluster分类数据，将结果存储在dataset/cluster文件夹中 """
# dataset = pd.read_csv('./dataset/clusterred_data.csv')
# name = list(dataset.columns)
# cluster_name = []
# name_list = [0, 1, 2, 5, 6, 7, 8]
# for i in name_list:
#     cluster_name.append(name[i])
# data = dataset.iloc[:, [0, 1, 2, 5, 6, 7, 8]]
# block_id = np.array(data.iloc[:, 0])
# cluster = []
# for i in range(28):
#     cluster.append([])
#
# for i in range(len(dataset)):
#     if pd.isna(dataset.iloc[i][5]) is False:
#         cluster[int(dataset.iloc[i][5])].append(list(data.iloc[i, :]))
#     if pd.isna(dataset.iloc[i][6]) is False:
#         cluster[int(dataset.iloc[i][6]) + 8].append(list(data.iloc[i, :]))
#
# count = 0
# for i in cluster:
#     count += 1
#     i = np.array(i)
#     i = pd.DataFrame(i, columns=cluster_name)
#     i.to_csv('./dataset/cluster/cluster_' + str(count) + '.csv', index=False)


""" 去除重复数据 """
# path = []
# for i in range(28):
#     path.append('./dataset/cluster/cluster_' + str(i + 1) + '.csv')
# count = 0
# for dataPath in path:
#     count += 1
#     clu_path = pd.read_csv(dataPath)
#
#     repeatIndex = []
#     hashtable = dict()
#     for i in range(0, len(clu_path)):
#         aa = hashtable.get(clu_path.iloc[i, 1])
#         if hashtable.get(clu_path.iloc[i, 1]) is None:
#             hashtable[clu_path.iloc[i, 1]] = 1
#         else:
#             repeatIndex.append(i)
#     data_drop = clu_path.drop(index=clu_path.index[repeatIndex])
#     data_drop.to_csv('./dataset/cluster_drop/cluster_drop_' + str(count) + '.csv', index=False)

"""  计算cluster的内部关系  """
# path = []
# for i in range(28):
#     path.append('./dataset/cluster_drop/cluster_drop_' + str(i + 1) + '.csv')
# count = 0
# from haversine import haversine, Unit
# for dataPath in path:
#     clu_data = pd.read_csv(dataPath)
#     link = []
#     length = len(clu_data)
#     for j in range(length):
#         for k in range(length):
#             if j == k:                   # 相同节点
#                 link.append([j, k, 0])
#             elif clu_data.iloc[j][2] != clu_data.iloc[k][2]:     # 节点类型不相同
#                 continue
#             else:
#                 # distance = haversine((i[j][-1], i[j][-2]), (i[k][-1], i[k][-2]), unit=Unit.KILOMETERS)
#                 distance = haversine((clu_data.iloc[j][-1], clu_data.iloc[j][-2]), (clu_data.iloc[k][-1], clu_data.iloc[k][-2]), unit=Unit.METERS)
#                 if distance == 0:
#                     link.append([j, k, 0])
#                 else:
#                     link.append([j, k, 1 / distance])
#
#     clu_link = np.array(link)
#     clu_link = pd.DataFrame(clu_link, columns=['code', 'code', '1 / distance'])
#     count += 1
#     clu_link.to_csv('./dataset/cluster_link/cluster_link_' + str(count) + '.csv', index=False)
# a = []


""" 计算跨图关系 """
# from haversine import haversine, Unit
# path = []
# for i in range(28):
#     path.append('./dataset/cluster_drop/cluster_drop_' + str(i + 1) + '.4csv')
#
# for i in range(1, 29):
#     for j in range(i, 29):
#         across_link = []
#         clusterOne = pd.read_csv(path[i - 1])
#         clusterTwo = pd.read_csv(path[j - 1])
#         for nodeOne in range(len(clusterOne)):
#             for nodeTwo in range(len(clusterTwo)):
#                 if clusterOne.iloc[nodeOne][1] == clusterTwo.iloc[nodeTwo][1]:
#                     across_link.append([nodeOne, nodeTwo, 1])
#                 elif clusterOne.iloc[nodeOne][2] == clusterTwo.iloc[nodeTwo][2]:
#                     # distance = haversine((clusterOne.iloc[nodeOne][-1], clusterOne.iloc[nodeOne][-2]),
#                     #                      (clusterTwo.iloc[nodeTwo][-1], clusterTwo.iloc[nodeTwo][-2]), unit=Unit.METERS)
#                     # across_link.append([nodeOne, nodeTwo, 1 / distance])
#                     across_link.append([nodeOne, nodeTwo, 1])
#                 else:
#                     continue
#         across_link = np.array(across_link)
#         across_link_data = pd.DataFrame(across_link, columns=['node', 'node', 'Connection'])
#         across_link_data.to_csv('./dataset/cluster_across_link/cluster_across_link_from' + str(i) + 'to' + str(j) + '.csv', index=False)
#         cc = []


""" 计算跨图相似度 """
# from sklearn import preprocessing

# min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0.8, 1))

# # CoSimHeat_matrix_sum = pd.read_csv('./result/CoSimHeat_matrix.csv', header=None)
# CoSimHeat_matrix_noweight_sum = pd.read_csv('CoSimHeat_matrix_noweight.csv', header=None)
# CoSimHeat_matrix_mean = pd.read_csv('CoSimHeat_matrix_mean.csv', header=None)

# CoSimHeat_matrix_noweight_sum = np.array(CoSimHeat_matrix_noweight_sum)
# CoSimHeat_matrix_mean = np.array(CoSimHeat_matrix_mean)

# for i in range(1, 29):
#     x = []
#     for k in range(1, 29):
#         if k == i:
#             continue
#         x.append(CoSimHeat_matrix_noweight_sum[i, k])
#     x = np.expand_dims(x, 1)
#     x_minmax = min_max_scaler.fit_transform(x)
#     for j in range(1, 28):
#         if j < i:
#             CoSimHeat_matrix_noweight_sum[i, j] = x_minmax[j - 1, 0]
#         elif j == i:
#             continue
#         else:
#             CoSimHeat_matrix_noweight_sum[i, j] = x_minmax[j - 2, 0]

# # CoSimHeat_matrix_noweight_sum_1 = pd.DataFrame(CoSimHeat_matrix_noweight_sum)
# # CoSimHeat_matrix_noweight_sum_1.to_csv('CoSimHeat.csv', index=False, header=False)
# c = []
