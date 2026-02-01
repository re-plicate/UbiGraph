"""Sanitized ultra-optimized processing (from cosimheat version).
Includes: add_lat_lon (simple), split_by_cluster (simple), remove_duplicates, compute_cluster_links,
compute_across_links_ultra_optimized (simplified indexing), and a small CLI example.
"""
import os
import argparse
import pandas as pd
import numpy as np
from haversine import haversine, Unit
from collections import defaultdict


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def add_lat_lon(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Expect a column that contains "(lon lat)"-like text in col 4 in original; here assume lon/lat exist
    if 'longitude' in df.columns and 'latitude' in df.columns:
        df.to_csv(output_csv, index=False)
        return output_csv
    # else try to parse a 5th column
    if df.shape[1] >= 5:
        col = df.columns[4]
        longs, lats = [], []
        for v in df[col].astype(str):
            t = v.strip()
            if t.startswith('(') and t.endswith(')'):
                parts = t[1:-1].split()
                if len(parts)>=2:
                    longs.append(parts[0]); lats.append(parts[1]); continue
            longs.append(''); lats.append('')
        df['Longitude'] = longs
        df['Latitude'] = lats
        df.to_csv(output_csv, index=False)
        return output_csv
    raise ValueError('Cannot find lon/lat in input')


def split_by_cluster(input_csv, output_dir, cluster_num=28):
    df = pd.read_csv(input_csv)
    ensure_dir(output_dir)
    # This simplified split assumes a 'cluster' column exists
    if 'cluster' in df.columns:
        for i, g in df.groupby('cluster'):
            g.to_csv(os.path.join(output_dir, f'cluster_{i+1}.csv'), index=False)
        return
    # fallback: split evenly
    n = len(df)
    per = max(1, n // cluster_num)
    for i in range(cluster_num):
        start = i*per
        end = start+per if i<cluster_num-1 else n
        sub = df.iloc[start:end]
        if len(sub)>0:
            sub.to_csv(os.path.join(output_dir, f'cluster_{i+1}.csv'), index=False)


def remove_duplicates(cluster_dir, out_dir, cluster_num=28):
    ensure_dir(out_dir)
    for idx in range(cluster_num):
        path = os.path.join(cluster_dir, f'cluster_{idx+1}.csv')
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        df2 = df.drop_duplicates(subset=df.columns[1]) if df.shape[1]>1 else df.drop_duplicates()
        df2.to_csv(os.path.join(out_dir, f'cluster_drop_{idx+1}.csv'), index=False)


def compute_cluster_links(cluster_dir, out_dir, cluster_num=28):
    ensure_dir(out_dir)
    for idx in range(cluster_num):
        path = os.path.join(cluster_dir, f'cluster_drop_{idx+1}.csv')
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        n = len(df)
        rows = []
        for i in range(n):
            for j in range(n):
                if i==j:
                    rows.append([i,j,0])
                else:
                    try:
                        d = haversine((float(df.iloc[i]['Latitude']), float(df.iloc[i]['Longitude'])), (float(df.iloc[j]['Latitude']), float(df.iloc[j]['Longitude'])), unit=Unit.METERS)
                        rows.append([i,j,1.0/d if d!=0 else 0])
                    except Exception:
                        rows.append([i,j,0])
        out = os.path.join(out_dir, f'cluster_link_{idx+1}.csv')
        pd.DataFrame(rows, columns=['code1','code2','1/distance']).to_csv(out, index=False)


def compute_across_links_ultra(cluster_dir, out_dir, cluster_num=28):
    ensure_dir(out_dir)
    # load all clusters
    data = {}
    for i in range(cluster_num):
        p = os.path.join(cluster_dir, f'cluster_drop_{i+1}.csv')
        if os.path.exists(p):
            data[i] = pd.read_csv(p)
    # compare each pair
    for i in data:
        for j in data:
            if i>=j: continue
            rows = []
            a = data[i]; b = data[j]
            for ia in range(len(a)):
                for ib in range(len(b)):
                    try:
                        d = haversine((float(a.iloc[ia]['Latitude']), float(a.iloc[ia]['Longitude'])), (float(b.iloc[ib]['Latitude']), float(b.iloc[ib]['Longitude'])), unit=Unit.METERS)
                        rows.append([ia, ib, 1.0/d if d!=0 else 0])
                    except Exception:
                        rows.append([ia, ib, 0])
            out = os.path.join(out_dir, f'cluster_across_link_from{i+1}to{j+1}.csv')
            pd.DataFrame(rows, columns=['node1','node2','Connection']).to_csv(out, index=False)


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', help='Input CSV to extract lon/lat (optional)', required=False)
    p.add_argument('--output-dir', default='./dataset_release')
    args = p.parse_args()
    ensure_dir(args.output_dir)
    # This script exposes utility functions; run specific functions as needed.
    print('Use these functions programmatically or adapt this script to your dataflow.')
