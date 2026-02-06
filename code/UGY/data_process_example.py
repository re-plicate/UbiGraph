"""Sanitized preprocessing script copied from project variants.
Generates cluster_drop, cluster_link, cluster_across_link CSVs from two segmented CSV inputs.
"""

import argparse
import os
import pandas as pd
from haversine import haversine, Unit
from sklearn.cluster import KMeans


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def kmeans_cluster_and_save(input_csv, output_dir, idx, n_clusters=15):
    raw = pd.read_csv(input_csv)
    if not set(['longitude', 'latitude', 'class']).issubset(raw.columns):
        raise ValueError('Input CSV must contain longitude, latitude, class columns')
    data = raw[['longitude', 'latitude', 'class']].dropna()
    coords = data[['latitude', 'longitude']].values
    if len(coords) == 0:
        print(f"[WARN] {input_csv} has no coords")
        return None
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)
    data['cluster_id'] = labels
    out_rows = []
    for cid in sorted(set(labels)):
        cpts = data[data['cluster_id'] == cid]
        center_lat = cpts['latitude'].mean()
        center_lon = cpts['longitude'].mean()
        dominant = cpts['class'].mode()[0]
        if dominant == 'unknown':
            continue
        out_rows.append({'longitude': center_lon, 'latitude': center_lat, 'class': dominant})
    if len(out_rows) == 0:
        print(f"[WARN] no centers saved for {input_csv}")
        return None
    df_out = pd.DataFrame(out_rows)
    out_path = os.path.join(output_dir, 'cluster_drop', f'cluster_drop_{idx}.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved {out_path} ({len(df_out)} centers)")
    return out_path


def compute_internal_links(drop_csv, out_link_dir):
    df = pd.read_csv(drop_csv)
    n = len(df)
    rows = []
    for i in range(n):
        for j in range(n):
            if i == j:
                rows.append([i, j, 0])
            else:
                lat1, lon1 = df.iloc[i]['latitude'], df.iloc[i]['longitude']
                lat2, lon2 = df.iloc[j]['latitude'], df.iloc[j]['longitude']
                try:
                    d = haversine((lat1, lon1), (lat2, lon2), unit=Unit.METERS)
                    weight = 1.0 / d if d != 0 else 0
                except Exception:
                    weight = 0
                rows.append([i, j, weight])
    out_df = pd.DataFrame(rows, columns=['node1', 'node2', '1/distance'])
    base = os.path.basename(drop_csv)
    idx = ''.join([c for c in base if c.isdigit()]) or '0'
    out_path = os.path.join(out_link_dir, f'cluster_link_{idx}.csv')
    out_df.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


def compute_across_link(drop_a, drop_b, out_dir):
    a = pd.read_csv(drop_a)
    b = pd.read_csv(drop_b)
    rows = []
    for i in range(len(a)):
        for j in range(len(b)):
            try:
                d = haversine((a.iloc[i]['latitude'], a.iloc[i]['longitude']), (b.iloc[j]['latitude'], b.iloc[j]['longitude']), unit=Unit.METERS)
                w = 1.0 / d if d != 0 else 0
            except Exception:
                w = 0
            rows.append([i, j, w])
    df = pd.DataFrame(rows, columns=['node1', 'node2', 'Connection'])
    out_path = os.path.join(out_dir, 'cluster_across_link', 'cluster_across_link_1_to_2.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-a', required=True)
    p.add_argument('--input-b', required=True)
    p.add_argument('--output-dir', default='./output_graphs')
    p.add_argument('--n-clusters', type=int, default=15)
    args = p.parse_args()

    out = args.output_dir
    ensure_dir(out)
    ensure_dir(os.path.join(out, 'cluster_drop'))
    ensure_dir(os.path.join(out, 'cluster_link'))
    ensure_dir(os.path.join(out, 'cluster_across_link'))

    drop_a = kmeans_cluster_and_save(args.input_a, out, 1, n_clusters=args.n_clusters)
    drop_b = kmeans_cluster_and_save(args.input_b, out, 2, n_clusters=args.n_clusters)

    if drop_a:
        compute_internal_links(drop_a, os.path.join(out, 'cluster_link'))
    if drop_b:
        compute_internal_links(drop_b, os.path.join(out, 'cluster_link'))
    if drop_a and drop_b:
        compute_across_link(drop_a, drop_b, out)


if __name__ == '__main__':
    main()
