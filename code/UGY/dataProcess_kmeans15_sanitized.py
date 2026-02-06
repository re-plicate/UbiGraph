"""Sanitized KMeans-15 processing script.
Reads two segmented CSVs, runs KMeans(n_clusters=15) per file,
outputs cluster_drop, cluster_link, cluster_across_link in an output dir.
"""
import argparse
import os
import pandas as pd
from haversine import haversine, Unit
from sklearn.cluster import KMeans


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def kmeans15_and_save(input_csv, out_dir, idx):
    df = pd.read_csv(input_csv)
    if not set(['longitude','latitude','class']).issubset(df.columns):
        raise ValueError('Input CSV must contain longitude, latitude, class')
    data = df[['longitude','latitude','class']].dropna()
    coords = data[['latitude','longitude']].values
    if len(coords) == 0:
        return None
    kmeans = KMeans(n_clusters=15, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)
    data['cluster_id'] = labels
    centers = []
    for cid in sorted(set(labels)):
        cpts = data[data['cluster_id']==cid]
        center_lat = cpts['latitude'].mean()
        center_lon = cpts['longitude'].mean()
        dominant = cpts['class'].mode()[0]
        if dominant == 'unknown':
            continue
        centers.append({'longitude': center_lon, 'latitude': center_lat, 'class': dominant})
    if not centers:
        return None
    out_df = pd.DataFrame(centers)
    path = os.path.join(out_dir, 'cluster_drop', f'cluster_drop_{idx}.csv')
    out_df.to_csv(path, index=False)
    print(f"Saved {path}")
    return path


def compute_links(drop_csv, link_dir):
    df = pd.read_csv(drop_csv)
    n = len(df)
    rows = []
    for i in range(n):
        for j in range(n):
            if i==j:
                rows.append([i,j,0])
            else:
                try:
                    d = haversine((df.iloc[i]['latitude'], df.iloc[i]['longitude']), (df.iloc[j]['latitude'], df.iloc[j]['longitude']), unit=Unit.METERS)
                    w = 1.0/d if d!=0 else 0
                except Exception:
                    w = 0
                rows.append([i,j,w])
    base = os.path.basename(drop_csv)
    idx = ''.join([c for c in base if c.isdigit()]) or '0'
    out = os.path.join(link_dir, f'cluster_link_{idx}.csv')
    pd.DataFrame(rows, columns=['node1','node2','1/distance']).to_csv(out, index=False)
    print(f"Saved {out}")


def compute_across(drop_a, drop_b, out_dir):
    a = pd.read_csv(drop_a)
    b = pd.read_csv(drop_b)
    rows = []
    for i in range(len(a)):
        for j in range(len(b)):
            try:
                d = haversine((a.iloc[i]['latitude'], a.iloc[i]['longitude']), (b.iloc[j]['latitude'], b.iloc[j]['longitude']), unit=Unit.METERS)
                w = 1.0/d if d!=0 else 0
            except Exception:
                w = 0
            rows.append([i,j,w])
    out = os.path.join(out_dir, 'cluster_across_link', 'cluster_across_link_1_to_2.csv')
    pd.DataFrame(rows, columns=['node1','node2','Connection']).to_csv(out, index=False)
    print(f"Saved {out}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-a', required=True)
    p.add_argument('--input-b', required=True)
    p.add_argument('--output-dir', default='./output_graphs')
    args = p.parse_args()

    out = args.output_dir
    ensure_dir(os.path.join(out,'cluster_drop'))
    ensure_dir(os.path.join(out,'cluster_link'))
    ensure_dir(os.path.join(out,'cluster_across_link'))

    drop_a = kmeans15_and_save(args.input_a, out, 1)
    drop_b = kmeans15_and_save(args.input_b, out, 2)
    if drop_a: compute_links(drop_a, os.path.join(out,'cluster_link'))
    if drop_b: compute_links(drop_b, os.path.join(out,'cluster_link'))
    if drop_a and drop_b: compute_across(drop_a, drop_b, out)

if __name__=='__main__':
    main()
