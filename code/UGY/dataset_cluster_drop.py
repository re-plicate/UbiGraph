"""Sanitized copy of graphcl_project/dataset_cluster_drop.py for release.
Only small path and dependency adjustments were made.
"""
import os
import glob
import pandas as pd
import numpy as np
import torch
from torch_geometric.data import Data, InMemoryDataset
from typing import List
import re


def _symmetrize_edge_index(edge_index: torch.Tensor) -> torch.Tensor:
    row, col = edge_index
    edge_index_sym = torch.cat([edge_index, edge_index.flip([0])], dim=1)
    edge_index_sym = torch.unique(edge_index_sym, dim=1)
    return edge_index_sym


class ClusterDropDataset(InMemoryDataset):
    def __init__(self, root_dir: str, aug: str = 'dnodes', return_pair: bool = True):
        super().__init__(root=None)
        self.root_dir = root_dir
        self.aug = aug
        self.return_pair = return_pair
        self.files = sorted(glob.glob(os.path.join(root_dir, 'cluster_drop_*.csv')))
        self.data_list: List[Data] = [self._load_csv_as_graph(fp) for fp in self.files]

    def _load_csv_as_graph(self, csv_path: str) -> Data:
        df = pd.read_csv(csv_path)
        required_cols = ['longitude', 'latitude']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV file {csv_path} missing cols: {required_cols}")
        coords = df[['longitude', 'latitude']].values.astype(np.float32)
        x = torch.from_numpy(coords)
        num_nodes = len(df)
        edges = []
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                edges.append((i, j))
                edges.append((j, i))
        if len(edges) == 0:
            edge_index = torch.zeros((2, 0), dtype=torch.long)
        else:
            edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        m = re.search(r"(\d+)", os.path.basename(csv_path))
        label = int(m.group(1)) if m else 0
        y = torch.tensor([label], dtype=torch.long)
        data = Data(x=x, edge_index=edge_index, y=y)
        return data

    def __len__(self) -> int:
        return len(self.data_list)

    def __getitem__(self, idx: int):
        from copy import deepcopy
        data = deepcopy(self.data_list[idx])
        if not self.return_pair:
            return data
        if self.aug == 'none':
            return data, data
        if self.aug == 'dnodes':
            aug_data = self._augment_dnodes(data)
        else:
            aug_data = data
        return data, aug_data

    def _augment_dnodes(self, data: Data, drop_ratio: float = 0.1) -> Data:
        from copy import deepcopy
        aug_data = deepcopy(data)
        num_nodes = data.x.size(0)
        num_drop = max(1, int(num_nodes * drop_ratio))
        keep_nodes = torch.randperm(num_nodes)[:num_nodes - num_drop]
        keep_nodes = torch.sort(keep_nodes)[0]
        aug_data.x = data.x[keep_nodes]
        if data.edge_index.size(1) > 0:
            node_map = torch.full((num_nodes,), -1, dtype=torch.long)
            node_map[keep_nodes] = torch.arange(len(keep_nodes))
            mask = torch.isin(data.edge_index[0], keep_nodes) & torch.isin(data.edge_index[1], keep_nodes)
            edge_index = data.edge_index[:, mask]
            edge_index[0] = node_map[edge_index[0]]
            edge_index[1] = node_map[edge_index[1]]
            aug_data.edge_index = edge_index
        else:
            aug_data.edge_index = torch.zeros((2, 0), dtype=torch.long)
        return aug_data
