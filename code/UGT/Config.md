# 停车位估算系统代码功能注释与解释

## 项目概述
这是一个基于机器学习的停车位占用率估算系统，主要包含以下核心功能：
1. 城市区域聚类分析
2. 基于EMD（Earth Mover's Distance）的相似性计算
3. 机器学习模型训练与预测
4. 众包数据融合

---

## 1. 数据库初始化 (initdb.sql)

### 主要表结构说明：

```sql
-- 街区表：存储城市街区的地理信息和属性
CREATE TABLE blocks (
    wkt geometry(Geometry),        -- 地理几何信息（WKT格式）
    block_id real,                 -- 街区ID
    area_type character varying(25), -- 区域类型
    pm_district real,              -- 停车管理区域
    street_name character varying(25), -- 街道名称
    has_occupancy boolean,         -- 是否有停车数据
    cwithid integer,               -- 有停车数据的聚类ID
    cwoutid integer                -- 无停车数据的聚类ID
);

-- 停车占用率表：存储历史停车数据
CREATE TABLE occupancy (
    block_id integer,              -- 街区ID
    timestamp timestamp,           -- 时间戳
    price_rate real,               -- 停车费率
    total_spots integer,           -- 总停车位数量
    occupied real                  -- 占用率百分比
);

-- POI兴趣点表：存储周边设施信息
CREATE TABLE poi_reduced (
    poi_osm_id,                    -- OSM兴趣点ID
    poi_amenity,                   -- 设施类型
    poi_geom                       -- 地理位置
);

-- 聚类相似性表：存储不同聚类间的相似性度量
CREATE TABLE cluster_similarity (
    cid1 integer,                  -- 聚类1 ID
    cid2 integer,                  -- 聚类2 ID
    similarity numeric,            -- 相似性分数
    simtype varchar(20)            -- 相似性类型（cosine/emd）
);
```

---

## 2. 数据预处理模块 (preprocessing/)

### 2.1 ProcessRawOccupancyData.py
```python
# 功能：预处理SFpark原始停车数据
# 作用：从大型CSV文件中提取关键字段，生成精简版数据集
# 处理字段：街区、时间、停车费率、占用时间等核心信息
```

### 2.2 ProcessFineTunedOccupancy.py
```python
# 功能：精细化处理停车占用率数据
# 主要计算：
# - 占用率 = 占用时间 / (占用时间 + 空闲时间) * 100
# - 总停车位数量 = 总时间 / 3600（小时）
# - 时间格式标准化
```

### 2.3 GroupTraffic.py
```python
# 功能：按区域分组交通数据
# 作用：将交通流量数据按管理区域进行聚合分析
```

---

## 3. 聚类分析模块 (clustering/ClusterKMeans.py)

### 核心功能：基于K-Means++的城市区域聚类

```python
def cluster_zone(has_occupancy, no_clusters_zone, blockTable, engine):
    """
    功能：对城市区域进行聚类分析
    
    参数说明：
    - has_occupancy: 布尔值，True表示有停车数据的区域，False表示无停车数据区域
    - no_clusters_zone: 聚类数量
    - blockTable: 数据库表对象
    - engine: 数据库连接引擎
    
    处理流程：
    1. 查询街区的地理位置和周边POI数量
    2. 提取街区的几何中心点坐标
    3. 使用K-Means++算法进行空间聚类
    4. 将聚类结果更新到数据库
    """
    
    # 查询条件：根据是否有停车数据筛选街区
    query_condition = ""
    if not has_occupancy:
        query_condition = "NOT"
    
    # SQL查询：获取街区几何信息、ID和周边设施数量
    query = """SELECT
                    ST_AsText(b.wkt) as geom,      -- 几何信息转换为WKT格式
                    b.block_id,                    -- 街区ID
                    aux.no_amenities              -- 周边POI数量
                FROM blocks b
                LEFT JOIN
                    (SELECT mbp.block_id,
                        count(*) AS no_amenities
                    FROM merge_block_poi mbp
                    GROUP BY mbp.block_id) AS aux ON b.block_id = aux.block_id
                WHERE """ + query_condition + " has_occupancy;"
    
    # 数据预处理：提取几何中心点坐标
    for index, row in blocks.iterrows():
        geom = wkt.loads(row['geom'])              # 解析WKT几何信息
        centroid = geom.centroid                   # 计算几何中心
        x, y = centroid.coords.xy                  # 提取坐标
        points[index][0] = x[0]                    # X坐标（经度）
        points[index][1] = y[0]                    # Y坐标（纬度）
    
    # K-Means++聚类
    kmeans = KMeans(n_clusters = no_clusters_zone).fit(points)
    
    # 更新数据库：将聚类ID写入对应字段
    for i in range(n_geom):
        if has_occupancy:
            # 有停车数据的区域更新cwithid字段
            stmt = blocksTable.update().where(blocksTable.c.block_id == blocksMap[i]).values(cwithid = int(kmeans.labels_[i]))
        else:
            # 无停车数据的区域更新cwoutid字段
            stmt = blocksTable.update().where(blocksTable.c.block_id == blocksMap[i]).values(cwoutid = int(kmeans.labels_[i]))
```

### 聚类策略：
- **有停车数据区域**：聚类数量由用户指定（通常为8个）
- **无停车数据区域**：聚类数量 = 2.6 × 有停车数据聚类数量（通常为20个）
- **聚类依据**：基于街区的空间位置（经纬度坐标）进行地理聚类

---

## 4. EMD相似性计算模块 (emd/AmenityEMD.py)

### 核心功能：基于Earth Mover's Distance的聚类相似性计算

```python
def calculateGaussianForCwith(cid):
    """
    功能：为有停车数据的聚类计算EMD高斯分布
    
    原理：基于周边设施（POI）的停留时间分布构建高斯混合模型
    - 每个设施类型对应一个高斯分布
    - 均值为该设施的平均停留时间
    - 标准差为停留时间的标准差
    - 权重为该设施在聚类中的密度
    """
    
    # 查询聚类中的设施信息
    amenitiesForClustersWith = pd.read_sql_query("""
        SELECT c.cid, a.name, c.dimvalue, a.mean_duration, a.stdev_duration
        FROM cluster_emd_gaussians c
        INNER JOIN amenities a ON c.dimname = a.name
        WHERE c.has_occupancy AND c.cid = """ + str(cid) + """
        ORDER BY a.name""", engine)
    
    # 构建高斯混合模型
    current_gaussian = np.zeros((n_bins))
    for index, row in amenitiesForClustersWith.iterrows():
        if row['stdev_duration'] == 0 or np.isnan(row['stdev_duration']):
            continue
        current_volume += row['dimvalue']
        # 添加高斯分布：权重 × 高斯函数
        current_gaussian += row['dimvalue'] * ot.datasets.make_1D_gauss(
            n_bins,
            m = offset + row['mean_duration'],    # 均值
            s = row['stdev_duration']             # 标准差
        )
    
    # 归一化处理
    current_gaussian /= current_volume
    return current_gaussian

def calculateDistance(gaussianMap1, has1, gaussianMap2, has2):
    """
    功能：计算两个聚类间的EMD距离
    
    参数：
    - gaussianMap1, gaussianMap2: 高斯分布映射
    - has1, has2: 布尔值，表示是否有停车数据
    
    计算过程：
    1. 使用Wasserstein距离（EMD的连续版本）计算分布间距离
    2. 归一化处理：距离 / 最大可能距离 * 100
    3. 将结果存储到数据库
    """
    
    for cid1 in gaussianMap1.keys():
        for cid2 in gaussianMap2.keys():
            # 避免重复计算
            if has1 == has2 and cid1 == cid2:
                continue
            if has1 == has2 and cid1 > cid2:
                continue
            
            gaussian1 = gaussianMap1[cid1]
            gaussian2 = gaussianMap2[cid2]
            
            # 计算Wasserstein距离
            result = wasserstein_distance(
                list(range(len(gaussian1))), 
                list(range(len(gaussian2))),
                u_weights = gaussian1, 
                v_weights = gaussian2
            )
            
            # 归一化处理
            result_norm = result * 100 / emd_max
            
            # 存储结果到数据库
            stmt = similarityTable.insert().values(
                cid1 = int(cid1), 
                has1 = has1, 
                cid2 = int(cid2), 
                has2 = has2,
                similarity = round(result_norm, 2), 
                simtype = 'emd'
            )
            conn.execute(stmt)
```

### EMD计算原理：
1. **高斯分布构建**：基于设施停留时间分布
2. **距离计算**：使用Wasserstein距离度量分布相似性
3. **相似性存储**：支持三种聚类间距离计算：
   - 有停车数据聚类 ↔ 有停车数据聚类
   - 有停车数据聚类 ↔ 无停车数据聚类  
   - 无停车数据聚类 ↔ 无停车数据聚类

---

## 5. 机器学习模型训练模块 (modeltraining/)

### 5.1 BestClusterModelSelection.py

```python
def queryClusterAll(clusterId, engine):
    """
    功能：查询指定聚类的所有停车数据
    
    返回数据：
    - cwithid: 聚类ID
    - timestamp: 时间戳
    - blocks: 街区ID列表
    - price_rate: 停车费率
    - total_spots: 总停车位
    - occupied: 占用率
    """

def queryClusterAvg(clusterId, engine):
    """
    功能：查询指定聚类的平均停车数据
    
    特点：将同一时间戳的多个街区数据按平均值聚合
    作用：减少数据噪声，提高模型稳定性
    """

def preprocess(clusterDataframe):
    """
    功能：数据预处理和特征工程
    
    处理步骤：
    1. 时间特征提取：年、周、星期几、小时
    2. 删除冗余字段：timestamp, blocks
    3. 保留核心特征：price_rate, total_spots, occupied
    """

def buildModel(method, clusterId, X, y):
    """
    功能：构建机器学习模型
    
    支持的模型类型：
    1. 决策树 (dt)
    2. 支持向量机 (svm) 
    3. 多层感知机 (mlp)
    4. 极端梯度提升 (xgb)
    
    模型选择策略：
    - 使用交叉验证进行超参数调优
    - 支持网格搜索和随机搜索
    - 自动选择最佳参数组合
    """
    
    if method == 'dt':
        # 决策树参数网格
        param_grid_dt = {
            "min_samples_split": [2, 3, 4, 5],           # 分裂所需最小样本数
            "min_samples_leaf": sp_randreal(0.03, 0.1),  # 叶节点最小样本比例
            "max_features": [0.7, 0.8, 0.9, 1],          # 特征选择比例
            "criterion": ["mse", "mae"],                  # 分裂标准
            "min_weight_fraction_leaf": [0, 0.1, 0.2]    # 叶节点最小权重比例
        }
        
    elif method == 'svm':
        # SVM参数网格
        param_grid_svr = {
            "C": [1e0, 1e1, 1e2, 1e3],                  # 正则化参数
            "gamma": np.logspace(-2, 2, 5)               # 核函数参数
        }
        
    elif method == 'mlp':
        # 神经网络参数
        model = MLPRegressor(
            hidden_layer_sizes=(7, 11),                  # 隐藏层结构
            max_iter=500                                 # 最大迭代次数
        )
        
    elif method == 'xgb':
        # XGBoost参数网格
        param_grid_xgb = {
            "max_depth": [2, 3],                         # 树的最大深度
            "n_estimators": [50, 100],                   # 树的数量
            "learning_rate": [0.1, 0.25]                 # 学习率
        }
```

### 5.2 ModelPredictionCwout.py

```python
# 功能：为无停车数据的聚类进行停车位占用率预测
# 核心思想：基于相似性找到最相似的有停车数据聚类，使用其训练好的模型进行预测

def predict_for_cluster_without_data(cwout_id, engine):
    """
    预测流程：
    1. 查找与目标聚类最相似的有停车数据聚类
    2. 加载该聚类的训练模型
    3. 使用模型预测目标聚类的停车占用率
    4. 将预测结果存储到数据库
    """
```

---

## 6. 众包数据融合模块 (crowdPark/simulate/)

### 6.1 run.py - 主运行脚本

```python
def generate_data(num_workers=100, num_plots=100, gt_plot=5, gt_price=10):
    """
    功能：生成模拟众包数据
    
    参数：
    - num_workers: 工人数量
    - num_plots: 停车位数量
    - gt_plot: 真实停车位数量
    - gt_price: 真实价格
    
    生成策略：
    1. 为每个工人生成能力参数（均值、方差）
    2. 基于工人能力生成POI标注数据
    3. 生成停车位数量和价格估算数据
    """
    
    # 工人能力参数生成
    worker_mu = np.random.normal(0, 1, num_workers)      # 工人能力均值
    worker_var = np.random.lognormal(0, 1, num_workers)  # 工人能力方差
    
    # 生成工人数据矩阵
    worker_data = np.zeros((num_workers, num_pois + num_plots + num_prices))
    
    for i in range(num_workers):
        # POI标注数据（二值化）
        arr = np.random.normal(1 + worker_mu[i], worker_var[i], num_pois)
        worker_data[i, :num_pois] = np.where(arr > 0, 1, 0)
        
        # 停车位数量估算
        worker_data[i, num_pois:num_pois+num_plots] = np.rint(
            np.random.normal(gt_plot + worker_mu[i], worker_var[i], num_plots)
        )
        
        # 价格估算
        worker_data[i, num_pois+num_plots:] = np.rint(
            np.random.normal(gt_price + worker_mu[i], worker_var[i], num_prices)
        )

def test(worker_data, worker_ids, worker_var):
    """
    功能：测试不同的众包数据融合算法
    
    测试算法：
    1. 无监督模型 (Unsupervised_Model)
    2. 联合最大似然估计 (JointMLEGaussian)
    3. 加权平均投票 (Wmv_Linear_Model)
    4. 期望最大化算法 (EM_Model)
    """
    
    # 无监督模型
    unsupervised_model = Unsupervised_Model(worker_data)
    unsupervised_model.train_worker_set(np.array(worker_ids))
    uns_mu = unsupervised_model.estimated_value_unsupervised
    
    # 联合估计模型
    joint = JointMLEGaussian(L, trainset, ans_train, model=3)
    jmu = joint.mu.T[0]
    
    # 加权平均投票
    wmv = Wmv_Linear_Model(worker_data.T, trainset, ans_train, [0,1])
    wmv_mu = np.hstack([np.ones((num_pois)), wmv.mu])
    
    # EM算法
    em_model = EM_Model(worker_data)
    em_model.train_worker_set(np.array(worker_ids))
    em_mu = em_model.estimated_value_em
```

### 6.2 worker_select.py - 工人选择策略

```python
def select(reliabilities, num_workers, num_pois, threshold):
    """
    功能：基于可靠性选择优质工人
    
    选择策略：
    1. 计算每个工人的可靠性分数
    2. 设置阈值筛选高质量工人
    3. 返回选中的工人ID列表
    
    可靠性计算：基于工人标注的POI数量
    """
```

---

## 7. 系统工作流程

### 完整的数据处理流程：

1. **数据导入**：
   - 导入街区地理数据
   - 导入停车占用率历史数据
   - 导入POI兴趣点数据

2. **区域聚类**：
   - 对有停车数据的区域进行K-Means聚类
   - 对无停车数据的区域进行K-Means聚类
   - 聚类结果存储到数据库

3. **相似性计算**：
   - 基于POI分布计算EMD相似性
   - 计算不同聚类间的距离矩阵
   - 存储相似性结果

4. **模型训练**：
   - 为有停车数据的聚类训练机器学习模型
   - 支持多种算法：决策树、SVM、神经网络、XGBoost
   - 模型持久化存储

5. **预测应用**：
   - 为无停车数据的聚类找到最相似的训练聚类
   - 使用训练好的模型进行停车占用率预测
   - 结果可视化展示

6. **众包融合**（可选）：
   - 收集众包工人的停车数据标注
   - 使用多种融合算法整合众包数据
   - 提高预测精度

---

## 8. 技术特点总结

### 核心创新点：
1. **空间聚类**：基于地理位置的智能区域划分
2. **EMD相似性**：基于设施分布的深度相似性度量
3. **多模型融合**：支持多种机器学习算法的自动选择
4. **众包数据融合**：整合多源数据提高预测精度

### 应用价值：
1. **城市规划**：为停车设施规划提供数据支持
2. **交通管理**：优化停车资源分配
3. **商业决策**：为停车定价策略提供依据
4. **用户体验**：提供实时停车位可用性预测 