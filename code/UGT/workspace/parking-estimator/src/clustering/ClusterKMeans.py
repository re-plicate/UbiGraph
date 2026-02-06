# -*- coding=utf-8 -*-
'''
This module computes applies K-Means++ clustering on the city blocks

Input parameters: n_clusters - the number of clusters with parking data

@author Andrei Ionita
'''
from shapely import wkt
from sqlalchemy import MetaData, Table, update
from sklearn.cluster import KMeans
from geoalchemy2 import Geometry, Geography
import pandas as pd
import numpy as np
import sqlalchemy

import math
import argparse

def cluster_zone(has_occupancy, no_clusters_zone, blockTable, engine):
    '''
    Clusters a zone (with parking data, without parking data) into a given number of clusters and writes the results
    in the database.
    :param has_occupancy:
    :param no_clusters_zone:
    :param blockTable:
    :param engine:
    :return:
    '''
    query_condition = ""
    if not has_occupancy:
        query_condition = "NOT"

    # 找 block 的定理位置、附近的poi数量
    # Retrieves all blocks belonging to a particular city zone
    query = """SELECT
                    ST_AsText(b.wkt) as geom,
                    b.block_id,
                    aux.no_amenities
                FROM blocks b
                LEFT JOIN
                    (SELECT mbp.block_id,
                        count(*) AS no_amenities
                    FROM merge_block_poi mbp
                    GROUP BY mbp.block_id) AS aux ON b.block_id = aux.block_id
                WHERE """ + query_condition + " has_occupancy;"""

    blocks = pd.read_sql(query, engine)

    # Preparing the kmeans++ input as point arrays, by assigning the blocks coordinates
    n_geom = len(blocks.index)
    # 获取各block 的坐标点，通过坐标进行聚类
    # 聚类后的结果以 cwithid 或 cwoutid 的形式更新blocks 表
    points = np.zeros((n_geom, 2))
    blocksMap = {}
    for index, row in blocks.iterrows():
        geom = wkt.loads(row['geom'])
        centroid = geom.centroid
        x, y = centroid.coords.xy
        points[index][0] = x[0]
        points[index][1] = y[0]
        blocksMap[index] = row['block_id']

    kmeans = KMeans(n_clusters = no_clusters_zone).fit(points)

    # Write cluster ids in the database, table blocks
    for i in range(n_geom):
        if has_occupancy:
            stmt = blocksTable.update().where(blocksTable.c.block_id == blocksMap[i]).values(cwithid = int(kmeans.labels_[i]))
        else:
            stmt = blocksTable.update().where(blocksTable.c.block_id == blocksMap[i]).values(cwoutid = int(kmeans.labels_[i]))
        conn.execute(stmt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cluster blocks into a predefined number of areas')
    parser.add_argument('n_clusters', metavar='clusters', type=int, help='number of clusters')
    args = parser.parse_args()

    # The number of predefined clusters
    cwith_no = args.n_clusters

    cwout_no = int(2.6 * cwith_no)
    total = cwith_no + cwout_no
    print("Clustering SFpark blocks into a total of " +  str(total) + " areas")
    print
    print( str(cwith_no) + " areas have parking data, " + str(cwout_no) + " have no parking data")
    print

    engine = sqlalchemy.create_engine('postgres://postgres:postgres@localhost:5432/sfpark')
    conn = engine.connect()
    metadata = MetaData(engine)
    blocksTable = Table('blocks', metadata, autoload=True)

    cluster_zone(True, cwith_no, blocksTable, engine)
    cluster_zone(False, cwout_no, blocksTable, engine)

    print("Clustering finished.")
