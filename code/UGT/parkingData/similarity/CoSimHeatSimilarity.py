import pandas as pd
from scipy.sparse import coo_matrix, csr_matrix, csc_matrix
from Sparse_matrix import AcrossGraphsCosimHeat
import numpy as np


# A、B: 类的索引
def SimilarityFromAtoB(A, B, link_path):
    len_A = len(pd.read_csv('./dataset/cluster_drop/cluster_drop_' + str(A) + '.csv'))
    len_B = len(pd.read_csv('./dataset/cluster_drop/cluster_drop_' + str(B) + '.csv'))
    clusterA_link = pd.read_csv(link_path[A - 1])
    clusterB_link = pd.read_csv(link_path[B - 1])
    seed = pd.read_csv(
        './dataset/cluster_across_link/cluster_across_link_from' + str(A) + 'to' + str(B) + '.csv')
    clusterA_link = csc_matrix((clusterA_link.iloc[:, 2], (clusterA_link.iloc[:, 0], clusterA_link.iloc[:, 1])),
                                shape=(len_A, len_A))
    clusterB_link = csc_matrix((clusterB_link.iloc[:, 2], (clusterB_link.iloc[:, 0], clusterB_link.iloc[:, 1])),
                                shape=(len_B, len_B))
    seed = csc_matrix((seed.iloc[:, 2], (seed.iloc[:, 0], seed.iloc[:, 1])), shape=(len_A, len_B))

    M = list(range(len_A))
    N = list(range(len_B))
    Lamda = 0.8
    Theta = 0.2
    result = AcrossGraphsCosimHeat(clusterA_link, clusterB_link, seed, M, N, Lamda, Theta)
    return result


cluster_link_path = []
for i in range(28):
    cluster_link_path.append('./dataset/cluster_link/cluster_link_' + str(i + 1) + '.csv')


result = []
mean_result = []
print()
sim_sum = []
CoSimHeat_matrix = np.zeros([29, 29])
for i in range(1, 28):
    for j in range(i + 1, 29):
        print('i : ', i, "| j :", j)
        sim = SimilarityFromAtoB(i, j, cluster_link_path)
        sim = np.array(sim)
        sim_data = pd.DataFrame(sim)
        sim_data.to_csv('./result/CoSimHeatFrom' + str(i) + 'to' + str(j) + '.csv', index=False, header=False)
        result.append(sim)
        mean_result.append(np.mean(sim))
        sim_sum.append(sum(sum(sim)))
        CoSimHeat_matrix[i, j] = sum(sum(sim))
        CoSimHeat_matrix[j, i] = sum(sum(sim))
        # CoSimHeat_matrix[i, j] = np.mean(sim)
        # CoSimHeat_matrix[j, i] = np.mean(sim)

cluster_Eight = CoSimHeat_matrix[1:9, 1:9]
cluster_Twenty = CoSimHeat_matrix[9:, 9:]
a_eight = cluster_Eight.argmax(axis=0)
a_twenty = cluster_Twenty.argmax(axis=0)

# CoSimHeat_matrix = pd.DataFrame(CoSimHeat_matrix)
# CoSimHeat_matrix.to_csv('./result/CoSimHeat_matrix.csv', header=False, index=False)


# CoSimHeat_matrix = pd.read_csv('./result/CoSimHeat_matrix.csv', header=None)
# CoSimHeat_matrix_noweight = pd.read_csv('CoSimHeat_matrix_noweight.csv', header=None)

# CoSimHeat_matrix = np.array(CoSimHeat_matrix)
# CoSimHeat_matrix_noweight = np.array(CoSimHeat_matrix_noweight)
# aa = CoSimHeat_matrix - CoSimHeat_matrix_noweight
#
# sum_value = np.array(sim_sum)
# aa_mean = np.mean(sum_value)
cc = 0
