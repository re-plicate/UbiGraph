import numpy as np
import json


def is_in_obstacle(x, y, obstacles):

    for obs in obstacles:
        x_start, y_start, height, width = obs
        x_start=x_start / 16
        y_start=y_start/16
        # 计算障碍物在0-1坐标体系中的边界
        x_end = x_start+ height / 16  # 长度范围终点
        y_end = y_start + width / 16  # 宽度范围终点

        # 检查点是否在当前障碍物区域内
        if (x_start <= x <= x_end) and (y_start <= y <= y_end):
            return True
    return False


def generate_poi_data(obstacles, num_pois=64):
    """生成指定数量的POI兴趣点，确保不在障碍物区域内"""
    poi_data = []
    while len(poi_data) < num_pois:
        # 生成0-1之间的x和y坐标
        x = np.random.uniform(0, 1)
        y = np.random.uniform(0, 1)
        # 生成0.8-1.2之间的data值
        data = np.random.uniform(0.8, 1.2)

        # 检查是否在障碍物区域外，只有不在障碍物区域内的点才会被保留
        if not is_in_obstacle(x, y, obstacles):
            poi_data.append([x, y, data])

    return poi_data


# 障碍物矩阵
obstacles = [
    [0, 2, 1, 1],
    [6, 5, 1, 1],
    [15, 11, 1, 2],
    [4, 10, 1, 1],
    [9, 8, 1, 1],
    [10, 10, 1, 1],
    [10, 13, 1, 1],
    [12, 2, 1, 1],
    [14, 11, 2, 1]
]

# 生成64个POI兴趣点
poi_result = generate_poi_data(obstacles, 256)

# 保存为JSON文件
with open('../mnt/poi_data.json', 'w') as f:
    json.dump(poi_result, f, indent=4)
