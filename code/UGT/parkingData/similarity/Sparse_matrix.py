import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, csc_matrix
import scanpy as sc
import scipy.sparse
from scipy.linalg import expm
import time
import gc


# 泰勒公式计算矩阵乘法
def SimpleExpm(matrix, K=10):
    matrix_K = scipy.sparse.identity(matrix.shape[0], dtype=np.float32)
    temp = matrix_K
    for i in range(1, K):
        temp = temp @ matrix / i
        matrix_K += temp.astype(np.float32)
    del temp
    gc.collect()
    return matrix_K


# 创建稀疏矩阵的出度对角矩阵
def CreatDiagArray(matrix):
    # 按列求和 计算出度
    d_matrix = matrix.sum(axis=1)  # 出度
    Output_matrix = np.array(matrix.sum(axis=1))
    Output_matrix = np.squeeze(Output_matrix)
    inv_Out = []
    for i in Output_matrix:
        if i != 0:
            inv_Out.append(1.0 / i)
        else:
            inv_Out.append(0)
    inv_Out = np.array(inv_Out).astype(np.float32)

    # 维度
    rows = np.array(range(0, matrix.shape[0]))
    columns = np.array(range(0, matrix.shape[0]))

    diag_matrix = csc_matrix((Output_matrix, (rows, columns)), shape=matrix.shape)
    inv_diag_matrix = csc_matrix((inv_Out, (rows, columns)), shape=matrix.shape)
    return d_matrix, diag_matrix, inv_diag_matrix


def AcrossGraphsCosimHeat(A, B, S, M, N, Lamda, Theta, K=3):
    """
    A       : 集合U的邻接矩阵  [n_A, n_A]
    B       : 集合V的邻接矩阵  [n_B, n_B]
    S       : 已知的对应节点关系 [n_A, n_B]
    M       : 集合U中需要计算的节点集
    N       : 集合V中需要计算的节点集
    Lamda   : diffusivity factor (0, 1)
    Theta   : type weight  [0, 1]
    K       : 迭代次数
    """

    # 出度
    d_A, diag_d_A, inv_diag_d_A = CreatDiagArray(A)
    d_B, diag_d_B, inv_diag_d_B = CreatDiagArray(B)

    # m : 边数； n：节点数
    m_A, n_A = sum(diag_d_A.data).astype(np.float32), A.shape[0]
    m_B, n_B = sum(diag_d_B.data).astype(np.float32), B.shape[0]
    # 单位矩阵
    I_A = scipy.sparse.identity(n_A, dtype=np.float32)
    I_B = scipy.sparse.identity(n_B, dtype=np.float32)

    Q = Lamda / 2 * (A.T @ inv_diag_d_A - I_A)
    P = Lamda / 2 * (inv_diag_d_B @ B - I_B)

    n_1 = S.sum(axis=1).sum()

    time_start = time.time()  # 记录开始时间

    # 计算初始值
    T0 = Theta / (m_A * m_B) * (d_A @ d_B.T) + (1.0 - Theta) / n_1 * S
    del A, B, d_A, S, d_B, diag_d_A, diag_d_B, inv_diag_d_A, inv_diag_d_B, I_A, I_B
    gc.collect()

    # 相似度矩阵
    Q_expm = SimpleExpm(Q)
    del Q

    # print("计算P_expm")
    P_expm = SimpleExpm(P)

    del P
    gc.collect()

    # print("计算 CosSimHeat")
    CosSimHeat = Q_expm @ T0 @ P_expm

    time_end = time.time()  # 记录结束时间
    time_sum = time_end - time_start  # 计算的时间差为程序的执行时间，单位为秒
    print("运算时间:", time_sum / 3600, " 小时")

    CosSimHeat = CosSimHeat[M, :]
    CosSimHeat = CosSimHeat[:, N]
    return CosSimHeat

